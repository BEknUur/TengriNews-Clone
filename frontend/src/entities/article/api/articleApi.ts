import { apiClient } from '@/shared/api/client'
import type { ArticleDetail, ArticleFilters, ArticleListItem, PaginatedResponse } from '../model/types'

export const getArticles = (filters?: ArticleFilters) =>
  apiClient
    .get<PaginatedResponse<ArticleListItem>>('/articles/', { params: filters })
    .then((r) => r.data)

export const getArticle = (id: number) =>
  apiClient.get<ArticleDetail>(`/articles/${id}/`).then((r) => r.data)

export const incrementView = (id: number) =>
  apiClient.post(`/articles/${id}/view/`)

export const bookmarkArticle = (id: number) =>
  apiClient.post(`/articles/${id}/bookmark/`)

export const unbookmarkArticle = (id: number) =>
  apiClient.delete(`/articles/${id}/bookmark/`)

export const reactToArticle = (id: number, type: string) =>
  apiClient.post(`/articles/${id}/reactions/`, { type })

export const addComment = (id: number, content: string, parent?: number) =>
  apiClient.post(`/articles/${id}/comments/`, { content, parent })
