from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProjectGenerateRequest(BaseModel):
    career_slug: Optional[str] = None


class ProjectStatusUpdateRequest(BaseModel):
    status: Optional[str] = None  # "recommended", "saved", "in_progress", "completed"
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    user_notes: Optional[str] = None


class ProjectItemSchema(BaseModel):
    id: str
    target_career: str
    title: str
    difficulty: str
    estimated_hours: str
    prerequisites: str
    skills_addressed: List[str]
    problem_statement: str
    objectives: List[str]
    functional_requirements: List[str]
    suggested_modules: List[str]
    deliverables: List[str]
    architecture_guide: str
    milestones: List[str]
    testing_requirements: str
    deployment_suggestions: str
    github_portfolio_guidance: str
    status: str = "recommended"
    github_url: str = ""
    demo_url: str = ""
    user_notes: str = ""

