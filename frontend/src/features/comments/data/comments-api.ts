import { request } from '@/common/api/request';
import type { Comment } from '@/common/entities';

export const commentsApi = {
  list: async (articleId: number, params?: any) => {
    const response = await request.get(`/comments/`, { params: { ...params, article: articleId } });
    return response.data as Comment[];
  },

  detail: async (id: number) => {
    const response = await request.get(`/comments/${id}/`);
    return response.data as Comment;
  },

  create: async (data: { article: number; content: string; parent?: number | null }) => {
    const response = await request.post('/comments/', data);
    return response.data as Comment;
  },

  update: async (id: number, data: { content: string }) => {
    const response = await request.patch(`/comments/${id}/`, data);
    return response.data as Comment;
  },

  delete: async (id: number) => {
    await request.delete(`/comments/${id}/`);
  },
};
