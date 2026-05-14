import { apiClient } from '@/shared/api/client'
import type { Category } from '../model/types'

export const getCategories = () =>
  apiClient.get<Category[]>('/categories/').then((r) => r.data)
