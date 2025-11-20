# Multi-Wizard Platform - UI Test Plan

## Test Environment
- **Frontend URL**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Test User Credentials**:
  - **Admin**: username: `admin`, password: `Admin@123`
  - **Regular User**: Create via registration

---

## 1. Authentication Tests

### 1.1 Login Page
- [ ] Navigate to `/login`
- [ ] Verify login form displays correctly
- [ ] Test login with valid credentials (admin/Admin@123)
- [ ] Test login with invalid credentials
- [ ] Verify error messages display correctly
- [ ] Verify successful login redirects to Dashboard

### 1.2 Registration Page
- [ ] Navigate to `/register`
- [ ] Verify registration form displays correctly
- [ ] Test registration with valid data
- [ ] Test password validation (min 8 chars, uppercase, lowercase, digit, special char)
- [ ] Test duplicate email/username validation
- [ ] Verify successful registration redirects to login

### 1.3 Logout
- [ ] Click user menu (top right)
- [ ] Click "Logout"
- [ ] Verify redirect to login page
- [ ] Verify cannot access protected routes after logout

---

## 2. Dashboard Tests

### 2.1 Dashboard Display
- [ ] Navigate to `/` (Dashboard)
- [ ] Verify dashboard stats cards display
- [ ] Verify recent activity section displays
- [ ] Verify quick action buttons work

---

## 3. Template Gallery Tests

### 3.1 Template Gallery Page
- [ ] Navigate to `/templates`
- [ ] Verify 6 system templates display:
  1. Employee Onboarding Portal
  2. Project Planning Wizard
  3. Restaurant Reservation System
  4. Travel Booking Assistant
  5. Fitness Program Designer
  6. Website Design Questionnaire
- [ ] Verify each template shows:
  - Template name
  - Description
  - Category
  - Difficulty level
  - Estimated time
  - Tags
  - Step count

### 3.2 Template Filtering
- [ ] Test search functionality
- [ ] Test category filter
- [ ] Test difficulty filter
- [ ] Verify filters work correctly

### 3.3 Template Clone
- [ ] Click "Clone" on a template
- [ ] Verify clone dialog opens
- [ ] Enter wizard name (e.g., "Test Clone 1")
- [ ] Click "Clone" button
- [ ] Verify redirect to Wizard Builder
- [ ] Verify cloned wizard appears with correct steps and options

---

## 4. Wizard Builder Tests (Admin)

### 4.1 Wizard Builder Access
- [ ] Navigate to `/admin/wizard-builder`
- [ ] Verify builder page loads
- [ ] Verify empty state shows if no wizards

### 4.2 Create New Wizard
- [ ] Click "Create New Wizard" button
- [ ] Enter wizard details:
  - Name: "QA Test Wizard"
  - Description: "Test wizard for QA"
  - Category: Select any
- [ ] Click "Save" or "Next"
- [ ] Verify wizard created successfully

### 4.3 Add Steps
- [ ] Click "Add Step" button
- [ ] Enter step name: "Test Step 1"
- [ ] Enter description
- [ ] Set step order
- [ ] Save step
- [ ] Verify step appears in list

### 4.4 Add Option Sets
For each step, test all 12 selection types:

#### 4.4.1 Single Select
- [ ] Add option set with type "single_select"
- [ ] Add multiple options
- [ ] Set as required/optional
- [ ] Save and verify

#### 4.4.2 Multiple Select
- [ ] Add option set with type "multiple_select"
- [ ] Add multiple options
- [ ] Set min/max selections
- [ ] Save and verify

#### 4.4.3 Text Input
- [ ] Add option set with type "text_input"
- [ ] Set placeholder text
- [ ] Set validation rules
- [ ] Save and verify

#### 4.4.4 Number Input
- [ ] Add option set with type "number_input"
- [ ] Set min/max values
- [ ] Set step increment
- [ ] Save and verify

#### 4.4.5 Date Input
- [ ] Add option set with type "date_input"
- [ ] Save and verify

#### 4.4.6 Time Input
- [ ] Add option set with type "time_input"
- [ ] Save and verify

#### 4.4.7 DateTime Input
- [ ] Add option set with type "datetime_input"
- [ ] Save and verify

#### 4.4.8 Rating
- [ ] Add option set with type "rating"
- [ ] Set min/max rating (1-5)
- [ ] Save and verify

#### 4.4.9 Slider
- [ ] Add option set with type "slider"
- [ ] Set min/max values
- [ ] Set step increment
- [ ] Save and verify

#### 4.4.10 Color Picker
- [ ] Add option set with type "color_picker"
- [ ] Save and verify

#### 4.4.11 File Upload
- [ ] Add option set with type "file_upload"
- [ ] Set allowed file types
- [ ] Set max file size
- [ ] Save and verify

#### 4.4.12 Rich Text
- [ ] Add option set with type "rich_text"
- [ ] Save and verify

### 4.5 Conditional Dependencies
Test all 4 dependency types:

#### 4.5.1 Disable If
- [ ] Create option set dependency with type "disable_if"
- [ ] Select trigger option
- [ ] Save dependency
- [ ] Test in wizard player

#### 4.5.2 Require If
- [ ] Create option set dependency with type "require_if"
- [ ] Select trigger option
- [ ] Save dependency
- [ ] Test in wizard player

#### 4.5.3 Show If
- [ ] Create option set dependency with type "show_if"
- [ ] Select trigger option
- [ ] Save dependency
- [ ] Test in wizard player

#### 4.5.4 Hide If
- [ ] Create option set dependency with type "hide_if"
- [ ] Select trigger option
- [ ] Save dependency
- [ ] Test in wizard player

### 4.6 Publish Wizard
- [ ] Mark wizard as "Published"
- [ ] Save changes
- [ ] Verify wizard appears in "Run Wizard" page

---

## 5. Run Wizard Tests

### 5.1 Wizard Browser
- [ ] Navigate to `/wizards`
- [ ] Verify published wizards display
- [ ] Verify cloned wizards display
- [ ] Click on a wizard to start

### 5.2 Wizard Player - Navigation
- [ ] Start a wizard
- [ ] Verify wizard loads correctly
- [ ] Verify first step displays
- [ ] Test "Next" button navigation
- [ ] Test "Previous" button navigation
- [ ] Verify progress bar updates
- [ ] Verify stepper shows current step

### 5.3 Wizard Player - All Input Types
Test each input type renders and works correctly:

#### 5.3.1 Single Select
- [ ] Verify radio buttons display
- [ ] Select an option
- [ ] Verify selection saves
- [ ] Click Next
- [ ] Click Previous
- [ ] Verify selection persists

#### 5.3.2 Multiple Select
- [ ] Verify checkboxes display
- [ ] Select multiple options
- [ ] Verify min/max selections enforced
- [ ] Verify selection saves

#### 5.3.3 Text Input
- [ ] Verify text area displays
- [ ] Enter text
- [ ] Verify character limits enforced
- [ ] Verify validation works

#### 5.3.4 Number Input
- [ ] Verify number input displays
- [ ] Enter number
- [ ] Verify min/max enforced
- [ ] Verify step increment works

#### 5.3.5 Date Input
- [ ] Verify date picker displays
- [ ] Select a date
- [ ] Verify date format correct

#### 5.3.6 Time Input
- [ ] Verify time picker displays
- [ ] Select a time
- [ ] Verify time format correct

#### 5.3.7 DateTime Input
- [ ] Verify datetime picker displays
- [ ] Select date and time
- [ ] Verify format correct

#### 5.3.8 Rating
- [ ] Verify star rating displays
- [ ] Click on stars to rate
- [ ] Verify rating saves

#### 5.3.9 Slider
- [ ] Verify slider displays
- [ ] Drag slider
- [ ] Verify value updates
- [ ] Verify min/max respected

#### 5.3.10 Color Picker
- [ ] Verify color picker displays
- [ ] Select a color
- [ ] Verify color saves

#### 5.3.11 File Upload
- [ ] Verify file upload button displays
- [ ] Click to upload file
- [ ] Select a file
- [ ] Verify file validates (type, size)
- [ ] Verify file uploads successfully

#### 5.3.12 Rich Text
- [ ] Verify rich text editor displays
- [ ] Enter formatted text
- [ ] Test bold, italic, lists
- [ ] Verify text saves with formatting

### 5.4 Wizard Player - Dependencies
- [ ] Select option that triggers "disable_if"
- [ ] Verify target field disables
- [ ] Select option that triggers "require_if"
- [ ] Verify target field becomes required
- [ ] Select option that triggers "show_if"
- [ ] Verify target field appears
- [ ] Select option that triggers "hide_if"
- [ ] Verify target field disappears

### 5.5 Wizard Player - Validation
- [ ] Try to click Next without filling required fields
- [ ] Verify error messages display
- [ ] Fill required fields
- [ ] Verify errors clear
- [ ] Verify can proceed to next step

### 5.6 Wizard Player - Auto-save
- [ ] Fill out some fields
- [ ] Wait for auto-save indicator
- [ ] Verify "Saved" message appears
- [ ] Refresh page
- [ ] Verify responses persist (if session exists)

### 5.7 Wizard Completion
- [ ] Complete all wizard steps
- [ ] Click "Complete" button
- [ ] Verify completion dialog appears
- [ ] Test "Skip" option
- [ ] Test "Save Run" with name
- [ ] Verify redirect to My Runs page

---

## 6. My Runs Tests

### 6.1 My Runs Page
- [ ] Navigate to `/runs`
- [ ] Verify page title: "My Wizard Runs"
- [ ] Verify stats cards display:
  - Total Runs
  - In Progress
  - Completed
  - Favorites
- [ ] Verify saved runs display in grid

### 6.2 Run Cards
For each run card, verify:
- [ ] Run name displays
- [ ] Run description displays (if exists)
- [ ] Status chip displays (completed/in_progress)
- [ ] "Stored" chip displays
- [ ] Progress bar shows 100% for completed
- [ ] Started date displays
- [ ] Completed date displays
- [ ] Last accessed date displays
- [ ] Tags display (if exists)

### 6.3 Run Actions
- [ ] Click "Edit" button
- [ ] Verify redirect to wizard player
- [ ] Verify URL contains `?session={run_id}`
- [ ] **CRITICAL**: Verify all saved responses load correctly
- [ ] Verify user can see their previous selections
- [ ] Verify can navigate through steps
- [ ] Verify can modify responses

### 6.4 Favorite Runs
- [ ] Click heart icon to favorite a run
- [ ] Verify heart fills (becomes solid)
- [ ] Verify favorite count increases in stats
- [ ] Click heart again to unfavorite
- [ ] Verify heart empties

### 6.5 Delete Run
- [ ] Click delete icon
- [ ] Verify confirmation dialog appears
- [ ] Click "Cancel"
- [ ] Verify dialog closes, run still exists
- [ ] Click delete icon again
- [ ] Click "Delete" in dialog
- [ ] Verify run removed from list
- [ ] Verify stats update

---

## 7. Store Tests

### 7.1 Store Page
- [ ] Navigate to `/store`
- [ ] Verify page title: "Store Wizard"
- [ ] Verify info alert displays
- [ ] Verify stored runs display (should be same 3 runs from database)

### 7.2 Store Run Cards
- [ ] Verify runs display:
  - save1
  - web1
  - test workout
- [ ] Verify each card shows:
  - Run name
  - Description
  - "Stored" chip (green)
  - "Completed" chip (blue)
  - Completed date
  - Total price (if calculated)
  - Tags

### 7.3 Run Selection
- [ ] Click on a run card
- [ ] Verify card border highlights (blue)
- [ ] Verify "Selected" chip appears
- [ ] Click another run card
- [ ] Verify both cards selected
- [ ] Verify "Compare Selected (2)" button appears at top

### 7.4 View Run
- [ ] Click "View" button (prevent card selection with stopPropagation)
- [ ] Verify navigates to wizard player
- [ ] Verify URL contains `?run_id={id}&view_only=true`
- [ ] Verify run loads in view mode

### 7.5 Share Run
- [ ] Click share icon
- [ ] Verify share dialog opens
- [ ] Verify run name displays in dialog
- [ ] Select share type:
  - [ ] View Only
  - [ ] Allow Edit
  - [ ] Allow Clone
- [ ] Click "Generate Link"
- [ ] Verify share link appears
- [ ] Click copy icon
- [ ] Verify "Share link copied" snackbar appears
- [ ] Paste link in notepad to verify format

### 7.6 Compare Runs (if implemented)
- [ ] Select 2 or more runs
- [ ] Click "Compare Selected" button
- [ ] Verify navigates to compare page
- [ ] Verify URL contains run IDs

---

## 8. Analytics Tests (Admin)

### 8.1 Analytics Dashboard
- [ ] Navigate to `/admin/analytics`
- [ ] Verify analytics page loads
- [ ] Verify charts display:
  - Usage statistics
  - Completion rates
  - Popular wizards
  - User engagement

---

## 9. User Management Tests (Admin)

### 9.1 User Management Page
- [ ] Navigate to `/admin/users`
- [ ] Verify user list displays
- [ ] Verify user table shows:
  - Username
  - Email
  - Full name
  - Role
  - Status
  - Created date

### 9.2 User Actions
- [ ] Test search/filter users
- [ ] Test change user role
- [ ] Test activate/deactivate user
- [ ] Test delete user (if allowed)

---

## 10. Responsive Design Tests

### 10.1 Desktop (1920x1080)
- [ ] Test all pages at full desktop resolution
- [ ] Verify layouts look correct
- [ ] Verify no horizontal scrolling

### 10.2 Tablet (768x1024)
- [ ] Test all pages at tablet resolution
- [ ] Verify responsive layouts
- [ ] Verify mobile menu works

### 10.3 Mobile (375x667)
- [ ] Test all pages at mobile resolution
- [ ] Verify hamburger menu appears
- [ ] Verify cards stack vertically
- [ ] Verify forms remain usable

---

## 11. Cross-Browser Tests

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)
- [ ] Safari (if Mac available)

---

## 12. Performance Tests

### 12.1 Load Times
- [ ] Measure page load time for Dashboard
- [ ] Measure page load time for Template Gallery
- [ ] Measure page load time for Wizard Player
- [ ] Verify all pages load within 2 seconds

### 12.2 API Response Times
- [ ] Monitor API calls in Network tab
- [ ] Verify API responses < 500ms
- [ ] Verify no failed requests

---

## 13. Error Handling Tests

### 13.1 Network Errors
- [ ] Stop backend server
- [ ] Try to load a page
- [ ] Verify error message displays
- [ ] Verify retry mechanism works

### 13.2 Validation Errors
- [ ] Submit forms with invalid data
- [ ] Verify error messages display correctly
- [ ] Verify error messages clear on correction

### 13.3 404 Errors
- [ ] Navigate to non-existent route (e.g., `/fake-page`)
- [ ] Verify redirect to Dashboard or 404 page

---

## 14. Data Persistence Tests

### 14.1 Session Persistence
- [ ] Start a wizard
- [ ] Fill some fields
- [ ] Refresh browser
- [ ] Verify session persists (if implemented)

### 14.2 Logout/Login
- [ ] Complete some actions
- [ ] Logout
- [ ] Login again
- [ ] Verify user data persists

---

## 15. Security Tests

### 15.1 Protected Routes
- [ ] Logout
- [ ] Try to access `/admin/wizard-builder`
- [ ] Verify redirect to login

### 15.2 Role-Based Access
- [ ] Login as regular user
- [ ] Try to access admin routes
- [ ] Verify access denied or redirect

---

## Critical Issues Found

### Issue 1: Store Page Not Opening
**Status**: Under investigation
**Steps**:
1. Navigate to `/store`
2. URL changes correctly
3. Page should display but user reports it doesn't open

**What to check**:
- [ ] Browser console for JavaScript errors (F12)
- [ ] Network tab for failed API requests
- [ ] Verify you're logged in
- [ ] Hard refresh browser (Ctrl+Shift+R)

---

## Test Execution Summary

**Total Test Cases**: 200+
**Executed**:
**Passed**:
**Failed**:
**Blocked**:

---

## Notes

- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000 (or 3001 if port conflict)
- Use admin credentials: admin/Admin@123
- Database should have 3 stored runs: save1, web1, test workout
- 6 system templates should exist in Template Gallery

---

## Next Steps

1. Execute all test cases systematically
2. Document any failures with:
   - Steps to reproduce
   - Expected result
   - Actual result
   - Screenshots
   - Browser console errors
3. Report critical bugs immediately
4. Retest failed cases after fixes
