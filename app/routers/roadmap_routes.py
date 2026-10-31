import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import AuthenticatedUser, get_current_user, get_user_supabase_client
from app.schemas.roadmap_schema import RoadmapGenerateRequest, ActivityStatusUpdateRequest
from app.services.ai_roadmap_service import generate_personalized_roadmap
from app.services.storage_manager import HybridStorageManager

logger = logging.getLogger("pathforge.roadmap_routes")

router = APIRouter(prefix="/roadmap", tags=["Personalized Roadmap Engine"])


@router.post("/generate", summary="Generate personalized learning roadmap")
async def generate_roadmap(
    payload: RoadmapGenerateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Generates a personalized, week-by-week learning plan based on the candidate's
    actual Skill Gap Report, preferred duration, and weekly study hours.
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
            detail="No Skill Gap Report found. Please run the Skill Gap Analyzer first to identify your learning gaps."
        )

    # 2. Generate Roadmap
    roadmap = await generate_personalized_roadmap(
        skill_gap_report=report,
        duration_weeks=payload.duration_weeks,
        hours_per_week=payload.hours_per_week
    )

    # 3. Persist
    saved = HybridStorageManager.save_roadmap(user_client, current_user.id, roadmap)

    return {
        "status": "success",
        "message": f"Personalized {payload.duration_weeks}-week roadmap generated successfully.",
        "data": saved
    }


@router.get("/current", summary="Get active learning roadmap")
def get_current_roadmap(
    career_slug: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves the candidate's active learning roadmap and activity progress."""
    user_client = get_user_supabase_client(current_user.access_token)
    roadmap = HybridStorageManager.get_active_roadmap(
        user_client=user_client,
        user_id=current_user.id,
        career_slug=career_slug
    )
    if not roadmap:
        return {
            "status": "success",
            "has_roadmap": False,
            "message": "No active roadmap found."
        }

    return {
        "status": "success",
        "has_roadmap": True,
        "data": roadmap
    }


@router.patch("/activities/{activity_id}", summary="Update learning activity status")
def update_activity(
    activity_id: str,
    payload: ActivityStatusUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Updates status of a learning activity (pending, in_progress, completed)
    and updates progress calculations.
    """
    user_client = get_user_supabase_client(current_user.access_token)
    updated_roadmap = HybridStorageManager.update_roadmap_activity_status(
        user_client=user_client,
        user_id=current_user.id,
        activity_id=activity_id,
        new_status=payload.status
    )
    if not updated_roadmap:
        raise HTTPException(status_code=404, detail="Activity or active roadmap not found.")

    return {
        "status": "success",
        "message": f"Activity marked as {payload.status}.",
        "data": updated_roadmap
    }

