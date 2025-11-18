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
  PlayArrow as ResumeIcon,
  Save as SaveTemplateIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { sessionService } from '../services/session.service';
import { wizardService } from '../services/wizard.service';
import { format } from 'date-fns';

const SessionDetailPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const { data: session, isLoading: sessionLoading } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => sessionService.getSession(sessionId!),
    enabled: !!sessionId,
  });

  const { data: wizard, isLoading: wizardLoading } = useQuery({
    queryKey: ['wizard', session?.wizard_id],
    queryFn: () => wizardService.getWizard(session!.wizard_id),
    enabled: !!session?.wizard_id,
  });

  if (sessionLoading || wizardLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!session || !wizard) {
    return (
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" color="error">
          Session not found
        </Typography>
        <Button startIcon={<BackIcon />} onClick={() => navigate('/sessions')} sx={{ mt: 2 }}>
          Back to Sessions
        </Button>
      </Box>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'abandoned':
        return 'error';
      case 'expired':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM d, yyyy h:mm a');
  };

  const getResponseValue = (optionSet: any, response: any) => {
    if (!response) return 'No response';

    const responseData = response.response_data;
    const value = responseData.value;

    if (value === null || value === undefined) return 'No response';

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

  const currentStepIndex = wizard.steps.findIndex(
    (step: any) => step.id === session.current_step_id
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button startIcon={<BackIcon />} onClick={() => navigate('/sessions')} sx={{ mb: 2 }}>
          Back to Sessions
        </Button>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              Session Details
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {session.session_name || 'Unnamed Session'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {session.status === 'in_progress' && (
              <Button
                variant="contained"
                startIcon={<ResumeIcon />}
                onClick={() => navigate(`/wizard/${wizard.id}?session=${session.id}`)}
              >
                Resume Session
              </Button>
            )}
            {session.status === 'completed' && (
              <Button
                variant="outlined"
                startIcon={<SaveTemplateIcon />}
                onClick={() => navigate('/sessions')}
              >
                Save as Template
              </Button>
            )}
          </Box>
        </Box>
      </Box>

      {/* Session Info Card */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Session Information
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
                      Status
                    </Typography>
                    <Chip
                      size="small"
                      label={session.status.replace('_', ' ')}
                      color={getStatusColor(session.status)}
                      sx={{ mt: 0.5 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Progress
                    </Typography>
                    <Typography variant="body1">
                      {Number(session.progress_percentage).toFixed(0)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Started
                    </Typography>
                    <Typography variant="body1">{formatDate(session.started_at)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Last Activity
                    </Typography>
                    <Typography variant="body1">{formatDate(session.last_activity_at)}</Typography>
                  </Grid>
                  {session.completed_at && (
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Completed
                      </Typography>
                      <Typography variant="body1">{formatDate(session.completed_at)}</Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Progress
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Stepper
                activeStep={session.status === 'completed' ? wizard.steps.length : currentStepIndex}
                orientation="vertical"
                sx={{ mt: 2 }}
              >
                {wizard.steps.map((step: any) => {
                  const hasResponse = session.responses.some((r: any) => r.step_id === step.id);
                  return (
                    <Step key={step.id} completed={hasResponse}>
                      <StepLabel>
                        {step.name}
                        {hasResponse && (
                          <Chip size="small" label="Answered" color="success" sx={{ ml: 1 }} />
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

      {/* Responses */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Responses
      </Typography>
      {wizard.steps.map((step: any) => {
        const stepResponses = session.responses.filter((r: any) => r.step_id === step.id);
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
                  <Chip size="small" label="Answered" color="success" />
                ) : (
                  <Chip size="small" label="Not Answered" color="default" />
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
                          primary={optionSet.name}
                          secondary={
                            <Box component="span" sx={{ mt: 1, display: 'block' }}>
                              <Typography
                                component="span"
                                variant="body1"
                                color="text.primary"
                              >
                                {getResponseValue(optionSet, response)}
                              </Typography>
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
                    No responses recorded for this step yet
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

export default SessionDetailPage;
