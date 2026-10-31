import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import AuthenticatedUser, get_current_user, get_user_supabase_client
from app.schemas.career_schema import (
    CareerPreferencesRequest,
    CareerSelectRequest,
)
from app.services.career_catalogue import CAREER_ROLES_CATALOGUE, get_role_by_slug
from app.services.ai_career_service import generate_career_recommendations
from app.services.resume_service import ResumeService
from app.services.storage_manager import HybridStorageManager

logger = logging.getLogger("pathforge.career_routes")

router = APIRouter(prefix="/careers", tags=["Career Path Recommender"])


@router.get("/catalogue", summary="Get complete career role catalogue")
def get_career_catalogue():
    """Returns the predefined 13 career roles with required skills and descriptions."""
    return {
        "status": "success",
        "total": len(CAREER_ROLES_CATALOGUE),
        "data": CAREER_ROLES_CATALOGUE
    }


@router.get("/catalogue/{slug}", summary="Get specific career role details")
def get_catalogue_role(slug: str):
    role = get_role_by_slug(slug)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career role '{slug}' not found in catalogue."
        )
    return {
        "status": "success",
        "data": role
    }


@router.post("/recommend", summary="Generate top 5 career recommendations based on resume")
async def recommend_careers(
    payload: CareerPreferencesRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Evaluates candidate's resume analysis and preferences, generates top 5 explainable
    career recommendations, and persists the result.
    """
    user_client = get_user_supabase_client(current_user.access_token)

    # 1. Obtain candidate resume analysis
    resume_analysis = None
    resume_id = payload.resume_id

    if not resume_id:
        # Fetch user's latest resume
        resumes = ResumeService.get_user_resumes(current_user)
        if resumes and len(resumes) > 0:
            resume_id = resumes[0]["id"]

    if resume_id:
        try:
            analysis_data = await ResumeService.get_resume_analysis(resume_id, current_user)
            resume_analysis = analysis_data.get("analysis")
        except Exception as e:
            logger.warning(f"Could not load analysis for resume {resume_id}: {e}")

    if not resume_analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume analysis found. Please upload and analyze a resume first."
        )

    preferences_dict = {
        "preferred_roles": payload.preferred_roles,
        "preferred_work_mode": payload.preferred_work_mode,
        "career_goals": payload.career_goals
    }

    # 2. Run recommendation engine
    recommendations = await generate_career_recommendations(
        resume_analysis=resume_analysis,
        user_preferences=preferences_dict
    )

    # 3. Persist recommendations
    saved = HybridStorageManager.save_career_recommendations(
        user_client=user_client,
        user_id=current_user.id,
        resume_id=resume_id,
        recommendations=recommendations,
        user_preferences=preferences_dict
    )

    return {
        "status": "success",
        "message": "Top 5 career recommendations generated successfully.",
        "resume_id": resume_id,
        "recommendations": recommendations,
        "recommendation_id": saved.get("id")
    }


@router.get("/recommendations", summary="Get latest saved career recommendations")
def get_saved_recommendations(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Returns the user's latest saved career recommendations."""
    user_client = get_user_supabase_client(current_user.access_token)
    latest = HybridStorageManager.get_latest_career_recommendations(user_client, current_user.id)
    if not latest:
        return {
            "status": "success",
            "has_recommendations": False,
            "recommendations": []
        }
    return {
        "status": "success",
        "has_recommendations": True,
        "data": latest
    }


@router.post("/select", summary="Select and save a target career")
def select_target_career(
    payload: CareerSelectRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Saves the user's selected target career in Supabase profile."""
    user_client = get_user_supabase_client(current_user.access_token)
    saved = HybridStorageManager.save_career_selection(
        user_client=user_client,
        user_id=current_user.id,
        career_slug=payload.career_slug,
        career_title=payload.career_title,
        career_data=payload.career_data or {}
    )
    return {
        "status": "success",
        "message": f"Successfully selected '{payload.career_title}' as your target career.",
        "data": saved
    }


@router.get("/selected", summary="Get user's currently selected target career")
def get_selected_target_career(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves the user's saved target career."""
    user_client = get_user_supabase_client(current_user.access_token)
    selected = HybridStorageManager.get_career_selection(user_client, current_user.id)
    if not selected:
        return {
            "status": "success",
            "has_selection": False,
            "data": None
        }
    return {
        "status": "success",
        "has_selection": True,
        "data": selected
    }

