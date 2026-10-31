# PATHFORGE AI - Career Intelligence & Transition System

> **Agentic AI Hackathon Project**  
> **Status: Feature 1 (Resume Analysis), Feature 2 (AI Career Path Recommender), & Feature 3 (AI Skill Gap Analyzer) Implemented**

PATHFORGE AI is an agentic AI-powered career transition companion. It integrates three core pillars into a seamless intelligence workflow:
1. **Feature 1: Intelligent Resume Analysis** (Extracts verified skills, projects, and work history without hallucinations)
2. **Feature 2: AI Career Path Recommender** (Matches profile against 13 industry roles to surface top 5 compatible careers)
3. **Feature 3: AI Skill Gap Analyzer** (Classifies skills into Have, Improve, and Not Found with actionable roadmaps and projects)

---

## 1. System Architecture & Features

### Feature 1: Intelligent Resume Analysis
- **Multi-Format Processing**: Full text extraction for `.pdf` (via PyMuPDF) and `.docx` (via python-docx).
- **Strict File Validation**: 5 MB upload limit, MIME/extension verification, magic byte checks (`%PDF-` / OpenXML zip), password protection detection, and scanned document warnings.
- **Nine Structured Dimensions**: Personal information, professional summary, technical skills, soft skills, education, work experience, projects, certifications, and additional achievements.
- **Resilient Persistence**: Multi-tiered hybrid storage manager (Supabase PostgreSQL primary + local cache) ensuring zero retrieval failures.

### Feature 2: AI Career Path Recommender
- **13 Predefined & Expandable Career Roles**:
  1. Software Developer
  2. Frontend Developer
  3. Backend Developer
  4. Full Stack Developer
  5. Python Developer
  6. Data Analyst
  7. Data Scientist
  8. Machine Learning Engineer
  9. AI Engineer
  10. Cloud Engineer
  11. DevOps Engineer
  12. Cybersecurity Analyst
  13. UI/UX Designer
- **Transparent Compatibility Engine**: Evaluates core required skills, recommended toolchains, soft skills, and hands-on projects to calculate realistic match percentages (35% to 96%).
- **Explainable Match Justifications**: Transparently cites candidate achievements, projects, and coursework rather than vague generalizations.
- **Fresher & Student Support**: Credits coursework and academic project evidence even with zero years of formal experience.
- **Target Career Selection**: Enables candidates to select and save their target career in their profile.

### Feature 3: AI Skill Gap Analyzer
- **Three-Tier Skill Classification**:
  - **Category A: Skills You Have**: Supported by evidence in projects or work history.
  - **Category B: Skills to Improve**: Identified in profile, but requiring deeper production mastery.
  - **Category C: Not Found in Profile**: Distinguishes "not found" from "confirmed missing".
- **Priority-Ranked Gap Table**: Categorized into High, Medium, and Low priorities with contextual explanations of why each skill matters.
- **Personalized 3-Phase Learning Roadmap**: Foundation (Weeks 1-3) -> Deepening (Weeks 4-6) -> Capstone (Weeks 7-9).
- **Targeted Portfolio Showcase Projects**: Actionable project blueprints featuring technologies, estimated hours, and expected GitHub outcomes.

---

## 2. Technology Stack

- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic v2
- **Document Processing**: PyMuPDF (`pymupdf`), python-docx
- **AI Models & Extraction**: Claude (Anthropic SDK), OpenAI API, and high-precision domain rule fallback
- **Database & Auth**: Supabase PostgreSQL with Row Level Security (RLS) & Supabase Auth JWT
- **Frontend**: Jinja2, HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Vanilla ES6 JavaScript

---

## 3. Project Structure

```text
PATHFORGE_AI/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application & web route mounting
│   ├── database.py              # Supabase client initialization
│   ├── auth.py                  # JWT auth dependency & user-scoped Supabase client
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── resume_routes.py     # Resume upload, retrieval, and delete API
│   │   ├── career_routes.py     # Career recommendations & target selection API
│   │   └── skill_gap_routes.py  # Skill gap analysis & report retrieval API
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── resume_schema.py     # Resume analysis Pydantic models
│   │   ├── career_schema.py     # Career recommendation Pydantic models
│   │   └── skill_gap_schema.py  # Skill gap report Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_service.py    # Validation, extraction, storage coordination
│   │   ├── career_catalogue.py  # 13 industry role definitions & requirements
│   │   ├── ai_career_service.py # Career matching & top 5 recommendation engine
│   │   ├── ai_skill_gap_service.py # 3-tier classification & roadmap generator
│   │   ├── ai_resume_service.py # Claude / OpenAI structured extractor & fallback
│   │   └── storage_manager.py   # Hybrid Supabase + local resilient persistence
│   ├── templates/
│   │   ├── auth.html            # Sign In & Registration portal
│   │   ├── resume_analysis.html # Feature 1: Resume Analysis dashboard
│   │   ├── career_recommender.html # Feature 2: Career Path Recommender
│   │   └── skill_gap.html       # Feature 3: AI Skill Gap Analyzer
│   └── static/
│       ├── css/
│       │   ├── auth.css
│       │   ├── resume_analysis.css
│       │   └── career_recommender.css
│       └── js/
│           ├── auth.js
│           ├── resume_analysis.js
│           ├── career_recommender.js
│           └── skill_gap.js
│
├── data/
│   └── pathforge_local.db       # Resilient SQLite fallback store
├── migrations/
│   ├── 001_create_resume_analysis.sql # Supabase migration 001
│   └── 002_career_and_skills_system.sql # Complete unified Supabase migration
│
├── tests/
│   ├── test_resume_analysis.py          # 15 automated unit tests
│   ├── test_career_and_skill_gap.py     # 10 automated career & skill gap tests
│   └── test_live_supabase_integration.py # Live Supabase RLS integration tests
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## 4. Setup & Running Locally

### Step 1: Run the Application
```bash
.\.venv\Scripts\python run.py
```
This automatically opens your default browser at `http://127.0.0.1:8000`.

### Step 2: Database Setup (Supabase)
Run the migration script `migrations/002_career_and_skills_system.sql` in your Supabase Project SQL Editor to provision all tables and Row Level Security policies.

### Step 3: Run Test Suite
```bash
# Feature 1: Resume Analysis Tests (15 tests)
.\.venv\Scripts\python tests/test_resume_analysis.py

# Feature 2 & 3: Career Recommender & Skill Gap Tests (10 tests)
.\.venv\Scripts\python tests/test_career_and_skill_gap.py

# Live Supabase Integration Tests
.\.venv\Scripts\python tests/test_live_supabase_integration.py
```
