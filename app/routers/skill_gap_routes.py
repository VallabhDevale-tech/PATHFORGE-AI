import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.auth import AuthenticatedUser, get_current_user, get_user_supabase_client
from app.schemas.skill_gap_schema import SkillGapAnalyzeRequest
from app.services.ai_skill_gap_service import generate_skill_gap_report
from app.services.skill_comparison_engine import estimate_user_skill_levels
from app.services.career_catalogue import get_role_by_slug
from app.services.resume_service import ResumeService
from app.services.storage_manager import HybridStorageManager

logger = logging.getLogger("pathforge.skill_gap_routes")

router = APIRouter(prefix="/skills", tags=["AI Skill Gap Analyzer"])


@router.get("/preview-profile", summary="Preview extracted candidate profile with estimated skill levels")
async def preview_candidate_profile(
    resume_id: Optional[str] = Query(None, description="Resume ID to preview"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Retrieves the candidate's structured resume profile for review before starting
    the skill gap comparison. Displays technical skills, projects, experience,
    and estimated proficiency levels (1-4).
    """
    # Find resume
    target_resume_id = resume_id
    if not target_resume_id:
        try:
            resumes = ResumeService.get_user_resumes(current_user)
            if resumes and len(resumes) > 0:
                target_resume_id = resumes[0]["id"]
        except Exception as r_err:
            logger.info(f"Resume list lookup note: {r_err}")

    resume_analysis = None
    if target_resume_id:
        try:
            analysis_data = await ResumeService.get_resume_analysis(target_resume_id, current_user)
            resume_analysis = analysis_data.get("analysis") or {}
        except Exception as e:
            logger.info(f"ResumeService direct fetch fallback note: {e}")

    # Resilient Hybrid Fallback
    if not resume_analysis:
        saved = HybridStorageManager.get_resume_analysis(None, current_user.id, target_resume_id) if target_resume_id else None
        if not saved:
            saved = HybridStorageManager.get_latest_resume_analysis(None, current_user.id)
        if saved:
            resume_analysis = saved.get("analysis") or saved

    if not resume_analysis:
        return {
            "status": "success",
            "has_resume": False,
            "message": "No analyzed resume found. Please upload a resume first."
        }

    # Fetch any user self-assessed overrides
    overrides = HybridStorageManager.get_skill_overrides(current_user.id)
    profile_skills_map = estimate_user_skill_levels(resume_analysis, overrides)

    p_info = resume_analysis.get("personal_information") or {}
    education = resume_analysis.get("education") or []
    experience = resume_analysis.get("work_experience") or []
    projects = resume_analysis.get("projects") or []
    certs = resume_analysis.get("certifications") or []

    skills_list = [
        {
            "name": data["name"],
            "level": data["level"],
            "is_estimated": data.get("is_estimated", True),
            "evidence": data.get("evidence", [])
        }
        for data in profile_skills_map.values()
    ]

    profile_dict = {
        "candidate_name": p_info.get("full_name") or "Candidate",
        "email": p_info.get("email"),
        "education": education,
        "work_experience": experience,
        "projects": projects,
        "certifications": certs,
        "technical_skills": [d["name"] for d in skills_list],
        "profile_skills": skills_list,
        "overrides": overrides
    }

    return {
        "status": "success",
        "has_resume": True,
        "resume_id": target_resume_id,
        "profile": profile_dict,
        **profile_dict
    }


@router.post("/override", summary="Save user self-assessed skill levels")
async def save_user_skill_override(
    payload: Dict[str, Any],
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Saves candidate's verified self-assessment skill levels (1=Beginner, 2=Intermediate, 3=Advanced, 4=Expert).
    """
    raw_dict = payload.get("overrides", payload)
    clean_overrides = {
        k: int(v) for k, v in raw_dict.items()
        if isinstance(v, (int, str)) and str(v).isdigit()
    }
    HybridStorageManager.save_skill_overrides(current_user.id, clean_overrides)
    return {
        "status": "success",
        "message": "Skill overrides saved successfully."
    }


@router.post("/analyze", summary="Analyze skill gaps against target career")
async def analyze_skills(
    payload: SkillGapAnalyzeRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Compares candidate's resume skills against selected target career.
    Uses deterministic comparison engine with proficiency gaps (Gap = Required - Current).
    Classifies skills into Matched, Skills to Improve, and Missing/Not Found.
    """
    user_client = get_user_supabase_client(current_user.access_token)

    # 1. Verify target career
    role = get_role_by_slug(payload.career_slug)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target career '{payload.career_slug}' is not recognized in career catalogue."
        )

    # 2. Get resume analysis
    resume_id = payload.resume_id
    if not resume_id:
        try:
            resumes = ResumeService.get_user_resumes(current_user)
            if resumes and len(resumes) > 0:
                resume_id = resumes[0]["id"]
        except Exception:
            pass

    # If still not found, check hybrid storage for any saved resume analysis
    if not resume_id:
        latest_saved = HybridStorageManager.get_latest_resume_analysis(None, current_user.id)
        if latest_saved:
            resume_id = latest_saved.get("resume_id") or "saved_resume"

    if not resume_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid analyzed resume found. Please upload or select a resume before running skill gap analysis."
        )

    resume_analysis = None
    try:
        analysis_data = await ResumeService.get_resume_analysis(resume_id, current_user)
        resume_analysis = analysis_data.get("analysis")
    except Exception as e:
        logger.info(f"ResumeService get_resume_analysis fallback note: {e}")

    # Resilient Hybrid Fallback
    if not resume_analysis:
        saved = HybridStorageManager.get_resume_analysis(None, current_user.id, resume_id)
        if not saved:
            saved = HybridStorageManager.get_latest_resume_analysis(None, current_user.id)
        if saved:
            resume_analysis = saved.get("analysis") or saved

    if not resume_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not retrieve resume analysis for skill gap comparison."
        )

    # Retrieve existing saved overrides if not provided in payload
    overrides = payload.user_skill_overrides
    if not overrides:
        overrides = HybridStorageManager.get_skill_overrides(current_user.id)
    else:
        HybridStorageManager.save_skill_overrides(current_user.id, overrides)

    # 3. Generate Skill Gap Report using deterministic engine
    report = await generate_skill_gap_report(
        resume_analysis=resume_analysis,
        career_slug=payload.career_slug,
        resume_id=resume_id,
        user_skill_overrides=overrides
    )

    # 4. Persist Report
    saved = HybridStorageManager.save_skill_gap_report(
        user_client=user_client,
        user_id=current_user.id,
        resume_id=resume_id,
        career_slug=payload.career_slug,
        career_title=role["title"],
        report_data=report
    )

    return {
        "status": "success",
        "message": f"Skill gap analysis for '{role['title']}' generated successfully.",
        "report_id": saved.get("id"),
        "resume_id": resume_id,
        "data": report
    }


@router.get("/report", summary="Get latest skill gap report")
def get_latest_report(
    career_slug: Optional[str] = Query(None, description="Optional target career slug filter"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves user's latest generated skill gap report."""
    user_client = get_user_supabase_client(current_user.access_token)
    latest = HybridStorageManager.get_latest_skill_gap_report(
        user_client=user_client,
        user_id=current_user.id,
        career_slug=career_slug
    )
    if not latest:
        return {
            "status": "success",
            "has_report": False,
            "message": "No skill gap report found for this user."
        }

    return {
        "status": "success",
        "has_report": True,
        "data": latest
    }


@router.get("/download", summary="Download skill gap report as structured JSON")
def download_report(
    career_slug: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Exports candidate's latest skill gap report as a formatted downloadable JSON file."""
    user_client = get_user_supabase_client(current_user.access_token)
    report = HybridStorageManager.get_latest_skill_gap_report(
        user_client=user_client,
        user_id=current_user.id,
        career_slug=career_slug
    )
    if not report:
        raise HTTPException(status_code=404, detail="No report available to download.")

    filename = f"pathforge_skill_gap_{report.get('career_slug', 'report')}.json"
    return JSONResponse(
        content=report,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
