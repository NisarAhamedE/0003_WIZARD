# Edit Run Workflow - Technical Specification

## Overview
This document defines the complete workflow for editing stored wizard runs, including the new "Update This Run" dialog with three action options.

## Workflow Sequence

```
My Runs Page → Edit Button → Wizard Player (Edit Mode) → Complete Button → Update This Run Dialog → Action Selection
```

## Detailed Flow

### 1. My Runs Page - Edit Action
**Location**: [MyRunsPage.tsx:85-88](frontend/src/pages/MyRunsPage.tsx#L85-L88)

**Current Behavior**:
```typescript
const handleEditRun = (run: WizardRun) => {
  // Navigate to wizard player in edit mode with the stored run
  navigate(`/wizard/${run.wizard_id}?session=${run.id}`);
};
```

**Trigger**: User clicks "Edit" button on a stored run card
**Action**: Navigates to WizardPlayerPage with `session` query parameter

---

### 2. Wizard Player Page - Edit Mode
**Location**: [WizardPlayerPage.tsx](frontend/src/pages/WizardPlayerPage.tsx)

**Current Detection Logic**:
```typescript
const sessionIdFromUrl = searchParams.get('session');
const isViewOnly = searchParams.get('view_only') === 'true';
```

**States**:
- `isCompleted`: Set to `true` when loading a completed run
- `isViewOnly`: Set to `true` for read-only mode (from URL param)
- **Edit Mode**: When `sessionIdFromUrl` exists and `isViewOnly` is `false`

**Edit Mode Indicators**:
1. **Banner Alert** (Line 1109-1113):
```tsx
{!isViewOnly && isCompleted && (
  <Alert severity="warning" sx={{ mb: 2 }}>
    <strong>Edit Mode</strong> - You are editing a completed wizard run. Changes will update the stored data.
  </Alert>
)}
```

2. **Complete Button Label** (Line 1183):
```tsx
{currentStepIndex === wizard.steps.length - 1 ? (isCompleted ? 'Update' : 'Complete') : 'Next'}
```
- Shows "Update" instead of "Complete" when editing a completed run
- Shows "Complete" for new runs

---

### 3. Complete Button Behavior in Edit Mode

**Current Behavior** (Line 1183, handleNext function):
- When user clicks "Update" button on last step:
  - Validates current step
  - Calls `completeSessionMutation` (Line 405)
  - Shows completion screen
  - Opens "Save This Run?" dialog (Line 1037)

**Required Changes**:
- ❌ **PROBLEM**: The current dialog asks "Save This Run?" which is confusing for edits
- ✅ **SOLUTION**: Need to detect edit mode and show "Update This Run" dialog instead

---

### 4. Update This Run Dialog - NEW COMPONENT

**Dialog Title**: "Update This Run"

**Dialog Description**:
```
You have made changes to this stored wizard run. How would you like to proceed?
```

**Three Action Buttons**:

#### Button 1: Skip (Do NOT Update)
- **Label**: "Skip" or "Discard Changes"
- **Icon**: CloseIcon or CancelIcon
- **Color**: Default/Secondary
- **Behavior**:
  - Do NOT save any modifications to database
  - Navigate to My Runs page (`/my-runs`)
  - Show snackbar: "Changes discarded"
  - Original run remains unchanged in database

#### Button 2: Update (Save to Current Run)
- **Label**: "Update Run"
- **Icon**: SaveIcon or UpdateIcon
- **Color**: Primary
- **Behavior**:
  - Save all modifications to the CURRENT run (same `run_id`)
  - Call existing `saveRunMutation` with `isUpdate: true`
  - Update run metadata (keep existing `run_name`)
  - Delete old responses and save new responses
  - Navigate to My Runs page (`/my-runs`)
  - Show snackbar: "Run updated successfully!"

#### Button 3: Save As (Create New Run)
- **Label**: "Save As New"
- **Icon**: AddIcon or ContentCopyIcon
- **Color**: Primary variant
- **Behavior**:
  - Show nested dialog to enter new run name
  - Create a NEW wizard run with a different `run_id`
  - Save all responses to the new run
  - Mark new run as `is_stored: true`
  - Keep original run unchanged
  - Navigate to My Runs page (`/my-runs`)
  - Show snackbar: "New run created successfully!"

---

## Implementation Details

### State Management

**New State Variables**:
```typescript
// Dialog states
const [showUpdateRunDialog, setShowUpdateRunDialog] = useState(false);
const [isEditMode, setIsEditMode] = useState(false);

// Save As nested dialog
const [showSaveAsDialog, setShowSaveAsDialog] = useState(false);
const [saveAsRunName, setSaveAsRunName] = useState('');
const [saveAsError, setSaveAsError] = useState('');
```

**Edit Mode Detection**:
```typescript
useEffect(() => {
  if (sessionIdFromUrl && !isViewOnly) {
    // Check if this is a completed run being edited
    const loadRun = async () => {
      const run = await wizardRunService.getWizardRun(sessionIdFromUrl);
      if (run.status === 'completed' && run.is_stored) {
        setIsEditMode(true);
      }
    };
    loadRun();
  }
}, [sessionIdFromUrl, isViewOnly]);
```

### Dialog Logic

**Trigger Condition** (modify handleNext at line 400):
```typescript
if (currentStepIndex === wizard.steps.length - 1) {
  // Last step - Complete wizard run
  await completeSessionMutation.mutateAsync(sessionId);

  // Show appropriate dialog based on mode
  if (isEditMode) {
    setShowUpdateRunDialog(true); // NEW: Update This Run dialog
  } else {
    setShowSessionNameDialog(true); // Existing: Save This Run dialog
  }
}
```

### Action Handlers

#### 1. Skip Handler
```typescript
const handleSkipUpdate = () => {
  setShowUpdateRunDialog(false);
  navigate('/my-runs');
  setSnackbar({
    open: true,
    message: 'Changes discarded',
    severity: 'info',
  });
};
```

#### 2. Update Handler
```typescript
const handleUpdateRun = async () => {
  if (!sessionId) return;

  try {
    // Use existing saveRunMutation with isUpdate flag
    await saveRunMutation.mutateAsync({
      runId: sessionId,
      name: existingRunName, // Keep existing name
      isUpdate: true,
    });

    setShowUpdateRunDialog(false);
    navigate('/my-runs');
    setSnackbar({
      open: true,
      message: 'Run updated successfully!',
      severity: 'success',
    });
  } catch (error) {
    setSnackbar({
      open: true,
      message: 'Failed to update run',
      severity: 'error',
    });
  }
};
```

#### 3. Save As Handler
```typescript
const handleSaveAs = () => {
  setShowUpdateRunDialog(false);
  setShowSaveAsDialog(true);
  // Pre-fill with original name + copy suffix
  setSaveAsRunName(`${existingRunName} (Copy)`);
};

const handleConfirmSaveAs = async () => {
  if (!saveAsRunName.trim()) {
    setSaveAsError('Run name is required');
    return;
  }

  try {
    // Create a NEW wizard run
    const newRun = await wizardRunService.createWizardRun({
      wizard_id: wizard!.id,
      run_name: saveAsRunName.trim(),
    });

    // Save all responses to the new run
    await saveRunMutation.mutateAsync({
      runId: newRun.id,
      name: saveAsRunName.trim(),
      isUpdate: false,
    });

    setShowSaveAsDialog(false);
    navigate('/my-runs');
    setSnackbar({
      open: true,
      message: 'New run created successfully!',
      severity: 'success',
    });
  } catch (error) {
    setSnackbar({
      open: true,
      message: 'Failed to create new run',
      severity: 'error',
    });
  }
};
```

---

## Backend Requirements

### API Endpoints (Already Exist)
All required endpoints are already implemented:

✅ `PUT /api/v1/wizard-runs/{run_id}` - Update run metadata
✅ `DELETE /api/v1/wizard-runs/{run_id}/responses` - Clear all responses
✅ `POST /api/v1/wizard-runs/{run_id}/steps` - Create step response
✅ `POST /api/v1/wizard-runs/{run_id}/option-sets` - Create option set response
✅ `POST /api/v1/wizard-runs` - Create new wizard run

### Service Layer (Already Implemented)
All required service methods exist in [wizardRun.service.ts](frontend/src/services/wizardRun.service.ts):

✅ `createWizardRun()` - Line 116
✅ `updateWizardRun()` - Line 124
✅ `clearAllResponses()` - Line 204
✅ `createStepResponse()` - Line 176
✅ `createOptionSetResponse()` - Line 215

---

## UI Components

### Update This Run Dialog
```tsx
<Dialog
  open={showUpdateRunDialog}
  onClose={() => setShowUpdateRunDialog(false)}
  maxWidth="sm"
  fullWidth
>
  <DialogTitle>Update This Run</DialogTitle>
  <DialogContent>
    <DialogContentText sx={{ mb: 2 }}>
      You have made changes to this stored wizard run. How would you like to proceed?
    </DialogContentText>

    {/* Show run info */}
    <Alert severity="info" sx={{ mb: 2 }}>
      <Typography variant="body2">
        <strong>Run Name:</strong> {existingRunName}
      </Typography>
    </Alert>
  </DialogContent>
  <DialogActions sx={{ flexDirection: 'column', gap: 1, p: 2 }}>
    {/* Button 1: Skip */}
    <Button
      onClick={handleSkipUpdate}
      variant="outlined"
      color="secondary"
      fullWidth
      startIcon={<CloseIcon />}
    >
      Skip (Discard Changes)
    </Button>

    {/* Button 2: Update */}
    <Button
      onClick={handleUpdateRun}
      variant="contained"
      color="primary"
      fullWidth
      startIcon={<SaveIcon />}
      disabled={saveRunMutation.isPending}
    >
      {saveRunMutation.isPending ? 'Updating...' : 'Update Run'}
    </Button>

    {/* Button 3: Save As */}
    <Button
      onClick={handleSaveAs}
      variant="outlined"
      color="primary"
      fullWidth
      startIcon={<ContentCopyIcon />}
    >
      Save As New Run
    </Button>
  </DialogActions>
</Dialog>
```

### Save As Dialog (Nested)
```tsx
<Dialog
  open={showSaveAsDialog}
  onClose={() => setShowSaveAsDialog(false)}
  maxWidth="sm"
  fullWidth
>
  <DialogTitle>Save As New Run</DialogTitle>
  <DialogContent>
    <DialogContentText sx={{ mb: 2 }}>
      Enter a name for the new wizard run:
    </DialogContentText>
    <TextField
      autoFocus
      margin="dense"
      label="New Run Name"
      type="text"
      fullWidth
      required
      value={saveAsRunName}
      onChange={(e) => {
        setSaveAsRunName(e.target.value);
        if (saveAsError) setSaveAsError('');
      }}
      error={!!saveAsError}
      helperText={saveAsError || 'Enter a unique name for this run'}
    />
  </DialogContent>
  <DialogActions>
    <Button onClick={() => setShowSaveAsDialog(false)}>
      Cancel
    </Button>
    <Button
      onClick={handleConfirmSaveAs}
      variant="contained"
      disabled={!saveAsRunName.trim() || saveRunMutation.isPending}
    >
      {saveRunMutation.isPending ? 'Creating...' : 'Create New Run'}
    </Button>
  </DialogActions>
</Dialog>
```

---

## Edge Cases & Validation

### 1. Concurrent Edits
**Problem**: User opens same run in two tabs
**Solution**: Backend should handle with optimistic locking or last-write-wins

### 2. Save As with Duplicate Name
**Problem**: User enters name that already exists
**Solution**: Backend validation returns error, show in `saveAsError` state

### 3. Network Failure During Save
**Problem**: Request fails mid-save
**Solution**: Already handled by existing mutation error handlers

### 4. Empty Responses
**Problem**: User clears all responses and saves
**Solution**: Existing validation in `saveRunMutation` prevents saving incomplete runs

---

## Testing Checklist

### Manual Testing Steps

1. ✅ **Navigate to My Runs**
   - Verify stored runs are displayed
   - Verify "Edit" button is visible

2. ✅ **Click Edit on a stored run**
   - Verify navigation to `/wizard/{wizardId}?session={runId}`
   - Verify "Edit Mode" banner is shown
   - Verify all responses are loaded correctly
   - Verify all fields are editable (not disabled)

3. ✅ **Make changes to responses**
   - Modify some option set values
   - Verify changes are reflected in state

4. ✅ **Navigate to last step**
   - Verify button shows "Update" instead of "Complete"

5. ✅ **Click Update button**
   - Verify "Update This Run" dialog opens (NOT "Save This Run")
   - Verify dialog shows current run name
   - Verify all 3 buttons are visible

6. ✅ **Test Button 1: Skip**
   - Click "Skip (Discard Changes)"
   - Verify navigation to `/my-runs`
   - Verify snackbar shows "Changes discarded"
   - Verify original run is unchanged in database

7. ✅ **Test Button 2: Update**
   - Click "Update Run"
   - Verify loading state on button
   - Verify API calls:
     - `DELETE /wizard-runs/{run_id}/responses`
     - `POST /wizard-runs/{run_id}/steps` (for each step)
     - `POST /wizard-runs/{run_id}/option-sets` (for each option set)
   - Verify navigation to `/my-runs`
   - Verify snackbar shows "Run updated successfully!"
   - Verify run is updated in database with new responses

8. ✅ **Test Button 3: Save As**
   - Click "Save As New Run"
   - Verify "Update This Run" dialog closes
   - Verify "Save As New Run" dialog opens
   - Verify pre-filled name is "{original_name} (Copy)"
   - Enter new run name
   - Click "Create New Run"
   - Verify API calls:
     - `POST /wizard-runs` (create new run)
     - `POST /wizard-runs/{new_run_id}/steps`
     - `POST /wizard-runs/{new_run_id}/option-sets`
   - Verify navigation to `/my-runs`
   - Verify snackbar shows "New run created successfully!"
   - Verify TWO runs exist: original (unchanged) + new copy

9. ✅ **Test Button 3: Save As with empty name**
   - Click "Save As New Run"
   - Clear the name field
   - Click "Create New Run"
   - Verify error message shows "Run name is required"
   - Verify "Create New Run" button is disabled

---

## File Changes Required

### Files to Modify
1. ✅ `frontend/src/pages/WizardPlayerPage.tsx`
   - Add new state variables
   - Add edit mode detection logic
   - Modify `handleNext` to show appropriate dialog
   - Add "Update This Run" dialog component
   - Add "Save As" nested dialog component
   - Add action handlers

### Files to Create
1. ✅ `EDIT_RUN_WORKFLOW_SPEC.md` (this file)

### Files Already Implemented (No Changes Needed)
1. ✅ `frontend/src/services/wizardRun.service.ts`
2. ✅ `frontend/src/types/wizardRun.types.ts`
3. ✅ `backend/app/api/v1/wizard_runs.py`
4. ✅ `backend/app/crud/wizard_run.py`

---

## Summary

This workflow provides users with three clear options when editing a stored wizard run:

1. **Skip**: Discard all changes and return to My Runs
2. **Update**: Save changes to the current run (destructive update)
3. **Save As**: Create a new run with changes, keep original intact (non-destructive)

The implementation leverages existing backend APIs and service methods, requiring only frontend changes to the WizardPlayerPage component.

**Key Principle**: The dialog clearly communicates what each action will do, preventing accidental data loss while providing flexibility for different use cases.
