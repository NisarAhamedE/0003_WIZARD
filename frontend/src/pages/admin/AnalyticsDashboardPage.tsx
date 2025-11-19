import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  AutoFixHigh as WizardIcon,
  PlayCircle as RunIcon,
  CheckCircle as CompletedIcon,
  People as UsersIcon,
  Timer as TimeIcon,
  TrendingUp as TrendIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analytics.service';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: string;
  subtitle?: string;
}> = ({ title, value, icon, color = 'primary.main', subtitle }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" component="div">
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box sx={{ color }}>{icon}</Box>
      </Box>
    </CardContent>
  </Card>
);

const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (minutes < 60) return `${minutes}m ${secs}s`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const AnalyticsDashboardPage: React.FC = () => {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: () => analyticsService.getDashboardStats(),
  });

  const { data: wizardPerformance, isLoading: perfLoading } = useQuery({
    queryKey: ['analytics', 'wizard-performance'],
    queryFn: () => analyticsService.getWizardPerformance(),
  });

  const { data: recentRuns, isLoading: runsLoading } = useQuery({
    queryKey: ['analytics', 'recent-runs'],
    queryFn: () => analyticsService.getRecentSessions(),
  });

  if (statsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics Dashboard
      </Typography>

      {/* Summary Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Wizards"
            value={stats?.total_wizards || 0}
            icon={<WizardIcon sx={{ fontSize: 40 }} />}
            color="primary.main"
            subtitle={`${stats?.published_wizards || 0} published`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Runs"
            value={stats?.total_sessions || 0}
            icon={<RunIcon sx={{ fontSize: 40 }} />}
            color="info.main"
            subtitle={`${stats?.sessions_this_week || 0} this week`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completion Rate"
            value={`${stats?.completion_rate || 0}%`}
            icon={<CompletedIcon sx={{ fontSize: 40 }} />}
            color="success.main"
            subtitle={`${stats?.completed_sessions || 0} completed`}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon={<UsersIcon sx={{ fontSize: 40 }} />}
            color="secondary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Average Run Time"
            value={formatDuration(stats?.average_session_time || 0)}
            icon={<TimeIcon sx={{ fontSize: 40 }} />}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Runs This Week"
            value={stats?.sessions_this_week || 0}
            icon={<TrendIcon sx={{ fontSize: 40 }} />}
            color="success.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Wizard Performance Table */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Wizard Performance
              </Typography>
              {perfLoading ? (
                <CircularProgress />
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Wizard</TableCell>
                        <TableCell align="right">Runs</TableCell>
                        <TableCell align="right">Completion</TableCell>
                        <TableCell align="right">Avg Time</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {wizardPerformance?.map((wizard) => (
                        <TableRow key={wizard.wizard_id}>
                          <TableCell>{wizard.wizard_name}</TableCell>
                          <TableCell align="right">{wizard.total_sessions}</TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={wizard.completion_rate}
                                sx={{ width: 60, height: 8, borderRadius: 4 }}
                              />
                              <Typography variant="body2">{wizard.completion_rate}%</Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            {formatDuration(wizard.average_time_seconds)}
                          </TableCell>
                        </TableRow>
                      ))}
                      {(!wizardPerformance || wizardPerformance.length === 0) && (
                        <TableRow>
                          <TableCell colSpan={4} align="center">
                            No wizard data available
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Runs */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Runs
              </Typography>
              {runsLoading ? (
                <CircularProgress />
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Wizard</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentRuns?.map((run) => (
                        <TableRow key={run.id}>
                          <TableCell>{run.wizard_name}</TableCell>
                          <TableCell>{run.user_name}</TableCell>
                          <TableCell>
                            <Chip
                              size="small"
                              label={run.status}
                              color={
                                run.status === 'completed'
                                  ? 'success'
                                  : run.status === 'in_progress'
                                    ? 'info'
                                    : 'default'
                              }
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                      {(!recentRuns || recentRuns.length === 0) && (
                        <TableRow>
                          <TableCell colSpan={3} align="center">
                            No recent runs
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboardPage;
