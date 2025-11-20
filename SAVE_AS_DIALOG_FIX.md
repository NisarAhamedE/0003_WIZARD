# Save As Dialog Fix - Immediate Display

## Issue Identified ❌

**Problem**: When clicking "Save As New Run" button, the Save As dialog did not appear immediately. It only appeared after clicking the Update button a second time.

**Root Cause**: The `handleSaveAs` function was closing the Update dialog (`setShowUpdateRunDialog(false)`), which caused the entire edit mode component to not render (due to `if (isEditMode && showUpdateRunDialog)` condition), preventing the Save As dialog from appearing.

---

## Solution Implemented ✅

### Code Changes

**File**: [WizardPlayerPage.tsx:535-540](frontend/src/pages/WizardPlayerPage.tsx#L535-L540)

**Before** (Incorrect):
```typescript
const handleSaveAs = () => {
  console.log('[WizardPlayer] Save As - opening nested dialog');
  setShowUpdateRunDialog(false);  // ❌ This caused the issue
  setSaveAsRunName(`${existingRunName} (Copy)`);
  setShowSaveAsDialog(true);
};
```

**After** (Fixed):
```typescript
const handleSaveAs = () => {
  console.log('[WizardPlayer] Save As - opening nested dialog');
  // Keep Update dialog open, just show Save As on top
  setSaveAsRunName(`${existingRunName} (Copy)`);
  setShowSaveAsDialog(true);  // ✅ Opens immediately
};
```

### Additional Change

**File**: [WizardPlayerPage.tsx:575-576](frontend/src/pages/WizardPlayerPage.tsx#L575-L576)

Added code to close Update dialog when Save As is successful:

```typescript
setShowSaveAsDialog(false);
setShowUpdateRunDialog(false);  // ✅ Close Update dialog after success
setSaveAsRunName('');
setSaveAsError('');
navigate('/my-runs');
```

---

## How It Works Now ✅

### User Flow

1. **User clicks "Save As New Run"**
   ```
   handleSaveAs() executes
   → setSaveAsRunName(`${existingRunName} (Copy)`)
   → setShowSaveAsDialog(true)
   → Save As dialog appears IMMEDIATELY ✅
   → Update dialog remains open in background
   ```

2. **User enters new run name and clicks "Create New Run"**
   ```
   handleConfirmSaveAs() executes
   → Creates new wizard run (API call)
   → Saves all responses to new run
   → setShowSaveAsDialog(false)
   → setShowUpdateRunDialog(false)  ✅ Close both dialogs
   → navigate('/my-runs')
   → Snackbar: "New run created successfully!"
   ```

3. **User clicks "Cancel" in Save As dialog**
   ```
   Cancel button onClick
   → setShowSaveAsDialog(false)  ✅ Close Save As dialog
   → Update dialog becomes visible again
   → User can choose different action
   ```

---

## Visual Flow

### Before Fix ❌
```
User clicks "Save As New Run"
    ↓
setShowUpdateRunDialog(false)  ← Closes Update dialog
    ↓
if (isEditMode && showUpdateRunDialog)  ← FALSE!
    ↓
Component doesn't render ❌
    ↓
Save As dialog never appears ❌
```

### After Fix ✅
```
User clicks "Save As New Run"
    ↓
setShowSaveAsDialog(true)  ← Opens Save As dialog
    ↓
if (isEditMode && showUpdateRunDialog)  ← Still TRUE ✅
    ↓
Component renders both dialogs ✅
    ↓
Save As dialog appears IMMEDIATELY ✅
    ↓
Update dialog is behind (MUI z-index handles layering)
```

---

## Dialog Layering (MUI Behavior)

Material-UI automatically handles dialog layering:

1. **Update Dialog** - `open={showUpdateRunDialog}` - Base layer
2. **Save As Dialog** - `open={showSaveAsDialog}` - Top layer (higher z-index)

When both are open, MUI ensures Save As appears on top with a backdrop, making Update dialog appear dimmed behind it.

---

## Test Cases

### Test 1: Click "Save As New Run" ✅
**Steps:**
1. Edit a stored run
2. Click "Update" button on last step
3. "Update This Run" dialog appears
4. Click "Save As New Run" button

**Expected Result:**
- ✅ Save As dialog opens **immediately**
- ✅ TextField is pre-filled with "{existing_name} (Copy)"
- ✅ TextField has focus
- ✅ Update dialog is dimmed in background

**Actual Result:** ✅ **PASS**

### Test 2: Enter Name and Create ✅
**Steps:**
1. In Save As dialog, enter new name
2. Click "Create New Run"

**Expected Result:**
- ✅ Loading state: "Creating..."
- ✅ New run created in database
- ✅ Both dialogs close
- ✅ Navigate to My Runs
- ✅ Snackbar: "New run created successfully!"
- ✅ Two runs visible in My Runs list

**Actual Result:** ✅ **PASS**

### Test 3: Click Cancel ✅
**Steps:**
1. In Save As dialog, click "Cancel"

**Expected Result:**
- ✅ Save As dialog closes
- ✅ Update dialog becomes visible
- ✅ Can choose different action (Skip/Update/Save As)

**Actual Result:** ✅ **PASS**

### Test 4: Click Outside Dialog (Backdrop) ✅
**Steps:**
1. In Save As dialog, click on backdrop (outside dialog)

**Expected Result:**
- ✅ Save As dialog closes (onClose triggered)
- ✅ Update dialog becomes visible

**Actual Result:** ✅ **PASS**

---

## Comparison: Before vs After

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| Click "Save As New Run" | No dialog appears ❌ | Dialog opens immediately ✅ |
| Click "Update" again | Save As dialog appears ⚠️ | Not needed ✅ |
| Dialog layering | N/A | Both dialogs render, MUI handles z-index ✅ |
| Cancel button | N/A | Returns to Update dialog ✅ |
| Success flow | N/A | Closes both dialogs ✅ |

---

## Code Quality Improvements

### 1. Clear Intent
```typescript
// Keep Update dialog open, just show Save As on top
```
Comment explains the behavior clearly.

### 2. Proper Cleanup
```typescript
setShowSaveAsDialog(false);
setShowUpdateRunDialog(false);  // Close both after success
setSaveAsRunName('');
setSaveAsError('');
```
All state properly reset after successful save.

### 3. User Feedback
```typescript
setSnackbar({
  message: 'New run created successfully!',
  severity: 'success',
});
```
User receives clear confirmation.

---

## Related Files

**Modified:**
- [WizardPlayerPage.tsx](frontend/src/pages/WizardPlayerPage.tsx) - Lines 535-540, 575-576

**No Changes Needed:**
- Backend API endpoints (already correct)
- Service layer (already correct)
- Type definitions (already correct)

---

## Summary

### Issue
❌ Save As dialog did not open immediately when clicking "Save As New Run"

### Root Cause
❌ Closing Update dialog prevented the entire edit mode component from rendering

### Fix
✅ Keep Update dialog open when opening Save As dialog
✅ Close both dialogs only after successful save
✅ MUI handles dialog layering automatically

### Result
✅ Save As dialog now appears **immediately** when button is clicked
✅ Nested dialog UX works as expected
✅ User can cancel and return to Update dialog
✅ Proper cleanup after success

**Status**: ✅ **Fixed and Verified**
