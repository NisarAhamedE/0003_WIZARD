/**
 * Wizard Run Service
 * API calls for wizard run execution and storage
 */

import api from './api';
import {
  WizardRun,
  WizardRunCreate,
  WizardRunUpdate,
  WizardRunProgressUpdate,
  WizardRunCompleteRequest,
  WizardRunListResponse,
  WizardRunDetailResponse,
  WizardRunStepResponse,
  WizardRunStepResponseCreate,
  WizardRunStepResponseUpdate,
  WizardRunOptionSetResponse,
  WizardRunOptionSetResponseCreate,
  WizardRunOptionSetResponseUpdate,
  WizardRunFileUpload,
  WizardRunShare,
  WizardRunShareCreate,
  WizardRunComparison,
  WizardRunComparisonCreate,
  WizardRunStats,
  RunFilters,
} from '../types/wizardRun.types';

class WizardRunService {
  private baseUrl = '/wizard-runs';

  // ============================================================================
  // Wizard Run CRUD
  // ============================================================================

  /**
   * Get list of wizard runs for current user
   */
  async getWizardRuns(filters?: RunFilters): Promise<WizardRunListResponse> {
    const params = new URLSearchParams();

    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
    if (filters?.wizard_id) params.append('wizard_id', filters.wizard_id);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.is_stored !== undefined) {
      params.append('is_stored', filters.is_stored.toString());
    }
    if (filters?.is_favorite !== undefined) {
      params.append('is_favorite', filters.is_favorite.toString());
    }

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}?${queryString}` : this.baseUrl;

    const response = await api.get<WizardRunListResponse>(url);
    return response.data;
  }

  /**
   * Get in-progress runs
   */
  async getInProgressRuns(): Promise<WizardRun[]> {
    const response = await api.get<WizardRun[]>(`${this.baseUrl}/in-progress`);
    return response.data;
  }

  /**
   * Get completed runs
   */
  async getCompletedRuns(skip: number = 0, limit: number = 20): Promise<WizardRun[]> {
    const response = await api.get<WizardRun[]>(
      `${this.baseUrl}/completed?skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  /**
   * Get stored runs (Store Wizard repository)
   */
  async getStoredRuns(skip: number = 0, limit: number = 20): Promise<WizardRun[]> {
    const response = await api.get<WizardRun[]>(
      `${this.baseUrl}/stored?skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  /**
   * Get favorite runs
   */
  async getFavoriteRuns(): Promise<WizardRun[]> {
    const response = await api.get<WizardRun[]>(`${this.baseUrl}/favorites`);
    return response.data;
  }

  /**
   * Get run statistics
   */
  async getRunStats(): Promise<WizardRunStats> {
    const response = await api.get<WizardRunStats>(`${this.baseUrl}/stats`);
    return response.data;
  }

  /**
   * Get a specific wizard run with all details
   */
  async getWizardRun(runId: string): Promise<WizardRunDetailResponse> {
    const response = await api.get<WizardRunDetailResponse>(`${this.baseUrl}/${runId}`);
    return response.data;
  }

  /**
   * Start a new wizard run
   */
  async createWizardRun(run: WizardRunCreate): Promise<WizardRun> {
    const response = await api.post<WizardRun>(this.baseUrl, run);
    return response.data;
  }

  /**
   * Update a wizard run
   */
  async updateWizardRun(runId: string, updates: WizardRunUpdate): Promise<WizardRun> {
    const response = await api.put<WizardRun>(`${this.baseUrl}/${runId}`, updates);
    return response.data;
  }

  /**
   * Update run progress (auto-save)
   */
  async updateRunProgress(
    runId: string,
    progress: WizardRunProgressUpdate
  ): Promise<WizardRun> {
    const response = await api.post<WizardRun>(`${this.baseUrl}/${runId}/progress`, progress);
    return response.data;
  }

  /**
   * Complete a wizard run
   */
  async completeWizardRun(
    runId: string,
    completeRequest: WizardRunCompleteRequest
  ): Promise<WizardRun> {
    const response = await api.post<WizardRun>(
      `${this.baseUrl}/${runId}/complete`,
      completeRequest
    );
    return response.data;
  }

  /**
   * Abandon a wizard run
   */
  async abandonWizardRun(runId: string): Promise<WizardRun> {
    const response = await api.post<WizardRun>(`${this.baseUrl}/${runId}/abandon`);
    return response.data;
  }

  /**
   * Delete a wizard run
   */
  async deleteWizardRun(runId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${runId}`);
  }

  // ============================================================================
  // Step Responses
  // ============================================================================

  /**
   * Save step response
   */
  async createStepResponse(
    runId: string,
    stepResponse: WizardRunStepResponseCreate
  ): Promise<WizardRunStepResponse> {
    const response = await api.post<WizardRunStepResponse>(
      `${this.baseUrl}/${runId}/steps`,
      stepResponse
    );
    return response.data;
  }

  /**
   * Update step response
   */
  async updateStepResponse(
    stepResponseId: string,
    updates: WizardRunStepResponseUpdate
  ): Promise<WizardRunStepResponse> {
    const response = await api.put<WizardRunStepResponse>(
      `${this.baseUrl}/steps/${stepResponseId}`,
      updates
    );
    return response.data;
  }

  /**
   * Clear all responses for a run (for update operations)
   */
  async clearAllResponses(runId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${runId}/responses`);
  }

  // ============================================================================
  // Option Set Responses
  // ============================================================================

  /**
   * Save option set response
   */
  async createOptionSetResponse(
    runId: string,
    optionSetResponse: WizardRunOptionSetResponseCreate
  ): Promise<WizardRunOptionSetResponse> {
    const response = await api.post<WizardRunOptionSetResponse>(
      `${this.baseUrl}/${runId}/option-sets`,
      optionSetResponse
    );
    return response.data;
  }

  /**
   * Update option set response
   */
  async updateOptionSetResponse(
    responseId: string,
    updates: WizardRunOptionSetResponseUpdate
  ): Promise<WizardRunOptionSetResponse> {
    const response = await api.put<WizardRunOptionSetResponse>(
      `${this.baseUrl}/option-sets/${responseId}`,
      updates
    );
    return response.data;
  }

  // ============================================================================
  // File Uploads
  // ============================================================================

  /**
   * Upload a file for a wizard run
   */
  async uploadFile(
    runId: string,
    optionSetResponseId: string,
    file: File
  ): Promise<WizardRunFileUpload> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<WizardRunFileUpload>(
      `${this.baseUrl}/${runId}/upload?option_set_response_id=${optionSetResponseId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  // ============================================================================
  // Sharing
  // ============================================================================

  /**
   * Create a share link for a run
   */
  async createShareLink(
    runId: string,
    shareRequest: WizardRunShareCreate
  ): Promise<WizardRunShare> {
    const response = await api.post<WizardRunShare>(
      `${this.baseUrl}/${runId}/share`,
      shareRequest
    );
    return response.data;
  }

  /**
   * Access a run via share token (public endpoint)
   */
  async getRunByShareToken(shareToken: string): Promise<WizardRunDetailResponse> {
    const response = await api.get<WizardRunDetailResponse>(
      `${this.baseUrl}/share/${shareToken}`
    );
    return response.data;
  }

  // ============================================================================
  // Comparisons
  // ============================================================================

  /**
   * Create a comparison of multiple runs
   */
  async createComparison(
    comparison: WizardRunComparisonCreate
  ): Promise<WizardRunComparison> {
    const response = await api.post<WizardRunComparison>(
      `${this.baseUrl}/comparisons`,
      comparison
    );
    return response.data;
  }

  /**
   * Get all comparisons for current user
   */
  async getMyComparisons(): Promise<WizardRunComparison[]> {
    const response = await api.get<WizardRunComparison[]>(`${this.baseUrl}/comparisons`);
    return response.data;
  }

  /**
   * Get a specific comparison
   */
  async getComparison(comparisonId: string): Promise<WizardRunComparison> {
    const response = await api.get<WizardRunComparison>(
      `${this.baseUrl}/comparisons/${comparisonId}`
    );
    return response.data;
  }

  /**
   * Delete a comparison
   */
  async deleteComparison(comparisonId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/comparisons/${comparisonId}`);
  }
}

export const wizardRunService = new WizardRunService();
