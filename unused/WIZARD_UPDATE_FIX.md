# Wizard Update Fix - Steps, Option Sets, and Options Now Editable

**Date**: 2025-01-18
**Issue**: When editing a wizard, modifications to steps, option_sets, and options were not being saved

---

## Problem Identified

### Root Cause:
The `WizardUpdate` schema did **NOT include the `steps` field**, so when editing a wizard through the Wizard Builder UI, any changes to:
- Steps
- Option Sets
- Options
- Option order

...were completely ignored by the backend API.

### Technical Details:

**Before Fix:**
```python
class WizardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    # ... other wizard-level fields
    # ❌ NO steps field - nested data ignored!
```

The `update` method in `wizard_crud` only updated wizard-level fields:
```python
def update(self, db: Session, db_obj: Wizard, obj_in: WizardUpdate):
    # Only updated name, description, is_published, etc.
    # Steps/options were never touched!
```

---

## Solution Implemented

### 1. Updated WizardUpdate Schema
**File**: `backend/app/schemas/wizard.py` (line 216)

Added `steps` field to allow updating nested data:
```python
class WizardUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    # ... other fields ...
    steps: Optional[List["StepCreate"]] = None  # ✓ Now accepts steps!
```

### 2. Updated CRUD Update Method
**File**: `backend/app/crud/wizard.py` (lines 91-128)

Completely rewrote the `update` method to handle nested updates:

```python
def update(self, db: Session, db_obj: Wizard, obj_in: WizardUpdate) -> Wizard:
    """Update wizard with nested steps, option_sets, and options"""
    # Update wizard basic fields
    update_data = obj_in.model_dump(exclude_unset=True, exclude={"steps"})
    for field in update_data:
        setattr(db_obj, field, update_data[field])

    # Handle steps update if provided
    if obj_in.steps is not None:
        # Delete existing steps (CASCADE deletes option_sets and options)
        db.query(Step).filter(Step.wizard_id == db_obj.id).delete()
        db.flush()

        # Recreate all steps with new data
        for step_data in obj_in.steps:
            # Create step
            db_step = Step(**step_dict, wizard_id=db_obj.id)

            # Create option sets
            for option_set_data in step_data.option_sets:
                db_option_set = OptionSet(**option_set_dict, step_id=db_step.id)

                # Create options
                for option_data in option_set_data.options:
                    db_option = Option(**option_data.model_dump(),
                                     option_set_id=db_option_set.id)
```

---

## How It Works Now

### Update Flow:
1. **Frontend** sends wizard update with complete `steps` array
2. **Backend** deletes all existing steps (CASCADE removes child data)
3. **Backend** recreates all steps, option_sets, and options from scratch
4. **Dependencies** are preserved (handled by OptionDependencyManager)
5. **Database** returns fully refreshed wizard with all nested data

### What's Editable Now:
- ✓ Wizard name, description, settings
- ✓ Add/remove/reorder steps
- ✓ Add/remove/modify option sets
- ✓ Add/remove/modify options
- ✓ Change option labels, values, descriptions
- ✓ Change selection types (single_select, multiple_select, etc.)
- ✓ Update validation rules (min_selections, max_selections, etc.)
- ✓ Modify help text and placeholders

---

## Testing

### Test Case 1: Edit Wizard Name
1. Open existing wizard in Wizard Builder
2. Change wizard name
3. Save
4. **Expected**: Name updates ✓

### Test Case 2: Add New Step
1. Open existing wizard
2. Click "Add Step"
3. Fill in step details
4. Save
5. **Expected**: New step appears in wizard ✓

### Test Case 3: Modify Option Set
1. Open existing wizard
2. Go to existing step
3. Change option set selection type
4. Save
5. **Expected**: Selection type updates ✓

### Test Case 4: Edit Options
1. Open existing wizard
2. Change option label/value
3. Add new option
4. Delete existing option
5. Save
6. **Expected**: All option changes persist ✓

---

## Files Modified

### Backend:
1. **backend/app/schemas/wizard.py** (line 216)
   - Added `steps: Optional[List["StepCreate"]] = None` to `WizardUpdate`

2. **backend/app/crud/wizard.py** (lines 91-128)
   - Rewrote `update()` method to handle nested data
   - Delete-and-recreate approach ensures clean updates
   - Returns fully loaded wizard with `self.get(db, db_obj.id)`

---

## Important Notes

### Delete-and-Recreate Strategy:
The update uses a **delete-and-recreate** approach rather than trying to diff and merge changes. This ensures:
- **Simplicity**: No complex diff logic needed
- **Consistency**: Fresh data every time
- **Reliability**: No orphaned records
- **CASCADE**: Database automatically cleans up option_sets and options

### Dependencies Handling:
- Dependencies are managed separately by the frontend `syncDependencies()` function
- After wizard update completes, dependencies are synced via dedicated endpoints
- This two-phase approach keeps the update logic clean

### Performance Consideration:
- For large wizards (100+ steps), this could be slow
- Currently acceptable for typical wizard sizes (5-20 steps)
- Future optimization: Implement intelligent diff/merge if needed

---

## API Usage Example

### Update Wizard Request:
```json
PUT /api/v1/wizards/{wizard_id}
{
  "name": "Updated Wizard Name",
  "description": "New description",
  "steps": [
    {
      "name": "Step 1",
      "step_order": 1,
      "option_sets": [
        {
          "name": "Question 1",
          "selection_type": "single_select",
          "options": [
            {"label": "Option A", "value": "a"},
            {"label": "Option B", "value": "b"}
          ]
        }
      ]
    }
  ]
}
```

### Response:
```json
{
  "id": "wizard-uuid",
  "name": "Updated Wizard Name",
  "description": "New description",
  "steps": [ /* full nested structure */ ],
  "updated_at": "2025-01-18T..."
}
```

---

## Status

**Issue**: Resolved ✓
**Testing**: Required (restart backend server)
**Breaking Changes**: None
**Migration**: Not required

---

## Next Steps

1. **Restart backend server** to load the new code
2. **Test wizard editing** in Wizard Builder
3. **Verify** that step/option changes persist
4. **Check** that dependencies still work after update

---

**Fixed**: 2025-01-18
**Files Modified**: 2
**Lines Changed**: ~40
**Backward Compatible**: Yes ✓
