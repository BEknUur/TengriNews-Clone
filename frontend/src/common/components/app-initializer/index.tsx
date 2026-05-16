import { useEffect } from 'react';
import { observer } from 'mobx-react-lite';
import { articlesStore } from '@/features/articles/stores/articles-store';
import { bookmarksStore } from '@/features/bookmarks/stores/bookmarks-store';
import { authStore } from '@/features/auth/stores/auth-store';
import { authApi } from '@/features/auth/data/auth-api';

export const AppInitializer = observer(() => {
  useEffect(() => {
    const bootstrap = async () => {
      await Promise.all([articlesStore.fetchCategories(), articlesStore.fetchTags()]);

      if (!authStore.isLoggedIn()) {
        return;
      }

      try {
        const user = await authApi.getCurrentUser();
        authStore.setUser(user);
        await bookmarksStore.fetchBookmarks();
      } catch {
        authStore.clearAuth();
      }
    };

    void bootstrap();
  }, []);

  return null;
});

AppInitializer.displayName = 'AppInitializer';
