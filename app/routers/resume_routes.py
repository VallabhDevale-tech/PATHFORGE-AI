import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse

from app.auth import AuthenticatedUser, get_current_user
from app.schemas.resume_schema import (
    ResumeResponse,
    ResumeAnalysisResponse,
)
from app.services.resume_service import ResumeService

logger = logging.getLogger("pathforge.resume_routes")

router = APIRouter(prefix="/resumes", tags=["Resume Analysis"])


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload and analyze candidate resume",
    response_description="Parsed structured resume analysis",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file in PDF or DOCX format (max 5 MB)"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Validates, extracts text, uploads to Supabase Storage, and executes
    AI-driven structured analysis on the candidate's resume.
    """
    logger.info(f"Processing upload '{file.filename}' for user '{current_user.id}'")
    result = await ResumeService.process_resume_upload(file, current_user)
    return {
        "status": "success",
        "message": "Resume uploaded and analyzed successfully.",
        "data": result,
    }


@router.get(
    "",
    response_model=List[ResumeResponse],
    summary="List authenticated user's uploaded resumes",
)
def list_user_resumes(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Returns history of resumes uploaded by the authenticated user.
    """
    resumes = ResumeService.get_user_resumes(current_user)
    return resumes


@router.get(
    "/{resume_id}",
    summary="Get details for a specific resume",
)
def get_resume(
    resume_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Returns metadata and details for a single resume belonging to the user.
    """
    resume = ResumeService.get_resume_by_id(resume_id, current_user)
    return {
        "status": "success",
        "data": resume,
    }


@router.get(
    "/{resume_id}/analysis",
    summary="Get structured AI analysis for a resume",
)
async def get_resume_analysis(
    resume_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Returns the structured AI analysis report for the specified resume.
    """
    analysis = await ResumeService.get_resume_analysis(resume_id, current_user)
    return {
        "status": "success",
        "data": analysis,
    }


@router.delete(
    "/{resume_id}",
    summary="Delete a resume and all associated analysis data",
)
def delete_resume(
    resume_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Deletes the resume from database, removes analysis records, and cleans up
    the file in Supabase Storage.
    """
    result = ResumeService.delete_resume(resume_id, current_user)
    return {
        "status": "success",
        "message": result.get("message", "Resume successfully deleted."),
        "resume_id": resume_id,
    }

