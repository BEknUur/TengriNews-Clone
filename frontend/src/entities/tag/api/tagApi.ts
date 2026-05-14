import { apiClient } from '@/shared/api/client'
import type { Tag } from '../model/types'

export const getTags = () =>
  apiClient.get<Tag[]>('/tags/').then((r) => r.data)
