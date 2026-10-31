import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Ensure the project root is in sys.path regardless of working directory
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SUPABASE_URL, SUPABASE_KEY
from app.routers.resume_routes import router as resume_router
from app.routers.career_routes import router as career_router
from app.routers.skill_gap_routes import router as skill_gap_router
from app.routers.roadmap_routes import router as roadmap_router
from app.routers.project_routes import router as project_router
from app.routers.adaptive_routes import router as adaptive_router

app = FastAPI(
    title="PATHFORGE AI",
    description="Your AI Career Transition Companion - Complete Career Intelligence & Adaptive Learning System",
    version="2.5.0"
)

STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)

# Register API Routers
app.include_router(resume_router)
app.include_router(career_router)
app.include_router(skill_gap_router)
app.include_router(roadmap_router)
app.include_router(project_router)
app.include_router(adaptive_router)


@app.get("/", response_class=HTMLResponse, summary="Authentication Page - Sign In & Register")
async def home_auth_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
        }
    )


@app.get("/login", response_class=HTMLResponse, summary="Login Alias")
async def login_alias(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
        }
    )


@app.get("/health", summary="Health check endpoint")
def health():
    return {
        "status": "success",
        "message": "Backend is running successfully",
        "features": [
            "Feature 1: Resume Analysis Engine",
            "Feature 2: AI Career Path Recommender",
            "Feature 3: AI Skill Gap Analyzer (Corrected)",
            "Feature 4: Personalized Roadmap",
            "Feature 5: Project Recommendations",
            "Feature 6: Adaptive Learning"
        ]
    }


@app.get("/resume-analysis", response_class=HTMLResponse, summary="Resume Analysis Web Dashboard")
async def resume_analysis_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="resume_analysis.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
            "active_page": "resume-analysis"
        }
    )


@app.get("/career-recommender", response_class=HTMLResponse, summary="Career Path Recommender Dashboard")
async def career_recommender_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="career_recommender.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
            "active_page": "career-recommender"
        }
    )


@app.get("/skill-gap-analyzer", response_class=HTMLResponse, summary="AI Skill Gap Analyzer Dashboard")
async def skill_gap_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="skill_gap.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
            "active_page": "skill-gap-analyzer"
        }
    )


@app.get("/personalized-roadmap", response_class=HTMLResponse, summary="Personalized Learning Roadmap Dashboard")
async def personalized_roadmap_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="roadmap.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
            "active_page": "personalized-roadmap"
        }
    )


@app.get("/project-recommendations", response_class=HTMLResponse, summary="Project Recommendations & Portfolio Dashboard")
async def project_recommendations_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
            "active_page": "project-recommendations"
        }
    )


@app.get("/adaptive-learning", response_class=HTMLResponse, summary="Adaptive Learning & Intelligence Dashboard")
async def adaptive_learning_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="adaptive.html",
        context={
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
            "active_page": "adaptive-learning"
        }
    )
