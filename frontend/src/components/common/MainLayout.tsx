import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  alpha,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Logout as LogoutIcon,
  Build as BuildIcon,
  Analytics as AnalyticsIcon,
  People as PeopleIcon,
  PlayArrow as WizardActionsIcon,
  LibraryBooks as TemplateIcon,
  DirectionsRun as RunIcon,
  Storage as StoreIcon,
  AccountCircle,
  Lock as LockIcon,
  Security as SecurityIcon,
  AutoAwesome as LogoIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';

const drawerWidth = 260;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Template Gallery', icon: <TemplateIcon />, path: '/templates' },
  { text: 'Wizard Builder', icon: <BuildIcon />, path: '/admin/wizard-builder' },
  { text: 'Run Wizard', icon: <WizardActionsIcon />, path: '/wizards' },
  { text: 'My Runs', icon: <RunIcon />, path: '/runs' },
  { text: 'Store', icon: <StoreIcon />, path: '/store' },
  { text: 'Analytics', icon: <AnalyticsIcon />, path: '/admin/analytics' },
  { text: 'Users', icon: <PeopleIcon />, path: '/admin/users' },
];

const MainLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/login');
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo Section */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Box
          sx={{
            width: 42,
            height: 42,
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #00D9FF 0%, #A855F7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(0, 217, 255, 0.3)',
          }}
        >
          <LogoIcon sx={{ color: '#0A0F1C', fontSize: 24 }} />
        </Box>
        <Box>
          <Typography
            variant="h6"
            noWrap
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
            variant="caption"
            sx={{
              color: 'text.secondary',
              fontSize: '0.7rem',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
            }}
          >
            Platform
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ mx: 2, mb: 2 }} />

      {/* Navigation Menu */}
      <List sx={{ px: 1, flex: 1 }}>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={isSelected}
                onClick={() => {
                  navigate(item.path);
                  setMobileOpen(false);
                }}
                sx={{
                  py: 1.5,
                  px: 2,
                  '& .MuiListItemIcon-root': {
                    color: isSelected ? 'primary.main' : 'text.secondary',
                  },
                  '& .MuiListItemText-primary': {
                    color: isSelected ? 'primary.main' : 'text.primary',
                  },
                }}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
                {isSelected && (
                  <Box
                    sx={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #00D9FF 0%, #A855F7 100%)',
                      boxShadow: '0 0 8px rgba(0, 217, 255, 0.6)',
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* User Section at Bottom */}
      <Box sx={{ p: 2, mt: 'auto' }}>
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            background: (theme) => alpha(theme.palette.primary.main, 0.08),
            border: (theme) => `1px solid ${alpha(theme.palette.primary.main, 0.15)}`,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Avatar sx={{ width: 36, height: 36, fontSize: '0.9rem' }}>
              {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 600,
                  color: 'text.primary',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {user?.full_name || user?.username}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: 'primary.main',
                  textTransform: 'capitalize',
                }}
              >
                {user?.role?.name || 'User'}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography
              variant="h6"
              noWrap
              sx={{
                fontWeight: 600,
                color: 'text.primary',
              }}
            >
              {menuItems.find((item) => item.path === location.pathname)?.text || 'Dashboard'}
            </Typography>
          </Box>

          {/* Right Side Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              onClick={handleMenuOpen}
              sx={{
                p: 0.5,
                border: (theme) => `2px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                '&:hover': {
                  border: (theme) => `2px solid ${theme.palette.primary.main}`,
                },
              }}
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
              </Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
              PaperProps={{
                sx: {
                  mt: 1,
                  minWidth: 200,
                },
              }}
            >
              <Box sx={{ px: 2, py: 1.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                  {user?.full_name || user?.username}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  {user?.email}
                </Typography>
              </Box>
              <Divider sx={{ my: 1 }} />
              <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
                <AccountCircle sx={{ mr: 1.5, color: 'primary.main' }} />
                My Profile
              </MenuItem>
              <MenuItem onClick={() => { handleMenuClose(); navigate('/change-password'); }}>
                <LockIcon sx={{ mr: 1.5, color: 'primary.main' }} />
                Change Password
              </MenuItem>
              <MenuItem onClick={() => { handleMenuClose(); navigate('/roles'); }}>
                <SecurityIcon sx={{ mr: 1.5, color: 'primary.main' }} />
                Roles & Privileges
              </MenuItem>
              <Divider sx={{ my: 1 }} />
              <MenuItem
                onClick={handleLogout}
                sx={{
                  color: 'error.main',
                  '&:hover': {
                    background: (theme) => alpha(theme.palette.error.main, 0.1),
                  },
                }}
              >
                <LogoutIcon sx={{ mr: 1.5 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          pt: { xs: 8, sm: 9 },
          pb: 4,
          px: { xs: 2, sm: 3, md: 4 },
          background: 'transparent',
        }}
      >
        <Outlet />
      </Box>

      {/* Decorative Background Elements */}
      <Box
        sx={{
          position: 'fixed',
          top: '10%',
          right: '5%',
          width: 400,
          height: 400,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(0, 217, 255, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: -1,
        }}
      />
      <Box
        sx={{
          position: 'fixed',
          bottom: '10%',
          left: '10%',
          width: 300,
          height: 300,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: -1,
        }}
      />
    </Box>
  );
};

export default MainLayout;
