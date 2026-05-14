import { Navigate } from 'react-router-dom'
import { LoginForm } from '@/features/auth/ui/LoginForm'
import { isAuthenticated } from '@/features/auth/model/useAuth'

export function LoginPage() {
  if (isAuthenticated()) return <Navigate to="/" replace />

  return (
    <div className="min-h-[calc(100vh-56px)] flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
          <p className="text-sm text-muted-foreground">Sign in to your account</p>
        </div>
        <LoginForm />
      </div>
    </div>
  )
}
