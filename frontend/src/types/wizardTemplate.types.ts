/**
 * Wizard Template Types
 * Maps to backend schemas in backend/app/schemas/wizard_template.py
 */

export interface WizardTemplate {
  id: string;
  template_name: string;
  template_description?: string;
  category?: string;
  icon?: string;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  estimated_time?: number;
  tags?: string[];
  preview_image?: string;
  step_count?: number;
  option_set_count?: number;
  is_system_template: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
  average_rating: number;
  wizard_structure: Record<string, any>; // JSONB structure
  is_active: boolean;
}

export interface WizardTemplateCreate {
  template_name: string;
  template_description?: string;
  category?: string;
  icon?: string;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  estimated_time?: number;
  tags?: string[];
  preview_image?: string;
  step_count?: number;
  option_set_count?: number;
  is_system_template?: boolean;
  created_by?: string;
  wizard_structure: Record<string, any>;
}

export interface WizardTemplateUpdate {
  template_name?: string;
  template_description?: string;
  category?: string;
  icon?: string;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  estimated_time?: number;
  tags?: string[];
  preview_image?: string;
  step_count?: number;
  option_set_count?: number;
  is_system_template?: boolean;
  wizard_structure?: Record<string, any>;
  is_active?: boolean;
}

export interface WizardTemplateListResponse {
  templates: WizardTemplate[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface WizardTemplateRating {
  id: string;
  template_id: string;
  user_id: string;
  rating: number; // 1-5
  review_text?: string;
  created_at: string;
}

export interface WizardTemplateRatingCreate {
  template_id: string;
  rating: number;
  review_text?: string;
}

export interface WizardTemplateRatingUpdate {
  rating?: number;
  review_text?: string;
}

export interface WizardTemplateStats {
  template_id: string;
  usage_count: number;
  average_rating: number;
  total_ratings: number;
  rating_distribution: {
    1: number;
    2: number;
    3: number;
    4: number;
    5: number;
  };
}

export interface WizardTemplateCloneRequest {
  template_id: string;
  wizard_name: string;
  wizard_description?: string;
  customizations?: Record<string, any>;
}

export interface WizardTemplateCloneResponse {
  wizard_id: string;
  message: string;
}

export interface TemplateFilters {
  category?: string;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  is_system_template?: boolean;
  search?: string;
  skip?: number;
  limit?: number;
}
