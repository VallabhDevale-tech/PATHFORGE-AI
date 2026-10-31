from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RoadmapGenerateRequest(BaseModel):
    career_slug: Optional[str] = None
    duration_weeks: int = 8
    hours_per_week: int = 10


class ActivityStatusUpdateRequest(BaseModel):
    status: str  # "pending", "in_progress", "completed"


class RoadmapActivity(BaseModel):
    id: str
    week_number: int
    title: str
    skill: str
    type: str
    estimated_hours: int
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "pending"


class RoadmapWeek(BaseModel):
    week_number: int
    stage: str
    skill: str
    learning_objective: str
    topics: List[str]
    resources: List[Dict[str, Any]]
    practical_exercises: List[str]
    expected_outcome: str
    completion_criteria: str
    estimated_hours: int
    activities: List[RoadmapActivity]
    is_completed: bool = False


class RoadmapResponse(BaseModel):
    id: str
    target_career: str
    career_slug: str
    duration_weeks: int
    hours_per_week: int
    total_weeks: int
    total_activities: int
    completed_activities: int
    progress_percentage: float
    stages: List[Dict[str, Any]]
    weeks: List[Dict[str, Any]]
    status: str = "active"
    pedagogical_strategy: Optional[str] = None

