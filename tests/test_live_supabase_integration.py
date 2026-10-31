import unittest
import uuid
from app.database import supabase, SUPABASE_URL, SUPABASE_KEY
from app.auth import get_user_supabase_client, ensure_user_profile


class TestLiveSupabaseIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a unique test user in Supabase Auth
        cls.test_email = f"pathforge_test_{uuid.uuid4().hex[:8]}@example.com"
        cls.test_password = "SecurePassword123!"
        
        try:
            signup_res = supabase.auth.sign_up({"email": cls.test_email, "password": cls.test_password})
            if signup_res.session:
                cls.token = signup_res.session.access_token
                cls.user_id = signup_res.user.id
            else:
                signin_res = supabase.auth.sign_in_with_password({"email": cls.test_email, "password": cls.test_password})
                cls.token = signin_res.session.access_token
                cls.user_id = signin_res.user.id
        except Exception:
            signin_res = supabase.auth.sign_in_with_password({"email": cls.test_email, "password": cls.test_password})
            cls.token = signin_res.session.access_token
            cls.user_id = signin_res.user.id

        cls.user_client = get_user_supabase_client(cls.token)
        # Ensure profile exists
        ensure_user_profile(cls.user_id, cls.test_email, cls.token)

    def test_live_01_user_profile_creation(self):
        """Verify that authenticated user profile exists in public.profiles."""
        profile_res = self.user_client.table("profiles").select("*").eq("id", self.user_id).execute()
        self.assertTrue(len(profile_res.data) > 0, "Profile should exist for authenticated user.")
        self.assertEqual(profile_res.data[0]["email"], self.test_email)

    def test_live_02_resume_crud_with_rls(self):
        """Verify that authenticated user can insert, select, and delete their own resumes under RLS."""
        # 1. Insert
        insert_data = {
            "user_id": self.user_id,
            "file_name": "live_integration_test.pdf",
            "file_path": f"{self.user_id}/live_integration_test.pdf",
            "extracted_text": "Live test resume content for automated verification.",
            "processing_status": "completed"
        }
        res = self.user_client.table("resumes").insert(insert_data).execute()
        self.assertTrue(len(res.data) > 0, "Insert should succeed.")
        resume_id = res.data[0]["id"]

        # 2. Query
        fetch_res = self.user_client.table("resumes").select("*").eq("id", resume_id).execute()
        self.assertEqual(len(fetch_res.data), 1)
        self.assertEqual(fetch_res.data[0]["file_name"], "live_integration_test.pdf")

        # 3. Delete
        del_res = self.user_client.table("resumes").delete().eq("id", resume_id).execute()
        
        # Verify deleted
        verify_res = self.user_client.table("resumes").select("*").eq("id", resume_id).execute()
        self.assertEqual(len(verify_res.data), 0)


if __name__ == "__main__":
    unittest.main()

