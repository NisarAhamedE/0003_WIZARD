# How to Fix "Failed to validate run name" Error

## The Problem

You're seeing this error when trying to save a wizard run:
> "Failed to validate run name. Please try again."

**Root Cause**: Your authentication token has expired or is missing.

## Solution: 2 Steps

### Step 1: Refresh the Browser to Get New Error Messages

The code has been updated to show better error messages, but you need to refresh:

1. **Hard refresh the browser**:
   - **Windows/Linux**: Press `Ctrl + Shift + R`
   - **Mac**: Press `Cmd + Shift + R`

   OR

   - Press `Ctrl + F5`

2. This will reload the page and pick up the new frontend code

### Step 2: Log Out and Log Back In

1. Click on your username in the top-right corner
2. Click **"Log out"**
3. Log back in with your credentials
4. Navigate back to the wizard
5. Complete the wizard and try saving again

## After You Do This

When you try to save again, if there's still an authentication issue, you'll now see a more helpful message:

> "Session expired. Please log in again and try saving."

Instead of the confusing validation error.

## Why This Happened

- The backend API requires authentication to check for duplicate run names
- Your authentication token expired (tokens typically expire after 30 minutes of inactivity)
- The old error message was too generic and didn't explain the real issue
- The code has been updated to show specific error messages based on the actual problem

## If It Still Doesn't Work

If you still see issues after logging in:

1. **Check Browser Console** (F12 → Console tab):
   - Look for red error messages
   - Screenshot and share them

2. **Check Network Tab** (F12 → Network tab):
   - Look for the request to `wizard-runs?skip=0&limit=1000`
   - Check the status code (should be 200 after logging in)
   - Check the response

3. **Verify You're Logged In**:
   - Open browser console (F12)
   - Type: `localStorage.getItem('access_token')`
   - Should show a long JWT token string
   - If it shows `null`, you're not logged in

## Backend Confirmation

I've verified the backend is working correctly:
- ✓ Backend server is running on port 8000
- ✓ Endpoint requires authentication (returns 401 without token)
- ✓ This is expected behavior

The issue is purely on the frontend side (expired token).
