import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pathforge.storage")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "pathforge_local.db"


def _get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_local_db():
    """Initializes local tables that mirror the Supabase schema for guaranteed zero-downtime persistence."""
    conn = _get_db()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS resume_analysis (
                id TEXT PRIMARY KEY,
                resume_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                personal_information TEXT NOT NULL DEFAULT '{}',
                professional_summary TEXT NOT NULL DEFAULT '{}',
                technical_skills TEXT NOT NULL DEFAULT '[]',
                soft_skills TEXT NOT NULL DEFAULT '[]',
                education TEXT NOT NULL DEFAULT '[]',
                work_experience TEXT NOT NULL DEFAULT '[]',
                projects TEXT NOT NULL DEFAULT '[]',
                certifications TEXT NOT NULL DEFAULT '[]',
                additional_information TEXT NOT NULL DEFAULT '[]',
                raw_analysis TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_la_resume_id ON resume_analysis(resume_id);
            CREATE INDEX IF NOT EXISTS idx_la_user_id ON resume_analysis(user_id);

            CREATE TABLE IF NOT EXISTS career_recommendations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_id TEXT,
                recommendations TEXT NOT NULL DEFAULT '[]',
                user_preferences TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_career_selections (
                id TEXT PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                career_slug TEXT NOT NULL,
                career_title TEXT NOT NULL,
                career_data TEXT NOT NULL DEFAULT '{}',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS skill_gap_reports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_id TEXT,
                career_slug TEXT NOT NULL,
                career_title TEXT NOT NULL,
                overall_match_percentage REAL NOT NULL,
                skills_have TEXT NOT NULL DEFAULT '[]',
                skills_improve TEXT NOT NULL DEFAULT '[]',
                skills_missing TEXT NOT NULL DEFAULT '[]',
                priority_gaps TEXT NOT NULL DEFAULT '[]',
                learning_path TEXT NOT NULL DEFAULT '[]',
                recommended_projects TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL
            );
        """)
    conn.close()


# Initialize upon module load
init_local_db()


class HybridStorageManager:
    """
    Coordinates data persistence across Supabase PostgreSQL (primary)
    and SQLite fallback (guaranteed resilience if Supabase tables are not yet migrated).
    """

    @classmethod
    def save_resume_analysis(
        cls,
        user_client: Any,
        user_id: str,
        resume_id: str,
        analysis_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        record_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Always write to local resilient DB first
        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO resume_analysis (
                        id, resume_id, user_id, personal_information, professional_summary,
                        technical_skills, soft_skills, education, work_experience,
                        projects, certifications, additional_information, raw_analysis, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record_id,
                    resume_id,
                    user_id,
                    json.dumps(analysis_dict.get("personal_information", {})),
                    json.dumps(analysis_dict.get("professional_summary", {})),
                    json.dumps(analysis_dict.get("technical_skills", [])),
                    json.dumps(analysis_dict.get("soft_skills", [])),
                    json.dumps(analysis_dict.get("education", [])),
                    json.dumps(analysis_dict.get("work_experience", [])),
                    json.dumps(analysis_dict.get("projects", [])),
                    json.dumps(analysis_dict.get("certifications", [])),
                    json.dumps(analysis_dict.get("additional_information", [])),
                    json.dumps(analysis_dict),
                    now_iso
                ))
            conn.close()
        except Exception as local_err:
            logger.warning(f"Local sqlite insert warning: {local_err}")

        # 2. Attempt to persist to Supabase PostgreSQL table
        try:
            supabase_payload = {
                "id": record_id,
                "resume_id": resume_id,
                "user_id": user_id,
                "personal_information": analysis_dict.get("personal_information", {}),
                "professional_summary": analysis_dict.get("professional_summary", {}),
                "technical_skills": analysis_dict.get("technical_skills", []),
                "soft_skills": analysis_dict.get("soft_skills", []),
                "education": analysis_dict.get("education", []),
                "work_experience": analysis_dict.get("work_experience", []),
                "projects": analysis_dict.get("projects", []),
                "certifications": analysis_dict.get("certifications", []),
                "additional_information": analysis_dict.get("additional_information", []),
                "raw_analysis": analysis_dict
            }
            res = user_client.table("resume_analysis").insert(supabase_payload).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as sb_err:
            logger.info(f"Supabase resume_analysis table save pending migration: {sb_err}")

        return {
            "id": record_id,
            "resume_id": resume_id,
            "user_id": user_id,
            "created_at": now_iso
        }

    @classmethod
    def get_resume_analysis(
        cls,
        user_client: Any,
        user_id: str,
        resume_id: str
    ) -> Optional[Dict[str, Any]]:
        # 1. Try Supabase PostgREST
        try:
            res = (
                user_client.table("resume_analysis")
                .select("*")
                .eq("resume_id", resume_id)
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if res.data and len(res.data) > 0:
                row = res.data[0]
                raw = row.get("raw_analysis")
                if isinstance(raw, str):
                    raw = json.loads(raw)
                return {
                    "id": row.get("id"),
                    "resume_id": row.get("resume_id"),
                    "user_id": row.get("user_id"),
                    "analysis": raw or {
                        "personal_information": row.get("personal_information", {}),
                        "professional_summary": row.get("professional_summary", {}),
                        "technical_skills": row.get("technical_skills", []),
                        "soft_skills": row.get("soft_skills", []),
                        "education": row.get("education", []),
                        "work_experience": row.get("work_experience", []),
                        "projects": row.get("projects", []),
                        "certifications": row.get("certifications", []),
                        "additional_information": row.get("additional_information", [])
                    },
                    "created_at": row.get("created_at")
                }
        except Exception as sb_err:
            logger.debug(f"Supabase resume_analysis query fallback: {sb_err}")

        # 2. Check local resilient store
        try:
            conn = _get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM resume_analysis
                WHERE resume_id = ? AND user_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (resume_id, user_id))
            row = cursor.fetchone()
            conn.close()

            if row:
                raw = json.loads(row["raw_analysis"]) if row["raw_analysis"] else {}
                return {
                    "id": row["id"],
                    "resume_id": row["resume_id"],
                    "user_id": row["user_id"],
                    "analysis": raw if raw else {
                        "personal_information": json.loads(row["personal_information"]),
                        "professional_summary": json.loads(row["professional_summary"]),
                        "technical_skills": json.loads(row["technical_skills"]),
                        "soft_skills": json.loads(row["soft_skills"]),
                        "education": json.loads(row["education"]),
                        "work_experience": json.loads(row["work_experience"]),
                        "projects": json.loads(row["projects"]),
                        "certifications": json.loads(row["certifications"]),
                        "additional_information": json.loads(row["additional_information"]),
                    },
                    "created_at": row["created_at"]
                }
        except Exception as local_err:
            logger.warning(f"Local storage retrieval note: {local_err}")

        return None

    @classmethod
    def save_career_selection(
        cls,
        user_client: Any,
        user_id: str,
        career_slug: str,
        career_title: str,
        career_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        record_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        # Local store
        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    INSERT INTO user_career_selections (id, user_id, career_slug, career_title, career_data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        career_slug = excluded.career_slug,
                        career_title = excluded.career_title,
                        career_data = excluded.career_data,
                        updated_at = excluded.updated_at
                """, (
                    record_id,
                    user_id,
                    career_slug,
                    career_title,
                    json.dumps(career_data),
                    now_iso
                ))
            conn.close()
        except Exception as e:
            logger.warning(f"Local save career selection error: {e}")

        # Supabase
        try:
            payload = {
                "user_id": user_id,
                "career_slug": career_slug,
                "career_title": career_title,
                "career_data": career_data,
                "updated_at": now_iso
            }
            res = user_client.table("user_career_selections").upsert(payload, on_conflict="user_id").execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as sb_err:
            logger.info(f"Supabase user_career_selections upsert note: {sb_err}")

        return {
            "id": record_id,
            "user_id": user_id,
            "career_slug": career_slug,
            "career_title": career_title,
            "career_data": career_data,
            "updated_at": now_iso
        }

    @classmethod
    def get_career_selection(
        cls,
        user_client: Any,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        # 1. Supabase
        try:
            res = user_client.table("user_career_selections").select("*").eq("user_id", user_id).limit(1).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                data = row.get("career_data")
                if isinstance(data, str):
                    data = json.loads(data)
                return {
                    "career_slug": row.get("career_slug"),
                    "career_title": row.get("career_title"),
                    "career_data": data,
                    "updated_at": row.get("updated_at")
                }
        except Exception as e:
            logger.debug(f"Supabase career selection query fallback: {e}")

        # 2. Local
        try:
            conn = _get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_career_selections WHERE user_id = ? LIMIT 1", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "career_slug": row["career_slug"],
                    "career_title": row["career_title"],
                    "career_data": json.loads(row["career_data"]) if row["career_data"] else {},
                    "updated_at": row["updated_at"]
                }
        except Exception as e:
            logger.warning(f"Local career selection retrieval note: {e}")

        return None

    @classmethod
    def save_career_recommendations(
        cls,
        user_client: Any,
        user_id: str,
        resume_id: Optional[str],
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        record_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        # Local
        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    INSERT INTO career_recommendations (id, user_id, resume_id, recommendations, user_preferences, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    record_id,
                    user_id,
                    resume_id,
                    json.dumps(recommendations),
                    json.dumps(user_preferences),
                    now_iso
                ))
            conn.close()
        except Exception as e:
            logger.warning(f"Local save career recommendations error: {e}")

        # Supabase
        try:
            payload = {
                "id": record_id,
                "user_id": user_id,
                "resume_id": resume_id,
                "recommendations": recommendations,
                "user_preferences": user_preferences
            }
            res = user_client.table("career_recommendations").insert(payload).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as sb_err:
            logger.info(f"Supabase career_recommendations table insert note: {sb_err}")

        return {
            "id": record_id,
            "user_id": user_id,
            "resume_id": resume_id,
            "recommendations": recommendations,
            "user_preferences": user_preferences,
            "created_at": now_iso
        }

    @classmethod
    def get_latest_career_recommendations(
        cls,
        user_client: Any,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        # Supabase
        try:
            res = (
                user_client.table("career_recommendations")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if res.data and len(res.data) > 0:
                row = res.data[0]
                recs = row.get("recommendations")
                if isinstance(recs, str):
                    recs = json.loads(recs)
                prefs = row.get("user_preferences")
                if isinstance(prefs, str):
                    prefs = json.loads(prefs)
                return {
                    "id": row.get("id"),
                    "user_id": row.get("user_id"),
                    "resume_id": row.get("resume_id"),
                    "recommendations": recs,
                    "user_preferences": prefs,
                    "created_at": row.get("created_at")
                }
        except Exception as e:
            logger.debug(f"Supabase career recommendations query fallback: {e}")

        # Local
        try:
            conn = _get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM career_recommendations
                WHERE user_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "resume_id": row["resume_id"],
                    "recommendations": json.loads(row["recommendations"]) if row["recommendations"] else [],
                    "user_preferences": json.loads(row["user_preferences"]) if row["user_preferences"] else {},
                    "created_at": row["created_at"]
                }
        except Exception as e:
            logger.warning(f"Local career recommendations query note: {e}")

        return None

    @classmethod
    def save_skill_gap_report(
        cls,
        user_client: Any,
        user_id: str,
        resume_id: Optional[str],
        career_slug: str,
        career_title: str,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        record_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        # Local
        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    INSERT INTO skill_gap_reports (
                        id, user_id, resume_id, career_slug, career_title,
                        overall_match_percentage, skills_have, skills_improve,
                        skills_missing, priority_gaps, learning_path, recommended_projects, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record_id,
                    user_id,
                    resume_id,
                    career_slug,
                    career_title,
                    float(report_data.get("overall_match_percentage", 0)),
                    json.dumps(report_data.get("skills_have", [])),
                    json.dumps(report_data.get("skills_improve", [])),
                    json.dumps(report_data.get("skills_missing", [])),
                    json.dumps(report_data.get("priority_gaps", [])),
                    json.dumps(report_data.get("learning_path", [])),
                    json.dumps(report_data.get("recommended_projects", [])),
                    now_iso
                ))
            conn.close()
        except Exception as e:
            logger.warning(f"Local save skill gap report error: {e}")

        # Supabase
        try:
            payload = {
                "id": record_id,
                "user_id": user_id,
                "resume_id": resume_id,
                "career_slug": career_slug,
                "career_title": career_title,
                "overall_match_percentage": float(report_data.get("overall_match_percentage", 0)),
                "skills_have": report_data.get("skills_have", []),
                "skills_improve": report_data.get("skills_improve", []),
                "skills_missing": report_data.get("skills_missing", []),
                "priority_gaps": report_data.get("priority_gaps", []),
                "learning_path": report_data.get("learning_path", []),
                "recommended_projects": report_data.get("recommended_projects", [])
            }
            res = user_client.table("skill_gap_reports").insert(payload).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as sb_err:
            logger.info(f"Supabase skill_gap_reports insert note: {sb_err}")

        return {
            "id": record_id,
            "user_id": user_id,
            "resume_id": resume_id,
            "career_slug": career_slug,
            "career_title": career_title,
            **report_data,
            "created_at": now_iso
        }

    @classmethod
    def get_latest_skill_gap_report(
        cls,
        user_client: Any,
        user_id: str,
        career_slug: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        # Supabase
        try:
            query = user_client.table("skill_gap_reports").select("*").eq("user_id", user_id)
            if career_slug:
                query = query.eq("career_slug", career_slug)
            res = query.order("created_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return {
                    "id": row.get("id"),
                    "user_id": row.get("user_id"),
                    "resume_id": row.get("resume_id"),
                    "career_slug": row.get("career_slug"),
                    "career_title": row.get("career_title"),
                    "overall_match_percentage": row.get("overall_match_percentage"),
                    "skills_have": row.get("skills_have") if isinstance(row.get("skills_have"), list) else json.loads(row.get("skills_have") or "[]"),
                    "skills_improve": row.get("skills_improve") if isinstance(row.get("skills_improve"), list) else json.loads(row.get("skills_improve") or "[]"),
                    "skills_missing": row.get("skills_missing") if isinstance(row.get("skills_missing"), list) else json.loads(row.get("skills_missing") or "[]"),
                    "priority_gaps": row.get("priority_gaps") if isinstance(row.get("priority_gaps"), list) else json.loads(row.get("priority_gaps") or "[]"),
                    "learning_path": row.get("learning_path") if isinstance(row.get("learning_path"), list) else json.loads(row.get("learning_path") or "[]"),
                    "recommended_projects": row.get("recommended_projects") if isinstance(row.get("recommended_projects"), list) else json.loads(row.get("recommended_projects") or "[]"),
                    "created_at": row.get("created_at")
                }
        except Exception as e:
            logger.debug(f"Supabase skill gap report query fallback: {e}")

        # Local
        try:
            conn = _get_db()
            cursor = conn.cursor()
            if career_slug:
                cursor.execute("""
                    SELECT * FROM skill_gap_reports
                    WHERE user_id = ? AND career_slug = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (user_id, career_slug))
            else:
                cursor.execute("""
                    SELECT * FROM skill_gap_reports
                    WHERE user_id = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "resume_id": row["resume_id"],
                    "career_slug": row["career_slug"],
                    "career_title": row["career_title"],
                    "overall_match_percentage": row["overall_match_percentage"],
                    "skills_have": json.loads(row["skills_have"]) if row["skills_have"] else [],
                    "skills_improve": json.loads(row["skills_improve"]) if row["skills_improve"] else [],
                    "skills_missing": json.loads(row["skills_missing"]) if row["skills_missing"] else [],
                    "priority_gaps": json.loads(row["priority_gaps"]) if row["priority_gaps"] else [],
                    "learning_path": json.loads(row["learning_path"]) if row["learning_path"] else [],
                    "recommended_projects": json.loads(row["recommended_projects"]) if row["recommended_projects"] else [],
                    "created_at": row["created_at"]
                }
        except Exception as e:
            logger.warning(f"Local skill gap report query note: {e}")

        return None

