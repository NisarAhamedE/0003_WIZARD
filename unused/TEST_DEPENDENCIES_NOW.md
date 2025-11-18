# Test Dependencies - Step by Step Guide

## Dependencies Confirmed in Database ✅

```
Dependency 1: Your Name field - disable_if "No, I'm existing" is selected
Dependency 2: Upload Document - require_if "Yes, I'm new" is selected
```

---

## CRITICAL: Restart Frontend First!

The dependencies are in the database, but your browser needs to reload the latest code.

### Option 1: Hard Refresh (Try This First)
1. Open browser to the wizard
2. Press **Ctrl + Shift + R** (Windows) or **Cmd + Shift + R** (Mac)
3. This forces a complete reload

### Option 2: Restart Frontend Server (If hard refresh doesn't work)
```bash
# In the terminal running frontend
Ctrl + C  (stop server)

cd frontend
npm start  (restart server)

# Wait for "Compiled successfully!"
# Then refresh browser
```

---

## Test Instructions

### Test URL
http://localhost:3000/wizard/c623ab03-41cb-4a66-9c27-545c28393632

---

## Test Case 1: Disable_if Dependency

### Steps:
1. Start the wizard
2. Enter session name: "Test Disable Dependency"
3. **Step 1**: Select "**No, I'm existing**"
4. Click "Next"
5. **Step 2**: Look at the "Your Name" field

### Expected Result:
- ✅ The "Your Name" text field should be **grayed out** (disabled)
- ✅ You cannot type in the field
- ✅ The field has a disabled appearance (lighter background)

### If It's NOT Working:
- The field is still white and you can type
- **Solution**: You need to restart the frontend server (see above)

---

## Test Case 2: Change Selection (Re-enable Field)

### Steps:
1. From Step 2, click "Previous"
2. **Step 1**: Change to "**Yes, I'm new**"
3. Click "Next"
4. **Step 2**: Look at the "Your Name" field again

### Expected Result:
- ✅ The "Your Name" text field should now be **enabled** (normal white)
- ✅ You CAN type in the field
- ✅ You can enter your name normally

---

## Test Case 3: Require_if Dependency

### Steps:
1. Continue with "Yes, I'm new" selected
2. Fill out all fields in Steps 2-4
3. **Step 5**: Look at the "Upload Document" field

### Expected Result:
- ✅ The field label should have a **red asterisk (*)** next to it
- ✅ This indicates the field is now **required**
- ✅ If you try to click "Complete" without uploading, you get an error

---

## Test Case 4: Require_if Removal

### Steps:
1. From Step 5, go back to Step 1
2. Change to "**No, I'm existing**"
3. Navigate back to Step 5

### Expected Result:
- ✅ The "Upload Document" field should **NOT** have a red asterisk
- ✅ The field is now **optional**
- ✅ You can complete the wizard without uploading

---

## Verification Checklist

- [ ] Hard refreshed browser (Ctrl + Shift + R)
- [ ] OR restarted frontend server
- [ ] Opened wizard URL: http://localhost:3000/wizard/c623ab03-41cb-4a66-9c27-545c28393632
- [ ] Selected "No, I'm existing" → Name field is **disabled**
- [ ] Changed to "Yes, I'm new" → Name field is **enabled**
- [ ] "Yes, I'm new" selected → Upload Document is **required** (red *)
- [ ] "No, I'm existing" selected → Upload Document is **optional** (no red *)

---

## Troubleshooting

### Issue: Dependencies Not Working

**Check 1: Frontend Needs Restart**
```bash
# Stop frontend (Ctrl + C)
cd frontend
npm start
```

**Check 2: Browser Cache**
- Clear browser cache completely
- Or open in Incognito/Private window

**Check 3: Verify Code is Updated**
- Open DevTools (F12)
- Go to Sources tab
- Find WizardPlayerPage.tsx
- Search for "isOptionSetDisabled"
- Should exist at line ~427

**Check 4: Check Console for Errors**
- Open DevTools (F12)
- Go to Console tab
- Look for any red errors
- If you see errors, take a screenshot

---

## Visual Guide

### When "No, I'm existing" is Selected:

```
Step 2: Personal Details
┌─────────────────────────────────────┐
│ Your Name                           │
│ ┌─────────────────────────────────┐ │  ← GRAYED OUT
│ │ [Field is disabled]             │ │  ← CANNOT TYPE
│ └─────────────────────────────────┘ │
│ This field will be disabled if you  │
│ selected 'existing customer'        │
└─────────────────────────────────────┘
```

### When "Yes, I'm new" is Selected:

```
Step 2: Personal Details
┌─────────────────────────────────────┐
│ Your Name                           │
│ ┌─────────────────────────────────┐ │  ← NORMAL WHITE
│ │ [Type here...]                  │ │  ← CAN TYPE
│ └─────────────────────────────────┘ │
│ This field will be disabled if you  │
│ selected 'existing customer'        │
└─────────────────────────────────────┘

Step 5: Final Details
┌─────────────────────────────────────┐
│ Upload Document *                   │  ← RED ASTERISK
│ [Choose File] button                │
│ Required if you're a new customer   │
└─────────────────────────────────────┘
```

---

## Database Confirmation

Dependencies are already in the database:

```
Your Name (text_input):
  - depends on: cfa36dc6-a598-4dcd-bfea-39d53e989ef5 ("No, I'm existing")
  - type: disable_if
  - ✅ CONFIRMED IN DATABASE

Upload Document (file_upload):
  - depends on: cdca5811-93b5-406d-bd1e-db25434f5542 ("Yes, I'm new")
  - type: require_if
  - ✅ CONFIRMED IN DATABASE
```

---

## Next Steps

1. ✅ **DONE**: Dependencies added to database
2. ⏳ **TODO**: Restart frontend (if not already)
3. ⏳ **TODO**: Test "disable_if" dependency
4. ⏳ **TODO**: Test "require_if" dependency
5. ⏳ **TODO**: Verify both dependencies work correctly

---

## Success Criteria

The test is successful when:
- ✅ Selecting "No, I'm existing" → Name field is grayed out and uneditable
- ✅ Selecting "Yes, I'm new" → Name field is enabled and editable
- ✅ Selecting "Yes, I'm new" → Upload Document shows red asterisk (required)
- ✅ Selecting "No, I'm existing" → Upload Document has no asterisk (optional)

If ALL of these work, then dependencies are working perfectly! 🎉

---

**Test Now**: http://localhost:3000/wizard/c623ab03-41cb-4a66-9c27-545c28393632
