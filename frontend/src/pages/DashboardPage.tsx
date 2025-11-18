import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
} from '@mui/material';
import {
  AutoFixHigh as WizardIcon,
  PlayCircle as SessionIcon,
  Save as TemplateIcon,
  ArrowForward as ArrowIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const quickActions = [
    {
      title: 'Browse Wizards',
      description: 'Explore available wizards and start a new session',
      icon: <WizardIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      action: () => navigate('/wizards'),
      buttonText: 'View Wizards',
    },
    {
      title: 'My Sessions',
      description: 'Continue your in-progress sessions or view completed ones',
      icon: <SessionIcon sx={{ fontSize: 48, color: 'secondary.main' }} />,
      action: () => navigate('/sessions'),
      buttonText: 'View Sessions',
    },
    {
      title: 'Templates',
      description: 'Use saved templates to quickly replay wizard configurations',
      icon: <TemplateIcon sx={{ fontSize: 48, color: 'success.main' }} />,
      action: () => navigate('/templates'),
      buttonText: 'View Templates',
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

      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Quick Actions
      </Typography>

      <Grid container spacing={3}>
        {quickActions.map((action, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
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
                  variant="outlined"
                  endIcon={<ArrowIcon />}
                  onClick={action.action}
                  fullWidth
                >
                  {action.buttonText}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 6 }}>
        <Typography variant="h5" gutterBottom>
          Getting Started
        </Typography>
        <Card>
          <CardContent>
            <Typography variant="body1" paragraph>
              Welcome to the Multi-Wizard Platform! Here's how to get started:
            </Typography>
            <ol>
              <li>
                <Typography variant="body1" paragraph>
                  <strong>Browse Wizards</strong> - Explore available wizards and find one that matches your needs.
                </Typography>
              </li>
              <li>
                <Typography variant="body1" paragraph>
                  <strong>Start a Session</strong> - Begin a wizard session and follow the step-by-step process.
                </Typography>
              </li>
              <li>
                <Typography variant="body1" paragraph>
                  <strong>Save Progress</strong> - Your progress is automatically saved, so you can resume anytime.
                </Typography>
              </li>
              <li>
                <Typography variant="body1" paragraph>
                  <strong>Create Templates</strong> - Save completed sessions as templates for quick reuse.
                </Typography>
              </li>
            </ol>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default DashboardPage;
