import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { DependencyType, OptionDependency } from '../types';

interface AvailableOption {
  id: string;
  label: string;
  value: string;
  stepName: string;
  optionSetName: string;
}

interface OptionDependencyManagerProps {
  currentOptionId?: string;
  dependencies: Array<{
    depends_on_option_id: string;
    dependency_type: DependencyType;
  }>;
  availableOptions: AvailableOption[];
  onChange: (dependencies: Array<{
    depends_on_option_id: string;
    dependency_type: DependencyType;
  }>) => void;
}

const OptionDependencyManager: React.FC<OptionDependencyManagerProps> = ({
  currentOptionId,
  dependencies,
  availableOptions,
  onChange,
}) => {
  const [newDependency, setNewDependency] = useState<{
    depends_on_option_id: string;
    dependency_type: DependencyType;
  }>({
    depends_on_option_id: '',
    dependency_type: 'show_if',
  });

  const handleAddDependency = () => {
    if (!newDependency.depends_on_option_id) {
      return;
    }

    // Check if dependency already exists
    const exists = dependencies.some(
      (dep) => dep.depends_on_option_id === newDependency.depends_on_option_id
    );

    if (exists) {
      alert('A dependency on this option already exists');
      return;
    }

    onChange([...dependencies, newDependency]);
    setNewDependency({
      depends_on_option_id: '',
      dependency_type: 'show_if',
    });
  };

  const handleRemoveDependency = (index: number) => {
    const newDependencies = dependencies.filter((_, i) => i !== index);
    onChange(newDependencies);
  };

  const getOptionLabel = (optionId: string) => {
    const option = availableOptions.find((opt) => opt.id === optionId);
    if (!option) return 'Unknown Option';
    return `${option.stepName} > ${option.optionSetName} > ${option.label}`;
  };

  const getDependencyTypeLabel = (type: DependencyType) => {
    switch (type) {
      case 'show_if':
        return 'Show If Selected';
      case 'hide_if':
        return 'Hide If Selected';
      case 'require_if':
        return 'Require If Selected';
      case 'disable_if':
        return 'Disable If Selected';
      default:
        return type;
    }
  };

  const getDependencyTypeColor = (type: DependencyType) => {
    switch (type) {
      case 'show_if':
        return 'success';
      case 'hide_if':
        return 'error';
      case 'require_if':
        return 'warning';
      case 'disable_if':
        return 'default';
      default:
        return 'default';
    }
  };

  // Filter out the current option from available options
  const filteredOptions = currentOptionId
    ? availableOptions.filter((opt) => opt.id !== currentOptionId)
    : availableOptions;

  return (
    <Box>
      <Typography variant="body2" fontWeight="bold" gutterBottom>
        Conditional Dependencies
      </Typography>
      <Typography variant="caption" color="text.secondary" paragraph>
        Control when this option is visible, required, or disabled based on other selections
      </Typography>

      {/* Existing Dependencies */}
      {dependencies.length > 0 ? (
        <Box sx={{ mb: 2 }}>
          {dependencies.map((dep, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 1,
                p: 1,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
              }}
            >
              <Box sx={{ flexGrow: 1 }}>
                <Chip
                  label={getDependencyTypeLabel(dep.dependency_type)}
                  color={getDependencyTypeColor(dep.dependency_type) as any}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Typography variant="caption" component="span">
                  {getOptionLabel(dep.depends_on_option_id)}
                </Typography>
              </Box>
              <IconButton
                size="small"
                color="error"
                onClick={() => handleRemoveDependency(index)}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          ))}
        </Box>
      ) : (
        <Alert severity="info" sx={{ mb: 2 }}>
          No dependencies configured. This option will always be visible.
        </Alert>
      )}

      {/* Add New Dependency */}
      {filteredOptions.length > 0 ? (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Dependency Type</InputLabel>
            <Select
              value={newDependency.dependency_type}
              label="Dependency Type"
              onChange={(e) =>
                setNewDependency({
                  ...newDependency,
                  dependency_type: e.target.value as DependencyType,
                })
              }
            >
              <MenuItem value="show_if">Show If Selected</MenuItem>
              <MenuItem value="hide_if">Hide If Selected</MenuItem>
              <MenuItem value="require_if">Require If Selected</MenuItem>
              <MenuItem value="disable_if">Disable If Selected</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ flexGrow: 1 }}>
            <InputLabel>Depends On</InputLabel>
            <Select
              value={newDependency.depends_on_option_id}
              label="Depends On"
              onChange={(e) =>
                setNewDependency({
                  ...newDependency,
                  depends_on_option_id: e.target.value,
                })
              }
            >
              {filteredOptions.map((opt) => (
                <MenuItem key={opt.id} value={opt.id}>
                  {opt.stepName} &gt; {opt.optionSetName} &gt; {opt.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            size="small"
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={handleAddDependency}
            disabled={!newDependency.depends_on_option_id}
          >
            Add
          </Button>
        </Box>
      ) : (
        <Alert severity="warning">
          No other options available. Create more options in other steps first.
        </Alert>
      )}
    </Box>
  );
};

export default OptionDependencyManager;
