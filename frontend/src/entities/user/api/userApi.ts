import { apiClient } from '@/shared/api/client'
import type { User } from '../model/types'

export const getCurrentUser = () =>
  apiClient.get<User>('/accounts/users/me/').then((r) => r.data)
