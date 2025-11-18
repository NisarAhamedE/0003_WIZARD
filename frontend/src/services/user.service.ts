import api from './api';

export interface UserRole {
  id: string;
  name: string;
  description?: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  role: UserRole;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  full_name?: string;
  is_active?: boolean;
}

export const userService = {
  async getUsers(params?: { skip?: number; limit?: number }): Promise<User[]> {
    const response = await api.get<User[]>('/users', { params });
    return response.data;
  },

  async getUser(userId: string): Promise<User> {
    const response = await api.get<User>(`/users/${userId}`);
    return response.data;
  },

  async updateUser(userId: string, data: UserUpdate): Promise<User> {
    const response = await api.put<User>(`/users/${userId}`, data);
    return response.data;
  },

  async changeUserRole(userId: string, roleName: string): Promise<void> {
    await api.put(`/users/${userId}/role`, null, {
      params: { role_name: roleName },
    });
  },

  async deactivateUser(userId: string): Promise<void> {
    await api.delete(`/users/${userId}`);
  },
};
