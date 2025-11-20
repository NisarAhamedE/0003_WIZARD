# Wizard Lifecycle Protection Strategy

**Design Philosophy:** Progressive protection based on wizard usage state

**Date:** November 19, 2025
**Status:** ✅ RECOMMENDED IMPLEMENTATION
**Complexity:** Medium (2 weeks implementation)

---

## Table of Contents
1. [Three-State Protection Model](#three-state-protection-model)
2. [State Detection Logic](#state-detection-logic)
3. [Implementation Details](#implementation-details)
4. [Database Schema Changes](#database-schema-changes)
5. [Backend API Changes](#backend-api-changes)
6. [Frontend UI Changes](#frontend-ui-changes)
7. [User Experience Flows](#user-experience-flows)
8. [Migration Guide](#migration-guide)

---

## Three-State Protection Model

### State 1: Draft (Unused Wizard) ✅ FULL EDITING

**Condition:** Wizard has NEVER been run (no runs exist, ever)

**Allowed Actions:**
- ✅ Edit wizard name/description
- ✅ Add/remove/reorder steps
- ✅ Add/remove/modify option sets
- ✅ Change field types
- ✅ Modify validation rules
- ✅ Delete wizard entirely
- ✅ No warnings needed

**Protection Level:** 🟢 **NONE** (Safe to modify freely)

**Rationale:** No user data exists, no risk of data loss

---

### State 2: In-Use (Has Active Runs, No Stored Runs) ⚠️ WARN + CONFIRM

**Condition:** Wizard has in-progress or completed runs, but NONE are stored

**Allowed Actions:**
- ⚠️ Edit (with warning)
- ⚠️ Delete steps/fields (with warning + confirmation)
- ⚠️ Delete wizard (with warning + option to delete runs)

**Protection Level:** 🟡 **WARNING** (User must confirm)

**Warning Message:**
```
⚠️ WARNING: Active Wizard Runs Exist

This wizard has 12 active runs:
  • 8 in-progress runs
  • 4 completed (not stored) runs

Modifying this wizard will affect users currently filling it out.

Options:
  [Cancel] [Delete All Runs & Modify] [Create New Version Instead]
```

**Rationale:** Runs exist but aren't "saved" permanently, give user choice

---

### State 3: Published (Has Stored Runs) 🔴 READ-ONLY + VERSION OPTIONS

**Condition:** At least ONE run has been stored (is_stored = true)

**Allowed Actions:**
- ✅ View wizard (read-only mode)
- ✅ Clone wizard (creates independent copy)
- ✅ Create new version (versioning system)
- ❌ Edit in-place (BLOCKED)
- ❌ Delete wizard (BLOCKED - must archive instead)

**Protection Level:** 🔴 **LOCKED** (Immutable for data integrity)

**UI Behavior:**
```
🔒 This wizard cannot be edited because it has stored runs.

Your options:
  [View Details] [Clone Wizard] [Create New Version] [Archive]
```

**Rationale:** Stored runs represent permanent user submissions that must be preserved

---

## State Detection Logic

### Backend Service

**File:** `backend/app/services/wizard_protection.py` (NEW)

```python
"""
Wizard Protection Service
Determines wizard state and enforces protection rules.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, exists
from uuid import UUID
from enum import Enum

from app.models.wizard import Wizard
from app.models.wizard_run import WizardRun


class WizardState(str, Enum):
    """Wizard protection states"""
    DRAFT = "draft"           # Never run
    IN_USE = "in_use"         # Has runs, none stored
    PUBLISHED = "published"   # Has stored runs


class WizardProtectionService:
    """Service for wizard state detection and protection enforcement"""

    def get_wizard_state(self, db: Session, wizard_id: UUID) -> dict:
        """
        Determine wizard's current protection state.

        Returns:
        {
            "state": "draft" | "in_use" | "published",
            "runs_count": {
                "total": 15,
                "in_progress": 8,
                "completed": 5,
                "stored": 2,
                "abandoned": 0
            },
            "can_edit": True/False,
            "can_delete": True/False,
            "warning_message": "..." or None
        }
        """
        # Count runs by status
        runs_query = db.query(WizardRun).filter(WizardRun.wizard_id == wizard_id)

        total_runs = runs_query.count()
        in_progress = runs_query.filter(WizardRun.status == 'in_progress').count()
        completed = runs_query.filter(WizardRun.status == 'completed').count()
        stored = runs_query.filter(WizardRun.is_stored == True).count()
        abandoned = runs_query.filter(WizardRun.status == 'abandoned').count()

        # Determine state
        if total_runs == 0:
            state = WizardState.DRAFT
            can_edit = True
            can_delete = True
            warning_message = None

        elif stored > 0:
            state = WizardState.PUBLISHED
            can_edit = False
            can_delete = False
            warning_message = (
                f"This wizard has {stored} stored run(s) and cannot be modified. "
                f"You can clone it or create a new version instead."
            )

        else:
            state = WizardState.IN_USE
            can_edit = True  # With confirmation
            can_delete = True  # With confirmation
            warning_message = (
                f"This wizard has {total_runs} active run(s). "
                f"Modifying it may affect users currently using it."
            )

        return {
            "state": state,
            "runs_count": {
                "total": total_runs,
                "in_progress": in_progress,
                "completed": completed,
                "stored": stored,
                "abandoned": abandoned
            },
            "can_edit": can_edit,
            "can_delete": can_delete,
            "warning_message": warning_message
        }


    def enforce_protection(self, db: Session, wizard_id: UUID, action: str) -> tuple[bool, str]:
        """
        Check if action is allowed on wizard.

        Args:
            wizard_id: UUID of wizard
            action: "edit" | "delete" | "view"

        Returns:
            (allowed: bool, message: str)
        """
        state_info = self.get_wizard_state(db, wizard_id)
        state = state_info["state"]

        if action == "view":
            return (True, "")  # Always allowed

        if action == "edit":
            if state == WizardState.PUBLISHED:
                return (False, "Cannot edit wizard with stored runs. Clone or version it instead.")
            elif state == WizardState.IN_USE:
                return (True, state_info["warning_message"])  # Allowed with warning
            else:
                return (True, "")  # Draft - no restrictions

        if action == "delete":
            if state == WizardState.PUBLISHED:
                return (False, "Cannot delete wizard with stored runs. Archive it instead.")
            elif state == WizardState.IN_USE:
                return (True, state_info["warning_message"])  # Allowed with warning
            else:
                return (True, "")  # Draft - no restrictions

        return (False, "Unknown action")


# Singleton instance
wizard_protection_service = WizardProtectionService()
```

---

## Database Schema Changes

### 1. Add State Tracking to Wizards

```sql
-- Migration: Add wizard lifecycle fields
ALTER TABLE wizards
ADD COLUMN first_run_at TIMESTAMP,           -- When first run was created
ADD COLUMN first_stored_run_at TIMESTAMP,    -- When first run was stored
ADD COLUMN lifecycle_state VARCHAR(20) DEFAULT 'draft',  -- draft/in_use/published
ADD COLUMN is_archived BOOLEAN DEFAULT FALSE,            -- Soft delete alternative
ADD COLUMN archived_at TIMESTAMP;

-- Trigger to update first_run_at
CREATE OR REPLACE FUNCTION update_wizard_first_run()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.wizard_id IS NOT NULL THEN
        UPDATE wizards
        SET first_run_at = COALESCE(first_run_at, NEW.started_at)
        WHERE id = NEW.wizard_id AND first_run_at IS NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER wizard_run_created
AFTER INSERT ON wizard_runs
FOR EACH ROW
EXECUTE FUNCTION update_wizard_first_run();

-- Trigger to update first_stored_run_at and lifecycle_state
CREATE OR REPLACE FUNCTION update_wizard_lifecycle()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_stored = TRUE AND OLD.is_stored = FALSE THEN
        UPDATE wizards
        SET
            first_stored_run_at = COALESCE(first_stored_run_at, NOW()),
            lifecycle_state = 'published'
        WHERE id = NEW.wizard_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER wizard_run_stored
AFTER UPDATE ON wizard_runs
FOR EACH ROW
WHEN (NEW.is_stored = TRUE AND OLD.is_stored = FALSE)
EXECUTE FUNCTION update_wizard_lifecycle();

-- Index for quick state lookups
CREATE INDEX idx_wizards_lifecycle_state ON wizards(lifecycle_state);
CREATE INDEX idx_wizards_archived ON wizards(is_archived);
```

---

## Backend API Changes

### 1. Add Protection Endpoint

**File:** `backend/app/api/v1/wizards.py`

```python
from app.services.wizard_protection import wizard_protection_service

@router.get("/{wizard_id}/protection-status")
async def get_wizard_protection_status(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get wizard protection status and allowed actions.

    Returns detailed information about wizard state and restrictions.
    """
    # Verify user has access to this wizard
    wizard = crud_wizard.get(db, wizard_id=wizard_id)
    if not wizard:
        raise HTTPException(status_code=404, detail="Wizard not found")

    if wizard.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get protection state
    state_info = wizard_protection_service.get_wizard_state(db, wizard_id)

    return state_info
```

### 2. Protect Edit Endpoint

```python
@router.put("/{wizard_id}")
async def update_wizard(
    wizard_id: UUID,
    wizard_update: WizardUpdate,
    force: bool = False,  # Allow override with explicit confirmation
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update wizard with protection checks.

    Query param 'force=true' bypasses warnings (but not hard blocks).
    """
    # Check protection
    allowed, message = wizard_protection_service.enforce_protection(
        db, wizard_id, "edit"
    )

    if not allowed:
        # HARD BLOCK - Cannot edit published wizard
        raise HTTPException(
            status_code=403,
            detail={
                "error": "wizard_locked",
                "message": message,
                "alternatives": [
                    {"action": "clone", "label": "Clone Wizard"},
                    {"action": "version", "label": "Create New Version"}
                ]
            }
        )

    if message and not force:
        # SOFT WARNING - Needs confirmation
        raise HTTPException(
            status_code=409,  # Conflict
            detail={
                "error": "confirmation_required",
                "message": message,
                "hint": "Add ?force=true to proceed"
            }
        )

    # Proceed with update
    wizard = crud_wizard.update(db, db_obj=wizard, obj_in=wizard_update)
    return wizard
```

### 3. Add Clone Endpoint

```python
@router.post("/{wizard_id}/clone")
async def clone_wizard(
    wizard_id: UUID,
    new_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clone a wizard to create independent copy.

    Useful for:
    - Creating variants of published wizards
    - Starting new version from existing wizard
    - Experimenting without affecting original
    """
    # Get original wizard with full structure
    original = crud_wizard.get_with_structure(db, wizard_id=wizard_id)
    if not original:
        raise HTTPException(status_code=404, detail="Wizard not found")

    # Create deep copy
    clone_name = new_name or f"{original.name} (Copy)"

    cloned_wizard = Wizard(
        name=clone_name,
        description=f"Cloned from: {original.name}",
        category=original.category,
        difficulty=original.difficulty,
        estimated_time=original.estimated_time,
        created_by=current_user.id,
        is_published=False,  # Clones start as draft
        lifecycle_state='draft'
    )

    db.add(cloned_wizard)
    db.flush()  # Get ID

    # Clone all steps
    for step in original.steps:
        cloned_step = Step(
            wizard_id=cloned_wizard.id,
            name=step.name,
            description=step.description,
            step_order=step.step_order,
            is_required=step.is_required,
            is_skippable=step.is_skippable
        )
        db.add(cloned_step)
        db.flush()

        # Clone all option sets
        for option_set in step.option_sets:
            cloned_option_set = OptionSet(
                step_id=cloned_step.id,
                name=option_set.name,
                selection_type=option_set.selection_type,
                is_required=option_set.is_required,
                # ... copy all fields
            )
            db.add(cloned_option_set)
            db.flush()

            # Clone all options
            for option in option_set.options:
                cloned_option = Option(
                    option_set_id=cloned_option_set.id,
                    label=option.label,
                    value=option.value,
                    # ... copy all fields
                )
                db.add(cloned_option)

    db.commit()
    db.refresh(cloned_wizard)

    return {
        "cloned_wizard": cloned_wizard,
        "original_wizard_id": wizard_id,
        "message": "Wizard cloned successfully"
    }
```

### 4. Add Archive Endpoint

```python
@router.post("/{wizard_id}/archive")
async def archive_wizard(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Archive a wizard instead of deleting it.

    Archived wizards:
    - Hidden from wizard list
    - Cannot be run by users
    - Preserved for historical runs
    - Can be unarchived later
    """
    wizard = crud_wizard.get(db, wizard_id=wizard_id)
    if not wizard:
        raise HTTPException(status_code=404, detail="Wizard not found")

    if wizard.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Archive instead of delete
    wizard.is_archived = True
    wizard.archived_at = datetime.now(timezone.utc)
    wizard.is_published = False  # Unpublish

    db.commit()

    return {
        "wizard_id": wizard_id,
        "status": "archived",
        "message": "Wizard archived successfully. Historical runs are preserved."
    }
```

---

## Frontend UI Changes

### 1. Protection Status Hook

**File:** `frontend/src/hooks/useWizardProtection.ts` (NEW)

```typescript
import { useQuery } from '@tanstack/react-query';
import { wizardService } from '../services/wizard.service';

export interface WizardProtectionStatus {
  state: 'draft' | 'in_use' | 'published';
  runs_count: {
    total: number;
    in_progress: number;
    completed: number;
    stored: number;
    abandoned: number;
  };
  can_edit: boolean;
  can_delete: boolean;
  warning_message: string | null;
}

export const useWizardProtection = (wizardId: string | undefined) => {
  return useQuery<WizardProtectionStatus>({
    queryKey: ['wizard-protection', wizardId],
    queryFn: () => wizardService.getProtectionStatus(wizardId!),
    enabled: !!wizardId,
    staleTime: 30000, // Cache for 30 seconds
  });
};
```

### 2. Wizard Builder Header with State Indicator

**File:** `frontend/src/pages/admin/WizardBuilderPage.tsx`

```typescript
import { useWizardProtection } from '../../hooks/useWizardProtection';

const WizardBuilderPage = () => {
  const { wizardId } = useParams();
  const { data: protection, isLoading: protectionLoading } = useWizardProtection(wizardId);

  // Render state badge
  const renderStateBadge = () => {
    if (!protection) return null;

    const badges = {
      draft: { color: 'success', icon: '✏️', label: 'Draft - Edit Freely' },
      in_use: { color: 'warning', icon: '⚠️', label: 'In Use - Edit with Caution' },
      published: { color: 'error', icon: '🔒', label: 'Published - Read Only' },
    };

    const badge = badges[protection.state];

    return (
      <Chip
        icon={<span>{badge.icon}</span>}
        label={badge.label}
        color={badge.color as any}
        sx={{ mr: 2 }}
      />
    );
  };

  // Show protection banner
  const renderProtectionBanner = () => {
    if (!protection || protection.state === 'draft') return null;

    if (protection.state === 'published') {
      return (
        <Alert severity="error" sx={{ mb: 2 }}>
          <AlertTitle>🔒 This Wizard is Locked</AlertTitle>
          <Typography variant="body2" sx={{ mb: 2 }}>
            This wizard has <strong>{protection.runs_count.stored} stored runs</strong> and cannot be edited
            to preserve data integrity.
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={handleCloneWizard}
            >
              Clone Wizard
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={handleCreateVersion}
            >
              Create New Version
            </Button>
          </Box>
        </Alert>
      );
    }

    if (protection.state === 'in_use') {
      return (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <AlertTitle>⚠️ Active Runs Exist</AlertTitle>
          <Typography variant="body2">
            This wizard has <strong>{protection.runs_count.total} active runs</strong>.
            Changes may affect users currently using this wizard.
          </Typography>
        </Alert>
      );
    }

    return null;
  };

  // Disable editing if published
  const isReadOnly = protection?.state === 'published';

  return (
    <Container>
      {/* Header with state */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Wizard Builder</Typography>
        {renderStateBadge()}
      </Box>

      {/* Protection banner */}
      {renderProtectionBanner()}

      {/* Wizard form - disabled if read-only */}
      <TextField
        label="Wizard Name"
        value={wizardName}
        onChange={(e) => setWizardName(e.target.value)}
        disabled={isReadOnly}
        helperText={isReadOnly ? "Read-only: Cannot edit published wizard" : ""}
      />

      {/* ... rest of form with disabled={isReadOnly} ... */}
    </Container>
  );
};
```

### 3. Confirmation Dialog for In-Use Wizards

```typescript
const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
const [pendingAction, setPendingAction] = useState<'edit' | 'delete' | null>(null);

const handleSaveWizard = async () => {
  // Check protection status
  if (protection?.state === 'in_use' && !hasUserConfirmed) {
    // Show confirmation dialog
    setConfirmDialogOpen(true);
    setPendingAction('edit');
    return;
  }

  // Proceed with save
  await saveWizard(wizardData, { force: true });
};

// Confirmation Dialog Component
<Dialog open={confirmDialogOpen} onClose={() => setConfirmDialogOpen(false)} maxWidth="sm">
  <DialogTitle>⚠️ Confirm Modification</DialogTitle>
  <DialogContent>
    <Alert severity="warning" sx={{ mb: 2 }}>
      This wizard has <strong>{protection?.runs_count.total} active runs</strong>.
    </Alert>

    <Typography variant="body2" paragraph>
      Modifying this wizard may:
    </Typography>
    <ul>
      <li>Affect users currently filling out the wizard</li>
      <li>Cause data inconsistencies in incomplete runs</li>
      <li>Break in-progress user sessions</li>
    </ul>

    <Typography variant="body2" sx={{ mt: 2 }}>
      What would you like to do?
    </Typography>
  </DialogContent>
  <DialogActions>
    <Button onClick={() => setConfirmDialogOpen(false)}>
      Cancel
    </Button>
    <Button
      onClick={handleDeleteAllRunsAndModify}
      color="error"
      variant="outlined"
    >
      Delete All Runs & Modify
    </Button>
    <Button
      onClick={handleCreateNewVersion}
      color="primary"
      variant="contained"
    >
      Create New Version Instead
    </Button>
  </DialogActions>
</Dialog>
```

### 4. Clone Wizard Dialog

```typescript
const [cloneDialogOpen, setCloneDialogOpen] = useState(false);
const [cloneName, setCloneName] = useState('');

const handleCloneWizard = () => {
  setCloneName(`${wizard.name} (Copy)`);
  setCloneDialogOpen(true);
};

const confirmClone = async () => {
  const clonedWizard = await wizardService.cloneWizard(wizardId, cloneName);
  setSnackbar({
    open: true,
    message: 'Wizard cloned successfully!',
    severity: 'success'
  });
  // Navigate to cloned wizard in builder
  navigate(`/admin/wizard-builder/${clonedWizard.id}`);
};

// Clone Dialog
<Dialog open={cloneDialogOpen} onClose={() => setCloneDialogOpen(false)} maxWidth="sm">
  <DialogTitle>Clone Wizard</DialogTitle>
  <DialogContent>
    <Typography variant="body2" paragraph>
      Create an independent copy of this wizard that you can edit freely.
    </Typography>
    <TextField
      autoFocus
      margin="dense"
      label="New Wizard Name"
      fullWidth
      value={cloneName}
      onChange={(e) => setCloneName(e.target.value)}
    />
  </DialogContent>
  <DialogActions>
    <Button onClick={() => setCloneDialogOpen(false)}>Cancel</Button>
    <Button onClick={confirmClone} variant="contained">
      Clone Wizard
    </Button>
  </DialogActions>
</Dialog>
```

---

## User Experience Flows

### Flow 1: Draft Wizard (No Restrictions)

```
User creates new wizard
    ↓
[Wizard Builder] State: Draft ✏️
    ↓
Edit freely:
  • Add/remove steps
  • Modify fields
  • Change validation
    ↓
Save → Success ✓
```

**UI State:**
- Green badge: "Draft - Edit Freely"
- No warnings
- All controls enabled

---

### Flow 2: In-Use Wizard (Warning Required)

```
Wizard has 10 active runs
    ↓
User tries to edit
    ↓
[Warning Dialog Appears] ⚠️
    ↓
User chooses:
  Option A: Cancel
  Option B: Delete all runs & modify
  Option C: Create new version
    ↓
Option A → No changes made
Option B → Deletes runs → Allows edit
Option C → Creates version → Navigates to new version
```

**UI State:**
- Orange badge: "In Use - Edit with Caution"
- Warning banner showing run counts
- Confirmation dialog on save/delete

---

### Flow 3: Published Wizard (Read-Only + Alternatives)

```
Wizard has stored runs
    ↓
User opens wizard builder
    ↓
[Read-Only Mode] 🔒
    ↓
All fields disabled
Banner shows: "Has 5 stored runs"
    ↓
User options:
  [Clone Wizard] → Creates editable copy
  [Create Version] → Versioning system (future)
  [Archive] → Hides wizard
```

**UI State:**
- Red badge: "Published - Read Only"
- Red alert banner with alternatives
- All form controls disabled
- Only view/clone/archive actions available

---

## Migration Guide

### Step 1: Database Migration

```bash
# Create migration file
alembic revision -m "add_wizard_lifecycle_protection"
```

```python
# Migration file
def upgrade():
    # Add columns
    op.add_column('wizards',
        sa.Column('first_run_at', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column('wizards',
        sa.Column('first_stored_run_at', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column('wizards',
        sa.Column('lifecycle_state', sa.String(20), server_default='draft')
    )
    op.add_column('wizards',
        sa.Column('is_archived', sa.Boolean(), server_default='false')
    )
    op.add_column('wizards',
        sa.Column('archived_at', sa.TIMESTAMP(timezone=True), nullable=True)
    )

    # Create indexes
    op.create_index('idx_wizards_lifecycle_state', 'wizards', ['lifecycle_state'])
    op.create_index('idx_wizards_archived', 'wizards', ['is_archived'])

    # Backfill existing wizards
    conn = op.get_bind()

    # Set lifecycle_state based on existing runs
    conn.execute("""
        UPDATE wizards w
        SET
            lifecycle_state = CASE
                WHEN EXISTS (
                    SELECT 1 FROM wizard_runs wr
                    WHERE wr.wizard_id = w.id AND wr.is_stored = true
                ) THEN 'published'
                WHEN EXISTS (
                    SELECT 1 FROM wizard_runs wr
                    WHERE wr.wizard_id = w.id
                ) THEN 'in_use'
                ELSE 'draft'
            END,
            first_run_at = (
                SELECT MIN(started_at)
                FROM wizard_runs wr
                WHERE wr.wizard_id = w.id
            ),
            first_stored_run_at = (
                SELECT MIN(completed_at)
                FROM wizard_runs wr
                WHERE wr.wizard_id = w.id AND wr.is_stored = true
            )
    """)

def downgrade():
    op.drop_index('idx_wizards_archived')
    op.drop_index('idx_wizards_lifecycle_state')
    op.drop_column('wizards', 'archived_at')
    op.drop_column('wizards', 'is_archived')
    op.drop_column('wizards', 'lifecycle_state')
    op.drop_column('wizards', 'first_stored_run_at')
    op.drop_column('wizards', 'first_run_at')
```

### Step 2: Backend Code

1. Create `backend/app/services/wizard_protection.py` (full code above)
2. Update `backend/app/api/v1/wizards.py` with protection endpoints
3. Update `backend/app/models/wizard.py` to include new columns
4. Update `backend/app/schemas/wizard.py` with protection status schema

### Step 3: Frontend Code

1. Create `frontend/src/hooks/useWizardProtection.ts`
2. Update `frontend/src/services/wizard.service.ts` with new methods
3. Update `frontend/src/pages/admin/WizardBuilderPage.tsx`
4. Add confirmation dialogs and clone functionality

---

## Implementation Timeline

### Week 1: Backend Foundation
- Day 1-2: Database migration
- Day 3-4: Protection service implementation
- Day 5: API endpoints (status, clone, archive)

### Week 2: Frontend Integration
- Day 1-2: Protection hook and service methods
- Day 3-4: Wizard builder UI updates
- Day 5: Confirmation dialogs and clone UI

### Week 3: Testing & Refinement
- Integration testing
- User acceptance testing
- Bug fixes and polish

**Total Effort:** ~15 days (3 weeks)

---

## Summary

### Your Three-Scenario Strategy: IMPLEMENTED ✅

| Scenario | Your Preference | Implementation Status |
|----------|----------------|----------------------|
| **1. Draft (Unused)** | Allow all modifications | ✅ No restrictions |
| **2. In-Use (Not stored)** | Warn + require confirmation | ✅ Warning dialog with options |
| **3. Published (Stored runs)** | Read-only + clone/version | ✅ Locked + alternatives |

### Benefits:

✅ **Data Protection** - Stored runs never affected
✅ **User-Friendly** - Progressive protection, not blocking
✅ **Flexibility** - Clone/version options for published wizards
✅ **Clear UX** - Visual state indicators (badges, banners)
✅ **Safe Evolution** - Can't accidentally destroy user data

This approach balances **data integrity** with **usability** perfectly! 🎯
