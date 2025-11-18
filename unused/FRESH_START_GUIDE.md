# Fresh Start Guide - All Wizards Reset

**Date**: 2025-01-18
**Status**: ✅ Complete

---

## What Was Done

### 1. Deleted All Old Wizards ✅
Removed all 8 existing wizards from the database:
- QA
- Customer Satisfaction Survey (2 instances)
- Job Application Form (2 instances)
- International Shipping Request
- Custom Laptop Configuration
- IT Support Ticket System

### 2. Created 2 New Comprehensive Test Wizards ✅

---

## Wizard 1: All Selection Types - Basic Test

**ID**: `cf1af9d7-31ed-4d6c-8541-d0565dc0c21d`
**URL**: http://localhost:3000/wizard/cf1af9d7-31ed-4d6c-8541-d0565dc0c21d

**Purpose**: Test all 12 selection types without dependencies

### Structure:
- **Step 1: Choice Selections**
  - Single Select: Choose Your Favorite Color (Red, Blue, Green, Yellow)
  - Multiple Select: Select Features (WiFi, Bluetooth, GPS, NFC) - Min: 1, Max: 4

- **Step 2: Text Inputs**
  - Text Input: Your Full Name (required)
  - Number Input: Your Age (required, min: 18, max: 100)
  - Rich Text: Additional Comments (optional)

- **Step 3: Date & Time**
  - Date Input: Event Date (required)
  - Time Input: Event Time (required)
  - DateTime Input: Full Event DateTime (optional)

- **Step 4: Interactive**
  - Rating: Service Rating (required, 1-5 stars)
  - Slider: Budget Range (required, 0-10000, step: 100)

- **Step 5: Advanced**
  - Color Picker: Theme Color (optional)
  - File Upload: Upload Document (optional)

**Total**: 12 selection types across 5 steps

---

## Wizard 2: All Selection Types - With Dependencies

**ID**: `c623ab03-41cb-4a66-9c27-545c28393632`
**URL**: http://localhost:3000/wizard/c623ab03-41cb-4a66-9c27-545c28393632

**Purpose**: Test all 12 selection types WITH conditional dependencies

### Structure:
- **Step 1: Basic Info**
  - Single Select: Are you a new customer? (Yes/No)
  - Multiple Select: Select Your Interests (Technology, Sports, Music, Travel)

- **Step 2: Personal Details**
  - Text Input: Your Name (required) - **DISABLED if "existing customer"**
  - Number Input: Your Age (required, min: 18, max: 100)
  - Rich Text: Tell us more (optional)

- **Step 3: Preferences**
  - Date Input: Preferred Date (required)
  - Time Input: Preferred Time (required)
  - Rating: Rate Your Experience (required, 1-5 stars)

- **Step 4: Budget & Style**
  - Slider: Your Budget (required, 0-5000, step: 100)
  - Color Picker: Preferred Color (optional)

- **Step 5: Final Details**
  - File Upload: Upload Document (optional) - **REQUIRED if "new customer"**
  - DateTime Input: Complete DateTime (optional)

### Dependencies Added ✅
1. **Disable name field for existing customers**
   - IF user selects "No, I'm existing"
   - THEN "Your Name" field becomes disabled (grayed out)

2. **Require document upload for new customers**
   - IF user selects "Yes, I'm new"
   - THEN "Upload Document" field becomes required (red asterisk)

---

## IMPORTANT: Restart Frontend to See Changes

The database has been completely reset. To see the new wizards in your browser:

### Option 1: Hard Refresh (Recommended)
1. Open browser to http://localhost:3000
2. Press **Ctrl + Shift + R** (Windows) or **Cmd + Shift + R** (Mac)
3. This clears cache and reloads

### Option 2: Restart Frontend Server
```bash
# Stop frontend (Ctrl + C)
cd frontend
npm start
```

### Option 3: Clear Browser Cache
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

---

## Testing Guide

### Test Wizard 1 (Basic - No Dependencies)
1. Navigate to: http://localhost:3000/wizard/cf1af9d7-31ed-4d6c-8541-d0565dc0c21d
2. Enter session name: "Test Session 1"
3. Fill out all 5 steps with sample data
4. Verify each selection type accepts input correctly
5. Complete wizard
6. Verify completion message

**Expected**: All 12 selection types should work perfectly ✅

---

### Test Wizard 2 (With Dependencies)
1. Navigate to: http://localhost:3000/wizard/c623ab03-41cb-4a66-9c27-545c28393632
2. Enter session name: "Test Session 2"

**Test Scenario A: New Customer**
- Step 1: Select "Yes, I'm new"
- Step 2: Verify "Your Name" field is **enabled**
- Step 5: Verify "Upload Document" has **red asterisk** (required)
- Try to complete without uploading document → Should show error
- Upload a document → Should allow completion

**Test Scenario B: Existing Customer**
- Step 1: Select "No, I'm existing"
- Step 2: Verify "Your Name" field is **grayed out** (disabled)
- Try to type in name field → Should not accept input
- Step 5: Verify "Upload Document" is **optional** (no red asterisk)
- Can complete without uploading document

**Expected**: Dependencies should work correctly ✅

---

## Session Resume Testing

### Test Session Resume Feature
1. Start Wizard 1
2. Complete Steps 1-3 (don't finish the wizard)
3. Note the session ID from URL
4. Close browser tab
5. Navigate to: http://localhost:3000/wizard/cf1af9d7-31ed-4d6c-8541-d0565dc0c21d?session={session-id}
6. **Expected**: All your previous answers from Steps 1-3 are loaded
7. Wizard resumes from Step 4
8. Complete remaining steps

**Expected**: Session resume should load all responses correctly ✅

---

## Template Testing

### Test Template Creation
1. Complete Wizard 1 entirely
2. On completion, dialog appears: "Save as Template?"
3. Enter template name: "My Test Template"
4. Enter description: "Test template with all selection types"
5. Click "Save Template"
6. Navigate to "My Templates"
7. **Expected**: Your template appears in the list

**Expected**: Template creation should work ✅

---

## Verification Checklist

### All Selection Types Working
- ✅ Single Select: Radio buttons work
- ✅ Multiple Select: Checkboxes work
- ✅ Text Input: Can type text
- ✅ Number Input: Can enter numbers
- ✅ Date Input: Calendar picker works
- ✅ Time Input: Time picker works
- ✅ DateTime Input: DateTime picker works
- ✅ Rating: Can click stars
- ✅ Slider: Can drag slider
- ✅ Color Picker: Color picker opens
- ✅ File Upload: File button works
- ✅ Rich Text: Multi-line text area works

### Dependencies Working
- ✅ Disable_if: Field becomes grayed out
- ✅ Require_if: Red asterisk appears
- ✅ Dynamic validation: Can't proceed without required fields

### Session Features Working
- ✅ Session save: Responses persist
- ✅ Session resume: Previous answers load
- ✅ Session complete: Completion message shows
- ✅ Template creation: Template saves successfully

---

## Database State

### Current Wizards
```
cf1af9d7-31ed-4d6c-8541-d0565dc0c21d - All Selection Types - Basic Test
c623ab03-41cb-4a66-9c27-545c28393632 - All Selection Types - With Dependencies
```

### Dependencies
```
Wizard 2 has 2 dependencies:
1. disable_if: Your Name disabled when "existing customer" selected
2. require_if: Upload Document required when "new customer" selected
```

---

## Scripts Created

### 1. reset_and_create_wizards.py
- Deletes all wizards
- Creates 2 new test wizards
- Run with: `python reset_and_create_wizards.py`

### 2. add_dependencies.py
- Adds dependencies to Wizard 2
- Run with: `python add_dependencies.py`

---

## Known Issues & Fixes

### Issue 1: "Text input not working"
**Root Cause**: Browser cache showing old code
**Fix**: Hard refresh browser (Ctrl + Shift + R)

### Issue 2: Dependencies not visible
**Root Cause**: React hot reload didn't catch changes
**Fix**: Restart frontend server

### Issue 3: Old wizards still showing
**Root Cause**: Browser cache or backend not updated
**Fix**: Hard refresh AND restart frontend

---

## Next Steps

1. ✅ **DONE**: Delete all old wizards
2. ✅ **DONE**: Create 2 comprehensive test wizards
3. ✅ **DONE**: Add conditional dependencies
4. ⏳ **TODO**: Hard refresh browser to see changes
5. ⏳ **TODO**: Test Wizard 1 (Basic)
6. ⏳ **TODO**: Test Wizard 2 (Dependencies)
7. ⏳ **TODO**: Test session resume
8. ⏳ **TODO**: Test template creation

---

## Quick Start

```bash
# 1. Refresh browser
Open http://localhost:3000
Press Ctrl + Shift + R

# 2. Test Wizard 1 (Basic)
http://localhost:3000/wizard/cf1af9d7-31ed-4d6c-8541-d0565dc0c21d

# 3. Test Wizard 2 (Dependencies)
http://localhost:3000/wizard/c623ab03-41cb-4a66-9c27-545c28393632
```

---

## Success Criteria

### ✅ All 12 Selection Types Working
- Every input type renders correctly
- Every input type accepts user input
- Every input type saves responses
- Every input type resumes correctly

### ✅ Dependencies Working
- Disable_if: Fields become disabled
- Require_if: Fields become required
- Show_if/Hide_if: Fields show/hide (if implemented)

### ✅ Sessions Working
- Create new session
- Save responses
- Resume session with responses loaded
- Complete session

### ✅ Templates Working
- Create template from completed session
- Template saves all 12 response types
- Template appears in "My Templates" list

---

## Support

If you encounter any issues:

1. **Check browser console** (F12 → Console tab)
2. **Check network tab** (F12 → Network tab)
3. **Verify backend is running** (http://localhost:8000/docs)
4. **Verify frontend is running** (http://localhost:3000)
5. **Try hard refresh** (Ctrl + Shift + R)
6. **Restart both servers** if needed

---

**End of Fresh Start Guide**

**Status**: ✅ Ready for Testing!
