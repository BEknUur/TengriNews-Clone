import { Link, NavLink } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import { Bookmark, LogOut, User } from 'lucide-react';

import { Button } from '@/common/components/ui/button';
import { Separator } from '@/common/components/ui/separator';
import { ROUTES } from '@/common/constants';
import { cn } from '@/common/lib/utils';
import { authStore } from '@/features/auth/stores/auth-store';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    'text-sm font-medium transition-colors hover:text-primary',
    isActive ? 'text-primary' : 'text-muted-foreground',
  );

export const Header = observer(() => {
  const handleLogout = () => {
    authStore.clearAuth();
    window.location.assign(ROUTES.AUTH.LOGIN);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border/80 bg-background/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-6 px-4 sm:px-6">
        <Link to={ROUTES.HOME} className="group flex items-center gap-2">
          <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground shadow-sm">
            TN
          </span>
          <span className="text-lg font-bold tracking-tight group-hover:text-primary transition-colors">
            TengriNews
          </span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          <NavLink to={ROUTES.HOME} className={navLinkClass} end>
            Home
          </NavLink>
          <NavLink to={ROUTES.ARTICLES} className={navLinkClass}>
            Articles
          </NavLink>
        </nav>

        <div className="flex items-center gap-2">
          {authStore.isLoggedIn() ? (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to={ROUTES.ACCOUNT.BOOKMARKS}>
                  <Bookmark className="size-4" />
                  Bookmarks
                </Link>
              </Button>
              <Button variant="ghost" size="sm" asChild>
                <Link to={ROUTES.ACCOUNT.PROFILE}>
                  <User className="size-4" />
                  {authStore.user?.first_name}
                </Link>
              </Button>
              <Separator orientation="vertical" className="mx-1 hidden h-6 sm:block" />
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="size-4" />
                Logout
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to={ROUTES.AUTH.LOGIN}>Login</Link>
              </Button>
              <Button size="sm" asChild>
                <Link to={ROUTES.AUTH.REGISTER}>Register</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
});

Header.displayName = 'Header';
