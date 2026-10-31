import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import AuthenticatedUser, get_current_user, get_user_supabase_client
from app.schemas.project_schema import ProjectGenerateRequest, ProjectStatusUpdateRequest
from app.services.ai_project_service import generate_recommended_projects
from app.services.storage_manager import HybridStorageManager

logger = logging.getLogger("pathforge.project_routes")

router = APIRouter(prefix="/projects", tags=["Project Recommendations & Portfolio"])


@router.post("/recommend", summary="Generate tailored project recommendations")
async def recommend_projects(
    payload: ProjectGenerateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Recommends practical portfolio projects specifically addressing candidate's skill gaps.
    """
    user_client = get_user_supabase_client(current_user.access_token)

    # 1. Fetch latest skill gap report
    report = HybridStorageManager.get_latest_skill_gap_report(
        user_client=user_client,
        user_id=current_user.id,
        career_slug=payload.career_slug
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Skill Gap Report found. Please run the Skill Gap Analyzer first to tailor projects."
        )

    # 2. Generate projects
    projects = generate_recommended_projects(report)

    # 3. Save to local/remote storage
    saved = HybridStorageManager.save_projects(
        user_client=user_client,
        user_id=current_user.id,
        career_slug=report.get("career_slug", "software-developer"),
        projects=projects
    )

    return {
        "status": "success",
        "message": f"Generated {len(saved)} tailored projects for {report.get('target_career')}.",
        "data": saved
    }


@router.get("", summary="Get recommended and saved projects")
def get_projects(
    career_slug: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves all projects generated for candidate with current progress status."""
    user_client = get_user_supabase_client(current_user.access_token)
    projects = HybridStorageManager.get_user_projects(
        user_client=user_client,
        user_id=current_user.id,
        career_slug=career_slug
    )
    return {
        "status": "success",
        "data": projects
    }


@router.patch("/{project_id}", summary="Update project progress, GitHub URL, and deployment URL")
def update_project(
    project_id: str,
    payload: ProjectStatusUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Updates a project's status (saved, in_progress, completed) and saves
    repository URLs and live demo links.
    """
    user_client = get_user_supabase_client(current_user.access_token)
    success = HybridStorageManager.update_project_status(
        user_client=user_client,
        user_id=current_user.id,
        project_id=project_id,
        status=payload.status,
        github_url=payload.github_url,
        demo_url=payload.demo_url,
        user_notes=payload.user_notes
    )
    if not success:
        raise HTTPException(status_code=404, detail="Project not found.")

    return {
        "status": "success",
        "message": "Project updated successfully."
    }


@router.get("/portfolio", summary="Get candidate completed showcase portfolio")
def get_portfolio(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves candidate's completed projects with live links and repo documentation."""
    user_client = get_user_supabase_client(current_user.access_token)
    all_projects = HybridStorageManager.get_user_projects(user_client, current_user.id)
    portfolio = [p for p in all_projects if p.get("status") == "completed"]
    return {
        "status": "success",
        "total_completed": len(portfolio),
        "data": portfolio
    }

