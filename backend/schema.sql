-- Multi-Wizard Platform Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. User Roles
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role_id UUID NOT NULL REFERENCES user_roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role_id ON users(role_id);

-- 3. Wizard Categories
CREATE TABLE wizard_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_wizard_categories_display_order ON wizard_categories(display_order);

-- 4. Wizards
CREATE TABLE wizards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES wizard_categories(id),
    created_by UUID NOT NULL REFERENCES users(id),
    icon VARCHAR(100),
    cover_image VARCHAR(500),
    is_published BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    allow_templates BOOLEAN DEFAULT TRUE,
    require_login BOOLEAN DEFAULT TRUE,
    allow_anonymous BOOLEAN DEFAULT FALSE,
    auto_save BOOLEAN DEFAULT TRUE,
    auto_save_interval INTEGER DEFAULT 30,
    estimated_time INTEGER,
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    tags JSONB DEFAULT '[]',
    total_sessions INTEGER DEFAULT 0,
    completed_sessions INTEGER DEFAULT 0,
    average_completion_time INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_wizards_category_id ON wizards(category_id);
CREATE INDEX idx_wizards_created_by ON wizards(created_by);
CREATE INDEX idx_wizards_is_published ON wizards(is_published);
CREATE INDEX idx_wizards_is_active ON wizards(is_active);

-- 5. Steps
CREATE TABLE steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID NOT NULL REFERENCES wizards(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    help_text TEXT,
    step_order INTEGER NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    is_skippable BOOLEAN DEFAULT FALSE,
    allow_back_navigation BOOLEAN DEFAULT TRUE,
    layout VARCHAR(50) DEFAULT 'vertical',
    custom_styles JSONB DEFAULT '{}',
    validation_rules JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(wizard_id, step_order)
);

CREATE INDEX idx_steps_wizard_id ON steps(wizard_id);
CREATE INDEX idx_steps_order ON steps(wizard_id, step_order);

-- 6. Option Sets
CREATE TABLE option_sets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    selection_type VARCHAR(50) NOT NULL CHECK (
        selection_type IN (
            'single_select', 'multiple_select', 'text_input', 'number_input',
            'date_input', 'time_input', 'datetime_input', 'file_upload',
            'rating', 'slider', 'color_picker', 'rich_text'
        )
    ),
    is_required BOOLEAN DEFAULT TRUE,
    min_selections INTEGER DEFAULT 0,
    max_selections INTEGER,
    min_value NUMERIC,
    max_value NUMERIC,
    regex_pattern VARCHAR(500),
    custom_validation JSONB DEFAULT '{}',
    display_order INTEGER DEFAULT 0,
    placeholder TEXT,
    help_text TEXT,
    step_increment NUMERIC DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_option_sets_step_id ON option_sets(step_id);
CREATE INDEX idx_option_sets_display_order ON option_sets(step_id, display_order);

-- 7. Options
CREATE TABLE options (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    option_set_id UUID NOT NULL REFERENCES option_sets(id) ON DELETE CASCADE,
    label VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    icon VARCHAR(100),
    image_url VARCHAR(500),
    price NUMERIC(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    is_default BOOLEAN DEFAULT FALSE,
    is_recommended BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_options_option_set_id ON options(option_set_id);
CREATE INDEX idx_options_display_order ON options(option_set_id, display_order);

-- 8. Option Dependencies
CREATE TABLE option_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    option_id UUID NOT NULL REFERENCES options(id) ON DELETE CASCADE,
    depends_on_option_id UUID NOT NULL REFERENCES options(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) NOT NULL CHECK (
        dependency_type IN ('requires', 'excludes', 'suggests', 'enables', 'disables')
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(option_id, depends_on_option_id)
);

CREATE INDEX idx_option_dependencies_option_id ON option_dependencies(option_id);
CREATE INDEX idx_option_dependencies_depends_on ON option_dependencies(depends_on_option_id);

-- 9. Flow Rules
CREATE TABLE flow_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID NOT NULL REFERENCES wizards(id) ON DELETE CASCADE,
    name VARCHAR(255),
    description TEXT,
    from_step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    to_step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    condition JSONB NOT NULL,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_flow_rules_wizard_id ON flow_rules(wizard_id);
CREATE INDEX idx_flow_rules_from_step ON flow_rules(from_step_id);
CREATE INDEX idx_flow_rules_to_step ON flow_rules(to_step_id);

-- 10. User Sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID NOT NULL REFERENCES wizards(id),
    user_id UUID REFERENCES users(id),
    session_name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress' CHECK (
        status IN ('in_progress', 'completed', 'abandoned', 'expired')
    ),
    current_step_id UUID REFERENCES steps(id),
    progress_percentage NUMERIC(5, 2) DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    browser_info JSONB DEFAULT '{}',
    total_time_seconds INTEGER,
    total_price NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_wizard_id ON user_sessions(wizard_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_status ON user_sessions(status);
CREATE INDEX idx_user_sessions_created_at ON user_sessions(created_at);

-- 11. Session Responses
CREATE TABLE session_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES user_sessions(id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES steps(id),
    option_set_id UUID NOT NULL REFERENCES option_sets(id),
    response_data JSONB NOT NULL,
    calculated_price NUMERIC(10, 2) DEFAULT 0,
    time_spent_seconds INTEGER,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, option_set_id)
);

CREATE INDEX idx_session_responses_session_id ON session_responses(session_id);
CREATE INDEX idx_session_responses_step_id ON session_responses(step_id);

-- 12. Templates
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID NOT NULL REFERENCES wizards(id),
    user_id UUID NOT NULL REFERENCES users(id),
    source_session_id UUID REFERENCES user_sessions(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_templates_wizard_id ON templates(wizard_id);
CREATE INDEX idx_templates_user_id ON templates(user_id);
CREATE INDEX idx_templates_is_public ON templates(is_public);

-- 13. Template Responses
CREATE TABLE template_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES steps(id),
    option_set_id UUID NOT NULL REFERENCES option_sets(id),
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(template_id, option_set_id)
);

CREATE INDEX idx_template_responses_template_id ON template_responses(template_id);

-- 14. Analytics Events
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES user_sessions(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    wizard_id UUID REFERENCES wizards(id) ON DELETE SET NULL,
    step_id UUID REFERENCES steps(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_data JSONB DEFAULT '{}',
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analytics_events_session_id ON analytics_events(session_id);
CREATE INDEX idx_analytics_events_wizard_id ON analytics_events(wizard_id);
CREATE INDEX idx_analytics_events_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_occurred_at ON analytics_events(occurred_at);

-- 15. Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- 16. System Settings
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed default roles
INSERT INTO user_roles (name, description, permissions) VALUES
('super_admin', 'Full system access', '{"all": true}'),
('admin', 'Wizard management access', '{"wizards": ["create", "read", "update", "delete"], "analytics": ["read"]}'),
('user', 'Standard user access', '{"sessions": ["create", "read", "update"], "templates": ["create", "read"]}');

-- Seed default settings
INSERT INTO system_settings (key, value, description, is_public) VALUES
('app_name', '"Multi-Wizard Platform"', 'Application name', true),
('max_session_duration', '86400', 'Maximum session duration in seconds (24 hours)', false),
('enable_anonymous_sessions', 'false', 'Allow anonymous wizard completion', false),
('default_auto_save_interval', '30', 'Default auto-save interval in seconds', false),
('max_file_upload_size', '10485760', 'Maximum file upload size in bytes (10MB)', false),
('supported_file_types', '["image/jpeg", "image/png", "application/pdf"]', 'Allowed file types for upload', true);
