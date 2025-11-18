# Conditional Filtering Implementation Summary

## Overview
This document summarizes the complete implementation of the conditional filtering feature for the Multi-Wizard Platform. This feature allows administrators to create dependencies between options, controlling their visibility, requirement status, and enabled/disabled state based on user selections.

## Implementation Date
November 18, 2025

## Feature Description
The conditional filtering feature enables dynamic option behavior based on the following dependency types:

1. **show_if**: Option is only visible if the dependency option is selected
2. **hide_if**: Option is hidden if the dependency option is selected
3. **require_if**: Option becomes required if the dependency option is selected
4. **disable_if**: Option is disabled if the dependency option is selected

## Backend Implementation

### 1. Database Schema
The `option_dependencies` table already existed in the database with the following structure:
- `id` (UUID, Primary Key)
- `option_id` (UUID, Foreign Key to options)
- `depends_on_option_id` (UUID, Foreign Key to options)
- `dependency_type` (VARCHAR, CHECK constraint for valid types)
- `created_at` (TIMESTAMP)

### 2. Updated Files

#### `backend/app/schemas/wizard.py`
**Added:**
- `DependencyType` enum with values: `show_if`, `hide_if`, `require_if`, `disable_if`
- `OptionDependencyBase` schema
- `OptionDependencyCreate` schema for creating dependencies
- `OptionDependencyResponse` schema for API responses
- Updated `OptionResponse` to include `dependencies: List[OptionDependencyResponse]`

**Location:** Lines 8-32

#### `backend/app/models/wizard.py`
**Updated:**
- `OptionDependency` model constraint to match new dependency types
- Updated CHECK constraint to: `dependency_type.in_(['show_if', 'hide_if', 'require_if', 'disable_if'])`

**Location:** Lines in OptionDependency class

#### `backend/app/crud/wizard.py`
**Added:**
- `OptionDependencyCRUD` class with methods:
  - `get(db, dependency_id)` - Get dependency by ID
  - `get_by_option(db, option_id)` - Get all dependencies for an option
  - `create(db, obj_in, option_id)` - Create new dependency
  - `delete(db, db_obj)` - Delete dependency
- Created `option_dependency_crud` instance

**Updated:**
- `WizardCRUD.get()` method to eager-load dependencies using `joinedload(Option.dependencies)`

**Location:** Lines 277-307

#### `backend/app/api/v1/wizards.py`
**Added API Endpoints:**
1. `GET /wizards/options/{option_id}/dependencies` - Get all dependencies for an option
2. `POST /wizards/options/{option_id}/dependencies` - Create new dependency
3. `DELETE /wizards/dependencies/{dependency_id}` - Delete dependency

**Location:** Lines 349-409

All endpoints are admin-only and include validation to ensure both the option and depends_on_option exist.

## Frontend Implementation

### 1. Updated Files

#### `frontend/src/types/wizard.types.ts`
**Added:**
- `DependencyType` type alias matching backend enum
- `OptionDependency` interface with full structure
- Updated `Option` interface to include `dependencies: OptionDependency[]`

**Location:** Lines 11-34

#### `frontend/src/services/wizard.service.ts`
**Added Methods:**
- `getOptionDependencies(optionId)` - Fetch dependencies for an option
- `createOptionDependency(optionId, data)` - Create new dependency
- `deleteOptionDependency(dependencyId)` - Delete dependency

**Location:** Lines 45-67

#### `frontend/src/components/OptionDependencyManager.tsx`
**Created New Component:**
A complete UI component for managing option dependencies with:
- Display of existing dependencies with color-coded chips
- Add new dependency interface with dropdowns for:
  - Dependency type selection
  - Target option selection (filtered to show only previous options)
- Remove dependency functionality
- Smart filtering to only show options from previous steps/option sets
- Visual feedback with color-coded dependency types:
  - `show_if` - Green (success)
  - `hide_if` - Red (error)
  - `require_if` - Orange (warning)
  - `disable_if` - Gray (default)

**Props:**
- `currentOptionId?: string` - ID of current option (for filtering)
- `dependencies: Array<{depends_on_option_id, dependency_type}>` - Current dependencies
- `availableOptions: AvailableOption[]` - Options that can be depended upon
- `onChange: (dependencies) => void` - Callback when dependencies change

#### `frontend/src/pages/admin/WizardBuilderPage.tsx`
**Major Updates:**

1. **Interface Changes:**
   - Added `id?: string` to `OptionData` interface
   - Added `dependencies?: Array<{...}>` to `OptionData` interface

2. **New Functions:**
   - `handleDependencyChange()` - Handle dependency updates
   - `getAllAvailableOptions(stepIndex, osIndex)` - Collect options from previous steps

3. **Updated Functions:**
   - `loadWizardForEditing()` - Now loads option IDs and dependencies from API
   - `handleAddOption()` - Initializes empty dependencies array for new options

4. **UI Changes:**
   - Changed option rendering from inline fields to Accordion components
   - Each option now has:
     - Expandable accordion with option label in header
     - Chip showing dependency count in header
     - Label and value text fields
     - Description multiline text field
     - Default selection toggle
     - Integrated `OptionDependencyManager` component

**Location:** Throughout file, major changes at lines 39-49, 188-198, 280-290, 314-359, 802-883

#### `frontend/src/pages/WizardPlayerPage.tsx`
**Implemented Complete Filtering Logic:**

1. **Helper Functions:**
   - `getAllSelectedOptionIds()` - Tracks all user selections across all steps
   - `shouldShowOption(option)` - Evaluates show_if/hide_if dependencies
   - `shouldDisableOption(option)` - Evaluates disable_if dependencies
   - `isOptionSetRequired(optionSet)` - Evaluates require_if dependencies

2. **Filtering Algorithm:**
   - Collects all selected option IDs from current and previous steps
   - For each option, checks all dependencies
   - Applies visibility filters before rendering
   - Applies disabled state to visible options
   - Dynamically updates required status of option sets

3. **UI Integration:**
   - `renderOptionSet()` filters options before display
   - Only visible options are rendered
   - Disabled options show as disabled in radio/checkbox controls
   - Required indicators update based on dependencies
   - Validation considers dynamic requirements

**Location:** Helper functions and rendering logic throughout WizardPlayerPage

## How It Works

### Wizard Builder (Admin) Flow:
1. Admin creates a wizard with multiple steps
2. For each option in an option set, admin can:
   - Click to expand the option accordion
   - Scroll to "Conditional Dependencies" section
   - Select a dependency type from dropdown
   - Select which previous option it depends on
   - Click "Add" to create the dependency
3. Dependencies are saved as part of the wizard structure
4. Admin can remove dependencies with the delete button

### Wizard Player (User) Flow:
1. User starts a wizard session
2. As user makes selections:
   - `getAllSelectedOptionIds()` tracks all selections
   - Options with `show_if` dependencies appear when dependency is met
   - Options with `hide_if` dependencies disappear when dependency is met
   - Options with `disable_if` dependencies become disabled when dependency is met
   - Option sets with any option having `require_if` become required when dependency is met
3. Validation respects dynamic requirements
4. User can only proceed if all (including dynamically required) fields are completed

## Data Flow

### Creating Dependencies (Edit Mode):
```
WizardBuilderPage
  ├─> Load existing wizard with dependencies
  ├─> User adds/removes dependencies in OptionDependencyManager
  ├─> Dependencies stored in local state (wizard.steps[].option_sets[].options[].dependencies)
  └─> On save, entire wizard structure (including dependencies) sent to backend
```

### Runtime Filtering (Player Mode):
```
WizardPlayerPage
  ├─> Load wizard with all option dependencies
  ├─> User makes selections
  ├─> getAllSelectedOptionIds() builds list of selected option IDs
  ├─> For each option:
  │   ├─> shouldShowOption() checks show_if/hide_if dependencies
  │   └─> shouldDisableOption() checks disable_if dependencies
  ├─> For each option set:
  │   └─> isOptionSetRequired() checks require_if dependencies
  └─> Render only visible options with correct states
```

## Important Implementation Details

### Option ID Management
- When editing existing wizards, option IDs are loaded from the API
- New options created in the builder don't have IDs until saved
- The `getAllAvailableOptions()` function filters out options without IDs
- Dependencies can only be created on saved options with IDs

### Dependency Direction
- Dependencies are always on **previous** options
- An option can only depend on options from:
  - Any previous step, OR
  - An earlier option set in the current step
- This prevents circular dependencies and ensures logical flow

### Multiple Dependencies
- An option can have multiple dependencies
- All dependencies are evaluated independently
- For visibility (`show_if`/`hide_if`):
  - Option is hidden if ANY `hide_if` dependency is met
  - Option is hidden if ANY `show_if` dependency is NOT met
- For state (`require_if`/`disable_if`):
  - Applied if dependency condition is met

## Testing the Feature

### Test Case 1: Show If Dependency
1. Create a wizard with 2 steps
2. Step 1: Add "Do you own a car?" with options "Yes" and "No"
3. Step 2: Add "What car brand?" with options "Toyota", "Honda", "Ford"
4. Edit each car brand option, add dependency: "Show If" → "Yes" (from step 1)
5. Save and test:
   - Select "No" in step 1 → Step 2 should show no options
   - Select "Yes" in step 1 → Step 2 should show all car brands

### Test Case 2: Require If Dependency
1. Create a wizard with 2 steps
2. Step 1: "Are you a student?" with "Yes"/"No"
3. Step 2: "Student ID" (text input, not required by default)
4. Edit the "Student ID" option set, create an option, add dependency: "Require If" → "Yes"
5. Save and test:
   - Select "No" → Should be able to skip Student ID
   - Select "Yes" → Student ID should become required (marked with *)

### Test Case 3: Multiple Dependencies
1. Create a wizard with 3 steps
2. Step 1: "Country" with "USA", "Canada", "Other"
3. Step 2: "State/Province" with "California", "Texas", "Ontario", "Quebec"
4. Configure dependencies:
   - "California", "Texas": Show If "USA" selected
   - "Ontario", "Quebec": Show If "Canada" selected
5. Save and test:
   - Select "USA" → Only USA states visible
   - Select "Canada" → Only Canadian provinces visible
   - Select "Other" → No options visible

## Known Limitations

1. **New Options in Builder**: Dependencies can only be added to options that have been saved (have IDs). After adding new options, save the wizard first before adding dependencies.

2. **Circular Dependencies**: The UI prevents circular dependencies by only allowing dependencies on previous options, but there's no backend validation for this yet.

3. **Complex Logic**: Currently doesn't support AND/OR logic between multiple dependencies. Each dependency is evaluated independently.

4. **Visual Preview**: The Wizard Builder doesn't show a preview of how dependencies will behave - admins must test in player mode.

## Files Changed Summary

### Backend Files (5 files):
1. `backend/app/schemas/wizard.py` - Added dependency schemas
2. `backend/app/models/wizard.py` - Updated dependency constraint
3. `backend/app/crud/wizard.py` - Added OptionDependencyCRUD class and eager loading
4. `backend/app/api/v1/wizards.py` - Added 3 new API endpoints
5. `backend/app/crud/__init__.py` - Export new CRUD (if applicable)

### Frontend Files (5 files):
1. `frontend/src/types/wizard.types.ts` - Added dependency types
2. `frontend/src/services/wizard.service.ts` - Added dependency API methods
3. `frontend/src/components/OptionDependencyManager.tsx` - New component (218 lines)
4. `frontend/src/pages/admin/WizardBuilderPage.tsx` - Major updates for dependency UI
5. `frontend/src/pages/WizardPlayerPage.tsx` - Filtering logic implementation

## Completion Status

✅ **COMPLETED** - All components implemented and integrated
- ✅ Backend schemas and models
- ✅ Backend CRUD operations
- ✅ Backend API endpoints
- ✅ Frontend types
- ✅ Frontend services
- ✅ Dependency management UI component
- ✅ Wizard Builder integration
- ✅ Wizard Player filtering logic

🔄 **READY FOR TESTING** - Manual testing recommended to verify:
- Dependency creation in Wizard Builder
- Dependency persistence across save/load
- Runtime filtering behavior in Wizard Player
- All 4 dependency types working correctly
- Edge cases and complex scenarios

## Next Steps for Production

1. **Add Backend Validation**: Prevent circular dependencies at API level
2. **Add Unit Tests**: Test filtering logic with various dependency scenarios
3. **Add Preview Mode**: Show dependency behavior preview in Wizard Builder
4. **Add Bulk Operations**: Allow copying dependencies between similar options
5. **Add Documentation**: Create admin guide with examples and best practices
6. **Add Analytics**: Track which dependencies are most commonly used
7. **Performance**: Consider caching dependency evaluation for large wizards

## Support

For questions or issues with this implementation, refer to:
- Database schema: `docs/02_DATABASE_SCHEMA.md`
- Original feature spec: `CONDITIONAL_FILTERING_FUNCTIONAL_GUIDE.md`
- API documentation: `http://localhost:8000/docs` (when server running)
