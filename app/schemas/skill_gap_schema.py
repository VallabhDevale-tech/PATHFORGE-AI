from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillRequirementItem(BaseModel):
    name: str
    category: str
    required_level: int
    required_level_name: str
    current_level: int
    current_level_name: str
    gap: int
    is_estimated: bool = True
    evidence: Optional[str] = None
    why_matters: Optional[str] = None
    action: Optional[str] = None
    status: str  # "matched", "needs_improvement", "not_found"


class SkillGapAnalyzeRequest(BaseModel):
    career_slug: str
    resume_id: Optional[str] = None
    user_skill_overrides: Optional[Dict[str, int]] = None  # Self-assessed overrides (1-4)


class SkillGapReportResponse(BaseModel):
    status: str = "success"
    target_career: str
    career_slug: str
    category: str
    resume_id: Optional[str] = None
    candidate_name: str
    total_required_skills: int
    matched_count: int
    improve_count: int
    missing_count: int
    coverage_percentage: float
    readiness_score: float
    matched_skills: List[Dict[str, Any]] = Field(default_factory=list)
    improvement_skills: List[Dict[str, Any]] = Field(default_factory=list)
    missing_skills: List[Dict[str, Any]] = Field(default_factory=list)
    priority_skills: List[str] = Field(default_factory=list)
    priority_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    category_breakdown: Dict[str, Any] = Field(default_factory=dict)
    mentor_advice: Optional[str] = None
    disclaimer: str
    analysis_status: str = "completed"
