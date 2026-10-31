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
    conn = sqlite3.connect(str(DB_PATH), timeout=15.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
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
            CREATE INDEX IF NOT EXISTS idx_la_user_resume ON resume_analysis(user_id, resume_id);
            CREATE INDEX IF NOT EXISTS idx_cr_user ON career_recommendations(user_id);
            CREATE INDEX IF NOT EXISTS idx_sgr_user ON skill_gap_reports(user_id);
            CREATE INDEX IF NOT EXISTS idx_sgr_user_career ON skill_gap_reports(user_id, career_slug);
            CREATE INDEX IF NOT EXISTS idx_lr_user ON learning_roadmaps(user_id);
            CREATE INDEX IF NOT EXISTS idx_lr_user_career ON learning_roadmaps(user_id, career_slug);
            CREATE INDEX IF NOT EXISTS idx_up_user ON user_projects(user_id);
            CREATE INDEX IF NOT EXISTS idx_up_user_career ON user_projects(user_id, career_slug);
            CREATE INDEX IF NOT EXISTS idx_la_user ON learning_assessments(user_id);
            CREATE INDEX IF NOT EXISTS idx_ra_user ON roadmap_adjustments(user_id);

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
                report_data TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS learning_roadmaps (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                career_slug TEXT NOT NULL,
                career_title TEXT NOT NULL,
                duration_weeks INTEGER NOT NULL,
                hours_per_week INTEGER NOT NULL,
                roadmap_data TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_projects (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                career_slug TEXT NOT NULL,
                title TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'recommended',
                github_url TEXT DEFAULT '',
                demo_url TEXT DEFAULT '',
                user_notes TEXT DEFAULT '',
                project_data TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS learning_assessments (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                score_percentage REAL NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                assessment_data TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_skill_overrides (
                user_id TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                custom_level INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, skill_name)
            );

            CREATE TABLE IF NOT EXISTS roadmap_adjustments (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                roadmap_id TEXT NOT NULL,
                focus_skill TEXT NOT NULL,
                adjustment_data TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            );
        """)

        # Add report_data column if existing database was created without it
        try:
            conn.execute("ALTER TABLE skill_gap_reports ADD COLUMN report_data TEXT DEFAULT '{}'")
        except Exception:
            pass

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
                        skills_missing, priority_gaps, learning_path, recommended_projects,
                        report_data, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(report_data),
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
                return {**report_data, "id": record_id, "created_at": now_iso}
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
                rep_data = row.get("report_data")
                if rep_data:
                    return rep_data if isinstance(rep_data, dict) else json.loads(rep_data)
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
                rep_data_str = row["report_data"] if "report_data" in row.keys() else None
                if rep_data_str and rep_data_str != "{}":
                    try:
                        return json.loads(rep_data_str)
                    except Exception:
                        pass
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

    # =========================================================================
    # FEATURE 4: PERSONALIZED ROADMAP METHODS
    # =========================================================================
    @classmethod
    def save_roadmap(
        cls,
        user_client: Any,
        user_id: str,
        roadmap_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        record_id = roadmap_data.get("id") or str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        career_slug = roadmap_data.get("career_slug", "software-developer")
        career_title = roadmap_data.get("target_career", "Software Engineering")
        duration = int(roadmap_data.get("duration_weeks", 8))
        hours = int(roadmap_data.get("hours_per_week", 10))

        # 1. Local SQLite
        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO learning_roadmaps (
                        id, user_id, career_slug, career_title, duration_weeks, hours_per_week,
                        roadmap_data, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record_id, user_id, career_slug, career_title, duration, hours,
                    json.dumps(roadmap_data), "active", now_iso, now_iso
                ))
            conn.close()
        except Exception as e:
            logger.warning(f"Local save roadmap error: {e}")

        # 2. Supabase
        try:
            payload = {
                "id": record_id,
                "user_id": user_id,
                "career_slug": career_slug,
                "career_title": career_title,
                "duration_weeks": duration,
                "hours_per_week": hours,
                "roadmap_data": roadmap_data,
                "status": "active"
            }
            user_client.table("learning_roadmaps").upsert(payload).execute()
        except Exception as e:
            logger.info(f"Supabase learning_roadmaps upsert note: {e}")

        return roadmap_data

    @classmethod
    def get_active_roadmap(
        cls,
        user_client: Any,
        user_id: str,
        career_slug: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        # Supabase
        try:
            query = user_client.table("learning_roadmaps").select("*").eq("user_id", user_id).eq("status", "active")
            if career_slug:
                query = query.eq("career_slug", career_slug)
            res = query.order("updated_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                data = res.data[0].get("roadmap_data")
                return data if isinstance(data, dict) else json.loads(data or "{}")
        except Exception as e:
            logger.debug(f"Supabase roadmap fetch fallback: {e}")

        # Local
        try:
            conn = _get_db()
            cursor = conn.cursor()
            if career_slug:
                cursor.execute("""
                    SELECT roadmap_data FROM learning_roadmaps
                    WHERE user_id = ? AND career_slug = ? AND status = 'active'
                    ORDER BY updated_at DESC LIMIT 1
                """, (user_id, career_slug))
            else:
                cursor.execute("""
                    SELECT roadmap_data FROM learning_roadmaps
                    WHERE user_id = ? AND status = 'active'
                    ORDER BY updated_at DESC LIMIT 1
                """, (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row["roadmap_data"])
        except Exception as e:
            logger.warning(f"Local roadmap query note: {e}")

        return None

    @classmethod
    def update_roadmap_activity_status(
        cls,
        user_client: Any,
        user_id: str,
        activity_id: str,
        new_status: str
    ) -> Optional[Dict[str, Any]]:
        """Updates activity status inside active roadmap and recalculates overall percentage."""
        roadmap = cls.get_active_roadmap(user_client, user_id)
        if not roadmap:
            return None

        updated = False
        total_acts = 0
        completed_acts = 0

        for w in roadmap.get("weeks", []):
            week_completed = True
            for act in w.get("activities", []):
                total_acts += 1
                if act.get("id") == activity_id:
                    act["status"] = new_status
                    updated = True
                if act.get("status") == "completed":
                    completed_acts += 1
                else:
                    week_completed = False
            w["is_completed"] = week_completed

        if updated:
            roadmap["completed_activities"] = completed_acts
            roadmap["total_activities"] = total_acts
            roadmap["progress_percentage"] = round((completed_acts / total_acts) * 100, 1) if total_acts > 0 else 0.0
            cls.save_roadmap(user_client, user_id, roadmap)

        return roadmap

    # =========================================================================
    # FEATURE 5: PROJECT RECOMMENDATIONS & PORTFOLIO METHODS
    # =========================================================================
    @classmethod
    def save_projects(
        cls,
        user_client: Any,
        user_id: str,
        career_slug: str,
        projects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            conn = _get_db()
            with conn:
                for p in projects:
                    conn.execute("""
                        INSERT OR REPLACE INTO user_projects (
                            id, user_id, career_slug, title, difficulty, status,
                            github_url, demo_url, user_notes, project_data, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        p["id"], user_id, career_slug, p.get("title", "Project"),
                        p.get("difficulty", "Intermediate"), p.get("status", "recommended"),
                        p.get("github_url", ""), p.get("demo_url", ""), p.get("user_notes", ""),
                        json.dumps(p), now_iso, now_iso
                    ))
            conn.close()
        except Exception as e:
            logger.warning(f"Local save projects error: {e}")
        return projects

    @classmethod
    def get_user_projects(
        cls,
        user_client: Any,
        user_id: str,
        career_slug: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            conn = _get_db()
            cursor = conn.cursor()
            if career_slug:
                cursor.execute("""
                    SELECT project_data, status, github_url, demo_url, user_notes
                    FROM user_projects
                    WHERE user_id = ? AND career_slug = ?
                    ORDER BY created_at DESC
                """, (user_id, career_slug))
            else:
                cursor.execute("""
                    SELECT project_data, status, github_url, demo_url, user_notes
                    FROM user_projects
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                """, (user_id,))
            rows = cursor.fetchall()
            conn.close()
            results = []
            for r in rows:
                p = json.loads(r["project_data"])
                p["status"] = r["status"]
                p["github_url"] = r["github_url"]
                p["demo_url"] = r["demo_url"]
                p["user_notes"] = r["user_notes"]
                results.append(p)
            return results
        except Exception as e:
            logger.warning(f"Local projects query error: {e}")
            return []

    @classmethod
    def update_project_status(
        cls,
        user_client: Any,
        user_id: str,
        project_id: str,
        status: Optional[str] = None,
        github_url: Optional[str] = None,
        demo_url: Optional[str] = None,
        user_notes: Optional[str] = None
    ) -> bool:
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            conn = _get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT project_data, status, github_url, demo_url, user_notes FROM user_projects WHERE id = ? AND user_id = ?", (project_id, user_id))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False

            p_data = json.loads(row["project_data"])
            curr_status = status or row["status"]
            curr_github = github_url if github_url is not None else row["github_url"]
            curr_demo = demo_url if demo_url is not None else row["demo_url"]
            curr_notes = user_notes if user_notes is not None else row["user_notes"]

            p_data["status"] = curr_status
            p_data["github_url"] = curr_github
            p_data["demo_url"] = curr_demo
            p_data["user_notes"] = curr_notes

            with conn:
                conn.execute("""
                    UPDATE user_projects
                    SET status = ?, github_url = ?, demo_url = ?, user_notes = ?, project_data = ?, updated_at = ?
                    WHERE id = ? AND user_id = ?
                """, (curr_status, curr_github, curr_demo, curr_notes, json.dumps(p_data), now_iso, project_id, user_id))
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"Project update error: {e}")
            return False

    # =========================================================================
    # FEATURE 6: ASSESSMENTS, SKILL OVERRIDES, & ADAPTATIONS
    # =========================================================================
    @classmethod
    def record_assessment(
        cls,
        user_client: Any,
        user_id: str,
        assessment_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        record_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        skill = assessment_dict.get("skill_name", "General")
        score = float(assessment_dict.get("score_percentage", 0.0))
        total_q = int(assessment_dict.get("total_questions", 0))
        correct = int(assessment_dict.get("correct_count", 0))

        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    INSERT INTO learning_assessments (
                        id, user_id, skill_name, score_percentage, total_questions, correct_count,
                        assessment_data, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (record_id, user_id, skill, score, total_q, correct, json.dumps(assessment_dict), now_iso))
            conn.close()
        except Exception as e:
            logger.warning(f"Record assessment error: {e}")

        return {**assessment_dict, "id": record_id, "created_at": now_iso}

    @classmethod
    def get_user_assessments(
        cls,
        user_client: Any,
        user_id: str
    ) -> List[Dict[str, Any]]:
        try:
            conn = _get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM learning_assessments WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [json.loads(r["assessment_data"]) for r in rows]
        except Exception as e:
            logger.warning(f"Get assessments error: {e}")
            return []

    @classmethod
    def save_skill_overrides(
        cls,
        user_id: str,
        overrides: Dict[str, int]
    ):
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            conn = _get_db()
            with conn:
                for skill, lvl in overrides.items():
                    conn.execute("""
                        INSERT OR REPLACE INTO user_skill_overrides (user_id, skill_name, custom_level, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, skill, int(lvl), now_iso))
            conn.close()
        except Exception as e:
            logger.warning(f"Save skill overrides error: {e}")

    @classmethod
    def get_skill_overrides(cls, user_id: str) -> Dict[str, int]:
        try:
            conn = _get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT skill_name, custom_level FROM user_skill_overrides WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return {r["skill_name"]: r["custom_level"] for r in rows}
        except Exception as e:
            logger.warning(f"Get skill overrides error: {e}")
            return {}

    @classmethod
    def save_adjustment(
        cls,
        user_client: Any,
        user_id: str,
        roadmap_id: str,
        adjustment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        adj_id = adjustment_data.get("id") or str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        focus = adjustment_data.get("focus_skill", "General")

        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO roadmap_adjustments (
                        id, user_id, roadmap_id, focus_skill, adjustment_data, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (adj_id, user_id, roadmap_id, focus, json.dumps(adjustment_data), "pending", now_iso))
            conn.close()
        except Exception as e:
            logger.warning(f"Save adjustment error: {e}")
        return adjustment_data

    @classmethod
    def get_pending_adjustment(
        cls,
        user_client: Any,
        user_id: str,
        roadmap_id: str
    ) -> Optional[Dict[str, Any]]:
        try:
            conn = _get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT adjustment_data FROM roadmap_adjustments
                WHERE user_id = ? AND roadmap_id = ? AND status = 'pending'
                ORDER BY created_at DESC LIMIT 1
            """, (user_id, roadmap_id))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row["adjustment_data"])
        except Exception as e:
            logger.warning(f"Get adjustment error: {e}")
        return None

    @classmethod
    def resolve_adjustment(
        cls,
        user_client: Any,
        user_id: str,
        adjustment_id: str,
        action: str  # "accept" or "reject"
    ) -> bool:
        new_status = "accepted" if action == "accept" else "rejected"
        try:
            conn = _get_db()
            with conn:
                conn.execute("""
                    UPDATE roadmap_adjustments
                    SET status = ?
                    WHERE id = ? AND user_id = ?
                """, (new_status, adjustment_id, user_id))
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"Resolve adjustment error: {e}")
            return False


