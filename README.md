<div align="center">

# ⚡ PATHFORGE AI
### *Forge Your Future. One Skill at a Time.*

**The AI-Powered Career Pivot Coach & Continuous Learning Intelligence System**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![UI Design](https://img.shields.io/badge/Theme-Light%203D%20Glassmorphism-4776FF?style=for-the-badge&logo=sketch&logoColor=white)](#-premium-light-3d-design-system)
[![Status](https://img.shields.io/badge/Build-Production%20Ready-success?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](#license)

<br/>

[Explore Features](#-the-six-core-pillars) •
[System Architecture](#-system-architecture) •
[Quickstart Guide](#-quickstart-guide) •
[Design System](#-premium-light-3d-design-system) •
[API & Route Reference](#-api--route-reference)

---

</div>

## 📖 Overview

**PATHFORGE AI** is an enterprise-grade, agentic AI platform engineered to empower students, career changers, and tech professionals to successfully navigate modern career transitions. 

Unlike conventional resume analyzers that produce generic suggestions, PATHFORGE AI acts as a **hyper-personalized career pivot coach**. It verifies actual evidence from your work history, calculates realistic career compatibility scores against 13 industry standards, isolates exact skill gaps, drafts actionable week-by-week roadmaps, provides production-level project blueprints, and continuously calibrates your curriculum via adaptive assessments.

Everything is presented in a **futuristic, ultra-fast, Light-Themed 3D SaaS experience** inspired by Apple Vision Pro, Linear, and Stripe.

---

## 🚀 The Six Core Pillars

PATHFORGE AI bridges the entire career lifecycle across **six seamlessly integrated features**:

```
 📄 Resume Ingestion  ──▶  🎯 Career Matching  ──▶  🔍 Skill Gap Analysis
         │                                                 │
         ▼                                                 ▼
 ⚡ Adaptive Calibration ◀──  💼 Portfolio Projects ◀──  🗺️ 8-Week Roadmap
```

| Feature | Route | Description & Primary Capabilities |
| :--- | :--- | :--- |
| **1. Intelligent Resume Analysis** | [`/resume-analysis`](#feature-1-intelligent-resume-analysis) | Multi-format PDF/DOCX parser extracting 9 structured dimensions (verified skills, projects, metrics) with 0% hallucinations. |
| **2. AI Career Pivot Coach** | [`/career-recommender`](#feature-2-ai-career-pivot-coach) | Matches candidate experience against 13 high-demand tech tracks, surfacing top 5 roles with transparent fit scores (35%–96%). |
| **3. AI Skill Gap Analyzer** | [`/skill-gap-analyzer`](#feature-3-ai-skill-gap-analyzer) | 3-tier classification (*Skills You Have*, *Skills to Improve*, *Not Found*) with severity badges and tailored closing strategies. |
| **4. Personalized Learning Roadmap** | [`/personalized-roadmap`](#feature-4-personalized-learning-roadmap) | Interactive 3D vertical timeline delivering 8 weeks of milestone-driven sprints, task checklists, and live completion velocity. |
| **5. Targeted Portfolio Projects** | [`/project-recommendations`](#feature-5-targeted-portfolio-projects) | Full-stack project blueprints tailored to missing skills with architecture specs, functional requirements, and GitHub tracking. |
| **6. Adaptive Learning Engine** | [`/adaptive-learning`](#feature-6-adaptive-learning-engine) | Real-time diagnostic radar, next-step leverage guidance, and safe, user-approved curriculum re-tuning based on test performance. |

---

## 🎨 Premium Light 3D Design System

The application features a tailored **Light-Themed 3D Glassmorphism** design system engineered for optimal contrast, focus, and visual elegance.

<div align="center">

| Token | Hex Code | Visual Preview | Application Scope |
| :--- | :--- | :---: | :--- |
| **Primary Blue** | `#4776FF` | `🟦` | Primary action buttons, timeline nodes, active highlights |
| **Deep Navy** | `#172554` | `🪨` | Brand contrast, headings, primary icons |
| **Main Canvas** | `#F8FAFF` | `⚪` | Main body background canvas |
| **Elevated Surface** | `#EFF5FF` | `🔲` | Secondary backgrounds, sidebar drawer, table headers |
| **Accent Sky** | `#75C8FF` | `🌐` | 3D glow accents, interactive borders, card hover rings |
| **Accent Purple** | `#A78BFA` | `🔮` | AI gradient highlights, badge accents |
| **Text Primary** | `#172033` | `⬛` | Slate 900 high-legibility headings |
| **Text Muted** | `#64748B` | `◽` | Slate 500 descriptive labels, subtitles |

</div>

### Key Frontend Architecture Highlights
- **Zero-Dependency 3D Card Tilt**: Smooth, high-performance card tilt rendered via `requestAnimationFrame` and CSS 3D matrix transforms (`perspective(1000px) rotateX(...) rotateY(...) scale3d(1.02, 1.02, 1.02)`).
- **Glassmorphism Elevation**: Multi-tiered shadow depth (`0 20px 40px -15px rgba(23, 37, 84, 0.08)`) with semi-transparent frosted acrylic cards.
- **SaaS Responsive Shell**: Collapsible sidebar, sticky topbar with live user state and breadcrumbs, and floating toast notifications.
- **Micro-Interactions**: Animated progress gauges, step indicators, expandable milestone accordions, and tactile button states.

---

## 💻 Feature Deep-Dive

### Feature 1: Intelligent Resume Analysis
- **Multi-Format Processing**: Extracts raw content from `.pdf` (via PyMuPDF) and `.docx` (via `python-docx`).
- **File Validation Engine**: 5 MB upload protection, MIME/extension verification, binary magic byte checks (`%PDF-` / OpenXML), encrypted PDF detection, and OCR warning heuristics.
- **Structured Dimension Extraction**: Parses identity, professional summary, technical proficiencies, soft skills, educational records, work history, verified projects, certifications, and achievements.
- **Hybrid Storage Resilience**: Saves directly to Supabase PostgreSQL (secured via Row Level Security), with automatic local SQLite offline caching.

### Feature 2: AI Career Pivot Coach
- **13 Supported Role Trajectories**:
  1. Full Stack Developer
  2. Frontend Developer
  3. Backend Developer
  4. Python Developer
  5. Software Developer
  6. Data Analyst
  7. Data Scientist
  8. Machine Learning Engineer
  9. AI Engineer
  10. Cloud Engineer
  11. DevOps Engineer
  12. Cybersecurity Analyst
  13. UI/UX Designer
- **Transparent Match Justifications**: Synthesizes verified coursework, personal projects, and job experience to assign realistic fit scores (35% to 96%) without inflated praise.
- **Fresher & Career Changer Support**: Credits academic projects and self-taught portfolios even when formal commercial experience is 0 years.

### Feature 3: AI Skill Gap Analyzer
- **Three-Tier Classification**:
  - `Category A (Skills You Have)`: Concrete evidence found in work history or code repositories.
  - `Category B (Skills to Improve)`: Found in candidate profile, but lacking production-level depth.
  - `Category C (Not Found)`: Critical role prerequisites missing from the candidate's portfolio.
- **Priority Ranking**: Flags missing competencies by urgency (*High Priority*, *Medium Priority*, *Good to Have*) with plain-English rationales explaining *why* recruiters require them.

### Feature 4: Personalized Learning Roadmap
- **8-Week Milestone Journey**: Automatically generated from the candidate's exact skill gaps and weekly study bandwidth.
- **Three Core Phases**:
  - **Weeks 1–3 (Foundation)**: Core syntax, tools, protocols, and architectural fundamentals.
  - **Weeks 4–6 (Deepening & Integration)**: Real-world workflows, API integrations, and database schemas.
  - **Weeks 7–8 (Capstone & Production)**: End-to-end deployment, unit testing, and portfolio hardening.
- **Progress Tracking**: Interactive activity checkboxes with dynamic roadmap percentage calculation.

### Feature 5: Targeted Portfolio Projects
- **Gap-Targeted Blueprints**: Generates practical, recruiter-impressing project specifications built specifically to prove competence in missing skills.
- **Architectural Blueprints**: Includes component diagrams, database schemas, functional requirements, testing criteria, and deployment recommendations.
- **Showcase Portfolio Tracker**: Dedicated workspace to store active projects, track development statuses (*Planning*, *In Progress*, *Completed*), and link live demo and GitHub repository URLs.

### Feature 6: Adaptive Learning Engine & Dedicated Quizzes
- **Velocity Metrics**: Visualizes roadmap completion percentage, active weekly tasks, completed projects, and average assessment score.
- **"What Should I Learn Next?" Card**: Analyzes current learning velocity to suggest the single highest-leverage activity for maximum momentum.
- **Interactive Stepper Quiz Engine**:
  - Accessible via `/quizzes` or topic pills inside the Adaptive Learning dashboard.
  - Generates 3-question targeted multiple-choice assessments for any tech topic (Python, Docker, SQL, React, etc.).
  - Complete stepper UI with progress bar, radio selection cards, instant scoring, circular gauge, and explanation breakdowns.
- **Safe Curriculum Adaptation**: Uncovers recurring weak areas and proposes non-destructive roadmap adjustments that users can accept or decline with a single click.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (Light 3D SaaS)"]
        UI_Land["Landing Page (/)"]
        UI_Auth["Auth Portal (/login, /signup)"]
        UI_Dash["Command Center (/dashboard)"]
        UI_Feat["6 Core Features & Quizzes (/quizzes)"]
    end

    subgraph Server["FastAPI Backend (Port 8000)"]
        Router["FastAPI Application Routers"]
        AuthDep["Supabase JWT Auth Guard"]
        Parser["Document Extraction (PyMuPDF / python-docx)"]
        
        subgraph Services["Core Intelligence Services"]
            S_Resume["Resume Analysis Service"]
            S_Career["Career Catalogue & Matching Engine"]
            S_Gap["Skill Gap & Roadmap Engine"]
            S_Project["Project Recommendation Service"]
            S_Adapt["Adaptive Learning & Quiz Engine"]
        end
        
        subgraph Storage["Resilient Hybrid Storage"]
            SupabaseDB[("Primary: Supabase PostgreSQL (RLS)")]
            SQLiteDB[("Offline Fallback: Local SQLite Store")]
        end
    end

    subgraph AI["AI Providers"]
        Claude["Anthropic Claude 3.5 Sonnet"]
        OpenAI["OpenAI GPT-4o-mini"]
        RuleFallback["Domain Rule Heuristic Engine"]
    end

    Client -->|HTTP / JSON Requests| Router
    Router --> AuthDep
    AuthDep --> Services
    Services --> Parser
    Services --> AI
    Services --> Storage
```

---

## 🗂️ Project Directory Tree

```text
PATHFORGE-AI/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application, static mounting & web routes
│   ├── database.py              # Supabase client initialization & environment verification
│   ├── auth.py                  # JWT auth dependency & user-scoped client resolver
│   │
│   ├── routers/                 # Modular API endpoints
│   │   ├── resume_routes.py     # Resume upload, parse, and retrieval API
│   │   ├── career_routes.py     # Career recommendations & target selection API
│   │   ├── skill_gap_routes.py  # Skill gap analysis & priority matrix API
│   │   ├── roadmap_routes.py    # Learning roadmap generation & progress API
│   │   ├── project_routes.py    # Project recommendation & portfolio links API
│   │   └── adaptive_routes.py   # Adaptive velocity, quiz generation & scoring API
│   │
│   ├── schemas/                 # Strict Pydantic v2 validation models
│   │   ├── resume_schema.py
│   │   ├── career_schema.py
│   │   ├── skill_gap_schema.py
│   │   ├── roadmap_schema.py
│   │   ├── project_schema.py
│   │   └── adaptive_schema.py
│   │
│   ├── services/                # Business logic & AI orchestration
│   │   ├── resume_service.py    # Document parsing & validation pipeline
│   │   ├── career_catalogue.py  # 13 industry role definitions & requirements
│   │   ├── ai_career_service.py # Career matching & score calculation engine
│   │   ├── ai_skill_gap_service.py # 3-tier classification & gap analysis
│   │   ├── roadmap_service.py   # 8-week structured roadmap generator
│   │   ├── project_service.py   # Portfolio project blueprint generator
│   │   ├── adaptive_service.py  # Quiz creation, scoring & roadmap adaptation
│   │   ├── ai_resume_service.py # Claude / OpenAI structured extractor & fallback
│   │   └── storage_manager.py   # Hybrid Supabase + SQLite persistence
│   │
│   ├── static/                  # Production frontend assets
│   │   ├── css/
│   │   │   ├── theme-3d.css     # Unified Light 3D design system & tokens
│   │   │   ├── resume_analysis.css
│   │   │   ├── career_recommender.css
│   │   │   └── auth.css
│   │   └── js/
│   │       ├── app-shell.js     # 3D tilt, auth listener, toasts, sidebar drawer
│   │       ├── auth.js          # Supabase Sign In / Sign Up handler
│   │       ├── dashboard.js     # Command Center metrics loader
│   │       ├── resume_analysis.js # Resume upload & results rendering
│   │       ├── career_recommender.js # Career match explorer & modal
│   │       ├── skill_gap.js     # Skill gap breakdown & matrix
│   │       ├── roadmap.js       # Timeline interaction & progress tracker
│   │       ├── projects.js      # Portfolio projects & blueprint guide
│   │       ├── adaptive.js      # Adaptive feedback & adjustment resolver
│   │       ├── quizzes.js       # Dedicated stepper quiz engine
│   │       ├── profile.js       # Candidate profile manager
│   │       └── settings.js      # Learning preferences & cache reset
│   │
│   └── templates/               # Jinja2 HTML views (Light 3D SaaS)
│       ├── base.html            # Responsive master layout shell
│       ├── landing.html         # High-converting 3D landing page
│       ├── auth.html            # Split-screen 3D authentication portal
│       ├── dashboard.html       # SaaS Command Center dashboard
│       ├── resume_analysis.html # Feature 1: Resume Analyzer
│       ├── career_recommender.html # Feature 2: Career Pivot Coach
│       ├── skill_gap.html       # Feature 3: Skill Gap Analyzer
│       ├── roadmap.html         # Feature 4: Learning Roadmap
│       ├── projects.html        # Feature 5: Projects & Portfolio
│       ├── adaptive.html        # Feature 6: Adaptive Learning Engine
│       ├── quizzes.html         # Dedicated Interactive Quizzes Engine
│       ├── profile.html         # Candidate Profile & Career Track
│       └── settings.html        # Preferences & Settings
│
├── data/
│   └── pathforge_local.db       # Local SQLite fallback storage
│
├── migrations/                  # Supabase PostgreSQL DDL schemas
│   ├── 001_create_resume_analysis.sql
│   ├── 002_career_and_skills_system.sql
│   └── 003_complete_career_intelligence_system.sql
│
├── tests/                       # Automated test suite
│   ├── test_resume_analysis.py
│   ├── test_career_and_skill_gap.py
│   ├── test_features_3_4_5_6.py
│   └── test_live_supabase_integration.py
│
├── .env.example                 # Environment configuration template
├── requirements.txt             # Python project dependencies
├── run.py                       # One-click server launcher with browser auto-open
└── README.md
```

---

## ⚡ Quickstart Guide

### Prerequisites
* **Python 3.10+** (Tested on Python 3.12 & 3.13)
* **Git**
* A free [Supabase](https://supabase.com) account (for PostgreSQL database & Auth)

---

### Step 1: Clone Repository
```bash
git clone https://github.com/mayureshpatil7557-ops/PATHFORGE-AI.git
cd PATHFORGE-AI
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-publishable-key

# Optional: Supabase JWT Secret (for local zero-latency token verification)
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# AI Model Provider (Anthropic Claude OR OpenAI)
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Alternative: OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```
*(Note: If no AI API key is provided, the platform automatically utilizes its high-precision domain heuristic fallback engine, ensuring the app remains fully functional out of the box!)*

### Step 5: Database Setup (Supabase)
Run the SQL migrations in your **Supabase Dashboard -> SQL Editor**:
1. Execute `migrations/001_create_resume_analysis.sql`
2. Execute `migrations/002_career_and_skills_system.sql`
3. Execute `migrations/003_complete_career_intelligence_system.sql`

This creates all tables, indexes, and Row Level Security (RLS) policies guaranteeing user data isolation.

### Step 6: Launch Application
```bash
python run.py
```
This automatically boots the FastAPI server on `http://127.0.0.1:8000` and opens your default browser!

---

## 🌐 API & Route Reference

### Web Pages (Jinja2 HTML Views)
| Path | Method | View Description |
| :--- | :---: | :--- |
| `/` | `GET` | 3D Interactive Landing Page |
| `/login` / `/signup` / `/auth` | `GET` | Split-Screen 3D Authentication Portal |
| `/dashboard` | `GET` | SaaS Command Center Dashboard |
| `/resume-analysis` | `GET` | Feature 1: Resume Upload & Analysis Workspace |
| `/career-recommender` | `GET` | Feature 2: Career Pivot Coach & Role Explorer |
| `/skill-gap-analyzer` | `GET` | Feature 3: Skill Gap Matrix & Breakdown |
| `/personalized-roadmap` | `GET` | Feature 4: 8-Week Interactive Learning Timeline |
| `/project-recommendations` | `GET` | Feature 5: Projects & Portfolio Manager |
| `/adaptive-learning` | `GET` | Feature 6: Adaptive Learning Intelligence Engine |
| `/quizzes` | `GET` | Interactive Topic Stepper Quiz Engine |
| `/profile` | `GET` | Candidate Profile & Verified Competencies |
| `/settings` | `GET` | Learning Bandwidth & Workspace Preferences |
| `/health` | `GET` | System Health Check API |

---

### Core REST API Endpoints
| Endpoint | Method | Auth Required | Purpose |
| :--- | :---: | :---: | :--- |
| `/resume/analyze` | `POST` | Yes | Uploads and processes `.pdf` or `.docx` resume. |
| `/resume/latest` | `GET` | Yes | Retrieves latest parsed resume profile. |
| `/career/recommend` | `POST` | Yes | Generates top 5 career recommendations based on profile. |
| `/career/select-target` | `POST` | Yes | Persists selected target career role. |
| `/skill-gap/analyze` | `POST` | Yes | Evaluates gaps between current profile and target career. |
| `/roadmap/generate` | `POST` | Yes | Generates personalized 8-week learning milestones. |
| `/roadmap/current` | `GET` | Yes | Fetches active roadmap and activity completion statuses. |
| `/roadmap/activity/toggle` | `POST` | Yes | Toggles completion status of a roadmap activity. |
| `/projects/generate` | `POST` | Yes | Creates targeted portfolio project blueprints from gaps. |
| `/projects/portfolio` | `GET` | Yes | Retrieves saved and active showcase projects. |
| `/projects/update-status` | `POST` | Yes | Updates GitHub repository and live deployment URLs. |
| `/adaptive/overview` | `GET` | Yes | Returns velocity metrics and overall roadmap progress. |
| `/adaptive/next` | `GET` | Yes | Recommends optimal next learning action. |
| `/adaptive/weak-areas` | `GET` | Yes | Diagnostics for demonstrated vs. needs-practice skills. |
| `/adaptive/quiz` | `GET` | Yes | Generates a 3-question assessment for any specified skill. |
| `/adaptive/quiz/submit` | `POST` | Yes | Evaluates answers, records score, and returns feedback. |
| `/adaptive/propose-adjustments` | `POST` | Yes | Evaluates metrics to propose adaptive curriculum tweaks. |

---

## 🔒 Security & Data Privacy

* **Row Level Security (RLS)**: Every database table (`resumes`, `career_recommendations`, `skill_gap_reports`, `learning_roadmaps`, `user_projects`, `learning_assessments`) enforces PostgreSQL RLS policies tied to `auth.uid()`, guaranteeing candidates can only access their own records.
* **Strict Upload Sanitization**: Files undergo binary magic-byte checks (`%PDF-`, PK zip headers), MIME validation, and strict 5 MB file size constraints.
* **Zero-Hallucination Grounding**: AI services use strictly bounded schema extraction with deterministic fallback rules, ensuring false certifications or fabricated skills are never recorded.

---

## 🧪 Testing

PATHFORGE AI comes equipped with comprehensive unit and integration test suites:

```bash
# Run Resume Analysis tests
python -m unittest tests/test_resume_analysis.py

# Run Career Recommender & Skill Gap tests
python -m unittest tests/test_career_and_skill_gap.py

# Run Features 3, 4, 5 & 6 End-to-End tests
python -m unittest tests/test_features_3_4_5_6.py
```

---

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are warmly welcomed!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">

**Built with passion for the Agentic AI Hackathon.**  
*Empowering the next generation of technologists to conquer their career transitions.*

[Back to Top ↑](#-pathforge-ai)

</div>
