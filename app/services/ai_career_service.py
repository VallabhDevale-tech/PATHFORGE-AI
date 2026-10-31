"""
PATHFORGE AI - AI Career Path Recommendation Engine
Analyzes verified candidate profiles (skills, projects, education, experience, preferences)
against the 13 career roles catalogue and produces the top 5 explainable career recommendations.
Supports Claude model integration with structured validation and deterministic fallback.
"""

import json
import logging
import os
import re
from typing import Dict, Any, List, Optional

from app.services.career_catalogue import CAREER_ROLES_CATALOGUE

logger = logging.getLogger("pathforge.career_service")

CLAUDE_CAREER_PROMPT = """You are the Career Intelligence Advisory Engine for PATHFORGE AI.
Analyze the user's documented profile and provide personalized, explainable match justifications for the candidate.

=== STRICT RULES ===
1. Base your explanation strictly on the candidate's actual documented skills, projects, and education.
2. DO NOT fabricate qualifications, experience, or certifications not present in the profile.
3. For freshers/students, emphasize project work, academic coursework, and foundation skills.
4. Output strict JSON with explanations and next steps.
"""


def _normalize_skill(skill: str) -> str:
    """Normalizes skill string for case-insensitive and alias matching."""
    s = skill.lower().strip()
    aliases = {
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "postgres": "postgresql",
        "fastapi": "fastapi",
        "react.js": "react",
        "reactjs": "react",
        "node": "node.js",
        "nodejs": "node.js",
        "k8s": "kubernetes",
        "oop": "object-oriented programming (oop)",
        "object oriented programming": "object-oriented programming (oop)",
        "ml": "machine learning",
        "ai": "ai integration",
        "artificial intelligence": "ai integration",
        "ui/ux": "ui/ux design",
        "ux/ui": "ui/ux design",
        "figma": "figma",
        "ci cd": "ci/cd",
        "cicd": "ci/cd",
    }
    return aliases.get(s, s)


def _skill_matches_profile(target_skill: str, normalized_skills: set, text_block: str) -> bool:
    n_target = _normalize_skill(target_skill)
    if n_target in normalized_skills:
        return True
    parts = [p.strip() for p in re.split(r"[/,&]", n_target) if len(p.strip()) >= 2]
    for p in parts:
        if p in normalized_skills or any(p in u or u in p for u in normalized_skills if len(u) >= 3):
            return True
        if re.search(r"\b" + re.escape(p) + r"\b", text_block):
            return True
    return any(n_target in u or u in n_target for u in normalized_skills if len(u) >= 3)


def compute_career_match(
    role: Dict[str, Any],
    user_skills: List[str],
    user_soft_skills: List[str],
    user_projects: List[Dict[str, Any]],
    user_education: List[Dict[str, Any]],
    user_experience: List[Dict[str, Any]],
    user_preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes a deterministic, explainable compatibility score and skill breakdown
    between a candidate's profile and a career role.
    """
    normalized_user_skills = set(_normalize_skill(s) for s in user_skills)
    normalized_user_soft = set(_normalize_skill(s) for s in user_soft_skills)

    # Check project text for skills evidence
    project_text = " ".join([
        (p.get("project_title") or "") + " " +
        (p.get("description") or "") + " " +
        " ".join(p.get("technologies_used") or [])
        for p in user_projects
    ]).lower()

    # Check education text
    edu_text = " ".join([
        (e.get("degree") or "") + " " +
        " ".join(e.get("relevant_coursework") or [])
        for e in user_education
    ]).lower()

    # Check required skills
    matched_required = []
    missing_required = []
    for req in role["required_skills"]:
        if _skill_matches_profile(req, normalized_user_skills, project_text):
            matched_required.append(req)
        else:
            missing_required.append(req)

    # Check recommended skills
    matched_recommended = []
    missing_recommended = []
    for rec in role["recommended_skills"]:
        if _skill_matches_profile(rec, normalized_user_skills, project_text):
            matched_recommended.append(rec)
        else:
            missing_recommended.append(rec)

    # Check soft skills
    matched_soft = []
    for soft in role["soft_skills"]:
        n_soft = _normalize_skill(soft)
        if n_soft in normalized_user_soft:
            matched_soft.append(soft)

    total_req = len(role["required_skills"])
    total_rec = len(role["recommended_skills"])

    req_score = (len(matched_required) / total_req) * 65 if total_req > 0 else 35
    rec_score = (len(matched_recommended) / total_rec) * 15 if total_rec > 0 else 10
    soft_score = (len(matched_soft) / len(role["soft_skills"])) * 10 if role["soft_skills"] else 5

    # Preference alignment boost
    pref_score = 0
    fav_roles = user_preferences.get("preferred_roles", [])
    if isinstance(fav_roles, list):
        fav_lower = [f.lower() for f in fav_roles]
        if any(role["slug"] in f or role["title"].lower() in f for f in fav_lower):
            pref_score = 10
    elif isinstance(fav_roles, str) and (role["slug"] in fav_roles.lower() or role["title"].lower() in fav_roles.lower()):
        pref_score = 10

    # Base raw score
    raw_score = req_score + rec_score + soft_score + pref_score

    # Experience, projects, and academic credits
    if user_education:
        raw_score += min(len(user_education) * 6, 12)
    if user_projects:
        raw_score += min(len(user_projects) * 6, 12)
    if user_experience:
        raw_score += min(len(user_experience) * 4, 12)

    # Calibrate compatibility score to realistic range (40% to 96%)
    compatibility_score = min(max(round(raw_score), 40), 96)

    # Formulate explainable match reason
    match_reasons = []
    if matched_required:
        match_reasons.append(f"Demonstrated proficiency in {len(matched_required)} core required skill(s): {', '.join(matched_required[:3])}.")
    if matched_recommended:
        match_reasons.append(f"Familiarity with modern toolchain technologies including {', '.join(matched_recommended[:2])}.")
    if user_projects:
        match_reasons.append(f"Documented practical project experience that aligns directly with {role['title']} responsibilities.")
    if not match_reasons:
        match_reasons.append(f"Strong foundation for transitioning into {role['title']} through targeted skill acquisition.")

    why_matched = " ".join(match_reasons)

    return {
        "career_slug": role["slug"],
        "career_title": role["title"],
        "category": role["category"],
        "description": role["description"],
        "compatibility_score": compatibility_score,
        "why_matched": why_matched,
        "existing_skills": matched_required + matched_recommended,
        "required_skills": role["required_skills"],
        "missing_skills": missing_required,
        "recommended_next_steps": role["suggested_next_steps"],
        "market_demand": role.get("market_demand", "High"),
        "typical_roles": role.get("typical_roles", [])
    }


async def generate_career_recommendations(
    resume_analysis: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates all 13 career roles against candidate profile and returns the top 5 recommendations.
    Uses Claude to refine explanations if configured, or deterministic rule engine.
    """
    prefs = user_preferences or {}

    tech_skills = resume_analysis.get("technical_skills") or []
    soft_skills = resume_analysis.get("soft_skills") or []
    projects = resume_analysis.get("projects") or []
    education = resume_analysis.get("education") or []
    experience = resume_analysis.get("work_experience") or []

    # Evaluate each role
    all_scored = []
    for role in CAREER_ROLES_CATALOGUE:
        match_data = compute_career_match(
            role=role,
            user_skills=tech_skills,
            user_soft_skills=soft_skills,
            user_projects=projects,
            user_education=education,
            user_experience=experience,
            user_preferences=prefs
        )
        all_scored.append(match_data)

    # Sort descending by compatibility score
    all_scored.sort(key=lambda x: x["compatibility_score"], reverse=True)

    # Select top 5
    top_5 = all_scored[:5]

    # Optional Claude enrichment
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and len(top_5) > 0:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            prompt = (
                f"Candidate technical skills: {tech_skills}\n"
                f"Candidate projects: {[p.get('project_title') for p in projects]}\n"
                f"Top 5 matched roles: {[r['career_title'] for r in top_5]}\n"
                "Please output a JSON object mapping each career_slug to an enhanced 'why_matched' string (max 2 sentences, factual)."
            )
            resp = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                max_tokens=1000,
                system=CLAUDE_CAREER_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            raw = resp.content[0].text.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            enhanced_dict = json.loads(raw)
            for rec in top_5:
                if rec["career_slug"] in enhanced_dict:
                    rec["why_matched"] = enhanced_dict[rec["career_slug"]]
        except Exception as e:
            logger.debug(f"Claude career explanation refinement skipped: {e}")

    return top_5
