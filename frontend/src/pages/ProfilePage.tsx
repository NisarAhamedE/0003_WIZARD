import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Container,
  Grid,
  Avatar,
  Chip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  CardHeader,
} from '@mui/material';
import {
  Person,
  Email,
  Badge,
  CalendarToday,
  AccessTime,
  Security,
  Edit,
  Lock,
  VerifiedUser,
  AdminPanelSettings,
  SupervisorAccount,
  CheckCircle,
  Cancel,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  if (!user) {
    return (
      <Container maxWidth="md">
        <Paper sx={{ p: 4, mt: 4, textAlign: 'center' }}>
          <Typography>Loading profile...</Typography>
        </Paper>
      </Container>
    );
  }

  const getRoleIcon = (roleName: string) => {
    switch (roleName) {
      case 'super_admin':
        return <AdminPanelSettings />;
      case 'admin':
        return <SupervisorAccount />;
      default:
        return <Person />;
    }
  };

  const getRoleColor = (roleName: string): 'error' | 'warning' | 'primary' => {
    switch (roleName) {
      case 'super_admin':
        return 'error';
      case 'admin':
        return 'warning';
      default:
        return 'primary';
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          My Profile
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          View and manage your account information
        </Typography>

        <Grid container spacing={3}>
          {/* Profile Card */}
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  mx: 'auto',
                  mb: 2,
                  bgcolor: 'primary.main',
                  fontSize: '3rem',
                }}
              >
                {user.full_name?.charAt(0) || user.username.charAt(0).toUpperCase()}
              </Avatar>
              <Typography variant="h5" gutterBottom>
                {user.full_name || user.username}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                @{user.username}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Chip
                  icon={getRoleIcon(user.role.name)}
                  label={user.role.name.replace('_', ' ').toUpperCase()}
                  color={getRoleColor(user.role.name)}
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 1 }}>
                {user.is_active ? (
                  <Chip icon={<CheckCircle />} label="Active" color="success" size="small" />
                ) : (
                  <Chip icon={<Cancel />} label="Inactive" color="error" size="small" />
                )}
                {user.is_verified && (
                  <Chip icon={<VerifiedUser />} label="Verified" color="info" size="small" />
                )}
              </Box>
              <Divider sx={{ my: 3 }} />
              <Button
                variant="contained"
                startIcon={<Lock />}
                onClick={() => navigate('/change-password')}
                fullWidth
                sx={{ mb: 1 }}
              >
                Change Password
              </Button>
              <Button
                variant="outlined"
                startIcon={<Edit />}
                onClick={() => navigate('/edit-profile')}
                fullWidth
                disabled
              >
                Edit Profile (Coming Soon)
              </Button>
            </Paper>
          </Grid>

          {/* Account Details */}
          <Grid item xs={12} md={8}>
            <Card elevation={3}>
              <CardHeader
                title="Account Information"
                avatar={<Person color="primary" />}
              />
              <CardContent>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Badge />
                    </ListItemIcon>
                    <ListItemText
                      primary="User ID"
                      secondary={user.id}
                      secondaryTypographyProps={{ sx: { fontFamily: 'monospace', fontSize: '0.85rem' } }}
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemIcon>
                      <Person />
                    </ListItemIcon>
                    <ListItemText primary="Username" secondary={user.username} />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemIcon>
                      <Email />
                    </ListItemIcon>
                    <ListItemText primary="Email" secondary={user.email} />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemIcon>
                      <CalendarToday />
                    </ListItemIcon>
                    <ListItemText primary="Account Created" secondary={formatDate(user.created_at)} />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemIcon>
                      <AccessTime />
                    </ListItemIcon>
                    <ListItemText primary="Last Login" secondary={formatDate(user.last_login)} />
                  </ListItem>
                </List>
              </CardContent>
            </Card>

            {/* Role Information */}
            <Card elevation={3} sx={{ mt: 3 }}>
              <CardHeader
                title="Role & Permissions"
                avatar={<Security color="primary" />}
                action={
                  <Button
                    size="small"
                    onClick={() => navigate('/roles')}
                  >
                    View All Roles
                  </Button>
                }
              />
              <CardContent>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    Current Role: {user.role.name.replace('_', ' ').toUpperCase()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {user.role.description}
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  Permissions:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {user.role.permissions && typeof user.role.permissions === 'object' ? (
                    user.role.permissions.all ? (
                      <Chip label="Full System Access" color="error" size="small" />
                    ) : (
                      Object.entries(user.role.permissions).map(([key, value]) => (
                        Array.isArray(value) ? (
                          value.map((perm: string) => (
                            <Chip
                              key={`${key}-${perm}`}
                              label={`${key}: ${perm}`}
                              size="small"
                              variant="outlined"
                            />
                          ))
                        ) : (
                          <Chip
                            key={key}
                            label={`${key}: ${value}`}
                            size="small"
                            variant="outlined"
                          />
                        )
                      ))
                    )
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No specific permissions defined
                    </Typography>
                  )}
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="text"
                    size="small"
                    onClick={() => navigate('/privileges')}
                  >
                    Learn about privileges
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ProfilePage;
