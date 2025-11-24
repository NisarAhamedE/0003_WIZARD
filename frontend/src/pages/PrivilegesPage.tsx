import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  ExpandMore,
  CheckCircle,
  Cancel,
  ArrowBack,
  Info,
  Security,
  Description,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

interface ModulePrivilege {
  module: string;
  description: string;
  actions: {
    name: string;
    description: string;
    superAdmin: boolean;
    admin: boolean;
    user: boolean;
  }[];
}

const modulePrivileges: ModulePrivilege[] = [
  {
    module: 'Dashboard',
    description: 'Main dashboard and statistics overview',
    actions: [
      { name: 'View Dashboard', description: 'Access the main dashboard', superAdmin: true, admin: true, user: true },
      { name: 'View Statistics', description: 'See personal run statistics', superAdmin: true, admin: true, user: true },
      { name: 'View System Stats', description: 'See system-wide statistics', superAdmin: true, admin: true, user: false },
    ],
  },
  {
    module: 'Template Gallery',
    description: 'Browse and clone wizard templates',
    actions: [
      { name: 'Browse Templates', description: 'View available templates', superAdmin: true, admin: true, user: true },
      { name: 'Clone Templates', description: 'Create wizard from template', superAdmin: true, admin: true, user: true },
      { name: 'Create Templates', description: 'Create new templates', superAdmin: true, admin: true, user: false },
      { name: 'Edit Templates', description: 'Modify existing templates', superAdmin: true, admin: true, user: false },
      { name: 'Delete Templates', description: 'Remove templates', superAdmin: true, admin: false, user: false },
    ],
  },
  {
    module: 'Wizard Builder',
    description: 'Create and configure wizards',
    actions: [
      { name: 'Access Builder', description: 'Open Wizard Builder', superAdmin: true, admin: true, user: false },
      { name: 'Create Wizards', description: 'Create new wizards', superAdmin: true, admin: true, user: false },
      { name: 'Edit Wizards', description: 'Modify wizard configuration', superAdmin: true, admin: true, user: false },
      { name: 'Delete Wizards', description: 'Remove wizards', superAdmin: true, admin: true, user: false },
      { name: 'Publish Wizards', description: 'Make wizards available', superAdmin: true, admin: true, user: false },
    ],
  },
  {
    module: 'Run Wizard',
    description: 'Execute published wizards',
    actions: [
      { name: 'Browse Wizards', description: 'View available wizards', superAdmin: true, admin: true, user: true },
      { name: 'Start Wizard Run', description: 'Begin a wizard execution', superAdmin: true, admin: true, user: true },
      { name: 'Save Progress', description: 'Save partial progress', superAdmin: true, admin: true, user: true },
      { name: 'Complete Run', description: 'Finish and save run', superAdmin: true, admin: true, user: true },
    ],
  },
  {
    module: 'My Runs',
    description: 'Manage personal wizard runs',
    actions: [
      { name: 'View Runs', description: 'See own wizard runs', superAdmin: true, admin: true, user: true },
      { name: 'Resume Runs', description: 'Continue incomplete runs', superAdmin: true, admin: true, user: true },
      { name: 'Delete Runs', description: 'Remove own runs', superAdmin: true, admin: true, user: true },
      { name: 'Favorite Runs', description: 'Mark runs as favorites', superAdmin: true, admin: true, user: true },
    ],
  },
  {
    module: 'Store',
    description: 'Stored runs and sharing',
    actions: [
      { name: 'View Stored Runs', description: 'Access stored runs', superAdmin: true, admin: true, user: true },
      { name: 'Share Runs', description: 'Create share links', superAdmin: true, admin: true, user: true },
      { name: 'Compare Runs', description: 'Compare multiple runs', superAdmin: true, admin: true, user: true },
      { name: 'Export Runs', description: 'Export run data', superAdmin: true, admin: true, user: true },
    ],
  },
  {
    module: 'Analytics',
    description: 'Reports and analytics',
    actions: [
      { name: 'View Analytics', description: 'Access analytics dashboard', superAdmin: true, admin: true, user: false },
      { name: 'View Reports', description: 'See detailed reports', superAdmin: true, admin: true, user: false },
      { name: 'Export Reports', description: 'Download report data', superAdmin: true, admin: false, user: false },
    ],
  },
  {
    module: 'User Management',
    description: 'Manage system users',
    actions: [
      { name: 'View Users', description: 'See user list', superAdmin: true, admin: false, user: false },
      { name: 'Create Users', description: 'Add new users', superAdmin: true, admin: false, user: false },
      { name: 'Edit Users', description: 'Modify user details', superAdmin: true, admin: false, user: false },
      { name: 'Delete Users', description: 'Remove users', superAdmin: true, admin: false, user: false },
      { name: 'Assign Roles', description: 'Change user roles', superAdmin: true, admin: false, user: false },
    ],
  },
];

const PrivilegesPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const PermissionCell = ({ allowed }: { allowed: boolean }) => (
    allowed ? (
      <CheckCircle color="success" fontSize="small" />
    ) : (
      <Cancel color="error" fontSize="small" />
    )
  );

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
          Privileges & Permissions
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Detailed breakdown of module access and actions by role
        </Typography>

        {user && (
          <Alert severity="info" sx={{ mb: 4 }} icon={<Security />}>
            Your current role: <strong>{user.role.name.replace('_', ' ').toUpperCase()}</strong> -
            Look for <CheckCircle color="success" fontSize="small" sx={{ verticalAlign: 'middle', mx: 0.5 }} />
            in your role column to see what you can access.
          </Alert>
        )}

        <Alert severity="warning" sx={{ mb: 4 }} icon={<Info />}>
          <strong>Note:</strong> Privileges are currently for documentation purposes.
          Actual permission enforcement will be implemented in a future update.
        </Alert>

        {/* Summary Table */}
        <Paper elevation={3} sx={{ mb: 4 }}>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.100' }}>
                  <TableCell><strong>Module / Action</strong></TableCell>
                  <TableCell align="center">
                    <Chip label="Super Admin" color="error" size="small" />
                  </TableCell>
                  <TableCell align="center">
                    <Chip label="Admin" color="warning" size="small" />
                  </TableCell>
                  <TableCell align="center">
                    <Chip label="User" color="primary" size="small" />
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {modulePrivileges.map((module) => (
                  <React.Fragment key={module.module}>
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell colSpan={4}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {module.module}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {module.description}
                        </Typography>
                      </TableCell>
                    </TableRow>
                    {module.actions.map((action) => (
                      <TableRow key={`${module.module}-${action.name}`} hover>
                        <TableCell sx={{ pl: 4 }}>
                          <Typography variant="body2">{action.name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {action.description}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <PermissionCell allowed={action.superAdmin} />
                        </TableCell>
                        <TableCell align="center">
                          <PermissionCell allowed={action.admin} />
                        </TableCell>
                        <TableCell align="center">
                          <PermissionCell allowed={action.user} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </React.Fragment>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Detailed Accordion View */}
        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Detailed Module Descriptions
        </Typography>
        {modulePrivileges.map((module) => (
          <Accordion key={module.module}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Description color="primary" />
                <Box>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {module.module}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {module.description}
                  </Typography>
                </Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <List dense>
                {module.actions.map((action) => (
                  <ListItem key={action.name}>
                    <ListItemIcon>
                      <CheckCircle color="action" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={action.name}
                      secondary={
                        <Box component="span">
                          {action.description}
                          <Box sx={{ mt: 0.5 }}>
                            {action.superAdmin && <Chip label="Super Admin" size="small" color="error" sx={{ mr: 0.5 }} />}
                            {action.admin && <Chip label="Admin" size="small" color="warning" sx={{ mr: 0.5 }} />}
                            {action.user && <Chip label="User" size="small" color="primary" />}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}

        <Paper elevation={2} sx={{ p: 3, mt: 4, bgcolor: 'info.50' }}>
          <Typography variant="h6" gutterBottom>
            How Privileges Work
          </Typography>
          <Typography variant="body2" paragraph>
            <strong>1. Role-Based Access Control (RBAC):</strong> Each user is assigned a role that determines their permissions across the platform.
          </Typography>
          <Typography variant="body2" paragraph>
            <strong>2. Inheritance:</strong> Higher-level roles typically inherit all permissions from lower-level roles, plus additional privileges.
          </Typography>
          <Typography variant="body2" paragraph>
            <strong>3. Module-Level Control:</strong> Permissions are organized by modules (Dashboard, Templates, Wizards, etc.) for easier management.
          </Typography>
          <Typography variant="body2">
            <strong>4. Future Enhancement:</strong> Granular action-level permissions will be enforced at both frontend (UI) and backend (API) levels in upcoming releases.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default PrivilegesPage;
