import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Divider,
  Grid,
  Button,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Public as PublicIcon,
  Lock as PrivateIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { templateService } from '../services/template.service';
import { wizardService } from '../services/wizard.service';
import { format } from 'date-fns';

const TemplateViewPage: React.FC = () => {
  const { templateId } = useParams<{ templateId: string }>();
  const navigate = useNavigate();

  const { data: template, isLoading: templateLoading } = useQuery({
    queryKey: ['template', templateId],
    queryFn: () => templateService.getTemplate(templateId!),
    enabled: !!templateId,
  });

  const { data: wizard, isLoading: wizardLoading } = useQuery({
    queryKey: ['wizard', template?.wizard_id],
    queryFn: () => wizardService.getWizard(template!.wizard_id),
    enabled: !!template?.wizard_id,
  });

  if (templateLoading || wizardLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!template || !wizard) {
    return (
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" color="error">
          Template not found
        </Typography>
        <Button startIcon={<BackIcon />} onClick={() => navigate('/templates')} sx={{ mt: 2 }}>
          Back to Templates
        </Button>
      </Box>
    );
  }

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM d, yyyy h:mm a');
  };

  const getResponseValue = (optionSet: any, response: any) => {
    if (!response) return 'No selection';

    const responseData = response.response_data;
    const value = responseData.value;

    if (value === null || value === undefined) return 'No selection';

    switch (optionSet.selection_type) {
      case 'single_select':
        const singleOption = optionSet.options.find((opt: any) => opt.id === value);
        return singleOption?.label || 'Unknown option';

      case 'multiple_select':
        if (Array.isArray(value)) {
          const selectedOptions = optionSet.options.filter((opt: any) =>
            value.includes(opt.id)
          );
          return selectedOptions.length > 0
            ? selectedOptions.map((opt: any) => opt.label).join(', ')
            : 'No selections';
        }
        return 'Invalid response';

      case 'text_input':
      case 'text_area':
      case 'number_input':
      case 'date_picker':
      case 'color_picker':
        return String(value);

      case 'rating':
        return `${value} stars`;

      case 'slider':
        return `${value}${optionSet.help_text ? ` ${optionSet.help_text}` : ''}`;

      default:
        return String(value);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button startIcon={<BackIcon />} onClick={() => navigate('/templates')} sx={{ mb: 2 }}>
          Back to Templates
        </Button>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {template.name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {template.description || 'No description'}
            </Typography>
          </Box>
          {template.is_public ? (
            <Chip icon={<PublicIcon />} label="Public" color="primary" />
          ) : (
            <Chip icon={<PrivateIcon />} label="Private" />
          )}
        </Box>
      </Box>

      {/* Template Info Card */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Template Information
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Wizard
                    </Typography>
                    <Typography variant="body1">{wizard.name}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Times Used
                    </Typography>
                    <Typography variant="body1">{template.times_used}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Created
                    </Typography>
                    <Typography variant="body1">{formatDate(template.created_at)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Last Used
                    </Typography>
                    <Typography variant="body1">
                      {template.last_used_at ? formatDate(template.last_used_at) : 'Never'}
                    </Typography>
                  </Grid>
                </Grid>
                {template.tags.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Tags
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {template.tags.map((tag: string, index: number) => (
                        <Chip key={index} label={tag} size="small" />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Progress Overview
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Stepper
                activeStep={wizard.steps.length}
                orientation="vertical"
                sx={{ mt: 2 }}
              >
                {wizard.steps.map((step: any) => {
                  const hasResponse = template.responses.some((r: any) => r.step_id === step.id);
                  return (
                    <Step key={step.id} completed={hasResponse}>
                      <StepLabel>
                        {step.name}
                        {hasResponse && (
                          <Chip size="small" label="Configured" color="success" sx={{ ml: 1 }} />
                        )}
                      </StepLabel>
                    </Step>
                  );
                })}
              </Stepper>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Template Configuration - Read Only */}
      <Paper sx={{ p: 2, mb: 3, bgcolor: 'info.light', color: 'info.contrastText' }}>
        <Typography variant="body2">
          <strong>Note:</strong> This is a read-only view of the template configuration.
          Values cannot be modified.
        </Typography>
      </Paper>

      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Template Configuration
      </Typography>
      {wizard.steps.map((step: any) => {
        const stepResponses = template.responses.filter((r: any) => r.step_id === step.id);
        const hasResponses = stepResponses.length > 0;
        const stepIndex = wizard.steps.findIndex((s: any) => s.id === step.id);

        return (
          <Card key={step.id} sx={{ mb: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  Step {stepIndex + 1}: {step.name}
                </Typography>
                {hasResponses ? (
                  <Chip size="small" label="Configured" color="success" />
                ) : (
                  <Chip size="small" label="Not Configured" color="default" />
                )}
              </Box>
              {step.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {step.description}
                </Typography>
              )}
              <Divider sx={{ my: 2 }} />

              {hasResponses ? (
                <List>
                  {step.option_sets.map((optionSet: any) => {
                    const response = stepResponses.find((r: any) => r.option_set_id === optionSet.id);
                    return (
                      <ListItem key={optionSet.id} sx={{ px: 0 }}>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body1" fontWeight="medium">
                                {optionSet.name}
                              </Typography>
                              {optionSet.is_required && (
                                <Chip label="Required" size="small" color="error" variant="outlined" />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box component="span" sx={{ mt: 1, display: 'block' }}>
                              <Paper
                                sx={{
                                  p: 1.5,
                                  mt: 1,
                                  bgcolor: 'grey.50',
                                  border: '1px solid',
                                  borderColor: 'grey.300',
                                }}
                              >
                                <Typography
                                  component="span"
                                  variant="body1"
                                  color="text.primary"
                                >
                                  {getResponseValue(optionSet, response)}
                                </Typography>
                              </Paper>
                            </Box>
                          }
                        />
                      </ListItem>
                    );
                  })}
                </List>
              ) : (
                <Paper sx={{ p: 2, bgcolor: 'grey.50', textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No configuration saved for this step
                  </Typography>
                </Paper>
              )}
            </CardContent>
          </Card>
        );
      })}
    </Box>
  );
};

export default TemplateViewPage;
