Complete Wizard Lifecycle System - Implementation Specification
Delete all "My Session" and "My Template" tables and code concepts.
We will re-engineer this as a complete wizard lifecycle system with five integrated components. Note: Wizard Builder already exists and is fully implemented (1,103 lines, located at frontend/src/pages/admin/WizardBuilderPage.tsx). We need to add the surrounding components to complete the lifecycle.

Complete Workflow Architecture
Wizard Template → Wizard Builder (✓ Implemented) → Run Wizard → Store Wizard → Play Wizard

1. Wizard Template (New Component - To Be Built)
Purpose
Provide a library of pre-built, ready-to-use wizard templates that serve as starting points for creating new wizards via the existing Wizard Builder.
Template Library Features
Template Categories:

Data Import & ETL Wizards
Configuration & Setup Wizards
Form & Survey Wizards
Product Configuration Wizards
Workflow & Approval Wizards
Integration & API Setup Wizards
Onboarding & Training Wizards

Template Properties:
typescriptinterface WizardTemplate {
  id: string;
  template_name: string;
  template_description: string;
  category: string;
  icon: string;
  difficulty_level: 'easy' | 'medium' | 'hard';
  estimated_time: number;
  tags: string[];
  preview_image?: string;
  step_count: number;
  option_set_count: number;
  is_system_template: boolean; // Cannot be deleted
  created_by: 'system' | 'admin';
  created_at: Date;
  usage_count: number;
  rating: number;
  wizard_structure: WizardData; // Complete wizard JSON
}
UI Components
Template Gallery View:

Grid/List toggle view
Filter by category, difficulty, tags
Search functionality
Sort by: popularity, rating, newest, name
Template cards showing:

Template name and icon
Brief description
Difficulty badge
Estimated time
Step count
Usage statistics
Rating (stars)
"Preview" and "Use Template" buttons



Template Preview Modal:

Full template details
Step-by-step structure preview
Option sets and fields overview
Sample screenshots/mockups
User ratings and reviews
"Use This Template" button (redirects to Wizard Builder)
"Clone & Customize" button

Template Actions:

Preview: View complete template structure without opening builder
Use Template: Clone template and open in Wizard Builder
Clone & Customize: Create editable copy with new name
Rate Template: 5-star rating system (for used templates)
Report Template: Flag inappropriate/broken templates

System Templates (Pre-built, Read-Only)
Example: SQL Data Import Wizard
typescript{
  template_name: "SQL Data Import & Execution Wizard",
  category: "Data Import & ETL",
  icon: "🗄️",
  difficulty_level: "medium",
  estimated_time: 20,
  is_system_template: true,
  wizard_structure: {
    name: "SQL File Import & Execute",
    description: "Import SQL files and execute them against your database",
    steps: [
      {
        name: "Select Database Connection",
        step_order: 1,
        option_sets: [
          {
            name: "Database Type",
            selection_type: "single_select",
            is_required: true,
            options: [
              { label: "SQL Server", value: "sqlserver" },
              { label: "PostgreSQL", value: "postgresql" },
              { label: "MySQL", value: "mysql" },
              { label: "Oracle", value: "oracle" }
            ]
          },
          {
            name: "Connection String",
            selection_type: "text_input",
            is_required: true,
            placeholder: "Server=localhost;Database=mydb;..."
          }
        ]
      },
      {
        name: "Upload SQL Files",
        step_order: 2,
        option_sets: [
          {
            name: "SQL Files",
            selection_type: "file_upload",
            is_required: true,
            help_text: "Upload .sql files to execute"
          },
          {
            name: "Execution Order",
            selection_type: "single_select",
            options: [
              { label: "Alphabetical", value: "alpha" },
              { label: "Manual Order", value: "manual" }
            ]
          }
        ]
      },
      {
        name: "Execution Options",
        step_order: 3,
        option_sets: [
          {
            name: "Transaction Mode",
            selection_type: "single_select",
            options: [
              { label: "Single Transaction (Rollback on Error)", value: "single" },
              { label: "Per-File Transaction", value: "perfile" },
              { label: "No Transaction", value: "none" }
            ]
          },
          {
            name: "Error Handling",
            selection_type: "single_select",
            options: [
              { label: "Stop on First Error", value: "stop" },
              { label: "Continue on Error", value: "continue" },
              { label: "Prompt on Error", value: "prompt" }
            ]
          }
        ]
      }
    ]
  }
}
Database Schema
sql-- New table for wizard templates
CREATE TABLE wizard_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(255) NOT NULL,
    template_description TEXT,
    category VARCHAR(100),
    icon VARCHAR(50),
    difficulty_level VARCHAR(20),
    estimated_time INTEGER,
    tags TEXT[],
    preview_image TEXT,
    step_count INTEGER,
    option_set_count INTEGER,
    is_system_template BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0,
    wizard_structure JSONB NOT NULL, -- Complete wizard JSON
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard'))
);

-- Template ratings
CREATE TABLE wizard_template_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES wizard_templates(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, user_id)
);

-- Indexes for performance
CREATE INDEX idx_wizard_templates_category ON wizard_templates(category);
CREATE INDEX idx_wizard_templates_system ON wizard_templates(is_system_template);
CREATE INDEX idx_wizard_templates_usage ON wizard_templates(usage_count DESC);
CREATE INDEX idx_wizard_templates_rating ON wizard_templates(average_rating DESC);
API Endpoints
typescript// Template Management
GET    /api/v1/wizard-templates              // List all templates
GET    /api/v1/wizard-templates/:id          // Get template details
POST   /api/v1/wizard-templates              // Create new template (admin only)
PUT    /api/v1/wizard-templates/:id          // Update template (admin only)
DELETE /api/v1/wizard-templates/:id          // Delete template (admin only, non-system)
POST   /api/v1/wizard-templates/:id/clone    // Clone template to Wizard Builder
GET    /api/v1/wizard-templates/categories   // List template categories

// Template Ratings
POST   /api/v1/wizard-templates/:id/rate     // Rate a template
GET    /api/v1/wizard-templates/:id/ratings  // Get template ratings

// Template Usage Tracking
POST   /api/v1/wizard-templates/:id/use      // Increment usage count
Integration with Wizard Builder
Flow:

User browses Wizard Template gallery
User clicks "Use This Template" on a template
System clones template structure
System redirects to Wizard Builder with pre-populated data
Wizard Builder opens in "edit mode" with template content
User can modify and save as a new wizard

Implementation:
typescript// In Wizard Template component
const handleUseTemplate = async (templateId: string) => {
  try {
    // Clone template and get wizard structure
    const response = await templateService.cloneTemplate(templateId);
    const wizardData = response.wizard_structure;
    
    // Navigate to Wizard Builder with pre-populated data
    navigate('/admin/wizard-builder', {
      state: { 
        mode: 'create-from-template',
        templateData: wizardData,
        templateName: response.template_name
      }
    });
  } catch (error) {
    showError('Failed to load template');
  }
};
typescript// In Wizard Builder component (modify existing code)
const WizardBuilderPage = () => {
  const location = useLocation();
  const templateData = location.state?.templateData;
  
  // Initialize wizard state with template data if available
  useEffect(() => {
    if (templateData) {
      setWizard({
        ...templateData,
        name: `${templateData.name} (Copy)`, // Append "Copy" to template name
        is_published: false // Start as draft
      });
      setIsEditing(false); // New wizard mode
    }
  }, [templateData]);
  
  // Rest of existing Wizard Builder code...
};

2. Wizard Builder (✓ Already Implemented)
Current Implementation Status

Location: frontend/src/pages/admin/WizardBuilderPage.tsx
Lines of Code: 1,103 lines
Status: Fully functional and production-ready

Core Capabilities (Already Built)
Wizard Management:

✓ Create new wizards from scratch
✓ Edit existing wizards
✓ Clone wizards
✓ Delete wizards with confirmation
✓ Publish/unpublish wizards

Step Builder:

✓ Add unlimited steps
✓ Reorder steps with drag handles
✓ Configure step properties (name, description, help text)
✓ Required/optional flags
✓ Skippable configuration

Option Sets (12 Input Types Supported):

✓ Single Select (radio buttons)
✓ Multiple Select (checkboxes)
✓ Text Input
✓ Number Input
✓ Date Input
✓ Time Input
✓ DateTime Input
✓ Rating (1-5 stars)
✓ Slider (range)
✓ Color Picker
✓ File Upload
✓ Rich Text Editor

Conditional Logic:

✓ Show/Hide fields based on selections
✓ Enable/Disable fields conditionally
✓ Make fields required conditionally
✓ Cross-field dependencies via OptionDependencyManager

Publishing & Settings:

✓ Publish/draft mode
✓ Login requirements
✓ Template creation allowed
✓ Auto-save functionality
✓ Difficulty levels (Easy, Medium, Hard)
✓ Estimated completion time
✓ Tagging system

Required Enhancements for Template Integration
1. Template Mode Support
typescript// Add to existing WizardBuilderPage component
interface WizardBuilderState {
  mode: 'create' | 'edit' | 'create-from-template';
  sourceTemplateId?: string;
  sourceTemplateName?: string;
}

// Display template source info when in template mode
{mode === 'create-from-template' && (
  <Alert severity="info" sx={{ mb: 2 }}>
    Creating wizard from template: <strong>{sourceTemplateName}</strong>
    <br />
    You can modify any part of this wizard before saving.
  </Alert>
)}
2. Save as Template Feature
typescript// Add "Save as Template" button in Wizard Builder
const handleSaveAsTemplate = async () => {
  try {
    await templateService.createTemplate({
      template_name: `${wizard.name} Template`,
      template_description: wizard.description,
      category: wizard.category_id,
      wizard_structure: wizard,
      is_system_template: false,
      created_by: 'admin'
    });
    showSuccess('Wizard saved as template!');
  } catch (error) {
    showError('Failed to save as template');
  }
};

// Add button in action bar
<Button
  variant="outlined"
  onClick={handleSaveAsTemplate}
  disabled={!wizard.name || wizard.steps.length === 0}
>
  Save as Template
</Button>
3. Template Preview in Builder
typescript// Add preview mode toggle
const [isPreviewMode, setIsPreviewMode] = useState(false);

<Button
  variant="outlined"
  startIcon={<VisibilityIcon />}
  onClick={() => setIsPreviewMode(!isPreviewMode)}
>
  {isPreviewMode ? 'Exit Preview' : 'Preview Wizard'}
</Button>
Existing Database Schema (No Changes Needed)
The current wizard builder uses these tables (already implemented):

wizards - Main wizard configuration
wizard_steps - Step definitions
option_sets - Input field groups
options - Individual options for select types
option_dependencies - Conditional logic rules


3. Run Wizard (New Component - To Be Built)
Purpose
Provide the user-facing interface for executing published wizards step-by-step, capturing user input, and completing wizard runs.
Run Wizard Features
Execution Interface:

Step-by-step navigation (Previous, Next, Cancel)
Progress indicator showing current step (e.g., "Step 2 of 5")
Visual progress bar
Step validation before proceeding
Real-time field validation
Help text and tooltips
Auto-save progress (if enabled in wizard settings)

Session Management:
typescriptinterface WizardRun {
  id: string;
  wizard_id: string;
  user_id: string;
  run_name?: string; // Set when storing
  status: 'in_progress' | 'completed' | 'abandoned';
  current_step: number;
  started_at: Date;
  completed_at?: Date;
  duration_seconds?: number;
  is_stored: boolean; // Has user saved this run?
  responses: StepResponse[];
}

interface StepResponse {
  step_id: string;
  step_order: number;
  completed_at: Date;
  option_set_responses: OptionSetResponse[];
}

interface OptionSetResponse {
  option_set_id: string;
  option_set_name: string;
  selection_type: string;
  selected_values: any[]; // Array of selected option IDs or input values
  selected_labels: string[]; // Human-readable labels
  uploaded_files?: FileUpload[];
}
UI Components
Step Display:
typescript<WizardRunContainer>
  {/* Header */}
  <WizardHeader>
    <Typography variant="h4">{wizard.name}</Typography>
    <Typography variant="body2">{wizard.description}</Typography>
    <LinearProgress 
      variant="determinate" 
      value={(currentStep / totalSteps) * 100} 
    />
    <Typography>Step {currentStep} of {totalSteps}</Typography>
  </WizardHeader>

  {/* Current Step Content */}
  <StepContent>
    <Typography variant="h5">{currentStepData.name}</Typography>
    <Typography variant="body1">{currentStepData.description}</Typography>
    {currentStepData.help_text && (
      <Alert severity="info">{currentStepData.help_text}</Alert>
    )}
    
    {/* Render Option Sets */}
    {currentStepData.option_sets.map(optionSet => (
      <OptionSetRenderer 
        key={optionSet.id}
        optionSet={optionSet}
        value={responses[optionSet.id]}
        onChange={(value) => handleOptionSetChange(optionSet.id, value)}
        error={validationErrors[optionSet.id]}
      />
    ))}
  </StepContent>

  {/* Navigation */}
  <WizardActions>
    <Button 
      onClick={handlePrevious}
      disabled={currentStep === 1}
    >
      Previous
    </Button>
    
    {currentStepData.is_skippable && (
      <Button onClick={handleSkip}>
        Skip Step
      </Button>
    )}
    
    <Button onClick={handleCancel} color="error">
      Cancel
    </Button>
    
    {currentStep < totalSteps ? (
      <Button 
        variant="contained"
        onClick={handleNext}
        disabled={!isStepValid()}
      >
        Next
      </Button>
    ) : (
      <Button 
        variant="contained"
        onClick={handleComplete}
        disabled={!isStepValid()}
      >
        Complete
      </Button>
    )}
  </WizardActions>
</WizardRunContainer>
Completion Dialog:
typescript<Dialog open={showCompletionDialog}>
  <DialogTitle>Wizard Completed!</DialogTitle>
  <DialogContent>
    <Typography>
      You've successfully completed "{wizard.name}"
    </Typography>
    <TextField
      fullWidth
      label="Save this run with a name (optional)"
      value={runName}
      onChange={(e) => setRunName(e.target.value)}
      placeholder="e.g., Laptop Config - Gaming Setup"
      helperText="Give this run a memorable name to save it for future reference"
      margin="normal"
    />
    <TextField
      fullWidth
      multiline
      rows={3}
      label="Notes (optional)"
      value={runNotes}
      onChange={(e) => setRunNotes(e.target.value)}
      placeholder="Add any notes about this configuration..."
      margin="normal"
    />
  </DialogContent>
  <DialogActions>
    <Button onClick={handleExitWithoutSaving}>
      Exit Without Saving
    </Button>
    <Button 
      variant="contained"
      onClick={handleSaveAndExit}
      disabled={!runName.trim()}
    >
      Save & Exit
    </Button>
  </DialogActions>
</Dialog>
Database Schema
sql-- Wizard runs (execution sessions)
CREATE TABLE wizard_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    run_name VARCHAR(255), -- User-provided name when storing
    run_notes TEXT, -- User-provided notes
    status VARCHAR(20) DEFAULT 'in_progress',
    current_step INTEGER DEFAULT 1,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    is_stored BOOLEAN DEFAULT FALSE, -- Has user explicitly saved this run?
    stored_at TIMESTAMP,
    tags TEXT[],
    CONSTRAINT check_status CHECK (status IN ('in_progress', 'completed', 'abandoned'))
);

-- Step responses
CREATE TABLE wizard_run_step_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    step_id UUID REFERENCES wizard_steps(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_spent_seconds INTEGER
);

-- Option set responses
CREATE TABLE wizard_run_option_set_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    step_response_id UUID REFERENCES wizard_run_step_responses(id) ON DELETE CASCADE,
    option_set_id UUID REFERENCES option_sets(id) ON DELETE CASCADE,
    option_set_name VARCHAR(255),
    selection_type VARCHAR(50),
    response_data JSONB NOT NULL -- Stores selected values, labels, files, etc.
);

-- File uploads tracking
CREATE TABLE wizard_run_file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    option_set_response_id UUID REFERENCES wizard_run_option_set_responses(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_path TEXT,
    file_size BIGINT,
    file_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_wizard_runs_user ON wizard_runs(user_id);
CREATE INDEX idx_wizard_runs_wizard ON wizard_runs(wizard_id);
CREATE INDEX idx_wizard_runs_status ON wizard_runs(status);
CREATE INDEX idx_wizard_runs_stored ON wizard_runs(is_stored);
CREATE INDEX idx_wizard_runs_completed ON wizard_runs(completed_at DESC);
API Endpoints
typescript// Run Management
POST   /api/v1/wizard-runs/start              // Start new wizard run
GET    /api/v1/wizard-runs/:id                // Get run details
PUT    /api/v1/wizard-runs/:id/step           // Update current step
POST   /api/v1/wizard-runs/:id/response       // Save step response
POST   /api/v1/wizard-runs/:id/complete       // Mark run as complete
POST   /api/v1/wizard-runs/:id/store          // Store completed run
DELETE /api/v1/wizard-runs/:id                // Delete/abandon run

// User's Runs
GET    /api/v1/wizard-runs/my-runs            // Get current user's runs
GET    /api/v1/wizard-runs/stored             // Get user's stored runs only
GET    /api/v1/wizard-runs/in-progress        // Get user's incomplete runs
Key Features Implementation
1. Auto-Save Progress
typescript// Auto-save every 30 seconds if wizard has auto_save enabled
useEffect(() => {
  if (!wizard.auto_save) return;
  
  const interval = setInterval(async () => {
    if (hasUnsavedChanges) {
      await saveProgress();
    }
  }, 30000); // 30 seconds
  
  return () => clearInterval(interval);
}, [hasUnsavedChanges, wizard.auto_save]);
2. Step Validation
typescriptconst validateCurrentStep = () => {
  const errors = {};
  
  currentStepData.option_sets.forEach(optionSet => {
    if (optionSet.is_required && !responses[optionSet.id]) {
      errors[optionSet.id] = 'This field is required';
    }
    
    if (optionSet.selection_type === 'multiple_select') {
      const selectedCount = responses[optionSet.id]?.length || 0;
      if (selectedCount < optionSet.min_selections) {
        errors[optionSet.id] = `Select at least ${optionSet.min_selections} options`;
      }
      if (optionSet.max_selections && selectedCount > optionSet.max_selections) {
        errors[optionSet.id] = `Select at most ${optionSet.max_selections} options`;
      }
    }
  });
  
  setValidationErrors(errors);
  return Object.keys(errors).length === 0;
};
3. Conditional Dependencies Evaluation
typescriptconst evaluateDependencies = (optionSetId: string) => {
  const optionSet = currentStepData.option_sets.find(os => os.id === optionSetId);
  
  optionSet.options.forEach(option => {
    option.dependencies.forEach(dep => {
      const dependsOnValue = responses[dep.depends_on_option_set_id];
      
      switch (dep.dependency_type) {
        case 'show_if':
          setOptionVisibility(option.id, dependsOnValue === dep.depends_on_option_id);
          break;
        case 'hide_if':
          setOptionVisibility(option.id, dependsOnValue !== dep.depends_on_option_id);
          break;
        case 'require_if':
          setOptionRequired(option.id, dependsOnValue === dep.depends_on_option_id);
          break;
        case 'disable_if':
          setOptionDisabled(option.id, dependsOnValue === dep.depends_on_option_id);
          break;
      }
    });
  });
};

4. Store Wizard (New Component - To Be Built)
Purpose
Provide a repository for users to view, manage, and replay their stored wizard runs with full details.
Store Wizard Features
Repository View:

List all stored runs for the current user
Search and filter capabilities
Sort options (date, name, wizard type, duration)
Grid/List view toggle
Pagination for large datasets

Run Details Display:
typescriptinterface StoredRunDisplay {
  run_id: string;
  run_name: string;
  run_notes?: string;
  wizard_name: string;
  wizard_icon: string;
  executed_by: string;
  execution_date: Date;
  completion_time: string; // e.g., "15 min 30 sec"
  total_steps: number;
  tags: string[];
  status: 'completed';
}
UI Components
Repository Grid:
typescript<Box sx={{ p: 3 }}>
  {/* Header */}
  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
    <Typography variant="h4">Stored Wizard Runs</Typography>
    <Box>
      <TextField
        size="small"
        placeholder="Search runs..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: <SearchIcon />
        }}
      />
      <ToggleButtonGroup value={viewMode}>
        <ToggleButton value="grid">
          <GridViewIcon />
        </ToggleButton>
        <ToggleButton value="list">
          <ListViewIcon />
        </ToggleButton>
      </ToggleButtonGroup>
    </Box>
  </Box>

  {/* Filters */}
  <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
    <FormControl size="small" sx={{ minWidth: 200 }}>
      <InputLabel>Filter by Wizard</InputLabel>
      <Select
        value={filterWizard}
        onChange={(e) => setFilterWizard(e.target.value)}
      >
        <MenuItem value="">All Wizards</MenuItem>
        {wizards.map(w => (
          <MenuItem key={w.id} value={w.id}>{w.name}</MenuItem>
        ))}
      </Select>
    </FormControl>
    
    <FormControl size="small" sx={{ minWidth: 150 }}>
      <InputLabel>Sort By</InputLabel>
      <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <MenuItem value="date_desc">Newest First</MenuItem>
        <MenuItem value="date_asc">Oldest First</MenuItem>
        <MenuItem value="name_asc">Name A-Z</MenuItem>
        <MenuItem value="duration_desc">Longest First</MenuItem>
      </Select>
    </FormControl>
  </Box>

  {/* Run Cards */}
  <Grid container spacing={2}>
    {storedRuns.map(run => (
      <Grid item xs={12} md={6} lg={4} key={run.id}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography variant="h2" sx={{ mr: 1 }}>
                {run.wizard_icon}
              </Typography>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6">{run.run_name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {run.wizard_name}
                </Typography>
              </Box>
              <Chip label="Completed" color="success" size="small" />
            </Box>
            
            <Divider sx={{ my: 1 }} />
            
            <Box sx={{ display: 'flex', gap: 2, my: 1 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Executed
                </Typography>
                <Typography variant="body2">
                  {formatDate(run.execution_date)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Duration
                </Typography>
                <Typography variant="body2">
                  {run.completion_time}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Steps
                </Typography>
                <Typography variant="body2">
                  {run.total_steps}
                </Typography>
              </Box>
            </Box>
            
            {run.tags.length > 0 && (
              <Box sx={{ mt: 1 }}>
                {run.tags.map(tag => (
                  <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5 }} />
                ))}
              </Box>
            )}
            
            {run.run_notes && (
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ mt: 1, fontStyle: 'italic' }}
              >
                {run.run_notes}
              </Typography>
            )}
          </CardContent>
          
          <CardActions>
            <Button 
              size="small" 
              startIcon={<PlayIcon />}
              onClick={() => handlePlayRun(run.id)}
            >
              Play
            </Button>
            <Button 
              size="small" 
              startIcon={<DownloadIcon />}
              onClick={() => handleExportRun(run.id)}
            >
              Export
            </Button>
            <IconButton 
              size="small"
              onClick={() => handleShareRun(run.id)}
            >
              <ShareIcon />
            </IconButton>
            <IconButton 
              size="small"
              onClick={() => handleDeleteRun(run.id)}
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          </CardActions>
        </Card>
      </Grid>
    ))}
  </Grid>
</Box>
Actions on Stored Runs
1. Play (View Details)

Navigate to Play Wizard component
Pass run ID for playback

2. Export
typescriptconst exportFormats = ['PDF', 'JSON', 'CSV', 'Excel'];

const handleExportRun = async (runId: string, format: string) => {
  try {
    const response = await runService.exportRun(runId, format);
    downloadFile(response.data, `wizard-run-${runId}.${format.toLowerCase()}`);
  } catch (error) {
    showError('Export failed');
  }
};
3. Share
typescript<Dialog open={showShareDialog}>
  <DialogTitle>Share Wizard Run</DialogTitle>
  <DialogContent>
    <FormControl fullWidth>
      <InputLabel>Share With</InputLabel>
      <Select multiple value={shareWithUsers}>
        {users.map(user => (
          <MenuItem key={user.id} value={user.id}>
            {user.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
    <FormControlLabel
      control={<Checkbox />}
      label="Allow recipients to export"
    />
    <FormControlLabel
      control={<Checkbox />}
      label="Notify recipients via email"
    />
  </DialogContent>
  <DialogActions>
    <Button onClick={handleCancelShare}>Cancel</Button>
    <Button variant="contained" onClick={handleConfirmShare}>
      Share
    </Button>
  </DialogActions>
</Dialog>
4. Compare Runs
typescript// Side-by-side comparison
<CompareRunsView>
  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
    <RunComparisonPanel run={run1} />
    <RunComparisonPanel run={run2} />
  </Box>
  
  <DifferenceHighlight>
    {/* Highlight different selections */}
    {differences.map(diff => (
      <Alert severity="info" key={diff.stepId}>
        Step "{diff.stepName}": Different selections in {diff.optionSetName}
      </Alert>
    ))}
  </DifferenceHighlight>
</CompareRunsView>
5. Add Notes (Post-Completion)
typescriptconst handleAddNotes = async (runId: string, notes: string) => {
  try {
    await runService.updateRunNotes(runId, notes);
    showSuccess('Notes added successfully');
  } catch (error) {
    showError('Failed to add notes');
  }
};
Database Extensions
sql-- Add sharing capability
CREATE TABLE wizard_run_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    shared_by UUID REFERENCES users(id) ON DELETE CASCADE,
    shared_with UUID REFERENCES users(id) ON DELETE CASCADE,
    can_export BOOLEAN DEFAULT FALSE,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(run_id, shared_with)
);

-- Run comparisons tracking
CREATE TABLE wizard_run_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    run_id_1 UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    run_id_2 UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_run_shares_with ON wizard_run_shares(shared_with);
CREATE INDEX idx_run_shares_by ON wizard_run_shares(shared_by);
API Endpoints
typescript// Stored Runs Management
GET    /api/v1/stored-runs                    // List user's stored runs
GET    /api/v1/stored-runs/:id                // Get stored run details
DELETE /api/v1/stored-runs/:id                // Delete stored run
PUT    /api/v1/stored-runs/:id/notes          // Update run notes
GET    /api/v1/stored-runs/:id/export         // Export run (PDF/JSON/CSV)

// Sharing
POST   /api/v1/stored-runs/:id/share          // Share run with users
GET    /api/v1/stored-runs/shared-with-me     // Get runs shared with user
DELETE /api/v1/stored-runs/shares/:shareId    // Revoke share

// Comparison
POST   /api/v1/stored-runs/compare            // Compare two runs
GET    /api/v1/stored-runs/comparisons        // Get user's comparison history

5. Play Wizard (New Component - To Be Built)
Purpose
Provide an interactive playback/replay interface that auto-plays through a stored wizard run, displaying all steps, user inputs, and selections in a read-only, visual format.
Play Wizard Features
Playback Interface:

Auto-play mode with configurable speed
Manual step navigation
Visual timeline/progress bar
Read-only display of all inputs
Highlighted user selections
Uploaded file previews
Step-by-step annotations

Playback Controls
typescriptinterface PlaybackControls {
  isPlaying: boolean;
  currentStep: number;
  totalSteps: number;
  playbackSpeed: 'slow' | 'normal' | 'fast'; // 2s, 1s, 0.5s per step
  canGoBack: boolean;
  canGoForward: boolean;
}
UI Components
Player Interface:
typescript<PlayWizardContainer>
  {/* Header with Run Info */}
  <Box sx={{ borderBottom: 1, borderColor: 'divider', p: 2 }}>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Box>
        <Typography variant="h5">{storedRun.run_name}</Typography>
        <Typography variant="caption" color="text.secondary">
          {storedRun.wizard_name} • Executed on {formatDate(storedRun.execution_date)}
        </Typography>
      </Box>
      <Chip label="PLAYBACK MODE" color="info" />
    </Box>
  </Box>

  {/* Timeline Progress */}
  <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
    <Stepper activeStep={currentStep - 1} alternativeLabel>
      {steps.map((step, index) => (
        <Step 
          key={step.id}
          completed={index < currentStep - 1}
          onClick={() => handleJumpToStep(index + 1)}
          sx={{ cursor: 'pointer' }}
        >
          <StepLabel>
            {step.name}
            <Typography variant="caption" display="block">
              {formatTime(step.completed_at)}
            </Typography>
          </StepLabel>
        </Step>
      ))}
    </Stepper>
  </Box>

  {/* Main Content Area */}
  <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
    {/* Step Content */}
    <Box sx={{ flex: 1, p: 3, overflow: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        {currentStepData.name}
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        {currentStepData.description}
      </Typography>
      
      {/* Display Option Sets with User Responses */}
      {currentStepData.option_sets.map((optionSet, index) => (
        <Card 
          key={optionSet.id} 
          sx={{ 
            mb: 2,
            border: 2,
            borderColor: 'primary.main',
            bgcolor: 'primary.50'
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircleIcon color="success" sx={{ mr: 1 }} />
              <Typography variant="h6">
                {optionSet.name}
                {optionSet.is_required && (
                  <Chip label="Required" size="small" sx={{ ml: 1 }} />
                )}
              </Typography>
            </Box>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {optionSet.description}
            </Typography>
            
            <Divider sx={{ my: 1 }} />
            
            {/* Display User Response */}
            <PlaybackResponseRenderer
              optionSet={optionSet}
              response={getResponse(optionSet.id)}
            />
          </CardContent>
        </Card>
      ))}
    </Box>

    {/* Sidebar with Metadata */}
    <Box 
      sx={{ 
        width: 300, 
        borderLeft: 1, 
        borderColor: 'divider',
        p: 2,
        bgcolor: 'background.default'
      }}
    >
      <Typography variant="h6" gutterBottom>Run Details</Typography>
      
      <List dense>
        <ListItem>
          <ListItemText 
            primary="Run Name"
            secondary={storedRun.run_name}
          />
        </ListItem>
        <ListItem>
          <ListItemText 
            primary="Executed By"
            secondary={storedRun.executed_by}
          />
        </ListItem>
        <ListItem>
          <ListItemText 
            primary="Date"
            secondary={formatFullDate(storedRun.execution_date)}
          />
        </ListItem>
        <ListItem>
          <ListItemText 
            primary="Duration"
            secondary={storedRun.completion_time}
          />
        </ListItem>
        <ListItem>
          <ListItemText 
            primary="Total Steps"
            secondary={storedRun.total_steps}
          />
        </ListItem>
      </List>
      
      {storedRun.run_notes && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>Notes</Typography>
          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
            {storedRun.run_notes}
          </Typography>
        </>
      )}
      
      {storedRun.tags.length > 0 && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>Tags</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {storedRun.tags.map(tag => (
              <Chip key={tag} label={tag} size="small" />
            ))}
          </Box>
        </>
      )}
    </Box>
  </Box>

  {/* Playback Controls */}
  <Box 
    sx={{ 
      borderTop: 1, 
      borderColor: 'divider', 
      p: 2,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      bgcolor: 'background.paper'
    }}
  >
    {/* Left: Speed Control */}
    <FormControl size="small" sx={{ minWidth: 120 }}>
      <InputLabel>Speed</InputLabel>
      <Select
        value={playbackSpeed}
        onChange={(e) => setPlaybackSpeed(e.target.value)}
      >
        <MenuItem value="slow">Slow (2s)</MenuItem>
        <MenuItem value="normal">Normal (1s)</MenuItem>
        <MenuItem value="fast">Fast (0.5s)</MenuItem>
      </Select>
    </FormControl>

    {/* Center: Transport Controls */}
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Button
        variant="outlined"
        startIcon={<FirstPageIcon />}
        onClick={handleGoToFirst}
        disabled={currentStep === 1}
      >
        First
      </Button>
      
      <Button
        variant="outlined"
        startIcon={<NavigateBeforeIcon />}
        onClick={handlePrevStep}
        disabled={currentStep === 1}
      >
        Previous
      </Button>
      
      <Button
        variant="contained"
        startIcon={isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
        onClick={handleTogglePlayPause}
        size="large"
      >
        {isPlaying ? 'Pause' : 'Play'}
      </Button>
      
      <Button
        variant="outlined"
        endIcon={<NavigateNextIcon />}
        onClick={handleNextStep}
        disabled={currentStep === totalSteps}
      >
        Next
      </Button>
      
      <Button
        variant="outlined"
        endIcon={<LastPageIcon />}
        onClick={handleGoToLast}
        disabled={currentStep === totalSteps}
      >
        Last
      </Button>
    </Box>

    {/* Right: Export & Close */}
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Button
        variant="outlined"
        startIcon={<FullscreenIcon />}
        onClick={handleToggleFullscreen}
      >
        Fullscreen
      </Button>
      
      <Button
        variant="outlined"
        startIcon={<DownloadIcon />}
        onClick={handleExportPDF}
      >
        Export PDF
      </Button>
      
      <Button
        variant="outlined"
        startIcon={<PrintIcon />}
        onClick={handlePrint}
      >
        Print
      </Button>
      
      <Button
        onClick={handleClose}
      >
        Close
      </Button>
    </Box>
  </Box>
</PlayWizardContainer>
Response Renderers (Read-Only Display)
typescriptconst PlaybackResponseRenderer: React.FC<{
  optionSet: OptionSetData;
  response: OptionSetResponse;
}> = ({ optionSet, response }) => {
  
  switch (optionSet.selection_type) {
    case 'single_select':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Selected Option:
          </Typography>
          <Chip 
            label={response.selected_labels[0]}
            color="primary"
            icon={<CheckCircleIcon />}
            sx={{ mt: 1 }}
          />
        </Box>
      );
    
    case 'multiple_select':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Selected Options ({response.selected_values.length}):
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
            {response.selected_labels.map((label, idx) => (
              <Chip 
                key={idx}
                label={label}
                color="primary"
                icon={<CheckCircleIcon />}
              />
            ))}
          </Box>
        </Box>
      );
    
    case 'text_input':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            User Input:
          </Typography>
          <Paper 
            variant="outlined" 
            sx={{ 
              p: 2, 
              bgcolor: 'grey.100',
              fontFamily: 'monospace'
            }}
          >
            {response.selected_values[0]}
          </Paper>
        </Box>
      );
    
    case 'number_input':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Value:
          </Typography>
          <Typography variant="h4" color="primary" sx={{ mt: 1 }}>
            {response.selected_values[0]}
          </Typography>
        </Box>
      );
    
    case 'date_input':
    case 'time_input':
    case 'datetime_input':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Selected Date/Time:
          </Typography>
          <Chip 
            label={formatDateTime(response.selected_values[0])}
            color="primary"
            icon={<EventIcon />}
            sx={{ mt: 1 }}
          />
        </Box>
      );
    
    case 'rating':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Rating:
          </Typography>
          <Rating 
            value={response.selected_values[0]}
            readOnly
            size="large"
            sx={{ mt: 1 }}
          />
        </Box>
      );
    
    case 'slider':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Selected Value:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Slider 
              value={response.selected_values[0]}
              disabled
              sx={{ mr: 2 }}
            />
            <Typography variant="h6" color="primary">
              {response.selected_values[0]}
            </Typography>
          </Box>
        </Box>
      );
    
    case 'color_picker':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Selected Color:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Box 
              sx={{ 
                width: 60, 
                height: 60, 
                bgcolor: response.selected_values[0],
                border: 2,
                borderColor: 'grey.400',
                borderRadius: 1,
                mr: 2
              }}
            />
            <Typography variant="h6" fontFamily="monospace">
              {response.selected_values[0]}
            </Typography>
          </Box>
        </Box>
      );
    
    case 'file_upload':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Uploaded Files ({response.uploaded_files?.length || 0}):
          </Typography>
          {response.uploaded_files?.map((file, idx) => (
            <Card key={idx} variant="outlined" sx={{ mb: 1 }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                <AttachFileIcon sx={{ mr: 2 }} />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body1">{file.file_name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatFileSize(file.file_size)} • {file.file_type}
                  </Typography>
                </Box>
                <Button 
                  size="small" 
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownloadFile(file)}
                >
                  Download
                </Button>
              </CardContent>
            </Card>
          ))}
        </Box>
      );
    
    case 'rich_text':
      return (
        <Box>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Content:
          </Typography>
          <Paper 
            variant="outlined" 
            sx={{ p: 2, bgcolor: 'grey.50' }}
          >
            <div dangerouslySetInnerHTML={{ __html: response.selected_values[0] }} />
          </Paper>
        </Box>
      );
    
    default:
      return (
        <Typography>
          {JSON.stringify(response.selected_values)}
        </Typography>
      );
  }
};
Auto-Play Logic
typescriptconst useAutoPlay = (
  isPlaying: boolean,
  currentStep: number,
  totalSteps: number,
  playbackSpeed: 'slow' | 'normal' | 'fast',
  onStepChange: (step: number) => void
) => {
  useEffect(() => {
    if (!isPlaying || currentStep >= totalSteps) return;
    
    const delays = {
      slow: 2000,
      normal: 1000,
      fast: 500
    };
    
    const timer = setTimeout(() => {
      onStepChange(currentStep + 1);
    }, delays[playbackSpeed]);
    
    return () => clearTimeout(timer);
  }, [isPlaying, currentStep, totalSteps, playbackSpeed, onStepChange]);
};

// Usage in component
const [isPlaying, setIsPlaying] = useState(false);
const [currentStep, setCurrentStep] = useState(1);

useAutoPlay(
  isPlaying,
  currentStep,
  totalSteps,
  playbackSpeed,
  (step) => {
    setCurrentStep(step);
    if (step >= totalSteps) {
      setIsPlaying(false); // Auto-stop at end
    }
  }
);
Export & Print Features
PDF Export:
typescriptconst handleExportPDF = async () => {
  try {
    const response = await runService.exportRunToPDF(runId);
    downloadFile(response.data, `${storedRun.run_name}.pdf`);
  } catch (error) {
    showError('PDF export failed');
  }
};

// Backend generates PDF with:
// - Run metadata
// - All steps with responses
// - Uploaded file listings
// - User notes and tags
Print View:
typescriptconst handlePrint = () => {
  window.print();
};

// Add print-specific CSS
<style>
  @media print {
    .no-print { display: none; }
    .playback-controls { display: none; }
    .page-break { page-break-after: always; }
  }
</style>
Video Recording (Advanced):
typescript// Use MediaRecorder API to record playback
const startRecording = () => {
  const canvas = document.querySelector('canvas');
  const stream = canvas.captureStream(30);
  const recorder = new MediaRecorder(stream);
  
  recorder.ondataavailable = (e) => {
    chunks.push(e.data);
  };
  
  recorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'video/webm' });
    downloadFile(blob, `${storedRun.run_name}_recording.webm`);
  };
  
  recorder.start();
};
API Endpoints
typescript// Playback
GET    /api/v1/play-wizard/:runId              // Get complete run data for playback
GET    /api/v1/play-wizard/:runId/step/:stepNum // Get specific step data
GET    /api/v1/play-wizard/:runId/files/:fileId // Download uploaded file

// Export
GET    /api/v1/play-wizard/:runId/export/pdf   // Generate and download PDF
GET    /api/v1/play-wizard/:runId/export/json  // Export as JSON

Complete Database Schema
sql-- ============================================
-- WIZARD TEMPLATES
-- ============================================
CREATE TABLE wizard_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(255) NOT NULL,
    template_description TEXT,
    category VARCHAR(100),
    icon VARCHAR(50),
    difficulty_level VARCHAR(20),
    estimated_time INTEGER,
    tags TEXT[],
    preview_image TEXT,
    step_count INTEGER,
    option_set_count INTEGER,
    is_system_template BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0,
    wizard_structure JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard'))
);

CREATE TABLE wizard_template_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES wizard_templates(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, user_id)
);

-- ============================================
-- EXISTING WIZARD BUILDER TABLES (No Changes)
-- ============================================
-- wizards
-- wizard_steps
-- option_sets
-- options
-- option_dependencies

-- ============================================
-- WIZARD RUNS (Execution)
-- ============================================
CREATE TABLE wizard_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    run_name VARCHAR(255),
    run_notes TEXT,
    status VARCHAR(20) DEFAULT 'in_progress',
    current_step INTEGER DEFAULT 1,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    is_stored BOOLEAN DEFAULT FALSE,
    stored_at TIMESTAMP,
    tags TEXT[],
    CONSTRAINT check_status CHECK (status IN ('in_progress', 'completed', 'abandoned'))
);

CREATE TABLE wizard_run_step_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    step_id UUID REFERENCES wizard_steps(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_spent_seconds INTEGER
);

CREATE TABLE wizard_run_option_set_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    step_response_id UUID REFERENCES wizard_run_step_responses(id) ON DELETE CASCADE,
    option_set_id UUID REFERENCES option_sets(id) ON DELETE CASCADE,
    option_set_name VARCHAR(255),
    selection_type VARCHAR(50),
    response_data JSONB NOT NULL
);

CREATE TABLE wizard_run_file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    option_set_response_id UUID REFERENCES wizard_run_option_set_responses(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_path TEXT,
    file_size BIGINT,
    file_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STORED WIZARD SHARING & COMPARISON
-- ============================================
CREATE TABLE wizard_run_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    shared_by UUID REFERENCES users(id) ON DELETE CASCADE,
    shared_with UUID REFERENCES users(id) ON DELETE CASCADE,
    can_export BOOLEAN DEFAULT FALSE,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(run_id, shared_with)
);

CREATE TABLE wizard_run_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    run_id_1 UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    run_id_2 UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================

-- Templates
CREATE INDEX idx_wizard_templates_category ON wizard_templates(category);
CREATE INDEX idx_wizard_templates_system ON wizard_templates(is_system_template);
CREATE INDEX idx_wizard_templates_usage ON wizard_templates(usage_count DESC);
CREATE INDEX idx_wizard_templates_rating ON wizard_templates(average_rating DESC);

-- Runs
CREATE INDEX idx_wizard_runs_user ON wizard_runs(user_id);
CREATE INDEX idx_wizard_runs_wizard ON wizard_runs(wizard_id);
CREATE INDEX idx_wizard_runs_status ON wizard_runs(status);
CREATE INDEX idx_wizard_runs_stored ON wizard_runs(is_stored);
CREATE INDEX idx_wizard_runs_completed ON wizard_runs(completed_at DESC);

-- Sharing
CREATE INDEX idx_run_shares_with ON wizard_run_shares(shared_with);
CREATE INDEX idx_run_shares_by ON wizard_run_shares(shared_by);

Complete API Specification
typescript// ============================================
// WIZARD TEMPLATES API
// ============================================
GET    /api/v1/wizard-templates
GET    /api/v1/wizard-templates/:id
POST   /api/v1/wizard-templates
PUT    /api/v1/wizard-templates/:id
DELETE /api/v1/wizard-templates/:id
POST   /api/v1/wizard-templates/:id/clone
GET    /api/v1/wizard-templates/categories
POST   /api/v1/wizard-templates/:id/rate
GET    /api/v1/wizard-templates/:id/ratings
POST   /api/v1/wizard-templates/:id/use

// ============================================
// WIZARD BUILDER API (Existing - No Changes)
// ============================================
POST   /api/v1/wizards/
GET    /api/v1/wizards/
GET    /api/v1/wizards/:id
PUT    /api/v1/wizards/:id
DELETE /api/v1/wizards/:id
GET    /api/v1/wizards/categories

// ============================================
// RUN WIZARD API
// ============================================
POST   /api/v1/wizard-runs/start
GET    /api/v1/wizard-runs/:id
PUT    /api/v1/wizard-runs/:id/step
POST   /api/v1/wizard-runs/:id/response
POST   /api/v1/wizard-runs/:id/complete
POST   /api/v1/wizard-runs/:id/store
DELETE /api/v1/wizard-runs/:id
GET    /api/v1/wizard-runs/my-runs
GET    /api/v1/wizard-runs/stored
GET    /api/v1/wizard-runs/in-progress

// ============================================
// STORE WIZARD API
// ============================================
GET    /api/v1/stored-runs
GET    /api/v1/stored-runs/:id
DELETE /api/v1/stored-runs/:id
PUT    /api/v1/stored-runs/:id/notes
GET    /api/v1/stored-runs/:id/export
POST   /api/v1/stored-runs/:id/share
GET    /api/v1/stored-runs/shared-with-me
DELETE /api/v1/stored-runs/shares/:shareId
POST   /api/v1/stored-runs/compare
GET    /api/v1/stored-runs/comparisons

// ============================================
// PLAY WIZARD API
// ============================================
GET    /api/v1/play-wizard/:runId
GET    /api/v1/play-wizard/:runId/step/:stepNum
GET    /api/v1/play-wizard/:runId/files/:fileId
GET    /api/v1/play-wizard/:runId/export/pdf
GET    /api/v1/play-wizard/:runId/export/json

Frontend Routes
typescript// App Routes
const routes = [
  // ============================================
  // PUBLIC ROUTES
  // ============================================
  {
    path: '/templates',
    component: WizardTemplateGallery,
    title: 'Wizard Templates'
  },
  {
    path: '/templates/:id',
    component: WizardTemplatePreview,
    title: 'Template Preview'
  },
  
  // ============================================
  // ADMIN ROUTES (Existing)
  // ============================================
  {
    path: '/admin/wizard-builder',
    component: WizardBuilderPage, // Existing component
    title: 'Wizard Builder',
    requiresAuth: true,
    requiresRole: ['admin', 'super_admin']
  },
  
  // ============================================
  // USER ROUTES (New)
  // ============================================
  {
    path: '/run/:wizardId',
    component: RunWizardPage,
    title: 'Run Wizard',
    requiresAuth: false // Based on wizard.require_login
  },
  {
    path: '/my-runs',
    component: StoreWizardPage,
    title: 'My Stored Runs',
    requiresAuth: true
  },
  {
    path: '/play/:runId',
    component: PlayWizardPage,
    title: 'Play Wizard Run',
    requiresAuth: true
  },
  {
    path: '/shared-runs',
    component: SharedRunsPage,
    title: 'Runs Shared With Me',
    requiresAuth: true
  }
];

Implementation Priority & Timeline
Phase 1: Foundation (Week 1-2)

✅ Wizard Builder (Already Implemented)
Create database schema for Templates, Runs, Stores
Set up API endpoints for all components
Implement authentication and authorization

Phase 2: Template System (Week 3-4)

Build Wizard Template Gallery UI
Implement template CRUD operations
Create system templates (5-10 examples)
Integrate template cloning with Wizard Builder
Add rating and review system

Phase 3: Run Wizard (Week 5-6)

Build Run Wizard execution interface
Implement step navigation and validation
Add auto-save functionality
Create completion dialog with store option
File upload handling

Phase 4: Store Wizard (Week 7-8)

Build Store Wizard repository UI
Implement search, filter, and sort
Add export functionality (PDF, JSON, CSV)
Implement sharing system
Add comparison feature

Phase 5: Play Wizard (Week 9-10)

Build Play Wizard playback interface
Implement auto-play logic
Create read-only response renderers
Add PDF export and print functionality
Video recording (if time permits)

Phase 6: Polish & Testing (Week 11-12)

End-to-end testing of complete workflow
Performance optimization
UI/UX refinements
Documentation and training materials
Bug fixes and edge case handling


Key Technical Decisions
State Management

React Query for server state
Context API for global app state
Local component state with useState for UI interactions

Styling

Material-UI (MUI) v5 for consistent design
Responsive design for mobile/tablet/desktop
Dark mode support (optional)

File Storage

AWS S3 or Azure Blob Storage for uploaded files
Database stores only file metadata and paths
Pre-signed URLs for secure file access

Performance

Lazy loading for large wizard lists
Pagination for stored runs
Virtual scrolling for long option lists
Debounced search/filter operations

Security

JWT-based authentication
Role-based access control (RBAC)
Input sanitization (XSS prevention)
CSRF protection
SQL injection prevention via parameterized queries


Success Metrics
User Engagement:

Number of wizards created from templates
Average completion rate for wizard runs
Number of stored runs per user
Play wizard usage statistics

System Performance:

Average wizard load time < 2 seconds
Run execution completion rate > 85%
API response time < 500ms
Zero data loss incidents

User Satisfaction:

User feedback ratings > 4.5/5
Feature adoption rate > 70%
Support ticket reduction by 30%


Conclusion
This comprehensive specification provides a complete, scalable wizard lifecycle system that:

Leverages existing Wizard Builder (1,103 lines, fully functional)
Adds Template System for quick wizard creation
Implements Run Wizard for user-facing execution
Provides Store Wizard for managing saved runs
Includes Play Wizard for interactive playback

The system is designed with best practices in database architecture, API design, and frontend development, ensuring maintainability, scalability, and excellent user experience.