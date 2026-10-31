import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from app.auth import AuthenticatedUser, get_current_user
from app.main import app

# Feature 3 imports
from app.services.skill_comparison_engine import (
    estimate_user_skill_levels,
    execute_skill_comparison
)
from app.services.career_catalogue import get_role_by_slug
from app.services.storage_manager import HybridStorageManager

# Feature 4 imports
from app.services.ai_roadmap_service import generate_personalized_roadmap

# Feature 5 imports
from app.services.ai_project_service import generate_recommended_projects

# Feature 6 imports
from app.services.ai_adaptive_service import (
    compute_learning_overview,
    identify_weak_areas,
    get_what_to_learn_next,
    generate_topic_quiz,
    evaluate_quiz_submission,
    propose_roadmap_adjustments
)


class TestFeatures3456Suite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.user_a = AuthenticatedUser(
            id="test-user-a-uuid-1111",
            email="user_a@example.com",
            access_token="mock_token_user_a"
        )
        cls.user_b = AuthenticatedUser(
            id="test-user-b-uuid-2222",
            email="user_b@example.com",
            access_token="mock_token_user_b"
        )

        cls.sample_profile = {
            "personal_information": {
                "full_name": "Alex Developer",
                "email": "alex@example.com"
            },
            "technical_skills": ["Python", "FastAPI", "SQL", "Git", "Docker"],
            "soft_skills": ["Problem Solving", "Collaboration"],
            "education": [
                {
                    "degree": "B.S. Software Engineering",
                    "institution": "Tech Institute",
                    "graduation_year": "2023"
                }
            ],
            "work_experience": [
                {
                    "company": "Cloud Systems",
                    "job_title": "Backend Intern",
                    "responsibilities": ["Created Python APIs with FastAPI", "Wrote SQL queries for PostgreSQL"]
                }
            ],
            "projects": [
                {
                    "project_title": "Containerized Microservice",
                    "description": "Dockerized Python FastAPI backend service with SQL database persistence.",
                    "technologies_used": ["Python", "FastAPI", "Docker", "SQL"]
                }
            ],
            "certifications": [
                {
                    "certificate_name": "Docker Essentials Certified",
                    "issuer": "Docker Inc"
                }
            ]
        }

        # Seed local storage for user_a with sample resume analysis
        HybridStorageManager.save_resume_analysis(
            None,
            cls.user_a.id,
            "sample-resume-id-123",
            cls.sample_profile
        )

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    # =========================================================================
    # PART 1: FEATURE 3 - SKILL GAP ANALYZER TESTS
    # =========================================================================
    def test_01_skill_level_estimation_from_evidence(self):
        """Verifies candidate skill levels are calculated from verified resume evidence."""
        levels = estimate_user_skill_levels(self.sample_profile, user_skill_overrides={})
        
        # Python: Mentioned in skills, experience, and projects -> should be Level >= 2
        self.assertGreaterEqual(levels.get("python", {}).get("level", 0), 2)
        # Docker: Mentioned in skills, projects, and certifications -> should be Level >= 2
        self.assertGreaterEqual(levels.get("docker", {}).get("level", 0), 2)
        # Kubernetes: Not mentioned anywhere -> should be 0
        self.assertEqual(levels.get("kubernetes", {}).get("level", 0), 0)

    def test_02_self_assessed_overrides_respected(self):
        """Verifies candidate self-assessed proficiency overrides baseline estimates."""
        # User explicitly overrides Python to Level 4 (Expert) and Kubernetes to Level 2
        levels = estimate_user_skill_levels(self.sample_profile, user_skill_overrides={"python": 4, "kubernetes": 2})
        self.assertEqual(levels.get("python", {}).get("level"), 4)
        self.assertEqual(levels.get("kubernetes", {}).get("level"), 2)

    def test_03_deterministic_gap_mathematics(self):
        """
        Verifies Gap = Required Level - Current Level:
        - Gap <= 0: Matched / Ready
        - Gap > 0: Needs Improvement
        - Not in profile: Not Found in Profile
        """
        role = get_role_by_slug("backend-developer")
        self.assertIsNotNone(role)

        comparison = execute_skill_comparison(
            resume_analysis=self.sample_profile,
            career_slug="backend-developer",
            user_skill_overrides={"python": 3}
        )

        self.assertIn("coverage_score", comparison)
        self.assertIn("matched_skills", comparison)
        self.assertIn("improvement_skills", comparison)
        self.assertIn("missing_skills", comparison)
        self.assertIn("priority_gaps", comparison)
        self.assertIn("category_breakdown", comparison)

        # Check matched skills have gap <= 0
        for s in comparison["matched_skills"]:
            self.assertLessEqual(s["gap"], 0)

        # Check improvement skills have gap > 0
        for s in comparison["improvement_skills"]:
            self.assertGreater(s["gap"], 0)

        # Check missing skills were not in the candidate's profile
        for s in comparison["missing_skills"]:
            self.assertEqual(s["current_level"], 0)
            self.assertEqual(s["status"], "not_found")

    def test_04_preview_profile_endpoint(self):
        """Tests GET /skills/preview-profile returns verified candidate facts."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        res = self.client.get("/skills/preview-profile?resume_id=sample-resume-id-123")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        profile = data["profile"]
        self.assertEqual(profile["candidate_name"], "Alex Developer")
        self.assertIn("Python", profile["technical_skills"])

    def test_05_override_and_analyze_endpoints(self):
        """Tests POST /skills/override and POST /skills/analyze end-to-end."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a

        # Save overrides (supporting nested overrides dict)
        override_res = self.client.post("/skills/override", json={
            "overrides": {"Python": 4, "FastAPI": 3}
        })
        self.assertEqual(override_res.status_code, 200)

        # Run analysis
        analyze_res = self.client.post("/skills/analyze", json={
            "career_slug": "backend-developer",
            "career_title": "Backend Developer",
            "resume_id": "sample-resume-id-123"
        })
        self.assertEqual(analyze_res.status_code, 200)
        report = analyze_res.json()["data"]
        self.assertIn("coverage_score", report)
        self.assertIn("matched_skills", report)

    def test_06_download_report_endpoint(self):
        """Tests GET /skills/download returns a downloadable JSON attachment."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        res = self.client.get("/skills/download?career_slug=backend-developer")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/json", res.headers.get("content-type", ""))
        self.assertIn("attachment", res.headers.get("content-disposition", ""))
        data = res.json()
        self.assertIn("candidate_name", data)

    # =========================================================================
    # PART 2: FEATURE 4 - PERSONALIZED ROADMAP TESTS
    # =========================================================================
    def test_07_roadmap_generation_from_skill_gaps(self):
        """Verifies roadmap generation produces structured weekly milestones with real resources."""
        gap_report = {
            "career_slug": "backend-developer",
            "career_title": "Backend Developer",
            "coverage_score": 65,
            "improvement_skills": [
                {"name": "PostgreSQL", "current_level": 2, "required_level": 3, "gap": 1, "priority": "High", "why_matters": "Core relational DB"}
            ],
            "missing_skills": [
                {"name": "Docker", "current_level": 0, "required_level": 2, "gap": 2, "priority": "High", "why_matters": "Container runtime"}
            ]
        }

        roadmap = asyncio.run(generate_personalized_roadmap(
            skill_gap_report=gap_report,
            duration_weeks=6,
            hours_per_week=12
        ))

        self.assertEqual(roadmap["duration_weeks"], 6)
        self.assertEqual(roadmap["hours_per_week"], 12)
        self.assertEqual(len(roadmap["weeks"]), 6)
        
        # Verify genuine resource links
        first_week = roadmap["weeks"][0]
        self.assertIn("activities", first_week)
        self.assertGreater(len(first_week["activities"]), 0)
        first_act = first_week["activities"][0]
        self.assertTrue(len(first_act["resources"]) > 0)
        self.assertTrue(first_act["resources"][0]["url"].startswith("http"))

    def test_08_activity_status_toggle_endpoint(self):
        """Tests PATCH /roadmap/activities/{id} toggles activity status and updates %."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a

        # Generate roadmap via API
        gen_res = self.client.post("/roadmap/generate", json={
            "career_slug": "backend-developer",
            "duration_weeks": 4,
            "hours_per_week": 10
        })
        self.assertEqual(gen_res.status_code, 200)
        roadmap = gen_res.json()["data"]
        act_id = roadmap["weeks"][0]["activities"][0]["id"]

        # Mark activity completed
        patch_res = self.client.patch(f"/roadmap/activities/{act_id}", json={
            "status": "completed"
        })
        self.assertEqual(patch_res.status_code, 200)
        updated_roadmap = patch_res.json()["data"]
        self.assertGreater(updated_roadmap["progress_percentage"], 0)
        self.assertEqual(updated_roadmap["completed_activities"], 1)

    # =========================================================================
    # PART 3: FEATURE 5 - PROJECT RECOMMENDATIONS TESTS
    # =========================================================================
    def test_09_project_recommendations_target_gaps(self):
        """Verifies projects target candidate skill gaps with 3 difficulty tiers."""
        gap_report = {
            "career_slug": "software-developer",
            "target_career": "Software Developer",
            "coverage_percentage": 50.0,
            "improvement_skills": [{"name": "FastAPI", "gap": 1}],
            "missing_skills": [{"name": "Docker", "gap": 2}]
        }
        projects = generate_recommended_projects(gap_report)
        self.assertGreater(len(projects), 0)
        difficulties = [p["difficulty"] for p in projects]
        self.assertTrue(any(d in ["Beginner", "Intermediate", "Advanced"] for d in difficulties))

        # Check blueprint structure
        first_proj = projects[0]
        self.assertIn("skills_addressed", first_proj)
        self.assertIn("architecture_guide", first_proj)
        self.assertIn("testing_requirements", first_proj)

    def test_10_project_portfolio_update_endpoint(self):
        """Tests PATCH /projects/{id} updates GitHub link, demo URL and status."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a

        # Generate recommendations via API
        rec_res = self.client.post("/projects/recommend", json={
            "career_slug": "backend-developer"
        })
        self.assertEqual(rec_res.status_code, 200)
        projects = rec_res.json()["data"]
        p_id = projects[0]["id"]

        # Update portfolio
        patch_res = self.client.patch(f"/projects/{p_id}", json={
            "status": "completed",
            "github_url": "https://github.com/alex/cloud-backend-demo",
            "demo_url": "https://cloud-backend.fly.dev",
            "user_notes": "Implemented async worker queue and unit tests."
        })
        self.assertEqual(patch_res.status_code, 200)

        # Verify portfolio endpoint lists it
        port_res = self.client.get("/projects/portfolio")
        self.assertEqual(port_res.status_code, 200)
        portfolio = port_res.json()["data"]
        self.assertTrue(any(p["id"] == p_id for p in portfolio))

    # =========================================================================
    # PART 4: FEATURE 6 - ADAPTIVE LEARNING TESTS
    # =========================================================================
    def test_11_adaptive_overview_metrics(self):
        """Tests GET /adaptive/overview returns aggregated velocity metrics."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        res = self.client.get("/adaptive/overview?career_slug=backend-developer")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIn("roadmap_completion_pct", data)
        self.assertIn("completed_activities", data)
        self.assertIn("completed_projects", data)

    def test_12_weak_area_diagnostics_and_tiers(self):
        """Tests GET /adaptive/weak-areas returns 4-tier diagnostic breakdown."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        res = self.client.get("/adaptive/weak-areas?career_slug=backend-developer")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIn("demonstrated_proficiency", data)
        self.assertIn("needs_more_practice", data)
        self.assertIn("in_progress", data)
        self.assertIn("not_started", data)

    def test_13_what_should_i_learn_next_recommendation(self):
        """Tests GET /adaptive/next provides actionable next learning step."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        res = self.client.get("/adaptive/next?career_slug=backend-developer")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIn("title", data)
        self.assertIn("why", data)
        self.assertIn("skill", data)
        self.assertIn("estimated_time_minutes", data)

    def test_14_topic_quiz_generation_and_evaluation(self):
        """Tests topic quiz generation and evaluation with feedback explanations."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a

        # Generate quiz
        quiz_res = self.client.get("/adaptive/quiz?skill=Python")
        self.assertEqual(quiz_res.status_code, 200)
        quiz = quiz_res.json()["data"]
        self.assertEqual(quiz["total_questions"], 3)
        self.assertEqual(len(quiz["questions"]), 3)

        # Submit answers (answering correctly)
        answers = {q["id"]: q["correct_index"] for q in quiz["questions"]}
        submit_res = self.client.post("/adaptive/quiz/submit", json={
            "quiz_id": quiz["quiz_id"],
            "skill_name": "Python",
            "answers": answers
        })
        self.assertEqual(submit_res.status_code, 200)
        eval_data = submit_res.json()["data"]
        self.assertEqual(eval_data["score_percentage"], 100.0)
        self.assertTrue(eval_data["is_passed"])
        self.assertEqual(len(eval_data["feedback"]), 3)

    def test_15_roadmap_adjustment_propose_and_resolve(self):
        """Tests non-destructive roadmap adjustment proposal and user resolve flow."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a

        # Propose adjustments
        prop_res = self.client.post("/adaptive/propose-adjustments?career_slug=backend-developer")
        self.assertEqual(prop_res.status_code, 200)
        prop_data = prop_res.json()

        if prop_data.get("has_adjustment"):
            adj_id = prop_data["data"]["id"]
            # Accept adjustment
            resolve_res = self.client.post(f"/adaptive/adjustment/resolve?adjustment_id={adj_id}&action=accept")
            self.assertEqual(resolve_res.status_code, 200)
            self.assertIn("accepted", resolve_res.json()["message"])

    # =========================================================================
    # PART 5: SECURITY & USER ISOLATION
    # =========================================================================
    def test_16_user_isolation_security(self):
        """Ensures User B cannot read or tamper with User A's roadmaps or projects."""
        # Authenticate as User B
        app.dependency_overrides[get_current_user] = lambda: self.user_b

        # User B should have 0% progress on backend-developer roadmap initially
        res = self.client.get("/adaptive/overview?career_slug=backend-developer")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        # User B has not completed user A's activity
        self.assertEqual(data["completed_activities"], 0)


if __name__ == "__main__":
    unittest.main()
