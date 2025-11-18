import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Snackbar,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Grid,
} from '@mui/material';
import {
  PlayArrow as ResumeIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Save as SaveTemplateIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { sessionService } from '../services/session.service';
import { wizardService } from '../services/wizard.service';
import { templateService } from '../services/template.service';
import { format } from 'date-fns';

const SessionsPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

  // Create session dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedWizardId, setSelectedWizardId] = useState<string>('');
  const [sessionName, setSessionName] = useState('');

  // Save as template dialog state
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [sessionForTemplate, setSessionForTemplate] = useState<string | null>(null);
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [templateIsPublic, setTemplateIsPublic] = useState(false);

  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({ open: false, message: '', severity: 'success' });

  const { data: sessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => sessionService.getSessions(),
  });

  const { data: wizards, isLoading: wizardsLoading } = useQuery({
    queryKey: ['wizards-for-session'],
    queryFn: () => wizardService.getWizards({ published_only: true }),
  });

  const deleteMutation = useMutation({
    mutationFn: (sessionId: string) => sessionService.abandonSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      setSnackbar({
        open: true,
        message: 'Session deleted successfully',
        severity: 'success',
      });
      setDeleteDialogOpen(false);
      setSessionToDelete(null);
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Failed to delete session',
        severity: 'error',
      });
    },
  });

  const createSessionMutation = useMutation({
    mutationFn: (data: { wizard_id: string; session_name?: string }) =>
      sessionService.createSession(data),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      setCreateDialogOpen(false);
      setSelectedWizardId('');
      setSessionName('');
      // Navigate to the wizard player
      navigate(`/wizard/${session.wizard_id}?session=${session.id}`);
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Failed to create session',
        severity: 'error',
      });
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
      setTemplateDialogOpen(false);
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
    setSessionForTemplate(null);
    setTemplateName('');
    setTemplateDescription('');
    setTemplateIsPublic(false);
  };

  const handleDeleteClick = (sessionId: string) => {
    setSessionToDelete(sessionId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (sessionToDelete) {
      deleteMutation.mutate(sessionToDelete);
    }
  };

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setSessionToDelete(null);
  };

  const handleCreateSession = () => {
    if (!selectedWizardId || !sessionName.trim()) return;
    createSessionMutation.mutate({
      wizard_id: selectedWizardId,
      session_name: sessionName.trim(),
    });
  };

  const handleSaveAsTemplate = (sessionId: string) => {
    setSessionForTemplate(sessionId);
    setTemplateDialogOpen(true);
  };

  const handleConfirmSaveTemplate = () => {
    if (!sessionForTemplate || !templateName.trim()) return;
    saveTemplateMutation.mutate({
      sessionId: sessionForTemplate,
      name: templateName.trim(),
      description: templateDescription.trim() || undefined,
      is_public: templateIsPublic,
    });
  };

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

  if (sessionsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            My Sessions
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View and manage your wizard sessions
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create New Session
        </Button>
      </Box>

      {sessions?.length === 0 ? (
        <Card sx={{ mt: 2 }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              You haven't started any wizard sessions yet.
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
            >
              Create Your First Session
            </Button>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Session Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Started</TableCell>
                <TableCell>Last Activity</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sessions?.map((session) => (
                <TableRow key={session.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body1" fontWeight={500}>
                        {session.session_name || 'Unnamed Session'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {session.wizard_name || 'Unknown Wizard'}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={session.status.replace('_', ' ')}
                      color={getStatusColor(session.status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={Number(session.progress_percentage)}
                        sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="body2">
                        {Number(session.progress_percentage).toFixed(0)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{formatDate(session.started_at)}</TableCell>
                  <TableCell>{formatDate(session.last_activity_at)}</TableCell>
                  <TableCell align="right">
                    {session.status === 'in_progress' && (
                      <Tooltip title="Resume">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() =>
                            navigate(`/wizard/${session.wizard_id}?session=${session.id}`)
                          }
                        >
                          <ResumeIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {session.status === 'completed' && (
                      <Tooltip title="Save as Template">
                        <IconButton
                          size="small"
                          color="secondary"
                          onClick={() => handleSaveAsTemplate(session.id)}
                        >
                          <SaveTemplateIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/sessions/${session.id}`)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    {session.status !== 'completed' && (
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteClick(session.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create New Session Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => {
          setCreateDialogOpen(false);
          setSelectedWizardId('');
          setSessionName('');
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Session</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Choose a wizard and provide a name for your session to get started.
          </DialogContentText>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Select Wizard</InputLabel>
                <Select
                  value={selectedWizardId}
                  label="Select Wizard"
                  onChange={(e) => setSelectedWizardId(e.target.value)}
                  disabled={wizardsLoading}
                >
                  {wizards?.map((wizard) => (
                    <MenuItem key={wizard.id} value={wizard.id}>
                      {wizard.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Session Name"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                placeholder="e.g., My Custom Laptop Config"
                helperText="This will help you identify the session later"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setCreateDialogOpen(false);
              setSelectedWizardId('');
              setSessionName('');
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreateSession}
            variant="contained"
            disabled={!selectedWizardId || !sessionName.trim() || createSessionMutation.isPending}
          >
            {createSessionMutation.isPending ? 'Creating...' : 'Start Wizard'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Save as Template Dialog */}
      <Dialog open={templateDialogOpen} onClose={() => setTemplateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Save as Template</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Save your completed session as a template to reuse later or share with others.
          </DialogContentText>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Template Name"
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                placeholder="e.g., My Gaming Laptop Config"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description (Optional)"
                value={templateDescription}
                onChange={(e) => setTemplateDescription(e.target.value)}
                placeholder="Describe what this template is for..."
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={templateIsPublic}
                    onChange={(e) => setTemplateIsPublic(e.target.checked)}
                  />
                }
                label="Make this template public (others can use it)"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTemplateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmSaveTemplate}
            variant="contained"
            color="secondary"
            disabled={!templateName.trim() || saveTemplateMutation.isPending}
          >
            {saveTemplateMutation.isPending ? 'Saving...' : 'Save Template'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleCancelDelete}>
        <DialogTitle>Delete Session</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this session? This action cannot be undone and all
            progress will be lost.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          severity={snackbar.severity}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SessionsPage;
