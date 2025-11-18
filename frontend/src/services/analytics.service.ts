import api from './api';

export interface DashboardStats {
  total_wizards: number;
  published_wizards: number;
  total_sessions: number;
  completed_sessions: number;
  sessions_this_week: number;
  completion_rate: number;
  average_session_time: number;
  total_users: number;
  total_revenue: number;
}

export interface WizardPerformance {
  wizard_id: string;
  wizard_name: string;
  total_sessions: number;
  completed_sessions: number;
  abandoned_sessions: number;
  completion_rate: number;
  average_time_seconds: number;
  total_revenue: number;
}

export interface SessionTimeline {
  date: string;
  total: number;
  completed: number;
}

export interface RecentSession {
  id: string;
  wizard_name: string;
  user_name: string;
  status: string;
  progress: number;
  started_at: string;
}

export const analyticsService = {
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/analytics/dashboard');
    return response.data;
  },

  async getWizardPerformance(limit: number = 10): Promise<WizardPerformance[]> {
    const response = await api.get<WizardPerformance[]>('/analytics/wizards/performance', {
      params: { limit },
    });
    return response.data;
  },

  async getSessionsTimeline(days: number = 30): Promise<SessionTimeline[]> {
    const response = await api.get<SessionTimeline[]>('/analytics/sessions/timeline', {
      params: { days },
    });
    return response.data;
  },

  async getRecentSessions(limit: number = 10): Promise<RecentSession[]> {
    const response = await api.get<RecentSession[]>('/analytics/sessions/recent', {
      params: { limit },
    });
    return response.data;
  },
};
