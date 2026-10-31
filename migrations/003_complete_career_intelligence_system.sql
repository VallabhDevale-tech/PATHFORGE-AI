-- =====================================================================
-- PATHFORGE AI - Migration 003: Complete Career Intelligence System (Part 2)
-- Includes Learning Roadmaps (Feature 4), User Projects & Portfolio (Feature 5),
-- Learning Assessments & Quizzes, Skill Overrides, and Roadmap Adjustments (Feature 6).
-- All tables are secured with Row Level Security (RLS) guaranteeing user data isolation.
-- =====================================================================

-- 1. LEARNING ROADMAPS (Feature 4: Personalized Roadmap)
CREATE TABLE IF NOT EXISTS public.learning_roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    career_slug TEXT NOT NULL,
    duration_weeks INTEGER NOT NULL DEFAULT 8,
    weekly_hours INTEGER NOT NULL DEFAULT 10,
    progress_percentage NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    total_activities INTEGER NOT NULL DEFAULT 0,
    completed_activities INTEGER NOT NULL DEFAULT 0,
    roadmap_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_learning_roadmaps_user_id ON public.learning_roadmaps(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_roadmaps_career_slug ON public.learning_roadmaps(career_slug);
ALTER TABLE public.learning_roadmaps ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'learning_roadmaps' AND policyname = 'roadmaps_select_policy') THEN
        CREATE POLICY roadmaps_select_policy ON public.learning_roadmaps FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'learning_roadmaps' AND policyname = 'roadmaps_insert_policy') THEN
        CREATE POLICY roadmaps_insert_policy ON public.learning_roadmaps FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'learning_roadmaps' AND policyname = 'roadmaps_update_policy') THEN
        CREATE POLICY roadmaps_update_policy ON public.learning_roadmaps FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'learning_roadmaps' AND policyname = 'roadmaps_delete_policy') THEN
        CREATE POLICY roadmaps_delete_policy ON public.learning_roadmaps FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 2. USER PROJECTS & PORTFOLIO TRACKING (Feature 5: Project Recommendations)
CREATE TABLE IF NOT EXISTS public.user_projects (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    career_slug TEXT NOT NULL,
    title TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'Intermediate',
    status TEXT NOT NULL DEFAULT 'recommended',
    github_url TEXT DEFAULT '',
    demo_url TEXT DEFAULT '',
    user_notes TEXT DEFAULT '',
    project_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_user_projects_user_id ON public.user_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_career_slug ON public.user_projects(career_slug);
CREATE INDEX IF NOT EXISTS idx_user_projects_status ON public.user_projects(status);
ALTER TABLE public.user_projects ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_projects' AND policyname = 'user_projects_select_policy') THEN
        CREATE POLICY user_projects_select_policy ON public.user_projects FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_projects' AND policyname = 'user_projects_insert_policy') THEN
        CREATE POLICY user_projects_insert_policy ON public.user_projects FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_projects' AND policyname = 'user_projects_update_policy') THEN
        CREATE POLICY user_projects_update_policy ON public.user_projects FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_projects' AND policyname = 'user_projects_delete_policy') THEN
        CREATE POLICY user_projects_delete_policy ON public.user_projects FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 3. LEARNING ASSESSMENTS & TOPIC QUIZZES (Feature 6: Adaptive Learning)
CREATE TABLE IF NOT EXISTS public.learning_assessments (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    score_percentage NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    total_questions INTEGER NOT NULL DEFAULT 3,
    correct_count INTEGER NOT NULL DEFAULT 0,
    assessment_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_learning_assessments_user_id ON public.learning_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_assessments_skill ON public.learning_assessments(skill_name);
ALTER TABLE public.learning_assessments ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'learning_assessments' AND policyname = 'assessments_select_policy') THEN
        CREATE POLICY assessments_select_policy ON public.learning_assessments FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'learning_assessments' AND policyname = 'assessments_insert_policy') THEN
        CREATE POLICY assessments_insert_policy ON public.learning_assessments FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'learning_assessments' AND policyname = 'assessments_delete_policy') THEN
        CREATE POLICY assessments_delete_policy ON public.learning_assessments FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 4. USER SKILL SELF-ASSESSMENT OVERRIDES (Feature 3: Skill Gap Analyzer)
CREATE TABLE IF NOT EXISTS public.user_skill_overrides (
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    custom_level INTEGER NOT NULL CHECK (custom_level BETWEEN 1 AND 4),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    PRIMARY KEY (user_id, skill_name)
);

CREATE INDEX IF NOT EXISTS idx_skill_overrides_user_id ON public.user_skill_overrides(user_id);
ALTER TABLE public.user_skill_overrides ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_skill_overrides' AND policyname = 'skill_overrides_select_policy') THEN
        CREATE POLICY skill_overrides_select_policy ON public.user_skill_overrides FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_skill_overrides' AND policyname = 'skill_overrides_insert_policy') THEN
        CREATE POLICY skill_overrides_insert_policy ON public.user_skill_overrides FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_skill_overrides' AND policyname = 'skill_overrides_update_policy') THEN
        CREATE POLICY skill_overrides_update_policy ON public.user_skill_overrides FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_skill_overrides' AND policyname = 'skill_overrides_delete_policy') THEN
        CREATE POLICY skill_overrides_delete_policy ON public.user_skill_overrides FOR DELETE TO authenticated USING (auth.uid() = user_id);
    END IF;
END $$;


-- 5. ROADMAP ADJUSTMENTS (Feature 6: Adaptive Learning)
CREATE TABLE IF NOT EXISTS public.roadmap_adjustments (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    roadmap_id TEXT NOT NULL,
    focus_skill TEXT NOT NULL,
    adjustment_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_roadmap_adjustments_user_id ON public.roadmap_adjustments(user_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_adjustments_status ON public.roadmap_adjustments(status);
ALTER TABLE public.roadmap_adjustments ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'roadmap_adjustments' AND policyname = 'adjustments_select_policy') THEN
        CREATE POLICY adjustments_select_policy ON public.roadmap_adjustments FOR SELECT TO authenticated USING (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'roadmap_adjustments' AND policyname = 'adjustments_insert_policy') THEN
        CREATE POLICY adjustments_insert_policy ON public.roadmap_adjustments FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'roadmap_adjustments' AND policyname = 'adjustments_update_policy') THEN
        CREATE POLICY adjustments_update_policy ON public.roadmap_adjustments FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

