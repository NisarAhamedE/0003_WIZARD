# Visual Test Checklist - Wizard Protection System

Use this checklist to visually verify the protection system is working correctly.

## 🎯 Quick Test Plan (15 minutes)

### Test 1: Draft Wizard ✅ (3 minutes)

**Setup**:
1. Start backend: `cd backend && venv/Scripts/python -m uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm start`
3. Login as admin
4. Go to Wizard Builder (`/admin/wizard-builder`)
5. Create a new wizard or edit one with 0 sessions

**Expected UI**:
```
Header:
  [Back to List] [Edit Wizard] [🟢 Draft]             [Save Wizard]

No banners below header

Form:
  ✓ All text fields editable
  ✓ All dropdowns enabled
  ✓ All switches toggleable
  ✓ [Add Tag] button enabled
  ✓ Tags have delete X
  ✓ [Add Step] button enabled
  ✓ Step delete buttons visible
```

**Actions to Test**:
- ✅ Change wizard name → Should save successfully
- ✅ Toggle Published switch → Should save successfully
- ✅ Add/remove tags → Should work
- ✅ Add/delete steps → Should work

---

### Test 2: In-Use Wizard ⚠️ (5 minutes)

**Setup**:
1. Go to Run Wizard (`/wizards`)
2. Start a wizard run (don't store it)
3. Complete some steps (don't finish)
4. Go back to Wizard Builder
5. Edit that same wizard

**Expected UI**:
```
Header:
  [Back to List] [Edit Wizard] [🟠 In Use]             [Update Wizard]

Warning Banner (Orange):
  ⚠️  Warning: This wizard has 1 active run(s) but no stored data.
      Modifying this wizard will affect 1 active run(s). You can delete all runs before modifying.
      [Delete All Runs & Continue]

Form:
  ✓ All fields still editable (no disabled state)
  ✓ Save button present
```

**Actions to Test**:
- ✅ Try to save → Should succeed (with warning shown)
- ✅ Click "Delete All Runs & Continue"
  - Dialog appears: "Delete All Runs & Continue?"
  - Shows warning: "This will permanently delete all 1 run(s)"
  - Lists alternatives
- ✅ Click "Delete All Runs" in dialog
  - Snackbar: "All runs deleted successfully!"
  - Badge changes to 🟢 Draft
  - Warning banner disappears
- ✅ Now edit freely → Should work as draft

---

### Test 3: Published Wizard 🔒 (7 minutes)

**Setup**:
1. Go to Run Wizard
2. Complete a wizard run fully
3. On completion dialog, check "Store this run"
4. Save the run
5. Go back to Wizard Builder
6. Edit that same wizard

**Expected UI**:
```
Header:
  [Back to List] [Edit Wizard] [🔴 Published]    [Clone] [New Version]
  (Note: NO Save button)

Error Banner (Red):
  🔒 Read-Only: This wizard has 1 stored run(s) and is read-only to protect user data.
      This wizard has 1 stored run(s). Use "Clone" or "New Version" to make changes.

Form:
  ⚠️  ALL FIELDS DISABLED:
  ✓ Text fields grayed out (can't type)
  ✓ Dropdowns grayed out (can't select)
  ✓ Switches grayed out (can't toggle)
  ✓ [Add Tag] button disabled
  ✓ Tags have NO delete X
  ✓ [Add Step] button disabled
  ✓ Step edit/delete buttons disabled
```

**Test Clone**:
1. ✅ Click "[Clone]" button
2. Dialog appears:
   ```
   Title: Clone Wizard
   Pre-filled Name: "Website Builder (Copy)"
   Description field (empty)
   [Cancel] [Clone Wizard]
   ```
3. ✅ Change name to "Website Builder - Test Clone"
4. ✅ Click "Clone Wizard"
5. Expected:
   - Snackbar: "Wizard cloned successfully!"
   - Opens the clone in editor
   - Clone has 🟢 Draft badge
   - All fields editable
   - All steps/options preserved
6. ✅ Edit the clone and save → Should work

**Test Version**:
1. ✅ Go back to published wizard (use Back to List)
2. ✅ Click "[New Version]" button
3. Dialog appears:
   ```
   Title: Create New Version
   Pre-filled Name: "Website Builder v2"
   Helper text: "Leave empty to auto-generate name"
   [Cancel] [Create Version]
   ```
4. ✅ Leave name as-is or customize
5. ✅ Click "Create Version"
6. Expected:
   - Snackbar: "New version created successfully!"
   - Opens v2 in editor
   - Version has 🟢 Draft badge
   - All fields editable
   - All steps/options preserved
7. ✅ Edit v2 and save → Should work

**Test Read-Only Enforcement**:
1. ✅ On published wizard, try clicking text fields → Should not focus
2. ✅ Try clicking dropdowns → Should not open
3. ✅ Try clicking switches → Should not toggle
4. ✅ No Save button should be visible
5. ✅ Step accordion should expand but edit buttons disabled

---

## 🔍 Detailed Visual Checks

### Badge Colors & Icons

| State | Badge | Icon | Color |
|-------|-------|------|-------|
| Draft | "Draft" | (none) | Green |
| In-Use | "In Use" | ⚠️  | Orange/Warning |
| Published | "Published" | 🔒 | Red/Error |

### Banner Appearance

**Warning Banner (In-Use)**:
```
Color: Orange background, dark orange border
Icon: ⚠️  Warning icon
Text: Bold "Warning:" prefix
Button: Small outlined warning-colored button
```

**Error Banner (Published)**:
```
Color: Red background, dark red border
Icon: 🔒 Lock icon
Text: Bold "Read-Only:" prefix
Typography: Small caption text with run count
```

### Dialog Styles

**Clone Dialog**:
```
Width: Medium (600px)
Fields: 2 text fields (Name required, Description optional)
Buttons: Gray Cancel, Blue contained Clone with icon
```

**Version Dialog**:
```
Width: Medium (600px)
Fields: 1 text field with helper text
Buttons: Gray Cancel, Blue contained Create with icon
```

**Delete Runs Dialog**:
```
Width: Medium (600px)
Warning Alert at top (orange)
Bulleted list of alternatives
Buttons: Gray Cancel, RED contained Delete
```

---

## 🐛 Common Issues & Solutions

### Issue: Badge not showing
**Check**: Protection status loaded?
- Open DevTools → Network tab
- Look for call to `/api/v1/wizards/{id}/protection-status`
- Should return `{state: "draft", can_edit: true, ...}`

### Issue: Fields not disabled on published wizard
**Check**: Protection state in React DevTools
- Install React DevTools
- Check `protectionStatus.state` value
- Should be exactly `"published"`

### Issue: Clone/Version buttons not showing
**Check**: Conditional rendering
- Buttons only show when `protectionStatus?.state === 'published'`
- Verify protection status loaded

### Issue: Save button still showing on published wizard
**Check**: Button conditional
- Should have: `{!protectionStatus || protectionStatus.can_edit ? <Button> : null}`
- If `can_edit = false`, button hidden

---

## ✅ Final Verification Checklist

Before marking as complete, verify ALL of these:

### UI Elements Present
- [ ] Protection badge shows next to title when editing
- [ ] Badge color matches state (green/orange/red)
- [ ] Lock icon shows for published
- [ ] Warning icon shows for in-use
- [ ] Error banner shows for published
- [ ] Warning banner shows for in-use
- [ ] Clone button shows for published only
- [ ] Version button shows for published only
- [ ] Save button hidden for published

### Functionality Working
- [ ] Draft wizard: All fields editable
- [ ] Draft wizard: Can save successfully
- [ ] In-use wizard: Warning banner appears
- [ ] In-use wizard: "Delete All Runs" button works
- [ ] In-use wizard: Confirmation dialog appears
- [ ] In-use wizard: After deletion, becomes draft
- [ ] Published wizard: All fields disabled
- [ ] Published wizard: Cannot type in text fields
- [ ] Published wizard: Cannot change dropdowns
- [ ] Published wizard: Cannot toggle switches
- [ ] Published wizard: Add/delete buttons disabled
- [ ] Published wizard: Clone dialog opens
- [ ] Published wizard: Clone creates editable copy
- [ ] Published wizard: Version dialog opens
- [ ] Published wizard: Version creates editable v2

### Backend Protection
- [ ] Try to update published wizard via API → Returns 403
- [ ] Try to delete published wizard → Returns 403
- [ ] Clone endpoint works → Returns new wizard
- [ ] Version endpoint works → Returns versioned wizard
- [ ] Protection status endpoint works → Returns correct state

---

## 📸 Screenshot Checklist

Take screenshots of these scenarios for documentation:

1. **Draft Wizard**
   - Full page with green badge
   - Editable form fields

2. **In-Use Wizard**
   - Orange badge
   - Warning banner with button
   - Delete confirmation dialog

3. **Published Wizard**
   - Red badge with lock
   - Error banner
   - Disabled form fields (grayed out)
   - Clone and Version buttons visible
   - Clone dialog
   - Version dialog

4. **After Clone**
   - New wizard as draft
   - Green badge
   - Editable fields

---

## 🎊 Success Criteria

**Test passes when**:
- ✅ All three wizard states display correctly
- ✅ Protection banners show appropriate messages
- ✅ Fields are disabled/enabled correctly
- ✅ Clone creates working copy
- ✅ Version creates linked copy
- ✅ Delete runs confirmation works
- ✅ Backend enforces protection rules
- ✅ User gets helpful guidance in all scenarios

**If ANY of the above fail**, check:
1. Backend running and migration applied?
2. Frontend compiled without errors?
3. Protection status API returning data?
4. React Query cache not stale?
5. Browser DevTools console for errors?

---

**Estimated Testing Time**: 15-20 minutes
**Prerequisites**: Backend running, frontend running, admin account
**Browser**: Chrome/Edge recommended (DevTools support)
