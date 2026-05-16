import { Outlet } from 'react-router-dom';

import { Footer } from '@/common/components/footer';
import { Header } from '@/common/components/header';

export const MainLayout = () => {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};
