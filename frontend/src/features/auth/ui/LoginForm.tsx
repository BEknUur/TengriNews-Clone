import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { useLogin } from '../model/useAuth'

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(1, 'Password is required'),
})

type FormData = z.infer<typeof schema>

export function LoginForm() {
  const navigate = useNavigate()
  const login = useLogin()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = (data: FormData) => {
    login.mutate(data, {
      onSuccess: () => navigate('/'),
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm">
      <div className="space-y-1">
        <label className="text-sm font-medium">Email</label>
        <Input
          type="email"
          placeholder="you@example.com"
          {...register('email')}
        />
        {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium">Password</label>
        <Input
          type="password"
          placeholder="••••••••"
          {...register('password')}
        />
        {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
      </div>

      {login.error && (
        <p className="text-xs text-red-500">Invalid email or password</p>
      )}

      <Button type="submit" className="w-full" disabled={login.isPending}>
        {login.isPending ? 'Signing in…' : 'Sign in'}
      </Button>

      <p className="text-sm text-center text-muted-foreground">
        No account?{' '}
        <Link to="/register" className="underline text-foreground">
          Register
        </Link>
      </p>
    </form>
  )
}
