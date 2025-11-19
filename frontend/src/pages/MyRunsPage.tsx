import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tab,
  Tabs,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  LinearProgress,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
} from '@mui/material';
import {
  DirectionsRun as RunIcon,
  PlayArrow as ResumeIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Share as ShareIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { wizardRunService } from '../services';
import { WizardRun, WizardRunStats } from '../types';

const MyRunsPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [runs, setRuns] = useState<WizardRun[]>([]);
  const [stats, setStats] = useState<WizardRunStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [runToDelete, setRunToDelete] = useState<WizardRun | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadStats();
    loadRuns();
  }, [activeTab]);

  const loadStats = async () => {
    try {
      const statsData = await wizardRunService.getRunStats();
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const loadRuns = async () => {
    try {
      setLoading(true);
      setError(null);

      let data: WizardRun[];

      switch (activeTab) {
        case 0: // All Runs
          const response = await wizardRunService.getWizardRuns({ limit: 50 });
          data = response.runs;
          break;
        case 1: // In Progress
          data = await wizardRunService.getInProgressRuns();
          break;
        case 2: // Completed
          data = await wizardRunService.getCompletedRuns(0, 50);
          break;
        case 3: // Favorites
          data = await wizardRunService.getFavoriteRuns();
          break;
        default:
          data = [];
      }

      setRuns(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load wizard runs');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (run: WizardRun) => {
    try {
      await wizardRunService.updateWizardRun(run.id, {
        is_favorite: !run.is_favorite,
      });
      loadRuns();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update favorite status');
    }
  };

  const handleResumeRun = (run: WizardRun) => {
    navigate(`/wizard/${run.wizard_id}?run_id=${run.id}`);
  };

  const handleViewRun = (run: WizardRun) => {
    navigate(`/wizard/${run.wizard_id}?run_id=${run.id}&view_only=true`);
  };

  const handleDeleteRun = (run: WizardRun) => {
    setRunToDelete(run);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!runToDelete) return;

    try {
      setDeleting(true);
      await wizardRunService.deleteWizardRun(runToDelete.id);
      setDeleteDialogOpen(false);
      setRunToDelete(null);
      loadRuns();
      loadStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete wizard run');
    } finally {
      setDeleting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'abandoned':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <RunIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
            <Typography variant="h4" component="h1" fontWeight="bold">
              My Wizard Runs
            </Typography>
          </Box>
        </Box>

        {/* Stats Cards */}
        {stats && (
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Runs
                  </Typography>
                  <Typography variant="h4">{stats.total_runs}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    In Progress
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {stats.in_progress}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Completed
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {stats.completed}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Favorites
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {stats.favorites}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label="All Runs" />
            <Tab label="In Progress" />
            <Tab label="Completed" />
            <Tab label="Favorites" />
          </Tabs>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Runs Grid */}
        {!loading && runs.length > 0 && (
          <Grid container spacing={3}>
            {runs.map((run) => (
              <Grid item xs={12} md={6} lg={4} key={run.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                      <Typography variant="h6" component="h3">
                        {run.run_name || 'Unnamed Run'}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleToggleFavorite(run)}
                        color={run.is_favorite ? 'error' : 'default'}
                      >
                        {run.is_favorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
                      </IconButton>
                    </Box>

                    {run.run_description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {run.run_description}
                      </Typography>
                    )}

                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={run.status.replace('_', ' ')}
                        color={getStatusColor(run.status) as any}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      {run.is_stored && (
                        <Chip label="Stored" size="small" variant="outlined" sx={{ mr: 1 }} />
                      )}
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Progress
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {Math.round(run.progress_percentage)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={run.progress_percentage}
                        sx={{ height: 8, borderRadius: 1 }}
                      />
                    </Box>

                    <Typography variant="caption" color="text.secondary" display="block">
                      Started: {formatDate(run.started_at)}
                    </Typography>
                    {run.completed_at && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        Completed: {formatDate(run.completed_at)}
                      </Typography>
                    )}
                    <Typography variant="caption" color="text.secondary" display="block">
                      Last accessed: {formatDate(run.last_accessed_at)}
                    </Typography>

                    {run.tags && run.tags.length > 0 && (
                      <Box sx={{ mt: 2, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {run.tags.map((tag, idx) => (
                          <Chip key={idx} label={tag} size="small" variant="outlined" />
                        ))}
                      </Box>
                    )}
                  </CardContent>

                  <CardActions>
                    {run.status === 'in_progress' ? (
                      <Button
                        size="small"
                        startIcon={<ResumeIcon />}
                        onClick={() => handleResumeRun(run)}
                      >
                        Resume
                      </Button>
                    ) : (
                      <Button
                        size="small"
                        startIcon={<ViewIcon />}
                        onClick={() => handleViewRun(run)}
                      >
                        View
                      </Button>
                    )}
                    <Tooltip title="Delete Run">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteRun(run)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Empty State */}
        {!loading && runs.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <RunIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No wizard runs found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Start a wizard to create your first run
            </Typography>
            <Button variant="contained" onClick={() => navigate('/wizards')}>
              Browse Wizards
            </Button>
          </Box>
        )}

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteDialogOpen} onClose={() => !deleting && setDeleteDialogOpen(false)}>
          <DialogTitle>Delete Wizard Run?</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete "{runToDelete?.run_name || 'this run'}"? This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)} disabled={deleting}>
              Cancel
            </Button>
            <Button
              onClick={confirmDelete}
              color="error"
              variant="contained"
              disabled={deleting}
              startIcon={deleting ? <CircularProgress size={20} /> : <DeleteIcon />}
            >
              {deleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default MyRunsPage;
