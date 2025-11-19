-- Migration: Drop Session and Template Tables
-- Date: 2025-11-19
-- Description: Remove all session and template functionality from the database

-- Drop tables in correct order (child tables first due to foreign key constraints)

-- Drop template response table
DROP TABLE IF EXISTS template_responses CASCADE;

-- Drop templates table
DROP TABLE IF EXISTS templates CASCADE;

-- Drop session responses table
DROP TABLE IF EXISTS session_responses CASCADE;

-- Drop user sessions table
DROP TABLE IF EXISTS user_sessions CASCADE;

-- Drop any related indexes (if they exist separately)
-- Note: CASCADE will handle indexes automatically, but listing for clarity

-- Remove any views or functions that depend on these tables
-- (Add specific DROP statements here if any views/functions exist)

COMMIT;
