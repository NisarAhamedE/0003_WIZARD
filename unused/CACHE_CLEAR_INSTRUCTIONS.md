# Clear Frontend Cache - Fix Duplicate Wizards

## Problem
Database shows **0 wizards**, but browser shows **5 duplicate wizards**.
This is a **frontend cache** issue.

---

## Solution: Complete Cache Clear

### Step 1: Close ALL Browser Tabs
1. Close **ALL tabs** with `localhost:3000`
2. Make sure NO wizard builder pages are open

### Step 2: Clear Browser Cache Completely

#### For Chrome:
1. Press **Ctrl + Shift + Delete**
2. Select "All time"
3. Check these boxes:
   - ✅ Cookies and other site data
   - ✅ Cached images and files
4. Click "Clear data"

#### For Firefox:
1. Press **Ctrl + Shift + Delete**
2. Select "Everything"
3. Check:
   - ✅ Cookies
   - ✅ Cache
4. Click "Clear Now"

#### For Edge:
1. Press **Ctrl + Shift + Delete**
2. Select "All time"
3. Check:
   - ✅ Cookies
   - ✅ Cached images and files
4. Click "Clear now"

### Step 3: Restart Frontend Server
```bash
# In the terminal running npm start
Ctrl + C  (stop server)

cd frontend
npm start  (restart server)
```

### Step 4: Open in Incognito Window
1. Open a **new incognito/private window**
2. Go to: http://localhost:3000
3. Login as admin

### Step 5: Verify Empty State
You should see:
- **Wizards page**: "No wizards found" or empty list
- **No duplicate entries**

---

## Alternative: Use Incognito Mode (Quickest)

If you don't want to clear cache:

1. Open **Incognito Window** (Ctrl + Shift + N in Chrome)
2. Go to: http://localhost:3000
3. Login as admin
4. You should see 0 wizards

---

## After Cache is Cleared

Run this to create clean test wizards:
```bash
python reset_and_create_wizards.py
python add_dependencies.py
```

You'll have 2 fresh wizards with no duplicates!

---

## Why This Happened

React Query (used in the frontend) caches API responses. When you:
1. Deleted wizards from database
2. But didn't clear frontend cache
3. Frontend kept showing old cached wizard list

**Solution**: Always clear cache after database reset.

---

## Quick Test

After clearing cache, check:
```
Open: http://localhost:3000/wizards
Expected: Empty list or "No wizards found"
Actual: [Should match expected]
```

If still showing duplicates → Incognito mode is your friend!
