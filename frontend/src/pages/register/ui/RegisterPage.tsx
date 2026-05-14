import { Navigate } from 'react-router-dom'
import { RegisterForm } from '@/features/auth/ui/RegisterForm'
import { isAuthenticated } from '@/features/auth/model/useAuth'

export function RegisterPage() {
  if (isAuthenticated()) return <Navigate to="/" replace />

  return (
    <div className="min-h-[calc(100vh-56px)] flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-bold tracking-tight">Create an account</h1>
          <p className="text-sm text-muted-foreground">Start reading and sharing news</p>
        </div>
        <RegisterForm />
      </div>
    </div>
  )
}
