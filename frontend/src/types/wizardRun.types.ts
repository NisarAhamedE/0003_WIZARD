/**
 * Wizard Run Types
 * Maps to backend schemas in backend/app/schemas/wizard_run.py
 */

export interface WizardRun {
  id: string;
  wizard_id: string;
  user_id?: string;
  run_name?: string;
  run_description?: string;
  status: 'in_progress' | 'completed' | 'abandoned';
  current_step_index: number;
  total_steps?: number;
  progress_percentage: number;
  started_at: string;
  completed_at?: string;
  last_accessed_at: string;
  calculated_price?: number;
  is_stored: boolean;
  is_favorite: boolean;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface WizardRunCreate {
  wizard_id: string;
  run_name?: string;
  run_description?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface WizardRunUpdate {
  run_name?: string;
  run_description?: string;
  is_favorite?: boolean;
  is_stored?: boolean;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface WizardRunProgressUpdate {
  current_step_index: number;
}

export interface WizardRunCompleteRequest {
  run_name?: string;
  run_description?: string;
  save_to_store?: boolean;
  tags?: string[];
}

export interface WizardRunListResponse {
  runs: WizardRun[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface WizardRunStepResponse {
  id: string;
  run_id: string;
  step_id: string;
  step_index: number;
  step_name?: string;
  completed: boolean;
  completed_at?: string;
  time_spent_seconds: number;
}

export interface WizardRunStepResponseCreate {
  run_id: string;
  step_id: string;
  step_index: number;
  step_name?: string;
  completed?: boolean;
  time_spent_seconds?: number;
}

export interface WizardRunStepResponseUpdate {
  completed?: boolean;
  time_spent_seconds?: number;
}

export interface WizardRunOptionSetResponse {
  id: string;
  run_id: string;
  step_response_id: string;
  option_set_id: string;
  option_set_name?: string;
  selection_type?: string;
  response_value: Record<string, any>; // JSONB
  selected_options?: string[];
  created_at: string;
  updated_at: string;
}

export interface WizardRunOptionSetResponseCreate {
  run_id: string;
  step_response_id: string;
  option_set_id: string;
  option_set_name?: string;
  selection_type?: string;
  response_value: Record<string, any>;
  selected_options?: string[];
}

export interface WizardRunOptionSetResponseUpdate {
  response_value?: Record<string, any>;
  selected_options?: string[];
}

export interface WizardRunFileUpload {
  id: string;
  run_id: string;
  option_set_response_id: string;
  file_name: string;
  file_path: string;
  file_size?: number;
  file_type?: string;
  uploaded_at: string;
}

export interface WizardRunFileUploadCreate {
  run_id: string;
  option_set_response_id: string;
  file_name: string;
  file_path: string;
  file_size?: number;
  file_type?: string;
}

export interface WizardRunShare {
  id: string;
  run_id: string;
  share_token: string;
  shared_by: string;
  share_type: 'view' | 'edit' | 'clone';
  expires_at?: string;
  created_at: string;
  access_count: number;
  last_accessed_at?: string;
  is_active: boolean;
}

export interface WizardRunShareCreate {
  run_id: string;
  share_type?: 'view' | 'edit' | 'clone';
  expires_at?: string;
}

export interface WizardRunComparison {
  id: string;
  comparison_name?: string;
  run_ids: string[];
  created_by: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface WizardRunComparisonCreate {
  comparison_name?: string;
  run_ids: string[];
  metadata?: Record<string, any>;
}

export interface WizardRunDetailResponse extends WizardRun {
  step_responses: WizardRunStepResponse[];
  option_set_responses: WizardRunOptionSetResponse[];
  file_uploads: WizardRunFileUpload[];
}

export interface WizardRunStats {
  total_runs: number;
  in_progress: number;
  completed: number;
  abandoned: number;
  stored: number;
  favorites: number;
  total_time_spent: number;
  average_completion_time?: number;
}

export interface RunFilters {
  wizard_id?: string;
  status?: 'in_progress' | 'completed' | 'abandoned';
  is_stored?: boolean;
  is_favorite?: boolean;
  skip?: number;
  limit?: number;
}
