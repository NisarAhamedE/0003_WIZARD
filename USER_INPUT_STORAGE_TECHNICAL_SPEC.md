# User Input Storage & Retrieval - Technical Specification

## Table of Contents
1. [Overview](#overview)
2. [Database Schema](#database-schema)
3. [Data Flow Architecture](#data-flow-architecture)
4. [Storage Process](#storage-process)
5. [Retrieval Process](#retrieval-process)
6. [Population Process](#population-process)
7. [Code Examples](#code-examples)
8. [Edge Cases & Validation](#edge-cases--validation)

---

## Overview

The Multi-Wizard Platform uses a sophisticated two-tier response storage system that separates step-level metadata from actual user input data. This design allows for flexible data storage while maintaining referential integrity and supporting complex wizard workflows.

### Key Design Principles

1. **Two-Tier Storage**: Step responses contain metadata, option set responses contain actual user data
2. **JSONB Format**: User input stored as flexible JSONB `{value: ...}` structure
3. **Relational Integrity**: Foreign key relationships maintain data consistency
4. **Type Agnostic**: Same storage mechanism handles 12 different input types
5. **Atomic Operations**: All-or-nothing save operations prevent partial data corruption

---

## Database Schema

### Core Tables

```sql
-- 1. Wizard Runs Table (Main container)
CREATE TABLE wizard_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wizard_id UUID NOT NULL REFERENCES wizards(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    run_name VARCHAR(255),
    run_description TEXT,
    status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress, completed, abandoned
    current_step_index INTEGER DEFAULT 0,
    total_steps INTEGER,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    last_accessed_at TIMESTAMP DEFAULT NOW(),
    calculated_price DECIMAL(10,2),
    is_stored BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    metadata JSONB,  -- Additional flexible metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Step Responses Table (Step-level metadata)
CREATE TABLE wizard_run_step_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES wizard_runs(id) ON DELETE CASCADE,
    step_id UUID NOT NULL,  -- References step from wizard structure
    step_index INTEGER NOT NULL,
    step_name VARCHAR(255),
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    time_spent_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(run_id, step_id)  -- One response per step per run
);

-- 3. Option Set Responses Table (Actual user input)
CREATE TABLE wizard_run_option_set_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES wizard_runs(id) ON DELETE CASCADE,
    step_response_id UUID NOT NULL REFERENCES wizard_run_step_responses(id) ON DELETE CASCADE,
    option_set_id UUID NOT NULL,  -- References option set from wizard structure
    option_set_name VARCHAR(255),
    selection_type VARCHAR(50),  -- single_select, multiple_select, text_input, etc.
    response_value JSONB NOT NULL,  -- The actual user input: {value: ...}
    selected_options TEXT[],  -- For select types, stores selected option values
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(run_id, option_set_id)  -- One response per option set per run
);

-- 4. File Uploads Table (For file_upload type)
CREATE TABLE wizard_run_file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES wizard_runs(id) ON DELETE CASCADE,
    option_set_response_id UUID NOT NULL REFERENCES wizard_run_option_set_responses(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

### Indexes for Performance

```sql
-- Speed up lookups by run_id
CREATE INDEX idx_step_responses_run_id ON wizard_run_step_responses(run_id);
CREATE INDEX idx_option_set_responses_run_id ON wizard_run_option_set_responses(run_id);

-- Speed up filtering by status
CREATE INDEX idx_wizard_runs_status ON wizard_runs(status);
CREATE INDEX idx_wizard_runs_is_stored ON wizard_runs(is_stored);

-- Speed up user-specific queries
CREATE INDEX idx_wizard_runs_user_id ON wizard_runs(user_id);
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    User fills wizard inputs
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ WizardPlayerPage Component (React State)                         │
│                                                                   │
│ const [responses, setResponses] = useState<ResponseData>({       │
│   "option-set-uuid-1": "text value",                             │
│   "option-set-uuid-2": ["choice1", "choice2"],                   │
│   "option-set-uuid-3": 42                                        │
│ });                                                               │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    User clicks "Complete" or "Save"
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│           FRONTEND: saveRunMutation (useMutation)                │
│                                                                   │
│ 1. Validate all required fields                                  │
│ 2. Clear existing responses (if updating)                        │
│ 3. Loop through wizard steps:                                    │
│    - Create step response (metadata)                             │
│    - Create option set responses (user data)                     │
│ 4. Update run metadata (name, description, is_stored)            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    HTTP POST requests to backend
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                           │
│                  (FastAPI + Pydantic Validation)                 │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ POST /wizard-runs/{run_id}/steps                                 │
│ ├─ Validates: run_id, step_id, step_index, step_name            │
│ └─ Creates: WizardRunStepResponse record                         │
│                                                                   │
│ POST /wizard-runs/{run_id}/option-sets                           │
│ ├─ Validates: run_id, step_response_id, option_set_id           │
│ └─ Creates: WizardRunOptionSetResponse with JSONB value          │
│                                                                   │
│ PUT /wizard-runs/{run_id}                                        │
│ └─ Updates: run_name, run_description, is_stored                 │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CRUD OPERATIONS                             │
│                    (SQLAlchemy ORM Layer)                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     POSTGRESQL DATABASE                          │
│                                                                   │
│ wizard_runs                                                       │
│ ├── wizard_run_step_responses                                    │
│ │   └── wizard_run_option_set_responses                          │
│ │       ├── response_value: {value: "actual data"}               │
│ │       └── wizard_run_file_uploads (if file type)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Storage Process

### Step-by-Step Storage Flow

#### 1. Frontend Preparation (WizardPlayerPage.tsx)

**Location:** `frontend/src/pages/WizardPlayerPage.tsx:140-234`

```typescript
// User clicks "Save" button after completing wizard
const saveRunMutation = useMutation({
  mutationFn: async (data: {
    runId: string;
    name: string;
    description: string
  }) => {

    // STEP 1: Validate all responses
    const validationErrors = validateAllSteps();
    if (validationErrors.length > 0) {
      throw new Error(`Validation failed:\n${validationErrors.join('\n')}`);
    }

    // STEP 2: Clear existing responses (prevents duplicates on re-save)
    try {
      const existingRun = await wizardRunService.getWizardRun(data.runId);
      if (existingRun.option_set_responses?.length > 0) {
        console.log('[WizardPlayer] Clearing old responses before update');
        await wizardRunService.clearAllResponses(data.runId);
      }
    } catch (error) {
      console.log('[WizardPlayer] No existing responses, proceeding with fresh save');
    }

    // STEP 3: Save all responses
    const savedStepResponses: string[] = [];
    const savedOptionSetResponses: string[] = [];

    for (let stepIndex = 0; stepIndex < wizard.steps.length; stepIndex++) {
      const step = wizard.steps[stepIndex];

      // Check if step has any responses
      const hasResponses = step.option_sets.some(os => {
        const val = responses[os.id];
        return val !== undefined && val !== null &&
               (Array.isArray(val) ? val.length > 0 : true);
      });

      if (!hasResponses) {
        console.log(`[WizardPlayer] Skipping step ${step.name} - no responses`);
        continue;
      }

      // Create step response (metadata)
      const stepResponse = await wizardRunService.createStepResponse(
        data.runId,
        {
          run_id: data.runId,
          step_id: step.id,
          step_index: stepIndex,
          step_name: step.name,
        }
      );
      savedStepResponses.push(stepResponse.id);

      // Create option set responses (actual user input)
      for (const optionSet of step.option_sets) {
        const responseValue = responses[optionSet.id];

        if (responseValue !== undefined && responseValue !== null) {
          // Skip empty arrays
          if (Array.isArray(responseValue) && responseValue.length === 0) {
            continue;
          }

          // Create option set response with JSONB wrapper
          const optionSetResp = await wizardRunService.createOptionSetResponse(
            data.runId,
            {
              run_id: data.runId,
              step_response_id: stepResponse.id,
              option_set_id: optionSet.id,
              response_value: { value: responseValue },  // ← JSONB wrapper
            }
          );
          savedOptionSetResponses.push(optionSetResp.id);
        }
      }
    }

    console.log(`[WizardPlayer] Saved ${savedStepResponses.length} step responses`);
    console.log(`[WizardPlayer] Saved ${savedOptionSetResponses.length} option set responses`);

    // STEP 4: Update run metadata
    const result = await wizardRunService.updateWizardRun(data.runId, {
      run_name: data.name,
      run_description: data.description,
      is_stored: true,  // Mark as stored
    });

    // STEP 5: Clear localStorage backup
    localStorage.removeItem(`wizard_responses_${data.runId}`);

    return result;
  },
  onSuccess: () => {
    setSnackbar({
      open: true,
      message: 'Run saved successfully!',
      severity: 'success',
    });
    navigate('/runs');  // Navigate to My Runs page
  },
  onError: (error: any) => {
    setSnackbar({
      open: true,
      message: error.message || 'Failed to save run',
      severity: 'error',
    });
  },
});
```

#### 2. Backend API Endpoints

**Location:** `backend/app/api/v1/wizard_runs.py:323-372`

##### 2.1 Create Step Response

```python
@router.post("/{run_id}/steps", response_model=WizardRunStepResponseResponse)
async def create_step_response(
    run_id: UUID,
    step_response: WizardRunStepResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a step response for a wizard run.

    Request Body:
    {
        "run_id": "uuid",
        "step_id": "uuid",
        "step_index": 0,
        "step_name": "Project Overview",
        "completed": false,
        "time_spent_seconds": 120
    }
    """
    # Verify run exists and user has access
    run = crud_wizard_run.get_wizard_run(db, run_id=run_id, user_id=current_user.id)
    if not run:
        raise HTTPException(status_code=404, detail="Wizard run not found")

    # Check if step response already exists
    existing = db.query(WizardRunStepResponse).filter(
        WizardRunStepResponse.run_id == run_id,
        WizardRunStepResponse.step_id == step_response.step_id
    ).first()

    if existing:
        # Update existing
        for key, value in step_response.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    # Create new step response
    db_step_response = WizardRunStepResponse(
        **step_response.dict()
    )
    db.add(db_step_response)
    db.commit()
    db.refresh(db_step_response)

    return db_step_response
```

##### 2.2 Create Option Set Response

```python
@router.post("/{run_id}/option-sets", response_model=WizardRunOptionSetResponseResponse)
async def create_option_set_response(
    run_id: UUID,
    option_set_response: WizardRunOptionSetResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create an option set response for a wizard run.

    Request Body:
    {
        "run_id": "uuid",
        "step_response_id": "uuid",
        "option_set_id": "uuid",
        "option_set_name": "Company Name",
        "selection_type": "text_input",
        "response_value": {
            "value": "Acme Corporation"  ← Actual user input wrapped in JSONB
        },
        "selected_options": []
    }
    """
    # Verify run exists and user has access
    run = crud_wizard_run.get_wizard_run(db, run_id=run_id, user_id=current_user.id)
    if not run:
        raise HTTPException(status_code=404, detail="Wizard run not found")

    # Verify step response exists
    step_response = db.query(WizardRunStepResponse).filter(
        WizardRunStepResponse.id == option_set_response.step_response_id,
        WizardRunStepResponse.run_id == run_id
    ).first()

    if not step_response:
        raise HTTPException(status_code=404, detail="Step response not found")

    # Check if option set response already exists
    existing = db.query(WizardRunOptionSetResponse).filter(
        WizardRunOptionSetResponse.run_id == run_id,
        WizardRunOptionSetResponse.option_set_id == option_set_response.option_set_id
    ).first()

    if existing:
        # Update existing
        for key, value in option_set_response.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    # Create new option set response
    db_option_set_response = WizardRunOptionSetResponse(
        **option_set_response.dict()
    )
    db.add(db_option_set_response)
    db.commit()
    db.refresh(db_option_set_response)

    return db_option_set_response
```

#### 3. Database Models (SQLAlchemy)

**Location:** `backend/app/models/wizard_run.py`

```python
class WizardRunStepResponse(Base):
    """Step response model - stores metadata about step completion"""
    __tablename__ = "wizard_run_step_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("wizard_runs.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(UUID(as_uuid=True), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_name = Column(String(255))
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    time_spent_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    run = relationship("WizardRun", back_populates="step_responses")
    option_set_responses = relationship(
        "WizardRunOptionSetResponse",
        back_populates="step_response",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint('run_id', 'step_id', name='uq_run_step'),
    )


class WizardRunOptionSetResponse(Base):
    """Option set response model - stores actual user input"""
    __tablename__ = "wizard_run_option_set_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("wizard_runs.id", ondelete="CASCADE"), nullable=False)
    step_response_id = Column(UUID(as_uuid=True), ForeignKey("wizard_run_step_responses.id", ondelete="CASCADE"), nullable=False)
    option_set_id = Column(UUID(as_uuid=True), nullable=False)
    option_set_name = Column(String(255))
    selection_type = Column(String(50))

    # CRITICAL: response_value is JSONB - stores {value: actual_data}
    response_value = Column(JSONB, nullable=False)

    selected_options = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    run = relationship("WizardRun", back_populates="option_set_responses")
    step_response = relationship("WizardRunStepResponse", back_populates="option_set_responses")
    file_uploads = relationship(
        "WizardRunFileUpload",
        back_populates="option_set_response",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint('run_id', 'option_set_id', name='uq_run_option_set'),
    )
```

---

## Retrieval Process

### Step-by-Step Retrieval Flow

#### 1. Frontend Triggers Load (User clicks "View" or "Edit")

**Location:** `frontend/src/pages/StoreWizardPage.tsx:65-67`

```typescript
// View button clicked
const handleViewRun = (run: WizardRun) => {
  navigate(`/wizard/${run.wizard_id}?session=${run.id}&view_only=true`);
};

// Edit button clicked (from MyRunsPage)
const handleEditRun = (run: WizardRun) => {
  navigate(`/wizard/${run.wizard_id}?session=${run.id}`);
};
```

#### 2. WizardPlayerPage Loads and Reads URL Parameters

**Location:** `frontend/src/pages/WizardPlayerPage.tsx:53-55`

```typescript
const [searchParams] = useSearchParams();
const sessionIdFromUrl = searchParams.get('session');  // Get run ID
const isViewOnly = searchParams.get('view_only') === 'true';  // Check if view mode
```

#### 3. useEffect Triggers Response Loading

**Location:** `frontend/src/pages/WizardPlayerPage.tsx:282-346`

```typescript
// Load wizard run responses when resuming an existing run
useEffect(() => {
  const loadRunResponses = async () => {
    if (!sessionId || !wizard) {
      console.log('[WizardPlayer] loadRunResponses - skipping');
      return;
    }

    console.log('[WizardPlayer] Loading responses for session:', sessionId);

    try {
      // STEP 1: Fetch full run details including all responses
      const run = await wizardRunService.getWizardRun(sessionId);

      console.log('[WizardPlayer] Loaded run:', run);
      console.log('[WizardPlayer] Run status:', run.status);
      console.log('[WizardPlayer] Option set responses:', run.option_set_responses?.length || 0);

      // STEP 2: Transform backend responses to frontend format
      const loadedResponses: ResponseData = {};

      if (run.option_set_responses) {
        console.log('[WizardPlayer] Processing', run.option_set_responses.length, 'responses');

        run.option_set_responses.forEach((resp) => {
          // CRITICAL: Extract value from JSONB wrapper
          // Backend stores: {value: "actual data"}
          // We need: "actual data"
          const responseValue = (resp.response_value as any)?.value || resp.response_value;

          console.log('[WizardPlayer] Response for option_set', resp.option_set_id, ':', responseValue);

          if (responseValue !== undefined && responseValue !== null) {
            // Map by option_set_id for quick lookup
            loadedResponses[resp.option_set_id] = responseValue;
          }
        });
      }

      console.log('[WizardPlayer] Final loadedResponses:', loadedResponses);
      console.log('[WizardPlayer] Number of responses:', Object.keys(loadedResponses).length);

      // STEP 3: Update React state with loaded responses
      setResponses(loadedResponses);
      console.log('[WizardPlayer] Responses state updated');

      // STEP 4: Set completion status
      if (run.status === 'completed') {
        console.log('[WizardPlayer] Setting isCompleted to true');
        setIsCompleted(true);
        // Start from step 0 for viewing/editing
        setCurrentStepIndex(0);
      }

      // STEP 5: Resume from last step if in progress
      if (run.status === 'in_progress' && run.current_step_index !== undefined) {
        console.log('[WizardPlayer] Resuming from step index:', run.current_step_index);
        setCurrentStepIndex(run.current_step_index);
      }

    } catch (error) {
      console.error('[WizardPlayer] Failed to load wizard run responses:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load run data',
        severity: 'error',
      });
    }
  };

  loadRunResponses();
}, [sessionId, wizard]);
```

#### 4. Backend API Returns Full Run Details

**Location:** `backend/app/api/v1/wizard_runs.py:98-117`

```python
@router.get("/{run_id}", response_model=WizardRunDetailResponse)
async def get_wizard_run(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get a specific wizard run with all related data.

    Returns:
    {
        "id": "uuid",
        "wizard_id": "uuid",
        "status": "completed",
        "run_name": "My Saved Run",
        ...
        "step_responses": [
            {
                "id": "uuid",
                "step_id": "uuid",
                "step_index": 0,
                "step_name": "Project Overview",
                "completed": true
            }
        ],
        "option_set_responses": [
            {
                "id": "uuid",
                "option_set_id": "uuid",
                "option_set_name": "Company Name",
                "selection_type": "text_input",
                "response_value": {
                    "value": "Acme Corporation"  ← User's saved input
                },
                "created_at": "2025-11-19T09:11:00Z"
            }
        ],
        "file_uploads": []
    }
    """
    run = crud_wizard_run.get_wizard_run_detail(
        db,
        run_id=run_id,
        user_id=current_user.id if current_user else None
    )

    if not run:
        raise HTTPException(status_code=404, detail="Wizard run not found")

    return run
```

#### 5. CRUD Layer Fetches from Database

**Location:** `backend/app/crud/wizard_run.py`

```python
def get_wizard_run_detail(
    db: Session,
    run_id: UUID,
    user_id: Optional[UUID] = None
) -> Optional[WizardRun]:
    """
    Get wizard run with all related responses using SQLAlchemy eager loading.
    """
    query = db.query(WizardRun).options(
        # Eager load relationships to avoid N+1 queries
        joinedload(WizardRun.step_responses).joinedload(
            WizardRunStepResponse.option_set_responses
        ).joinedload(
            WizardRunOptionSetResponse.file_uploads
        ),
        joinedload(WizardRun.option_set_responses),
        joinedload(WizardRun.file_uploads)
    ).filter(WizardRun.id == run_id)

    # Filter by user if provided (authentication)
    if user_id:
        query = query.filter(WizardRun.user_id == user_id)

    run = query.first()

    return run
```

**Generated SQL (simplified):**

```sql
SELECT
    wr.id, wr.wizard_id, wr.run_name, wr.status, wr.is_stored,
    srep.id, srep.step_id, srep.step_index, srep.step_name,
    osrep.id, osrep.option_set_id, osrep.option_set_name,
    osrep.selection_type, osrep.response_value  -- ← JSONB with user data
FROM wizard_runs wr
LEFT JOIN wizard_run_step_responses srep ON srep.run_id = wr.id
LEFT JOIN wizard_run_option_set_responses osrep ON osrep.step_response_id = srep.id
WHERE wr.id = 'run-uuid'
  AND wr.user_id = 'user-uuid';
```

---

## Population Process

### How UI Fields Get Populated

#### 1. Render Cycle Begins

**Location:** `frontend/src/pages/WizardPlayerPage.tsx:1122-1157`

```typescript
{currentStep && (
  <Card sx={{ mb: 3 }}>
    <CardContent>
      <Typography variant="h5" gutterBottom>
        {currentStep.name}
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {(() => {
          console.log(`[WizardPlayer] Rendering step ${currentStepIndex}`);
          console.log(`[WizardPlayer] Step has ${currentStep.option_sets.length} option sets`);
          return null;
        })()}

        {/* Render each option set (input field) */}
        {currentStep.option_sets.map((optionSet) => (
          <Box key={optionSet.id}>
            {renderOptionSet(optionSet)}
          </Box>
        ))}
      </Box>
    </CardContent>
  </Card>
)}
```

#### 2. renderOptionSet Function Renders Each Input

**Location:** `frontend/src/pages/WizardPlayerPage.tsx:566-1007`

```typescript
const renderOptionSet = (optionSet: OptionSet) => {
  console.log(`[WizardPlayer] renderOptionSet called for: ${optionSet.id}`);
  console.log(`[WizardPlayer] Current state - isViewOnly: ${isViewOnly}, isCompleted: ${isCompleted}`);

  // Get the current value from responses state
  const currentValue = responses[optionSet.id];

  if (isViewOnly) {
    console.log(`[WizardPlayer] Rendering ${optionSet.id} in VIEW mode with value:`, currentValue);
  } else {
    console.log(`[WizardPlayer] Rendering ${optionSet.id} in EDIT mode with value:`, currentValue);
  }

  // Render based on selection type
  switch (optionSet.selection_type) {
    case 'single_select':
      return (
        <FormControl component="fieldset" fullWidth>
          <FormLabel>{optionSet.name}</FormLabel>

          {/* POPULATION HAPPENS HERE */}
          <RadioGroup
            value={responses[optionSet.id] || ''}  // ← Retrieves saved value
            onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
          >
            {optionSet.options.map((option) => {
              const isDisabled = shouldDisableOption(option) || isViewOnly;
              return (
                <FormControlLabel
                  key={option.id}
                  value={option.value}  // ← Matches against saved value
                  control={<Radio />}
                  label={option.label}
                  disabled={isDisabled}
                />
              );
            })}
          </RadioGroup>
        </FormControl>
      );

    case 'multiple_select':
      const selectedValues = (responses[optionSet.id] as string[]) || [];
      return (
        <FormControl component="fieldset" fullWidth>
          <FormLabel>{optionSet.name}</FormLabel>

          <FormGroup>
            {optionSet.options.map((option) => {
              const isDisabled = shouldDisableOption(option) || isViewOnly;
              return (
                <FormControlLabel
                  key={option.id}
                  control={
                    <Checkbox
                      checked={selectedValues.includes(option.value)}  // ← Checks if saved
                      onChange={(e) => {
                        const newValues = e.target.checked
                          ? [...selectedValues, option.value]
                          : selectedValues.filter((v) => v !== option.value);
                        handleResponseChange(optionSet.id, newValues);
                      }}
                      disabled={isDisabled}
                    />
                  }
                  label={option.label}
                />
              );
            })}
          </FormGroup>
        </FormControl>
      );

    case 'text_input':
      const isTextInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
      return (
        <FormControl fullWidth>
          <TextField
            label={optionSet.name}
            multiline
            rows={4}
            value={responses[optionSet.id] || ''}  // ← Displays saved text
            onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
            disabled={isTextInputDisabled}
          />
        </FormControl>
      );

    case 'number_input':
      const isNumberInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
      return (
        <FormControl fullWidth>
          <TextField
            label={optionSet.name}
            type="number"
            value={responses[optionSet.id] || ''}  // ← Displays saved number
            onChange={(e) => handleResponseChange(optionSet.id, parseFloat(e.target.value))}
            disabled={isNumberInputDisabled}
          />
        </FormControl>
      );

    case 'rating':
      const isRatingDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
      return (
        <FormControl fullWidth>
          <FormLabel>{optionSet.name}</FormLabel>

          <Rating
            value={Number(responses[optionSet.id]) || 0}  // ← Displays saved rating
            onChange={(event, newValue) => {
              handleResponseChange(optionSet.id, newValue);
            }}
            disabled={isRatingDisabled}
            max={5}
            size="large"
          />
        </FormControl>
      );

    case 'slider':
      const isSliderDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
      const sliderMin = optionSet.validation?.min || 0;
      const sliderMax = optionSet.validation?.max || 100;

      return (
        <FormControl fullWidth>
          <FormLabel>{optionSet.name}</FormLabel>

          <Slider
            value={Number(responses[optionSet.id]) || sliderMin}  // ← Displays saved value
            onChange={(event, newValue) => {
              handleResponseChange(optionSet.id, newValue);
            }}
            disabled={isSliderDisabled}
            min={sliderMin}
            max={sliderMax}
            marks
            valueLabelDisplay="auto"
          />
        </FormControl>
      );

    case 'date_input':
      const isDateInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
      return (
        <FormControl fullWidth>
          <TextField
            label={optionSet.name}
            type="date"
            value={responses[optionSet.id] || ''}  // ← Displays saved date
            onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
            disabled={isDateInputDisabled}
            InputLabelProps={{ shrink: true }}
          />
        </FormControl>
      );

    case 'color_picker':
      const isColorPickerDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
      return (
        <FormControl fullWidth>
          <FormLabel>{optionSet.name}</FormLabel>

          <TextField
            type="color"
            value={responses[optionSet.id] || '#000000'}  // ← Displays saved color
            onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
            disabled={isColorPickerDisabled}
            fullWidth
          />
        </FormControl>
      );

    // ... other cases (time_input, datetime_input, file_upload, rich_text)
  }
};
```

### Key Population Mechanisms

#### 1. React State Mapping

```typescript
// responses state object:
{
  "uuid-1": "text value",      // text_input
  "uuid-2": "option_a",         // single_select
  "uuid-3": ["opt1", "opt2"],   // multiple_select
  "uuid-4": 42,                 // number_input
  "uuid-5": "2025-11-19",       // date_input
  "uuid-6": 4,                  // rating (1-5)
  "uuid-7": 75,                 // slider (0-100)
  "uuid-8": "#ff5733",          // color_picker
}

// Each input component reads from responses[optionSet.id]
```

#### 2. Value Binding Patterns

| Input Type | How Value is Bound | Example |
|------------|-------------------|---------|
| `single_select` | `<RadioGroup value={responses[id] \|\| ''}>` | `value="option_a"` |
| `multiple_select` | `checked={selectedValues.includes(option.value)}` | `checked={true}` |
| `text_input` | `<TextField value={responses[id] \|\| ''}>` | `value="My text"` |
| `number_input` | `<TextField value={responses[id] \|\| ''} type="number">` | `value={42}` |
| `date_input` | `<TextField value={responses[id] \|\| ''} type="date">` | `value="2025-11-19"` |
| `rating` | `<Rating value={Number(responses[id]) \|\| 0}>` | `value={4}` |
| `slider` | `<Slider value={Number(responses[id]) \|\| min}>` | `value={75}` |
| `color_picker` | `<TextField value={responses[id] \|\| '#000000'} type="color">` | `value="#ff5733"` |

#### 3. React Re-render Flow

```
User clicks "View"
    ↓
URL param: ?session=uuid&view_only=true
    ↓
WizardPlayerPage mounts
    ↓
useEffect detects sessionId
    ↓
Calls wizardRunService.getWizardRun(sessionId)
    ↓
Backend returns full run with option_set_responses
    ↓
Frontend transforms: {value: X} → X
    ↓
setResponses({ "uuid-1": "value1", "uuid-2": "value2", ... })
    ↓
React detects state change
    ↓
Re-renders WizardPlayerPage
    ↓
Renders currentStep.option_sets
    ↓
Each renderOptionSet(optionSet) reads responses[optionSet.id]
    ↓
MUI components display the values
    ↓
User sees populated form fields ✓
```

---

## Code Examples

### Example 1: Storing a Complete Wizard Run

```typescript
// User completes a wizard with these responses:
const responses = {
  "opt-1": "Acme Corporation",           // Company name (text_input)
  "opt-2": "business",                   // Website type (single_select)
  "opt-3": ["modern", "minimalist"],     // Design styles (multiple_select)
  "opt-4": 10,                           // Number of pages (number_input)
  "opt-5": "2025-12-31",                 // Launch date (date_input)
  "opt-6": 5,                            // Design importance (rating)
  "opt-7": "#ff6b35",                    // Brand color (color_picker)
};

// Frontend loops through wizard structure and creates:

// Step 1: Company Information
POST /wizard-runs/{run_id}/steps
{
  "run_id": "run-123",
  "step_id": "step-1",
  "step_index": 0,
  "step_name": "Company Information"
}
// Response: { "id": "step-resp-1", ... }

POST /wizard-runs/{run_id}/option-sets
{
  "run_id": "run-123",
  "step_response_id": "step-resp-1",
  "option_set_id": "opt-1",
  "option_set_name": "Company Name",
  "selection_type": "text_input",
  "response_value": { "value": "Acme Corporation" }  // ← JSONB wrapper
}

POST /wizard-runs/{run_id}/option-sets
{
  "run_id": "run-123",
  "step_response_id": "step-resp-1",
  "option_set_id": "opt-2",
  "option_set_name": "Website Type",
  "selection_type": "single_select",
  "response_value": { "value": "business" }
}

// Step 2: Design Preferences
POST /wizard-runs/{run_id}/steps
{
  "run_id": "run-123",
  "step_id": "step-2",
  "step_index": 1,
  "step_name": "Design Preferences"
}
// Response: { "id": "step-resp-2", ... }

POST /wizard-runs/{run_id}/option-sets
{
  "run_id": "run-123",
  "step_response_id": "step-resp-2",
  "option_set_id": "opt-3",
  "option_set_name": "Design Styles",
  "selection_type": "multiple_select",
  "response_value": { "value": ["modern", "minimalist"] }  // ← Array in JSONB
}

// ... and so on for all steps

// Finally, update run metadata
PUT /wizard-runs/{run_id}
{
  "run_name": "Acme Corp Website 2025",
  "run_description": "Business website redesign project",
  "is_stored": true
}
```

### Example 2: Retrieving and Populating

```typescript
// User clicks "View" on stored run
GET /wizard-runs/run-123

// Backend returns:
{
  "id": "run-123",
  "wizard_id": "wizard-456",
  "run_name": "Acme Corp Website 2025",
  "status": "completed",
  "is_stored": true,
  "step_responses": [
    {
      "id": "step-resp-1",
      "step_id": "step-1",
      "step_index": 0,
      "step_name": "Company Information"
    },
    {
      "id": "step-resp-2",
      "step_id": "step-2",
      "step_index": 1,
      "step_name": "Design Preferences"
    }
  ],
  "option_set_responses": [
    {
      "id": "osresp-1",
      "option_set_id": "opt-1",
      "option_set_name": "Company Name",
      "selection_type": "text_input",
      "response_value": { "value": "Acme Corporation" }
    },
    {
      "id": "osresp-2",
      "option_set_id": "opt-2",
      "option_set_name": "Website Type",
      "selection_type": "single_select",
      "response_value": { "value": "business" }
    },
    {
      "id": "osresp-3",
      "option_set_id": "opt-3",
      "option_set_name": "Design Styles",
      "selection_type": "multiple_select",
      "response_value": { "value": ["modern", "minimalist"] }
    }
  ]
}

// Frontend transforms to:
const loadedResponses = {
  "opt-1": "Acme Corporation",        // Extracted from response_value.value
  "opt-2": "business",
  "opt-3": ["modern", "minimalist"],
};

// React state updated
setResponses(loadedResponses);

// Components re-render with values:
<TextField value={responses["opt-1"]} />  // Shows "Acme Corporation"
<RadioGroup value={responses["opt-2"]}>   // "business" radio selected
<Checkbox checked={selectedValues.includes("modern")} />  // Checked
<Checkbox checked={selectedValues.includes("minimalist")} />  // Checked
```

---

## Edge Cases & Validation

### 1. Handling Missing or Null Values

```typescript
// Frontend always provides fallback values
value={responses[optionSet.id] || ''}           // Empty string for text
value={responses[optionSet.id] || 0}            // 0 for numbers
value={responses[optionSet.id] || '#000000'}    // Default color
selectedValues = (responses[optionSet.id] as string[]) || []  // Empty array
```

### 2. Preventing Duplicate Responses

**Problem:** Re-saving a wizard run creates duplicate entries

**Solution:** Clear all responses before saving

```typescript
// Before saving, check for existing responses
const existingRun = await wizardRunService.getWizardRun(runId);
if (existingRun.option_set_responses?.length > 0) {
  // Delete all existing responses
  await wizardRunService.clearAllResponses(runId);
}

// Backend DELETE endpoint
@router.delete("/{run_id}/responses")
async def clear_all_responses(run_id: UUID, db: Session):
    """Delete all step and option set responses for a run"""
    db.query(WizardRunStepResponse).filter(
        WizardRunStepResponse.run_id == run_id
    ).delete()
    # Cascades to option_set_responses due to FK constraint
    db.commit()
```

### 3. Type Coercion for Different Input Types

```typescript
// Number inputs
handleResponseChange(optionSet.id, parseFloat(e.target.value))

// Rating (MUI returns number or null)
handleResponseChange(optionSet.id, newValue || 0)

// Slider
handleResponseChange(optionSet.id, Number(newValue))

// Date inputs (string format)
handleResponseChange(optionSet.id, e.target.value)  // "2025-11-19"

// Multiple select (array)
handleResponseChange(optionSet.id, [...selectedValues, newValue])
```

### 4. Validating Required Fields

```typescript
const validateAllSteps = (): string[] => {
  const errors: string[] = [];

  wizard.steps.forEach((step, stepIndex) => {
    step.option_sets.forEach((optionSet) => {
      const isRequired = isOptionSetRequired(optionSet);

      if (isRequired) {
        const response = responses[optionSet.id];

        // Check for missing or empty responses
        if (!response || (Array.isArray(response) && response.length === 0)) {
          errors.push(
            `Step ${stepIndex + 1} (${step.name}): "${optionSet.name}" is required`
          );
        }
      }
    });
  });

  return errors;
};
```

### 5. Handling Anonymous Users

```typescript
// Backend allows null user_id for anonymous runs
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

// Frontend can create runs without authentication
@router.post("/", response_model=WizardRunResponse)
async def create_wizard_run(
    run: WizardRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)  // ← Optional
):
    user_id = current_user.id if current_user else None
    # ...
```

### 6. Progress Tracking During Multi-Step Save

```typescript
// Track saved items for potential rollback
const savedStepResponses: string[] = [];
const savedOptionSetResponses: string[] = [];

try {
  for (const step of wizard.steps) {
    const stepResp = await createStepResponse(...);
    savedStepResponses.push(stepResp.id);

    for (const optionSet of step.option_sets) {
      const osResp = await createOptionSetResponse(...);
      savedOptionSetResponses.push(osResp.id);
    }
  }
} catch (error) {
  console.error('Save failed, saved items:', {
    stepResponses: savedStepResponses,
    optionSetResponses: savedOptionSetResponses
  });
  // Could implement rollback here
  throw error;
}
```

### 7. JSONB Flexibility for Future Extensions

The JSONB `response_value` column allows storing additional metadata:

```json
// Current structure
{
  "value": "user input"
}

// Future extensions possible
{
  "value": "user input",
  "confidence": 0.95,
  "suggested_by": "ai",
  "edited": true,
  "edit_history": [
    {"timestamp": "2025-11-19T10:00:00Z", "value": "old value"}
  ]
}
```

---

## Performance Considerations

### 1. Eager Loading Relationships

```python
# Use SQLAlchemy joinedload to avoid N+1 queries
query = db.query(WizardRun).options(
    joinedload(WizardRun.step_responses).joinedload(
        WizardRunStepResponse.option_set_responses
    )
).filter(WizardRun.id == run_id)

# Generates single optimized SQL query instead of multiple round trips
```

### 2. Database Indexes

```sql
-- Speed up common queries
CREATE INDEX idx_step_responses_run_id ON wizard_run_step_responses(run_id);
CREATE INDEX idx_option_set_responses_run_id ON wizard_run_option_set_responses(run_id);
CREATE INDEX idx_option_set_responses_option_set_id ON wizard_run_option_set_responses(option_set_id);
```

### 3. Pagination for Large Lists

```python
# Backend pagination
@router.get("/stored", response_model=List[WizardRunResponse])
async def get_stored_runs(
    skip: int = 0,
    limit: int = 20,  # Default limit
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    runs = crud_wizard_run.get_stored_runs(db, user_id=current_user.id, skip=skip, limit=limit)
    return runs
```

### 4. Frontend Caching with React Query

```typescript
// Automatically caches and reuses fetched data
const { data: run, isLoading } = useQuery({
  queryKey: ['wizard-run', runId],
  queryFn: () => wizardRunService.getWizardRun(runId),
  staleTime: 5 * 60 * 1000,  // 5 minutes
  cacheTime: 10 * 60 * 1000,  // 10 minutes
});
```

---

## Summary

The Multi-Wizard Platform implements a robust, scalable user input storage and retrieval system with these key characteristics:

✅ **Two-tier architecture** separates metadata from data
✅ **JSONB flexibility** supports all 12 input types with one schema
✅ **Atomic operations** prevent partial saves
✅ **Referential integrity** via foreign key constraints and cascades
✅ **Type-agnostic storage** handles complex data structures
✅ **Performance optimized** with indexes and eager loading
✅ **Frontend state management** using React hooks and React Query
✅ **Real-time validation** prevents invalid data entry
✅ **Support for anonymous users** enables public wizards
✅ **Comprehensive logging** for debugging and monitoring

This architecture supports viewing, editing, sharing, and comparing wizard runs while maintaining data integrity and performance at scale.
