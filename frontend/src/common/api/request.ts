import axios from 'axios';

import { apiConfig } from './config/api.config';
import { getAuthToken } from '@/common/utils/auth';

export const request = axios.create({
  baseURL: apiConfig.apiUrl,
  timeout: apiConfig.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

request.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    return config;
  },
  (error) => Promise.reject(error),
);

request.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      localStorage.removeItem('auth_refresh');

      const isAuthPage = window.location.pathname.startsWith('/auth/');
      if (!isAuthPage) {
        window.location.href = '/auth/login';
      }
    }

    return Promise.reject(error);
  },
);

export default request;
