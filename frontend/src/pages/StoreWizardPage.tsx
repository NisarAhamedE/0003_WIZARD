import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
} from '@mui/material';
import {
  Storage as StoreIcon,
  Visibility as ViewIcon,
  Share as ShareIcon,
  CompareArrows as CompareIcon,
  ContentCopy as CopyIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { wizardRunService } from '../services';
import { WizardRun, WizardRunShare } from '../types';

const StoreWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const [storedRuns, setStoredRuns] = useState<WizardRun[]>([]);
  const [selectedRuns, setSelectedRuns] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [selectedRun, setSelectedRun] = useState<WizardRun | null>(null);
  const [shareType, setShareType] = useState<'view' | 'edit' | 'clone'>('view');
  const [shareLink, setShareLink] = useState<string>('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  useEffect(() => {
    loadStoredRuns();
  }, []);

  const loadStoredRuns = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await wizardRunService.getStoredRuns(0, 100);
      setStoredRuns(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load stored runs');
    } finally {
      setLoading(false);
    }
  };

  const handleViewRun = (run: WizardRun) => {
    navigate(`/wizard/${run.wizard_id}?session=${run.id}&view_only=true`);
  };

  const handleShareRun = async (run: WizardRun) => {
    setSelectedRun(run);
    setShareDialogOpen(true);
  };

  const handleCreateShareLink = async () => {
    if (!selectedRun) return;

    try {
      const share = await wizardRunService.createShareLink(selectedRun.id, {
        run_id: selectedRun.id,
        share_type: shareType,
      });

      const link = `${window.location.origin}/shared-run/${share.share_token}`;
      setShareLink(link);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create share link');
    }
  };

  const handleCopyShareLink = () => {
    navigator.clipboard.writeText(shareLink);
    setSnackbarMessage('Share link copied to clipboard!');
    setSnackbarOpen(true);
  };

  const handleToggleSelection = (runId: string) => {
    setSelectedRuns((prev) =>
      prev.includes(runId) ? prev.filter((id) => id !== runId) : [...prev, runId]
    );
  };

  const handleCompareSelected = () => {
    if (selectedRuns.length < 2) {
      setError('Please select at least 2 runs to compare');
      return;
    }
    navigate(`/compare-runs?ids=${selectedRuns.join(',')}`);
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

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <StoreIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
            <Typography variant="h4" component="h1" fontWeight="bold">
              Store Wizard
            </Typography>
          </Box>
          {selectedRuns.length >= 2 && (
            <Button
              variant="contained"
              startIcon={<CompareIcon />}
              onClick={handleCompareSelected}
            >
              Compare Selected ({selectedRuns.length})
            </Button>
          )}
        </Box>

        {/* Info Box */}
        <Alert severity="info" sx={{ mb: 3 }}>
          This is your repository of saved wizard runs. You can view, share, compare, and export your stored runs.
        </Alert>

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

        {/* Stored Runs Grid */}
        {!loading && storedRuns.length > 0 && (
          <Grid container spacing={3}>
            {storedRuns.map((run) => (
              <Grid item xs={12} md={6} lg={4} key={run.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    border: selectedRuns.includes(run.id) ? 2 : 0,
                    borderColor: 'primary.main',
                    cursor: 'pointer',
                  }}
                  onClick={() => handleToggleSelection(run.id)}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                      <Typography variant="h6" component="h3">
                        {run.run_name || 'Unnamed Run'}
                      </Typography>
                      {selectedRuns.includes(run.id) && (
                        <Chip label="Selected" color="primary" size="small" />
                      )}
                    </Box>

                    {run.run_description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {run.run_description}
                      </Typography>
                    )}

                    <Box sx={{ mb: 2 }}>
                      <Chip label="Stored" color="success" size="small" sx={{ mr: 1 }} />
                      <Chip label="Completed" color="info" size="small" />
                    </Box>

                    <Typography variant="caption" color="text.secondary" display="block">
                      Completed: {run.completed_at ? formatDate(run.completed_at) : 'N/A'}
                    </Typography>

                    {run.calculated_price !== undefined && run.calculated_price !== null && (
                      <Typography variant="body2" color="primary" sx={{ mt: 1, fontWeight: 'bold' }}>
                        Total: ${run.calculated_price.toFixed(2)}
                      </Typography>
                    )}

                    {run.tags && run.tags.length > 0 && (
                      <Box sx={{ mt: 2, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {run.tags.map((tag, idx) => (
                          <Chip key={idx} label={tag} size="small" variant="outlined" />
                        ))}
                      </Box>
                    )}
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<ViewIcon />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewRun(run);
                      }}
                    >
                      View
                    </Button>
                    <Tooltip title="Share Run">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleShareRun(run);
                        }}
                      >
                        <ShareIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Export (Coming Soon)">
                      <IconButton size="small" disabled>
                        <DownloadIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Empty State */}
        {!loading && storedRuns.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <StoreIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No stored runs yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Complete a wizard and choose "Save to Store" to add runs here
            </Typography>
            <Button variant="contained" onClick={() => navigate('/wizards')}>
              Start a Wizard
            </Button>
          </Box>
        )}

        {/* Share Dialog */}
        <Dialog
          open={shareDialogOpen}
          onClose={() => {
            setShareDialogOpen(false);
            setShareLink('');
          }}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Share Wizard Run</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Create a shareable link for "{selectedRun?.run_name}"
              </Typography>

              {!shareLink ? (
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Share Type:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip
                      label="View Only"
                      color={shareType === 'view' ? 'primary' : 'default'}
                      onClick={() => setShareType('view')}
                    />
                    <Chip
                      label="Allow Edit"
                      color={shareType === 'edit' ? 'primary' : 'default'}
                      onClick={() => setShareType('edit')}
                    />
                    <Chip
                      label="Allow Clone"
                      color={shareType === 'clone' ? 'primary' : 'default'}
                      onClick={() => setShareType('clone')}
                    />
                  </Box>
                </Box>
              ) : (
                <Box>
                  <TextField
                    fullWidth
                    label="Share Link"
                    value={shareLink}
                    InputProps={{
                      readOnly: true,
                      endAdornment: (
                        <IconButton onClick={handleCopyShareLink} edge="end">
                          <CopyIcon />
                        </IconButton>
                      ),
                    }}
                  />
                </Box>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => {
                setShareDialogOpen(false);
                setShareLink('');
              }}
            >
              Close
            </Button>
            {!shareLink && (
              <Button onClick={handleCreateShareLink} variant="contained">
                Generate Link
              </Button>
            )}
          </DialogActions>
        </Dialog>

        {/* Snackbar */}
        <Snackbar
          open={snackbarOpen}
          autoHideDuration={3000}
          onClose={() => setSnackbarOpen(false)}
          message={snackbarMessage}
        />
      </Box>
    </Container>
  );
};

export default StoreWizardPage;
