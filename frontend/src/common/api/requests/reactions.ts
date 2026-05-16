import { request } from '@/common/api';
import type { Reaction, ReactionCreate } from '@/common/entities';

export const reactionsApi = {
  // Get reactions for a resource
  list: async (params?: { article?: number; comment?: number }) => {
    const response = await request.get<Reaction[]>('/reactions/', { params });
    return response.data;
  },

  // Create or update reaction
  create: async (data: ReactionCreate) => {
    const response = await request.post<Reaction>('/reactions/', data);
    return response.data;
  },

  // Delete reaction
  delete: async (id: number) => {
    await request.delete(`/reactions/${id}/`);
  },
};
