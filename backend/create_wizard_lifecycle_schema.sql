-- Migration: Create Wizard Lifecycle System Schema
-- Date: 2025-11-19
-- Description: Create all tables for the new wizard lifecycle system
-- Components: Wizard Templates, Wizard Runs, Store Wizard, Play Wizard

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- WIZARD TEMPLATE SYSTEM
-- ============================================================================

-- Wizard Templates table
CREATE TABLE wizard_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(255) NOT NULL,
    template_description TEXT,
    category VARCHAR(100),
    icon VARCHAR(50),
    difficulty_level VARCHAR(20),
    estimated_time INTEGER,
    tags TEXT[],
    preview_image TEXT,
    step_count INTEGER,
    option_set_count INTEGER,
    is_system_template BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0,
    wizard_structure JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard'))
);

-- Wizard Template Ratings
CREATE TABLE wizard_template_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES wizard_templates(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, user_id)
);

-- ============================================================================
-- WIZARD RUN SYSTEM (Run Wizard + Store Wizard)
-- ============================================================================

-- Wizard Runs table
CREATE TABLE wizard_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    run_name VARCHAR(255),
    run_description TEXT,
    status VARCHAR(20) DEFAULT 'in_progress',
    current_step_index INTEGER DEFAULT 0,
    total_steps INTEGER,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    calculated_price DECIMAL(10,2),
    is_stored BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    metadata JSONB,
    CONSTRAINT check_status CHECK (status IN ('in_progress', 'completed', 'abandoned'))
);

-- Wizard Run Step Responses
CREATE TABLE wizard_run_step_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    step_id UUID REFERENCES steps(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    step_name VARCHAR(255),
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_spent_seconds INTEGER DEFAULT 0,
    UNIQUE(run_id, step_id)
);

-- Wizard Run Option Set Responses
CREATE TABLE wizard_run_option_set_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    step_response_id UUID REFERENCES wizard_run_step_responses(id) ON DELETE CASCADE,
    option_set_id UUID REFERENCES option_sets(id) ON DELETE CASCADE,
    option_set_name VARCHAR(255),
    selection_type VARCHAR(50),
    response_value JSONB NOT NULL,
    selected_options UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Wizard Run File Uploads
CREATE TABLE wizard_run_file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    option_set_response_id UUID REFERENCES wizard_run_option_set_responses(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SHARING AND COLLABORATION
-- ============================================================================

-- Wizard Run Shares
CREATE TABLE wizard_run_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    share_token VARCHAR(255) UNIQUE NOT NULL,
    shared_by UUID REFERENCES users(id) ON DELETE CASCADE,
    share_type VARCHAR(20) DEFAULT 'view',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_share_type CHECK (share_type IN ('view', 'edit', 'clone'))
);

-- ============================================================================
-- COMPARISON AND ANALYTICS
-- ============================================================================

-- Wizard Run Comparisons (for comparing multiple runs)
CREATE TABLE wizard_run_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    comparison_name VARCHAR(255),
    run_ids UUID[] NOT NULL,
    created_by UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Wizard Templates indexes
CREATE INDEX idx_wizard_templates_category ON wizard_templates(category);
CREATE INDEX idx_wizard_templates_difficulty ON wizard_templates(difficulty_level);
CREATE INDEX idx_wizard_templates_system ON wizard_templates(is_system_template);
CREATE INDEX idx_wizard_templates_active ON wizard_templates(is_active);
CREATE INDEX idx_wizard_templates_created_at ON wizard_templates(created_at DESC);
CREATE INDEX idx_wizard_templates_usage ON wizard_templates(usage_count DESC);
CREATE INDEX idx_wizard_templates_rating ON wizard_templates(average_rating DESC);

-- Wizard Template Ratings indexes
CREATE INDEX idx_template_ratings_template ON wizard_template_ratings(template_id);
CREATE INDEX idx_template_ratings_user ON wizard_template_ratings(user_id);

-- Wizard Runs indexes
CREATE INDEX idx_wizard_runs_wizard ON wizard_runs(wizard_id);
CREATE INDEX idx_wizard_runs_user ON wizard_runs(user_id);
CREATE INDEX idx_wizard_runs_status ON wizard_runs(status);
CREATE INDEX idx_wizard_runs_stored ON wizard_runs(is_stored);
CREATE INDEX idx_wizard_runs_favorite ON wizard_runs(is_favorite);
CREATE INDEX idx_wizard_runs_started ON wizard_runs(started_at DESC);
CREATE INDEX idx_wizard_runs_completed ON wizard_runs(completed_at DESC);
CREATE INDEX idx_wizard_runs_last_accessed ON wizard_runs(last_accessed_at DESC);

-- Wizard Run Step Responses indexes
CREATE INDEX idx_run_step_responses_run ON wizard_run_step_responses(run_id);
CREATE INDEX idx_run_step_responses_step ON wizard_run_step_responses(step_id);

-- Wizard Run Option Set Responses indexes
CREATE INDEX idx_run_option_responses_run ON wizard_run_option_set_responses(run_id);
CREATE INDEX idx_run_option_responses_step_response ON wizard_run_option_set_responses(step_response_id);
CREATE INDEX idx_run_option_responses_option_set ON wizard_run_option_set_responses(option_set_id);

-- Wizard Run File Uploads indexes
CREATE INDEX idx_run_file_uploads_run ON wizard_run_file_uploads(run_id);
CREATE INDEX idx_run_file_uploads_response ON wizard_run_file_uploads(option_set_response_id);

-- Wizard Run Shares indexes
CREATE INDEX idx_run_shares_run ON wizard_run_shares(run_id);
CREATE INDEX idx_run_shares_token ON wizard_run_shares(share_token);
CREATE INDEX idx_run_shares_shared_by ON wizard_run_shares(shared_by);
CREATE INDEX idx_run_shares_active ON wizard_run_shares(is_active);

-- Wizard Run Comparisons indexes
CREATE INDEX idx_run_comparisons_created_by ON wizard_run_comparisons(created_by);

-- ============================================================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for wizard_templates
CREATE TRIGGER update_wizard_templates_updated_at
    BEFORE UPDATE ON wizard_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for wizard_run_option_set_responses
CREATE TRIGGER update_wizard_run_option_set_responses_updated_at
    BEFORE UPDATE ON wizard_run_option_set_responses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA (System Templates will be added separately)
-- ============================================================================

COMMIT;
