import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Container,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  Alert,
} from '@mui/material';
import {
  AdminPanelSettings,
  SupervisorAccount,
  Person,
  CheckCircle,
  Info,
  Security,
  ArrowBack,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

interface RoleDefinition {
  name: string;
  displayName: string;
  description: string;
  color: 'error' | 'warning' | 'primary' | 'success';
  icon: React.ReactNode;
  permissions: string[];
}

const roles: RoleDefinition[] = [
  {
    name: 'super_admin',
    displayName: 'Super Admin',
    description: 'Full system access with complete control over all features and user management.',
    color: 'error',
    icon: <AdminPanelSettings />,
    permissions: [
      'Full access to all system features',
      'User management (create, edit, delete users)',
      'Role assignment and management',
      'System configuration and settings',
      'View and manage all wizards',
      'Access to analytics and reports',
      'Audit log access',
      'Database management operations',
    ],
  },
  {
    name: 'admin',
    displayName: 'Admin',
    description: 'Administrative access for managing wizards, templates, and viewing analytics.',
    color: 'warning',
    icon: <SupervisorAccount />,
    permissions: [
      'Create, edit, and delete wizards',
      'Manage wizard templates',
      'View analytics and reports',
      'Manage own wizard sessions',
      'Access to Wizard Builder',
      'Clone and customize templates',
      'View user activity (limited)',
    ],
  },
  {
    name: 'user',
    displayName: 'User',
    description: 'Standard user access for browsing templates, running wizards, and managing personal runs.',
    color: 'primary',
    icon: <Person />,
    permissions: [
      'Browse template gallery',
      'Clone templates (creates personal wizard)',
      'Run published wizards',
      'View and manage own wizard runs',
      'Save and store completed runs',
      'Share runs via links',
      'Update personal profile',
    ],
  },
];

const RolesPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate(-1)}
          >
            Back
          </Button>
        </Box>

        <Typography variant="h4" gutterBottom>
          User Roles
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Overview of available roles and their permissions in the Multi-Wizard Platform
        </Typography>

        {user && (
          <Alert severity="info" sx={{ mb: 4 }}>
            Your current role: <strong>{user.role.name.replace('_', ' ').toUpperCase()}</strong>
          </Alert>
        )}

        <Grid container spacing={3}>
          {roles.map((role) => (
            <Grid item xs={12} md={4} key={role.name}>
              <Card
                elevation={3}
                sx={{
                  height: '100%',
                  border: user?.role.name === role.name ? 2 : 0,
                  borderColor: `${role.color}.main`,
                }}
              >
                <CardHeader
                  avatar={
                    <Box
                      sx={{
                        bgcolor: `${role.color}.light`,
                        p: 1,
                        borderRadius: 1,
                        color: `${role.color}.main`,
                      }}
                    >
                      {role.icon}
                    </Box>
                  }
                  title={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {role.displayName}
                      {user?.role.name === role.name && (
                        <Chip label="Your Role" size="small" color={role.color} />
                      )}
                    </Box>
                  }
                  subheader={role.description}
                />
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Security fontSize="small" />
                    Permissions
                  </Typography>
                  <List dense>
                    {role.permissions.map((permission, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <CheckCircle fontSize="small" color={role.color} />
                        </ListItemIcon>
                        <ListItemText
                          primary={permission}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Paper elevation={2} sx={{ p: 3, mt: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Info color="info" />
            <Typography variant="h6">Role Information</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" paragraph>
            Roles determine what actions users can perform within the platform. Each role has a specific set of permissions that control access to features and data.
          </Typography>
          <Typography variant="body2" paragraph>
            <strong>Role Assignment:</strong> Roles are assigned by Super Admins during user creation or through user management. Users cannot change their own roles.
          </Typography>
          <Typography variant="body2">
            <strong>Need different permissions?</strong> Contact your system administrator to request a role change.
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/privileges')}
            >
              View Detailed Privileges
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default RolesPage;
