# Sample Data for Testing

## Overview

This file contains comprehensive sample data to populate the database for testing and development purposes.

## SQL Insert Statements
```sql
-- ============================================
-- SAMPLE DATA: Users
-- ============================================
INSERT INTO users (user_id, email, full_name, password_hash, user_role) VALUES
(1, 'admin@wizardplatform.com', 'Admin User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU8W.gxkKYOm', 'SUPER_ADMIN'),
(2, 'john.doe@company.com', 'John Doe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU8W.gxkKYOm', 'USER'),
(3, 'jane.smith@company.com', 'Jane Smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU8W.gxkKYOm', 'USER'),
(4, 'wizard.admin@company.com', 'Wizard Admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU8W.gxkKYOm', 'ADMIN');
-- Note: All passwords are 'password123' hashed with bcrypt

SELECT setval('users_user_id_seq', 4, true);

-- ============================================
-- SAMPLE DATA: Wizards
-- ============================================
INSERT INTO wizards (
    wizard_id, wizard_key, wizard_name, wizard_description, wizard_category,
    wizard_icon, wizard_color, allow_save_progress, allow_templates, 
    max_steps, estimated_time_minutes, is_active, is_public, is_featured, created_by
) VALUES
(1, 'software-license-config', 
 'Software License Configuration', 
 'Configure your software license, subscription plan, and deployment options for your organization',
 'Configuration',
 'key', '#3498db', TRUE, TRUE, 5, 10, TRUE, TRUE, TRUE, 1),

(2, 'cloud-deployment-setup',
 'Cloud Deployment Setup',
 'Set up your cloud infrastructure with automated provisioning and configuration',
 'Deployment',
 'cloud', '#2ecc71', TRUE, TRUE, 7, 15, TRUE, TRUE, FALSE, 1),

(3, 'user-onboarding-flow',
 'New User Onboarding',
 'Complete your user profile, preferences, and initial setup',
 'Onboarding',
 'user-plus', '#9b59b6', TRUE, FALSE, 4, 8, TRUE, TRUE, TRUE, 1),

(4, 'team-provisioning',
 'Team Resource Provisioning',
 'Provision resources, access permissions, and tools for your team members',
 'Administration',
 'users', '#e74c3c', TRUE, TRUE, 6, 12, TRUE, FALSE, FALSE, 1);

SELECT setval('wizards_wizard_id_seq', 4, true);

-- ============================================
-- WIZARD 1: Software License Configuration - Steps
-- ============================================
INSERT INTO wizard_steps (
    step_id, wizard_id, step_key, step_name, step_order, step_title, 
    step_description, step_help_text, is_required, allow_back_navigation
) VALUES
(101, 1, 'license_type', 'License Type', 1, 'Choose Your License Type', 
 'Select the type of license that best suits your organization needs',
 'Choose between Personal, Business, or Enterprise licenses. This determines available features and pricing.',
 TRUE, FALSE),

(102, 1, 'plan_configuration', 'Plan Configuration', 2, 'Configure Your Plan', 
 'Select your subscription plan and deployment region',
 'Choose the plan tier and the region where your services will be deployed.',
 TRUE, TRUE),

(103, 1, 'additional_features', 'Additional Features', 3, 'Add Optional Features', 
 'Select additional features and add-ons for your subscription',
 'These optional features can enhance your experience. You can add or remove them later.',
 FALSE, TRUE),

(104, 1, 'customization', 'Customization', 4, 'Customize Your Experience', 
 'Configure appearance, branding, and user interface preferences',
 'Personalize the look and feel of your platform.',
 FALSE, TRUE),

(105, 1, 'deployment_info', 'Deployment Information', 5, 'Deployment Details', 
 'Provide information about your deployment environment',
 'We need some basic information to complete your setup.',
 TRUE, TRUE);

-- ============================================
-- WIZARD 1, STEP 1: License Type Options
-- ============================================
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1001, 101, 'license_type', 'License Type Selection', 'Select Your License Type',
 'Choose the license type that matches your organization size and needs',
 'SINGLE', TRUE, 1, 1, 1);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, 
    option_price, option_order, option_icon
) VALUES
(10001, 1001, 'personal', 'Personal License', 
 'Perfect for individual developers and freelancers. Includes basic features for personal projects.',
 0.00, 1, 'user'),

(10002, 1001, 'business', 'Business License', 
 'Ideal for small to medium teams. Includes collaboration tools and priority support.',
 0.00, 2, 'briefcase'),

(10003, 1001, 'enterprise', 'Enterprise License', 
 'For large organizations requiring advanced security, compliance, and dedicated support.',
 0.00, 3, 'building');

-- ============================================
-- WIZARD 1, STEP 2: Plan Configuration (Multiple Sets)
-- ============================================

-- Set 1: Plan Selection
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1002, 102, 'plan_tier', 'Plan Tier', 'Choose Your Plan',
 'Select the plan tier based on your needs',
 'SINGLE', TRUE, 1, 1, 1);

-- Personal Plans
INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, 
    option_price, option_order
) VALUES
(10101, 1002, 'personal_basic', 'Basic Plan', 
 '1 user, 5GB storage, basic features - Perfect for getting started',
 9.00, 1),

(10102, 1002, 'personal_pro', 'Pro Plan', 
 '1 user, 50GB storage, advanced features, API access',
 29.00, 2);

-- Business Plans
INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, 
    option_price, option_order
) VALUES
(10103, 1002, 'business_team', 'Team Plan', 
 'Up to 10 users, 100GB storage, team collaboration tools',
 99.00, 3),

(10104, 1002, 'business_corporate', 'Corporate Plan', 
 'Up to 50 users, 500GB storage, advanced security, SSO',
 299.00, 4);

-- Enterprise Plans
INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, 
    option_price, option_order, is_recommended
) VALUES
(10105, 1002, 'enterprise_custom', 'Enterprise Plan', 
 'Unlimited users, unlimited storage, dedicated support, custom SLA',
 999.00, 5, TRUE);

-- Set 2: Region Selection
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1003, 102, 'deployment_region', 'Region', 'Select Deployment Region',
 'Choose the geographic region for your deployment',
 'SINGLE', TRUE, 1, 1, 2);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, option_order
) VALUES
(10201, 1003, 'us_east', 'US East (Virginia)', 'North America - East Coast', 1),
(10202, 1003, 'us_west', 'US West (Oregon)', 'North America - West Coast', 2),
(10203, 1003, 'eu_central', 'EU Central (Frankfurt)', 'Europe - Germany', 3),
(10204, 1003, 'asia_pacific', 'Asia Pacific (Singapore)', 'Southeast Asia', 4),
(10205, 1003, 'uk', 'UK (London)', 'United Kingdom', 5);

-- Set 3: Billing Cycle (Optional)
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1004, 102, 'billing_cycle', 'Billing Cycle', 'Choose Billing Frequency',
 'Select how often you want to be billed',
 'SINGLE', FALSE, 0, 1, 3);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, 
    option_price, option_order, is_default
) VALUES
(10301, 1004, 'monthly', 'Monthly Billing', 
 'Pay monthly with flexible cancellation',
 0.00, 1, TRUE),

(10302, 1004, 'annual', 'Annual Billing', 
 'Pay annually and save 15% - Best value!',
 -0.15, 2, FALSE),

(10303, 1004, 'biennial', 'Biennial Billing', 
 'Pay every 2 years and save 20%',
 -0.20, 3, FALSE);

-- ============================================
-- WIZARD 1, STEP 3: Additional Features (Multiple Selection)
-- ============================================
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1005, 103, 'addon_features', 'Add-on Features', 'Select Additional Features',
 'Choose optional features to enhance your subscription',
 'MULTIPLE', FALSE, 0, NULL, 1);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, 
    option_price, option_order
) VALUES
(10401, 1005, 'feature_api', 'API Access', 
 'RESTful API with 10,000 requests/month',
 20.00, 1),

(10402, 1005, 'feature_support', 'Priority Support', 
 '24/7 dedicated support with 1-hour response time',
 50.00, 2),

(10403, 1005, 'feature_analytics', 'Advanced Analytics', 
 'Detailed usage reports and business intelligence dashboard',
 30.00, 3),

(10404, 1005, 'feature_sso', 'Single Sign-On (SSO)', 
 'Enterprise SSO integration with SAML 2.0',
 40.00, 4),

(10405, 1005, 'feature_audit', 'Audit Logs', 
 'Complete audit trail with 2-year retention',
 25.00, 5),

(10406, 1005, 'feature_whitelabel', 'White Label', 
 'Custom branding and domain',
 100.00, 6);

-- ============================================
-- WIZARD 1, STEP 4: Customization Options
-- ============================================

-- Set 1: Theme
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1006, 104, 'ui_theme', 'Theme', 'Choose Your Theme',
 'SINGLE', TRUE, 1, 1, 1);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, option_order
) VALUES
(10501, 1006, 'theme_light', 'Light Theme', 'Clean and bright interface', 1),
(10502, 1006, 'theme_dark', 'Dark Theme', 'Easy on the eyes, perfect for night work', 2),
(10503, 1006, 'theme_auto', 'Auto Theme', 'Automatically matches your system preference', 3);

-- Set 2: Brand Colors (Multiple, Min: 2, Max: 3)
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1007, 104, 'brand_colors', 'Brand Colors', 'Select Your Brand Colors (2-3)',
 'Choose 2 to 3 colors for your brand identity',
 'MULTIPLE', FALSE, 2, 3, 2);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_value, option_order
) VALUES
(10601, 1007, 'color_blue', 'Blue', '#007bff', 1),
(10602, 1007, 'color_green', 'Green', '#28a745', 2),
(10603, 1007, 'color_red', 'Red', '#dc3545', 3),
(10604, 1007, 'color_purple', 'Purple', '#6f42c1', 4),
(10605, 1007, 'color_orange', 'Orange', '#fd7e14', 5),
(10606, 1007, 'color_teal', 'Teal', '#20c997', 6);

-- ============================================
-- WIZARD 1, STEP 5: Deployment Information
-- ============================================
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1008, 105, 'contact_info', 'Contact Information', 'Your Contact Details',
 'Provide your organization contact information',
 'TEXT_INPUT', TRUE, 1, 1, 1);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, requires_input, 
    input_placeholder, option_order
) VALUES
(10701, 1008, 'contact_form', 'Contact Details', TRUE,
 'Company Name, Email, Phone',
 1);

-- Set 2: Deployment Options
INSERT INTO wizard_option_sets (
    set_id, step_id, set_key, set_name, set_title, set_description,
    selection_type, is_required, min_selections, max_selections, set_order
) VALUES
(1009, 105, 'deployment_type', 'Deployment Type', 'Select Deployment Method (1-2)',
 'Choose how you want to deploy your solution',
 'MULTIPLE', TRUE, 1, 2, 2);

INSERT INTO wizard_options (
    option_id, set_id, option_key, option_label, option_description, option_order
) VALUES
(10801, 1009, 'deploy_cloud', 'Cloud Deployment', 
 'We host and manage everything for you', 1),

(10802, 1009, 'deploy_onprem', 'On-Premise', 
 'Deploy on your own servers and infrastructure', 2),

(10803, 1009, 'deploy_hybrid', 'Hybrid Setup', 
 'Combination of cloud and on-premise deployment', 3);

-- ============================================
-- OPTION DEPENDENCIES (Show/Hide Logic)
-- ============================================

-- Personal Plans only show when Personal License selected
INSERT INTO wizard_option_dependencies (
    option_id, depends_on_step_id, depends_on_option_id, dependency_type
) VALUES
(10101, 101, 10001, 'SHOW_IF'), -- Basic shows if Personal
(10102, 101, 10001, 'SHOW_IF'); -- Pro shows if Personal

-- Business Plans only show when Business License selected
INSERT INTO wizard_option_dependencies (
    option_id, depends_on_step_id, depends_on_option_id, dependency_type
) VALUES
(10103, 101, 10002, 'SHOW_IF'), -- Team shows if Business
(10104, 101, 10002, 'SHOW_IF'); -- Corporate shows if Business

-- Enterprise Plan only shows when Enterprise License selected
INSERT INTO wizard_option_dependencies (
    option_id, depends_on_step_id, depends_on_option_id, dependency_type
) VALUES
(10105, 101, 10003, 'SHOW_IF'); -- Enterprise Plan shows if Enterprise License

-- SSO only for Business and Enterprise
INSERT INTO wizard_option_dependencies (
    option_id, depends_on_step_id, depends_on_option_id, dependency_type
) VALUES
(10404, 101, 10002, 'SHOW_IF'), -- SSO shows for Business
(10404, 101, 10003, 'SHOW_IF'); -- SSO shows for Enterprise

-- Audit Logs only for Business and Enterprise
INSERT INTO wizard_option_dependencies (
    option_id, depends_on_step_id, depends_on_option_id, dependency_type
) VALUES
(10405, 101, 10002, 'SHOW_IF'), -- Audit shows for Business
(10405, 101, 10003, 'SHOW_IF'); -- Audit shows for Enterprise

-- White Label only for Enterprise
INSERT INTO wizard_option_dependencies (
    option_id, depends_on_step_id, depends_on_option_id, dependency_type
) VALUES
(10406, 101, 10003, 'SHOW_IF'); -- White Label only for Enterprise

-- ============================================
-- FLOW RULES (Step Navigation)
-- ============================================
INSERT INTO wizard_flow_rules (
    wizard_id, from_step_id, from_option_id, to_step_id, condition_type, priority
) VALUES
-- Step 1 → Step 2 (for all license types)
(1, 101, 10001, 102, 'REQUIRED', 1),
(1, 101, 10002, 102, 'REQUIRED', 1),
(1, 101, 10003, 102, 'REQUIRED', 1),

-- Step 2 → Step 3 (optional)
(1, 102, NULL, 103, 'OPTIONAL', 1),

-- Step 3 → Step 4 (optional)
(1, 103, NULL, 104, 'OPTIONAL', 1),

-- Step 4 → Step 5 (required)
(1, 104, NULL, 105, 'REQUIRED', 1);

-- ============================================
-- SAMPLE USER SESSIONS
-- ============================================

-- User 2: Completed Session
INSERT INTO wizard_user_sessions (
    session_id, wizard_id, user_id, session_name, session_token, session_description,
    current_step_id, is_completed, store_user_data, total_price, 
    started_at, completed_at, completion_time_minutes
) VALUES
(1001, 1, 2, 'Production Deployment - Q4 2024', 'tok_prod_q4_abc123xyz',
 'Main production environment setup for Q4 business goals',
 105, TRUE, TRUE, 409.00,
 '2024-11-01 09:00:00', '2024-11-01 09:12:00', 12);

-- User 2's Completed Session - Selections
INSERT INTO wizard_user_selections (
    session_id, step_id, set_id, option_id, selected_value, 
    selection_order, time_spent_seconds
) VALUES
-- Step 1: Business License
(1001, 101, 1001, 10002, 'business', 1, 45),

-- Step 2: Corporate Plan
(1001, 102, 1002, 10104, 'business_corporate', 2, 120),

-- Step 2: US East Region
(1001, 102, 1003, 10201, 'us_east', 3, 30),

-- Step 2: Annual Billing
(1001, 102, 1004, 10302, 'annual', 4, 25),

-- Step 3: API Access
(1001, 103, 1005, 10401, 'feature_api', 5, 60),

-- Step 3: Priority Support
(1001, 103, 1005, 10402, 'feature_support', 6, 40),

-- Step 3: SSO
(1001, 103, 1005, 10404, 'feature_sso', 7, 50),

-- Step 4: Dark Theme
(1001, 104, 1006, 10502, 'theme_dark', 8, 20),

-- Step 5: Contact Info
(1001, 105, 1008, 10701, 'contact_form', 9, 180),

-- Step 5: Cloud Deployment
(1001, 105, 1009, 10801, 'deploy_cloud', 10, 35);

-- Store additional input for contact form
UPDATE wizard_user_selections 
SET additional_input = '{
    "company_name": "Acme Corporation",
    "email": "admin@acme.com",
    "phone": "+1-555-0100",
    "user_count": 35
}'::jsonb
WHERE session_id = 1001 AND option_id = 10701;

-- User 2: In-Progress Session
INSERT INTO wizard_user_sessions (
    session_id, wizard_id, user_id, session_name, session_token, session_description,
    current_step_id, is_completed, store_user_data, started_at
) VALUES
(1002, 1, 2, 'Development Environment Setup', 'tok_dev_setup_456def',
 'Setting up development environment for testing',
 102, FALSE, FALSE, '2024-11-15 14:30:00');

-- User 2's In-Progress Session - Partial Selections
INSERT INTO wizard_user_selections (
    session_id, step_id, set_id, option_id, selected_value, 
    selection_order, time_spent_seconds
) VALUES
(1002, 101, 1001, 10001, 'personal', 1, 30);

-- User 3: Completed Session
INSERT INTO wizard_user_sessions (
    session_id, wizard_id, user_id, session_name, session_token,
    current_step_id, is_completed, store_user_data, total_price,
    started_at, completed_at, completion_time_minutes
) VALUES
(1003, 1, 3, 'Small Team Setup', 'tok_team_789ghi',
 105, TRUE, TRUE, 149.00,
 '2024-11-10 10:00:00', '2024-11-10 10:08:00', 8);

-- User 3's selections (Team plan, fewer features)
INSERT INTO wizard_user_selections (
    session_id, step_id, set_id, option_id, selected_value, selection_order
) VALUES
(1003, 101, 1001, 10002, 'business', 1),
(1003, 102, 1002, 10103, 'business_team', 2),
(1003, 102, 1003, 10202, 'us_west', 3),
(1003, 102, 1004, 10301, 'monthly', 4),
(1003, 103, 1005, 10401, 'feature_api', 5);

-- Skip Step 4 (Customization)
INSERT INTO wizard_step_skips (session_id, step_id, skip_reason) VALUES
(1003, 104, 'Using default theme and colors');

-- ============================================
-- SESSION TEMPLATE
-- ============================================
INSERT INTO wizard_session_templates (
    template_id, wizard_id, original_session_id, user_id,
    template_name, template_description, config_json, config_summary,
    is_public, use_count
) VALUES
(5001, 1, 1001, 2,
 'Standard Production Configuration',
 'Our recommended production setup with business license, corporate plan, and essential features',
 '{
    "license_type": "business",
    "plan": "business_corporate",
    "region": "us_east",
    "billing": "annual",
    "features": ["api", "support", "sso"],
    "theme": "dark",
    "deployment": "cloud",
    "total_price": 409.00
 }'::jsonb,
 'Business → Corporate ($299) → Annual → API + Support + SSO',
 FALSE, 2);

-- ============================================
-- ACTIVITY LOG
-- ============================================
INSERT INTO wizard_session_activity_log (
    session_id, wizard_id, user_id, activity_type, activity_details
) VALUES
(1001, 1, 2, 'SESSION_STARTED', '{"session_name": "Production Deployment - Q4 2024"}'::jsonb),
(1001, 1, 2, 'STEP_COMPLETED', '{"step_name": "License Type", "selection": "Business"}'::jsonb),
(1001, 1, 2, 'STEP_COMPLETED', '{"step_name": "Plan Configuration", "plan": "Corporate"}'::jsonb),
(1001, 1, 2, 'STEP_COMPLETED', '{"step_name": "Additional Features", "count": 3}'::jsonb),
(1001, 1, 2, 'STEP_COMPLETED', '{"step_name": "Customization", "theme": "Dark"}'::jsonb),
(1001, 1, 2, 'STEP_COMPLETED', '{"step_name": "Deployment Info"}'::jsonb),
(1001, 1, 2, 'SESSION_COMPLETED', '{"total_price": 409.00, "completion_time": 12}'::jsonb),
(1001, 1, 2, 'SESSION_SAVED_AS_TEMPLATE', '{"template_id": 5001, "template_name": "Standard Production Configuration"}'::jsonb);

-- ============================================
-- Reset Sequences
-- ============================================
SELECT setval('wizard_steps_step_id_seq', 200, true);
SELECT setval('wizard_option_sets_set_id_seq', 2000, true);
SELECT setval('wizard_options_option_id_seq', 20000, true);
SELECT setval('wizard_user_sessions_session_id_seq', 2000, true);
SELECT setval('wizard_user_selections_selection_id_seq', 10000, true);
SELECT setval('wizard_session_templates_template_id_seq', 6000, true);
```

## Test Data Summary

### Users (4)
- 1 Super Admin
- 1 Regular Admin
- 2 Regular Users

### Wizards (1 fully configured)
- Software License Configuration (5 steps, 37 options across 9 option sets)

### User Sessions (3)
- 1 completed session by John Doe (Business → Corporate with full selections)
- 1 in-progress session by John Doe
- 1 completed session by Jane Smith (Business → Team with partial features)

### Templates (1)
- "Standard Production Configuration" created from John's completed session

### Activity Logs (8)
- Complete journey tracking for John's first session

## Quick Test Queries
```sql
-- Verify wizard structure
SELECT 
    w.wizard_name,
    COUNT(DISTINCT ws.step_id) as total_steps,
    COUNT(DISTINCT wos.set_id) as total_sets,
    COUNT(DISTINCT wo.option_id) as total_options
FROM wizards w
LEFT JOIN wizard_steps ws ON ws.wizard_id = w.wizard_id
LEFT JOIN wizard_option_sets wos ON wos.step_id = ws.step_id
LEFT JOIN wizard_options wo ON wo.set_id = wos.set_id
WHERE w.wizard_id = 1
GROUP BY w.wizard_id, w.wizard_name;

-- View user sessions
SELECT 
    u.full_name,
    w.wizard_name,
    s.session_name,
    s.is_completed,
    COUNT(sel.selection_id) as selections_made
FROM wizard_user_sessions s
JOIN users u ON u.user_id = s.user_id
JOIN wizards w ON w.wizard_id = s.wizard_id
LEFT JOIN wizard_user_selections sel ON sel.session_id = s.session_id
GROUP BY u.full_name, w.wizard_name, s.session_name, s.is_completed;

-- Get complete session journey
SELECT 
    ws.step_order,
    ws.step_title,
    wos.set_title,
    wo.option_label,
    wo.option_price,
    sel.selected_at
FROM wizard_user_selections sel
JOIN wizard_steps ws ON ws.step_id = sel.step_id
JOIN wizard_option_sets wos ON wos.set_id = sel.set_id
JOIN wizard_options wo ON wo.option_id = sel.option_id
WHERE sel.session_id = 1001
ORDER BY sel.selection_order;
```