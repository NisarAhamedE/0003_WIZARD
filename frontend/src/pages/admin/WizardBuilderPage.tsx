import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  DragIndicator as DragIcon,
  Edit as EditIcon,
  AddCircle as CreateIcon,
} from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { wizardService } from '../../services/wizard.service';
import OptionDependencyManager from '../../components/OptionDependencyManager';
import { DependencyType } from '../../types';

interface OptionData {
  id?: string;
  label: string;
  value: string;
  description?: string;
  is_default: boolean;
  dependencies?: Array<{
    depends_on_option_id: string;
    dependency_type: DependencyType;
  }>;
}

interface OptionSetData {
  name: string;
  description?: string;
  selection_type: string;
  is_required: boolean;
  min_selections: number;
  max_selections?: number;
  placeholder?: string;
  help_text?: string;
  options: OptionData[];
}

interface StepData {
  name: string;
  description?: string;
  help_text?: string;
  step_order: number;
  is_required: boolean;
  is_skippable: boolean;
  option_sets: OptionSetData[];
}

interface WizardData {
  name: string;
  description?: string;
  category_id?: string;
  icon?: string;
  is_published: boolean;
  allow_templates: boolean;
  require_login: boolean;
  auto_save: boolean;
  estimated_time?: number;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  tags: string[];
  steps: StepData[];
}

const WizardBuilderPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [editingWizardId, setEditingWizardId] = useState<string | null>(null);
  const [showWizardList, setShowWizardList] = useState(true);
  const [wizard, setWizard] = useState<WizardData>({
    name: '',
    description: '',
    is_published: false,
    allow_templates: true,
    require_login: true,
    auto_save: true,
    difficulty_level: 'easy',
    tags: [],
    steps: [],
  });

  const [tagInput, setTagInput] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => wizardService.getCategories(),
  });

  const { data: wizardsList } = useQuery({
    queryKey: ['wizards-list'],
    queryFn: () => wizardService.getWizards({ published_only: false }),
  });

  const createWizardMutation = useMutation({
    mutationFn: (data: WizardData) => wizardService.createWizard(data),
    onSuccess: async (createdWizard) => {
      // Sync dependencies after creation
      try {
        await syncDependencies(createdWizard.id);
        setSnackbar({ open: true, message: 'Wizard created successfully!', severity: 'success' });
      } catch (error) {
        setSnackbar({ open: true, message: 'Wizard created but failed to sync dependencies', severity: 'warning' });
      }
      queryClient.invalidateQueries({ queryKey: ['wizards-list'] });
      resetForm();
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.detail || 'Failed to create wizard', severity: 'error' });
    },
  });

  const updateWizardMutation = useMutation({
    mutationFn: (data: { id: string; wizard: Partial<WizardData> }) => wizardService.updateWizard(data.id, data.wizard as any),
    onSuccess: async (_, variables) => {
      // Sync dependencies after update
      try {
        await syncDependencies(variables.id);
        setSnackbar({ open: true, message: 'Wizard updated successfully!', severity: 'success' });
      } catch (error) {
        setSnackbar({ open: true, message: 'Wizard updated but failed to sync dependencies', severity: 'warning' });
      }
      queryClient.invalidateQueries({ queryKey: ['wizards-list'] });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.detail || 'Failed to update wizard', severity: 'error' });
    },
  });

  const resetForm = () => {
    setWizard({
      name: '',
      description: '',
      is_published: false,
      allow_templates: true,
      require_login: true,
      auto_save: true,
      difficulty_level: 'easy',
      tags: [],
      steps: [],
    });
    setEditingWizardId(null);
    setShowWizardList(true);
  };

  const loadWizardForEditing = async (wizardId: string) => {
    try {
      const wizardData = await wizardService.getWizard(wizardId);
      // Transform the data to match our form structure
      const formData: WizardData = {
        name: wizardData.name,
        description: wizardData.description || '',
        category_id: wizardData.category?.id,
        icon: wizardData.icon,
        is_published: wizardData.is_published,
        allow_templates: wizardData.allow_templates,
        require_login: wizardData.require_login,
        auto_save: wizardData.auto_save,
        estimated_time: wizardData.estimated_time,
        difficulty_level: wizardData.difficulty_level as 'easy' | 'medium' | 'hard' | undefined,
        tags: wizardData.tags || [],
        steps: wizardData.steps.map((step: any) => ({
          name: step.name,
          description: step.description || '',
          help_text: step.help_text || '',
          step_order: step.step_order,
          is_required: step.is_required,
          is_skippable: step.is_skippable || false,
          option_sets: step.option_sets.map((os: any) => ({
            name: os.name,
            description: os.description || '',
            selection_type: os.selection_type,
            is_required: os.is_required,
            min_selections: os.min_selections || 0,
            max_selections: os.max_selections,
            placeholder: os.placeholder || '',
            help_text: os.help_text || '',
            options: os.options.map((opt: any) => ({
              id: opt.id,
              label: opt.label,
              value: opt.value,
              description: opt.description || '',
              is_default: opt.is_default || false,
              dependencies: opt.dependencies?.map((dep: any) => ({
                depends_on_option_id: dep.depends_on_option_id,
                dependency_type: dep.dependency_type,
              })) || [],
            })),
          })),
        })),
      };
      setWizard(formData);
      setEditingWizardId(wizardId);
      setShowWizardList(false);
    } catch (error: any) {
      setSnackbar({ open: true, message: 'Failed to load wizard', severity: 'error' });
    }
  };

  const handleCreateNew = () => {
    resetForm();
    setShowWizardList(false);
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !wizard.tags.includes(tagInput.trim())) {
      setWizard({ ...wizard, tags: [...wizard.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setWizard({ ...wizard, tags: wizard.tags.filter((t) => t !== tag) });
  };

  const handleAddStep = () => {
    const newStep: StepData = {
      name: `Step ${wizard.steps.length + 1}`,
      description: '',
      step_order: wizard.steps.length + 1,
      is_required: true,
      is_skippable: false,
      option_sets: [],
    };
    setWizard({ ...wizard, steps: [...wizard.steps, newStep] });
  };

  const handleRemoveStep = (index: number) => {
    const newSteps = wizard.steps.filter((_, i) => i !== index).map((step, i) => ({
      ...step,
      step_order: i + 1,
    }));
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleStepChange = (index: number, field: keyof StepData, value: any) => {
    const newSteps = [...wizard.steps];
    newSteps[index] = { ...newSteps[index], [field]: value };
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleAddOptionSet = (stepIndex: number) => {
    const newOptionSet: OptionSetData = {
      name: 'New Option Set',
      selection_type: 'single_select',
      is_required: true,
      min_selections: 0,
      options: [],
    };
    const newSteps = [...wizard.steps];
    newSteps[stepIndex].option_sets.push(newOptionSet);
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleRemoveOptionSet = (stepIndex: number, optionSetIndex: number) => {
    const newSteps = [...wizard.steps];
    newSteps[stepIndex].option_sets = newSteps[stepIndex].option_sets.filter((_, i) => i !== optionSetIndex);
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleOptionSetChange = (stepIndex: number, optionSetIndex: number, field: keyof OptionSetData, value: any) => {
    const newSteps = [...wizard.steps];
    newSteps[stepIndex].option_sets[optionSetIndex] = {
      ...newSteps[stepIndex].option_sets[optionSetIndex],
      [field]: value,
    };
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleAddOption = (stepIndex: number, optionSetIndex: number) => {
    const newOption: OptionData = {
      label: 'New Option',
      value: `option_${Date.now()}`,
      is_default: false,
      dependencies: [],
    };
    const newSteps = [...wizard.steps];
    newSteps[stepIndex].option_sets[optionSetIndex].options.push(newOption);
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleRemoveOption = (stepIndex: number, optionSetIndex: number, optionIndex: number) => {
    const newSteps = [...wizard.steps];
    newSteps[stepIndex].option_sets[optionSetIndex].options = newSteps[stepIndex].option_sets[optionSetIndex].options.filter(
      (_, i) => i !== optionIndex
    );
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleOptionChange = (
    stepIndex: number,
    optionSetIndex: number,
    optionIndex: number,
    field: keyof OptionData,
    value: any
  ) => {
    const newSteps = [...wizard.steps];
    newSteps[stepIndex].option_sets[optionSetIndex].options[optionIndex] = {
      ...newSteps[stepIndex].option_sets[optionSetIndex].options[optionIndex],
      [field]: value,
    };
    setWizard({ ...wizard, steps: newSteps });
  };

  const handleDependencyChange = (
    stepIndex: number,
    optionSetIndex: number,
    optionIndex: number,
    dependencies: Array<{
      depends_on_option_id: string;
      dependency_type: DependencyType;
    }>
  ) => {
    handleOptionChange(stepIndex, optionSetIndex, optionIndex, 'dependencies', dependencies);
  };

  // Get all available options for dependency selection
  const getAllAvailableOptions = (currentStepIndex: number, currentOptionSetIndex: number) => {
    const availableOptions: Array<{
      id: string;
      label: string;
      value: string;
      stepName: string;
      optionSetName: string;
    }> = [];

    wizard.steps.forEach((step, stepIdx) => {
      step.option_sets.forEach((optionSet, osIdx) => {
        // Only include options from previous steps or earlier option sets in current step
        if (
          stepIdx < currentStepIndex ||
          (stepIdx === currentStepIndex && osIdx < currentOptionSetIndex)
        ) {
          optionSet.options.forEach((option) => {
            if (option.id) {
              availableOptions.push({
                id: option.id,
                label: option.label,
                value: option.value,
                stepName: step.name,
                optionSetName: optionSet.name,
              });
            }
          });
        }
      });
    });

    return availableOptions;
  };

  // Sync dependencies after wizard is saved
  const syncDependencies = async (wizardId: string) => {
    try {
      // Reload the wizard to get the latest option IDs
      const savedWizard = await wizardService.getWizard(wizardId);

      // Build a map of option value -> option ID from saved wizard
      const optionIdMap = new Map<string, string>();
      savedWizard.steps.forEach(step => {
        step.option_sets.forEach(optionSet => {
          optionSet.options.forEach(option => {
            optionIdMap.set(option.value, option.id);
          });
        });
      });

      // Build a map of option value -> existing dependencies from saved wizard
      const existingDepsMap = new Map<string, any[]>();
      savedWizard.steps.forEach(step => {
        step.option_sets.forEach(optionSet => {
          optionSet.options.forEach(option => {
            existingDepsMap.set(option.value, option.dependencies || []);
          });
        });
      });

      // Process dependencies from local state
      for (const step of wizard.steps) {
        for (const optionSet of step.option_sets) {
          for (const option of optionSet.options) {
            const optionId = optionIdMap.get(option.value);
            if (!optionId) continue; // Skip if option not found

            const localDeps = option.dependencies || [];
            const existingDeps = existingDepsMap.get(option.value) || [];

            // Find dependencies to add
            for (const localDep of localDeps) {
              const exists = existingDeps.some(
                ed => ed.depends_on_option_id === localDep.depends_on_option_id &&
                      ed.dependency_type === localDep.dependency_type
              );

              if (!exists) {
                // Add new dependency
                try {
                  await wizardService.createOptionDependency(optionId, {
                    depends_on_option_id: localDep.depends_on_option_id,
                    dependency_type: localDep.dependency_type
                  });
                } catch (error) {
                  console.error('Failed to create dependency:', error);
                }
              }
            }

            // Find dependencies to remove
            for (const existingDep of existingDeps) {
              const stillExists = localDeps.some(
                ld => ld.depends_on_option_id === existingDep.depends_on_option_id &&
                      ld.dependency_type === existingDep.dependency_type
              );

              if (!stillExists && existingDep.id) {
                // Remove dependency
                try {
                  await wizardService.deleteOptionDependency(existingDep.id);
                } catch (error) {
                  console.error('Failed to delete dependency:', error);
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to sync dependencies:', error);
      throw error;
    }
  };

  const handleSave = () => {
    if (!wizard.name.trim()) {
      setSnackbar({ open: true, message: 'Please enter a wizard name', severity: 'error' });
      return;
    }
    if (wizard.steps.length === 0) {
      setSnackbar({ open: true, message: 'Please add at least one step', severity: 'error' });
      return;
    }
    if (editingWizardId) {
      // Update existing wizard
      updateWizardMutation.mutate({ id: editingWizardId, wizard });
    } else {
      // Create new wizard
      createWizardMutation.mutate(wizard);
    }
  };

  return (
    <Box>
      {showWizardList ? (
        // Wizard List View
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Wizard Builder</Typography>
            <Button variant="contained" startIcon={<CreateIcon />} onClick={handleCreateNew}>
              Create New Wizard
            </Button>
          </Box>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Existing Wizards
              </Typography>
              {wizardsList && wizardsList.length > 0 ? (
                <Grid container spacing={2}>
                  {wizardsList.map((w: any) => (
                    <Grid item xs={12} sm={6} md={4} key={w.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" noWrap>
                            {w.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {w.description?.substring(0, 100) || 'No description'}
                            {w.description?.length > 100 ? '...' : ''}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                            <Chip
                              size="small"
                              label={w.is_published ? 'Published' : 'Draft'}
                              color={w.is_published ? 'success' : 'default'}
                            />
                            <Chip size="small" label={w.difficulty_level || 'easy'} />
                          </Box>
                          <Button
                            variant="outlined"
                            startIcon={<EditIcon />}
                            fullWidth
                            onClick={() => loadWizardForEditing(w.id)}
                          >
                            Edit Wizard
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography color="text.secondary">No wizards found. Create your first wizard!</Typography>
              )}
            </CardContent>
          </Card>
        </Box>
      ) : (
        // Wizard Builder Form
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button variant="outlined" onClick={resetForm}>
                Back to List
              </Button>
              <Typography variant="h4">
                {editingWizardId ? 'Edit Wizard' : 'Create New Wizard'}
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={createWizardMutation.isPending || updateWizardMutation.isPending}
            >
              {createWizardMutation.isPending || updateWizardMutation.isPending
                ? 'Saving...'
                : editingWizardId
                  ? 'Update Wizard'
                  : 'Save Wizard'}
            </Button>
          </Box>

          <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Wizard Name"
                    value={wizard.name}
                    onChange={(e) => setWizard({ ...wizard, name: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Description"
                    value={wizard.description}
                    onChange={(e) => setWizard({ ...wizard, description: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={wizard.category_id || ''}
                      label="Category"
                      onChange={(e) => setWizard({ ...wizard, category_id: e.target.value })}
                    >
                      <MenuItem value="">None</MenuItem>
                      {categories?.map((cat: any) => (
                        <MenuItem key={cat.id} value={cat.id}>
                          {cat.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Difficulty Level</InputLabel>
                    <Select
                      value={wizard.difficulty_level || ''}
                      label="Difficulty Level"
                      onChange={(e) => setWizard({ ...wizard, difficulty_level: e.target.value as 'easy' | 'medium' | 'hard' })}
                    >
                      <MenuItem value="easy">Easy</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="hard">Hard</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Estimated Time (minutes)"
                    value={wizard.estimated_time || ''}
                    onChange={(e) => setWizard({ ...wizard, estimated_time: parseInt(e.target.value) || undefined })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Icon"
                    value={wizard.icon || ''}
                    onChange={(e) => setWizard({ ...wizard, icon: e.target.value })}
                    placeholder="e.g., feedback, settings, person"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <TextField
                      label="Add Tag"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                      size="small"
                    />
                    <Button onClick={handleAddTag} variant="outlined" size="small">
                      Add
                    </Button>
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                    {wizard.tags.map((tag) => (
                      <Chip key={tag} label={tag} onDelete={() => handleRemoveTag(tag)} size="small" />
                    ))}
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Settings */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Settings
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={wizard.is_published}
                    onChange={(e) => setWizard({ ...wizard, is_published: e.target.checked })}
                  />
                }
                label="Published"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={wizard.require_login}
                    onChange={(e) => setWizard({ ...wizard, require_login: e.target.checked })}
                  />
                }
                label="Require Login"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={wizard.allow_templates}
                    onChange={(e) => setWizard({ ...wizard, allow_templates: e.target.checked })}
                  />
                }
                label="Allow Templates"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={wizard.auto_save}
                    onChange={(e) => setWizard({ ...wizard, auto_save: e.target.checked })}
                  />
                }
                label="Auto Save"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Steps */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Steps ({wizard.steps.length})</Typography>
                <Button startIcon={<AddIcon />} onClick={handleAddStep} variant="outlined">
                  Add Step
                </Button>
              </Box>

              {wizard.steps.length === 0 ? (
                <Alert severity="info">No steps added yet. Click "Add Step" to create your first step.</Alert>
              ) : (
                wizard.steps.map((step, stepIndex) => (
                  <Accordion key={stepIndex} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                        <DragIcon color="action" />
                        <Typography sx={{ flexGrow: 1 }}>
                          Step {step.step_order}: {step.name}
                        </Typography>
                        <Chip
                          size="small"
                          label={`${step.option_sets.length} option sets`}
                          color="primary"
                          variant="outlined"
                        />
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRemoveStep(stepIndex);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Step Name"
                            value={step.name}
                            onChange={(e) => handleStepChange(stepIndex, 'name', e.target.value)}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Box>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={step.is_required}
                                  onChange={(e) => handleStepChange(stepIndex, 'is_required', e.target.checked)}
                                />
                              }
                              label="Required"
                            />
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={step.is_skippable}
                                  onChange={(e) => handleStepChange(stepIndex, 'is_skippable', e.target.checked)}
                                />
                              }
                              label="Skippable"
                            />
                          </Box>
                        </Grid>
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            multiline
                            rows={2}
                            label="Description"
                            value={step.description || ''}
                            onChange={(e) => handleStepChange(stepIndex, 'description', e.target.value)}
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="Help Text"
                            value={step.help_text || ''}
                            onChange={(e) => handleStepChange(stepIndex, 'help_text', e.target.value)}
                          />
                        </Grid>

                        <Grid item xs={12}>
                          <Divider sx={{ my: 2 }} />
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Typography variant="subtitle1">Option Sets</Typography>
                            <Button size="small" startIcon={<AddIcon />} onClick={() => handleAddOptionSet(stepIndex)}>
                              Add Option Set
                            </Button>
                          </Box>

                          {step.option_sets.map((optionSet, osIndex) => (
                            <Card key={osIndex} variant="outlined" sx={{ mb: 2, p: 2 }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Typography variant="subtitle2">Option Set {osIndex + 1}</Typography>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleRemoveOptionSet(stepIndex, osIndex)}
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Box>
                              <Grid container spacing={2}>
                                <Grid item xs={12} sm={6}>
                                  <TextField
                                    fullWidth
                                    size="small"
                                    label="Name"
                                    value={optionSet.name}
                                    onChange={(e) => handleOptionSetChange(stepIndex, osIndex, 'name', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                  <FormControl fullWidth size="small">
                                    <InputLabel>Selection Type</InputLabel>
                                    <Select
                                      value={optionSet.selection_type}
                                      label="Selection Type"
                                      onChange={(e) =>
                                        handleOptionSetChange(stepIndex, osIndex, 'selection_type', e.target.value)
                                      }
                                    >
                                      <MenuItem value="single_select">Single Select</MenuItem>
                                      <MenuItem value="multiple_select">Multiple Select</MenuItem>
                                      <MenuItem value="text_input">Text Input</MenuItem>
                                      <MenuItem value="number_input">Number Input</MenuItem>
                                      <MenuItem value="date_input">Date Input</MenuItem>
                                      <MenuItem value="time_input">Time Input</MenuItem>
                                      <MenuItem value="datetime_input">DateTime Input</MenuItem>
                                      <MenuItem value="rating">Rating</MenuItem>
                                      <MenuItem value="slider">Slider</MenuItem>
                                      <MenuItem value="color_picker">Color Picker</MenuItem>
                                      <MenuItem value="file_upload">File Upload</MenuItem>
                                      <MenuItem value="rich_text">Rich Text</MenuItem>
                                    </Select>
                                  </FormControl>
                                </Grid>
                                <Grid item xs={12}>
                                  <TextField
                                    fullWidth
                                    size="small"
                                    label="Description"
                                    value={optionSet.description || ''}
                                    onChange={(e) =>
                                      handleOptionSetChange(stepIndex, osIndex, 'description', e.target.value)
                                    }
                                  />
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                  <TextField
                                    fullWidth
                                    size="small"
                                    label="Placeholder"
                                    value={optionSet.placeholder || ''}
                                    onChange={(e) =>
                                      handleOptionSetChange(stepIndex, osIndex, 'placeholder', e.target.value)
                                    }
                                  />
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                  <FormControlLabel
                                    control={
                                      <Switch
                                        checked={optionSet.is_required}
                                        onChange={(e) =>
                                          handleOptionSetChange(stepIndex, osIndex, 'is_required', e.target.checked)
                                        }
                                      />
                                    }
                                    label="Required"
                                  />
                                </Grid>

                                {/* Options for select types */}
                                {(optionSet.selection_type === 'single_select' ||
                                  optionSet.selection_type === 'multiple_select') && (
                                  <Grid item xs={12}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                      <Typography variant="body2">Options</Typography>
                                      <Button
                                        size="small"
                                        onClick={() => handleAddOption(stepIndex, osIndex)}
                                        startIcon={<AddIcon />}
                                      >
                                        Add Option
                                      </Button>
                                    </Box>
                                    {optionSet.options.map((option, optIndex) => (
                                      <Accordion key={optIndex} sx={{ mb: 1 }}>
                                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                                            <Typography sx={{ flexGrow: 1 }}>
                                              Option {optIndex + 1}: {option.label || 'Untitled'}
                                            </Typography>
                                            {option.dependencies && option.dependencies.length > 0 && (
                                              <Chip
                                                size="small"
                                                label={`${option.dependencies.length} ${option.dependencies.length === 1 ? 'dependency' : 'dependencies'}`}
                                                color="primary"
                                                variant="outlined"
                                              />
                                            )}
                                            <IconButton
                                              size="small"
                                              color="error"
                                              onClick={(e) => {
                                                e.stopPropagation();
                                                handleRemoveOption(stepIndex, osIndex, optIndex);
                                              }}
                                            >
                                              <DeleteIcon fontSize="small" />
                                            </IconButton>
                                          </Box>
                                        </AccordionSummary>
                                        <AccordionDetails>
                                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                            <Box sx={{ display: 'flex', gap: 1 }}>
                                              <TextField
                                                size="small"
                                                label="Label"
                                                value={option.label}
                                                onChange={(e) =>
                                                  handleOptionChange(stepIndex, osIndex, optIndex, 'label', e.target.value)
                                                }
                                                sx={{ flexGrow: 1 }}
                                              />
                                              <TextField
                                                size="small"
                                                label="Value"
                                                value={option.value}
                                                onChange={(e) =>
                                                  handleOptionChange(stepIndex, osIndex, optIndex, 'value', e.target.value)
                                                }
                                                sx={{ flexGrow: 1 }}
                                              />
                                            </Box>
                                            <TextField
                                              size="small"
                                              label="Description (optional)"
                                              value={option.description || ''}
                                              onChange={(e) =>
                                                handleOptionChange(stepIndex, osIndex, optIndex, 'description', e.target.value)
                                              }
                                              fullWidth
                                              multiline
                                              rows={2}
                                            />
                                            <FormControlLabel
                                              control={
                                                <Switch
                                                  checked={option.is_default}
                                                  onChange={(e) =>
                                                    handleOptionChange(stepIndex, osIndex, optIndex, 'is_default', e.target.checked)
                                                  }
                                                />
                                              }
                                              label="Default Selection"
                                            />
                                            <Divider />
                                            <OptionDependencyManager
                                              currentOptionId={option.id}
                                              dependencies={option.dependencies || []}
                                              availableOptions={getAllAvailableOptions(stepIndex, osIndex)}
                                              onChange={(deps) => handleDependencyChange(stepIndex, osIndex, optIndex, deps)}
                                            />
                                          </Box>
                                        </AccordionDetails>
                                      </Accordion>
                                    ))}
                                  </Grid>
                                )}
                              </Grid>
                            </Card>
                          ))}
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
        </Box>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default WizardBuilderPage;
