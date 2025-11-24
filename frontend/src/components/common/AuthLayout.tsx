import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Box, Container, Paper, Typography, alpha } from '@mui/material';
import { AutoAwesome as LogoIcon } from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';

const AuthLayout: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #0A0F1C 0%, #0D1321 50%, #111827 100%)',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #00D9FF 0%, #A855F7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 32px rgba(0, 217, 255, 0.4)',
              animation: 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 1 },
                '50%': { transform: 'scale(1.05)', opacity: 0.8 },
              },
            }}
          >
            <LogoIcon sx={{ color: '#0A0F1C', fontSize: 32 }} />
          </Box>
          <Typography sx={{ color: 'text.secondary', fontWeight: 500 }}>
            Loading...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0A0F1C 0%, #0D1321 50%, #111827 100%)',
        py: 4,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Decorative Background Elements */}
      <Box
        sx={{
          position: 'absolute',
          top: '-20%',
          left: '-10%',
          width: 600,
          height: 600,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(0, 217, 255, 0.12) 0%, transparent 70%)',
          pointerEvents: 'none',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '-20%',
          right: '-10%',
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, transparent 70%)',
          pointerEvents: 'none',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 800,
          height: 800,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(0, 217, 255, 0.05) 0%, transparent 50%)',
          pointerEvents: 'none',
        }}
      />

      <Container maxWidth="sm" sx={{ position: 'relative', zIndex: 1 }}>
        <Paper
          elevation={3}
          sx={{
            p: { xs: 3, sm: 5 },
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            background: 'linear-gradient(135deg, rgba(31, 41, 55, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%)',
            backdropFilter: 'blur(20px)',
            border: `1px solid ${alpha('#ffffff', 0.1)}`,
            boxShadow: '0 24px 48px rgba(0, 0, 0, 0.4)',
            borderRadius: 4,
          }}
        >
          {/* Logo */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              mb: 4,
            }}
          >
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #00D9FF 0%, #A855F7 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 8px 24px rgba(0, 217, 255, 0.35)',
              }}
            >
              <LogoIcon sx={{ color: '#0A0F1C', fontSize: 30 }} />
            </Box>
            <Box>
              <Typography
                component="h1"
                variant="h4"
                sx={{
                  fontWeight: 700,
                  background: 'linear-gradient(135deg, #00D9FF 0%, #A855F7 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  letterSpacing: '-0.02em',
                }}
              >
                Wizard
              </Typography>
              <Typography
                sx={{
                  color: 'text.secondary',
                  fontSize: '0.75rem',
                  letterSpacing: '0.15em',
                  textTransform: 'uppercase',
                  mt: -0.5,
                }}
              >
                Platform
              </Typography>
            </Box>
          </Box>

          <Outlet />
        </Paper>

        {/* Footer */}
        <Typography
          variant="body2"
          sx={{
            textAlign: 'center',
            mt: 4,
            color: 'text.secondary',
            fontSize: '0.8rem',
          }}
        >
          Multi-Wizard Platform v1.0
        </Typography>
      </Container>
    </Box>
  );
};

export default AuthLayout;
