import { request } from '@/common/api/request';
import type { Article, ArticleListItem, Category, Tag, PaginationParams } from '@/common/entities';

interface ArticlesListResponse {
  data: ArticleListItem[];
  pagination: {
    count?: number;
    returned?: number;
    next_cursor?: string | null;
  };
}

export const articlesApi = {
  list: async (params?: PaginationParams) => {
    const response = await request.get<ArticlesListResponse>('/articles/', {
      params: {
        ...params,
        pagination: 'page',
      },
    });

    const { data, pagination } = response.data;

    return {
      results: data,
      count: pagination.count ?? data.length,
    };
  },

  detail: async (id: number | string) => {
    const response = await request.get(`/articles/${id}/`);
    return response.data as Article;
  },

  create: async (data: Partial<Article>) => {
    const response = await request.post('/articles/', data);
    return response.data;
  },

  update: async (id: number | string, data: Partial<Article>) => {
    const response = await request.patch(`/articles/${id}/`, data);
    return response.data;
  },

  delete: async (id: number | string) => {
    await request.delete(`/articles/${id}/`);
  },

  publish: async (id: number | string) => {
    const response = await request.post(`/articles/${id}/publish/`);
    return response.data;
  },
};

export const categoriesApi = {
  list: async () => {
    const response = await request.get('/categories/');
    return response.data as Category[];
  },

  detail: async (id: number) => {
    const response = await request.get(`/categories/${id}/`);
    return response.data as Category;
  },
};

export const tagsApi = {
  list: async () => {
    const response = await request.get('/tags/');
    return response.data as Tag[];
  },

  detail: async (id: number) => {
    const response = await request.get(`/tags/${id}/`);
    return response.data as Tag;
  },
};
