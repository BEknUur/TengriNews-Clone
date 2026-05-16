import { request } from '@/common/api';
import type { Comment, CommentCreate, PaginatedResponse, PaginationParams } from '@/common/entities';

export const commentsApi = {
  // List comments for an article
  list: async (articleId: number, params?: PaginationParams) => {
    const response = await request.get<PaginatedResponse<Comment>>('/comments/', {
      params: { article: articleId, ...params },
    });
    return response.data;
  },

  // Get single comment
  detail: async (id: number) => {
    const response = await request.get<Comment>(`/comments/${id}/`);
    return response.data;
  },

  // Create comment
  create: async (data: CommentCreate) => {
    const response = await request.post<Comment>('/comments/', data);
    return response.data;
  },

  // Update comment
  update: async (id: number, data: Partial<Comment>) => {
    const response = await request.patch<Comment>(`/comments/${id}/`, data);
    return response.data;
  },

  // Delete comment
  delete: async (id: number) => {
    await request.delete(`/comments/${id}/`);
  },
};
