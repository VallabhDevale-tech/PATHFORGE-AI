"""
PATHFORGE AI - Adaptive Learning & Continuous Intelligence Engine (Feature 6)
Monitors user progress across Roadmaps (Feature 4), Projects (Feature 5), and Assessments.
Identifies weak areas, powers "What Should I Learn Next?", generates topic quizzes,
and proposes non-destructive roadmap adjustments with user approval.
"""

import json
import logging
import os
import uuid
from typing import Dict, List, Any, Optional

logger = logging.getLogger("pathforge.adaptive_service")

# Static high-quality quiz bank for foundational assessment checks
STATIC_QUIZ_BANK: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {
            "id": "q_py_1",
            "question": "Which of the following data structures in Python is immutable?",
            "options": ["List", "Dictionary", "Tuple", "Set"],
            "correct_index": 2,
            "explanation": "Tuples in Python are immutable; once created, their elements cannot be modified or reassigned."
        },
        {
            "id": "q_py_2",
            "question": "What is the primary difference between a generator function and a standard function in Python?",
            "options": [
                "Generators run on a separate OS thread.",
                "Generators use 'yield' to produce values lazily on demand rather than storing everything in memory.",
                "Generators cannot accept arguments.",
                "Generators can only return integer values."
            ],
            "correct_index": 1,
            "explanation": "Generators produce sequence values lazily using 'yield', drastically conserving memory for large datasets."
        },
        {
            "id": "q_py_3",
            "question": "In Python's asyncio model, what keyword pauses coroutine execution until an awaitable object finishes?",
            "options": ["defer", "pause", "async", "await"],
            "correct_index": 3,
            "explanation": "'await' yields control back to the event loop until the awaited future or coroutine completes."
        }
    ],
    "sql": [
        {
            "id": "q_sql_1",
            "question": "What is the primary purpose of the SQL GROUP BY clause?",
            "options": [
                "To sort output rows in ascending order.",
                "To arrange identical data into groups for aggregate functions like COUNT, SUM, or AVG.",
                "To join two tables on foreign keys.",
                "To limit the total number of returned rows."
            ],
            "correct_index": 1,
            "explanation": "GROUP BY partitions result rows so aggregate calculations can run independently per group."
        },
        {
            "id": "q_sql_2",
            "question": "Which index type is most effective in PostgreSQL for equality lookups and range queries on sequential numbers?",
            "options": ["B-Tree Index", "GIN Index", "BRIN Index", "Hash Index"],
            "correct_index": 0,
            "explanation": "B-Tree is the default and most versatile index in PostgreSQL for equality and range comparisons (<, <=, =, >=, >)."
        },
        {
            "id": "q_sql_3",
            "question": "What does an INNER JOIN return when comparing two tables?",
            "options": [
                "All rows from the left table and only matching rows from the right.",
                "All rows from both tables regardless of match.",
                "Only rows where there is a matching value in both tables.",
                "All rows from the right table only."
            ],
            "correct_index": 2,
            "explanation": "INNER JOIN filters out non-matching rows and returns only records with corresponding keys in both tables."
        }
    ],
    "fastapi": [
        {
            "id": "q_fa_1",
            "question": "How does FastAPI achieve automatic request body validation and serialization?",
            "options": [
                "Using Django ORM models.",
                "Using Pydantic BaseModel schemas and Python type hints.",
                "Through custom regex parsing scripts.",
                "Via manual JSON decode middleware."
            ],
            "correct_index": 1,
            "explanation": "FastAPI leverages Pydantic models and type hints for automatic validation, serialization, and Swagger docs."
        },
        {
            "id": "q_fa_2",
            "question": "What parameter is used in FastAPI route definitions to inject reusable authentication or database dependencies?",
            "options": ["Inject()", "Provide()", "Depends()", "Require()"],
            "correct_index": 2,
            "explanation": "'Depends()' is FastAPI's dependency injection declaration primitive."
        }
    ]
}


def compute_learning_overview(
    roadmap: Optional[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    assessments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes global progress metrics across roadmap, projects, and assessments.
    """
    total_activities = 0
    completed_activities = 0
    in_progress_activities = 0
    pending_activities = 0

    if roadmap and "weeks" in roadmap:
        for w in roadmap["weeks"]:
            for act in w.get("activities", []):
                total_activities += 1
                st = act.get("status", "pending")
                if st == "completed":
                    completed_activities += 1
                elif st == "in_progress":
                    in_progress_activities += 1
                else:
                    pending_activities += 1

    progress_pct = round((completed_activities / total_activities) * 100, 1) if total_activities > 0 else 0.0

    # Project metrics
    completed_projects = [p for p in projects if p.get("status") == "completed"]
    active_projects = [p for p in projects if p.get("status") in ["saved", "in_progress"]]

    # Assessment metrics
    total_quizzes = len(assessments)
    avg_score = round(sum(a.get("score_percentage", 0) for a in assessments) / total_quizzes, 1) if total_quizzes > 0 else 0.0

    return {
        "roadmap_progress_percentage": progress_pct,
        "roadmap_completion_pct": progress_pct,
        "total_activities": total_activities,
        "completed_activities": completed_activities,
        "in_progress_activities": in_progress_activities,
        "pending_activities": pending_activities,
        "completed_projects": len(completed_projects),
        "completed_projects_count": len(completed_projects),
        "active_projects_count": len(active_projects),
        "total_assessments_taken": total_quizzes,
        "assessments_completed_count": total_quizzes,
        "assessment_average_score": avg_score,
        "average_assessment_score": avg_score
    }


def identify_weak_areas(
    skill_gap_report: Optional[Dict[str, Any]],
    assessments: List[Dict[str, Any]],
    roadmap: Optional[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorizes skills into 4 distinct evidentiary tiers:
      - Demonstrated Proficiency (Passed quiz >= 70% or verified in resume)
      - Needs More Practice (Quiz score < 70% or high gap with uncompleted activities)
      - In Progress (Currently active in current roadmap week)
      - Not Started (Pending future activities)
    """
    demonstrated: List[Dict[str, Any]] = []
    needs_practice: List[Dict[str, Any]] = []
    in_progress: List[Dict[str, Any]] = []
    not_started: List[Dict[str, Any]] = []

    # 1. Check assessment scores
    quiz_scores_by_skill: Dict[str, List[float]] = {}
    for a in assessments:
        skill = a.get("skill_name", "").lower()
        if skill:
            quiz_scores_by_skill.setdefault(skill, []).append(a.get("score_percentage", 0.0))

    # Evaluate quiz scores
    for skill, scores in quiz_scores_by_skill.items():
        avg = sum(scores) / len(scores)
        if avg < 70.0:
            needs_practice.append({
                "skill": skill.capitalize(),
                "reason": f"Assessment score average is {round(avg)}% (<70% benchmark).",
                "recommendation": "Review foundational concepts and complete reinforcement quiz."
            })
        else:
            demonstrated.append({
                "skill": skill.capitalize(),
                "reason": f"Validated by quiz assessment score of {round(avg)}%.",
                "level": "Proficient"
            })

    # 2. Check roadmap activities status
    if roadmap and "weeks" in roadmap:
        for w in roadmap["weeks"]:
            skill = w.get("skill", "")
            acts = w.get("activities", [])
            has_in_progress = any(a.get("status") == "in_progress" for a in acts)
            all_completed = all(a.get("status") == "completed" for a in acts) and len(acts) > 0
            all_pending = all(a.get("status") == "pending" for a in acts)

            if has_in_progress:
                in_progress.append({
                    "skill": skill,
                    "week_number": w.get("week_number"),
                    "objective": w.get("learning_objective")
                })
            elif all_completed:
                if not any(d["skill"].lower() == skill.lower() for d in demonstrated):
                    demonstrated.append({
                        "skill": skill,
                        "reason": f"Completed all Milestone practical exercises in Week {w.get('week_number')}.",
                        "level": "Competent"
                    })
            elif all_pending:
                not_started.append({
                    "skill": skill,
                    "week_number": w.get("week_number")
                })

    # 3. Add high priority missing skills from gap report if not already covered
    if skill_gap_report:
        for m in skill_gap_report.get("missing_skills", []):
            s_name = m.get("name", "")
            if not any(item["skill"].lower() == s_name.lower() for item in needs_practice + demonstrated + in_progress):
                needs_practice.append({
                    "skill": s_name,
                    "reason": f"High priority career gap with no verified evidence documented.",
                    "recommendation": f"Start foundational study and build initial practical exercise."
                })

    return {
        "demonstrated_proficiency": demonstrated[:5],
        "needs_more_practice": needs_practice[:5],
        "in_progress": in_progress[:3],
        "not_started": not_started[:5]
    }


def get_what_to_learn_next(
    roadmap: Optional[Dict[str, Any]],
    weak_areas: Dict[str, Any],
    projects: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Determines the single best next learning activity to execute.
    Explains what to learn, why recommended, career skill improved, and estimated time.
    """
    # Priority 1: If there is an activity currently marked "in_progress", finish it
    if roadmap and "weeks" in roadmap:
        for w in roadmap["weeks"]:
            for act in w.get("activities", []):
                if act.get("status") == "in_progress":
                    return {
                        "action_type": "roadmap_activity",
                        "type": "roadmap_activity",
                        "title": f"Continue: {act.get('title')}",
                        "skill_improved": act.get("skill"),
                        "skill": act.get("skill"),
                        "why_recommended": "You currently have this learning activity in progress. Completing it will finalize your active milestone.",
                        "why": "You currently have this learning activity in progress. Completing it will finalize your active milestone.",
                        "estimated_time": f"{act.get('estimated_hours', 1)} hours",
                        "estimated_time_minutes": int(act.get("estimated_hours", 1) * 60),
                        "target_id": act.get("id"),
                        "resources": act.get("resources", [])
                    }

    # Priority 2: If there are flagged weak areas, recommend a reinforcing quiz or concept
    weak_list = weak_areas.get("needs_more_practice", [])
    if weak_list:
        weak_skill = weak_list[0]["skill"]
        return {
            "action_type": "quiz",
            "type": "quiz",
            "title": f"Take 5-Minute Quiz: {weak_skill} Proficiency Check",
            "skill_improved": weak_skill,
            "skill": weak_skill,
            "why_recommended": f"Identified as needing practice ({weak_list[0]['reason']}). Testing your knowledge reinforces retention.",
            "why": f"Identified as needing practice ({weak_list[0]['reason']}). Testing your knowledge reinforces retention.",
            "estimated_time": "5-10 minutes",
            "estimated_time_minutes": 10,
            "target_id": f"quiz_{weak_skill.lower()}",
            "resources": []
        }

    # Priority 3: Next pending activity in roadmap
    if roadmap and "weeks" in roadmap:
        for w in roadmap["weeks"]:
            for act in w.get("activities", []):
                if act.get("status") == "pending":
                    return {
                        "action_type": "roadmap_activity",
                        "type": "roadmap_activity",
                        "title": act.get("title"),
                        "skill_improved": act.get("skill"),
                        "skill": act.get("skill"),
                        "why_recommended": f"Next planned milestone in Week {w.get('week_number')} of your personalized curriculum.",
                        "why": f"Next planned milestone in Week {w.get('week_number')} of your personalized curriculum.",
                        "estimated_time": f"{act.get('estimated_hours', 1)} hours",
                        "estimated_time_minutes": int(act.get("estimated_hours", 1) * 60),
                        "target_id": act.get("id"),
                        "resources": act.get("resources", [])
                    }

    # Fallback
    return {
        "action_type": "general",
        "type": "general",
        "title": "Review Portfolio Capstone Architecture",
        "skill_improved": "Full Stack & Cloud",
        "skill": "Full Stack & Cloud",
        "why_recommended": "You have completed your active milestones! Review project documentation and push updates to GitHub.",
        "why": "You have completed your active milestones! Review project documentation and push updates to GitHub.",
        "estimated_time": "30 minutes",
        "estimated_time_minutes": 30,
        "target_id": "portfolio_review",
        "resources": []
    }


def generate_topic_quiz(skill_name: str) -> Dict[str, Any]:
    """Generates an assessment quiz for a specific topic with multiple choice questions."""
    lower = skill_name.lower()
    questions = []

    for key, q_list in STATIC_QUIZ_BANK.items():
        if key in lower or lower in key:
            questions = q_list
            break

    if not questions:
        # Dynamic fallback questions for any skill
        questions = [
            {
                "id": f"q_{uuid.uuid4().hex[:6]}",
                "question": f"What is the recommended design pattern when structuring production {skill_name} components?",
                "options": [
                    "Single monolithic script with global state.",
                    "Separation of concerns with modular interfaces and dependency injection.",
                    "Directly coupling database drivers inside client presentation markup.",
                    "Disabling all logging and error boundaries."
                ],
                "correct_index": 1,
                "explanation": "Separation of concerns allows independent testing, maintenance, and safe refactoring."
            },
            {
                "id": f"q_{uuid.uuid4().hex[:6]}",
                "question": f"When configuring automated test suites for {skill_name}, what is the role of mock fixtures?",
                "options": [
                    "To permanently replace production databases.",
                    "To simulate external network or third-party service dependencies reliably.",
                    "To bypass syntax compilation errors.",
                    "To slow down continuous integration runners."
                ],
                "correct_index": 1,
                "explanation": "Mock fixtures isolate the unit under test from non-deterministic network and database states."
            },
            {
                "id": f"q_{uuid.uuid4().hex[:6]}",
                "question": f"Which metric is most critical when optimizing performance in {skill_name} deployments?",
                "options": [
                    "Line count of comments.",
                    "p95 / p99 response latency and memory allocation.",
                    "Frequency of git commits per hour.",
                    "Number of HTML tags."
                ],
                "correct_index": 1,
                "explanation": "p95/p99 tail latency and memory utilization measure real-world user performance under load."
            }
        ]

    return {
        "quiz_id": f"quiz_{uuid.uuid4().hex[:8]}",
        "skill_name": skill_name,
        "total_questions": len(questions),
        "questions": [
            {
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "correct_index": q["correct_index"],
                "explanation": q["explanation"]
            }
            for q in questions
        ]
    }


def evaluate_quiz_submission(
    quiz_data: Dict[str, Any],
    user_answers: Dict[str, int]
) -> Dict[str, Any]:
    """
    Evaluates quiz submission answers, computes score percentage,
    and returns question-by-question feedback and explanations.
    """
    questions = quiz_data.get("questions", [])
    total = len(questions)
    correct_count = 0
    feedback = []

    for q in questions:
        q_id = q["id"]
        chosen = user_answers.get(q_id)
        is_correct = (chosen == q["correct_index"])
        if is_correct:
            correct_count += 1

        feedback.append({
            "question_id": q_id,
            "question": q["question"],
            "chosen_index": chosen,
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    score_pct = round((correct_count / total) * 100, 1) if total > 0 else 0.0

    return {
        "quiz_id": quiz_data.get("quiz_id"),
        "skill_name": quiz_data.get("skill_name"),
        "score_percentage": score_pct,
        "total_questions": total,
        "correct_count": correct_count,
        "is_passed": (score_pct >= 70.0),
        "feedback": feedback
    }


def propose_roadmap_adjustments(
    roadmap: Dict[str, Any],
    weak_areas: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Proposes non-destructive adjustments to future pending activities in the roadmap
    based on identified weak areas. Never overwrites without user approval.
    """
    needs_practice = weak_areas.get("needs_more_practice", [])
    if not needs_practice:
        return None

    focus_item = needs_practice[0]
    focus_skill = focus_item["skill"]

    proposed_changes = [
        f"Insert 1 targeted reinforcement exercise for {focus_skill} into your upcoming week.",
        f"Add official reference tutorials and practice links to your study checklist.",
        f"Dedicate +2 practice hours to {focus_skill} to ensure baseline proficiency before capstone delivery."
    ]

    return {
        "id": f"adj_{uuid.uuid4().hex[:8]}",
        "focus_skill": focus_skill,
        "reason": focus_item["reason"],
        "proposed_changes": proposed_changes,
        "status": "pending",
        "action_prompt": f"Would you like to insert targeted reinforcement for '{focus_skill}' into your learning plan?"
    }
