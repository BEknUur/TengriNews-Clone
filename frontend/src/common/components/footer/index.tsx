import { Link } from 'react-router-dom';

import { Separator } from '@/common/components/ui/separator';
import { ROUTES } from '@/common/constants';

export const Footer = () => {
  return (
    <footer className="mt-auto border-t border-border bg-card">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div>
            <p className="text-lg font-bold text-foreground">TengriNews</p>
            <p className="mt-2 text-sm text-muted-foreground">
              A modern news platform for staying informed.
            </p>
          </div>
          <div>
            <p className="text-sm font-semibold">Quick links</p>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to={ROUTES.HOME} className="hover:text-primary transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to={ROUTES.ARTICLES} className="hover:text-primary transition-colors">
                  Articles
                </Link>
              </li>
              <li>
                <Link to={ROUTES.AUTH.LOGIN} className="hover:text-primary transition-colors">
                  Login
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <p className="text-sm font-semibold">Contact</p>
            <p className="mt-3 text-sm text-muted-foreground">info@tengrinews.com</p>
          </div>
        </div>
        <Separator className="my-8" />
        <p className="text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} TengriNews. All rights reserved.
        </p>
      </div>
    </footer>
  );
};
