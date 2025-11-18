export interface SessionResponse {
  id: string;
  session_id: string;
  step_id: string;
  option_set_id: string;
  response_data: ResponseData;
  time_spent_seconds?: number;
  answered_at: string;
  is_valid: boolean;
  validation_errors: string[];
}

export interface ResponseData {
  selected_option_id?: string;
  selected_option_ids?: string[];
  text?: string;
  number?: number;
  date?: string;
  file_url?: string;
  rating?: number;
  color?: string;
}

export type SessionStatus = 'in_progress' | 'completed' | 'abandoned' | 'expired';

export interface Session {
  id: string;
  wizard_id: string;
  user_id?: string;
  session_name?: string;
  status: SessionStatus;
  current_step_id?: string;
  progress_percentage: number;
  started_at: string;
  last_activity_at: string;
  completed_at?: string;
  metadata: Record<string, unknown>;
  browser_info: Record<string, unknown>;
  total_time_seconds?: number;
  responses: SessionResponse[];
  created_at: string;
  updated_at: string;
}

export interface SessionListItem {
  id: string;
  wizard_id: string;
  session_name?: string;
  status: SessionStatus;
  progress_percentage: number;
  started_at: string;
  last_activity_at: string;
  completed_at?: string;
}

export interface CreateSessionRequest {
  wizard_id: string;
  session_name?: string;
  metadata?: Record<string, unknown>;
  browser_info?: Record<string, unknown>;
}

export interface SaveResponseRequest {
  step_id: string;
  option_set_id: string;
  response_data: ResponseData;
  time_spent_seconds?: number;
}
