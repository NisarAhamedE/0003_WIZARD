# Save Run Validation Error - Improved Error Handling

## Issue

When trying to save a wizard run, users were seeing the generic error message:
> "Failed to validate run name. Please try again."

This error appeared even though the issue was often **authentication-related** (expired session) or a **network connectivity problem**, not an actual run name validation issue.

## Root Cause

The error occurred in the `handleSaveRun` and `handleConfirmSaveAs` functions when:

1. **Authentication token expired** (401 Unauthorized)
2. **Network connection issues** (ECONNREFUSED, Network Error)
3. **Permission issues** (403 Forbidden)
4. **Backend server not responding**
5. **Invalid API response structure**

The original code caught all errors with a generic message, making it difficult for users to understand what actually went wrong.

## Solution Implemented

### Enhanced Error Messages

Updated error handling in two locations to provide **specific, actionable error messages**:

#### 1. `handleSaveRun` Function (Lines 498-513)

**Before:**
```typescript
} catch (error) {
  console.error('[WizardPlayer] Error checking for duplicate names:', error);
  setSessionNameError('Failed to validate run name. Please try again.');
}
```

**After:**
```typescript
} catch (error: any) {
  console.error('[WizardPlayer] Error checking for duplicate names:', error);

  // Provide more specific error messages based on error type
  if (error.response?.status === 401) {
    setSessionNameError('Session expired. Please log in again and try saving.');
  } else if (error.response?.status === 403) {
    setSessionNameError('You do not have permission to access this resource.');
  } else if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
    setSessionNameError('Unable to connect to server. Please check your connection.');
  } else if (!error.response) {
    setSessionNameError('Network error. Please check your internet connection.');
  } else {
    setSessionNameError('Failed to validate run name. Please try again.');
  }
}
```

#### 2. `handleConfirmSaveAs` Function (Lines 651-674)

**Before:**
```typescript
} catch (error: any) {
  console.error('[WizardPlayer] Failed to create new run:', error);
  setSnackbar({
    open: true,
    message: error.message || 'Failed to create new run',
    severity: 'error',
  });
}
```

**After:**
```typescript
} catch (error: any) {
  console.error('[WizardPlayer] Failed to create new run:', error);

  // Provide more specific error messages
  let errorMessage = 'Failed to create new run';
  if (error.response?.status === 401) {
    errorMessage = 'Session expired. Please log in again and try saving.';
  } else if (error.response?.status === 403) {
    errorMessage = 'You do not have permission to create runs.';
  } else if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
    errorMessage = 'Unable to connect to server. Please check your connection.';
  } else if (!error.response) {
    errorMessage = 'Network error. Please check your internet connection.';
  } else if (error.message) {
    errorMessage = error.message;
  }

  setSaveAsError(errorMessage);
  setSnackbar({
    open: true,
    message: errorMessage,
    severity: 'error',
  });
}
```

## Error Message Matrix

| HTTP Status / Error Type | User-Friendly Message | User Action Required |
|-------------------------|----------------------|---------------------|
| **401 Unauthorized** | "Session expired. Please log in again and try saving." | Log out and log back in |
| **403 Forbidden** | "You do not have permission to access this resource." | Contact admin for access |
| **ECONNREFUSED** | "Unable to connect to server. Please check your connection." | Verify backend is running |
| **Network Error** | "Network error. Please check your internet connection." | Check internet connection |
| **No Response** | "Network error. Please check your internet connection." | Check connectivity |
| **Other Errors** | "Failed to validate run name. Please try again." | Try again or contact support |

## Benefits

### 1. **User Experience** ✅
- Users immediately understand what went wrong
- Clear guidance on how to fix the issue
- No confusion about "validation" when it's actually authentication

### 2. **Faster Problem Resolution** ✅
- Users can self-diagnose authentication issues
- Reduces support tickets for common issues
- Easier to identify network vs. server issues

### 3. **Better Debugging** ✅
- Console logs still capture full error details
- Error type checking helps identify root cause
- Maintains existing defensive checks

## Common Scenarios

### Scenario 1: Expired Session (Most Common)

**What User Sees:**
```
Session expired. Please log in again and try saving.
```

**Solution:**
1. Click "Skip" to close the save dialog
2. Log out from the application
3. Log back in with your credentials
4. Navigate back to the wizard
5. Try saving again

---

### Scenario 2: Backend Server Not Running

**What User Sees:**
```
Unable to connect to server. Please check your connection.
```

**Solution:**
1. Verify backend server is running on port 8000
2. Check backend logs for errors
3. Restart backend if needed:
   ```bash
   cd backend
   venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
   ```

---

### Scenario 3: Internet Connection Issue

**What User Sees:**
```
Network error. Please check your internet connection.
```

**Solution:**
1. Check your internet connection
2. Verify you can access other websites
3. Try refreshing the page (Ctrl + Shift + R)
4. Check if localhost is accessible

---

### Scenario 4: Actual Duplicate Run Name

**What User Sees:**
```
A run with this name already exists. Please choose a different name.
```

**Solution:**
1. Enter a different, unique run name
2. Try adding a number or date to make it unique
3. Click "Save Run" again

---

## Testing

### Test Case 1: Expired Token
1. Log in to the application
2. Manually delete `localStorage.getItem('access_token')` in browser console
3. Try to save a wizard run
4. **Expected**: "Session expired. Please log in again and try saving."

### Test Case 2: Backend Down
1. Stop the backend server
2. Try to save a wizard run
3. **Expected**: "Unable to connect to server. Please check your connection."

### Test Case 3: Valid Save
1. Ensure user is logged in
2. Backend is running
3. Enter a unique run name
4. **Expected**: Run saves successfully

### Test Case 4: Duplicate Name
1. Create a run with name "Test Run"
2. Try to create another run with name "Test Run"
3. **Expected**: "A run with this name already exists. Please choose a different name."

---

## Files Modified

- **[frontend/src/pages/WizardPlayerPage.tsx](frontend/src/pages/WizardPlayerPage.tsx)**
  - Lines 498-513: Updated `handleSaveRun` error handling
  - Lines 651-674: Updated `handleConfirmSaveAs` error handling
  - Lines 608-612: Improved defensive check error message

---

## Backward Compatibility

✅ **Fully backward compatible**
- All existing error handling preserved
- Console logging maintained for debugging
- Defensive checks still in place
- No breaking changes to API or types

---

## Additional Improvements Made

1. **Response Structure Check**: Enhanced error message when API returns invalid structure
   ```typescript
   if (!existingRuns || !Array.isArray(existingRuns.runs)) {
     console.error('[WizardPlayer] Invalid response from getWizardRuns:', existingRuns);
     setSaveAsError('Unable to validate run name. Please check your connection and try again.');
     return;
   }
   ```

2. **TypeScript Type Safety**: Changed `error` to `error: any` to access response properties safely

3. **Consistent Error Display**: Both dialog errors and snackbar errors now use the same logic

---

## Next Steps for Debugging

If a user reports this issue, ask them to:

1. **Check Browser Console** (F12 → Console):
   ```javascript
   // Look for these logs:
   [WizardPlayer] Error checking for duplicate names: ...
   ```

2. **Check Network Tab** (F12 → Network):
   - Find: `GET /api/v1/wizard-runs?skip=0&limit=1000`
   - Check: Response status code (200, 401, 403, 500, etc.)
   - View: Response body

3. **Verify Authentication**:
   ```javascript
   // In browser console:
   localStorage.getItem('access_token')  // Should return a JWT token
   ```

4. **Test API Directly**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/wizard-runs?skip=0&limit=1000" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

---

## Summary

### Problem
Generic error message "Failed to validate run name" appeared for all types of errors, confusing users and making debugging difficult.

### Solution
Implemented specific error messages based on error type (401, 403, network errors, etc.) with clear instructions for users.

### Result
- ✅ Better user experience with actionable error messages
- ✅ Faster problem diagnosis and resolution
- ✅ Reduced confusion about authentication vs. validation issues
- ✅ Maintained all existing error handling and defensive checks

---

**Status**: ✅ **Implemented and Ready for Testing**

**File**: [frontend/src/pages/WizardPlayerPage.tsx](frontend/src/pages/WizardPlayerPage.tsx)

**Test**: Try saving a run after logging out or stopping the backend to verify improved error messages.
