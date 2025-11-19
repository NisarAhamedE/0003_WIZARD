import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  LibraryBooks as TemplateIcon,
  PlayArrow as RunIcon,
  DirectionsRun as MyRunsIcon,
  Storage as StoreIcon,
  Build as BuildIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { wizardRunService } from '../services';
import { WizardRunStats } from '../types';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<WizardRunStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const runStats = await wizardRunService.getRunStats();
      setStats(runStats);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Template Gallery',
      description: 'Browse pre-built wizard templates and clone them to customize',
      icon: <TemplateIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      action: () => navigate('/templates'),
      buttonText: 'Browse Templates',
      color: 'primary.main',
    },
    {
      title: 'Run Wizard',
      description: 'Explore available wizards and start a new wizard run',
      icon: <RunIcon sx={{ fontSize: 48, color: 'secondary.main' }} />,
      action: () => navigate('/wizards'),
      buttonText: 'Run Wizard',
      color: 'secondary.main',
    },
    {
      title: 'My Runs',
      description: 'Continue your in-progress runs or view completed ones',
      icon: <MyRunsIcon sx={{ fontSize: 48, color: 'success.main' }} />,
      action: () => navigate('/runs'),
      buttonText: 'View My Runs',
      color: 'success.main',
    },
  ];

  const adminActions = [
    {
      title: 'Wizard Builder',
      description: 'Create and customize wizards from scratch or templates',
      icon: <BuildIcon sx={{ fontSize: 48, color: 'warning.main' }} />,
      action: () => navigate('/admin/wizard-builder'),
      buttonText: 'Build Wizard',
      color: 'warning.main',
    },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {user?.full_name || user?.username}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your role:{' '}
          <Chip
            label={user?.role?.name?.replace('_', ' ').toUpperCase()}
            size="small"
            color={
              user?.role?.name === 'super_admin'
                ? 'error'
                : user?.role?.name === 'admin'
                ? 'warning'
                : 'default'
            }
          />
        </Typography>
      </Box>

      {/* Statistics Dashboard */}
      {!loading && stats && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
            Your Statistics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="caption">
                    Total Runs
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {stats.total_runs}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="caption">
                    In Progress
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {stats.in_progress}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="caption">
                    Completed
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {stats.completed}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="caption">
                    Stored
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {stats.stored}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Quick Actions
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {quickActions.map((action, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6,
                },
              }}
            >
              <CardContent
                sx={{
                  flexGrow: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                }}
              >
                <Box sx={{ mb: 2 }}>{action.icon}</Box>
                <Typography variant="h6" gutterBottom>
                  {action.title}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 3, flexGrow: 1 }}
                >
                  {action.description}
                </Typography>
                <Button
                  variant="contained"
                  onClick={action.action}
                  fullWidth
                  sx={{ bgcolor: action.color }}
                >
                  {action.buttonText}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Admin Actions */}
      {user?.role?.name && ['admin', 'super_admin'].includes(user.role.name) && (
        <>
          <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
            Admin Actions
          </Typography>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {adminActions.map((action, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardContent
                    sx={{
                      flexGrow: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      textAlign: 'center',
                    }}
                  >
                    <Box sx={{ mb: 2 }}>{action.icon}</Box>
                    <Typography variant="h6" gutterBottom>
                      {action.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 3, flexGrow: 1 }}
                    >
                      {action.description}
                    </Typography>
                    <Button
                      variant="contained"
                      onClick={action.action}
                      fullWidth
                      sx={{ bgcolor: action.color }}
                    >
                      {action.buttonText}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Wizard Lifecycle System
        </Typography>
        <Card>
          <CardContent>
            <Typography variant="body1" paragraph>
              Welcome to the Multi-Wizard Platform! Follow the wizard lifecycle:
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={2.4}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <TemplateIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="subtitle2" fontWeight="bold">
                    1. Template Gallery
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Browse pre-built templates
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <BuildIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                  <Typography variant="subtitle2" fontWeight="bold">
                    2. Wizard Builder
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Create or customize wizards
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <RunIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
                  <Typography variant="subtitle2" fontWeight="bold">
                    3. Run Wizard
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Execute wizards step-by-step
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <MyRunsIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                  <Typography variant="subtitle2" fontWeight="bold">
                    4. My Runs
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Track and resume runs
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <StoreIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                  <Typography variant="subtitle2" fontWeight="bold">
                    5. Store Wizard
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Save and share completed runs
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default DashboardPage;
