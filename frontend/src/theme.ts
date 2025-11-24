import { createTheme, alpha } from '@mui/material/styles';

// Nexus-inspired dark theme colors
const colors = {
  // Primary cyan/teal accent
  primary: {
    main: '#00D9FF',
    light: '#5CE1FF',
    dark: '#00A8CC',
    contrastText: '#0A0F1C',
  },
  // Secondary purple accent
  secondary: {
    main: '#A855F7',
    light: '#C084FC',
    dark: '#7C3AED',
    contrastText: '#ffffff',
  },
  // Background colors - dark blue/black gradient
  background: {
    default: '#0A0F1C',
    paper: '#111827',
    card: '#1F2937',
    elevated: '#252F3F',
  },
  // Text colors
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
    disabled: '#6B7280',
  },
  // Status colors
  success: {
    main: '#10B981',
    light: '#34D399',
    dark: '#059669',
  },
  error: {
    main: '#EF4444',
    light: '#F87171',
    dark: '#DC2626',
  },
  warning: {
    main: '#F59E0B',
    light: '#FBBF24',
    dark: '#D97706',
  },
  info: {
    main: '#3B82F6',
    light: '#60A5FA',
    dark: '#2563EB',
  },
  // Divider
  divider: 'rgba(255, 255, 255, 0.08)',
};

// Glassmorphism effect styles
export const glassEffect = {
  background: 'rgba(17, 24, 39, 0.7)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
};

export const glassCardEffect = {
  background: 'linear-gradient(135deg, rgba(31, 41, 55, 0.9) 0%, rgba(17, 24, 39, 0.9) 100%)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
};

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: colors.primary,
    secondary: colors.secondary,
    success: colors.success,
    error: colors.error,
    warning: colors.warning,
    info: colors.info,
    background: {
      default: colors.background.default,
      paper: colors.background.paper,
    },
    text: colors.text,
    divider: colors.divider,
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
      color: colors.text.primary,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,
      letterSpacing: '-0.01em',
      color: colors.text.primary,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
      color: colors.text.primary,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: colors.text.primary,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      color: colors.text.primary,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      color: colors.text.primary,
    },
    body1: {
      color: colors.text.secondary,
    },
    body2: {
      color: colors.text.secondary,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: `linear-gradient(135deg, ${colors.background.default} 0%, #0D1321 50%, #111827 100%)`,
          minHeight: '100vh',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 10,
          fontWeight: 600,
          padding: '10px 24px',
          transition: 'all 0.2s ease-in-out',
        },
        contained: {
          background: `linear-gradient(135deg, ${colors.primary.main} 0%, ${colors.primary.dark} 100%)`,
          boxShadow: `0 4px 14px ${alpha(colors.primary.main, 0.4)}`,
          '&:hover': {
            background: `linear-gradient(135deg, ${colors.primary.light} 0%, ${colors.primary.main} 100%)`,
            boxShadow: `0 6px 20px ${alpha(colors.primary.main, 0.5)}`,
            transform: 'translateY(-1px)',
          },
        },
        containedSecondary: {
          background: `linear-gradient(135deg, ${colors.secondary.main} 0%, ${colors.secondary.dark} 100%)`,
          boxShadow: `0 4px 14px ${alpha(colors.secondary.main, 0.4)}`,
          '&:hover': {
            background: `linear-gradient(135deg, ${colors.secondary.light} 0%, ${colors.secondary.main} 100%)`,
            boxShadow: `0 6px 20px ${alpha(colors.secondary.main, 0.5)}`,
          },
        },
        outlined: {
          borderColor: alpha(colors.primary.main, 0.5),
          color: colors.primary.main,
          '&:hover': {
            borderColor: colors.primary.main,
            background: alpha(colors.primary.main, 0.1),
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          background: colors.background.card,
          border: `1px solid ${alpha('#ffffff', 0.08)}`,
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.25)',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            borderColor: alpha(colors.primary.main, 0.3),
            boxShadow: `0 8px 32px rgba(0, 0, 0, 0.35), 0 0 0 1px ${alpha(colors.primary.main, 0.1)}`,
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          backgroundImage: 'none',
        },
        elevation1: {
          background: colors.background.card,
          border: `1px solid ${alpha('#ffffff', 0.08)}`,
        },
        elevation2: {
          background: colors.background.card,
          border: `1px solid ${alpha('#ffffff', 0.1)}`,
        },
        elevation3: {
          background: colors.background.elevated,
          border: `1px solid ${alpha('#ffffff', 0.1)}`,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'rgba(10, 15, 28, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: `1px solid ${alpha('#ffffff', 0.08)}`,
          boxShadow: 'none',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: colors.background.paper,
          borderRight: `1px solid ${alpha('#ffffff', 0.08)}`,
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          margin: '4px 8px',
          transition: 'all 0.2s ease',
          '&.Mui-selected': {
            background: `linear-gradient(135deg, ${alpha(colors.primary.main, 0.2)} 0%, ${alpha(colors.primary.main, 0.1)} 100%)`,
            borderLeft: `3px solid ${colors.primary.main}`,
            '&:hover': {
              background: `linear-gradient(135deg, ${alpha(colors.primary.main, 0.25)} 0%, ${alpha(colors.primary.main, 0.15)} 100%)`,
            },
          },
          '&:hover': {
            background: alpha('#ffffff', 0.05),
          },
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: colors.text.secondary,
          minWidth: 40,
          '.Mui-selected &': {
            color: colors.primary.main,
          },
        },
      },
    },
    MuiListItemText: {
      styleOverrides: {
        primary: {
          fontWeight: 500,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            background: alpha(colors.background.card, 0.5),
            transition: 'all 0.2s ease',
            '& fieldset': {
              borderColor: alpha('#ffffff', 0.1),
              transition: 'all 0.2s ease',
            },
            '&:hover fieldset': {
              borderColor: alpha(colors.primary.main, 0.5),
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.primary.main,
              boxShadow: `0 0 0 3px ${alpha(colors.primary.main, 0.15)}`,
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
        filled: {
          background: alpha(colors.primary.main, 0.15),
          color: colors.primary.main,
          border: `1px solid ${alpha(colors.primary.main, 0.3)}`,
        },
        outlined: {
          borderColor: alpha('#ffffff', 0.2),
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          background: `linear-gradient(135deg, ${colors.primary.main} 0%, ${colors.secondary.main} 100%)`,
          color: colors.background.default,
          fontWeight: 600,
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          background: colors.background.elevated,
          border: `1px solid ${alpha('#ffffff', 0.1)}`,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 8px',
          transition: 'all 0.2s ease',
          '&:hover': {
            background: alpha(colors.primary.main, 0.1),
          },
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: alpha('#ffffff', 0.08),
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
        standardSuccess: {
          background: alpha(colors.success.main, 0.15),
          border: `1px solid ${alpha(colors.success.main, 0.3)}`,
          color: colors.success.light,
        },
        standardError: {
          background: alpha(colors.error.main, 0.15),
          border: `1px solid ${alpha(colors.error.main, 0.3)}`,
          color: colors.error.light,
        },
        standardWarning: {
          background: alpha(colors.warning.main, 0.15),
          border: `1px solid ${alpha(colors.warning.main, 0.3)}`,
          color: colors.warning.light,
        },
        standardInfo: {
          background: alpha(colors.info.main, 0.15),
          border: `1px solid ${alpha(colors.info.main, 0.3)}`,
          color: colors.info.light,
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          minHeight: 44,
        },
        indicator: {
          background: `linear-gradient(90deg, ${colors.primary.main} 0%, ${colors.secondary.main} 100%)`,
          height: 3,
          borderRadius: '3px 3px 0 0',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          minHeight: 44,
          transition: 'all 0.2s ease',
          '&.Mui-selected': {
            color: colors.primary.main,
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 8,
          background: alpha('#ffffff', 0.1),
        },
        bar: {
          borderRadius: 4,
          background: `linear-gradient(90deg, ${colors.primary.main} 0%, ${colors.secondary.main} 100%)`,
        },
      },
    },
    MuiCircularProgress: {
      styleOverrides: {
        root: {
          color: colors.primary.main,
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          background: colors.background.elevated,
          border: `1px solid ${alpha('#ffffff', 0.1)}`,
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)',
          fontSize: '0.875rem',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          background: colors.background.card,
          border: `1px solid ${alpha('#ffffff', 0.1)}`,
          boxShadow: '0 24px 48px rgba(0, 0, 0, 0.4)',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: alpha('#ffffff', 0.08),
        },
        head: {
          fontWeight: 600,
          color: colors.text.primary,
          background: alpha(colors.background.card, 0.5),
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          transition: 'background 0.2s ease',
          '&:hover': {
            background: alpha(colors.primary.main, 0.05),
          },
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        root: {
          '& .MuiSwitch-switchBase.Mui-checked': {
            color: colors.primary.main,
            '& + .MuiSwitch-track': {
              backgroundColor: colors.primary.main,
            },
          },
        },
      },
    },
    MuiSkeleton: {
      styleOverrides: {
        root: {
          background: alpha('#ffffff', 0.1),
        },
      },
    },
  },
});

export default theme;
