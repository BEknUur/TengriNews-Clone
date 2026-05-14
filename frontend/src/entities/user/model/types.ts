export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'ADMIN' | 'EDITOR' | 'USER'
  avatar: string | null
  date_joined: string
}
