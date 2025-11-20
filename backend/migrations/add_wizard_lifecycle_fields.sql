-- Migration: Add Wizard Lifecycle Protection Fields
-- Purpose: Enable three-state protection strategy (draft, in_use, published)
-- Created: 2025-11-20

BEGIN;

-- Add lifecycle fields to wizards table
ALTER TABLE wizards
ADD COLUMN IF NOT EXISTS lifecycle_state VARCHAR(20) DEFAULT 'draft'
    CHECK (lifecycle_state IN ('draft', 'in_use', 'published')),
ADD COLUMN IF NOT EXISTS first_run_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS first_stored_run_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS parent_wizard_id UUID REFERENCES wizards(id) ON DELETE SET NULL;

-- Add comment explaining lifecycle_state values
COMMENT ON COLUMN wizards.lifecycle_state IS
'Draft: Never run, full editing allowed | In-Use: Has runs but none stored, edits allowed with warning | Published: Has stored runs, read-only';

-- Add index for lifecycle queries
CREATE INDEX IF NOT EXISTS idx_wizards_lifecycle_state ON wizards(lifecycle_state);
CREATE INDEX IF NOT EXISTS idx_wizards_first_run_at ON wizards(first_run_at);
CREATE INDEX IF NOT EXISTS idx_wizards_first_stored_run_at ON wizards(first_stored_run_at);
CREATE INDEX IF NOT EXISTS idx_wizards_parent_wizard_id ON wizards(parent_wizard_id);
CREATE INDEX IF NOT EXISTS idx_wizards_is_archived ON wizards(is_archived) WHERE is_archived = TRUE;

-- Update existing wizards based on their current run status
-- Set lifecycle_state to 'published' for wizards with stored runs
UPDATE wizards w
SET lifecycle_state = 'published',
    first_stored_run_at = (
        SELECT MIN(completed_at)
        FROM wizard_runs wr
        WHERE wr.wizard_id = w.id
        AND wr.is_stored = TRUE
    )
WHERE EXISTS (
    SELECT 1
    FROM wizard_runs wr
    WHERE wr.wizard_id = w.id
    AND wr.is_stored = TRUE
);

-- Set lifecycle_state to 'in_use' for wizards with runs but no stored runs
UPDATE wizards w
SET lifecycle_state = 'in_use',
    first_run_at = (
        SELECT MIN(started_at)
        FROM wizard_runs wr
        WHERE wr.wizard_id = w.id
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM wizard_runs wr
    WHERE wr.wizard_id = w.id
    AND wr.is_stored = TRUE
)
AND EXISTS (
    SELECT 1
    FROM wizard_runs wr
    WHERE wr.wizard_id = w.id
);

-- Wizards with no runs remain in 'draft' state (already set by DEFAULT)

COMMIT;

-- Rollback script (save for reference)
-- BEGIN;
-- ALTER TABLE wizards
-- DROP COLUMN IF EXISTS lifecycle_state,
-- DROP COLUMN IF EXISTS first_run_at,
-- DROP COLUMN IF EXISTS first_stored_run_at,
-- DROP COLUMN IF EXISTS is_archived,
-- DROP COLUMN IF EXISTS archived_at,
-- DROP COLUMN IF EXISTS version_number,
-- DROP COLUMN IF EXISTS parent_wizard_id;
--
-- DROP INDEX IF EXISTS idx_wizards_lifecycle_state;
-- DROP INDEX IF EXISTS idx_wizards_first_run_at;
-- DROP INDEX IF EXISTS idx_wizards_first_stored_run_at;
-- DROP INDEX IF EXISTS idx_wizards_parent_wizard_id;
-- DROP INDEX IF EXISTS idx_wizards_is_archived;
-- COMMIT;
