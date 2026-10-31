import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import AuthenticatedUser, get_current_user, get_user_supabase_client
from app.schemas.adaptive_schema import QuizSubmitRequest, AdjustmentActionRequest
from app.services.ai_adaptive_service import (
    compute_learning_overview,
    identify_weak_areas,
    get_what_to_learn_next,
    generate_topic_quiz,
    evaluate_quiz_submission,
    propose_roadmap_adjustments
)
from app.services.storage_manager import HybridStorageManager

logger = logging.getLogger("pathforge.adaptive_routes")

router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning Engine"])


@router.get("/overview", summary="Get comprehensive learning metrics overview")
def get_overview(
    career_slug: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Aggregates roadmap activity progress, projects, and assessment scores."""
    user_client = get_user_supabase_client(current_user.access_token)
    roadmap = HybridStorageManager.get_active_roadmap(user_client, current_user.id, career_slug)
    projects = HybridStorageManager.get_user_projects(user_client, current_user.id, career_slug)
    assessments = HybridStorageManager.get_user_assessments(user_client, current_user.id)

    metrics = compute_learning_overview(roadmap, projects, assessments)
    return {
        "status": "success",
        "data": metrics
    }


@router.get("/weak-areas", summary="Identify candidate weak areas vs demonstrated skills")
def get_weak_areas(
    career_slug: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Categorizes skills into Demonstrated, Needs Practice, In Progress, and Not Started."""
    user_client = get_user_supabase_client(current_user.access_token)
    gap_report = HybridStorageManager.get_latest_skill_gap_report(user_client, current_user.id, career_slug)
    assessments = HybridStorageManager.get_user_assessments(user_client, current_user.id)
    roadmap = HybridStorageManager.get_active_roadmap(user_client, current_user.id, career_slug)

    weak_areas = identify_weak_areas(gap_report, assessments, roadmap)
    return {
        "status": "success",
        "data": weak_areas
    }


@router.get("/next", summary="What Should I Learn Next? recommendation")
def what_to_learn_next(
    career_slug: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Returns the single best next learning activity based on progress and weak areas."""
    user_client = get_user_supabase_client(current_user.access_token)
    roadmap = HybridStorageManager.get_active_roadmap(user_client, current_user.id, career_slug)
    gap_report = HybridStorageManager.get_latest_skill_gap_report(user_client, current_user.id, career_slug)
    assessments = HybridStorageManager.get_user_assessments(user_client, current_user.id)
    projects = HybridStorageManager.get_user_projects(user_client, current_user.id, career_slug)

    weak_areas = identify_weak_areas(gap_report, assessments, roadmap)
    recommendation = get_what_to_learn_next(roadmap, weak_areas, projects)

    return {
        "status": "success",
        "data": recommendation
    }


@router.get("/quiz", summary="Generate interactive topic assessment quiz")
def get_quiz(
    skill: str = Query(..., description="Skill to test, e.g. Python, SQL, FastAPI"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Generates a 3-question multiple choice assessment testing practical knowledge."""
    quiz = generate_topic_quiz(skill)
    return {
        "status": "success",
        "data": quiz
    }


@router.post("/quiz/submit", summary="Submit quiz answers and record evaluation")
def submit_quiz(
    payload: QuizSubmitRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Scores quiz submission and persists result as learning assessment evidence."""
    user_client = get_user_supabase_client(current_user.access_token)
    quiz_data = generate_topic_quiz(payload.skill_name)
    eval_result = evaluate_quiz_submission(quiz_data, payload.answers)

    # Persist to database
    HybridStorageManager.record_assessment(user_client, current_user.id, eval_result)

    return {
        "status": "success",
        "message": f"Quiz scored: {eval_result['score_percentage']}%.",
        "data": eval_result
    }


@router.post("/propose-adjustments", summary="Analyze progress and propose roadmap adjustments")
def propose_adjustments(
    career_slug: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Analyzes progress and generates proposed non-destructive adjustments for user review."""
    user_client = get_user_supabase_client(current_user.access_token)
    roadmap = HybridStorageManager.get_active_roadmap(user_client, current_user.id, career_slug)
    if not roadmap:
        raise HTTPException(status_code=400, detail="No active roadmap found to adjust.")

    gap_report = HybridStorageManager.get_latest_skill_gap_report(user_client, current_user.id, career_slug)
    assessments = HybridStorageManager.get_user_assessments(user_client, current_user.id)
    weak_areas = identify_weak_areas(gap_report, assessments, roadmap)

    adjustment = propose_roadmap_adjustments(roadmap, weak_areas)
    if not adjustment:
        return {
            "status": "success",
            "has_adjustment": False,
            "message": "Learning pace is on track! No adjustments currently recommended."
        }

    # Save as pending
    HybridStorageManager.save_adjustment(user_client, current_user.id, roadmap["id"], adjustment)

    return {
        "status": "success",
        "has_adjustment": True,
        "data": adjustment
    }


@router.post("/adjustment/resolve", summary="Accept or reject proposed roadmap adjustment")
def resolve_adjustment(
    adjustment_id: str = Query(...),
    action: str = Query(..., pattern="^(accept|reject)$"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """User accepts or rejects proposed roadmap adjustment without overwriting completed work."""
    user_client = get_user_supabase_client(current_user.access_token)
    success = HybridStorageManager.resolve_adjustment(user_client, current_user.id, adjustment_id, action)
    if not success:
        raise HTTPException(status_code=404, detail="Adjustment record not found.")

    return {
        "status": "success",
        "message": f"Roadmap adjustment {action}ed successfully."
    }
