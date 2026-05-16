import { request } from '@/common/api';
import type { AuthTokens, User } from '@/common/entities';

interface LoginPayload {
  email: string;
  password: string;
}

interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface AuthResponse {
  access: {
    token: string;
  };
  refresh?: {
    token: string;
  };
  user: User;
}

export const authApi = {
  // Login
  login: async (data: LoginPayload) => {
    const response = await request.post<AuthResponse>('/accounts/login/', data);
    return response.data;
  },

  // Register
  register: async (data: RegisterPayload) => {
    const response = await request.post<AuthResponse>('/accounts/register/', data);
    return response.data;
  },

  // Logout
  logout: async () => {
    await request.post('/accounts/logout/');
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await request.get<User>('/accounts/me/');
    return response.data;
  },

  // Refresh token
  refreshToken: async (refreshToken: string) => {
    const response = await request.post<AuthTokens>('/accounts/auth/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },
};
