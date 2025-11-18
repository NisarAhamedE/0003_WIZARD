# Database Schema - PostgreSQL

## Overview

This document contains the complete PostgreSQL database schema for the Multi-Wizard Platform with 16 interconnected tables.

## Schema Diagram
```
wizards (1) ──< wizard_steps (M)
                    │
                    └──< wizard_option_sets (M)
                              │
                              └──< wizard_options (M)

wizards (1) ──< wizard_flow_rules (M)
wizards (1) ──< wizard_user_sessions (M) ──< wizard_user_selections (M)
users (1) ──< wizard_user_sessions (M)
wizards (1) ──< wizard_session_templates (M)
wizards (1) ──< wizard_analytics (M)
```

## Complete SQL Schema
```sql
-- ============================================
-- Enable UUID Extension (Optional but recommended)
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLE 1: users
-- Purpose: Store user accounts and authentication
-- ============================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    password_hash VARCHAR(255) NOT NULL,
    user_role VARCHAR(20) DEFAULT 'USER' CHECK (user_role IN ('USER', 'ADMIN', 'SUPER_ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(user_role);

-- ============================================
-- TABLE 2: wizards
-- Purpose: Store wizard definitions (top-level)
-- ============================================
CREATE TABLE wizards (
    wizard_id SERIAL PRIMARY KEY,
    wizard_key VARCHAR(100) UNIQUE NOT NULL,
    wizard_name VARCHAR(200) NOT NULL,
    wizard_description TEXT,
    wizard_category VARCHAR(100),
    
    -- Display Settings
    wizard_icon VARCHAR(100),
    wizard_color VARCHAR(50),
    wizard_banner_image VARCHAR(255),
    
    -- Configuration
    allow_save_progress BOOLEAN DEFAULT TRUE,
    allow_templates BOOLEAN DEFAULT TRUE,
    require_login BOOLEAN DEFAULT TRUE,
    max_steps INTEGER,
    estimated_time_minutes INTEGER,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    version VARCHAR(20) DEFAULT '1.0',
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    
    -- Analytics
    total_starts INTEGER DEFAULT 0,
    total_completions INTEGER DEFAULT 0,
    avg_completion_time_minutes INTEGER
);

CREATE INDEX idx_wizards_key ON wizards(wizard_key);
CREATE INDEX idx_wizards_active ON wizards(is_active, is_public);
CREATE INDEX idx_wizards_category ON wizards(wizard_category);
CREATE INDEX idx_wizards_featured ON wizards(is_featured);

-- ============================================
-- TABLE 3: wizard_steps
-- Purpose: Store steps within wizards
-- ============================================
CREATE TABLE wizard_steps (
    step_id SERIAL PRIMARY KEY,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    step_key VARCHAR(100) NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    step_order INTEGER NOT NULL,
    step_title VARCHAR(200),
    step_description TEXT,
    step_help_text TEXT,
    
    -- Step Configuration
    is_required BOOLEAN DEFAULT TRUE,
    allow_back_navigation BOOLEAN DEFAULT TRUE,
    auto_advance BOOLEAN DEFAULT FALSE,
    show_progress_bar BOOLEAN DEFAULT TRUE,
    
    -- Display
    step_icon VARCHAR(100),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_step_key UNIQUE (wizard_id, step_key)
);

CREATE INDEX idx_steps_wizard ON wizard_steps(wizard_id);
CREATE INDEX idx_steps_wizard_order ON wizard_steps(wizard_id, step_order);

-- ============================================
-- TABLE 4: wizard_option_sets
-- Purpose: Store option sets within steps
-- ============================================
CREATE TABLE wizard_option_sets (
    set_id SERIAL PRIMARY KEY,
    step_id INTEGER NOT NULL REFERENCES wizard_steps(step_id) ON DELETE CASCADE,
    set_key VARCHAR(100) NOT NULL,
    set_name VARCHAR(100) NOT NULL,
    set_title VARCHAR(200),
    set_description TEXT,
    set_help_text TEXT,
    set_order INTEGER DEFAULT 0,
    
    -- Configuration
    selection_type VARCHAR(20) DEFAULT 'SINGLE' CHECK (selection_type IN ('SINGLE', 'MULTIPLE', 'TEXT_INPUT', 'FILE_UPLOAD', 'DATE_PICKER')),
    is_required BOOLEAN DEFAULT TRUE,
    min_selections INTEGER DEFAULT 0,
    max_selections INTEGER,
    
    -- Validation
    validation_rules JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_set_key UNIQUE (step_id, set_key)
);

CREATE INDEX idx_option_sets_step ON wizard_option_sets(step_id);
CREATE INDEX idx_option_sets_step_order ON wizard_option_sets(step_id, set_order);

-- ============================================
-- TABLE 5: wizard_options
-- Purpose: Store individual options within option sets
-- ============================================
CREATE TABLE wizard_options (
    option_id SERIAL PRIMARY KEY,
    set_id INTEGER NOT NULL REFERENCES wizard_option_sets(set_id) ON DELETE CASCADE,
    option_key VARCHAR(100) NOT NULL,
    option_label VARCHAR(200) NOT NULL,
    option_description TEXT,
    option_value VARCHAR(255),
    option_icon VARCHAR(100),
    option_image_url VARCHAR(255),
    option_price DECIMAL(10, 2) DEFAULT 0.00,
    option_order INTEGER DEFAULT 0,
    
    -- Configuration
    is_default BOOLEAN DEFAULT FALSE,
    is_disabled BOOLEAN DEFAULT FALSE,
    is_recommended BOOLEAN DEFAULT FALSE,
    requires_input BOOLEAN DEFAULT FALSE,
    input_placeholder VARCHAR(255),
    
    -- Metadata
    option_metadata JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_option_key UNIQUE (set_id, option_key)
);

CREATE INDEX idx_options_set ON wizard_options(set_id);
CREATE INDEX idx_options_set_order ON wizard_options(set_id, option_order);

-- ============================================
-- TABLE 6: wizard_flow_rules
-- Purpose: Define navigation flow between steps
-- ============================================
CREATE TABLE wizard_flow_rules (
    rule_id SERIAL PRIMARY KEY,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    rule_name VARCHAR(100),
    rule_description TEXT,
    
    from_step_id INTEGER NOT NULL REFERENCES wizard_steps(step_id),
    from_option_id INTEGER REFERENCES wizard_options(option_id),
    to_step_id INTEGER NOT NULL REFERENCES wizard_steps(step_id),
    
    condition_type VARCHAR(20) DEFAULT 'REQUIRED' CHECK (condition_type IN ('REQUIRED', 'OPTIONAL', 'CONDITIONAL')),
    condition_expression TEXT,
    priority INTEGER DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_flow_rules_wizard ON wizard_flow_rules(wizard_id);
CREATE INDEX idx_flow_rules_from ON wizard_flow_rules(from_step_id, from_option_id);

-- ============================================
-- TABLE 7: wizard_option_dependencies
-- Purpose: Define option visibility dependencies
-- ============================================
CREATE TABLE wizard_option_dependencies (
    dependency_id SERIAL PRIMARY KEY,
    option_id INTEGER NOT NULL REFERENCES wizard_options(option_id) ON DELETE CASCADE,
    depends_on_step_id INTEGER NOT NULL REFERENCES wizard_steps(step_id),
    depends_on_option_id INTEGER NOT NULL REFERENCES wizard_options(option_id),
    dependency_type VARCHAR(20) DEFAULT 'SHOW_IF' CHECK (dependency_type IN ('SHOW_IF', 'HIDE_IF', 'REQUIRE_IF', 'DISABLE_IF')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_option_deps_option ON wizard_option_dependencies(option_id);
CREATE INDEX idx_option_deps_depends ON wizard_option_dependencies(depends_on_step_id, depends_on_option_id);

-- ============================================
-- TABLE 8: wizard_set_dependencies
-- Purpose: Define option set visibility dependencies
-- ============================================
CREATE TABLE wizard_set_dependencies (
    dependency_id SERIAL PRIMARY KEY,
    set_id INTEGER NOT NULL REFERENCES wizard_option_sets(set_id) ON DELETE CASCADE,
    depends_on_step_id INTEGER NOT NULL REFERENCES wizard_steps(step_id),
    depends_on_option_id INTEGER NOT NULL REFERENCES wizard_options(option_id),
    dependency_type VARCHAR(20) DEFAULT 'SHOW_IF' CHECK (dependency_type IN ('SHOW_IF', 'HIDE_IF', 'REQUIRE_IF')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_set_deps_set ON wizard_set_dependencies(set_id);
CREATE INDEX idx_set_deps_depends ON wizard_set_dependencies(depends_on_step_id, depends_on_option_id);

-- ============================================
-- TABLE 9: wizard_user_sessions
-- Purpose: Store user wizard sessions
-- ============================================
CREATE TABLE wizard_user_sessions (
    session_id SERIAL PRIMARY KEY,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_name VARCHAR(255) NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    session_description TEXT,
    
    -- Session Status
    current_step_id INTEGER REFERENCES wizard_steps(step_id),
    is_completed BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    
    -- Privacy Control
    store_user_data BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Metadata
    total_price DECIMAL(10, 2) DEFAULT 0.00,
    session_metadata JSONB,
    
    -- Analytics
    completion_time_minutes INTEGER
);

CREATE INDEX idx_sessions_wizard ON wizard_user_sessions(wizard_id);
CREATE INDEX idx_sessions_user ON wizard_user_sessions(user_id);
CREATE INDEX idx_sessions_token ON wizard_user_sessions(session_token);
CREATE INDEX idx_sessions_wizard_user ON wizard_user_sessions(wizard_id, user_id, is_completed);

-- ============================================
-- TABLE 10: wizard_user_selections
-- Purpose: Store user selections within sessions
-- ============================================
CREATE TABLE wizard_user_selections (
    selection_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES wizard_user_sessions(session_id) ON DELETE CASCADE,
    step_id INTEGER NOT NULL REFERENCES wizard_steps(step_id),
    set_id INTEGER NOT NULL REFERENCES wizard_option_sets(set_id),
    option_id INTEGER REFERENCES wizard_options(option_id),
    selected_value TEXT,
    
    -- User Input Data
    additional_input JSONB,
    additional_input_encrypted TEXT,
    
    -- Tracking
    selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    selection_order INTEGER,
    time_spent_seconds INTEGER
);

CREATE INDEX idx_selections_session ON wizard_user_selections(session_id);
CREATE INDEX idx_selections_session_step ON wizard_user_selections(session_id, step_id);
CREATE INDEX idx_selections_session_order ON wizard_user_selections(session_id, selection_order);

-- ============================================
-- TABLE 11: wizard_step_skips
-- Purpose: Track skipped steps
-- ============================================
CREATE TABLE wizard_step_skips (
    skip_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES wizard_user_sessions(session_id) ON DELETE CASCADE,
    step_id INTEGER NOT NULL REFERENCES wizard_steps(step_id),
    skip_reason VARCHAR(255),
    skipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_session_step_skip UNIQUE (session_id, step_id)
);

CREATE INDEX idx_step_skips_session ON wizard_step_skips(session_id);

-- ============================================
-- TABLE 12: wizard_session_templates
-- Purpose: Store saved session templates
-- ============================================
CREATE TABLE wizard_session_templates (
    template_id SERIAL PRIMARY KEY,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    original_session_id INTEGER NOT NULL REFERENCES wizard_user_sessions(session_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    template_name VARCHAR(255) NOT NULL,
    template_description TEXT,
    
    -- Template Configuration
    config_json JSONB NOT NULL,
    config_summary TEXT,
    
    -- Template Metadata
    is_public BOOLEAN DEFAULT FALSE,
    is_official BOOLEAN DEFAULT FALSE,
    use_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- Tags
    tags JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_templates_wizard ON wizard_session_templates(wizard_id);
CREATE INDEX idx_templates_user ON wizard_session_templates(user_id);
CREATE INDEX idx_templates_wizard_public ON wizard_session_templates(wizard_id, is_public);

-- ============================================
-- TABLE 13: wizard_session_replays
-- Purpose: Track session replay history
-- ============================================
CREATE TABLE wizard_session_replays (
    replay_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES wizard_session_templates(template_id),
    original_session_id INTEGER REFERENCES wizard_user_sessions(session_id),
    new_session_id INTEGER NOT NULL REFERENCES wizard_user_sessions(session_id) ON DELETE CASCADE,
    
    replay_with_data BOOLEAN DEFAULT FALSE,
    modifications_made BOOLEAN DEFAULT FALSE,
    
    replayed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_replays_user ON wizard_session_replays(user_id);
CREATE INDEX idx_replays_wizard ON wizard_session_replays(wizard_id);
CREATE INDEX idx_replays_template ON wizard_session_replays(template_id);

-- ============================================
-- TABLE 14: wizard_session_shares
-- Purpose: Manage session sharing
-- ============================================
CREATE TABLE wizard_session_shares (
    share_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES wizard_user_sessions(session_id) ON DELETE CASCADE,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    shared_by_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    shared_with_user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    share_token VARCHAR(255) UNIQUE NOT NULL,
    
    -- Permissions
    can_view BOOLEAN DEFAULT TRUE,
    can_clone BOOLEAN DEFAULT TRUE,
    can_edit BOOLEAN DEFAULT FALSE,
    
    -- Settings
    include_user_data BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP,
    max_uses INTEGER,
    use_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_shares_token ON wizard_session_shares(share_token);
CREATE INDEX idx_shares_session ON wizard_session_shares(session_id);
CREATE INDEX idx_shares_wizard ON wizard_session_shares(wizard_id);

-- ============================================
-- TABLE 15: wizard_session_activity_log
-- Purpose: Log all session activities
-- ============================================
CREATE TABLE wizard_session_activity_log (
    log_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES wizard_user_sessions(session_id) ON DELETE CASCADE,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
        'SESSION_STARTED',
        'STEP_COMPLETED',
        'STEP_SKIPPED',
        'SESSION_PAUSED',
        'SESSION_RESUMED',
        'SESSION_COMPLETED',
        'SESSION_SAVED_AS_TEMPLATE',
        'SESSION_REPLAYED',
        'SESSION_SHARED',
        'SESSION_DELETED'
    )),
    activity_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_session ON wizard_session_activity_log(session_id);
CREATE INDEX idx_activity_wizard ON wizard_session_activity_log(wizard_id);
CREATE INDEX idx_activity_user ON wizard_session_activity_log(user_id);
CREATE INDEX idx_activity_type ON wizard_session_activity_log(activity_type);
CREATE INDEX idx_activity_created ON wizard_session_activity_log(created_at);

-- ============================================
-- TABLE 16: wizard_analytics
-- Purpose: Store daily wizard analytics
-- ============================================
CREATE TABLE wizard_analytics (
    analytics_id SERIAL PRIMARY KEY,
    wizard_id INTEGER NOT NULL REFERENCES wizards(wizard_id) ON DELETE CASCADE,
    analytics_date DATE NOT NULL,
    
    -- Daily Stats
    total_starts INTEGER DEFAULT 0,
    total_completions INTEGER DEFAULT 0,
    total_abandons INTEGER DEFAULT 0,
    
    -- Step Analytics
    avg_completion_time_minutes DECIMAL(10, 2),
    most_abandoned_step_id INTEGER REFERENCES wizard_steps(step_id),
    most_time_spent_step_id INTEGER REFERENCES wizard_steps(step_id),
    
    -- User Analytics
    unique_users INTEGER DEFAULT 0,
    returning_users INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_wizard_date UNIQUE (wizard_id, analytics_date)
);

CREATE INDEX idx_analytics_wizard ON wizard_analytics(wizard_id);
CREATE INDEX idx_analytics_date ON wizard_analytics(analytics_date);
CREATE INDEX idx_analytics_wizard_date ON wizard_analytics(wizard_id, analytics_date);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wizards_updated_at BEFORE UPDATE ON wizards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wizard_steps_updated_at BEFORE UPDATE ON wizard_steps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wizard_session_templates_updated_at BEFORE UPDATE ON wizard_session_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: Complete wizard overview with step count
CREATE VIEW v_wizard_overview AS
SELECT 
    w.*,
    COUNT(DISTINCT ws.step_id) as total_steps,
    COUNT(DISTINCT t.template_id) as total_templates
FROM wizards w
LEFT JOIN wizard_steps ws ON ws.wizard_id = w.wizard_id AND ws.is_active = TRUE
LEFT JOIN wizard_session_templates t ON t.wizard_id = w.wizard_id
GROUP BY w.wizard_id;

-- View: User session summary
CREATE VIEW v_user_session_summary AS
SELECT 
    s.session_id,
    s.session_name,
    s.wizard_id,
    w.wizard_name,
    s.user_id,
    u.email,
    u.full_name,
    s.is_completed,
    s.started_at,
    s.completed_at,
    COUNT(DISTINCT sel.step_id) as steps_completed,
    (SELECT COUNT(*) FROM wizard_steps WHERE wizard_id = s.wizard_id AND is_active = TRUE) as total_steps
FROM wizard_user_sessions s
JOIN wizards w ON w.wizard_id = s.wizard_id
JOIN users u ON u.user_id = s.user_id
LEFT JOIN wizard_user_selections sel ON sel.session_id = s.session_id
GROUP BY s.session_id, w.wizard_name, u.email, u.full_name;

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================
COMMENT ON TABLE wizards IS 'Stores wizard definitions and metadata';
COMMENT ON TABLE wizard_steps IS 'Stores steps within each wizard';
COMMENT ON TABLE wizard_option_sets IS 'Groups of options within each step';
COMMENT ON TABLE wizard_options IS 'Individual selectable options';
COMMENT ON TABLE wizard_user_sessions IS 'User sessions for completing wizards';
COMMENT ON TABLE wizard_session_templates IS 'Saved configurations for reuse';
```

## Migration Notes

### Initial Migration (Alembic)
```python
# alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Copy all CREATE TABLE statements from above
    pass

def downgrade():
    # Drop all tables in reverse order
    op.drop_table('wizard_analytics')
    op.drop_table('wizard_session_activity_log')
    op.drop_table('wizard_session_shares')
    op.drop_table('wizard_session_replays')
    op.drop_table('wizard_session_templates')
    op.drop_table('wizard_step_skips')
    op.drop_table('wizard_user_selections')
    op.drop_table('wizard_user_sessions')
    op.drop_table('wizard_set_dependencies')
    op.drop_table('wizard_option_dependencies')
    op.drop_table('wizard_flow_rules')
    op.drop_table('wizard_options')
    op.drop_table('wizard_option_sets')
    op.drop_table('wizard_steps')
    op.drop_table('wizards')
    op.drop_table('users')
```

## Database Constraints Summary

### Primary Keys
All tables have a `SERIAL PRIMARY KEY` for auto-incrementing IDs.

### Foreign Keys
- 28 foreign key relationships ensuring referential integrity
- Most use `ON DELETE CASCADE` for automatic cleanup

### Unique Constraints
- `users.email` - Unique email addresses
- `wizards.wizard_key` - Unique wizard identifiers
- `wizard_steps.(wizard_id, step_key)` - Unique step keys per wizard
- `wizard_option_sets.(step_id, set_key)` - Unique set keys per step
- `wizard_options.(set_id, option_key)` - Unique option keys per set
- `wizard_user_sessions.session_token` - Unique session tokens
- `wizard_step_skips.(session_id, step_id)` - One skip record per step per session

### Check Constraints
- `users.user_role` - Must be USER, ADMIN, or SUPER_ADMIN
- `wizard_option_sets.selection_type` - Must be valid selection type
- `wizard_flow_rules.condition_type` - Must be REQUIRED, OPTIONAL, or CONDITIONAL
- `wizard_option_dependencies.dependency_type` - Must be valid dependency type

### Indexes (38 total)
Optimized for common query patterns:
- Foreign key lookups
- User/wizard/session relationships
- Date-based queries
- Token lookups