import { request } from '@/common/api';
import type { Category } from '@/common/entities';

export const categoriesApi = {
  // List all categories
  list: async () => {
    const response = await request.get<Category[]>('/categories/');
    return response.data;
  },

  // Get single category
  detail: async (id: number | string) => {
    const response = await request.get<Category>(`/categories/${id}/`);
    return response.data;
  },

  // Create category (admin only)
  create: async (data: Omit<Category, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await request.post<Category>('/categories/', data);
    return response.data;
  },

  // Update category
  update: async (id: number, data: Partial<Category>) => {
    const response = await request.patch<Category>(`/categories/${id}/`, data);
    return response.data;
  },

  // Delete category
  delete: async (id: number) => {
    await request.delete(`/categories/${id}/`);
  },
};
