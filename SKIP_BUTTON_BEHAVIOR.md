# Skip Button Behavior - Technical Explanation

## Overview
The "Skip (Discard Changes)" button in the "Update This Run" dialog allows users to exit the edit workflow **without saving any modifications** and **without deleting the run**.

---

## How It Works

### Implementation
**File**: [WizardPlayerPage.tsx:487-496](frontend/src/pages/WizardPlayerPage.tsx#L487-L496)

```typescript
const handleSkipUpdate = () => {
  console.log('[WizardPlayer] Skip update - discarding changes');
  setShowUpdateRunDialog(false);  // Close dialog
  navigate('/my-runs');            // Navigate to My Runs
  setSnackbar({
    open: true,
    message: 'Changes discarded',
    severity: 'info',
  });
};
```

### What Happens When You Click Skip

1. **Dialog Closes** - `setShowUpdateRunDialog(false)`
2. **Navigation** - User is redirected to `/my-runs` page
3. **Notification** - Info snackbar shows "Changes discarded"
4. **No API Calls** - Zero network requests made
5. **Run Preserved** - Original run remains in database unchanged

---

## Data Flow Explanation

### Edit Workflow Data States

#### 1. Initial State (Before Edit)
```
Database (Run #123):
  run_name: "Test Run"
  responses: [A, B, C]  ← Original responses
  status: completed
  is_stored: true
```

#### 2. Edit Mode (User Making Changes)
```
Database (Run #123):
  responses: [A, B, C]  ← Still original (unchanged)

Memory (Frontend State):
  responses: [X, Y, Z]  ← Modified in state only
```

#### 3. Click Skip Button
```
Action: handleSkipUpdate()
  - Close dialog
  - Navigate to /my-runs
  - No API calls

Result:
  Database (Run #123):
    responses: [A, B, C]  ← Still original ✅

  Memory (Frontend State):
    responses: [X, Y, Z]  ← Discarded (user navigated away)
```

#### 4. My Runs Page Shows
```
Run #123 displayed with:
  run_name: "Test Run"
  responses: [A, B, C]  ← Original responses preserved ✅
  status: completed
```

---

## Why the Run Is NOT Deleted

### Key Principle: Separation of State
- **Frontend State**: Changes are stored in React state (`responses` object)
- **Backend State**: Original run data remains in PostgreSQL database
- **No Auto-Save**: Changes are NOT auto-saved to database

### Skip Button Logic
```typescript
// ❌ Does NOT do this:
await wizardRunService.deleteWizardRun(sessionId);

// ❌ Does NOT do this:
await wizardRunService.updateWizardRun(sessionId, {...});

// ✅ ONLY does this:
navigate('/my-runs');
```

### Result
Since there are **zero API calls**, the database is never touched, and the run persists with its original data.

---

## Comparison: Skip vs Update vs Save As

### Skip Button
- **Action**: Discard all changes
- **API Calls**: 0
- **Database Changes**: None
- **Result**: Original run unchanged in My Runs
- **Run Preserved**: ✅ Yes

### Update Button
- **Action**: Save modifications to current run
- **API Calls**: 5+ (delete old responses, save new ones)
- **Database Changes**: Overwrites existing responses
- **Result**: Run #123 updated with new data
- **Run Preserved**: ✅ Yes (but modified)

### Save As Button
- **Action**: Create new run with modifications
- **API Calls**: 4+ (create run, save responses)
- **Database Changes**: New run created
- **Result**: 2 runs exist (original + new copy)
- **Run Preserved**: ✅ Yes (and duplicated)

---

## User Journey: Edit → Skip

### Step-by-Step

1. **My Runs Page**
   ```
   [Run #123: Test Run]
   Status: Completed
   Responses: A, B, C
   [Edit Button]
   ```

2. **Click Edit**
   - Navigate to `/wizard/456?session=123`
   - Load original responses: A, B, C
   - Edit mode banner shown

3. **Make Changes**
   - User changes A → X
   - User changes B → Y
   - User changes C → Z
   - Changes stored in `responses` state only

4. **Navigate to Last Step**
   - Click "Update" button (not "Complete")
   - "Update This Run" dialog opens

5. **Click Skip Button**
   - Dialog closes
   - Navigate to `/my-runs`
   - Snackbar: "Changes discarded"

6. **My Runs Page (After Skip)**
   ```
   [Run #123: Test Run]  ← Still there! ✅
   Status: Completed
   Responses: A, B, C    ← Original responses! ✅
   [Edit Button]         ← Can edit again
   ```

---

## Console Verification

### When Skip is Clicked
```
[WizardPlayer] Skip update - discarding changes
```

### Network Tab (Chrome DevTools)
```
No requests made ✅
```

### Database Query
```sql
-- Before Edit
SELECT id, run_name, status FROM wizard_runs WHERE id = '123';
-- Result: 123 | Test Run | completed

-- After Skip
SELECT id, run_name, status FROM wizard_runs WHERE id = '123';
-- Result: 123 | Test Run | completed ✅ (unchanged)
```

---

## Code Review: Why Skip Doesn't Delete

### handleSkipUpdate Function Analysis

```typescript
const handleSkipUpdate = () => {
  // 1. Log action (debugging only)
  console.log('[WizardPlayer] Skip update - discarding changes');

  // 2. Close the dialog
  setShowUpdateRunDialog(false);

  // 3. Navigate to My Runs page
  navigate('/my-runs');

  // 4. Show notification
  setSnackbar({
    open: true,
    message: 'Changes discarded',
    severity: 'info',
  });

  // ✅ No API calls to:
  //   - wizardRunService.deleteWizardRun()
  //   - wizardRunService.updateWizardRun()
  //   - wizardRunService.clearAllResponses()
  //   - Any other mutation
};
```

### Comparison: handleDeleteRun (in MyRunsPage)

For contrast, here's what a DELETE actually looks like:

```typescript
// This is in MyRunsPage.tsx, NOT called by Skip button
const confirmDelete = async () => {
  try {
    setDeleting(true);
    await wizardRunService.deleteWizardRun(runToDelete.id); // ← Actually deletes!
    // ... rest of logic
  }
};
```

**Key Difference**: Skip button does NOT call `deleteWizardRun()` at all.

---

## Edge Cases

### What if user refreshes during edit?
- Changes in state are lost
- Original run still exists in database
- Can edit again from My Runs

### What if user navigates away without clicking anything?
- Same as Skip - changes discarded
- Run preserved in database

### What if network fails during edit?
- Skip button still works (no network needed)
- Run remains in database

### What if two users edit the same run?
- Each has their own `responses` state
- Skip button discards local changes only
- Last person to click "Update" wins

---

## Testing Skip Button

### Manual Test
1. Go to My Runs
2. Note the run name and responses
3. Click Edit
4. Make changes to several fields
5. Navigate to last step
6. Click "Update" button
7. Click "Skip (Discard Changes)" button
8. Verify:
   - ✅ Returned to My Runs page
   - ✅ Run still exists with same name
   - ✅ Snackbar shows "Changes discarded"
   - ✅ Click Edit again - original responses still there

### Automated Test (Future)
```typescript
describe('Skip Button', () => {
  it('should discard changes without deleting run', async () => {
    const { getByText, queryByText } = render(<WizardPlayerPage />);

    // Make changes
    fireEvent.change(input, { target: { value: 'new value' } });

    // Click Update, then Skip
    fireEvent.click(getByText('Update'));
    fireEvent.click(getByText('Skip (Discard Changes)'));

    // Verify navigation
    expect(mockNavigate).toHaveBeenCalledWith('/my-runs');

    // Verify no API calls
    expect(wizardRunService.deleteWizardRun).not.toHaveBeenCalled();
    expect(wizardRunService.updateWizardRun).not.toHaveBeenCalled();
  });
});
```

---

## Summary

### Skip Button Guarantees

✅ **Run is NOT deleted** - Zero deletion API calls
✅ **Run is NOT modified** - Zero update API calls
✅ **Run persists in My Runs** - Database unchanged
✅ **Original responses preserved** - Can re-edit anytime
✅ **Safe operation** - No data loss risk
✅ **Instant feedback** - Snackbar confirms action

### User Mental Model

> "Skip means: Close the wizard and throw away my edits. The original run stays exactly as it was before I clicked Edit."

This is a **non-destructive, safe exit** from the edit workflow.
