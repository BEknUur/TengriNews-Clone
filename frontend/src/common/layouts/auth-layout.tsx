import { Link, Outlet } from 'react-router-dom';

import { ROUTES } from '@/common/constants';

export const AuthLayout = () => {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden overflow-hidden bg-primary lg:block">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,oklch(0.65_0.18_252),transparent_50%),radial-gradient(circle_at_80%_80%,oklch(0.55_0.12_200),transparent_45%)]" />
        <div className="relative flex h-full flex-col justify-between p-10 text-primary-foreground">
          <Link to={ROUTES.HOME} className="flex items-center gap-2 text-lg font-bold">
            <span className="flex size-10 items-center justify-center rounded-lg bg-white/15 backdrop-blur">
              TN
            </span>
            TengriNews
          </Link>
          <div className="max-w-md space-y-4">
            <p className="text-3xl font-bold leading-tight">News that matters, delivered clearly.</p>
            <p className="text-sm leading-relaxed text-primary-foreground/80">
              Read the latest stories, save bookmarks, and join the conversation.
            </p>
          </div>
          <p className="text-xs text-primary-foreground/60">© TengriNews</p>
        </div>
      </div>

      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-[400px]">
          <Outlet />
        </div>
      </div>
    </div>
  );
};
