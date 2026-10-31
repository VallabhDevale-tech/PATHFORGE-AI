-- =====================================================================
-- PATHFORGE AI - Migration 001: Resume Analysis & Storage Setup
-- =====================================================================

-- 1. Create resume_analysis table to store structured AI analysis
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

-- Index for fast queries by resume_id and user_id
CREATE INDEX IF NOT EXISTS idx_resume_analysis_resume_id ON public.resume_analysis(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_analysis_user_id ON public.resume_analysis(user_id);

-- 2. Enable Row Level Security (RLS) on resume_analysis
ALTER TABLE public.resume_analysis ENABLE ROW LEVEL SECURITY;

-- 3. RLS Policies for resume_analysis table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'Users can view their own resume analyses'
    ) THEN
        CREATE POLICY "Users can view their own resume analyses"
            ON public.resume_analysis FOR SELECT
            TO authenticated
            USING (auth.uid() = user_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'Users can insert their own resume analyses'
    ) THEN
        CREATE POLICY "Users can insert their own resume analyses"
            ON public.resume_analysis FOR INSERT
            TO authenticated
            WITH CHECK (auth.uid() = user_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'Users can update their own resume analyses'
    ) THEN
        CREATE POLICY "Users can update their own resume analyses"
            ON public.resume_analysis FOR UPDATE
            TO authenticated
            USING (auth.uid() = user_id)
            WITH CHECK (auth.uid() = user_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'resume_analysis' AND policyname = 'Users can delete their own resume analyses'
    ) THEN
        CREATE POLICY "Users can delete their own resume analyses"
            ON public.resume_analysis FOR DELETE
            TO authenticated
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- 4. Create private Supabase Storage bucket 'resumes' if it doesn't already exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', false)
ON CONFLICT (id) DO NOTHING;

-- 5. Storage RLS Policies for the 'resumes' bucket
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'Authenticated users can upload to their resumes folder'
    ) THEN
        CREATE POLICY "Authenticated users can upload to their resumes folder"
            ON storage.objects FOR INSERT
            TO authenticated
            WITH CHECK (
                bucket_id = 'resumes' AND
                (storage.foldername(name))[1] = auth.uid()::text
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'Authenticated users can read their own resumes'
    ) THEN
        CREATE POLICY "Authenticated users can read their own resumes"
            ON storage.objects FOR SELECT
            TO authenticated
            USING (
                bucket_id = 'resumes' AND
                (storage.foldername(name))[1] = auth.uid()::text
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'Authenticated users can delete their own resumes'
    ) THEN
        CREATE POLICY "Authenticated users can delete their own resumes"
            ON storage.objects FOR DELETE
            TO authenticated
            USING (
                bucket_id = 'resumes' AND
                (storage.foldername(name))[1] = auth.uid()::text
            );
    END IF;
END $$;

