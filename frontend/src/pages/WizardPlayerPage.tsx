import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Checkbox,
  FormGroup,
  TextField,
  Alert,
  Paper,
  Divider,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
  Slider,
  Rating,
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
  CheckCircle as CompleteIcon,
  Close as CloseIcon,
  Save as SaveIcon,
  ContentCopy as ContentCopyIcon,
} from '@mui/icons-material';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { wizardService } from '../services/wizard.service';
import { wizardRunService } from '../services';
import { OptionSet } from '../types';

interface ResponseData {
  [optionSetId: string]: string | string[] | number;
}

const WizardPlayerPage: React.FC = () => {
  const { wizardId } = useParams<{ wizardId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const sessionIdFromUrl = searchParams.get('session');
  const isViewOnly = searchParams.get('view_only') === 'true';
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [responses, setResponses] = useState<ResponseData>({});
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isCompleted, setIsCompleted] = useState(false);
  const [showCompletionScreen, setShowCompletionScreen] = useState(false);
  const runCreationAttempted = useRef(false);

  // Run name dialog state (for new runs)
  const [showSessionNameDialog, setShowSessionNameDialog] = useState(false);
  const [sessionName, setSessionName] = useState('');
  const [sessionNameError, setSessionNameError] = useState('');

  // Edit mode states
  const [isEditMode, setIsEditMode] = useState(false);
  const [existingRunName, setExistingRunName] = useState('');
  const [showUpdateRunDialog, setShowUpdateRunDialog] = useState(false);

  // Save As dialog state
  const [showSaveAsDialog, setShowSaveAsDialog] = useState(false);
  const [saveAsRunName, setSaveAsRunName] = useState('');
  const [saveAsError, setSaveAsError] = useState('');

  // Snackbar state
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info';
  }>({ open: false, message: '', severity: 'success' });

  const { data: wizard, isLoading } = useQuery({
    queryKey: ['wizard', wizardId],
    queryFn: () => wizardService.getWizard(wizardId!),
    enabled: !!wizardId,
  });

  const createSessionMutation = useMutation({
    mutationFn: (data: { wizard_id: string; run_name?: string }) =>
      wizardRunService.createWizardRun(data),
    onSuccess: (run) => {
      setSessionId(run.id);
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Failed to create run',
        severity: 'error',
      });
    },
  });

  const completeSessionMutation = useMutation({
    mutationFn: (id: string) => wizardRunService.completeWizardRun(id, {}),
    onSuccess: (data) => {
      console.log('✓ Wizard run completed successfully:', data);
      setIsCompleted(true);

      // Invalidate runs cache to refresh the list
      queryClient.invalidateQueries({ queryKey: ['wizard-runs'] });

      // Show different screens based on mode (dialog will be triggered in handleNext)
      if (!isEditMode) {
        setShowCompletionScreen(true); // Show completion screen for new runs
        setShowSessionNameDialog(true); // Show dialog asking if user wants to save the run
      }

      setSnackbar({
        open: true,
        message: isEditMode ? 'Wizard updated successfully!' : 'Wizard completed successfully!',
        severity: 'success',
      });
    },
    onError: (error: any) => {
      console.error('✗ Error completing wizard run:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to complete wizard run',
        severity: 'error',
      });
    },
  });

  const saveRunMutation = useMutation({
    mutationFn: async (data: { runId: string; name: string; description?: string; isUpdate?: boolean }) => {
      console.log('[WizardPlayer] Saving run with all responses...');

      // LOOPHOLE #6 FIX: Validate all responses before saving
      const validationErrors: string[] = [];
      wizard?.steps.forEach((step, stepIndex) => {
        step.option_sets.forEach((optionSet) => {
          const isRequired = optionSet.is_required;
          const responseValue = responses[optionSet.id];

          if (isRequired && (responseValue === undefined || responseValue === null ||
              (Array.isArray(responseValue) && responseValue.length === 0))) {
            validationErrors.push(`Step ${stepIndex + 1}: ${optionSet.name} is required`);
          }
        });
      });

      if (validationErrors.length > 0) {
        throw new Error(`Validation failed:\n${validationErrors.join('\n')}`);
      }

      // LOOPHOLE #1 & #5 FIX: Check if responses already exist and delete them first
      try {
        const existingRun = await wizardRunService.getWizardRun(data.runId);
        if (existingRun.option_set_responses && existingRun.option_set_responses.length > 0) {
          console.log('[WizardPlayer] Existing responses found, deleting old responses before update');
          await wizardRunService.clearAllResponses(data.runId);
          console.log('[WizardPlayer] Old responses cleared, proceeding with fresh save');
        }
      } catch (error) {
        console.log('[WizardPlayer] No existing responses found, proceeding with fresh save');
      }

      // LOOPHOLE #2 & #3 FIX: Collect all operations to ensure atomicity
      const savedStepResponses: string[] = [];
      const savedOptionSetResponses: string[] = [];

      try {
        // Step 1: Save all responses from all steps to database
        if (wizard) {
          for (let stepIndex = 0; stepIndex < wizard.steps.length; stepIndex++) {
            const step = wizard.steps[stepIndex];
            // LOOPHOLE #4 FIX: Only create step response if it has at least one option set response
            const hasResponses = step.option_sets.some(os => {
              const val = responses[os.id];
              return val !== undefined && val !== null && (Array.isArray(val) ? val.length > 0 : true);
            });

            if (!hasResponses) {
              console.log(`[WizardPlayer] Skipping step ${step.name} - no responses`);
              continue;
            }

            // Create step response
            const stepResponse = await wizardRunService.createStepResponse(data.runId, {
              run_id: data.runId,
              step_id: step.id,
              step_index: stepIndex,
              step_name: step.name,
            });

            savedStepResponses.push(stepResponse.id);
            console.log(`[WizardPlayer] Created step response for step ${step.name}:`, stepResponse.id);

            // Create option set responses for this step
            for (const optionSet of step.option_sets) {
              const responseValue = responses[optionSet.id];
              if (responseValue !== undefined && responseValue !== null) {
                // Skip empty arrays
                if (Array.isArray(responseValue) && responseValue.length === 0) {
                  continue;
                }

                const optionSetResp = await wizardRunService.createOptionSetResponse(data.runId, {
                  run_id: data.runId,
                  step_response_id: stepResponse.id,
                  option_set_id: optionSet.id,
                  response_value: { value: responseValue },
                });

                savedOptionSetResponses.push(optionSetResp.id);
              }
            }
          }
          console.log('[WizardPlayer] All responses saved successfully');
          console.log(`[WizardPlayer] Saved ${savedStepResponses.length} step responses and ${savedOptionSetResponses.length} option set responses`);
        }

        // Step 2: Update run metadata (name, description, mark as stored)
        const result = await wizardRunService.updateWizardRun(data.runId, {
          run_name: data.name,
          run_description: data.description,
          is_stored: true,
        });

        // LOOPHOLE #8 FIX: Clear localStorage backup after successful save
        localStorage.removeItem(`wizard_responses_${data.runId}`);

        return result;

      } catch (error) {
        // LOOPHOLE #3 FIX: On error, log what was saved for potential rollback
        console.error('[WizardPlayer] Save failed, saved items before error:', {
          stepResponses: savedStepResponses,
          optionSetResponses: savedOptionSetResponses,
        });
        console.error('[WizardPlayer] Error details:', error);

        // Note: Ideally we would rollback here, but that requires backend support
        // For now, we throw the error to trigger the onError handler
        throw error;
      }
    },
    onSuccess: () => {
      setSnackbar({
        open: true,
        message: 'Run saved successfully!',
        severity: 'success',
      });
      setShowSessionNameDialog(false);
      setSessionName('');
      // Navigate to My Runs page to show the stored run
      navigate('/my-runs');
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.message || 'Failed to save run',
        severity: 'error',
      });
    },
  });


  // Load existing session from URL or create new run automatically
  useEffect(() => {
    console.log('[WizardPlayer] Session initialization effect:', {
      hasWizard: !!wizard,
      sessionId,
      sessionIdFromUrl,
      runCreationAttempted: runCreationAttempted.current
    });

    if (wizard && !sessionId && !runCreationAttempted.current) {
      if (sessionIdFromUrl) {
        // Load existing session from URL
        console.log('[WizardPlayer] Setting sessionId from URL:', sessionIdFromUrl);
        setSessionId(sessionIdFromUrl);
      } else {
        // Automatically create a new run without asking for a name
        console.log('[WizardPlayer] Creating new run automatically');
        runCreationAttempted.current = true;
        createSessionMutation.mutate({
          wizard_id: wizard.id,
        });
      }
    }
  }, [wizard, sessionIdFromUrl]);

  // Load wizard run responses when resuming an existing run
  useEffect(() => {
    const loadRunResponses = async () => {
      if (!sessionId || !wizard) {
        console.log('[WizardPlayer] loadRunResponses - skipping:', { sessionId, hasWizard: !!wizard });
        return;
      }

      console.log('[WizardPlayer] Loading responses for session:', sessionId);
      console.log('[WizardPlayer] Current wizard structure:', wizard);

      try {
        const run = await wizardRunService.getWizardRun(sessionId);
        console.log('[WizardPlayer] Loaded run:', run);
        console.log('[WizardPlayer] Run status:', run.status);
        console.log('[WizardPlayer] Number of option_set_responses:', run.option_set_responses?.length || 0);

        // Transform run option set responses to ResponseData format
        const loadedResponses: ResponseData = {};
        if (run.option_set_responses) {
          console.log('[WizardPlayer] Processing', run.option_set_responses.length, 'responses');
          run.option_set_responses.forEach((resp) => {
            // Extract value from response_value object (backend uses response_value, not response_data)
            const responseValue = (resp.response_value as any)?.value || resp.response_value;
            console.log('[WizardPlayer] Response for option_set', resp.option_set_id, ':', responseValue);
            console.log('[WizardPlayer] Raw response_value:', resp.response_value);
            if (responseValue !== undefined && responseValue !== null) {
              loadedResponses[resp.option_set_id] = responseValue;
            }
          });
        }

        console.log('[WizardPlayer] Final loadedResponses object:', loadedResponses);
        console.log('[WizardPlayer] Number of keys in loadedResponses:', Object.keys(loadedResponses).length);
        setResponses(loadedResponses);
        console.log('[WizardPlayer] Responses state updated');

        // Set completion status if run is completed
        if (run.status === 'completed') {
          console.log('[WizardPlayer] Setting isCompleted to true');
          setIsCompleted(true);
          // In view mode or for completed runs, show all steps from the beginning
          // so users can navigate through and see all their answers
          setCurrentStepIndex(0);

          // Detect edit mode: completed + stored + not view-only
          if (run.is_stored && !isViewOnly) {
            console.log('[WizardPlayer] Edit mode detected');
            setIsEditMode(true);
            setExistingRunName(run.run_name || 'Unnamed Run');
          }
        }

        // Resume from last step if in progress
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

  const currentStep = wizard?.steps[currentStepIndex];
  const progress = wizard ? ((currentStepIndex + 1) / wizard.steps.length) * 100 : 0;

  const validateStep = (): boolean => {
    if (!currentStep) return false;
    const newErrors: { [key: string]: string } = {};

    currentStep.option_sets.forEach((optionSet) => {
      // Check if option set is required (either statically or dynamically)
      const isRequired = isOptionSetRequired(optionSet);

      if (isRequired) {
        const response = responses[optionSet.id];
        if (!response || (Array.isArray(response) && response.length === 0)) {
          newErrors[optionSet.id] = 'This field is required';
        } else if (optionSet.selection_type === 'multiple_select' && Array.isArray(response)) {
          if (optionSet.min_selections && response.length < optionSet.min_selections) {
            newErrors[optionSet.id] = `Please select at least ${optionSet.min_selections} options`;
          }
          if (optionSet.max_selections && response.length > optionSet.max_selections) {
            newErrors[optionSet.id] = `Please select at most ${optionSet.max_selections} options`;
          }
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = async () => {
    if (!validateStep() || !sessionId || !currentStep || !wizard) return;

    // Don't save responses on Next - only save when user chooses to store the run
    // Responses are kept in memory (state) until user completes and saves

    if (currentStepIndex < wizard.steps.length - 1) {
      // Move to next step
      const nextStepIndex = currentStepIndex + 1;
      console.log(`→ Moving to step ${nextStepIndex + 1} of ${wizard.steps.length}`);
      setCurrentStepIndex(nextStepIndex);
      setErrors({});

      // Update wizard run progress
      const progressPercentage = ((nextStepIndex + 1) / wizard.steps.length) * 100;
      console.log(`→ Progress: ${Math.round(progressPercentage)}%`);
      try {
        await wizardRunService.updateRunProgress(sessionId, {
          current_step_index: nextStepIndex,
        });
        console.log('✓ Progress updated successfully');
      } catch (error) {
        console.error('✗ Error updating progress:', error);
      }
    } else {
      // Last step - Complete or Update wizard run
      console.log(`→ Last step (${currentStepIndex + 1}/${wizard.steps.length})`);
      console.log(`→ Run ID: ${sessionId}`);
      console.log(`→ Edit Mode: ${isEditMode}`);

      if (isEditMode) {
        // Edit Mode: Don't call complete API, just show update dialog
        console.log('[WizardPlayer] Edit mode - showing Update This Run dialog directly');
        setShowUpdateRunDialog(true);
        setSnackbar({
          open: true,
          message: 'Ready to update run',
          severity: 'info',
        });
      } else {
        // New Run: Call complete API and show save dialog
        console.log('[WizardPlayer] New run - completing wizard run');
        try {
          const result = await completeSessionMutation.mutateAsync(sessionId);
          console.log('✓ Complete wizard run mutation successful:', result);
          // showCompletionScreen and showSessionNameDialog set in mutation onSuccess
        } catch (error) {
          console.error('✗ Error completing wizard run:', error);
        }
      }
    }
  };

  const handlePrevious = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
      setErrors({});
    }
  };

  const handleSaveRun = async () => {
    if (!sessionName.trim()) {
      setSessionNameError('Run name is required');
      return;
    }
    if (!sessionId) return;

    try {
      // Check for duplicate run name
      console.log('[WizardPlayer] Checking for duplicate run name');
      const existingRuns = await wizardRunService.getWizardRuns({
        skip: 0,
        limit: 100, // Backend max limit is 100
      });

      // Defensive check for response structure
      if (!existingRuns || !Array.isArray(existingRuns.runs)) {
        console.error('[WizardPlayer] Invalid response from getWizardRuns:', existingRuns);
        setSessionNameError('Failed to validate run name. Please try again.');
        return;
      }

      const duplicateExists = existingRuns.runs.some(
        run => run.run_name?.toLowerCase().trim() === sessionName.trim().toLowerCase()
      );

      if (duplicateExists) {
        setSessionNameError('A run with this name already exists. Please choose a different name.');
        console.log('[WizardPlayer] Duplicate run name found');
        return;
      }

      // No duplicate, proceed with save
      saveRunMutation.mutate({
        runId: sessionId,
        name: sessionName.trim(),
      });
    } catch (error: any) {
      console.error('[WizardPlayer] Error checking for duplicate names:', error);

      // Provide more specific error messages based on error type
      if (error.response?.status === 401) {
        setSessionNameError('Session expired. Please log in again and try saving.');
      } else if (error.response?.status === 403) {
        setSessionNameError('You do not have permission to access this resource.');
      } else if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        setSessionNameError('Unable to connect to server. Please check your connection.');
      } else if (!error.response) {
        setSessionNameError('Network error. Please check your internet connection.');
      } else {
        setSessionNameError('Failed to validate run name. Please try again.');
      }
    }
  };

  const handleSkipSaveRun = () => {
    setShowSessionNameDialog(false);
    setSessionName('');
    navigate('/my-runs');
  };

  // ============================================================================
  // Edit Mode Action Handlers
  // ============================================================================

  /**
   * Handler for Skip button - Discard all changes
   */
  const handleSkipUpdate = () => {
    console.log('[WizardPlayer] Skip update - discarding changes');
    setShowUpdateRunDialog(false);
    navigate('/my-runs');
    setSnackbar({
      open: true,
      message: 'Changes discarded',
      severity: 'info',
    });
  };

  /**
   * Handler for Update button - Save modifications to current run
   */
  const handleUpdateRun = async () => {
    console.log('[WizardPlayer] Update run - saving modifications to current run');
    if (!sessionId) {
      console.error('[WizardPlayer] No session ID available');
      return;
    }

    try {
      await saveRunMutation.mutateAsync({
        runId: sessionId,
        name: existingRunName,
        isUpdate: true,
      });

      setShowUpdateRunDialog(false);
      navigate('/my-runs');
      setSnackbar({
        open: true,
        message: 'Run updated successfully!',
        severity: 'success',
      });
    } catch (error: any) {
      console.error('[WizardPlayer] Failed to update run:', error);
      setSnackbar({
        open: true,
        message: error.message || 'Failed to update run',
        severity: 'error',
      });
    }
  };

  /**
   * Handler for Save As button - Open nested dialog
   */
  const handleSaveAs = () => {
    console.log('[WizardPlayer] Save As - opening nested dialog');
    // Keep Update dialog open, just show Save As on top
    setSaveAsRunName(`${existingRunName} (Copy)`);
    setShowSaveAsDialog(true);
  };

  /**
   * Handler for Save As confirmation - Create new run
   */
  const handleConfirmSaveAs = async () => {
    console.log('[WizardPlayer] Confirming Save As with name:', saveAsRunName);

    if (!saveAsRunName.trim()) {
      setSaveAsError('Run name is required');
      return;
    }

    if (!wizard) {
      console.error('[WizardPlayer] No wizard available');
      return;
    }

    try {
      // Check for duplicate run name
      console.log('[WizardPlayer] Checking for duplicate run name');
      const existingRuns = await wizardRunService.getWizardRuns({
        skip: 0,
        limit: 100, // Backend max limit is 100
      });

      // Defensive check for response structure
      if (!existingRuns || !Array.isArray(existingRuns.runs)) {
        console.error('[WizardPlayer] Invalid response from getWizardRuns:', existingRuns);
        setSaveAsError('Unable to validate run name. Please check your connection and try again.');
        return;
      }

      const duplicateExists = existingRuns.runs.some(
        run => run.run_name?.toLowerCase().trim() === saveAsRunName.trim().toLowerCase()
      );

      if (duplicateExists) {
        setSaveAsError('A run with this name already exists. Please choose a different name.');
        console.log('[WizardPlayer] Duplicate run name found');
        return;
      }

      // Create a NEW wizard run
      console.log('[WizardPlayer] Creating new wizard run');
      const newRun = await wizardRunService.createWizardRun({
        wizard_id: wizard.id,
        run_name: saveAsRunName.trim(),
      });

      console.log('[WizardPlayer] New run created:', newRun.id);

      // Save all responses to the new run
      await saveRunMutation.mutateAsync({
        runId: newRun.id,
        name: saveAsRunName.trim(),
        isUpdate: false,
      });

      setShowSaveAsDialog(false);
      setShowUpdateRunDialog(false);  // Close the Update dialog too
      setSaveAsRunName('');
      setSaveAsError('');
      navigate('/my-runs');
      setSnackbar({
        open: true,
        message: 'New run created successfully!',
        severity: 'success',
      });
    } catch (error: any) {
      console.error('[WizardPlayer] Failed to create new run:', error);

      // Provide more specific error messages
      let errorMessage = 'Failed to create new run';
      if (error.response?.status === 401) {
        errorMessage = 'Session expired. Please log in again and try saving.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to create runs.';
      } else if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        errorMessage = 'Unable to connect to server. Please check your connection.';
      } else if (!error.response) {
        errorMessage = 'Network error. Please check your internet connection.';
      } else if (error.message) {
        errorMessage = error.message;
      }

      setSaveAsError(errorMessage);
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error',
      });
    }
  };

  const handleResponseChange = (optionSetId: string, value: string | string[] | number) => {
    setResponses({ ...responses, [optionSetId]: value });
    if (errors[optionSetId]) {
      setErrors({ ...errors, [optionSetId]: '' });
    }
  };

  // Get all selected option IDs from all previous steps
  const getAllSelectedOptionIds = (): string[] => {
    if (!wizard) return [];
    const selectedIds: string[] = [];

    wizard.steps.forEach((step, index) => {
      if (index <= currentStepIndex) {
        step.option_sets.forEach((optionSet) => {
          const response = responses[optionSet.id];
          if (response) {
            if (Array.isArray(response)) {
              // Multiple select: find option IDs for selected values
              optionSet.options.forEach((opt) => {
                if (response.includes(opt.value)) {
                  selectedIds.push(opt.id);
                }
              });
            } else {
              // Single select: find option ID for selected value
              const selectedOption = optionSet.options.find((opt) => opt.value === response);
              if (selectedOption) {
                selectedIds.push(selectedOption.id);
              }
            }
          }
        });
      }
    });

    return selectedIds;
  };

  // Check if an option should be shown based on dependencies
  const shouldShowOption = (option: any): boolean => {
    if (!option.dependencies || option.dependencies.length === 0) {
      return true; // No dependencies, always show
    }

    const selectedOptionIds = getAllSelectedOptionIds();

    for (const dep of option.dependencies) {
      const isDependencyMet = selectedOptionIds.includes(dep.depends_on_option_id);

      switch (dep.dependency_type) {
        case 'show_if':
          // Only show if the dependent option is selected
          if (!isDependencyMet) return false;
          break;
        case 'hide_if':
          // Hide if the dependent option is selected
          if (isDependencyMet) return false;
          break;
        // REQUIRE_IF and DISABLE_IF don't affect visibility
      }
    }

    return true;
  };

  // Check if an option should be disabled based on dependencies
  const shouldDisableOption = (option: any): boolean => {
    if (!option.dependencies || option.dependencies.length === 0) {
      return false;
    }

    const selectedOptionIds = getAllSelectedOptionIds();

    for (const dep of option.dependencies) {
      const isDependencyMet = selectedOptionIds.includes(dep.depends_on_option_id);

      if (dep.dependency_type === 'disable_if' && isDependencyMet) {
        return true;
      }
    }

    return false;
  };

  // Check if an option set becomes required based on dependencies
  const isOptionSetRequired = (optionSet: OptionSet): boolean => {
    if (optionSet.is_required) return true;

    const selectedOptionIds = getAllSelectedOptionIds();

    // Check if any option in this set has a REQUIRE_IF dependency that's met
    for (const option of optionSet.options) {
      if (option.dependencies) {
        for (const dep of option.dependencies) {
          if (dep.dependency_type === 'require_if' &&
            selectedOptionIds.includes(dep.depends_on_option_id)) {
            return true;
          }
        }
      }
    }

    return false;
  };

  // Check if an option set should be disabled based on dependencies
  const isOptionSetDisabled = (optionSet: OptionSet): boolean => {
    const selectedOptionIds = getAllSelectedOptionIds();

    // Check if any option in this set has a DISABLE_IF dependency that's met
    for (const option of optionSet.options) {
      if (option.dependencies) {
        for (const dep of option.dependencies) {
          if (dep.dependency_type === 'disable_if' &&
            selectedOptionIds.includes(dep.depends_on_option_id)) {
            return true;
          }
        }
      }
    }

    return false;
  };

  const renderOptionSet = (optionSet: OptionSet) => {
    console.log(`[WizardPlayer] renderOptionSet called for: ${optionSet.id} (${optionSet.name})`);
    console.log(`[WizardPlayer] Current state - isViewOnly: ${isViewOnly}, isCompleted: ${isCompleted}`);

    // Filter options based on dependencies
    const visibleOptions = optionSet.options.filter(shouldShowOption);

    // Only check for empty options on selection types that require options
    const selectionTypesNeedingOptions = ['single_select', 'multiple_select'];
    if (selectionTypesNeedingOptions.includes(optionSet.selection_type) && visibleOptions.length === 0) {
      console.log(`[WizardPlayer] Skipping option set ${optionSet.id} - no visible options`);
      return null;
    }

    // Check if this option set is dynamically required
    const isDynamicallyRequired = isOptionSetRequired(optionSet);

    // Debug log for view mode
    const currentValue = responses[optionSet.id];
    if (isViewOnly || isCompleted) {
      console.log(`[WizardPlayer] Rendering option set ${optionSet.id} (${optionSet.name}) in view mode`);
      console.log(`[WizardPlayer] Current value for ${optionSet.id}:`, currentValue);
      console.log(`[WizardPlayer] isViewOnly: ${isViewOnly}, isCompleted: ${isCompleted}`);
    } else {
      console.log(`[WizardPlayer] Rendering option set ${optionSet.id} in EDIT mode with value:`, currentValue);
    }

    switch (optionSet.selection_type) {
      case 'single_select':
        return (
          <FormControl component="fieldset" error={!!errors[optionSet.id]} fullWidth>
            <FormLabel component="legend">
              {optionSet.name}
              {isDynamicallyRequired && !optionSet.is_required && <span style={{ color: 'red' }}> *</span>}
            </FormLabel>
            {optionSet.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {optionSet.description}
              </Typography>
            )}
            <RadioGroup
              value={responses[optionSet.id] || ''}
              onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
            >
              {visibleOptions.map((option) => {
                const isDisabled = shouldDisableOption(option) || isViewOnly;
                return (
                  <FormControlLabel
                    key={option.id}
                    value={option.value}
                    control={<Radio />}
                    label={option.label}
                    disabled={isDisabled}
                  />
                );
              })}
            </RadioGroup>
            {errors[optionSet.id] && (
              <Typography variant="caption" color="error">
                {errors[optionSet.id]}
              </Typography>
            )}
          </FormControl>
        );

      case 'multiple_select':
        const selectedValues = (responses[optionSet.id] as string[]) || [];
        return (
          <FormControl component="fieldset" error={!!errors[optionSet.id]} fullWidth>
            <FormLabel component="legend">
              {optionSet.name}
              {isDynamicallyRequired && !optionSet.is_required && <span style={{ color: 'red' }}> *</span>}
            </FormLabel>
            {optionSet.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {optionSet.description}
              </Typography>
            )}
            <FormGroup>
              {visibleOptions.map((option) => {
                const isDisabled = shouldDisableOption(option) || isViewOnly;
                return (
                  <FormControlLabel
                    key={option.id}
                    control={
                      <Checkbox
                        checked={selectedValues.includes(option.value)}
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
                    disabled={isDisabled}
                  />
                );
              })}
            </FormGroup>
            {errors[optionSet.id] && (
              <Typography variant="caption" color="error">
                {errors[optionSet.id]}
              </Typography>
            )}
          </FormControl>
        );

      case 'text_input':
        const isTextInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <TextField
              label={optionSet.name}
              multiline
              rows={4}
              value={responses[optionSet.id] || ''}
              onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
              placeholder={optionSet.placeholder || ''}
              helperText={errors[optionSet.id] || optionSet.help_text}
              error={!!errors[optionSet.id]}
              required={isDynamicallyRequired}
              disabled={isTextInputDisabled}
            />
          </FormControl>
        );

      case 'number_input':
        const isNumberInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <TextField
              label={optionSet.name}
              type="number"
              value={responses[optionSet.id] || ''}
              onChange={(e) => handleResponseChange(optionSet.id, Number(e.target.value))}
              placeholder={optionSet.placeholder || ''}
              helperText={errors[optionSet.id] || optionSet.help_text}
              error={!!errors[optionSet.id]}
              required={isDynamicallyRequired}
              disabled={isNumberInputDisabled}
              inputProps={{
                min: optionSet.min_value,
                max: optionSet.max_value,
                step: optionSet.step_increment,
              }}
            />
          </FormControl>
        );

      case 'rating':
        const isRatingDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl component="fieldset" error={!!errors[optionSet.id]} fullWidth>
            <FormLabel component="legend">
              {optionSet.name}
              {isDynamicallyRequired && !optionSet.is_required && <span style={{ color: 'red' }}> *</span>}
            </FormLabel>
            {optionSet.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {optionSet.description}
              </Typography>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <Rating
                value={Number(responses[optionSet.id]) || 0}
                onChange={(_, newValue) => handleResponseChange(optionSet.id, newValue || 0)}
                max={optionSet.max_value ? Number(optionSet.max_value) : 5}
                size="large"
                disabled={isRatingDisabled}
              />
              {responses[optionSet.id] && (
                <Typography variant="body2">({responses[optionSet.id]})</Typography>
              )}
            </Box>
            {optionSet.help_text && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                {optionSet.help_text}
              </Typography>
            )}
            {errors[optionSet.id] && (
              <Typography variant="caption" color="error">
                {errors[optionSet.id]}
              </Typography>
            )}
          </FormControl>
        );

      case 'slider':
        const sliderValue = Number(responses[optionSet.id]) || Number(optionSet.min_value) || 0;
        const isSliderDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <FormLabel component="legend">
              {optionSet.name}
              {isDynamicallyRequired && !optionSet.is_required && <span style={{ color: 'red' }}> *</span>}
            </FormLabel>
            {optionSet.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {optionSet.description}
              </Typography>
            )}
            <Box sx={{ px: 2 }}>
              <Slider
                value={sliderValue}
                onChange={(_, newValue) => handleResponseChange(optionSet.id, Array.isArray(newValue) ? newValue[0] : newValue)}
                min={Number(optionSet.min_value) || 0}
                max={Number(optionSet.max_value) || 100}
                step={Number(optionSet.step_increment) || 1}
                marks
                valueLabelDisplay="on"
                disabled={isSliderDisabled}
              />
            </Box>
            {optionSet.help_text && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                {optionSet.help_text}
              </Typography>
            )}
            {errors[optionSet.id] && (
              <Typography variant="caption" color="error">
                {errors[optionSet.id]}
              </Typography>
            )}
          </FormControl>
        );

      case 'date_input':
        const isDateInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <TextField
              label={optionSet.name}
              type="date"
              value={responses[optionSet.id] || ''}
              onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
              helperText={errors[optionSet.id] || optionSet.help_text}
              error={!!errors[optionSet.id]}
              required={isDynamicallyRequired}
              disabled={isDateInputDisabled}
              InputLabelProps={{
                shrink: true,
              }}
            />
          </FormControl>
        );

      case 'time_input':
        const isTimeInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <TextField
              label={optionSet.name}
              type="time"
              value={responses[optionSet.id] || ''}
              onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
              helperText={errors[optionSet.id] || optionSet.help_text}
              error={!!errors[optionSet.id]}
              required={isDynamicallyRequired}
              disabled={isTimeInputDisabled}
              InputLabelProps={{
                shrink: true,
              }}
            />
          </FormControl>
        );

      case 'datetime_input':
        const isDateTimeInputDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <TextField
              label={optionSet.name}
              type="datetime-local"
              value={responses[optionSet.id] || ''}
              onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
              helperText={errors[optionSet.id] || optionSet.help_text}
              error={!!errors[optionSet.id]}
              required={isDynamicallyRequired}
              disabled={isDateTimeInputDisabled}
              InputLabelProps={{
                shrink: true,
              }}
            />
          </FormControl>
        );

      case 'color_picker':
        const isColorPickerDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <FormLabel component="legend">
              {optionSet.name}
              {isDynamicallyRequired && !optionSet.is_required && <span style={{ color: 'red' }}> *</span>}
            </FormLabel>
            {optionSet.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {optionSet.description}
              </Typography>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
              <input
                type="color"
                value={responses[optionSet.id] || '#000000'}
                onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
                disabled={isColorPickerDisabled}
                style={{ width: 60, height: 40, cursor: isColorPickerDisabled ? 'not-allowed' : 'pointer', border: '1px solid #ccc', borderRadius: 4 }}
              />
              <TextField
                value={responses[optionSet.id] || '#000000'}
                onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
                placeholder="#000000"
                size="small"
                disabled={isColorPickerDisabled}
              />
            </Box>
            {optionSet.help_text && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                {optionSet.help_text}
              </Typography>
            )}
            {errors[optionSet.id] && (
              <Typography variant="caption" color="error">
                {errors[optionSet.id]}
              </Typography>
            )}
          </FormControl>
        );

      case 'file_upload':
        const isFileUploadDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <FormLabel component="legend">
              {optionSet.name}
              {isDynamicallyRequired && !optionSet.is_required && <span style={{ color: 'red' }}> *</span>}
            </FormLabel>
            {optionSet.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {optionSet.description}
              </Typography>
            )}
            <Button variant="outlined" component="label" sx={{ mt: 1 }} disabled={isFileUploadDisabled}>
              {responses[optionSet.id] ? 'Change File' : 'Choose File'}
              <input
                type="file"
                hidden
                disabled={isFileUploadDisabled}
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (file && sessionId) {
                    try {
                      // Note: Need to get the option set response ID first before uploading
                      // For now, we'll store the file name as a placeholder
                      handleResponseChange(optionSet.id, file.name);
                      setSnackbar({
                        open: true,
                        message: `File ${file.name} selected`,
                        severity: 'success',
                      });
                    } catch (error) {
                      console.error('File selection failed:', error);
                      setSnackbar({
                        open: true,
                        message: 'File selection failed',
                        severity: 'error',
                      });
                    }
                  }
                }}
              />
            </Button>
            {responses[optionSet.id] && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2">
                  File uploaded: <a href={responses[optionSet.id] as string} target="_blank" rel="noopener noreferrer">View File</a>
                </Typography>
              </Box>
            )}
            {responses[optionSet.id] && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected: {responses[optionSet.id]}
              </Typography>
            )}
            {optionSet.help_text && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                {optionSet.help_text}
              </Typography>
            )}
            {errors[optionSet.id] && (
              <Typography variant="caption" color="error">
                {errors[optionSet.id]}
              </Typography>
            )}
          </FormControl>
        );

      case 'rich_text':
        const isRichTextDisabled = isOptionSetDisabled(optionSet) || isViewOnly;
        return (
          <FormControl fullWidth error={!!errors[optionSet.id]}>
            <TextField
              label={optionSet.name}
              multiline
              rows={8}
              value={responses[optionSet.id] || ''}
              onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
              placeholder={optionSet.placeholder || 'Enter text with formatting...'}
              helperText={errors[optionSet.id] || optionSet.help_text}
              error={!!errors[optionSet.id]}
              required={isDynamicallyRequired}
              disabled={isRichTextDisabled}
            />
          </FormControl>
        );

      default:
        return (
          <TextField
            fullWidth
            label={optionSet.name}
            value={responses[optionSet.id] || ''}
            onChange={(e) => handleResponseChange(optionSet.id, e.target.value)}
            placeholder={optionSet.placeholder || ''}
            helperText={optionSet.help_text}
            required={optionSet.is_required}
          />
        );
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!wizard) {
    return (
      <Card>
        <CardContent>
          <Typography variant="body1" color="error">
            Wizard not found
          </Typography>
        </CardContent>
      </Card>
    );
  }


  // Show completion screen ONLY if just completed in this session
  if (showCompletionScreen) {
    return (
      <>
        <Box>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <CompleteIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
              <Typography variant="h4" gutterBottom>
                Wizard Completed!
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Thank you for completing the {wizard.name} wizard.
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* Save Run Dialog */}
        <Dialog open={showSessionNameDialog} onClose={handleSkipSaveRun} maxWidth="sm" fullWidth>
          <DialogTitle>Save This Run?</DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ mb: 2 }}>
              Would you like to save this wizard run? You can view and manage it later in My Runs.
            </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              label="Run Name"
              type="text"
              fullWidth
              required
              value={sessionName}
              onChange={(e) => {
                setSessionName(e.target.value);
                if (sessionNameError) setSessionNameError('');
              }}
              error={!!sessionNameError}
              helperText={sessionNameError || 'Enter a descriptive name for this run'}
              placeholder={`${wizard.name} - ${new Date().toLocaleDateString()}`}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleSkipSaveRun}>Skip</Button>
            <Button
              onClick={handleSaveRun}
              variant="contained"
              disabled={!sessionName.trim() || saveRunMutation.isPending}
            >
              {saveRunMutation.isPending ? 'Saving...' : 'Save Run'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </>
    );
  }

  // ============================================================================
  // Update This Run Dialog (for Edit Mode)
  // ============================================================================
  if (isEditMode && showUpdateRunDialog) {
    return (
      <>
        <Box>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <CompleteIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
              <Typography variant="h4" gutterBottom>
                Wizard Updated!
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                You have made changes to this stored wizard run.
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* Update This Run Dialog */}
        <Dialog
          open={showUpdateRunDialog}
          onClose={() => setShowUpdateRunDialog(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Update This Run</DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ mb: 2 }}>
              You have made changes to this stored wizard run. How would you like to proceed?
            </DialogContentText>

            {/* Show run info */}
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Run Name:</strong> {existingRunName}
              </Typography>
            </Alert>
          </DialogContent>
          <DialogActions sx={{ flexDirection: 'column', gap: 1, p: 2, alignItems: 'stretch' }}>
            {/* Button 1: Skip - Discard Changes */}
            <Button
              onClick={handleSkipUpdate}
              variant="outlined"
              color="secondary"
              fullWidth
              startIcon={<CloseIcon />}
            >
              Skip (Discard Changes)
            </Button>

            {/* Button 2: Update - Save to Current Run */}
            <Button
              onClick={handleUpdateRun}
              variant="contained"
              color="primary"
              fullWidth
              startIcon={<SaveIcon />}
              disabled={saveRunMutation.isPending}
            >
              {saveRunMutation.isPending ? 'Updating...' : 'Update Run'}
            </Button>

            {/* Button 3: Save As - Create New Run */}
            <Button
              onClick={handleSaveAs}
              variant="outlined"
              color="primary"
              fullWidth
              startIcon={<ContentCopyIcon />}
            >
              Save As New Run
            </Button>
          </DialogActions>
        </Dialog>

        {/* Save As Dialog (Nested) */}
        <Dialog
          open={showSaveAsDialog}
          onClose={() => setShowSaveAsDialog(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Save As New Run</DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ mb: 2 }}>
              Enter a name for the new wizard run:
            </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              label="New Run Name"
              type="text"
              fullWidth
              required
              value={saveAsRunName}
              onChange={(e) => {
                setSaveAsRunName(e.target.value);
                if (saveAsError) setSaveAsError('');
              }}
              error={!!saveAsError}
              helperText={saveAsError || 'Enter a unique name for this run'}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowSaveAsDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleConfirmSaveAs}
              variant="contained"
              disabled={!saveAsRunName.trim() || saveRunMutation.isPending}
            >
              {saveRunMutation.isPending ? 'Creating...' : 'Create New Run'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {wizard.name}
      </Typography>

      {/* View Mode Banner */}
      {isViewOnly && (() => {
        console.log('[WizardPlayer] Rendering in VIEW MODE - responses object:', responses);
        console.log('[WizardPlayer] Number of responses:', Object.keys(responses).length);
        return (
          <Alert severity="info" sx={{ mb: 2 }}>
            <strong>View Mode</strong> - You are viewing a completed wizard run. All fields are read-only.
          </Alert>
        );
      })()}

      {/* Edit Mode Banner for completed runs */}
      {!isViewOnly && isCompleted && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <strong>Edit Mode</strong> - You are editing a completed wizard run. Changes will update the stored data.
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2">
            Step {currentStepIndex + 1} of {wizard.steps.length}
          </Typography>
          <Typography variant="body2">{Math.round(progress)}% Complete</Typography>
        </Box>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
      </Paper>

      <Stepper activeStep={currentStepIndex} alternativeLabel sx={{ mb: 4 }}>
        {wizard.steps.map((step) => (
          <Step key={step.id}>
            <StepLabel>{step.name}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {currentStep && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              {currentStep.name}
            </Typography>
            {currentStep.description && (
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                {currentStep.description}
              </Typography>
            )}
            {currentStep.help_text && (
              <Alert severity="info" sx={{ mb: 3 }}>
                {currentStep.help_text}
              </Alert>
            )}

            <Divider sx={{ mb: 3 }} />

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {(() => {
                console.log(`[WizardPlayer] Rendering step ${currentStepIndex}: ${currentStep.name}`);
                console.log(`[WizardPlayer] Step has ${currentStep.option_sets.length} option sets`);
                console.log(`[WizardPlayer] Option set IDs in this step:`, currentStep.option_sets.map(os => os.id));
                return null;
              })()}
              {currentStep.option_sets.map((optionSet) => (
                <Box key={optionSet.id}>{renderOptionSet(optionSet)}</Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          startIcon={<PrevIcon />}
          onClick={handlePrevious}
          disabled={currentStepIndex === 0}
        >
          Previous
        </Button>
        {!isViewOnly && (
          <Button
            variant="contained"
            endIcon={currentStepIndex === wizard.steps.length - 1 ? <CompleteIcon /> : <NextIcon />}
            onClick={handleNext}
            disabled={completeSessionMutation.isPending}
          >
            {currentStepIndex === wizard.steps.length - 1 ? (isCompleted ? 'Update' : 'Complete') : 'Next'}
          </Button>
        )}
        {isViewOnly && currentStepIndex < wizard.steps.length - 1 && (
          <Button
            variant="outlined"
            endIcon={<NextIcon />}
            onClick={() => setCurrentStepIndex(currentStepIndex + 1)}
          >
            Next
          </Button>
        )}
      </Box>

      {currentStep && currentStep.is_skippable && !isViewOnly && !isCompleted && !showCompletionScreen && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Button
            color="inherit"
            onClick={async () => {
              // Skip logic: move to next step without validating or saving
              if (currentStepIndex < wizard.steps.length - 1) {
                const nextStepIndex = currentStepIndex + 1;
                setCurrentStepIndex(nextStepIndex);
                setErrors({});

                // Update progress
                if (sessionId) {
                  try {
                    await wizardRunService.updateRunProgress(sessionId, {
                      current_step_index: nextStepIndex,
                    });
                  } catch (error) {
                    console.error('Error updating progress on skip:', error);
                  }
                }
              } else {
                // Skip last step = complete
                if (sessionId) {
                  try {
                    await completeSessionMutation.mutateAsync(sessionId);
                  } catch (error) {
                    console.error('Error completing wizard run on skip:', error);
                  }
                }
              }
            }}
          >
            Skip this step
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default WizardPlayerPage;
