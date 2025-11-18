export * from './user.types';
export * from './wizard.types';
export * from './session.types';
export * from './template.types';

// Common API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  error_code?: string;
}
