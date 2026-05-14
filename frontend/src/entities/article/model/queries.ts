import { useQuery } from '@tanstack/react-query'
import { getArticles, getArticle } from '../api/articleApi'
import type { ArticleFilters, ArticleListItem, PaginatedResponse } from './types'

export const useArticles = (filters?: ArticleFilters) =>
  useQuery<PaginatedResponse<ArticleListItem>>({
    queryKey: ['articles', filters],
    queryFn: () => getArticles(filters),
  })

export const useArticle = (id: number) =>
  useQuery({
    queryKey: ['article', id],
    queryFn: () => getArticle(id),
    enabled: !!id,
  })
