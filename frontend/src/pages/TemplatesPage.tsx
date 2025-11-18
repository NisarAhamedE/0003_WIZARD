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
  Replay as ReplayIcon,
  Public as PublicIcon,
  Lock as PrivateIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { templateService } from '../services/template.service';
import { format } from 'date-fns';

const TemplatesPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templateService.getTemplates(),
  });

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM d, yyyy');
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
        My Templates
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        View and manage templates saved from completed wizard sessions
      </Typography>

      {templates?.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary">
              No templates available. Complete a wizard session and save it as a template!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {templates?.map((template) => (
            <Grid item xs={12} sm={6} md={4} key={template.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                      {template.name}
                    </Typography>
                    {template.is_public ? (
                      <Chip
                        icon={<PublicIcon />}
                        label="Public"
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ) : (
                      <Chip
                        icon={<PrivateIcon />}
                        label="Private"
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2, minHeight: 40 }}
                  >
                    {template.description || 'No description'}
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
                    {template.tags.map((tag, index) => (
                      <Chip key={index} label={tag} size="small" />
                    ))}
                  </Box>

                  <Typography variant="caption" color="text.secondary" display="block">
                    Created: {formatDate(template.created_at)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Used {template.times_used} times
                  </Typography>
                </CardContent>

                <CardActions sx={{ gap: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<ViewIcon />}
                    fullWidth
                    onClick={() => navigate(`/templates/${template.id}`)}
                  >
                    View
                  </Button>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<ReplayIcon />}
                    fullWidth
                  >
                    Use Template
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

export default TemplatesPage;
