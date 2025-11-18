import api from './api';
import {
  Template,
  TemplateListItem,
  CreateTemplateFromSessionRequest,
} from '../types';

export const templateService = {
  async getTemplates(params?: {
    skip?: number;
    limit?: number;
    wizard_id?: string;
    mine_only?: boolean;
  }): Promise<TemplateListItem[]> {
    const response = await api.get<TemplateListItem[]>('/templates', { params });
    return response.data;
  },

  async getTemplate(templateId: string): Promise<Template> {
    const response = await api.get<Template>(`/templates/${templateId}`);
    return response.data;
  },

  async createTemplateFromSession(
    sessionId: string,
    data: CreateTemplateFromSessionRequest
  ): Promise<Template> {
    const response = await api.post<Template>(
      `/templates/from-session/${sessionId}`,
      null,
      { params: data }
    );
    return response.data;
  },

  async updateTemplate(
    templateId: string,
    data: Partial<Template>
  ): Promise<Template> {
    const response = await api.put<Template>(`/templates/${templateId}`, data);
    return response.data;
  },

  async replayTemplate(
    templateId: string,
    sessionName?: string
  ): Promise<{ session_id: string; message: string }> {
    const response = await api.post(`/templates/${templateId}/replay`, null, {
      params: { session_name: sessionName },
    });
    return response.data;
  },

  async deleteTemplate(templateId: string): Promise<void> {
    await api.delete(`/templates/${templateId}`);
  },
};
