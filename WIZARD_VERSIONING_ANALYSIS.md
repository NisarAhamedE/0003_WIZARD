# Wizard Structure Modification Impact Analysis

**Critical Issue:** What happens to stored wizard runs when the wizard structure is modified?

**Date:** November 19, 2025
**Severity:** 🔴 **HIGH** - Potential Data Loss & Corruption
**Status:** ⚠️ **NEEDS ATTENTION**

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Current Behavior Analysis](#current-behavior-analysis)
3. [Impact Scenarios](#impact-scenarios)
4. [Root Cause Analysis](#root-cause-analysis)
5. [Proposed Solutions](#proposed-solutions)
6. [Implementation Recommendations](#implementation-recommendations)

---

## Problem Statement

### The Scenario

```
Timeline:
┌─────────────────────────────────────────────────────────────┐
│ Day 1: Create Wizard "Customer Survey"                      │
│ ├─ Step 1: Personal Info                                    │
│ │  ├─ Option Set: Full Name (text_input)                    │
│ │  └─ Option Set: Email (text_input)                        │
│ ├─ Step 2: Preferences                                      │
│ │  └─ Option Set: Favorite Color (single_select)            │
│ └─ Publish wizard                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Day 2: User completes wizard run                            │
│ Stored Run ID: run-123                                      │
│ Responses:                                                   │
│ ├─ Full Name: "John Doe"                                    │
│ ├─ Email: "john@example.com"                                │
│ └─ Favorite Color: "blue"                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Day 3: Admin modifies wizard in Wizard Builder              │
│ SCENARIO A: Delete "Email" option set                       │
│ SCENARIO B: Delete entire "Personal Info" step              │
│ SCENARIO C: Add new required field "Phone Number"           │
│ SCENARIO D: Change "Favorite Color" from single to multiple │
│ SCENARIO E: Delete the entire wizard                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    ❓ WHAT HAPPENS?
```

---

## Current Behavior Analysis

### Database Structure

```sql
-- Wizard structure (mutable)
wizards
  ↓ ondelete='CASCADE'
steps
  ↓ ondelete='CASCADE'
option_sets
  ↓ ondelete='CASCADE'
options

-- Run responses (references wizard structure)
wizard_runs
  ├─ wizard_id → wizards.id (ondelete='CASCADE')
  └─ wizard_run_step_responses
      ├─ step_id → steps.id (ondelete='CASCADE')  ⚠️
      └─ wizard_run_option_set_responses
          └─ option_set_id → option_sets.id (ondelete='CASCADE')  ⚠️⚠️
```

### Critical Foreign Keys

**From:** `backend/app/models/wizard_run.py`

```python
class WizardRunStepResponse(Base):
    step_id = Column(UUID, ForeignKey('steps.id', ondelete='CASCADE'))
    # ⚠️ If step is deleted, ALL responses for that step are CASCADE DELETED

class WizardRunOptionSetResponse(Base):
    option_set_id = Column(UUID, ForeignKey('option_sets.id', ondelete='CASCADE'))
    # ⚠️⚠️ If option set is deleted, ALL user responses are CASCADE DELETED
```

---

## Impact Scenarios

### Scenario A: Delete an Option Set (e.g., "Email" field)

**Admin Action:**
```typescript
// Wizard Builder - User deletes "Email" option set
DELETE /api/v1/option-sets/{email-option-set-id}
```

**Database Effect:**
```sql
-- PostgreSQL cascade delete
DELETE FROM option_sets WHERE id = 'email-option-set-id';

-- Automatically triggers cascade:
DELETE FROM wizard_run_option_set_responses
WHERE option_set_id = 'email-option-set-id';
```

**Result:**
```
Before deletion:
run-123:
  ├─ Full Name: "John Doe" ✓
  ├─ Email: "john@example.com" ✓
  └─ Favorite Color: "blue" ✓

After deletion:
run-123:
  ├─ Full Name: "John Doe" ✓
  ├─ Email: [DELETED] ❌  ← USER DATA LOST!
  └─ Favorite Color: "blue" ✓
```

**Impact:**
- ❌ **User response data permanently deleted**
- ❌ **No warning to admin**
- ❌ **No way to recover**
- ❌ **Historical data corrupted**

---

### Scenario B: Delete an Entire Step

**Admin Action:**
```typescript
// Wizard Builder - Delete "Personal Info" step
DELETE /api/v1/steps/{personal-info-step-id}
```

**Database Effect:**
```sql
DELETE FROM steps WHERE id = 'personal-info-step-id';

-- Cascades to:
DELETE FROM option_sets WHERE step_id = 'personal-info-step-id';
DELETE FROM wizard_run_step_responses WHERE step_id = 'personal-info-step-id';
DELETE FROM wizard_run_option_set_responses
  WHERE step_response_id IN (
    SELECT id FROM wizard_run_step_responses
    WHERE step_id = 'personal-info-step-id'
  );
```

**Result:**
```
Before deletion:
run-123:
  Step 1 (Personal Info):
    ├─ Full Name: "John Doe" ✓
    └─ Email: "john@example.com" ✓
  Step 2 (Preferences):
    └─ Favorite Color: "blue" ✓

After deletion:
run-123:
  Step 1 (Personal Info): [DELETED] ❌  ← ENTIRE STEP LOST!
  Step 2 (Preferences):
    └─ Favorite Color: "blue" ✓
```

**Impact:**
- ❌ **All user responses for that step deleted**
- ❌ **Multiple users' data affected**
- ❌ **Analytics/reporting broken**
- ❌ **Compliance issues (GDPR requires data retention)**

---

### Scenario C: Delete the Entire Wizard

**Admin Action:**
```typescript
DELETE /api/v1/wizards/{wizard-id}
```

**Database Effect:**
```sql
DELETE FROM wizards WHERE id = 'wizard-id';

-- CASCADE deletes EVERYTHING:
DELETE FROM steps WHERE wizard_id = 'wizard-id';
DELETE FROM option_sets WHERE step_id IN (...);
DELETE FROM wizard_runs WHERE wizard_id = 'wizard-id';  ⚠️⚠️⚠️
DELETE FROM wizard_run_step_responses WHERE run_id IN (...);
DELETE FROM wizard_run_option_set_responses WHERE run_id IN (...);
```

**Result:**
```
Before deletion:
- 500 stored wizard runs
- 5,000 user responses
- Historical data from 3 months

After deletion:
[ALL DATA DELETED] ❌❌❌
```

**Impact:**
- ❌❌❌ **CATASTROPHIC DATA LOSS**
- ❌ **All stored runs deleted**
- ❌ **All user responses deleted**
- ❌ **All analytics data lost**
- ❌ **Legal/compliance violations**

---

### Scenario D: Modify Option Set Type

**Admin Action:**
```typescript
// Change "Favorite Color" from single_select to multiple_select
PUT /api/v1/option-sets/{color-option-set-id}
{
  "selection_type": "multiple_select"  // Was: "single_select"
}
```

**Current Stored Data:**
```json
{
  "option_set_id": "color-option-set-id",
  "selection_type": "single_select",
  "response_value": {
    "value": "blue"  // Single string value
  }
}
```

**What happens when viewing the run?**

```typescript
// Frontend tries to render multiple_select
<Checkbox checked={selectedValues.includes("blue")} />
// BUT selectedValues expects array: ["blue"]
// Actual value is string: "blue"
// Result: TYPE MISMATCH ERROR ❌
```

**Impact:**
- ❌ **Runtime errors when viewing stored runs**
- ❌ **UI breaks or shows incorrect data**
- ❌ **Cannot edit the run**

---

### Scenario E: Add New Required Field

**Admin Action:**
```typescript
// Add new required option set "Phone Number"
POST /api/v1/option-sets
{
  "step_id": "personal-info-step-id",
  "name": "Phone Number",
  "is_required": true
}
```

**What happens to existing runs?**

```
Existing run-123:
  ├─ Full Name: "John Doe" ✓
  ├─ Email: "john@example.com" ✓
  ├─ Phone Number: [MISSING] ❌  ← New required field

When user tries to EDIT run-123:
  → Validation fails: "Phone Number is required"
  → Cannot save changes
  → Run is locked/unusable ❌
```

**Impact:**
- ❌ **Existing runs become invalid**
- ❌ **Users cannot edit their saved runs**
- ❌ **Breaks backward compatibility**

---

## Root Cause Analysis

### Design Flaw: Direct Foreign Key References

```python
# CURRENT (PROBLEMATIC):
class WizardRunOptionSetResponse:
    option_set_id = ForeignKey('option_sets.id', ondelete='CASCADE')
    # ⚠️ Directly references mutable wizard structure
    # ⚠️ When wizard changes, run data is affected
```

### Why This is Problematic

```
Wizard Structure (VERSION 1)          Wizard Structure (VERSION 2)
┌─────────────────────┐              ┌─────────────────────┐
│ option_set_id: A    │              │ option_set_id: A    │
│ name: "Email"       │  ─DELETE→    │ [DELETED]           │
└─────────────────────┘              └─────────────────────┘
         ↑                                      ↑
         │                                      │
    REFERENCES                              BROKEN!
         │                                      │
┌─────────────────────┐              ┌─────────────────────┐
│ Run Response        │              │ Run Response        │
│ option_set_id: A ✓  │  ────────→   │ option_set_id: A ❌ │
│ value: "john@..."   │              │ [CASCADE DELETED]   │
└─────────────────────┘              └─────────────────────┘
```

### The Core Problem

**Runs are tied to wizard structure, not wizard version/snapshot**

- Wizards are **mutable** (can be edited/deleted)
- Runs **reference** wizard structure directly
- When structure changes, run data is **destroyed** or **invalidated**

---

## Proposed Solutions

### Solution 1: Wizard Versioning (Snapshot Approach) ⭐ RECOMMENDED

**Concept:** Create immutable snapshots of wizard structure for each run

```sql
-- NEW TABLE: Wizard versions (immutable snapshots)
CREATE TABLE wizard_versions (
    id UUID PRIMARY KEY,
    wizard_id UUID REFERENCES wizards(id) ON DELETE SET NULL,
    version_number INTEGER NOT NULL,
    structure JSONB NOT NULL,  -- Full wizard structure snapshot
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE(wizard_id, version_number)
);

-- MODIFIED: Runs reference version, not wizard
CREATE TABLE wizard_runs (
    id UUID PRIMARY KEY,
    wizard_id UUID REFERENCES wizards(id) ON DELETE SET NULL,  -- Changed to SET NULL
    wizard_version_id UUID REFERENCES wizard_versions(id) ON DELETE RESTRICT,  -- Cannot delete versions with runs
    ...
);

-- Run responses NO LONGER reference wizard structure
CREATE TABLE wizard_run_option_set_responses (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,

    -- REMOVE: option_set_id foreign key
    -- ADD: Denormalized snapshot data
    option_set_snapshot JSONB NOT NULL,  -- {id, name, type, options, etc.}

    response_value JSONB NOT NULL,
    ...
);
```

**How It Works:**

```
Day 1: Wizard created
┌─────────────────────────────────┐
│ wizards                          │
│ id: wizard-1                     │
│ name: "Customer Survey"          │
└─────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ wizard_versions                  │
│ id: version-1                    │
│ wizard_id: wizard-1              │
│ version_number: 1                │
│ structure: {                     │
│   steps: [                       │
│     {id: "step-1",               │
│      name: "Personal Info",      │
│      option_sets: [              │
│        {id: "opt-1", name: "Email"}, │
│        ...                       │
│      ]}                          │
│   ]                              │
│ }                                │
└─────────────────────────────────┘

Day 2: User completes run
┌─────────────────────────────────┐
│ wizard_runs                      │
│ id: run-123                      │
│ wizard_id: wizard-1              │
│ wizard_version_id: version-1  ✓ │  ← REFERENCES IMMUTABLE VERSION
└─────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ wizard_run_option_set_responses  │
│ option_set_snapshot: {           │  ← FULL SNAPSHOT
│   id: "opt-1",                   │
│   name: "Email",                 │
│   type: "text_input"             │
│ }                                │
│ response_value: {                │
│   value: "john@example.com"      │
│ }                                │
└─────────────────────────────────┘

Day 3: Admin modifies wizard
┌─────────────────────────────────┐
│ wizards (MODIFIED)               │
│ id: wizard-1                     │
│ name: "Customer Survey"          │
│ [Email field DELETED]            │
└─────────────────────────────────┘
         │
         ↓ Creates new version
┌─────────────────────────────────┐
│ wizard_versions                  │
│ version-1 (OLD - IMMUTABLE) ✓   │  ← OLD RUNS STILL USE THIS
│ version-2 (NEW - ACTIVE) ✓      │  ← NEW RUNS USE THIS
└─────────────────────────────────┘

Result: run-123 STILL WORKS ✓
- References version-1 (immutable)
- Has full snapshot of structure
- Can view/edit with original structure
- New runs use version-2
```

**Advantages:**
- ✅ **Data preservation** - Old runs never affected
- ✅ **Full audit trail** - See exactly what user saw
- ✅ **Time travel** - View wizard as it was at run time
- ✅ **Safe modifications** - Admins can change wizard freely
- ✅ **Rollback capability** - Can revert to old versions

**Disadvantages:**
- ⚠️ Storage overhead (full structure per version)
- ⚠️ More complex queries
- ⚠️ Migration required for existing data

---

### Solution 2: Denormalization (Store Everything) ⭐ SIMPLE

**Concept:** Store complete wizard structure snapshot with each run

```sql
-- Add snapshot column to runs
ALTER TABLE wizard_runs ADD COLUMN wizard_structure_snapshot JSONB;

-- Remove foreign key constraints that cascade delete
ALTER TABLE wizard_run_step_responses
DROP CONSTRAINT fk_step_id;

ALTER TABLE wizard_run_option_set_responses
DROP CONSTRAINT fk_option_set_id;

-- Add snapshot columns
ALTER TABLE wizard_run_step_responses
ADD COLUMN step_snapshot JSONB;

ALTER TABLE wizard_run_option_set_responses
ADD COLUMN option_set_snapshot JSONB;
```

**Implementation:**

```typescript
// When creating a run, snapshot entire wizard
const createRun = async (wizardId: string) => {
  const wizard = await getWizardWithFullStructure(wizardId);

  return await wizardRunService.create({
    wizard_id: wizardId,
    wizard_structure_snapshot: wizard  // ← Store entire structure
  });
};

// When viewing a run
const viewRun = async (runId: string) => {
  const run = await wizardRunService.get(runId);

  // Use snapshot, not current wizard
  const wizardStructure = run.wizard_structure_snapshot;

  // Render using historical structure
  return renderWizard(wizardStructure, run.responses);
};
```

**Advantages:**
- ✅ **Simple implementation** - Just add columns
- ✅ **Fast reads** - No joins needed
- ✅ **Complete isolation** - Wizard changes don't affect runs
- ✅ **Easy migration** - Can backfill snapshots

**Disadvantages:**
- ⚠️ **Storage duplication** - Full wizard per run
- ⚠️ **No normalization** - Updates don't propagate
- ⚠️ **Harder to query** - JSONB queries less efficient

---

### Solution 3: Soft Deletes + Historical Preservation

**Concept:** Never actually delete wizard structure

```sql
-- Add soft delete flags
ALTER TABLE wizards ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE steps ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE option_sets ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;

-- Change cascade to SET NULL
ALTER TABLE wizard_runs
DROP CONSTRAINT fk_wizard_id,
ADD CONSTRAINT fk_wizard_id
FOREIGN KEY (wizard_id) REFERENCES wizards(id) ON DELETE SET NULL;
```

**Implementation:**

```python
# Instead of DELETE
def delete_option_set(option_set_id):
    option_set = db.query(OptionSet).filter(OptionSet.id == option_set_id).first()
    option_set.is_deleted = True  # Soft delete
    option_set.deleted_at = datetime.now()
    db.commit()

# Filter in queries
def get_active_option_sets(step_id):
    return db.query(OptionSet).filter(
        OptionSet.step_id == step_id,
        OptionSet.is_deleted == False  # Only active
    ).all()

# For viewing runs, show ALL (including deleted)
def get_run_option_sets(run_id):
    return db.query(OptionSet).filter(
        OptionSet.id.in_(run_responses_option_set_ids)
        # Don't filter is_deleted - show historical data
    ).all()
```

**Advantages:**
- ✅ **Data preservation** - Nothing truly deleted
- ✅ **Audit trail** - See what was deleted and when
- ✅ **Recovery possible** - Can undelete
- ✅ **Moderate complexity** - Easier than versioning

**Disadvantages:**
- ⚠️ **Query complexity** - Must filter is_deleted everywhere
- ⚠️ **Storage accumulation** - Deleted data remains
- ⚠️ **Doesn't solve type changes** - Modifying still breaks runs

---

### Solution 4: Hybrid Approach ⭐⭐ BEST OF ALL WORLDS

**Combine versioning with denormalization:**

```sql
-- Wizard versions (for metadata)
CREATE TABLE wizard_versions (
    id UUID PRIMARY KEY,
    wizard_id UUID REFERENCES wizards(id),
    version_number INTEGER,
    published_at TIMESTAMP,
    is_active BOOLEAN
);

-- Runs reference version
CREATE TABLE wizard_runs (
    wizard_version_id UUID REFERENCES wizard_versions(id),
    -- NO foreign keys to steps/option_sets
);

-- Store snapshots in responses (denormalized)
CREATE TABLE wizard_run_option_set_responses (
    option_set_id UUID NOT NULL,  -- For querying, not FK
    option_set_snapshot JSONB NOT NULL,  -- Full structure
    response_value JSONB NOT NULL
);
```

**Best of both worlds:**
- ✅ Version tracking for audit/rollback
- ✅ Denormalized for fast reads
- ✅ No cascade delete issues
- ✅ Complete data preservation

---

## Implementation Recommendations

### Priority 1: Immediate Protection (Week 1) 🔴 CRITICAL

**1. Remove CASCADE deletes**

```sql
-- Migration: Remove dangerous cascades
ALTER TABLE wizard_run_step_responses
DROP CONSTRAINT wizard_run_step_responses_step_id_fkey,
ADD CONSTRAINT wizard_run_step_responses_step_id_fkey
FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE SET NULL;

ALTER TABLE wizard_run_option_set_responses
DROP CONSTRAINT wizard_run_option_set_responses_option_set_id_fkey,
ADD CONSTRAINT wizard_run_option_set_responses_option_set_id_fkey
FOREIGN KEY (option_set_id) REFERENCES option_sets(id) ON DELETE SET NULL;
```

**2. Add warning in Wizard Builder UI**

```typescript
const handleDeleteOptionSet = (optionSetId: string) => {
  // Check if any runs use this option set
  const affectedRuns = await getRunsUsingOptionSet(optionSetId);

  if (affectedRuns.length > 0) {
    showWarning({
      title: "Warning: Active Runs Exist",
      message: `${affectedRuns.length} stored wizard runs contain data for this field.
                Deleting it may break those runs.

                Recommended: Create a new version instead.`,
      actions: ["Cancel", "Delete Anyway", "Create New Version"]
    });
  }
};
```

---

### Priority 2: Implement Versioning (Month 1) 🟡 HIGH

**1. Create wizard_versions table**

```sql
CREATE TABLE wizard_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE SET NULL,
    version_number INTEGER NOT NULL,
    structure JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT FALSE,
    change_summary TEXT,

    UNIQUE(wizard_id, version_number)
);

CREATE INDEX idx_wizard_versions_wizard ON wizard_versions(wizard_id);
CREATE INDEX idx_wizard_versions_active ON wizard_versions(wizard_id, is_active);
```

**2. Auto-create versions on publish**

```python
@router.post("/wizards/{wizard_id}/publish")
async def publish_wizard(wizard_id: UUID, db: Session):
    wizard = get_wizard_with_structure(db, wizard_id)

    # Get current version number
    last_version = db.query(WizardVersion)\
        .filter(WizardVersion.wizard_id == wizard_id)\
        .order_by(desc(WizardVersion.version_number))\
        .first()

    new_version_number = (last_version.version_number + 1) if last_version else 1

    # Create new version
    version = WizardVersion(
        wizard_id=wizard_id,
        version_number=new_version_number,
        structure=wizard.to_dict(),  # Full snapshot
        is_active=True
    )

    # Deactivate old versions
    db.query(WizardVersion)\
        .filter(WizardVersion.wizard_id == wizard_id)\
        .update({WizardVersion.is_active: False})

    db.add(version)
    db.commit()

    return version
```

**3. Update runs to reference version**

```sql
ALTER TABLE wizard_runs
ADD COLUMN wizard_version_id UUID REFERENCES wizard_versions(id);

-- Backfill: Create version 1 for existing wizards
INSERT INTO wizard_versions (wizard_id, version_number, structure, is_active)
SELECT id, 1, row_to_json(wizard.*), true
FROM wizards;

UPDATE wizard_runs wr
SET wizard_version_id = wv.id
FROM wizard_versions wv
WHERE wr.wizard_id = wv.wizard_id AND wv.version_number = 1;
```

---

### Priority 3: Denormalize Run Data (Month 2) 🟢 MEDIUM

**Add snapshot columns:**

```sql
ALTER TABLE wizard_run_step_responses
ADD COLUMN step_snapshot JSONB;

ALTER TABLE wizard_run_option_set_responses
ADD COLUMN option_set_snapshot JSONB;

-- Backfill snapshots from current structure
UPDATE wizard_run_step_responses wrsr
SET step_snapshot = (
    SELECT row_to_json(s.*)
    FROM steps s
    WHERE s.id = wrsr.step_id
);
```

**Update save logic:**

```typescript
// When saving responses
for (const optionSet of step.option_sets) {
  await wizardRunService.createOptionSetResponse({
    run_id: runId,
    option_set_id: optionSet.id,
    option_set_snapshot: optionSet,  // ← FULL SNAPSHOT
    response_value: { value: responseValue }
  });
}
```

---

### Priority 4: UI Changes (Month 2) 🟢 MEDIUM

**1. Show version in View mode**

```typescript
<Alert severity="info">
  You are viewing a run from Wizard v{run.wizard_version_number}
  {isCurrentVersion ?
    "(Current version)" :
    "(Older version - wizard has been updated)"}
</Alert>
```

**2. Allow viewing different versions**

```typescript
<Select value={selectedVersion} onChange={handleVersionChange}>
  {versions.map(v => (
    <MenuItem value={v.id}>
      Version {v.version_number} - {formatDate(v.created_at)}
    </MenuItem>
  ))}
</Select>
```

**3. Migration tool for old runs**

```typescript
<Button onClick={migrateToNewVersion}>
  Migrate this run to latest wizard version
</Button>
```

---

## Summary & Recommendations

### Current Status: 🔴 CRITICAL VULNERABILITY

**Problem:** Modifying or deleting wizard structure CASCADE DELETES user data

**Affected:**
- ❌ All stored wizard runs
- ❌ Historical analytics
- ❌ User submissions
- ❌ Compliance/audit trails

### Recommended Solution: Hybrid Versioning + Denormalization

**Implementation Timeline:**

| Priority | Task | Time | Impact |
|----------|------|------|--------|
| 🔴 IMMEDIATE | Remove CASCADE deletes | 2 hours | Prevent data loss |
| 🔴 IMMEDIATE | Add deletion warnings | 4 hours | Alert admins |
| 🟡 Week 1 | Implement versioning | 16 hours | Enable safe changes |
| 🟡 Week 2 | Denormalize snapshots | 12 hours | Complete isolation |
| 🟢 Month 1 | UI improvements | 8 hours | Better UX |

**Total Effort:** ~42 hours to fully solve

---

## Code Examples

### Before (Current - Problematic):

```python
# Deleting option set CASCADE DELETES user data ❌
DELETE FROM option_sets WHERE id = 'opt-1';
→ CASCADE deletes all responses containing that option set
→ User data lost forever
```

### After (With Versioning - Safe):

```python
# Deleting option set is SAFE ✓
DELETE FROM option_sets WHERE id = 'opt-1';
→ Old runs reference wizard_version with snapshot
→ User data preserved in option_set_snapshot JSONB
→ New runs use wizard_version without that option set
→ Both coexist safely
```

---

## Conclusion

**This is a critical architectural issue that must be addressed before production deployment.**

Without versioning, any wizard modification risks:
- 🔴 Permanent data loss
- 🔴 Broken stored runs
- 🔴 Compliance violations
- 🔴 User trust issues

**The recommended hybrid solution provides:**
- ✅ Complete data preservation
- ✅ Safe wizard evolution
- ✅ Backward compatibility
- ✅ Forward compatibility
- ✅ Audit compliance
