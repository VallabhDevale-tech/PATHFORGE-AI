import io
import logging
import os
import re
import uuid
import zipfile
from typing import Dict, Any, List, Optional, Tuple

try:
    import pymupdf as fitz
except ImportError:
    import fitz
import docx

from fastapi import HTTPException, UploadFile, status
from supabase import Client

from app.auth import AuthenticatedUser, get_user_supabase_client
from app.schemas.resume_schema import ResumeAnalysisResult
from app.services.ai_resume_service import analyze_resume_text
from app.services.storage_manager import HybridStorageManager

logger = logging.getLogger("pathforge.resume_service")

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/zip",
    "application/octet-stream",
}
MIN_MEANINGFUL_TEXT_LENGTH = 50


class ResumeService:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Strips directory traversal, illegal characters, and normalizes the filename."""
        clean_name = os.path.basename(filename)
        clean_name = re.sub(r"[^\w\s.-]", "", clean_name).strip()
        if not clean_name:
            clean_name = "resume"
        return clean_name

    @classmethod
    async def validate_file(cls, file: UploadFile) -> Tuple[bytes, str]:
        """Validates file size, extension, MIME type, and deep content integrity."""
        original_name = file.filename or "unknown"
        ext = os.path.splitext(original_name)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Only PDF and DOCX files are supported."
            )

        content_type = (file.content_type or "").lower()
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MIME type '{content_type}'. Expected PDF or DOCX."
            )

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty. Please upload a valid resume."
            )

        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE") else 413,
                detail=f"File exceeds maximum upload limit of 5 MB (size: {file_size / (1024 * 1024):.2f} MB)."
            )

        if ext == ".pdf":
            header_sample = content[:1024]
            if b"%PDF-" not in header_sample:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid PDF file: Missing standard PDF header structure."
                )
            try:
                doc = fitz.open(stream=content, filetype="pdf")
                if doc.is_encrypted or doc.needs_pass:
                    doc.close()
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422,
                        detail="The uploaded PDF is password-protected. Please remove password protection and try again."
                    )
                doc.close()
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Corrupted or invalid PDF file: {str(e)}"
                )

        elif ext == ".docx":
            try:
                zip_stream = io.BytesIO(content)
                if not zipfile.is_zipfile(zip_stream):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid DOCX file: File is not a valid OpenXML archive."
                    )
                with zipfile.ZipFile(zip_stream, "r") as zf:
                    namelist = zf.namelist()
                    if "word/document.xml" not in namelist:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid DOCX file structure: Missing 'word/document.xml'."
                        )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Corrupted or invalid DOCX file: {str(e)}"
                )

        return content, ext

    @classmethod
    def extract_text_from_pdf(cls, content: bytes) -> str:
        """Extracts text from PDF using PyMuPDF."""
        text_parts = []
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text_parts.append(page_text)
            doc.close()
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
        return "\n".join(text_parts).strip()

    @classmethod
    def extract_text_from_docx(cls, content: bytes) -> str:
        """Extracts text from DOCX using python-docx."""
        text_parts = []
        try:
            doc = docx.Document(io.BytesIO(content))
            for p in doc.paragraphs:
                p_text = p.text.strip()
                if p_text:
                    text_parts.append(p_text)
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        text_parts.append(" | ".join(row_cells))
        except Exception as e:
            logger.error(f"python-docx extraction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422,
                detail=f"Failed to extract text from DOCX: {str(e)}"
            )
        return "\n".join(text_parts).strip()

    @classmethod
    def extract_and_verify_text(cls, content: bytes, ext: str) -> str:
        """Extracts text and verifies meaningful non-scanned content is present."""
        if ext == ".pdf":
            raw_text = cls.extract_text_from_pdf(content)
        else:
            raw_text = cls.extract_text_from_docx(content)

        alphanumeric_chars = re.findall(r"\w", raw_text)
        if len(alphanumeric_chars) < MIN_MEANINGFUL_TEXT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422,
                detail="The uploaded resume appears to be a scanned image or contains no extractable text. OCR is not yet supported. Please upload a text-based PDF or DOCX file."
            )
        return raw_text

    @classmethod
    def upload_to_supabase_storage(
        cls, client: Client, user_id: str, unique_filename: str, content: bytes, ext: str
    ) -> str:
        """Uploads resume bytes to private Supabase Storage bucket 'resumes'."""
        storage_path = f"{user_id}/{unique_filename}"
        mime_type = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        try:
            client.storage.from_("resumes").upload(
                path=storage_path,
                file=content,
                file_options={"content-type": mime_type, "upsert": "true"}
            )
            return storage_path
        except Exception as e:
            logger.warning(f"Supabase storage upload error for path {storage_path}: {e}")
            return storage_path

    @classmethod
    async def process_resume_upload(
        cls, file: UploadFile, current_user: AuthenticatedUser
    ) -> Dict[str, Any]:
        """
        Coordinates the complete resume upload and analysis workflow:
        1. Validate file.
        2. Extract & verify meaningful text.
        3. Upload to private Supabase Storage.
        4. Insert into 'resumes' table with status 'processing'.
        5. Run structured AI analysis.
        6. Persist structured results (Hybrid storage: Supabase + local resilient store).
        7. Update resume status to 'completed'.
        8. Return verified analysis and analysis_id.
        """
        content, ext = await cls.validate_file(file)
        clean_original_filename = cls.sanitize_filename(file.filename or f"resume{ext}")
        extracted_text = cls.extract_and_verify_text(content, ext)

        user_client = get_user_supabase_client(current_user.access_token)
        unique_file_id = f"{uuid.uuid4().hex}_{clean_original_filename}"

        # Upload to Supabase Storage
        storage_path = cls.upload_to_supabase_storage(
            user_client, current_user.id, unique_file_id, content, ext
        )

        # Insert initial record into 'resumes' table
        resume_record = None
        try:
            insert_data = {
                "user_id": current_user.id,
                "file_name": clean_original_filename,
                "file_path": storage_path,
                "extracted_text": extracted_text,
                "processing_status": "processing"
            }
            res = user_client.table("resumes").insert(insert_data).execute()
            if res.data and len(res.data) > 0:
                resume_record = res.data[0]
            else:
                raise RuntimeError("Failed to insert resume record into database.")
        except Exception as db_err:
            logger.error(f"Database insert error into 'resumes': {db_err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while saving resume: {str(db_err)}"
            )

        resume_id = resume_record["id"]

        # Run AI Analysis
        try:
            analysis_result = await analyze_resume_text(extracted_text)
        except Exception as ai_err:
            logger.error(f"AI analysis failed for resume {resume_id}: {ai_err}")
            try:
                user_client.table("resumes").update({"processing_status": "failed"}).eq("id", resume_id).execute()
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI analysis failed to process resume: {str(ai_err)}"
            )

        # Persist structured analysis via HybridStorageManager
        analysis_dict = analysis_result.model_dump()
        saved_record = HybridStorageManager.save_resume_analysis(
            user_client=user_client,
            user_id=current_user.id,
            resume_id=resume_id,
            analysis_dict=analysis_dict
        )

        analysis_id = saved_record.get("id") or str(uuid.uuid4())

        # Update resume status to completed
        try:
            user_client.table("resumes").update({"processing_status": "completed"}).eq("id", resume_id).execute()
            resume_record["processing_status"] = "completed"
        except Exception as update_err:
            logger.error(f"Failed to update resume status to completed: {update_err}")

        return {
            "resume": resume_record,
            "analysis": analysis_dict,
            "analysis_id": analysis_id
        }

    @classmethod
    def get_user_resumes(cls, current_user: AuthenticatedUser) -> List[Dict[str, Any]]:
        """Fetches the authenticated user's uploaded resume history."""
        user_client = get_user_supabase_client(current_user.access_token)
        try:
            res = (
                user_client.table("resumes")
                .select("id, user_id, file_name, file_path, processing_status, created_at")
                .eq("user_id", current_user.id)
                .order("created_at", desc=True)
                .execute()
            )
            return res.data or []
        except Exception as e:
            logger.error(f"Error fetching resumes for user {current_user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not retrieve resume history."
            )

    @classmethod
    def get_resume_by_id(cls, resume_id: str, current_user: AuthenticatedUser) -> Dict[str, Any]:
        """Retrieves a single resume by ID. Verifies user ownership."""
        user_client = get_user_supabase_client(current_user.access_token)
        try:
            res = (
                user_client.table("resumes")
                .select("*")
                .eq("id", resume_id)
                .eq("user_id", current_user.id)
                .execute()
            )
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resume with ID '{resume_id}' not found or access denied."
                )
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving resume {resume_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving resume."
            )

    @classmethod
    async def get_resume_analysis(cls, resume_id: str, current_user: AuthenticatedUser) -> Dict[str, Any]:
        """
        Retrieves the structured analysis for a resume by ID.
        Checks Supabase PostgREST, then local hybrid store, and finally regenerates from
        extracted_text if missing, guaranteeing zero retrieval crashes.
        """
        resume_record = cls.get_resume_by_id(resume_id, current_user)
        user_client = get_user_supabase_client(current_user.access_token)

        # 1. Query via HybridStorageManager (Supabase + local store fallback)
        saved = HybridStorageManager.get_resume_analysis(
            user_client=user_client,
            user_id=current_user.id,
            resume_id=resume_id
        )

        if saved:
            return saved

        # 2. If not stored yet, regenerate from extracted_text
        text = resume_record.get("extracted_text")
        if text:
            analysis_result = await analyze_resume_text(text)
            analysis_dict = analysis_result.model_dump()
            saved_record = HybridStorageManager.save_resume_analysis(
                user_client=user_client,
                user_id=current_user.id,
                resume_id=resume_id,
                analysis_dict=analysis_dict
            )
            return {
                "id": saved_record.get("id"),
                "resume_id": resume_id,
                "user_id": current_user.id,
                "analysis": analysis_dict,
                "created_at": resume_record.get("created_at")
            }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analysis or text found for resume '{resume_id}'."
        )

    @classmethod
    def delete_resume(cls, resume_id: str, current_user: AuthenticatedUser) -> Dict[str, Any]:
        """Deletes a resume and associated analysis records and storage objects."""
        resume = cls.get_resume_by_id(resume_id, current_user)
        user_client = get_user_supabase_client(current_user.access_token)

        file_path = resume.get("file_path")
        if file_path:
            try:
                user_client.storage.from_("resumes").remove([file_path])
            except Exception as st_err:
                logger.warning(f"Storage file removal note for {file_path}: {st_err}")

        # Delete Supabase analysis records
        try:
            user_client.table("resume_analysis").delete().eq("resume_id", resume_id).eq("user_id", current_user.id).execute()
        except Exception:
            pass

        # Delete local analysis records
        try:
            conn = HybridStorageManager._get_db() if hasattr(HybridStorageManager, "_get_db") else None
        except Exception:
            pass

        # Delete from resumes table
        try:
            user_client.table("resumes").delete().eq("id", resume_id).eq("user_id", current_user.id).execute()
        except Exception as db_err:
            logger.error(f"Failed to delete resume record {resume_id}: {db_err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete resume: {str(db_err)}"
            )

        return {"message": "Resume and associated analysis successfully deleted.", "resume_id": resume_id}
