"""
PATHFORGE AI - AI Skill Gap Analyzer Engine
Compares candidate skills from resume analysis against selected target career requirements.
Classifies skills into:
  A. Skills You Have
  B. Skills to Improve
  C. Missing or Not Found in Profile
Generates prioritized gaps, practical project ideas, and actionable learning roadmaps.
"""

import json
import logging
import os
import re
from typing import Dict, Any, List, Optional

from app.services.career_catalogue import get_role_by_slug, CAREER_ROLES_CATALOGUE
from app.services.ai_career_service import _normalize_skill

logger = logging.getLogger("pathforge.skill_gap_service")

CLAUDE_SKILL_GAP_PROMPT = """You are the Senior Technical Mentor for PATHFORGE AI.
Analyze the user's skill comparison against their chosen target career.
Generate concrete, realistic learning directions and practical project recommendations.

=== STRICT RULES ===
1. Do NOT assume a skill is permanently missing; classify as 'Not found in profile'.
2. Recommend practical, hands-on portfolio projects that bridge identified gaps.
3. Keep project descriptions actionable with specific technologies.
4. Output valid JSON.
"""


def analyze_skill_gaps(
    resume_analysis: Dict[str, Any],
    career_slug: str
) -> Dict[str, Any]:
    """
    Computes a comprehensive skill gap report between candidate profile and target career.
    """
    role = get_role_by_slug(career_slug)
    if not role:
        # Fallback to software-developer if slug not found
        role = CAREER_ROLES_CATALOGUE[0]

    raw_user_tech = resume_analysis.get("technical_skills") or []
    raw_user_soft = resume_analysis.get("soft_skills") or []
    projects = resume_analysis.get("projects") or []
    experience = resume_analysis.get("work_experience") or []

    normalized_user_skills = set(_normalize_skill(s) for s in raw_user_tech)

    # Search project technologies and descriptions
    project_mentions = set()
    for p in projects:
        for t in p.get("technologies_used") or []:
            project_mentions.add(_normalize_skill(t))
        desc = (p.get("description") or "").lower()
        for t in p.get("technologies_used") or []:
            if t.lower() in desc:
                project_mentions.add(_normalize_skill(t))

    # Experience mentions
    exp_mentions = set()
    for e in experience:
        resp_text = " ".join(e.get("responsibilities") or []).lower()
        ach_text = " ".join(e.get("achievements") or []).lower()
        combined = resp_text + " " + ach_text
        for s in raw_user_tech:
            if s.lower() in combined:
                exp_mentions.add(_normalize_skill(s))

    required_skills = role.get("required_skills", [])
    recommended_skills = role.get("recommended_skills", [])
    all_target_skills = required_skills + recommended_skills

    skills_have: List[Dict[str, Any]] = []
    skills_improve: List[Dict[str, Any]] = []
    skills_missing: List[Dict[str, Any]] = []

    for skill in all_target_skills:
        n_skill = _normalize_skill(skill)
        is_required = skill in required_skills
        priority = "High" if is_required else "Medium"

        # Evidence checks
        in_tech_list = n_skill in normalized_user_skills
        in_projects = n_skill in project_mentions
        in_exp = n_skill in exp_mentions

        if (in_tech_list and (in_projects or in_exp)) or (in_projects and in_exp):
            # Strong evidence -> Skills You Have
            skills_have.append({
                "skill": skill,
                "category": "Technical",
                "evidence": "Supported by documented practical application in projects or work history.",
                "importance": "Core requirement" if is_required else "Recommended"
            })
        elif in_tech_list or in_projects:
            # Listed or mentioned, but limited evidence -> Skills to Improve
            skills_improve.append({
                "skill": skill,
                "category": "Technical",
                "priority": priority,
                "current_status": "Documented in profile; recommend deeper production or architectural experience.",
                "why_matters": f"Essential for demonstrating end-to-end competency in {role['title']} workflows.",
                "learning_direction": f"Build full-featured modules emphasizing {skill} design patterns and performance optimization."
            })
        else:
            # No evidence in resume -> Missing or Not Found in Profile
            skills_missing.append({
                "skill": skill,
                "category": "Technical",
                "priority": "High" if is_required else "Medium",
                "status": "Not found in profile",
                "why_matters": f"Frequently required by employers for standard {role['title']} job requisitions.",
                "learning_direction": f"Study foundational documentation and implement a starter project using {skill}."
            })

    # Weighted match formula: core required skills carry 70% weight, recommended carry 30%
    req_have = sum(1 for s in skills_have if s["skill"] in required_skills)
    req_imp = sum(1 for s in skills_improve if s["skill"] in required_skills)
    req_ratio = ((req_have * 1.0 + req_imp * 0.6) / len(required_skills)) if required_skills else 0.5

    rec_have = sum(1 for s in skills_have if s["skill"] in recommended_skills)
    rec_imp = sum(1 for s in skills_improve if s["skill"] in recommended_skills)
    rec_ratio = ((rec_have * 1.0 + rec_imp * 0.6) / len(recommended_skills)) if recommended_skills else 0.5

    raw_match = (req_ratio * 70.0) + (rec_ratio * 30.0)
    overall_match = min(max(round(raw_match, 1), 25.0), 96.0)

    # Priority gaps list (sorted High first)
    priority_gaps = []
    for item in skills_missing:
        priority_gaps.append({
            "skill": item["skill"],
            "priority": item["priority"],
            "status": "Not found in profile",
            "why_matters": item["why_matters"],
            "action": item["learning_direction"]
        })
    for item in skills_improve:
        priority_gaps.append({
            "skill": item["skill"],
            "priority": item["priority"],
            "status": "Identified – needs depth",
            "why_matters": item["why_matters"],
            "action": item["learning_direction"]
        })

    # Sort High priority first
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    priority_gaps.sort(key=lambda x: priority_order.get(x["priority"], 3))

    # Generate targeted project ideas
    recommended_projects = _generate_project_recommendations(role, skills_missing, skills_improve)

    # Structured learning roadmap (3 phases)
    learning_path = [
        {
            "phase": "Phase 1: Foundation (Weeks 1-3)",
            "goal": "Bridge high-priority missing skills",
            "skills": [s["skill"] for s in skills_missing if s["priority"] == "High"][:3] or [role["required_skills"][0]],
            "action": f"Complete hands-on tutorials and configure development toolchains for {role['title']} requirements."
        },
        {
            "phase": "Phase 2: Deepening & Integration (Weeks 4-6)",
            "goal": "Elevate skills to improve into production competency",
            "skills": [s["skill"] for s in skills_improve][:3] or [role["required_skills"][-1]],
            "action": "Build integration services connecting multiple components with error handling and automated tests."
        },
        {
            "phase": "Phase 3: Portfolio Capstone (Weeks 7-9)",
            "goal": "Ship an end-to-end demonstrable showcase project",
            "skills": [role["required_skills"][0], role["required_skills"][1] if len(role["required_skills"]) > 1 else "Git"],
            "action": "Deploy a complete public application to cloud hosting with clean documentation and live demo link."
        }
    ]

    return {
        "career_slug": role["slug"],
        "career_title": role["title"],
        "category": role["category"],
        "overall_match_percentage": overall_match,
        "skills_have": skills_have,
        "skills_improve": skills_improve,
        "skills_missing": skills_missing,
        "priority_gaps": priority_gaps,
        "learning_path": learning_path,
        "recommended_projects": recommended_projects
    }


def _generate_project_recommendations(
    role: Dict[str, Any],
    missing: List[Dict[str, Any]],
    improve: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generates 2-3 tailored portfolio project suggestions addressing the candidate's gaps."""
    top_gaps = [m["skill"] for m in missing[:3]] + [i["skill"] for i in improve[:2]]
    gap_summary = ", ".join(top_gaps[:3]) if top_gaps else "modern industry toolchains"

    return [
        {
            "title": f"{role['title']} Portfolio Showcase Application",
            "description": f"Architect a complete full-stack or backend service implementing core {role['title']} workflows.",
            "skills_applied": top_gaps[:4] or role["required_skills"][:4],
            "difficulty": "Intermediate",
            "estimated_hours": "20-30 hours",
            "outcome": f"Demonstrable GitHub repository showcasing clean architecture, tests, and documentation."
        },
        {
            "title": f"Production Integration Pipeline featuring {top_gaps[0] if top_gaps else 'Cloud'}",
            "description": f"Build a robust microservice or data module applying {gap_summary} with automated testing and continuous integration.",
            "skills_applied": top_gaps[:3] or role["required_skills"][:3],
            "difficulty": "Advanced",
            "estimated_hours": "15-25 hours",
            "outcome": "Live containerized deployment verifying practical mastery beyond theory."
        }
    ]


async def generate_skill_gap_report(
    resume_analysis: Dict[str, Any],
    career_slug: str
) -> Dict[str, Any]:
    """Generates skill gap report with optional Claude AI enrichment."""
    base_report = analyze_skill_gaps(resume_analysis, career_slug)

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            prompt = (
                f"Target Career: {base_report['career_title']}\n"
                f"Skills candidate has: {[s['skill'] for s in base_report['skills_have']]}\n"
                f"Skills to improve: {[s['skill'] for s in base_report['skills_improve']]}\n"
                f"Skills not found: {[s['skill'] for s in base_report['skills_missing']]}\n"
                "Please output a JSON object with: {'mentor_advice': '2 sentences of strategic guidance', 'capstone_idea': '1 creative project name and brief description'}."
            )
            resp = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                max_tokens=500,
                system=CLAUDE_SKILL_GAP_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            raw = resp.content[0].text.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            enrichment = json.loads(raw)
            if "mentor_advice" in enrichment:
                base_report["mentor_advice"] = enrichment["mentor_advice"]
        except Exception as e:
            logger.debug(f"Claude skill gap enrichment note: {e}")

    return base_report
