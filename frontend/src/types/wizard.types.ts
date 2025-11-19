export interface WizardCategory {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
  is_active: boolean;
  created_at: string;
}

export type DependencyType = 'show_if' | 'hide_if' | 'require_if' | 'disable_if';

export interface OptionDependency {
  id: string;
  option_id: string;
  depends_on_option_id: string;
  dependency_type: DependencyType;
  created_at: string;
}

export interface Option {
  id: string;
  option_set_id: string;
  label: string;
  value: string;
  description?: string;
  display_order: number;
  icon?: string;
  image_url?: string;
  is_default: boolean;
  is_recommended: boolean;
  is_active: boolean;
  metadata: Record<string, unknown>;
  dependencies: OptionDependency[];
  created_at: string;
}

export interface OptionSet {
  id: string;
  step_id: string;
  name: string;
  description?: string;
  selection_type: SelectionType;
  is_required: boolean;
  min_selections: number;
  max_selections?: number;
  min_value?: number;
  max_value?: number;
  regex_pattern?: string;
  custom_validation: Record<string, unknown>;
  display_order: number;
  placeholder?: string;
  help_text?: string;
  step_increment: number;
  options: Option[];
  created_at: string;
}

export type SelectionType =
  | 'single_select'
  | 'multiple_select'
  | 'text_input'
  | 'number_input'
  | 'date_input'
  | 'time_input'
  | 'datetime_input'
  | 'file_upload'
  | 'rating'
  | 'slider'
  | 'color_picker'
  | 'rich_text';

export interface Step {
  id: string;
  wizard_id: string;
  name: string;
  description?: string;
  help_text?: string;
  step_order: number;
  is_required: boolean;
  is_skippable: boolean;
  allow_back_navigation: boolean;
  layout: string;
  custom_styles: Record<string, unknown>;
  validation_rules: Record<string, unknown>;
  option_sets: OptionSet[];
  created_at: string;
}

export interface Wizard {
  id: string;
  name: string;
  description?: string;
  category_id?: string;
  created_by: string;
  icon?: string;
  cover_image?: string;
  is_published: boolean;
  is_active: boolean;
  allow_templates: boolean;
  require_login: boolean;
  allow_anonymous: boolean;
  auto_save: boolean;
  auto_save_interval: number;
  estimated_time?: number;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  tags: string[];
  total_sessions: number;
  completed_sessions: number;
  average_completion_time?: number;
  steps: Step[];
  category?: WizardCategory;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface WizardListItem {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  cover_image?: string;
  is_published: boolean;
  require_login: boolean;
  estimated_time?: number;
  difficulty_level?: string;
  tags: string[];
  total_sessions: number;
  completed_sessions: number;
  category?: WizardCategory;
  created_at: string;
}
