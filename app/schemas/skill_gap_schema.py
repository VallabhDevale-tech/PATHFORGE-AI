from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillHaveItem(BaseModel):
    skill: str
    category: str = "Technical"
    evidence: str
    importance: str = "Core requirement"


class SkillImproveItem(BaseModel):
    skill: str
    category: str = "Technical"
    priority: str = "High"
    current_status: str
    why_matters: str
    learning_direction: str


class SkillMissingItem(BaseModel):
    skill: str
    category: str = "Technical"
    priority: str = "High"
    status: str = "Not found in profile"
    why_matters: str
    learning_direction: str


class LearningPhase(BaseModel):
    phase: str
    goal: str
    skills: List[str]
    action: str


class RecommendedProject(BaseModel):
    title: str
    description: str
    skills_applied: List[str]
    difficulty: str
    estimated_hours: str
    outcome: str


class SkillGapAnalyzeRequest(BaseModel):
    resume_id: Optional[str] = None
    career_slug: str


class SkillGapReportResponse(BaseModel):
    status: str = "success"
    career_slug: str
    career_title: str
    category: str
    overall_match_percentage: float
    skills_have: List[Dict[str, Any]] = Field(default_factory=list)
    skills_improve: List[Dict[str, Any]] = Field(default_factory=list)
    skills_missing: List[Dict[str, Any]] = Field(default_factory=list)
    priority_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    learning_path: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_projects: List[Dict[str, Any]] = Field(default_factory=list)
    mentor_advice: Optional[str] = None

