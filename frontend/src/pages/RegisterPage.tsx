import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  CheckCircle,
  Cancel,
  Person,
  Email,
  Lock,
  Badge,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [registrationComplete, setRegistrationComplete] = useState(false);
  const { register } = useAuth();

  const steps = ['Enter Details', 'Create Account', 'Welcome!'];

  // Password validation checks
  const passwordChecks = {
    length: formData.password.length >= 8,
    uppercase: /[A-Z]/.test(formData.password),
    lowercase: /[a-z]/.test(formData.password),
    number: /[0-9]/.test(formData.password),
    match: formData.password === formData.confirmPassword && formData.confirmPassword !== '',
  };

  const isPasswordValid = passwordChecks.length && passwordChecks.uppercase &&
    passwordChecks.lowercase && passwordChecks.number;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!passwordChecks.match) {
      setError('Passwords do not match');
      return;
    }

    if (!isPasswordValid) {
      setError('Password does not meet all requirements');
      return;
    }

    setLoading(true);
    setActiveStep(1);

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.full_name || undefined,
      });
      setActiveStep(2);
      setRegistrationComplete(true);
      // Auto redirect after 3 seconds
      setTimeout(() => {
        navigate('/');
      }, 3000);
    } catch (err: unknown) {
      setActiveStep(0);
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (registrationComplete) {
    return (
      <Box sx={{ width: '100%', maxWidth: 500, textAlign: 'center' }}>
        <Stepper activeStep={2} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom color="success.main">
            Registration Successful!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Welcome to Multi-Wizard Platform, <strong>{formData.full_name || formData.username}</strong>!
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Your account has been created successfully. You are now logged in.
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            You will be redirected to the dashboard in a few seconds...
          </Alert>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Account Details:
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><Person fontSize="small" /></ListItemIcon>
              <ListItemText primary="Username" secondary={formData.username} />
            </ListItem>
            <ListItem>
              <ListItemIcon><Email fontSize="small" /></ListItemIcon>
              <ListItemText primary="Email" secondary={formData.email} />
            </ListItem>
            <ListItem>
              <ListItemIcon><Badge fontSize="small" /></ListItemIcon>
              <ListItemText primary="Role" secondary="User (Standard Access)" />
            </ListItem>
          </List>
          <Button
            variant="contained"
            onClick={() => navigate('/')}
            sx={{ mt: 2 }}
          >
            Go to Dashboard Now
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ width: '100%', maxWidth: 450 }}
    >
      <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Typography variant="h5" sx={{ mb: 1, textAlign: 'center' }}>
        Create Account
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
        Fill in your details to get started
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        margin="normal"
        fullWidth
        id="full_name"
        label="Full Name"
        name="full_name"
        autoComplete="name"
        value={formData.full_name}
        onChange={handleChange}
        disabled={loading}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Person color="action" />
            </InputAdornment>
          ),
        }}
      />

      <TextField
        margin="normal"
        required
        fullWidth
        id="email"
        label="Email Address"
        name="email"
        autoComplete="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        disabled={loading}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Email color="action" />
            </InputAdornment>
          ),
        }}
      />

      <TextField
        margin="normal"
        required
        fullWidth
        id="username"
        label="Username"
        name="username"
        autoComplete="username"
        value={formData.username}
        onChange={handleChange}
        disabled={loading}
        helperText="3-100 characters, alphanumeric with underscores/hyphens"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Badge color="action" />
            </InputAdornment>
          ),
        }}
      />

      <TextField
        margin="normal"
        required
        fullWidth
        name="password"
        label="Password"
        type={showPassword ? 'text' : 'password'}
        id="password"
        value={formData.password}
        onChange={handleChange}
        disabled={loading}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Lock color="action" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => setShowPassword(!showPassword)}
                edge="end"
                disabled={loading}
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      {/* Password Requirements */}
      {formData.password && (
        <Box sx={{ mt: 1, mb: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Password Requirements:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 0.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {passwordChecks.length ?
                <CheckCircle fontSize="small" color="success" /> :
                <Cancel fontSize="small" color="error" />}
              <Typography variant="caption" color={passwordChecks.length ? 'success.main' : 'error.main'}>
                8+ chars
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {passwordChecks.uppercase ?
                <CheckCircle fontSize="small" color="success" /> :
                <Cancel fontSize="small" color="error" />}
              <Typography variant="caption" color={passwordChecks.uppercase ? 'success.main' : 'error.main'}>
                Uppercase
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {passwordChecks.lowercase ?
                <CheckCircle fontSize="small" color="success" /> :
                <Cancel fontSize="small" color="error" />}
              <Typography variant="caption" color={passwordChecks.lowercase ? 'success.main' : 'error.main'}>
                Lowercase
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {passwordChecks.number ?
                <CheckCircle fontSize="small" color="success" /> :
                <Cancel fontSize="small" color="error" />}
              <Typography variant="caption" color={passwordChecks.number ? 'success.main' : 'error.main'}>
                Number
              </Typography>
            </Box>
          </Box>
        </Box>
      )}

      <TextField
        margin="normal"
        required
        fullWidth
        name="confirmPassword"
        label="Confirm Password"
        type={showConfirmPassword ? 'text' : 'password'}
        id="confirmPassword"
        value={formData.confirmPassword}
        onChange={handleChange}
        disabled={loading}
        error={formData.confirmPassword !== '' && !passwordChecks.match}
        helperText={formData.confirmPassword !== '' && !passwordChecks.match ? 'Passwords do not match' : ''}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Lock color="action" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                edge="end"
                disabled={loading}
              >
                {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2, py: 1.5 }}
        disabled={loading || !isPasswordValid || !passwordChecks.match}
      >
        {loading ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={24} color="inherit" />
            <span>Creating Account...</span>
          </Box>
        ) : (
          'Sign Up'
        )}
      </Button>

      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="body2">
          Already have an account?{' '}
          <Link component={RouterLink} to="/login" underline="hover">
            Sign In
          </Link>
        </Typography>
      </Box>
    </Box>
  );
};

export default RegisterPage;
