import api from './api';
import { Wizard, WizardListItem, WizardCategory, OptionDependency, DependencyType } from '../types';

export const wizardService = {
  async getWizards(params?: {
    skip?: number;
    limit?: number;
    category_id?: string;
    published_only?: boolean;
  }): Promise<WizardListItem[]> {
    const response = await api.get<WizardListItem[]>('/wizards', { params });
    return response.data;
  },

  async getWizard(wizardId: string): Promise<Wizard> {
    const response = await api.get<Wizard>(`/wizards/${wizardId}`);
    return response.data;
  },

  async getCategories(): Promise<WizardCategory[]> {
    const response = await api.get<WizardCategory[]>('/wizards/categories/');
    return response.data;
  },

  async createWizard(data: any): Promise<Wizard> {
    const response = await api.post<Wizard>('/wizards/', data);
    return response.data;
  },

  async updateWizard(wizardId: string, data: Partial<Wizard>): Promise<Wizard> {
    const response = await api.put<Wizard>(`/wizards/${wizardId}`, data);
    return response.data;
  },

  async publishWizard(wizardId: string, publish: boolean = true): Promise<void> {
    await api.put(`/wizards/${wizardId}/publish`, null, {
      params: { publish },
    });
  },

  async deleteWizard(wizardId: string): Promise<void> {
    await api.delete(`/wizards/${wizardId}`);
  },

  // Option Dependency Management
  async getOptionDependencies(optionId: string): Promise<OptionDependency[]> {
    const response = await api.get<OptionDependency[]>(`/wizards/options/${optionId}/dependencies`);
    return response.data;
  },

  async createOptionDependency(
    optionId: string,
    data: {
      depends_on_option_id: string;
      dependency_type: DependencyType;
    }
  ): Promise<OptionDependency> {
    const response = await api.post<OptionDependency>(
      `/wizards/options/${optionId}/dependencies`,
      data
    );
    return response.data;
  },

  async deleteOptionDependency(dependencyId: string): Promise<void> {
    await api.delete(`/wizards/dependencies/${dependencyId}`);
  },
};
