import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
  Rating,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  LibraryBooks as TemplateIcon,
  ContentCopy as CloneIcon,
  TrendingUp as PopularIcon,
  Star as TopRatedIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { wizardTemplateService } from '../services';
import { WizardTemplate, WizardTemplateStats } from '../types';

const TemplateGalleryPage: React.FC = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<WizardTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [viewMode, setViewMode] = useState<'all' | 'popular' | 'top-rated'>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<WizardTemplate | null>(null);
  const [templateStats, setTemplateStats] = useState<WizardTemplateStats | null>(null);
  const [cloneDialogOpen, setCloneDialogOpen] = useState(false);
  const [wizardName, setWizardName] = useState('');
  const [wizardDescription, setWizardDescription] = useState('');
  const [cloning, setCloning] = useState(false);

  const categories = ['Business', 'Marketing', 'Development', 'Design', 'Education', 'Other'];
  const difficulties = ['easy', 'medium', 'hard'];

  useEffect(() => {
    loadTemplates();
  }, [viewMode, categoryFilter, difficultyFilter, searchQuery]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);

      let data: WizardTemplate[];

      if (viewMode === 'popular') {
        data = await wizardTemplateService.getPopularTemplates(20);
      } else if (viewMode === 'top-rated') {
        data = await wizardTemplateService.getTopRatedTemplates(20);
      } else {
        const response = await wizardTemplateService.getTemplates({
          search: searchQuery || undefined,
          category: categoryFilter || undefined,
          difficulty_level: difficultyFilter as any || undefined,
          limit: 50,
        });
        data = response.templates;
      }

      setTemplates(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTemplate = async (template: WizardTemplate) => {
    setSelectedTemplate(template);
    try {
      const stats = await wizardTemplateService.getTemplateStats(template.id);
      setTemplateStats(stats);
    } catch (err) {
      console.error('Failed to load template stats:', err);
    }
  };

  const handleCloneTemplate = (template: WizardTemplate) => {
    setSelectedTemplate(template);
    setWizardName(`${template.template_name} (Clone)`);
    setWizardDescription(template.template_description || '');
    setCloneDialogOpen(true);
  };

  const handleConfirmClone = async () => {
    if (!selectedTemplate || !wizardName.trim()) return;

    try {
      setCloning(true);
      const result = await wizardTemplateService.cloneTemplate({
        template_id: selectedTemplate.id,
        wizard_name: wizardName.trim(),
        wizard_description: wizardDescription.trim() || undefined,
      });

      setCloneDialogOpen(false);
      navigate('/admin/wizard-builder');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to clone template');
    } finally {
      setCloning(false);
    }
  };

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
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

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
          <TemplateIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" fontWeight="bold">
            Template Gallery
          </Typography>
        </Box>

        {/* Filters */}
        <Box sx={{ mb: 4 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Search Templates"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name..."
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryFilter}
                  label="Category"
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Difficulty</InputLabel>
                <Select
                  value={difficultyFilter}
                  label="Difficulty"
                  onChange={(e) => setDifficultyFilter(e.target.value)}
                >
                  <MenuItem value="">All Levels</MenuItem>
                  {difficulties.map((diff) => (
                    <MenuItem key={diff} value={diff}>
                      {diff.charAt(0).toUpperCase() + diff.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>View</InputLabel>
                <Select
                  value={viewMode}
                  label="View"
                  onChange={(e) => setViewMode(e.target.value as any)}
                >
                  <MenuItem value="all">All Templates</MenuItem>
                  <MenuItem value="popular">
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <PopularIcon sx={{ mr: 1, fontSize: 20 }} />
                      Popular
                    </Box>
                  </MenuItem>
                  <MenuItem value="top-rated">
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <TopRatedIcon sx={{ mr: 1, fontSize: 20 }} />
                      Top Rated
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
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

        {/* Templates Grid */}
        {!loading && templates.length > 0 && (
          <Grid container spacing={3}>
            {templates.map((template) => (
              <Grid item xs={12} sm={6} md={4} key={template.id}>
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
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" component="h2" gutterBottom>
                        {template.template_name}
                      </Typography>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleViewTemplate(template)}
                        >
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {template.template_description || 'No description available'}
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                      {template.category && (
                        <Chip label={template.category} size="small" variant="outlined" />
                      )}
                      {template.difficulty_level && (
                        <Chip
                          label={template.difficulty_level}
                          size="small"
                          color={getDifficultyColor(template.difficulty_level) as any}
                        />
                      )}
                      {template.is_system_template && (
                        <Chip label="System" size="small" color="primary" />
                      )}
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Rating value={template.average_rating} readOnly precision={0.5} size="small" />
                        <Typography variant="caption" color="text.secondary">
                          ({template.usage_count} uses)
                        </Typography>
                      </Box>
                      {template.estimated_time && (
                        <Typography variant="caption" color="text.secondary">
                          ~{template.estimated_time} min
                        </Typography>
                      )}
                    </Box>

                    {template.tags && template.tags.length > 0 && (
                      <Box sx={{ mt: 2, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {template.tags.slice(0, 3).map((tag, idx) => (
                          <Chip key={idx} label={tag} size="small" variant="filled" />
                        ))}
                        {template.tags.length > 3 && (
                          <Chip label={`+${template.tags.length - 3}`} size="small" />
                        )}
                      </Box>
                    )}
                  </CardContent>

                  <CardActions>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<CloneIcon />}
                      onClick={() => handleCloneTemplate(template)}
                    >
                      Clone to Builder
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Empty State */}
        {!loading && templates.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <TemplateIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No templates found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try adjusting your filters or search query
            </Typography>
          </Box>
        )}

        {/* Clone Dialog */}
        <Dialog open={cloneDialogOpen} onClose={() => !cloning && setCloneDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Clone Template to Wizard Builder</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                label="Wizard Name"
                value={wizardName}
                onChange={(e) => setWizardName(e.target.value)}
                required
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Description (Optional)"
                value={wizardDescription}
                onChange={(e) => setWizardDescription(e.target.value)}
                multiline
                rows={3}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCloneDialogOpen(false)} disabled={cloning}>
              Cancel
            </Button>
            <Button
              onClick={handleConfirmClone}
              variant="contained"
              disabled={!wizardName.trim() || cloning}
              startIcon={cloning ? <CircularProgress size={20} /> : <CloneIcon />}
            >
              {cloning ? 'Cloning...' : 'Clone'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default TemplateGalleryPage;
