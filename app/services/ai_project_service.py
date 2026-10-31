"""
PATHFORGE AI - Project Recommendations & Portfolio Engine (Feature 5)
Recommends practical, portfolio-grade projects targeting candidate skill gaps.
Provides complete architectural blueprints, milestones, testing requirements,
deployment guidance, and portfolio tracking.
"""

import json
import logging
import os
import uuid
from typing import Dict, List, Any, Optional

logger = logging.getLogger("pathforge.project_service")

# Project Templates Database mapped to careers and focus gaps
CAREER_PROJECT_BLUEPRINTS: Dict[str, List[Dict[str, Any]]] = {
    "software-developer": [
        {
            "title": "Scalable Task & Workflow Management API",
            "difficulty": "Intermediate",
            "estimated_hours": "18-24 hours",
            "prerequisites": "Basic Python or Java syntax and fundamental OOP principles.",
            "skills_addressed": ["Python", "FastAPI", "SQL", "Unit Testing", "Git"],
            "problem_statement": "Teams require an automated, auditable system to coordinate async task assignments, status state machines, and email notifications without race conditions.",
            "objectives": ["Design a relational schema with foreign keys and task transitions.", "Implement REST endpoints with JWT authentication.", "Write 80%+ unit test coverage with pytest."],
            "functional_requirements": [
                "User registration and role-based access (Admin, Member, Viewer).",
                "CRUD operations for tasks with priorities, tags, and due dates.",
                "State machine workflow validation (Pending -> In Progress -> Completed).",
                "Automated pagination and full-text search by task title."
            ],
            "suggested_modules": ["auth_service", "task_controller", "database_models", "notification_worker", "test_suite"],
            "deliverables": ["GitHub repository with clean Git commits", "Automated CI test workflow via GitHub Actions", "Postman / OpenAPI interactive documentation"],
            "architecture_guide": "Layered architecture: Router Layer -> Service/Business Logic -> Data Access Object (DAO) -> PostgreSQL database.",
            "milestones": [
                "Milestone 1: Setup virtual environment, Pydantic schemas, and SQLAlchemy / SQL models.",
                "Milestone 2: Implement JWT authentication and role-based endpoint protection.",
                "Milestone 3: Build task CRUD endpoints, state transitions, and search filters.",
                "Milestone 4: Write unit test suite with fixtures and configure GitHub Actions CI."
            ],
            "testing_requirements": "Test status code outputs, invalid payloads (422), unauthenticated access (401), and unauthorized task deletion (403).",
            "deployment_suggestions": "Deploy containerized FastAPI application on Render or Railway with managed PostgreSQL.",
            "github_portfolio_guidance": "Include clear README with architectural diagram, API endpoint tables, local setup instructions, and test command."
        },
        {
            "title": "Algorithmic Code Execution & Evaluator Sandbox",
            "difficulty": "Advanced",
            "estimated_hours": "30-40 hours",
            "prerequisites": "Intermediate Python, Linux process management, and Docker basics.",
            "skills_addressed": ["Python", "Docker", "Linux", "Data Structures", "Asyncio"],
            "problem_statement": "Educational platforms need an isolated, timeout-guarded environment to safely execute untrusted candidate code submissions.",
            "objectives": ["Build a sandboxed runner executing user code inside ephemeral Docker containers.", "Enforce strict CPU and memory limits.", "Validate submission outputs against hidden test cases."],
            "functional_requirements": ["Submission ingestion queue.", "Ephemeral container creation and destruction.", "Time-limit and memory-limit enforcement.", "Test result aggregation and score reporting."],
            "suggested_modules": ["submission_api", "docker_runner", "sandbox_evaluator", "metrics_logger"],
            "deliverables": ["Production-ready runner service", "Docker compose configuration", "Live demo or video demonstration"],
            "architecture_guide": "Async worker pattern: Web API enqueues submission -> Worker spins up isolated Docker container with read-only filesystem -> Captures stdout/stderr -> Evaluates output against assertions.",
            "milestones": [
                "Milestone 1: Scaffold API and submission data models.",
                "Milestone 2: Write Docker SDK client launching lightweight scratch containers.",
                "Milestone 3: Implement timeout guards and exit-code inspectors.",
                "Milestone 4: Integrate test case assertion engine and security hardening."
            ],
            "testing_requirements": "Test infinite loop termination, fork bomb resistance, and file system write rejection.",
            "deployment_suggestions": "Deploy on AWS EC2 or DigitalOcean Droplet with Docker daemon access.",
            "github_portfolio_guidance": "Highlight security sandboxing principles, threat model considerations, and memory benchmarks in README."
        }
    ],
    "machine-learning-engineer": [
        {
            "title": "End-to-End Customer Churn Prediction & Model Serving Pipeline",
            "difficulty": "Intermediate",
            "estimated_hours": "20-28 hours",
            "prerequisites": "Python, Pandas, and foundational understanding of classification algorithms.",
            "skills_addressed": ["Python", "Scikit-Learn", "Pandas", "FastAPI", "MLOps & Model Serving", "Docker"],
            "problem_statement": "Subscription businesses face revenue loss from customer attrition and require an automated, real-time risk scoring API.",
            "objectives": ["Train an interpretable Gradient Boosting classifier on customer behavior data.", "Serialize the trained model with versioned artifacts.", "Expose low-latency prediction endpoint via FastAPI."],
            "functional_requirements": [
                "Data cleaning, imputation, and feature engineering pipeline.",
                "Cross-validated model evaluation with ROC-AUC and Precision-Recall metrics.",
                "Real-time prediction REST API validating incoming customer attributes.",
                "Feature importance explanation output explaining why churn is predicted."
            ],
            "suggested_modules": ["data_pipeline", "model_trainer", "artifact_registry", "inference_api", "test_suite"],
            "deliverables": ["Jupyter notebook with EDA and cross-validation analysis", "FastAPI inference service in Docker", "SHAP feature importance visualization"],
            "architecture_guide": "Training Pipeline -> Serialized Pipeline Artifact (.joblib) -> FastAPI Inference Server -> Response with Probability & Top Drivers.",
            "milestones": [
                "Milestone 1: Exploratory data analysis, handling categorical features with OneHotEncoder.",
                "Milestone 2: Model comparison (Logistic Regression vs. Random Forest vs. XGBoost).",
                "Milestone 3: Package model into Scikit-Learn Pipeline and save artifact.",
                "Milestone 4: Build FastAPI `/predict` endpoint with Pydantic payload and containerize."
            ],
            "testing_requirements": "Test deterministic predictions against benchmark cases, invalid schema rejections, and latency < 100ms.",
            "deployment_suggestions": "Deploy containerized model on Render or AWS ECS.",
            "github_portfolio_guidance": "Document model evaluation metrics (ROC-AUC), business ROI justification, and live API request example."
        },
        {
            "title": "Production Deep Learning Image Classifier with Drift Monitoring",
            "difficulty": "Advanced",
            "estimated_hours": "35-45 hours",
            "prerequisites": "Intermediate PyTorch/TensorFlow and deep learning foundations.",
            "skills_addressed": ["Deep Learning", "TensorFlow or PyTorch", "Docker", "MLOps", "Python"],
            "problem_statement": "Computer vision models deployed to production suffer accuracy degradation over time due to distribution drift.",
            "objectives": ["Fine-tune a ResNet/EfficientNet model on domain images.", "Implement data drift detection monitoring inference inputs.", "Build an automated retraining trigger."],
            "functional_requirements": ["Transfer learning pipeline with data augmentation.", "Batch and real-time image inference endpoint.", "Out-of-distribution (OOD) confidence detection.", "Drift metrics logger."],
            "suggested_modules": ["model_architecture", "dataset_loaders", "drift_detector", "serving_engine"],
            "deliverables": ["Trained model weights", "Inference container with GPU/CPU support", "Monitoring dashboard"],
            "architecture_guide": "PyTorch fine-tuned model served with ONNX Runtime or FastAPI -> Prediction logger -> Evidentiary drift statistical checks.",
            "milestones": [
                "Milestone 1: Transfer learning and validation set evaluation.",
                "Milestone 2: Export model to ONNX for 3x latency acceleration.",
                "Milestone 3: Implement inference API with image preprocessing.",
                "Milestone 4: Add data distribution Kolmogorov-Smirnov drift checks."
            ],
            "testing_requirements": "Test inference output shape, corrupted image handling, and drift detector sensitivity.",
            "deployment_suggestions": "Deploy with Docker on Hugging Face Spaces or AWS EC2.",
            "github_portfolio_guidance": "Include sample test images, confusion matrix, loss curves, and benchmark inference latency."
        }
    ],
    "ai-engineer": [
        {
            "title": "Enterprise Document RAG Knowledge Assistant",
            "difficulty": "Intermediate",
            "estimated_hours": "20-26 hours",
            "prerequisites": "Python, basic understanding of embeddings and vector similarity.",
            "skills_addressed": ["Python", "RAG Architectures", "Vector Databases & Embeddings", "FastAPI", "Prompt Engineering"],
            "problem_statement": "Employees waste hundreds of hours searching complex internal PDF policy manuals and engineering documentation.",
            "objectives": ["Chunk and embed unstructured PDF documents.", "Store high-dimensional vectors in ChromaDB/Pinecone.", "Synthesize grounded answers using Claude API with exact citations."],
            "functional_requirements": [
                "Document ingestion and recursive character chunking.",
                "Vector similarity search with metadata filtering.",
                "Hallucination guardrails and source citation links.",
                "Conversational history memory retention."
            ],
            "suggested_modules": ["document_ingestion", "vector_store", "retriever_engine", "prompt_manager", "chat_api"],
            "deliverables": ["Interactive web chat interface", "FastAPI backend with `/chat` and `/upload` endpoints", "Sample indexed knowledge corpus"],
            "architecture_guide": "Client Query -> Embedding Model -> Vector DB Retrieval (Top K) -> Augmented System Prompt -> Claude LLM -> Grounded Answer with Citations.",
            "milestones": [
                "Milestone 1: PDF text extraction and chunking strategies (500 tokens with 50 token overlap).",
                "Milestone 2: Vector embedding generation and indexing in ChromaDB/Supabase pgvector.",
                "Milestone 3: Construct prompt template demanding verbatim quotes from context.",
                "Milestone 4: Build FastAPI streaming response endpoint and test citation veracity."
            ],
            "testing_requirements": "Verify that queries with no relevant documents return 'I cannot answer based on provided documents' rather than hallucinating.",
            "deployment_suggestions": "Deploy FastAPI on Render with Supabase pgvector or persistent ChromaDB volume.",
            "github_portfolio_guidance": "Include video walkthrough, example Q&A showing accurate citations, and benchmark retrieval latency."
        }
    ],
    "frontend-developer": [
        {
            "title": "High-Performance Analytics Dashboard with Next.js & TypeScript",
            "difficulty": "Intermediate",
            "estimated_hours": "18-24 hours",
            "prerequisites": "Basic JavaScript and HTML/CSS knowledge.",
            "skills_addressed": ["TypeScript", "React", "Next.js", "Responsive Design", "Tailwind CSS / Bootstrap"],
            "problem_statement": "Business teams need responsive real-time financial telemetry dashboards with dark mode and zero layout shift.",
            "objectives": ["Build a type-safe interactive dashboard with reusable component architecture.", "Implement dynamic data filtering and chart visualizations.", "Ensure WCAG AAA accessibility compliance."],
            "functional_requirements": [
                "KPI statistic cards with trend indicator badges.",
                "Interactive time-series line and bar charts.",
                "Filter controls by date range and category.",
                "Accessible dark/light theme toggle with local storage persistence."
            ],
            "suggested_modules": ["components/charts", "components/kpi_cards", "hooks/useDashboardData", "types/telemetry"],
            "deliverables": ["Live deployment on Vercel", "Lighthouse score > 95 across Performance & Accessibility", "Clean GitHub repo"],
            "architecture_guide": "Next.js App Router -> React Server Components for initial load -> Client Components for filter state -> Chart.js/Recharts.",
            "milestones": [
                "Milestone 1: Setup Next.js with TypeScript and Tailwind CSS.",
                "Milestone 2: Build atomic UI components (Button, Card, Badge, Input).",
                "Milestone 3: Integrate interactive data charts with responsive viewports.",
                "Milestone 4: Perform accessibility audit and optimize asset loading."
            ],
            "testing_requirements": "Test component rendering with React Testing Library, responsive layout at 375px and 1440px.",
            "deployment_suggestions": "Deploy to Vercel with automatic preview deployments on pull requests.",
            "github_portfolio_guidance": "Include live preview link, Lighthouse audit badge, and mobile responsiveness screenshots."
        }
    ]
}


def get_default_project_for_skill(skill: str, career_title: str, difficulty: str = "Beginner") -> Dict[str, Any]:
    """Generates a structured project blueprint for any individual skill gap."""
    return {
        "title": f"Hands-on {skill} Implementation System",
        "difficulty": difficulty,
        "estimated_hours": "12-16 hours" if difficulty == "Beginner" else "20-25 hours",
        "prerequisites": f"Foundational knowledge of {skill} syntax and developer environment setup.",
        "skills_addressed": [skill, "Git", "Clean Architecture"],
        "problem_statement": f"Develop a modular, verifiable software component demonstrating proficiency in {skill} to support {career_title} workflows.",
        "objectives": [f"Implement core patterns using {skill}.", "Structure modular, maintainable code with unit tests.", "Document project architecture clearly for technical recruiters."],
        "functional_requirements": [
            f"Core operations leveraging {skill} best practices.",
            "Automated input validation and error handling.",
            "Configuration management via environment variables.",
            "Test suite verifying primary functionality."
        ],
        "suggested_modules": ["core_logic", "data_layer", "interfaces", "test_suite"],
        "deliverables": [f"Public GitHub repository with {skill} implementation", "Technical documentation in README.md"],
        "architecture_guide": "Single responsibility modules with decoupled interfaces and automated unit testing.",
        "milestones": [
            f"Milestone 1: Scaffold repository and configure {skill} development environment.",
            f"Milestone 2: Implement core business logic and primary {skill} features.",
            "Milestone 3: Add automated unit tests and error handling.",
            "Milestone 4: Write comprehensive README and publish repository."
        ],
        "testing_requirements": "Unit tests verifying valid cases and error conditions.",
        "deployment_suggestions": "Publish to GitHub and deploy to Render, Vercel, or cloud container as appropriate.",
        "github_portfolio_guidance": f"Document why {skill} was selected, key design trade-offs, and steps to run locally."
    }


def generate_recommended_projects(
    skill_gap_report: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Produces 3-4 personalized project recommendations addressing the candidate's exact skill gaps.
    Classifies difficulty based on current candidate profile evidence.
    """
    career_slug = skill_gap_report.get("career_slug", "software-developer")
    career_title = skill_gap_report.get("target_career", "Software Engineering")
    missing_skills = skill_gap_report.get("missing_skills", [])
    improvement_skills = skill_gap_report.get("improvement_skills", [])
    coverage_pct = skill_gap_report.get("coverage_percentage", 0.0)

    # 1. Check if predefined blueprints exist for career
    predefined = CAREER_PROJECT_BLUEPRINTS.get(career_slug, [])
    projects: List[Dict[str, Any]] = []

    for bp in predefined:
        p = dict(bp)
        p["id"] = f"proj_{uuid.uuid4().hex[:10]}"
        p["target_career"] = career_title
        p["status"] = "recommended"
        projects.append(p)

    # 2. Add tailored projects specifically for highest missing/improvement skills
    gap_skills = [m["name"] for m in missing_skills[:2]] + [i["name"] for i in improvement_skills[:2]]
    for skill in gap_skills:
        # Determine appropriate difficulty based on user coverage
        diff = "Beginner" if coverage_pct < 35 else ("Intermediate" if coverage_pct < 70 else "Advanced")
        custom_proj = get_default_project_for_skill(skill, career_title, diff)
        custom_proj["id"] = f"proj_{uuid.uuid4().hex[:10]}"
        custom_proj["target_career"] = career_title
        custom_proj["status"] = "recommended"
        projects.append(custom_proj)

    # Return top 4 distinct projects
    return projects[:4]

