from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CareerRecommendationItem(BaseModel):
    career_slug: str
    career_title: str
    category: str
    description: str
    compatibility_score: float
    why_matched: str
    existing_skills: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    recommended_next_steps: List[str] = Field(default_factory=list)
    market_demand: str = "High"
    typical_roles: List[str] = Field(default_factory=list)


class CareerPreferencesRequest(BaseModel):
    resume_id: Optional[str] = None
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_work_mode: Optional[str] = "Any"
    career_goals: Optional[str] = None


class CareerSelectRequest(BaseModel):
    career_slug: str
    career_title: str
    career_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CareerRecommendationResponse(BaseModel):
    status: str = "success"
    recommendations: List[CareerRecommendationItem]
    resume_id: Optional[str] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)

