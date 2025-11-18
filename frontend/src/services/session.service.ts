import api from './api';
import {
  Session,
  SessionListItem,
  CreateSessionRequest,
  SaveResponseRequest,
} from '../types';

export const sessionService = {
  async getSessions(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<SessionListItem[]> {
    const response = await api.get<SessionListItem[]>('/sessions', { params });
    return response.data;
  },

  async getSession(sessionId: string): Promise<Session> {
    const response = await api.get<Session>(`/sessions/${sessionId}`);
    return response.data;
  },

  async createSession(data: CreateSessionRequest): Promise<Session> {
    const response = await api.post<Session>('/sessions', data);
    return response.data;
  },

  async updateSession(
    sessionId: string,
    data: Partial<Session>
  ): Promise<Session> {
    const response = await api.put<Session>(`/sessions/${sessionId}`, data);
    return response.data;
  },

  async saveResponse(
    sessionId: string,
    data: SaveResponseRequest
  ): Promise<Session> {
    const response = await api.post<Session>(
      `/sessions/${sessionId}/responses`,
      data
    );
    return response.data;
  },

  async completeSession(sessionId: string): Promise<Session> {
    const response = await api.put<Session>(`/sessions/${sessionId}/complete`);
    return response.data;
  },

  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/sessions/${sessionId}`);
  },

  // Alias for backward compatibility
  async abandonSession(sessionId: string): Promise<void> {
    return this.deleteSession(sessionId);
  },
};
