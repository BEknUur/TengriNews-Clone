import { request } from '@/common/api/request';
import type { Bookmark } from '@/common/entities';

export const bookmarksApi = {
  list: async () => {
    const response = await request.get('/bookmarks/');
    return response.data as Bookmark[];
  },

  create: async (articleId: number) => {
    const response = await request.post(`/articles/${articleId}/bookmark/`);
    return response.data as Bookmark;
  },

  delete: async (articleId: number) => {
    await request.delete(`/articles/${articleId}/bookmark/`);
  },
};
