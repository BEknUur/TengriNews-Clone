import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { useRegister } from '../model/useAuth'

const schema = z
  .object({
    first_name: z.string().min(1, 'First name is required'),
    last_name: z.string().min(1, 'Last name is required'),
    email: z.string().email('Invalid email'),
    password: z.string().min(6, 'At least 6 characters'),
    password_confirm: z.string().min(1, 'Please confirm your password'),
  })
  .refine((d) => d.password === d.password_confirm, {
    message: 'Passwords do not match',
    path: ['password_confirm'],
  })

type FormData = z.infer<typeof schema>

export function RegisterForm() {
  const navigate = useNavigate()
  const register_ = useRegister()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = (data: FormData) => {
    register_.mutate(data, {
      onSuccess: () => navigate('/'),
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className="text-sm font-medium">First name</label>
          <Input placeholder="John" {...register('first_name')} />
          {errors.first_name && (
            <p className="text-xs text-red-500">{errors.first_name.message}</p>
          )}
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium">Last name</label>
          <Input placeholder="Doe" {...register('last_name')} />
          {errors.last_name && (
            <p className="text-xs text-red-500">{errors.last_name.message}</p>
          )}
        </div>
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium">Email</label>
        <Input type="email" placeholder="you@example.com" {...register('email')} />
        {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium">Password</label>
        <Input type="password" placeholder="••••••••" {...register('password')} />
        {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium">Confirm password</label>
        <Input type="password" placeholder="••••••••" {...register('password_confirm')} />
        {errors.password_confirm && (
          <p className="text-xs text-red-500">{errors.password_confirm.message}</p>
        )}
      </div>

      {register_.error && (
        <p className="text-xs text-red-500">Registration failed. Try another email.</p>
      )}

      <Button type="submit" className="w-full" disabled={register_.isPending}>
        {register_.isPending ? 'Creating account…' : 'Create account'}
      </Button>

      <p className="text-sm text-center text-muted-foreground">
        Already have an account?{' '}
        <Link to="/login" className="underline text-foreground">
          Sign in
        </Link>
      </p>
    </form>
  )
}
