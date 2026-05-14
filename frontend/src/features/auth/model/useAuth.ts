import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/client'
import { getToken, removeToken, setToken } from '@/shared/lib/token'

interface LoginData {
  email: string
  password: string
}

interface RegisterData {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
}

interface AuthResponse {
  access: string
  refresh: string
}

export const useLogin = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: LoginData) =>
      apiClient.post<AuthResponse>('/accounts/auth/token/', data).then((r) => r.data),
    onSuccess: (data) => {
      setToken(data.access)
      void queryClient.invalidateQueries({ queryKey: ['currentUser'] })
    },
  })
}

export const useRegister = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: RegisterData) =>
      apiClient.post<AuthResponse>('/accounts/auth/register/', data).then((r) => r.data),
    onSuccess: (data) => {
      setToken(data.access)
      void queryClient.invalidateQueries({ queryKey: ['currentUser'] })
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  return () => {
    removeToken()
    queryClient.clear()
    window.location.href = '/'
  }
}

export const isAuthenticated = () => !!getToken()
