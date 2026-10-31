"""
PATHFORGE AI - Deterministic Skill Comparison Engine
Compares candidate profile skills against structured career requirements.
Uses 4 proficiency levels:
  1 = Beginner
  2 = Intermediate
  3 = Advanced
  4 = Expert
Applies the deterministic formula: Gap = Required Level - Current Level
Outputs matched, improvement, and unverified/not found skills strictly conforming
to the shared data contract.
"""

import re
from typing import Dict, List, Any, Optional
from app.services.career_catalogue import get_role_by_slug, PROFICIENCY_LEVELS, CAREER_ROLES_CATALOGUE
from app.services.ai_career_service import _normalize_skill


def estimate_user_skill_levels(
    resume_analysis: Dict[str, Any],
    user_skill_overrides: Optional[Dict[str, int]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Analyzes resume data (technical skills, projects, work experience, education, certifications)
    to estimate proficiency levels (1 to 4) for each identified skill.
    Allows user self-assessed overrides to take precedence.
    """
    technical_skills = resume_analysis.get("technical_skills") or []
    soft_skills = resume_analysis.get("soft_skills") or []
    projects = resume_analysis.get("projects") or []
    work_exp = resume_analysis.get("work_experience") or []
    education = resume_analysis.get("education") or []
    certs = resume_analysis.get("certifications") or []

    # Map of normalized skill -> metadata
    profile_skills: Dict[str, Dict[str, Any]] = {}

    # 1. Base technical skills mentioned in list -> default Level 1 (Beginner - estimated)
    for s in technical_skills:
        n = _normalize_skill(s)
        profile_skills[n] = {
            "name": s,
            "level": 1,
            "is_estimated": True,
            "evidence": ["Documented in resume technical skills list."]
        }

    # 2. Check practical application in Projects -> Upgrade to Level 2 (Intermediate)
    for p in projects:
        proj_techs = p.get("technologies_used") or []
        proj_title = p.get("project_title") or "Project"
        proj_desc = p.get("description") or ""

        for t in proj_techs:
            n = _normalize_skill(t)
            if n not in profile_skills:
                profile_skills[n] = {
                    "name": t,
                    "level": 2,
                    "is_estimated": True,
                    "evidence": [f"Implemented in practical project '{proj_title}'."]
                }
            else:
                profile_skills[n]["level"] = max(profile_skills[n]["level"], 2)
                profile_skills[n]["evidence"].append(f"Implemented in practical project '{proj_title}'.")

        # Also search keywords in description
        for n, data in list(profile_skills.items()):
            if re.search(r"\b" + re.escape(n) + r"\b", proj_desc.lower()):
                profile_skills[n]["level"] = max(profile_skills[n]["level"], 2)

    # 3. Check Work Experience -> Multiple projects / production responsibilities -> Upgrade to Level 3 (Advanced)
    for exp in work_exp:
        role_title = exp.get("job_title") or ""
        company = exp.get("company") or "Company"
        resp_text = " ".join(exp.get("responsibilities") or []) + " " + " ".join(exp.get("achievements") or [])
        resp_lower = resp_text.lower()
        is_senior = any(term in role_title.lower() for term in ["senior", "lead", "architect", "principal", "staff"])

        for n, data in list(profile_skills.items()):
            if re.search(r"\b" + re.escape(n) + r"\b", resp_lower):
                new_level = 3 if is_senior else 2
                profile_skills[n]["level"] = max(profile_skills[n]["level"], new_level)
                profile_skills[n]["evidence"].append(f"Applied in professional role '{role_title}' at {company}.")

    # 4. Check Certifications -> Boost level
    for c in certs:
        c_name = (c.get("certification_name") or "").lower()
        for n, data in list(profile_skills.items()):
            if re.search(r"\b" + re.escape(n) + r"\b", c_name):
                profile_skills[n]["level"] = min(profile_skills[n]["level"] + 1, 4)
                profile_skills[n]["evidence"].append(f"Certified: {c.get('certification_name')}.")

    # 5. User Self-Assessment / Verified Overrides take precedence
    if user_skill_overrides:
        for skill_name, custom_level in user_skill_overrides.items():
            n = _normalize_skill(skill_name)
            clamped_level = max(1, min(int(custom_level), 4))
            if n in profile_skills:
                profile_skills[n]["level"] = clamped_level
                profile_skills[n]["is_estimated"] = False
                profile_skills[n]["evidence"].append(f"Self-assessed / verified by candidate as Level {clamped_level} ({PROFICIENCY_LEVELS.get(clamped_level)}).")
            else:
                profile_skills[n] = {
                    "name": skill_name,
                    "level": clamped_level,
                    "is_estimated": False,
                    "evidence": [f"Added and self-assessed by candidate as Level {clamped_level} ({PROFICIENCY_LEVELS.get(clamped_level)})."]
                }

    return profile_skills


def execute_skill_comparison(
    resume_analysis: Dict[str, Any],
    career_slug: str,
    resume_id: Optional[str] = None,
    user_skill_overrides: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Executes the deterministic comparison engine between candidate skills and target career requirements.
    Calculates Gap = Required Level - Current Level for each requirement.
    Produces matched, improvement, and missing skills conforming to Part 6 Data Contract.
    """
    role = get_role_by_slug(career_slug)
    if not role:
        role = CAREER_ROLES_CATALOGUE[0]

    # Candidate profile info
    personal_info = resume_analysis.get("personal_information") or {}
    candidate_name = personal_info.get("full_name") or "Candidate"

    # 1. Estimate/retrieve candidate skills with verified overrides
    profile_skills = estimate_user_skill_levels(resume_analysis, user_skill_overrides)

    matched_skills: List[Dict[str, Any]] = []
    improvement_skills: List[Dict[str, Any]] = []
    missing_skills: List[Dict[str, Any]] = []
    priority_skills: List[str] = []

    # Category breakdown tracker: category -> {total, matched, improve, missing}
    categories_map: Dict[str, Dict[str, int]] = {}

    skill_requirements = role.get("skill_requirements") or []
    total_required = len(skill_requirements)

    for req in skill_requirements:
        req_name = req["name"]
        cat = req.get("category", "Technical")
        required_level = int(req.get("required_level", 2))
        priority = req.get("priority", "Medium")
        why_matters = req.get("why_matters", f"Key skill for {role['title']} responsibilities.")

        if cat not in categories_map:
            categories_map[cat] = {"total": 0, "matched": 0, "improve": 0, "missing": 0}
        categories_map[cat]["total"] += 1

        n_req = _normalize_skill(req_name)

        # Match against profile skills (direct normalized match or substring search)
        found_data = None
        for n_user, u_data in profile_skills.items():
            if n_req == n_user or (len(n_req) >= 3 and n_req in n_user) or (len(n_user) >= 3 and n_user in n_req):
                found_data = u_data
                break

        if found_data:
            current_level = int(found_data["level"])
            is_estimated = found_data.get("is_estimated", True)
            evidence = " ".join(found_data.get("evidence", [])) or "Referenced in candidate resume profile."

            gap = required_level - current_level

            if gap <= 0:
                # Meets or exceeds requirement
                categories_map[cat]["matched"] += 1
                matched_skills.append({
                    "name": req_name,
                    "category": cat,
                    "current_level": current_level,
                    "current_level_name": PROFICIENCY_LEVELS.get(current_level, "Beginner"),
                    "required_level": required_level,
                    "required_level_name": PROFICIENCY_LEVELS.get(required_level, "Intermediate"),
                    "gap": gap,
                    "is_estimated": is_estimated,
                    "evidence": evidence,
                    "status": "matched"
                })
            else:
                # Skill is present, but current < required
                categories_map[cat]["improve"] += 1
                if priority == "High":
                    priority_skills.append(req_name)
                improvement_skills.append({
                    "name": req_name,
                    "category": cat,
                    "current_level": current_level,
                    "current_level_name": PROFICIENCY_LEVELS.get(current_level, "Beginner"),
                    "required_level": required_level,
                    "required_level_name": PROFICIENCY_LEVELS.get(required_level, "Advanced"),
                    "gap": gap,
                    "priority": priority,
                    "is_estimated": is_estimated,
                    "evidence": evidence,
                    "why_matters": why_matters,
                    "action": f"Elevate proficiency from {PROFICIENCY_LEVELS.get(current_level)} to {PROFICIENCY_LEVELS.get(required_level)} through advanced project application.",
                    "status": "needs_improvement"
                })
        else:
            # No reliable evidence in resume -> unverified / not found in profile
            categories_map[cat]["missing"] += 1
            if priority in ["High", "Medium"]:
                priority_skills.append(req_name)
            missing_skills.append({
                "name": req_name,
                "category": cat,
                "current_level": 0,
                "current_level_name": "Not Documented",
                "required_level": required_level,
                "required_level_name": PROFICIENCY_LEVELS.get(required_level, "Intermediate"),
                "gap": required_level,
                "priority": priority,
                "why_matters": why_matters,
                "action": f"Begin foundational learning and practical tutorials in {req_name} to meet {PROFICIENCY_LEVELS.get(required_level)} baseline.",
                "status": "not_found"
            })

    # Transparent skill coverage calculation (illustrative coverage percentage)
    matched_count = len(matched_skills)
    improve_count = len(improvement_skills)
    missing_count = len(missing_skills)

    # Coverage score: strictly matched skills out of total listed required skills
    coverage_percentage = round((matched_count / total_required) * 100, 1) if total_required > 0 else 0.0

    # Overall weighted readiness score: Matched (1.0) + In Progress/Improve (0.5)
    readiness_score = round(((matched_count * 1.0 + improve_count * 0.5) / total_required) * 100, 1) if total_required > 0 else 0.0

    # Ensure priority skills has high-priority items first and deduplicated
    priority_skills_unique = []
    for s in priority_skills:
        if s not in priority_skills_unique:
            priority_skills_unique.append(s)

    # Compile priority gaps table
    priority_gaps_table = []
    for m in missing_skills:
        priority_gaps_table.append({
            "skill": m["name"],
            "category": m["category"],
            "priority": m["priority"],
            "current_level": "None (Unverified)",
            "required_level": m["required_level_name"],
            "status": "Not found in profile",
            "why_matters": m["why_matters"],
            "action": m["action"]
        })
    for imp in improvement_skills:
        priority_gaps_table.append({
            "skill": imp["name"],
            "category": imp["category"],
            "priority": imp["priority"],
            "current_level": imp["current_level_name"],
            "required_level": imp["required_level_name"],
            "status": f"Needs +{imp['gap']} level depth",
            "why_matters": imp["why_matters"],
            "action": imp["action"]
        })

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    priority_gaps_table.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return {
        "target_career": role["title"],
        "career_slug": role["slug"],
        "category": role["category"],
        "resume_id": resume_id,
        "candidate_name": candidate_name,
        "total_required_skills": total_required,
        "matched_count": matched_count,
        "improve_count": improve_count,
        "missing_count": missing_count,
        "coverage_percentage": coverage_percentage,
        "coverage_score": coverage_percentage,
        "overall_match_percentage": coverage_percentage,
        "readiness_score": readiness_score,
        "matched_skills": matched_skills,
        "improvement_skills": improvement_skills,
        "missing_skills": missing_skills,
        "skills_have": [{"skill": s["name"], "name": s["name"]} for s in matched_skills] + [{"skill": s["name"], "name": s["name"]} for s in improvement_skills],
        "skills_improve": [{"skill": s["name"], "name": s["name"]} for s in improvement_skills],
        "skills_missing": [{"skill": s["name"], "name": s["name"]} for s in missing_skills],
        "learning_path": [
            {"week": 1, "focus": "Bridge foundational gaps", "resources": ["Official Documentation", "Interactive Tutorials"]},
            {"week": 2, "focus": "Deepen core architectural fluency", "resources": ["Comprehensive Guides", "Practice Exercises"]},
            {"week": 3, "focus": "Production capstone delivery", "resources": ["Project Blueprints", "Automated Testing"]}
        ],
        "recommended_projects": [
            {"title": f"Hands-on {role['title']} Integration Service", "difficulty": "Intermediate"},
            {"title": f"Production {role['title']} Capstone System", "difficulty": "Advanced"}
        ],
        "priority_skills": priority_skills_unique,
        "priority_gaps": priority_gaps_table,
        "category_breakdown": categories_map,
        "profile_skills_summary": [
            {
                "name": v["name"],
                "level": v["level"],
                "level_name": PROFICIENCY_LEVELS.get(v["level"], "Beginner"),
                "is_estimated": v.get("is_estimated", True)
            }
            for v in profile_skills.values()
        ],
        "analysis_status": "completed",
        "disclaimer": "This score is a skill coverage indicator comparing documented profile evidence against standardized career expectations. It does not represent an employability guarantee or formal job-readiness certification."
    }
