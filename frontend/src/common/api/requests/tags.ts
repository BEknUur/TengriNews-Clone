import { request } from '@/common/api';
import type { Tag } from '@/common/entities';

export const tagsApi = {
  // List all tags
  list: async () => {
    const response = await request.get<Tag[]>('/tags/');
    return response.data;
  },

  // Get single tag
  detail: async (id: number | string) => {
    const response = await request.get<Tag>(`/tags/${id}/`);
    return response.data;
  },

  // Create tag (admin only)
  create: async (data: Omit<Tag, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await request.post<Tag>('/tags/', data);
    return response.data;
  },

  // Update tag
  update: async (id: number, data: Partial<Tag>) => {
    const response = await request.patch<Tag>(`/tags/${id}/`, data);
    return response.data;
  },

  // Delete tag
  delete: async (id: number) => {
    await request.delete(`/tags/${id}/`);
  },
};
