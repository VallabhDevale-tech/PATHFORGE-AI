"""
PATHFORGE AI - AI Skill Gap Analyzer Service
Integrates the deterministic Skill Comparison Engine with Claude AI Advisory.
Produces the comprehensive, explainable Skill Gap Report.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

from app.services.skill_comparison_engine import execute_skill_comparison
from app.services.career_catalogue import get_role_by_slug

logger = logging.getLogger("pathforge.skill_gap_service")

CLAUDE_SKILL_GAP_PROMPT = """You are the Senior Technical Mentor for PATHFORGE AI.
Analyze the user's deterministic skill gap report for their target career.
Generate practical mentor guidance (3-4 sentences) explaining their strongest foundation,
the single most critical skill bridge they need to make, and advice on building hands-on portfolio proof.

Output ONLY a JSON object:
{
  "mentor_advice": "Your personalized strategic advice here..."
}
"""


def analyze_skill_gaps(
    resume_analysis: Dict[str, Any],
    career_slug: str,
    resume_id: Optional[str] = None,
    user_skill_overrides: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Backward-compatible synchronous function for skill gap comparison.
    """
    comp = execute_skill_comparison(
        resume_analysis=resume_analysis,
        career_slug=career_slug,
        resume_id=resume_id,
        user_skill_overrides=user_skill_overrides
    )
    total = comp.get("total_required_skills", 1)
    have_count = comp.get("matched_count", 0) + comp.get("improve_count", 0)
    comp["overall_match_percentage"] = round((have_count / total) * 100, 1) if total > 0 else 0.0
    comp["skills_have"] = [{"skill": s["name"], "name": s["name"]} for s in comp.get("matched_skills", [])] + [{"skill": s["name"], "name": s["name"]} for s in comp.get("improvement_skills", [])]
    comp["skills_improve"] = [{"skill": s["name"], "name": s["name"]} for s in comp.get("improvement_skills", [])]
    comp["skills_missing"] = [{"skill": s["name"], "name": s["name"]} for s in comp.get("missing_skills", [])]
    return comp


async def generate_skill_gap_report(
    resume_analysis: Dict[str, Any],
    career_slug: str,
    resume_id: Optional[str] = None,
    user_skill_overrides: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Generates a full Skill Gap Report using the deterministic engine and Claude guidance.
    """
    # 1. Deterministic comparison
    report = execute_skill_comparison(
        resume_analysis=resume_analysis,
        career_slug=career_slug,
        resume_id=resume_id,
        user_skill_overrides=user_skill_overrides
    )

    role_title = report.get("target_career", "Software Engineering")
    matched_names = [s["name"] for s in report.get("matched_skills", [])[:3]]
    missing_names = [s["name"] for s in report.get("missing_skills", [])[:2]]
    improve_names = [s["name"] for s in report.get("improvement_skills", [])[:2]]

    # 2. Check for Claude API
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    mentor_advice = None

    if anthropic_key and not anthropic_key.startswith("your-"):
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=anthropic_key)
            model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

            prompt = (
                f"Candidate Name: {report.get('candidate_name')}\n"
                f"Target Career: {role_title}\n"
                f"Coverage Score: {report.get('coverage_percentage')}%\n"
                f"Matched Skills: {', '.join(matched_names) or 'None'}\n"
                f"Skills to Improve: {', '.join(improve_names) or 'None'}\n"
                f"Missing / Unverified: {', '.join(missing_names) or 'None'}\n"
            )

            resp = await client.messages.create(
                model=model_name,
                max_tokens=600,
                system=CLAUDE_SKILL_GAP_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )

            raw_text = resp.content[0].text.strip()
            # Parse JSON
            if "{" in raw_text and "}" in raw_text:
                json_part = raw_text[raw_text.find("{"):raw_text.rfind("}") + 1]
                parsed = json.loads(json_part)
                mentor_advice = parsed.get("mentor_advice")
        except Exception as e:
            logger.warning(f"Claude mentor advice query failed (fallback used): {e}")

    # 3. Deterministic mentor guidance fallback
    if not mentor_advice:
        matched_str = f"strong foundation in {', '.join(matched_names)}" if matched_names else "solid foundational enthusiasm"
        focus_str = f"{', '.join(missing_names or improve_names or ['modern production architectures'])}"
        mentor_advice = (
            f"You demonstrate {matched_str}. To successfully transition into a competitive {role_title} role, "
            f"your immediate focus should be on building demonstrable practical proficiency in {focus_str}. "
            f"Ground your learning with production-grade portfolio projects and automated test suites."
        )

    report["mentor_advice"] = mentor_advice
    return report
