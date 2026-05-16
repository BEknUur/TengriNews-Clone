import { Outlet, Navigate } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import { authStore } from '@/features/auth/stores/auth-store';

export const AuthGuardLayout = observer(() => {
  if (!authStore.isLoggedIn()) {
    return <Navigate to="/auth/login" replace />;
  }

  return <Outlet />;
});

AuthGuardLayout.displayName = 'AuthGuardLayout';
