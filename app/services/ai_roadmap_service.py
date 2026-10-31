"""
PATHFORGE AI - Personalized Learning Roadmap Engine (Feature 4)
Generates structured, week-by-week learning roadmaps tailored to the candidate's
actual Skill Gap Analyzer report, preferred duration, and weekly study hours.
Uses genuine resources (docs, free courses, tutorials) with completion tracking.
"""

import json
import logging
import os
import uuid
from typing import Dict, List, Any, Optional

logger = logging.getLogger("pathforge.roadmap_service")

# Genuine, verified learning resources database for technical skills
VERIFIED_RESOURCES = {
    "python": [
        {"name": "Official Python 3 Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "Documentation", "is_free": True},
        {"name": "Real Python Tutorials & Guides", "url": "https://realpython.com/", "type": "Tutorial", "is_free": True},
        {"name": "freeCodeCamp Python Full Course", "url": "https://www.freecodecamp.org/news/python-for-beginners-full-course/", "type": "Video Course", "is_free": True}
    ],
    "fastapi": [
        {"name": "FastAPI Official Interactive Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "Documentation", "is_free": True},
        {"name": "Full Stack FastAPI Template & Architecture", "url": "https://github.com/fastapi/full-stack-fastapi-template", "type": "Repository", "is_free": True}
    ],
    "sql": [
        {"name": "SQLBolt Interactive SQL Lessons", "url": "https://sqlbolt.com/", "type": "Practice Platform", "is_free": True},
        {"name": "PostgreSQL Official Tutorial", "url": "https://www.postgresql.org/docs/current/tutorial.html", "type": "Documentation", "is_free": True}
    ],
    "react": [
        {"name": "React Official Interactive Docs", "url": "https://react.dev/learn", "type": "Documentation", "is_free": True},
        {"name": "freeCodeCamp 10-Hour React Course", "url": "https://www.freecodecamp.org/news/free-react-course-2024/", "type": "Course", "is_free": True}
    ],
    "typescript": [
        {"name": "TypeScript Official Handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "type": "Documentation", "is_free": True},
        {"name": "Total TypeScript Free Tutorials", "url": "https://www.totaltypescript.com/tutorials", "type": "Practice Platform", "is_free": True}
    ],
    "docker": [
        {"name": "Docker Official Getting Started Guide", "url": "https://docs.docker.com/get-started/", "type": "Documentation", "is_free": True},
        {"name": "Play with Docker Interactive Labs", "url": "https://labs.play-with-docker.com/", "type": "Practice Platform", "is_free": True}
    ],
    "git": [
        {"name": "Pro Git Book (Free Online Edition)", "url": "https://git-scm.com/book/en/v2", "type": "Book", "is_free": True},
        {"name": "Learn Git Branching Interactive", "url": "https://learngitbranching.js.org/", "type": "Practice Platform", "is_free": True}
    ],
    "machine learning": [
        {"name": "Scikit-Learn Official User Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "type": "Documentation", "is_free": True},
        {"name": "Coursera Machine Learning Specialization (Free Audit)", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "type": "Course", "is_free": True}
    ],
    "deep learning": [
        {"name": "PyTorch Official Deep Learning Tutorials", "url": "https://pytorch.org/tutorials/", "type": "Documentation", "is_free": True},
        {"name": "fast.ai Practical Deep Learning for Coders", "url": "https://course.fast.ai/", "type": "Course", "is_free": True}
    ],
    "pandas": [
        {"name": "Pandas Official 10-Minutes Tutorial", "url": "https://pandas.pydata.org/docs/user_guide/10min.html", "type": "Documentation", "is_free": True},
        {"name": "Kaggle Learn: Pandas Interactive Course", "url": "https://www.kaggle.com/learn/pandas", "type": "Practice Platform", "is_free": True}
    ],
    "aws": [
        {"name": "AWS Skill Builder Free Digital Training", "url": "https://aws.amazon.com/training/digital/", "type": "Course", "is_free": True},
        {"name": "AWS Ramp-Up Guide: Architect", "url": "https://aws.amazon.com/training/ramp-up-guides/", "type": "Documentation", "is_free": True}
    ],
    "linux": [
        {"name": "Linux Journey Interactive Learning", "url": "https://linuxjourney.com/", "type": "Tutorial", "is_free": True},
        {"name": "OverTheWire Bandit Wargame (Linux CLI)", "url": "https://overthewire.org/wargames/bandit/", "type": "Practice Platform", "is_free": True}
    ],
    "cybersecurity": [
        {"name": "TryHackMe Free Pre-Security Learning Path", "url": "https://tryhackme.com/path/outline/presecurity", "type": "Practice Platform", "is_free": True},
        {"name": "OWASP Top Ten Security Project", "url": "https://owasp.org/www-project-top-ten/", "type": "Documentation", "is_free": True}
    ],
    "ui/ux": [
        {"name": "Figma Official Video Tutorials & Community", "url": "https://help.figma.com/hc/en-us/categories/360002051613-Getting-Started", "type": "Documentation", "is_free": True},
        {"name": "Nielsen Norman Group UX Research Articles", "url": "https://www.nngroup.com/articles/", "type": "Articles", "is_free": True}
    ]
}


def _get_resources_for_skill(skill_name: str) -> List[Dict[str, Any]]:
    """Returns verified learning resources for a given skill with fallback to official dev resources."""
    lower = skill_name.lower()
    for key, res_list in VERIFIED_RESOURCES.items():
        if key in lower or lower in key:
            return res_list

    # Fallback to general high-quality free technical learning resource
    return [
        {
            "name": f"freeCodeCamp {skill_name} Learning Guide",
            "url": "https://www.freecodecamp.org/news/search/?query=" + skill_name.replace(" ", "%20"),
            "type": "Tutorial",
            "is_free": True
        },
        {
            "name": f"DevDocs API Documentation: {skill_name}",
            "url": "https://devdocs.io/",
            "type": "Documentation",
            "is_free": True
        }
    ]


CLAUDE_ROADMAP_PROMPT = """You are the Senior Curriculum Architect for PATHFORGE AI.
Based on the candidate's verified skill gaps, generate a personalized, week-by-week learning plan.

=== STRICT RULES ===
1. Tailor the sequence strictly to the user's missing and improvement skills.
2. Provide realistic weekly objectives and practical exercises.
3. Only recommend genuine learning resources.
4. Output valid JSON adhering to the specified schema.
"""


def generate_deterministic_roadmap(
    skill_gap_report: Dict[str, Any],
    duration_weeks: int = 8,
    hours_per_week: int = 10
) -> Dict[str, Any]:
    """
    Constructs a deterministic, personalized learning roadmap structured into suitable stages
    adapting to the candidate's exact gaps.
    """
    target_career = skill_gap_report.get("target_career", "Software Engineering")
    career_slug = skill_gap_report.get("career_slug", "software-developer")
    missing_skills = skill_gap_report.get("missing_skills", [])
    improvement_skills = skill_gap_report.get("improvement_skills", [])
    matched_skills = skill_gap_report.get("matched_skills", [])

    duration_weeks = max(4, min(duration_weeks, 16))
    hours_per_week = max(3, min(hours_per_week, 40))

    # Determine adapted stages based on gap severity
    has_missing = len(missing_skills) > 0
    has_improve = len(improvement_skills) > 0

    stages: List[Dict[str, Any]] = []
    if has_missing:
        stages.append({"id": "stage_1", "name": "Stage 1: Foundation", "description": "Bridge critical unverified or missing baseline skills."})
    if has_improve:
        stages.append({"id": "stage_2", "name": "Stage 2: Core Skills", "description": "Deepen practical fluency in key framework and database patterns."})
    stages.append({"id": "stage_3", "name": "Stage 3: Intermediate Integration", "description": "Integrate multiple components into cohesive systems with error handling."})
    stages.append({"id": "stage_4", "name": "Stage 4: Practical Application", "description": "Build verifiable portfolio projects demonstrating end-to-end competency."})
    stages.append({"id": "stage_5", "name": "Stage 5: Career Readiness", "description": "Refine testing, code reviews, documentation, and interview problem-solving."})

    # Distribute skills across weeks
    priority_focus = [m["name"] for m in missing_skills if m.get("priority") == "High"]
    other_missing = [m["name"] for m in missing_skills if m.get("priority") != "High"]
    improve_focus = [i["name"] for i in improvement_skills]

    all_gap_skills = priority_focus + other_missing + improve_focus
    if not all_gap_skills:
        all_gap_skills = [m.get("name", "Core Practice") for m in matched_skills[:3]] or ["Modern Architecture", "CI/CD & Testing", "Performance Optimization"]

    weeks: List[Dict[str, Any]] = []
    num_skills = len(all_gap_skills)

    for w_idx in range(1, duration_weeks + 1):
        # Determine assigned skill for this week
        skill_idx = (w_idx - 1) % num_skills
        primary_skill = all_gap_skills[skill_idx]
        resources = _get_resources_for_skill(primary_skill)

        # Stage mapping
        stage_num = 1 if w_idx <= 2 else (2 if w_idx <= 4 else (3 if w_idx <= 6 else 4))
        stage_title = f"Stage {stage_num}"

        is_capstone_week = (w_idx == duration_weeks)

        if is_capstone_week:
            learning_objective = f"Consolidate learning into an end-to-end production capstone demonstrating {target_career} competencies."
            topics = ["Architecture Review", "Security & Error Handling", "Cloud Deployment & Live Demo Link", "README & Portfolio Setup"]
            exercises = [
                f"Deploy complete capstone application integrating {primary_skill}.",
                "Write comprehensive README.md with architecture diagram and live URL.",
                "Conduct full manual walkthrough testing edge cases."
            ]
        elif w_idx <= 2 and has_missing:
            learning_objective = f"Establish solid fundamentals in {primary_skill} with hands-on syntax and core concepts."
            topics = [f"{primary_skill} Syntax & Setup", "Core APIs and Conventions", "Standard Data Manipulation", "Initial Mini-Exercise"]
            exercises = [
                f"Complete introductory interactive tutorial for {primary_skill}.",
                f"Write a standalone script demonstrating fundamental {primary_skill} operations.",
                "Push exercise code to a GitHub practice repository."
            ]
        else:
            learning_objective = f"Deepen architectural mastery and production best practices in {primary_skill}."
            topics = [f"Advanced {primary_skill} Patterns", "Modular Component Design", "Unit & Integration Testing", "Performance Tuning"]
            exercises = [
                f"Build a multi-feature module using {primary_skill} with clean error handling.",
                f"Write automated tests covering happy path and edge cases.",
                "Review code quality against industry linting standards."
            ]

        # Activity breakdown
        activities: List[Dict[str, Any]] = [
            {
                "id": f"act_{uuid.uuid4().hex[:8]}",
                "week_number": w_idx,
                "title": f"Study Concept: {topics[0]}",
                "skill": primary_skill,
                "type": "Concept Learning",
                "estimated_hours": max(1, round(hours_per_week * 0.3)),
                "resources": resources[:2],
                "status": "pending"
            },
            {
                "id": f"act_{uuid.uuid4().hex[:8]}",
                "week_number": w_idx,
                "title": f"Practical Exercise: {exercises[0]}",
                "skill": primary_skill,
                "type": "Hands-on Exercise",
                "estimated_hours": max(2, round(hours_per_week * 0.45)),
                "resources": [resources[0]],
                "status": "pending"
            },
            {
                "id": f"act_{uuid.uuid4().hex[:8]}",
                "week_number": w_idx,
                "title": f"Milestone Verification: {exercises[1]}",
                "skill": primary_skill,
                "type": "Milestone Task",
                "estimated_hours": max(1, round(hours_per_week * 0.25)),
                "resources": [],
                "status": "pending"
            }
        ]

        weeks.append({
            "week_number": w_idx,
            "stage": stage_title,
            "skill": primary_skill,
            "learning_objective": learning_objective,
            "topics": topics,
            "resources": resources,
            "practical_exercises": exercises,
            "expected_outcome": f"Demonstrable code artifact exhibiting working competency in {primary_skill}.",
            "completion_criteria": f"Successfully complete practical exercise and push verified code commit.",
            "estimated_hours": hours_per_week,
            "activities": activities,
            "is_completed": False
        })

    total_activities = sum(len(w["activities"]) for w in weeks)

    return {
        "id": f"rm_{uuid.uuid4().hex[:12]}",
        "target_career": target_career,
        "career_slug": career_slug,
        "duration_weeks": duration_weeks,
        "hours_per_week": hours_per_week,
        "total_weeks": duration_weeks,
        "total_activities": total_activities,
        "completed_activities": 0,
        "progress_percentage": 0.0,
        "stages": stages,
        "weeks": weeks,
        "status": "active"
    }


async def generate_personalized_roadmap(
    skill_gap_report: Dict[str, Any],
    duration_weeks: int = 8,
    hours_per_week: int = 10
) -> Dict[str, Any]:
    """
    Generates a personalized learning roadmap. Uses deterministic engine as foundation,
    and enriches with Claude AI if credentials are available.
    """
    # Deterministic base
    base_roadmap = generate_deterministic_roadmap(skill_gap_report, duration_weeks, hours_per_week)

    # Optional Claude enrichment
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and not anthropic_key.startswith("your-"):
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=anthropic_key)
            model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

            prompt = (
                f"Candidate Target Career: {skill_gap_report.get('target_career')}\n"
                f"Missing Skills: {[m['name'] for m in skill_gap_report.get('missing_skills', [])]}\n"
                f"Improvement Skills: {[i['name'] for i in skill_gap_report.get('improvement_skills', [])]}\n"
                f"Duration: {duration_weeks} weeks, {hours_per_week} hours/week.\n"
                f"Provide a brief 2-sentence pedagogical strategy overview for this candidate."
            )

            resp = await client.messages.create(
                model=model_name,
                max_tokens=250,
                system=CLAUDE_ROADMAP_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            base_roadmap["pedagogical_strategy"] = resp.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Claude roadmap enrichment skipped: {e}")

    if "pedagogical_strategy" not in base_roadmap:
        base_roadmap["pedagogical_strategy"] = (
            f"This personalized {duration_weeks}-week curriculum bridges your highest-priority skill gaps "
            f"sequentially through hands-on implementation and structured project milestones."
        )

    return base_roadmap

