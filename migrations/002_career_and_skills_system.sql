-- =====================================================================
-- PATHFORGE AI - Migration 002: Complete Career Intelligence System
-- Includes Resume Analysis, Career Catalogue, Career Recommendations,
-- Target Career Selections, and Skill Gap Reports with RLS.
-- =====================================================================

-- 1. Create resume_analysis table
CREATE TABLE IF NOT EXISTS public.resume_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES public.resumes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    personal_information JSONB NOT NULL DEFAULT '{}'::jsonb,
    professional_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    technical_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    soft_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    education JSONB NOT NULL DEFAULT '[]'::jsonb,
    work_experience JSONB NOT NULL DEFAULT '[]'::jsonb,
    projects JSONB NOT NULL DEFAULT '[]'::jsonb,
    certifications JSONB NOT NULL DEFAULT '[]'::jsonb,
    additional_information JSONB NOT NULL DEFAULT '[]'::jsonb,
    raw_analysis JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_resume_analysis_resume_id ON public.resume_analysis(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_analysis_user_id ON public.resume_analysis(user_id);
ALTER TABLE public.resume_analysis ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'resume_analysis_select_policy') THEN
        CREATE POLICY resume_analysis_select_policy ON public.resume_analysis FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'resume_analysis_insert_policy') THEN
        CREATE POLICY resume_analysis_insert_policy ON public.resume_analysis FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'resume_analysis_update_policy') THEN
        CREATE POLICY resume_analysis_update_policy ON public.resume_analysis FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'resume_analysis_delete_policy') THEN
        CREATE POLICY resume_analysis_delete_policy ON public.resume_analysis FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 2. Create career_recommendations table
CREATE TABLE IF NOT EXISTS public.career_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
    recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
    user_preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_career_recs_user_id ON public.career_recommendations(user_id);
ALTER TABLE public.career_recommendations ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'career_recommendations' AND policyname = 'career_recs_select_policy') THEN
        CREATE POLICY career_recs_select_policy ON public.career_recommendations FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'career_recommendations' AND policyname = 'career_recs_insert_policy') THEN
        CREATE POLICY career_recs_insert_policy ON public.career_recommendations FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'career_recommendations' AND policyname = 'career_recs_delete_policy') THEN
        CREATE POLICY career_recs_delete_policy ON public.career_recommendations FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 3. Create user_career_selections table
CREATE TABLE IF NOT EXISTS public.user_career_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    career_slug TEXT NOT NULL,
    career_title TEXT NOT NULL,
    career_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_user_career_selection UNIQUE (user_id)
);

CREATE INDEX IF NOT EXISTS idx_career_selection_user_id ON public.user_career_selections(user_id);
ALTER TABLE public.user_career_selections ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_career_selections' AND policyname = 'career_selection_select_policy') THEN
        CREATE POLICY career_selection_select_policy ON public.user_career_selections FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_career_selections' AND policyname = 'career_selection_insert_policy') THEN
        CREATE POLICY career_selection_insert_policy ON public.user_career_selections FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_career_selections' AND policyname = 'career_selection_update_policy') THEN
        CREATE POLICY career_selection_update_policy ON public.user_career_selections FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_career_selections' AND policyname = 'career_selection_delete_policy') THEN
        CREATE POLICY career_selection_delete_policy ON public.user_career_selections FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 4. Create skill_gap_reports table
CREATE TABLE IF NOT EXISTS public.skill_gap_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
    career_slug TEXT NOT NULL,
    career_title TEXT NOT NULL,
    overall_match_percentage NUMERIC(5,2) NOT NULL,
    skills_have JSONB NOT NULL DEFAULT '[]'::jsonb,
    skills_improve JSONB NOT NULL DEFAULT '[]'::jsonb,
    skills_missing JSONB NOT NULL DEFAULT '[]'::jsonb,
    priority_gaps JSONB NOT NULL DEFAULT '[]'::jsonb,
    learning_path JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommended_projects JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_skill_gap_user_id ON public.skill_gap_reports(user_id);
ALTER TABLE public.skill_gap_reports ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'skill_gap_reports' AND policyname = 'skill_gap_select_policy') THEN
        CREATE POLICY skill_gap_select_policy ON public.skill_gap_reports FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'skill_gap_reports' AND policyname = 'skill_gap_insert_policy') THEN
        CREATE POLICY skill_gap_insert_policy ON public.skill_gap_reports FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'skill_gap_reports' AND policyname = 'skill_gap_delete_policy') THEN
        CREATE POLICY skill_gap_delete_policy ON public.skill_gap_reports FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 5. Storage bucket 'resumes' and RLS
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', false)
ON CONFLICT (id) DO NOTHING;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'resumes_storage_insert_policy') THEN
        CREATE POLICY resumes_storage_insert_policy ON storage.objects FOR INSERT TO authenticated
        WITH CHECK (bucket_id = 'resumes' AND (storage.foldername(name))[1] = auth.uid()::text);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'resumes_storage_select_policy') THEN
        CREATE POLICY resumes_storage_select_policy ON storage.objects FOR SELECT TO authenticated
        USING (bucket_id = 'resumes' AND (storage.foldername(name))[1] = auth.uid()::text);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'resumes_storage_delete_policy') THEN
        CREATE POLICY resumes_storage_delete_policy ON storage.objects FOR DELETE TO authenticated
        USING (bucket_id = 'resumes' AND (storage.foldername(name))[1] = auth.uid()::text);
    END IF;
END $$;

