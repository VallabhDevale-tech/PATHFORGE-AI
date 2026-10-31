from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Section-Specific Models (Structured Resume Analysis)
# ---------------------------------------------------------------------------

class PersonalInformation(BaseModel):
    full_name: Optional[str] = Field(None, description="Full legal or professional name")
    email: Optional[str] = Field(None, description="Email address found in resume")
    phone_number: Optional[str] = Field(None, description="Phone / mobile number")
    location: Optional[str] = Field(None, description="City, State, Country or address")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(None, description="Personal website or portfolio URL")


class ProfessionalSummary(BaseModel):
    existing_summary: Optional[str] = Field(
        None, description="Verbatim or summarized professional summary stated in resume"
    )
    main_strengths: List[str] = Field(
        default_factory=list, description="Core professional strengths evident in the resume"
    )
    primary_areas_of_experience: List[str] = Field(
        default_factory=list, description="Primary domains or areas of demonstrated experience"
    )


class EducationItem(BaseModel):
    degree: Optional[str] = Field(None, description="Degree or certificate name (e.g. B.S. Computer Science)")
    institution: Optional[str] = Field(None, description="Name of university, college, or school")
    graduation_year: Optional[str] = Field(None, description="Graduation year or expected graduation year")
    relevant_coursework: List[str] = Field(
        default_factory=list, description="Relevant courses listed under this education entry"
    )


class WorkExperienceItem(BaseModel):
    company: Optional[str] = Field(None, description="Company or organization name")
    job_title: Optional[str] = Field(None, description="Position or title held")
    start_date: Optional[str] = Field(None, description="Employment start date")
    end_date: Optional[str] = Field(None, description="Employment end date or 'Present'")
    responsibilities: List[str] = Field(
        default_factory=list, description="Key duties and day-to-day responsibilities"
    )
    achievements: List[str] = Field(
        default_factory=list, description="Measurable achievements or key impacts"
    )


class ProjectItem(BaseModel):
    project_title: Optional[str] = Field(None, description="Name or title of the project")
    description: Optional[str] = Field(None, description="Brief overview of the project")
    technologies_used: List[str] = Field(
        default_factory=list, description="Tools, frameworks, and programming languages utilized"
    )
    contributions: List[str] = Field(
        default_factory=list, description="Specific contributions made by the individual"
    )


class CertificationItem(BaseModel):
    certification_name: Optional[str] = Field(None, description="Name of certification or license")
    issuing_organization: Optional[str] = Field(None, description="Issuing authority (e.g., AWS, Cisco)")
    date: Optional[str] = Field(None, description="Date issued or valid through")


class ResumeAnalysisResult(BaseModel):
    personal_information: PersonalInformation = Field(default_factory=PersonalInformation)
    professional_summary: ProfessionalSummary = Field(default_factory=ProfessionalSummary)
    technical_skills: List[str] = Field(
        default_factory=list, description="All technical skills supported by evidence in the resume"
    )
    soft_skills: List[str] = Field(
        default_factory=list, description="Interpersonal and professional soft skills identified"
    )
    education: List[EducationItem] = Field(default_factory=list)
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    additional_information: List[str] = Field(
        default_factory=list, description="Notable achievements, publications, awards, or volunteer activities"
    )


# ---------------------------------------------------------------------------
# API Transport / Response Schemas
# ---------------------------------------------------------------------------

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_path: Optional[str] = None
    processing_status: str
    created_at: str

    class Config:
        from_attributes = True


class ResumeAnalysisResponse(BaseModel):
    id: str
    resume_id: str
    user_id: str
    analysis: ResumeAnalysisResult
    created_at: str

    class Config:
        from_attributes = True


class ResumeDetailResponse(BaseModel):
    resume: ResumeResponse
    analysis: Optional[ResumeAnalysisResult] = None
    extracted_text_preview: Optional[str] = None

