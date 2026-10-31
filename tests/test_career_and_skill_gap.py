import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from app.auth import AuthenticatedUser, get_current_user
from app.main import app
from app.services.career_catalogue import CAREER_ROLES_CATALOGUE, get_role_by_slug
from app.services.ai_career_service import compute_career_match, generate_career_recommendations
from app.services.ai_skill_gap_service import analyze_skill_gaps, generate_skill_gap_report
from app.services.storage_manager import HybridStorageManager


class TestCareerAndSkillGapSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.test_user = AuthenticatedUser(
            id="test-career-user-123",
            email="career_tester@example.com",
            access_token="mock_career_token"
        )

        cls.sample_resume_analysis = {
            "personal_information": {
                "full_name": "Jordan Developer",
                "email": "jordan@example.com"
            },
            "professional_summary": {
                "existing_summary": "Full Stack Engineer with 3 years building web APIs and interfaces.",
                "main_strengths": ["Python", "FastAPI", "React", "PostgreSQL"],
                "primary_areas_of_experience": ["Web Development", "Backend"]
            },
            "technical_skills": ["Python", "FastAPI", "React", "JavaScript", "SQL", "PostgreSQL", "Git", "HTML", "CSS"],
            "soft_skills": ["Problem-solving", "Teamwork", "Communication"],
            "education": [
                {
                    "degree": "B.S. Computer Science",
                    "institution": "State University",
                    "graduation_year": "2021",
                    "relevant_coursework": ["Data Structures", "Algorithms"]
                }
            ],
            "work_experience": [
                {
                    "company": "Tech Innovations",
                    "job_title": "Full Stack Developer",
                    "start_date": "2021",
                    "end_date": "Present",
                    "responsibilities": ["Developed backend REST APIs using FastAPI", "Created React user interfaces"],
                    "achievements": ["Improved page load speed by 35%"]
                }
            ],
            "projects": [
                {
                    "project_title": "E-Commerce Microservices",
                    "description": "Scalable checkout pipeline using FastAPI, React, and PostgreSQL.",
                    "technologies_used": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
                    "contributions": ["Architected database schemas and endpoints."]
                }
            ],
            "certifications": [],
            "additional_information": []
        }

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    # -------------------------------------------------------------------------
    # 1. Career Role Catalogue Tests
    # -------------------------------------------------------------------------
    def test_01_catalogue_contains_all_13_required_roles(self):
        """Verifies that the career catalogue contains exactly the 13 required roles."""
        self.assertEqual(len(CAREER_ROLES_CATALOGUE), 13)
        slugs = [r["slug"] for r in CAREER_ROLES_CATALOGUE]
        required_slugs = [
            "software-developer",
            "frontend-developer",
            "backend-developer",
            "full-stack-developer",
            "python-developer",
            "data-analyst",
            "data-scientist",
            "machine-learning-engineer",
            "ai-engineer",
            "cloud-engineer",
            "devops-engineer",
            "cybersecurity-analyst",
            "ui-ux-designer"
        ]
        for req in required_slugs:
            self.assertIn(req, slugs, f"Missing required career role: {req}")

    def test_02_catalogue_api_endpoint(self):
        """Test GET /careers/catalogue returns 200 and 13 roles."""
        res = self.client.get("/careers/catalogue")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total"], 13)

    # -------------------------------------------------------------------------
    # 2. Career Path Recommender Matching Tests
    # -------------------------------------------------------------------------
    def test_03_career_matching_algorithm(self):
        """Test that full stack role scores highest for full stack resume."""
        full_stack_role = get_role_by_slug("full-stack-developer")
        match = compute_career_match(
            role=full_stack_role,
            user_skills=self.sample_resume_analysis["technical_skills"],
            user_soft_skills=self.sample_resume_analysis["soft_skills"],
            user_projects=self.sample_resume_analysis["projects"],
            user_education=self.sample_resume_analysis["education"],
            user_experience=self.sample_resume_analysis["work_experience"],
            user_preferences={}
        )
        self.assertGreaterEqual(match["compatibility_score"], 70)
        self.assertIn("Python", match["existing_skills"])
        self.assertIn("React", match["existing_skills"])
        self.assertTrue(len(match["why_matched"]) > 20)

    def test_04_top_5_recommendations_generation(self):
        """Test generate_career_recommendations returns exactly 5 sorted roles."""
        import asyncio
        recs = asyncio.run(generate_career_recommendations(self.sample_resume_analysis))
        self.assertEqual(len(recs), 5)
        # Verify descending order of compatibility score
        scores = [r["compatibility_score"] for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_05_freshers_student_support(self):
        """Test that freshers with zero work experience receive valid explainable recommendations."""
        fresher_profile = {
            "technical_skills": ["Python", "SQL", "Pandas", "Data Structures"],
            "soft_skills": ["Problem-solving"],
            "education": [{"degree": "B.Tech Computer Science", "relevant_coursework": ["Algorithms"]}],
            "work_experience": [],
            "projects": [
                {
                    "project_title": "Student Analytics Portal",
                    "description": "Built data exploration dashboard using Python and SQL.",
                    "technologies_used": ["Python", "SQL", "Pandas"]
                }
            ]
        }
        import asyncio
        recs = asyncio.run(generate_career_recommendations(fresher_profile))
        self.assertEqual(len(recs), 5)
        self.assertGreater(recs[0]["compatibility_score"], 40)

    # -------------------------------------------------------------------------
    # 3. Target Career Selection & Persistence Tests
    # -------------------------------------------------------------------------
    def test_06_target_career_selection_flow(self):
        """Test POST /careers/select and GET /careers/selected."""
        app.dependency_overrides[get_current_user] = lambda: self.test_user

        select_res = self.client.post("/careers/select", json={
            "career_slug": "full-stack-developer",
            "career_title": "Full Stack Developer"
        })
        self.assertEqual(select_res.status_code, 200)

        get_res = self.client.get("/careers/selected")
        self.assertEqual(get_res.status_code, 200)
        data = get_res.json()
        self.assertTrue(data["has_selection"])
        self.assertEqual(data["data"]["career_slug"], "full-stack-developer")

    # -------------------------------------------------------------------------
    # 4. Skill Gap Analyzer Tests
    # -------------------------------------------------------------------------
    def test_07_skill_gap_classification(self):
        """Test that skills are categorized into Have, Improve, and Missing."""
        report = analyze_skill_gaps(self.sample_resume_analysis, "full-stack-developer")
        self.assertEqual(report["career_slug"], "full-stack-developer")
        self.assertIn("overall_match_percentage", report)
        self.assertGreater(report["overall_match_percentage"], 50)

        # Candidate has Python and React
        skills_have_names = [s["skill"] for s in report["skills_have"]]
        self.assertTrue("Python" in skills_have_names or "React" in skills_have_names)

        # Candidate does not have TypeScript in skills -> should be in missing
        skills_missing_names = [s["skill"] for s in report["skills_missing"]]
        self.assertIn("TypeScript", skills_missing_names)

        # Check that priority gaps and learning path are generated
        self.assertGreater(len(report["priority_gaps"]), 0)
        self.assertEqual(len(report["learning_path"]), 3)
        self.assertGreaterEqual(len(report["recommended_projects"]), 2)

    def test_08_skill_gap_api_endpoint(self):
        """Test POST /skills/analyze returns complete structured report."""
        app.dependency_overrides[get_current_user] = lambda: self.test_user

        # Seed mock resume analysis into local store
        HybridStorageManager.save_resume_analysis(
            None,
            self.test_user.id,
            "mock-resume-id-789",
            self.sample_resume_analysis
        )

        with patch("app.services.resume_service.ResumeService.get_user_resumes") as mock_resumes:
            mock_resumes.return_value = [{"id": "mock-resume-id-789"}]
            with patch("app.services.resume_service.ResumeService.get_resume_analysis") as mock_analysis:
                mock_analysis.return_value = {"analysis": self.sample_resume_analysis}

                res = self.client.post("/skills/analyze", json={
                    "career_slug": "backend-developer",
                    "resume_id": "mock-resume-id-789"
                })
                self.assertEqual(res.status_code, 200)
                data = res.json()["data"]
                self.assertEqual(data["career_slug"], "backend-developer")
                self.assertIn("overall_match_percentage", data)
                self.assertIn("skills_have", data)
                self.assertIn("skills_missing", data)

    # -------------------------------------------------------------------------
    # 5. Page Rendering Tests
    # -------------------------------------------------------------------------
    def test_09_career_recommender_page_renders(self):
        """Test GET /career-recommender renders HTML."""
        res = self.client.get("/career-recommender")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Career Path Recommender", res.text)
        self.assertIn("Top 5 Recommended Career Paths", res.text)

    def test_10_skill_gap_analyzer_page_renders(self):
        """Test GET /skill-gap-analyzer renders HTML."""
        res = self.client.get("/skill-gap-analyzer")
        self.assertEqual(res.status_code, 200)
        self.assertIn("AI Skill Gap Analyzer", res.text)
        self.assertIn("Target Career Role to Analyze Against", res.text)


if __name__ == "__main__":
    unittest.main()

