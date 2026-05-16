import { request } from '@/common/api';
import type { Article, ArticleListItem, PaginatedResponse, PaginationParams } from '@/common/entities';

export const articlesApi = {
  // List articles with pagination and filtering
  list: async (params?: PaginationParams & { search?: string; category?: number; tags?: number[] }) => {
    const response = await request.get<PaginatedResponse<ArticleListItem>>('/articles/', { params });
    return response.data;
  },

  // Get single article
  detail: async (id: number | string) => {
    const response = await request.get<Article>(`/articles/${id}/`);
    return response.data;
  },

  // Create article (admin/editor only)
  create: async (data: Partial<Article>) => {
    const response = await request.post<Article>('/articles/', data);
    return response.data;
  },

  // Update article
  update: async (id: number, data: Partial<Article>) => {
    const response = await request.patch<Article>(`/articles/${id}/`, data);
    return response.data;
  },

  // Publish article
  publish: async (id: number) => {
    const response = await request.post(`/articles/${id}/publish/`);
    return response.data;
  },

  // Delete article
  delete: async (id: number) => {
    await request.delete(`/articles/${id}/`);
  },
};
