# QA Test Report - All Selection Types
## Session & Template Testing

**Test Date**: 2025-01-18
**Wizard ID**: `5aac7dfd-32f6-44e3-9568-6f3ffed851de`
**Wizard Name**: QA Test - All Selection Types
**Test URL**: http://localhost:3000/wizard/5aac7dfd-32f6-44e3-9568-6f3ffed851de

---

## Test Wizard Structure

### Step 1: Choice Selections
- ✅ **Single Select**: Choose Your Favorite Color (Red, Blue, Green)
- ✅ **Multiple Select**: Select Features (WiFi, Bluetooth, GPS, NFC) - Min: 1, Max: 3

### Step 2: Text & Number Inputs
- ✅ **Text Input**: Your Name (Required, help text included)
- ✅ **Number Input**: Your Age (Required, Min: 18, Max: 100)
- ✅ **Rich Text**: Additional Comments (Optional, multiline)

### Step 3: Date & Time Inputs
- ✅ **Date Input**: Event Date (Required)
- ✅ **Time Input**: Event Time (Required)
- ✅ **DateTime Input**: Full Event DateTime (Optional)

### Step 4: Interactive Inputs
- ✅ **Rating**: Service Rating (Required, Max: 5 stars)
- ✅ **Slider**: Budget Range (Required, Min: 0, Max: 10000, Step: 100)

### Step 5: Advanced Inputs
- ✅ **Color Picker**: Theme Color (Optional)
- ✅ **File Upload**: Upload Document (Optional, Max: 1 file)

**Total**: 12 Selection Types across 5 Steps

---

## Test Plan

### Test 1: New Session Creation ✅

**Objective**: Verify all 12 selection types render correctly and accept user input

**Steps**:
1. Navigate to wizard URL
2. Enter session name: "QA Test Session - All Types"
3. For each step, fill out all fields:

#### Step 1 Test Data:
- Single Select: Blue
- Multiple Select: WiFi, Bluetooth

#### Step 2 Test Data:
- Text Input: "John Doe"
- Number Input: 25
- Rich Text: "This is a multi-line\ntest comment with\nmultiple lines of text"

#### Step 3 Test Data:
- Date Input: 2025-12-25
- Time Input: 14:30
- DateTime Input: 2025-12-25T18:00

#### Step 4 Test Data:
- Rating: 4 stars
- Slider: 5000

#### Step 5 Test Data:
- Color Picker: #3498DB (blue)
- File Upload: test_document.pdf

**Expected Results**:
- ✅ All fields render with correct input types
- ✅ All fields accept and display entered values
- ✅ Validation works (required fields, min/max values)
- ✅ "Next" button advances to next step
- ✅ "Previous" button returns to previous step with data intact
- ✅ Progress bar shows correct percentage
- ✅ Step indicator highlights current step
- ✅ Session completes successfully

**Actual Results**:
_[To be filled during manual testing]_

---

### Test 2: Session Resume ✅

**Objective**: Verify resuming a session loads all responses correctly

**Prerequisites**: Complete Test 1 first (without completing the wizard)

**Steps**:
1. Complete Steps 1-3 of the wizard
2. Note the session ID from URL
3. Close the browser tab
4. Navigate to: http://localhost:3000/wizard/5aac7dfd-32f6-44e3-9568-6f3ffed851de?session={session-id}
5. Verify all previous responses are loaded

**Expected Results**:
- ✅ Single Select shows "Blue" selected
- ✅ Multiple Select shows "WiFi" and "Bluetooth" checked
- ✅ Text Input shows "John Doe"
- ✅ Number Input shows "25"
- ✅ Rich Text shows multiline comment
- ✅ Date Input shows "2025-12-25"
- ✅ Time Input shows "14:30"
- ✅ DateTime Input shows "2025-12-25T18:00"
- ✅ Wizard resumes from Step 4 (last incomplete step)
- ✅ Can continue filling out remaining steps
- ✅ Can go back to previous steps and modify answers

**Actual Results**:
_[To be filled during manual testing]_

---

### Test 3: Session Completion ✅

**Objective**: Verify completing a session saves all responses

**Steps**:
1. Resume the session from Test 2
2. Complete Steps 4-5
3. Click "Complete" button
4. Verify completion message appears

**Expected Results**:
- ✅ Completion message displayed
- ✅ Session status changed to "completed"
- ✅ "Save as Template" dialog appears
- ✅ All steps show as completed in stepper
- ✅ Session appears in "My Sessions" list as completed

**Actual Results**:
_[To be filled during manual testing]_

---

### Test 4: Template Creation from Completed Session ✅

**Objective**: Verify creating a template from a completed session

**Prerequisites**: Complete Test 3 first

**Steps**:
1. After completing wizard, template dialog should appear
2. Enter template name: "QA Template - All Types"
3. Enter description: "Test template with all 12 selection types"
4. Set "Make Public": No
5. Click "Save Template"

**Expected Results**:
- ✅ Template is created successfully
- ✅ Success message shown
- ✅ Template appears in "My Templates" list
- ✅ Template name: "QA Template - All Types"
- ✅ Template description matches input
- ✅ Template is marked as private
- ✅ Template contains all 12 response values from session

**Verification Steps**:
1. Navigate to "My Templates"
2. Find "QA Template - All Types"
3. Verify template details match

**Actual Results**:
_[To be filled during manual testing]_

---

### Test 5: View Completed Session ✅

**Objective**: Verify viewing a completed session shows all responses

**Steps**:
1. Navigate to "My Sessions"
2. Find the completed session
3. Click "View" button

**Expected Results**:
- ✅ All 5 steps are displayed
- ✅ All 12 responses are shown correctly:
  - Single Select: Blue
  - Multiple Select: WiFi, Bluetooth
  - Text: "John Doe"
  - Number: 25
  - Rich Text: multiline comment
  - Date: 2025-12-25
  - Time: 14:30
  - DateTime: 2025-12-25T18:00
  - Rating: 4 stars
  - Slider: 5000
  - Color: #3498DB
  - File: test_document.pdf
- ✅ Responses are read-only (cannot edit)
- ✅ Can navigate between steps
- ✅ Session metadata shown (date, time spent, etc.)

**Actual Results**:
_[To be filled during manual testing]_

---

### Test 6: Template Application (Future Feature) ⏳

**Objective**: Verify starting a new session from a template pre-fills responses

**Note**: This feature is not yet implemented. This test will be updated once template application is implemented.

**Expected Flow**:
1. Navigate to wizard with template parameter: `?template={template-id}`
2. Dialog shows: "Start new session from template?"
3. User confirms
4. New session is created
5. All form fields are pre-filled with template values
6. User can modify values
7. User completes wizard
8. New session is saved with modified values

**Status**: ⏳ Pending implementation

---

## Test 7: Disabled State with Dependencies ✅

**Objective**: Verify disabled state works for all selection types

**Setup**: Create a test wizard with conditional dependencies

**Test Case 7.1: Text Input Disabled**
- Add dependency: text_input has `disable_if` when single_select = "Red"
- Select "Red"
- **Expected**: Text input is grayed out, cannot type
- Deselect "Red", select "Blue"
- **Expected**: Text input becomes enabled, can type

**Test Case 7.2: Number Input Disabled**
- Add dependency: number_input has `disable_if` when multiple_select includes "WiFi"
- Check "WiFi"
- **Expected**: Number input is grayed out, cannot enter numbers
- Uncheck "WiFi"
- **Expected**: Number input becomes enabled

**Test Case 7.3: Rating Disabled**
- Add dependency: rating has `disable_if` when slider < 1000
- Set slider to 500
- **Expected**: Rating stars are grayed out, cannot click
- Set slider to 5000
- **Expected**: Rating becomes enabled

**Test Case 7.4: Slider Disabled**
- Add dependency: slider has `disable_if` when rating = 1
- Set rating to 1 star
- **Expected**: Slider is grayed out, cannot drag
- Set rating to 5 stars
- **Expected**: Slider becomes enabled

**Test Case 7.5: Date/Time/DateTime Disabled**
- Add dependencies for each date input type
- **Expected**: Calendar/time pickers are disabled
- **Expected**: Cannot select dates/times when disabled

**Test Case 7.6: Color Picker Disabled**
- Add dependency for color picker
- **Expected**: Color input is grayed out
- **Expected**: Cannot open color picker when disabled

**Test Case 7.7: File Upload Disabled**
- Add dependency for file upload
- **Expected**: "Choose File" button is grayed out
- **Expected**: Cannot click to select file when disabled

**Test Case 7.8: Rich Text Disabled**
- Add dependency for rich text
- **Expected**: Text area is grayed out
- **Expected**: Cannot type when disabled

**Actual Results**:
_[To be filled during manual testing]_

---

## Test 8: Response Data Integrity ✅

**Objective**: Verify responses are saved and loaded with correct data types

**Steps**:
1. Complete a session with all selection types
2. Use browser DevTools > Network tab to inspect API calls
3. Verify save response payload
4. Resume session and verify load response payload

**Expected Payloads**:

### Save Response (POST /api/v1/sessions/{id}/responses):
```json
{
  "step_id": "step-uuid",
  "option_set_id": "os-uuid",
  "response_data": {
    "value": <actual value>
  }
}
```

### Load Response (GET /api/v1/sessions/{id}):
```json
{
  "responses": [
    {
      "option_set_id": "os-single-select",
      "response_data": { "value": "blue" }
    },
    {
      "option_set_id": "os-multiple-select",
      "response_data": { "value": ["wifi", "bluetooth"] }
    },
    {
      "option_set_id": "os-text-input",
      "response_data": { "value": "John Doe" }
    },
    {
      "option_set_id": "os-number-input",
      "response_data": { "value": 25 }
    },
    {
      "option_set_id": "os-rating",
      "response_data": { "value": 4 }
    },
    {
      "option_set_id": "os-slider",
      "response_data": { "value": 5000 }
    },
    {
      "option_set_id": "os-date-input",
      "response_data": { "value": "2025-12-25" }
    },
    {
      "option_set_id": "os-time-input",
      "response_data": { "value": "14:30" }
    },
    {
      "option_set_id": "os-datetime-input",
      "response_data": { "value": "2025-12-25T18:00" }
    },
    {
      "option_set_id": "os-color-picker",
      "response_data": { "value": "#3498DB" }
    },
    {
      "option_set_id": "os-file-upload",
      "response_data": { "value": "test_document.pdf" }
    },
    {
      "option_set_id": "os-rich-text",
      "response_data": { "value": "Multi\\nline\\ntext" }
    }
  ]
}
```

**Verification**:
- ✅ `value` field contains correct data type for each selection type
- ✅ String types: text_input, date_input, time_input, datetime_input, color_picker, file_upload, rich_text
- ✅ Number types: number_input, rating, slider
- ✅ Array types: multiple_select
- ✅ UUID types: single_select (option ID)

**Actual Results**:
_[To be filled during manual testing]_

---

## Test 9: Validation Rules ✅

**Objective**: Verify validation works correctly for all selection types

**Test Case 9.1: Required Field Validation**
- Leave required field empty
- Click "Next"
- **Expected**: Error message "This field is required"
- **Expected**: Cannot advance to next step

**Test Case 9.2: Number Input Range Validation**
- Enter age: 15 (below min: 18)
- **Expected**: Error message "Value must be at least 18"
- Enter age: 150 (above max: 100)
- **Expected**: Error message "Value must be at most 100"
- Enter age: 25 (valid)
- **Expected**: No error, can proceed

**Test Case 9.3: Multiple Select Min/Max Validation**
- Select 0 items (below min: 1)
- **Expected**: Error message "Please select at least 1 option"
- Select 4 items (above max: 3)
- **Expected**: Error message "Please select at most 3 options"
- Select 2 items (valid)
- **Expected**: No error, can proceed

**Test Case 9.4: Dynamic Requirement (require_if)**
- Create dependency: rich_text becomes required if rating < 3
- Set rating to 2 stars
- **Expected**: Rich text shows red asterisk (*)
- **Expected**: Cannot proceed without filling rich text
- Fill rich text
- **Expected**: Can proceed
- Set rating to 5 stars
- **Expected**: Red asterisk disappears
- **Expected**: Can proceed without rich text

**Actual Results**:
_[To be filled during manual testing]_

---

## Test 10: Navigation & Progress ✅

**Objective**: Verify wizard navigation and progress tracking

**Test Case 10.1: Forward Navigation**
- Complete Step 1
- Click "Next"
- **Expected**: Advances to Step 2
- **Expected**: Progress bar updates (20% → 40%)
- **Expected**: Stepper highlights Step 2

**Test Case 10.2: Backward Navigation**
- From Step 3, click "Previous"
- **Expected**: Returns to Step 2
- **Expected**: Progress bar updates (60% → 40%)
- **Expected**: Previous responses still shown

**Test Case 10.3: Stepper Click Navigation**
- Click on Step 1 in stepper
- **Expected**: Navigates to Step 1
- **Expected**: Responses preserved

**Test Case 10.4: Progress Calculation**
- Verify progress percentages:
  - Step 1: 20%
  - Step 2: 40%
  - Step 3: 60%
  - Step 4: 80%
  - Step 5: 100%

**Actual Results**:
_[To be filled during manual testing]_

---

## Edge Cases & Error Handling ✅

### Edge Case 1: Browser Refresh
1. Fill out Step 1-3
2. Refresh browser (F5)
3. **Expected**: Session persists, responses loaded
4. **Expected**: Resumes from current step

### Edge Case 2: Back Button Navigation
1. Fill out Step 1-2
2. Click browser back button
3. **Expected**: Returns to previous page (not previous step)
4. **Expected**: Session still exists

### Edge Case 3: Invalid Session ID
1. Navigate to: `?session=invalid-uuid-123`
2. **Expected**: Error snackbar "Failed to load session data"
3. **Expected**: Page doesn't crash
4. **Expected**: Can start new session

### Edge Case 4: Concurrent Edits
1. Open session in two browser tabs
2. Make changes in Tab 1, click "Next"
3. Make different changes in Tab 2, click "Next"
4. **Expected**: Last write wins
5. **Expected**: No data corruption

### Edge Case 5: Long Text Input
1. Enter 10,000 character string in rich_text
2. **Expected**: Saves successfully
3. **Expected**: Loads correctly when resumed

### Edge Case 6: Special Characters
1. Enter special characters: `<script>alert('XSS')</script>`
2. **Expected**: Saved as plain text (not executed)
3. **Expected**: Displays correctly (escaped)

**Actual Results**:
_[To be filled during manual testing]_

---

## Browser Compatibility ✅

Test all functionality in:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Edge (latest)
- ✅ Safari (latest, macOS)

**Specific Tests**:
- Date/Time/DateTime pickers (vary by browser)
- Color picker UI (varies by browser)
- File upload button (varies by browser)
- Rating component (MUI - should be consistent)
- Slider component (MUI - should be consistent)

**Actual Results**:
_[To be filled during manual testing]_

---

## Performance Testing ✅

### Performance Test 1: Initial Load Time
- Measure time from URL entry to wizard render
- **Target**: < 2 seconds
- **Actual**: _[To be measured]_

### Performance Test 2: Step Navigation Speed
- Measure time from "Next" click to next step render
- **Target**: < 500ms
- **Actual**: _[To be measured]_

### Performance Test 3: Session Resume Load Time
- Measure time to load all 12 responses
- **Target**: < 1 second
- **Actual**: _[To be measured]_

### Performance Test 4: Large Session (100 responses)
- Create wizard with 100 option sets
- Complete entire session
- Resume session
- **Expected**: Still performs within targets
- **Actual**: _[To be measured]_

---

## Database Verification ✅

### SQL Queries for Verification

```sql
-- Verify session created
SELECT * FROM user_sessions WHERE id = '{session-id}';

-- Verify all responses saved
SELECT
    sr.id,
    os.name as option_set_name,
    os.selection_type,
    sr.response_data
FROM session_responses sr
JOIN option_sets os ON sr.option_set_id = os.id
WHERE sr.session_id = '{session-id}'
ORDER BY sr.answered_at;

-- Expected: 12 rows (one for each selection type)

-- Verify template created
SELECT * FROM templates WHERE name = 'QA Template - All Types';

-- Verify template responses
SELECT
    tr.id,
    os.name as option_set_name,
    os.selection_type,
    tr.response_data
FROM template_responses tr
JOIN option_sets os ON tr.option_set_id = os.id
JOIN templates t ON tr.template_id = t.id
WHERE t.name = 'QA Template - All Types'
ORDER BY os.name;

-- Expected: 12 rows (one for each selection type)
```

**Verification Checklist**:
- ✅ user_sessions table has entry with correct status
- ✅ session_responses table has 12 entries
- ✅ Each response_data.value matches expected value
- ✅ templates table has entry
- ✅ template_responses table has 12 entries
- ✅ Template responses match session responses

**Actual Results**:
_[To be filled after SQL verification]_

---

## Known Issues & Limitations

### Current Limitations:
1. **File Upload**: Only stores filename, not actual file data
   - **Impact**: Cannot retrieve uploaded file
   - **Workaround**: Use external file storage service
   - **Future**: Implement S3/local file storage

2. **Rich Text**: Uses plain textarea, not WYSIWYG editor
   - **Impact**: No formatting (bold, italic, etc.)
   - **Workaround**: Use markdown syntax manually
   - **Future**: Integrate TinyMCE or Quill

3. **Template Application**: Not yet implemented
   - **Impact**: Cannot start new session from template
   - **Status**: Planned for next release

### Known Bugs:
_[None currently known - to be updated during testing]_

---

## QA Sign-Off

### Test Summary

| Test Category | Total Tests | Passed | Failed | Pending |
|---------------|-------------|--------|--------|---------|
| New Session Creation | 12 | _[ ]_ | _[ ]_ | _[✓]_ |
| Session Resume | 12 | _[ ]_ | _[ ]_ | _[✓]_ |
| Session Completion | 1 | _[ ]_ | _[ ]_ | _[✓]_ |
| Template Creation | 1 | _[ ]_ | _[ ]_ | _[✓]_ |
| View Completed Session | 12 | _[ ]_ | _[ ]_ | _[✓]_ |
| Disabled State | 8 | _[ ]_ | _[ ]_ | _[✓]_ |
| Data Integrity | 12 | _[ ]_ | _[ ]_ | _[✓]_ |
| Validation | 4 | _[ ]_ | _[ ]_ | _[✓]_ |
| Navigation | 4 | _[ ]_ | _[ ]_ | _[✓]_ |
| Edge Cases | 6 | _[ ]_ | _[ ]_ | _[✓]_ |
| Browser Compatibility | 4 | _[ ]_ | _[ ]_ | _[✓]_ |
| Performance | 4 | _[ ]_ | _[ ]_ | _[✓]_ |
| Database Verification | 6 | _[ ]_ | _[ ]_ | _[✓]_ |
| **TOTAL** | **86** | **0** | **0** | **86** |

### Test Execution Notes:
_[To be filled during manual testing]_

### Blocker Issues:
_[None / List any critical issues]_

### Sign-Off:
- **QA Tester**: _[Name]_
- **Date**: _[Date]_
- **Status**: ⏳ **Testing In Progress**
- **Recommendation**: _[Approve / Reject / Approve with Conditions]_

---

## Quick Test Guide

### 5-Minute Smoke Test
1. Start wizard: http://localhost:3000/wizard/5aac7dfd-32f6-44e3-9568-6f3ffed851de
2. Enter session name: "Quick Test"
3. Fill out all 5 steps with sample data
4. Complete wizard
5. Save as template: "Quick Template"
6. Navigate to "My Sessions" - verify session appears
7. Click "Resume" - verify responses loaded
8. Navigate to "My Templates" - verify template appears

**Expected**: All steps work without errors ✅

### Manual Test Execution Checklist
- [ ] Test 1: New Session Creation
- [ ] Test 2: Session Resume
- [ ] Test 3: Session Completion
- [ ] Test 4: Template Creation
- [ ] Test 5: View Completed Session
- [ ] Test 7: Disabled State
- [ ] Test 8: Response Data Integrity
- [ ] Test 9: Validation Rules
- [ ] Test 10: Navigation & Progress
- [ ] Edge Cases
- [ ] Browser Compatibility
- [ ] Performance Testing
- [ ] Database Verification

---

## Appendix: Test Data Reference

### Complete Test Dataset
```typescript
const testData = {
  session_name: "QA Test Session - All Types",
  step1: {
    single_select: "blue",
    multiple_select: ["wifi", "bluetooth"]
  },
  step2: {
    text_input: "John Doe",
    number_input: 25,
    rich_text: "This is a multi-line\\ntest comment with\\nmultiple lines of text"
  },
  step3: {
    date_input: "2025-12-25",
    time_input: "14:30",
    datetime_input: "2025-12-25T18:00"
  },
  step4: {
    rating: 4,
    slider: 5000
  },
  step5: {
    color_picker: "#3498DB",
    file_upload: "test_document.pdf"
  }
};
```

---

**End of QA Test Report**
