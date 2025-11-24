import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  AlertTitle,
  CircularProgress,
  InputAdornment,
  IconButton,
  Divider,
  Collapse,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person,
  Lock,
  Login as LoginIcon,
  ErrorOutline,
  WifiOff,
  LockOutlined,
  ReportProblem,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

// Error type for better categorization
interface LoginError {
  type: 'credentials' | 'network' | 'server' | 'validation' | 'unknown';
  title: string;
  message: string;
  suggestion?: string;
}

// Parse error and return user-friendly message
const parseLoginError = (err: any): LoginError => {
  // Network error (no response from server)
  if (err?.code === 'ERR_NETWORK' || err?.message === 'Network Error') {
    return {
      type: 'network',
      title: 'Connection Failed',
      message: 'Unable to connect to the server. Please check your internet connection.',
      suggestion: 'Make sure the backend server is running and accessible.',
    };
  }

  // Timeout error
  if (err?.code === 'ECONNABORTED' || err?.message?.includes('timeout')) {
    return {
      type: 'network',
      title: 'Request Timeout',
      message: 'The server took too long to respond.',
      suggestion: 'Please try again. If the problem persists, the server may be overloaded.',
    };
  }

  // Get HTTP status code
  const status = err?.response?.status;
  const detail = err?.response?.data?.detail;

  // Handle specific HTTP status codes
  switch (status) {
    case 400:
      return {
        type: 'validation',
        title: 'Invalid Request',
        message: detail || 'The request was invalid. Please check your input.',
        suggestion: 'Make sure all fields are filled correctly.',
      };

    case 401:
      // Check for specific error messages from backend
      if (detail?.toLowerCase()?.includes('inactive') || detail?.toLowerCase()?.includes('disabled')) {
        return {
          type: 'credentials',
          title: 'Account Disabled',
          message: 'Your account has been deactivated.',
          suggestion: 'Please contact an administrator to reactivate your account.',
        };
      }
      return {
        type: 'credentials',
        title: 'Invalid Credentials',
        message: 'The username or password you entered is incorrect.',
        suggestion: 'Please check your credentials and try again. Passwords are case-sensitive.',
      };

    case 403:
      return {
        type: 'credentials',
        title: 'Access Denied',
        message: detail || 'You do not have permission to access this resource.',
        suggestion: 'Please contact an administrator if you believe this is an error.',
      };

    case 404:
      return {
        type: 'server',
        title: 'Service Not Found',
        message: 'The login service is not available.',
        suggestion: 'Please try again later or contact support.',
      };

    case 422:
      return {
        type: 'validation',
        title: 'Validation Error',
        message: detail || 'Please check your input and try again.',
        suggestion: 'Make sure username and password are in the correct format.',
      };

    case 429:
      return {
        type: 'server',
        title: 'Too Many Attempts',
        message: 'You have made too many login attempts.',
        suggestion: 'Please wait a few minutes before trying again.',
      };

    case 500:
      return {
        type: 'server',
        title: 'Server Error',
        message: 'An internal server error occurred.',
        suggestion: 'Please try again later. If the problem persists, contact support.',
      };

    case 502:
    case 503:
    case 504:
      return {
        type: 'server',
        title: 'Service Unavailable',
        message: 'The server is temporarily unavailable.',
        suggestion: 'Please try again in a few moments.',
      };

    default:
      // Check for CORS errors
      if (err?.message?.includes('CORS') || err?.message?.includes('cross-origin')) {
        return {
          type: 'server',
          title: 'Configuration Error',
          message: 'There is a server configuration issue.',
          suggestion: 'Please contact the administrator.',
        };
      }

      // Generic error with detail from server
      if (detail) {
        return {
          type: 'unknown',
          title: 'Login Failed',
          message: typeof detail === 'string' ? detail : 'An error occurred during login.',
          suggestion: 'Please try again or contact support if the problem persists.',
        };
      }

      // Completely unknown error
      return {
        type: 'unknown',
        title: 'Login Failed',
        message: err?.message || 'An unexpected error occurred.',
        suggestion: 'Please try again. If the problem persists, contact support.',
      };
  }
};

// Get icon based on error type
const getErrorIcon = (type: LoginError['type']) => {
  switch (type) {
    case 'credentials':
      return <LockOutlined />;
    case 'network':
      return <WifiOff />;
    case 'server':
      return <ReportProblem />;
    case 'validation':
      return <ErrorOutline />;
    default:
      return <ErrorOutline />;
  }
};

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<LoginError | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();

  // Client-side validation
  const validateForm = (): LoginError | null => {
    if (!username.trim()) {
      return {
        type: 'validation',
        title: 'Username Required',
        message: 'Please enter your username or email address.',
      };
    }

    if (username.trim().length < 3) {
      return {
        type: 'validation',
        title: 'Invalid Username',
        message: 'Username must be at least 3 characters long.',
      };
    }

    if (!password) {
      return {
        type: 'validation',
        title: 'Password Required',
        message: 'Please enter your password.',
      };
    }

    if (password.length < 6) {
      return {
        type: 'validation',
        title: 'Invalid Password',
        message: 'Password must be at least 6 characters long.',
      };
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Client-side validation first
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      await login({ username: username.trim(), password });
    } catch (err: any) {
      console.error('Login error:', err);
      const parsedError = parseLoginError(err);
      setError(parsedError);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ width: '100%', maxWidth: 400 }}
    >
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <LoginIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        <Typography variant="h5" sx={{ mb: 1 }}>
          Welcome Back
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Sign in to continue to Multi-Wizard Platform
        </Typography>
      </Box>

      {/* Enhanced Error Display */}
      <Collapse in={!!error}>
        {error && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            icon={getErrorIcon(error.type)}
            onClose={() => setError(null)}
          >
            <AlertTitle sx={{ fontWeight: 600 }}>{error.title}</AlertTitle>
            <Typography variant="body2" sx={{ mb: error.suggestion ? 1 : 0 }}>
              {error.message}
            </Typography>
            {error.suggestion && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                {error.suggestion}
              </Typography>
            )}
          </Alert>
        )}
      </Collapse>

      <TextField
        margin="normal"
        required
        fullWidth
        id="username"
        label="Username or Email"
        name="username"
        autoComplete="username"
        autoFocus
        value={username}
        onChange={(e) => {
          setUsername(e.target.value);
          if (error?.type === 'validation') setError(null);
        }}
        disabled={loading}
        error={error?.type === 'validation' && error.title.includes('Username')}
        sx={{
          '& .MuiOutlinedInput-root': {
            background: 'rgba(15, 23, 42, 0.5)',
            '& fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.15)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.25)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#00D9FF',
            },
          },
          '& .MuiInputLabel-root': {
            color: 'rgba(156, 163, 175, 0.8)',
            '&.Mui-focused': {
              color: '#00D9FF',
            },
          },
          '& .MuiOutlinedInput-input': {
            color: '#F9FAFB',
          },
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Person sx={{ color: 'rgba(156, 163, 175, 0.7)' }} />
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
        autoComplete="current-password"
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          if (error?.type === 'validation') setError(null);
        }}
        disabled={loading}
        error={error?.type === 'validation' && error.title.includes('Password')}
        sx={{
          '& .MuiOutlinedInput-root': {
            background: 'rgba(15, 23, 42, 0.5)',
            '& fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.15)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.25)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#00D9FF',
            },
          },
          '& .MuiInputLabel-root': {
            color: 'rgba(156, 163, 175, 0.8)',
            '&.Mui-focused': {
              color: '#00D9FF',
            },
          },
          '& .MuiOutlinedInput-input': {
            color: '#F9FAFB',
          },
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Lock sx={{ color: 'rgba(156, 163, 175, 0.7)' }} />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => setShowPassword(!showPassword)}
                edge="end"
                disabled={loading}
                sx={{ color: 'rgba(156, 163, 175, 0.7)' }}
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      <Box sx={{ textAlign: 'right', mt: 1 }}>
        <Link component={RouterLink} to="/forgot-password" variant="body2" underline="hover">
          Forgot Password?
        </Link>
      </Box>

      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 2, mb: 2, py: 1.5 }}
        disabled={loading}
      >
        {loading ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={24} color="inherit" />
            <span>Signing In...</span>
          </Box>
        ) : (
          'Sign In'
        )}
      </Button>

      <Divider sx={{ my: 2 }}>
        <Typography variant="body2" color="text.secondary">
          OR
        </Typography>
      </Divider>

      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="body2">
          Don't have an account?{' '}
          <Link component={RouterLink} to="/register" underline="hover">
            Sign Up
          </Link>
        </Typography>
      </Box>

      <Box
        sx={{
          mt: 3,
          p: 2.5,
          borderRadius: 2,
          background: 'linear-gradient(135deg, rgba(0, 217, 255, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%)',
          border: '1px solid rgba(0, 217, 255, 0.2)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Decorative glow */}
        <Box
          sx={{
            position: 'absolute',
            top: -20,
            right: -20,
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(0, 217, 255, 0.15) 0%, transparent 70%)',
            pointerEvents: 'none',
          }}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
          <InfoIcon sx={{ fontSize: 18, color: '#00D9FF' }} />
          <Typography
            variant="caption"
            sx={{
              color: '#00D9FF',
              fontWeight: 600,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
            }}
          >
            Demo Credentials
          </Typography>
        </Box>
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            gap: { xs: 1, sm: 3 },
          }}
        >
          <Box>
            <Typography variant="caption" sx={{ color: 'rgba(156, 163, 175, 0.8)' }}>
              Username
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: '#F9FAFB',
                fontWeight: 600,
                fontFamily: 'monospace',
                background: 'rgba(0, 0, 0, 0.2)',
                px: 1.5,
                py: 0.5,
                borderRadius: 1,
                mt: 0.5,
              }}
            >
              admin
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: 'rgba(156, 163, 175, 0.8)' }}>
              Password
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: '#F9FAFB',
                fontWeight: 600,
                fontFamily: 'monospace',
                background: 'rgba(0, 0, 0, 0.2)',
                px: 1.5,
                py: 0.5,
                borderRadius: 1,
                mt: 0.5,
              }}
            >
              Admin123!
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default LoginPage;
