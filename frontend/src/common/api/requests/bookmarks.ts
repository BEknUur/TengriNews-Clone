import { request } from '@/common/api';
import type { Bookmark, BookmarkCreate, PaginatedResponse, PaginationParams } from '@/common/entities';

export const bookmarksApi = {
  // List user's bookmarks
  list: async (params?: PaginationParams) => {
    const response = await request.get<PaginatedResponse<Bookmark>>('/bookmarks/', { params });
    return response.data;
  },

  // Create bookmark
  create: async (data: BookmarkCreate) => {
    const response = await request.post<Bookmark>('/bookmarks/', data);
    return response.data;
  },

  // Delete bookmark
  delete: async (id: number) => {
    await request.delete(`/bookmarks/${id}/`);
  },
};
