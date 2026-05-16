import { request } from '@/common/api/request';
import type { AuthTokens, RegisterResponse, User } from '@/common/entities';

export const authApi = {
  login: async (credentials: { email: string; password: string }): Promise<AuthTokens> => {
    const response = await request.post('/accounts/auth/token/', credentials);
    return response.data;
  },

  register: async (data: {
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
  }): Promise<RegisterResponse> => {
    const response = await request.post('/accounts/auth/register/', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await request.get('/accounts/users/me/');
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<{ access: string }> => {
    const response = await request.post('/accounts/auth/token/refresh/', { refresh: refreshToken });
    return response.data;
  },
};
