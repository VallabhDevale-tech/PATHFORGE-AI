import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import AuthenticatedUser, get_current_user, get_user_supabase_client
from app.schemas.skill_gap_schema import SkillGapAnalyzeRequest
from app.services.ai_skill_gap_service import generate_skill_gap_report
from app.services.career_catalogue import get_role_by_slug
from app.services.resume_service import ResumeService
from app.services.storage_manager import HybridStorageManager

logger = logging.getLogger("pathforge.skill_gap_routes")

router = APIRouter(prefix="/skills", tags=["AI Skill Gap Analyzer"])


@router.post("/analyze", summary="Analyze skill gaps against target career")
async def analyze_skills(
    payload: SkillGapAnalyzeRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Compares candidate's resume skills against selected target career.
    Classifies skills into Skills You Have, Skills to Improve, and Missing/Not Found in Profile.
    Persists the resulting report.
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
        resumes = ResumeService.get_user_resumes(current_user)
        if resumes and len(resumes) > 0:
            resume_id = resumes[0]["id"]

    if not resume_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume found. Please upload a resume first to run skill gap analysis."
        )

    try:
        analysis_data = await ResumeService.get_resume_analysis(resume_id, current_user)
        resume_analysis = analysis_data.get("analysis")
    except Exception as e:
        logger.error(f"Error fetching resume analysis for skill gap {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve resume analysis for skill gap comparison."
        )

    # 3. Generate Skill Gap Report
    report = await generate_skill_gap_report(
        resume_analysis=resume_analysis,
        career_slug=payload.career_slug
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
            "data": None
        }
    return {
        "status": "success",
        "has_report": True,
        "data": latest
    }

