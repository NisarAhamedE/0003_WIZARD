import { ResponseData } from './session.types';

export interface TemplateResponse {
  id: string;
  template_id: string;
  step_id: string;
  option_set_id: string;
  response_data: ResponseData;
}

export interface Template {
  id: string;
  wizard_id: string;
  user_id: string;
  source_session_id?: string;
  name: string;
  description?: string;
  is_public: boolean;
  is_active: boolean;
  times_used: number;
  last_used_at?: string;
  tags: string[];
  responses: TemplateResponse[];
  created_at: string;
  updated_at: string;
}

export interface TemplateListItem {
  id: string;
  wizard_id: string;
  user_id: string;
  name: string;
  description?: string;
  is_public: boolean;
  tags: string[];
  times_used: number;
  last_used_at?: string;
  created_at: string;
}

export interface CreateTemplateFromSessionRequest {
  name: string;
  description?: string;
  is_public?: boolean;
  tags?: string[];
}
