/**
 * Wizard Template Service
 * API calls for wizard template management
 */

import api from './api';
import {
  WizardTemplate,
  WizardTemplateCreate,
  WizardTemplateUpdate,
  WizardTemplateListResponse,
  WizardTemplateRating,
  WizardTemplateRatingCreate,
  WizardTemplateStats,
  WizardTemplateCloneRequest,
  WizardTemplateCloneResponse,
  TemplateFilters,
} from '../types/wizardTemplate.types';

class WizardTemplateService {
  private baseUrl = '/wizard-templates';

  /**
   * Get list of templates with filtering and pagination
   */
  async getTemplates(filters?: TemplateFilters): Promise<WizardTemplateListResponse> {
    const params = new URLSearchParams();

    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
    if (filters?.category) params.append('category', filters.category);
    if (filters?.difficulty_level) params.append('difficulty_level', filters.difficulty_level);
    if (filters?.is_system_template !== undefined) {
      params.append('is_system_template', filters.is_system_template.toString());
    }
    if (filters?.search) params.append('search', filters.search);

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}?${queryString}` : this.baseUrl;

    const response = await api.get<WizardTemplateListResponse>(url);
    return response.data;
  }

  /**
   * Get popular templates by usage count
   */
  async getPopularTemplates(limit: number = 10): Promise<WizardTemplate[]> {
    const response = await api.get<WizardTemplate[]>(`${this.baseUrl}/popular?limit=${limit}`);
    return response.data;
  }

  /**
   * Get top rated templates
   */
  async getTopRatedTemplates(limit: number = 10): Promise<WizardTemplate[]> {
    const response = await api.get<WizardTemplate[]>(`${this.baseUrl}/top-rated?limit=${limit}`);
    return response.data;
  }

  /**
   * Get templates by category
   */
  async getTemplatesByCategory(category: string): Promise<WizardTemplate[]> {
    const response = await api.get<WizardTemplate[]>(`${this.baseUrl}/categories/${category}`);
    return response.data;
  }

  /**
   * Get a specific template by ID
   */
  async getTemplate(templateId: string): Promise<WizardTemplate> {
    const response = await api.get<WizardTemplate>(`${this.baseUrl}/${templateId}`);
    return response.data;
  }

  /**
   * Create a new template (Admin only)
   */
  async createTemplate(template: WizardTemplateCreate): Promise<WizardTemplate> {
    const response = await api.post<WizardTemplate>(this.baseUrl, template);
    return response.data;
  }

  /**
   * Update a template (Admin only)
   */
  async updateTemplate(
    templateId: string,
    updates: WizardTemplateUpdate
  ): Promise<WizardTemplate> {
    const response = await api.put<WizardTemplate>(`${this.baseUrl}/${templateId}`, updates);
    return response.data;
  }

  /**
   * Delete a template (Admin only)
   */
  async deleteTemplate(templateId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${templateId}`);
  }

  /**
   * Clone a template to create a new wizard in Wizard Builder
   */
  async cloneTemplate(
    cloneRequest: WizardTemplateCloneRequest
  ): Promise<WizardTemplateCloneResponse> {
    const response = await api.post<WizardTemplateCloneResponse>(
      `${this.baseUrl}/clone`,
      cloneRequest
    );
    return response.data;
  }

  /**
   * Get ratings for a template
   */
  async getTemplateRatings(
    templateId: string,
    skip: number = 0,
    limit: number = 20
  ): Promise<WizardTemplateRating[]> {
    const response = await api.get<WizardTemplateRating[]>(
      `${this.baseUrl}/${templateId}/ratings?skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  /**
   * Get template statistics
   */
  async getTemplateStats(templateId: string): Promise<WizardTemplateStats> {
    const response = await api.get<WizardTemplateStats>(`${this.baseUrl}/${templateId}/stats`);
    return response.data;
  }

  /**
   * Rate a template (creates or updates user's rating)
   */
  async rateTemplate(
    templateId: string,
    rating: WizardTemplateRatingCreate
  ): Promise<WizardTemplateRating> {
    const response = await api.post<WizardTemplateRating>(
      `${this.baseUrl}/${templateId}/ratings`,
      rating
    );
    return response.data;
  }

  /**
   * Delete user's rating for a template
   */
  async deleteTemplateRating(templateId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${templateId}/ratings`);
  }

  /**
   * Get current user's ratings
   */
  async getMyRatings(skip: number = 0, limit: number = 20): Promise<WizardTemplateRating[]> {
    const response = await api.get<WizardTemplateRating[]>(
      `${this.baseUrl}/users/me/ratings?skip=${skip}&limit=${limit}`
    );
    return response.data;
  }
}

export const wizardTemplateService = new WizardTemplateService();
