import { createBrowserRouter } from 'react-router-dom';
import { MainLayout } from '@/common/layouts/main-layout';
import { AuthLayout } from '@/common/layouts/auth-layout';
import { AuthGuardLayout } from '@/common/layouts/auth-guard-layout';
import { HomeView } from '@/features/articles/views/home-view';
import { ArticlesListView } from '@/features/articles/views/articles-list-view';
import { ArticleDetailView } from '@/features/articles/views/article-detail-view';
import { LoginView } from '@/features/auth/views/login-view';
import { RegisterView } from '@/features/auth/views/register-view';
import { ProfileView } from '@/features/articles/views/profile-view';
import { BookmarksView } from '@/features/bookmarks/views/bookmarks-view';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <HomeView />,
      },
      {
        path: 'articles',
        element: <ArticlesListView />,
      },
      {
        path: 'article/:id',
        element: <ArticleDetailView />,
      },
      {
        element: <AuthGuardLayout />,
        children: [
          {
            path: 'profile',
            element: <ProfileView />,
          },
          {
            path: 'bookmarks',
            element: <BookmarksView />,
          },
        ],
      },
    ],
  },
  {
    element: <AuthLayout />,
    children: [
      {
        path: 'auth/login',
        element: <LoginView />,
      },
      {
        path: 'auth/register',
        element: <RegisterView />,
      },
    ],
  },
]);
