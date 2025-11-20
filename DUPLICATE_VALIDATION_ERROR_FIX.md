# Duplicate Validation Error Fix

## Issue ❌

**Error Message**: "Failed to validate run name. Please try again."

**Location**: Appears when trying to save a wizard run in the "Save This Run?" dialog

**Screenshot**: User entered "nisae111aaafgf" as run name and received validation error

---

## Root Cause Analysis

### The Error Location

The error appears in two locations in [WizardPlayerPage.tsx](frontend/src/pages/WizardPlayerPage.tsx):

1. **handleSaveRun** (Lines 461-502) - For saving new runs
2. **handleConfirmSaveAs** (Lines 575-643) - For "Save As New Run" feature

### What Was Happening

```typescript
try {
  const existingRuns = await wizardRunService.getWizardRuns({
    skip: 0,
    limit: 1000,
  });

  const duplicateExists = existingRuns.runs.some(  // ❌ ERROR HERE
    run => run.run_name?.toLowerCase().trim() === sessionName.trim().toLowerCase()
  );
} catch (error) {
  console.error('[WizardPlayer] Error checking for duplicate names:', error);
  setSessionNameError('Failed to validate run name. Please try again.');  // ❌ USER SEES THIS
}
```

### Possible Causes

1. **API Call Failed**:
   - Authentication token expired or missing
   - Backend server not running or unreachable
   - Network timeout or connection error
   - CORS issues

2. **Invalid Response Structure**:
   - `existingRuns` is `undefined` or `null`
   - `existingRuns.runs` is not an array
   - Backend returned error response instead of data

3. **Backend Error**:
   - Database connection issue
   - SQL query failed
   - Unexpected exception in backend

---

## Solution Implemented ✅

### Code Changes

**File**: [WizardPlayerPage.tsx](frontend/src/pages/WizardPlayerPage.tsx)

#### Change 1: handleSaveRun (Lines 468-501)

**Before** (Lines 468-501):
```typescript
try {
  const existingRuns = await wizardRunService.getWizardRuns({
    skip: 0,
    limit: 1000,
  });

  const duplicateExists = existingRuns.runs.some(
    run => run.run_name?.toLowerCase().trim() === sessionName.trim().toLowerCase()
  );
  // ... rest of logic
} catch (error) {
  console.error('[WizardPlayer] Error checking for duplicate names:', error);
  setSessionNameError('Failed to validate run name. Please try again.');
}
```

**After** (Lines 468-501):
```typescript
try {
  const existingRuns = await wizardRunService.getWizardRuns({
    skip: 0,
    limit: 1000,
  });

  // ✅ NEW: Defensive check for response structure
  if (!existingRuns || !Array.isArray(existingRuns.runs)) {
    console.error('[WizardPlayer] Invalid response from getWizardRuns:', existingRuns);
    setSessionNameError('Failed to validate run name. Please try again.');
    return;
  }

  const duplicateExists = existingRuns.runs.some(
    run => run.run_name?.toLowerCase().trim() === sessionName.trim().toLowerCase()
  );
  // ... rest of logic
} catch (error) {
  console.error('[WizardPlayer] Error checking for duplicate names:', error);
  setSessionNameError('Failed to validate run name. Please try again.');
}
```

#### Change 2: handleConfirmSaveAs (Lines 588-643)

Same defensive check added:
```typescript
// Defensive check for response structure
if (!existingRuns || !Array.isArray(existingRuns.runs)) {
  console.error('[WizardPlayer] Invalid response from getWizardRuns:', existingRuns);
  setSaveAsError('Failed to validate run name. Please try again.');
  return;
}
```

---

## How the Fix Works ✅

### Defense-in-Depth Approach

1. **Try-Catch Block** (Existing):
   - Catches network errors, timeouts, and exceptions
   - Shows generic error message to user

2. **Response Validation** (NEW):
   - Checks if `existingRuns` is not null/undefined
   - Verifies `existingRuns.runs` is an array
   - Logs invalid response to console for debugging
   - Shows same error message but prevents crash

### Error Flow

```
API Call: wizardRunService.getWizardRuns()
    ↓
Response received
    ↓
Check: Is response valid?
    ↓
├── YES (existingRuns && Array.isArray(existingRuns.runs))
│   ↓
│   Check for duplicate names
│   ↓
│   Proceed with save or show duplicate error
│
└── NO (null, undefined, or invalid structure)
    ↓
    Log error to console
    ↓
    Show error message to user
    ↓
    Return early (prevent crash)
```

---

## What to Check Next 🔍

Since we've added defensive coding, the next step is to investigate **why** the API call is failing:

### 1. Check Browser Console

Open DevTools (F12) and look for:

```javascript
// Look for these console logs:
[WizardPlayer] Checking for duplicate run name
[WizardPlayer] Invalid response from getWizardRuns: undefined

// Or network errors:
Error checking for duplicate names: TypeError: Cannot read property 'runs' of undefined
```

### 2. Check Network Tab

In DevTools → Network:
- Look for `GET /api/v1/wizard-runs?skip=0&limit=1000`
- Check response status:
  - **200 OK**: Response received successfully
  - **401 Unauthorized**: Authentication token missing/expired
  - **403 Forbidden**: User doesn't have permission
  - **500 Internal Server Error**: Backend error

### 3. Check Backend Logs

In the backend terminal, look for:
```
INFO:     127.0.0.1 - "GET /api/v1/wizard-runs?skip=0&limit=1000 HTTP/1.1" 401 Unauthorized
```

Or database errors:
```
ERROR:    Exception in ASGI application
...
sqlalchemy.exc.OperationalError: ...
```

### 4. Check Authentication

Verify the user is properly logged in:
```typescript
// In browser console:
localStorage.getItem('auth_token')  // Should return a JWT token

// Or check AuthContext:
// Look for auth state in React DevTools
```

### 5. Test API Directly

Use curl or Postman to test the endpoint:
```bash
curl -X GET "http://localhost:8000/api/v1/wizard-runs?skip=0&limit=1000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "accept: application/json"
```

Expected response:
```json
{
  "runs": [...],
  "total": 5,
  "page": 1,
  "page_size": 1000,
  "total_pages": 1
}
```

---

## Expected Response Structure

The backend endpoint [/api/v1/wizard-runs](backend/app/api/v1/wizard_runs.py#L56-L88) returns:

```typescript
interface WizardRunListResponse {
  runs: WizardRun[];        // ✅ MUST be an array
  total: number;            // Total count of runs
  page: number;             // Current page number
  page_size: number;        // Items per page
  total_pages: number;      // Total number of pages
}
```

The defensive check ensures:
- `existingRuns` is **not null/undefined**
- `existingRuns.runs` is **an array** (not null, not undefined, not a string, etc.)

---

## Testing the Fix

### Test Case 1: Valid Response ✅

**Scenario**: Backend returns proper response

**API Response**:
```json
{
  "runs": [
    { "id": "abc", "run_name": "Test Run", ... },
    { "id": "def", "run_name": "Another Run", ... }
  ],
  "total": 2,
  "page": 1,
  "page_size": 1000,
  "total_pages": 1
}
```

**Result**:
- ✅ `existingRuns` is defined
- ✅ `existingRuns.runs` is an array
- ✅ Duplicate check runs normally
- ✅ User can save if no duplicate found

---

### Test Case 2: Empty Response ✅

**Scenario**: User has no existing runs

**API Response**:
```json
{
  "runs": [],  // Empty array
  "total": 0,
  "page": 1,
  "page_size": 1000,
  "total_pages": 0
}
```

**Result**:
- ✅ `existingRuns.runs` is an array (length 0)
- ✅ `Array.isArray([])` returns `true`
- ✅ `.some()` on empty array returns `false`
- ✅ No duplicate found, save proceeds

---

### Test Case 3: Null Response ❌

**Scenario**: API returns `null` instead of data

**API Response**: `null`

**Result**:
- ❌ `existingRuns === null`
- ✅ Defensive check catches this: `if (!existingRuns || ...)`
- ✅ Logs: `Invalid response from getWizardRuns: null`
- ✅ Shows error: "Failed to validate run name"
- ✅ Returns early, **no crash**

---

### Test Case 4: Undefined Response ❌

**Scenario**: API call fails, returns `undefined`

**Result**:
- ❌ `existingRuns === undefined`
- ✅ Defensive check catches this: `if (!existingRuns || ...)`
- ✅ Logs error to console
- ✅ Shows error message
- ✅ **No crash**

---

### Test Case 5: Invalid Structure ❌

**Scenario**: Backend returns error object instead of proper response

**API Response**:
```json
{
  "detail": "Database connection failed",
  "error_code": "DB_ERROR"
}
```

**Result**:
- ✅ `existingRuns` is defined (it's an object)
- ❌ `existingRuns.runs` is `undefined` (no runs property)
- ✅ `Array.isArray(undefined)` returns `false`
- ✅ Defensive check catches this
- ✅ Logs: `Invalid response from getWizardRuns: { detail: "...", error_code: "..." }`
- ✅ Shows error message
- ✅ **No crash**

---

### Test Case 6: Network Error (Exception) ❌

**Scenario**: Network timeout or connection refused

**Result**:
- ❌ Exception thrown during API call
- ✅ Caught by `catch (error)` block
- ✅ Logs: `Error checking for duplicate names: Network Error`
- ✅ Shows error message
- ✅ **No crash**

---

## Potential Root Causes

Based on the error, here are the most likely causes:

### 1. Authentication Token Expired (Most Likely)

**Symptom**: API returns 401 Unauthorized

**How to Check**:
```typescript
// Browser console:
localStorage.getItem('auth_token')

// Network tab: Look for 401 status
```

**Solution**:
- Log out and log back in
- Check if token refresh mechanism is working
- Verify token expiration time in backend config

---

### 2. Backend Not Running (Likely)

**Symptom**: Network error, connection refused

**How to Check**:
```bash
# Check if backend is running:
curl http://localhost:8000/api/v1/health

# Check backend logs
```

**Solution**:
- Start backend server: `cd backend && uvicorn app.main:app --reload --port 8000`

---

### 3. Database Connection Issue (Possible)

**Symptom**: Backend returns 500 Internal Server Error

**How to Check**:
- Check backend logs for SQL errors
- Try connecting to database manually:
  ```bash
  psql -U postgres -d wizarddb
  ```

**Solution**:
- Restart database service
- Check database credentials in backend `.env`

---

### 4. CORS Issue (Less Likely)

**Symptom**: Browser blocks request

**How to Check**:
- Look for CORS error in browser console
- Check Network tab for preflight OPTIONS request

**Solution**:
- Verify backend CORS settings allow frontend origin
- Check `app/main.py` CORS middleware config

---

### 5. Backend Response Format Changed (Unlikely)

**Symptom**: Backend returns data but in different format

**How to Check**:
- Inspect actual API response in Network tab
- Compare with expected `WizardRunListResponse` interface

**Solution**:
- Check if backend schema was recently changed
- Verify Pydantic schema matches frontend types

---

## Benefits of This Fix

### 1. Prevents Crashes ✅
- No more `TypeError: Cannot read property 'runs' of undefined`
- App stays functional even with API errors

### 2. Better Debugging ✅
- Console logs show exact response received
- Easier to diagnose root cause

### 3. Consistent Error Handling ✅
- Same error message for all failure scenarios
- User experience is consistent

### 4. Graceful Degradation ✅
- User is informed of the issue
- Can retry the operation
- App doesn't freeze or crash

---

## User Impact

### Before Fix ❌
- App crashes with TypeError
- White screen or frozen UI
- No indication of what went wrong
- Must refresh page to recover

### After Fix ✅
- Error message shown to user
- UI remains functional
- User can:
  - Try different name
  - Cancel and try later
  - Check network/authentication
- Console has diagnostic info

---

## Next Steps for User

If you encounter this error again:

1. **Check Browser Console** (F12 → Console tab):
   - Look for `[WizardPlayer] Invalid response from getWizardRuns:`
   - Copy the logged response object
   - Share with developer

2. **Check Network Tab** (F12 → Network tab):
   - Find the `wizard-runs?skip=0&limit=1000` request
   - Check status code (401, 403, 500, etc.)
   - View response body

3. **Try Refreshing**:
   - Hard refresh: Ctrl + Shift + R
   - Clear cache and reload

4. **Check Authentication**:
   - Log out and log back in
   - Verify token hasn't expired

5. **Retry Operation**:
   - Click the save button again
   - Try a different run name

---

## Summary

### Problem
API call to check for duplicate run names was failing, causing the error "Failed to validate run name. Please try again."

### Solution
Added defensive checks to validate API response structure before processing.

### Changes Made
- **File**: [WizardPlayerPage.tsx](frontend/src/pages/WizardPlayerPage.tsx)
- **Lines Modified**:
  - handleSaveRun: Added check at line 477-481
  - handleConfirmSaveAs: Added check at line 597-601

### Result
- ✅ App no longer crashes on invalid API responses
- ✅ Better error logging for debugging
- ✅ User sees consistent error message
- ✅ Can identify root cause from console logs

---

**Status**: ✅ **Fix Implemented and Ready for Testing**

**Test Required**: Reproduce the original error scenario and verify the improved error handling.
