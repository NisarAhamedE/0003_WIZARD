import React, { useState, useEffect } from 'react';
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
  Switch,
  Slider,
  Rating,
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
  CheckCircle as CompleteIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
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
  const searchParams = new URLSearchParams(window.location.search);
  const sessionIdFromUrl = searchParams.get('session');
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [responses, setResponses] = useState<ResponseData>({});
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isCompleted, setIsCompleted] = useState(false);

  // Session name dialog state
  const [showSessionNameDialog, setShowSessionNameDialog] = useState(false);
  const [sessionName, setSessionName] = useState('');
  const [sessionNameError, setSessionNameError] = useState('');

  // Template dialog state
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [templateIsPublic, setTemplateIsPublic] = useState(false);

  // Snackbar state
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({ open: false, message: '', severity: 'success' });

  const { data: wizard, isLoading } = useQuery({
    queryKey: ['wizard', wizardId],
    queryFn: () => wizardService.getWizard(wizardId!),
    enabled: !!wizardId,
  });

  const createSessionMutation = useMutation({
    mutationFn: (data: { wizard_id: string; run_name: string }) =>
      wizardRunService.createWizardRun(data),
    onSuccess: (run) => {
      setSessionId(run.id);
      setShowSessionNameDialog(false);
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Failed to create run',
        severity: 'error',
      });
    },
  });

  const saveResponseMutation = useMutation({
    mutationFn: async (data: { session_id: string; responses: any[] }) => {
      // Save each response individually
      for (const response of data.responses) {
        await sessionService.saveResponse(data.session_id, {
          step_id: response.step_id,
          option_set_id: response.option_set_id,
          response_data: response.response_data,
        });
      }
    },
  });

  const completeSessionMutation = useMutation({
    mutationFn: (id: string) => sessionService.completeSession(id),
    onSuccess: (data) => {
      console.log('✓ Session completed successfully:', data);
      setIsCompleted(true);
      // Invalidate sessions cache to refresh the list
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      // Show dialog asking if user wants to save as template
      setShowTemplateDialog(true);
      setSnackbar({
        open: true,
        message: 'Wizard completed successfully!',
        severity: 'success',
      });
    },
    onError: (error: any) => {
      console.error('✗ Error completing session:', error);

      // If session is already completed (not in progress), treat as success
      if (error.response?.data?.detail === 'Session is not in progress') {
        console.log('Session was already completed, showing completion screen');
        setIsCompleted(true);
        queryClient.invalidateQueries({ queryKey: ['sessions'] });
        setShowTemplateDialog(true);
        setSnackbar({
          open: true,
          message: 'Wizard completed successfully!',
          severity: 'success',
        });
        return;
      }

      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to complete session',
        severity: 'error',
      });
      // Still mark as completed locally for UX if it's a terminal error
      // But if it's a real error (e.g. network), maybe we shouldn't?
      // For now, keeping existing behavior but fixing the confusing error message
      setIsCompleted(true);
    },
  });

  const saveTemplateMutation = useMutation({
    mutationFn: (data: { sessionId: string; name: string; description?: string; is_public?: boolean }) =>
      templateService.createTemplateFromSession(data.sessionId, {
        name: data.name,
        description: data.description,
        is_public: data.is_public,
      }),
    onSuccess: () => {
      setSnackbar({
        open: true,
        message: 'Template saved successfully!',
        severity: 'success',
      });
      setShowTemplateDialog(false);
      resetTemplateForm();
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Failed to save template',
        severity: 'error',
      });
    },
  });

  const resetTemplateForm = () => {
    setTemplateName('');
    setTemplateDescription('');
    setTemplateIsPublic(false);
  };

  // Load existing session from URL or show session name dialog for new sessions
  useEffect(() => {
    if (wizard && !sessionId) {
      if (sessionIdFromUrl) {
        // Load existing session from URL
        setSessionId(sessionIdFromUrl);
      } else {
        // Show dialog for new session
        setShowSessionNameDialog(true);
      }
    }
  }, [wizard, sessionIdFromUrl]);

  // Load session responses when resuming an existing session
  useEffect(() => {
    const loadSessionResponses = async () => {
      if (!sessionId || !wizard) return;

      try {
        const session = await sessionService.getSession(sessionId);

        // Transform session responses to ResponseData format
        const loadedResponses: ResponseData = {};
        session.responses.forEach((resp) => {
          // Extract value from response_data object
          const responseValue = (resp.response_data as any).value;
          if (responseValue !== undefined && responseValue !== null) {
            loadedResponses[resp.option_set_id] = responseValue;
          }
        });

        setResponses(loadedResponses);

        // Set completion status if session is completed
        if (session.status === 'completed') {
          setIsCompleted(true);
        }

        // Optionally: Resume from last step
        // Find the step index based on current_step_id
        if (session.current_step_id && session.status === 'in_progress') {
          const stepIndex = wizard.steps.findIndex(s => s.id === session.current_step_id);
          if (stepIndex !== -1) {
            setCurrentStepIndex(stepIndex);
          }
        }
      } catch (error) {
        console.error('Failed to load session responses:', error);
        setSnackbar({
          open: true,
          message: 'Failed to load session data',
          severity: 'error',
        });
      }
    };

    loadSessionResponses();
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

    // Save responses for current step
    const stepResponses = currentStep.option_sets.map((os) => ({
      step_id: currentStep.id,
      option_set_id: os.id,
      response_data: { value: responses[os.id] || null },
    }));

    try {
      await saveResponseMutation.mutateAsync({
        session_id: sessionId,
        responses: stepResponses,
      });
    } catch (error) {
      console.error('Error saving response:', error);
      // Continue even if save fails for better UX
    }

    if (currentStepIndex < wizard.steps.length - 1) {
      // Move to next step
      const nextStepIndex = currentStepIndex + 1;
      console.log(`→ Moving to step ${nextStepIndex + 1} of ${wizard.steps.length}`);
      setCurrentStepIndex(nextStepIndex);
      setErrors({});

      // Update session progress
      const progressPercentage = ((nextStepIndex + 1) / wizard.steps.length) * 100;
      console.log(`→ Progress: ${Math.round(progressPercentage)}%`);
      try {
        await sessionService.updateSession(sessionId, {
          current_step_id: wizard.steps[nextStepIndex].id,
          progress_percentage: Math.round(progressPercentage),
        } as any);
        console.log('✓ Progress updated successfully');
      } catch (error) {
        console.error('✗ Error updating progress:', error);
      }
    } else {
      // Complete session (last step)
      console.log(`→ Last step (${currentStepIndex + 1}/${wizard.steps.length}) - Completing session...`);
      console.log(`→ Session ID: ${sessionId}`);
      try {
        const result = await completeSessionMutation.mutateAsync(sessionId);
        console.log('✓ Complete session mutation successful:', result);
      } catch (error) {
        console.error('✗ Error completing session:', error);
        // Show error to user but still mark as completed locally for UX
        setIsCompleted(true);
      }
    }
  };

  const handlePrevious = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
      setErrors({});
    }
  };

  const handleSaveAsTemplate = () => {
    if (!sessionId || !templateName.trim()) return;
    saveTemplateMutation.mutate({
      sessionId,
      name: templateName.trim(),
      description: templateDescription.trim() || undefined,
      is_public: templateIsPublic,
    });
  };

  const handleSkipTemplate = () => {
    setShowTemplateDialog(false);
    resetTemplateForm();
  };

  const handleCreateSession = () => {
    if (!sessionName.trim()) {
      setSessionNameError('Run name is required');
      return;
    }
    if (!wizard) return;

    createSessionMutation.mutate({
      wizard_id: wizard.id,
      run_name: sessionName.trim(),
    });
  };

  const handleCancelSessionCreation = () => {
    setShowSessionNameDialog(false);
    navigate('/wizards');
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
    // Filter options based on dependencies
    const visibleOptions = optionSet.options.filter(shouldShowOption);

    // Only check for empty options on selection types that require options
    const selectionTypesNeedingOptions = ['single_select', 'multiple_select'];
    if (selectionTypesNeedingOptions.includes(optionSet.selection_type) && visibleOptions.length === 0) {
      return null;
    }

    // Check if this option set is dynamically required
    const isDynamicallyRequired = isOptionSetRequired(optionSet);
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
                const isDisabled = shouldDisableOption(option);
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
                const isDisabled = shouldDisableOption(option);
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
        const isTextInputDisabled = isOptionSetDisabled(optionSet);
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
        const isNumberInputDisabled = isOptionSetDisabled(optionSet);
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
        const isRatingDisabled = isOptionSetDisabled(optionSet);
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
        const isSliderDisabled = isOptionSetDisabled(optionSet);
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
        const isDateInputDisabled = isOptionSetDisabled(optionSet);
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
        const isTimeInputDisabled = isOptionSetDisabled(optionSet);
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
        const isDateTimeInputDisabled = isOptionSetDisabled(optionSet);
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
        const isColorPickerDisabled = isOptionSetDisabled(optionSet);
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
        const isFileUploadDisabled = isOptionSetDisabled(optionSet);
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
                      // Show uploading state (could add specific state for this)
                      const result = await sessionService.uploadFile(sessionId, file);
                      handleResponseChange(optionSet.id, result.url);
                      setSnackbar({
                        open: true,
                        message: `File ${file.name} uploaded successfully`,
                        severity: 'success',
                      });
                    } catch (error) {
                      console.error('Upload failed:', error);
                      setSnackbar({
                        open: true,
                        message: 'File upload failed',
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
        const isRichTextDisabled = isOptionSetDisabled(optionSet);
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

  // Show run name dialog before starting wizard
  if (showSessionNameDialog) {
    return (
      <>
        <Box>
          <Typography variant="h4" gutterBottom>
            {wizard.name}
          </Typography>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Start New Run
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Please provide a name for this wizard run. This will help you identify it later in your runs list.
              </Typography>
              <TextField
                autoFocus
                fullWidth
                label="Run Name"
                value={sessionName}
                onChange={(e) => {
                  setSessionName(e.target.value);
                  if (sessionNameError) setSessionNameError('');
                }}
                error={!!sessionNameError}
                helperText={sessionNameError || 'Enter a descriptive name for this run'}
                placeholder={`${wizard.name} - ${new Date().toLocaleDateString()}`}
                required
                sx={{ mb: 3 }}
              />
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={handleCancelSessionCreation}>
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  onClick={handleCreateSession}
                  disabled={createSessionMutation.isPending}
                >
                  {createSessionMutation.isPending ? 'Creating...' : 'Start Run'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>

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

  if (isCompleted) {
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
              <Button variant="contained" onClick={() => navigate('/sessions')}>
                View My Sessions
              </Button>
            </CardContent>
          </Card>
        </Box>

        {/* Save as Template Dialog */}
        <Dialog open={showTemplateDialog} onClose={handleSkipTemplate} maxWidth="sm" fullWidth>
          <DialogTitle>Save as Template?</DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ mb: 2 }}>
              Would you like to save this wizard session as a template? You can reuse it later or share it with others.
            </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              label="Template Name"
              type="text"
              fullWidth
              required
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Description (optional)"
              type="text"
              fullWidth
              multiline
              rows={3}
              value={templateDescription}
              onChange={(e) => setTemplateDescription(e.target.value)}
              sx={{ mb: 2 }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={templateIsPublic}
                  onChange={(e) => setTemplateIsPublic(e.target.checked)}
                />
              }
              label="Make this template public"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleSkipTemplate}>Skip</Button>
            <Button
              onClick={handleSaveAsTemplate}
              variant="contained"
              disabled={!templateName.trim() || saveTemplateMutation.isPending}
            >
              {saveTemplateMutation.isPending ? 'Saving...' : 'Save Template'}
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
        <Button
          variant="contained"
          endIcon={currentStepIndex === wizard.steps.length - 1 ? <CompleteIcon /> : <NextIcon />}
          onClick={handleNext}
          disabled={saveResponseMutation.isPending || completeSessionMutation.isPending}
        >
          {currentStepIndex === wizard.steps.length - 1 ? 'Complete' : 'Next'}
        </Button>
      </Box>

      {currentStep && currentStep.is_skippable && (
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
                const progressPercentage = ((nextStepIndex + 1) / wizard.steps.length) * 100;
                if (sessionId) {
                  try {
                    await sessionService.updateSession(sessionId, {
                      current_step_id: wizard.steps[nextStepIndex].id,
                      progress_percentage: Math.round(progressPercentage),
                    } as any);
                  } catch (error) {
                    console.error('Error updating progress on skip:', error);
                  }
                }
              } else {
                // Skip last step = complete? Or just finish?
                // Usually skip means "don't answer", so we just complete.
                if (sessionId) {
                  try {
                    await completeSessionMutation.mutateAsync(sessionId);
                  } catch (error) {
                    console.error('Error completing session on skip:', error);
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
