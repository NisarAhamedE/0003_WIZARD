import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  AccessTime as TimeIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { wizardService } from '../services/wizard.service';

const WizardBrowserPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: wizards, isLoading } = useQuery({
    queryKey: ['wizards'],
    queryFn: () => wizardService.getWizards({ published_only: true }),
  });

  const getDifficultyColor = (level?: string) => {
    switch (level) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'warning';
      case 'hard':
        return 'error';
      default:
        return 'default';
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Available Wizards
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Choose a wizard to start your step-by-step journey
      </Typography>

      {wizards?.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary">
              No wizards available at the moment. Check back later!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {wizards?.map((wizard) => (
            <Grid item xs={12} sm={6} md={4} key={wizard.id}>
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
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    {wizard.name}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2, minHeight: 60 }}
                  >
                    {wizard.description || 'No description available'}
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    {wizard.difficulty_level && (
                      <Chip
                        size="small"
                        label={wizard.difficulty_level}
                        color={getDifficultyColor(wizard.difficulty_level)}
                      />
                    )}
                    {wizard.category && (
                      <Chip
                        size="small"
                        label={wizard.category.name}
                        variant="outlined"
                      />
                    )}
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <TimeIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      {wizard.estimated_time
                        ? `~${wizard.estimated_time} min`
                        : 'Time varies'}
                    </Typography>
                  </Box>

                  <Typography variant="caption" color="text.secondary">
                    {wizard.completed_sessions} / {wizard.total_sessions} sessions completed
                  </Typography>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<PlayIcon />}
                    onClick={() => navigate(`/wizard/${wizard.id}`)}
                    fullWidth
                  >
                    Start Wizard
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default WizardBrowserPage;
