import { useQuery } from '@tanstack/react-query'
import { getCurrentUser } from '../api/userApi'
import { getToken } from '@/shared/lib/token'

export const useCurrentUser = () =>
  useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
    enabled: !!getToken(),
    retry: false,
  })
