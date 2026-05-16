import { observer } from 'mobx-react-lite';
import { useEffect } from 'react';
import { Bookmark } from 'lucide-react';

import { ArticleCard } from '@/features/articles/components/article-card';
import { bookmarksStore } from '@/features/bookmarks/stores/bookmarks-store';
import { Card, CardContent } from '@/common/components/ui/card';
import { Loader } from '@/common/components/ui/loader';

export const BookmarksView = observer(() => {
  useEffect(() => {
    void bookmarksStore.fetchBookmarks();
  }, []);

  if (bookmarksStore.isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="space-y-1 border-b border-border pb-6">
        <h1 className="flex items-center gap-2 text-3xl font-bold tracking-tight">
          <Bookmark className="size-7 text-primary" />
          My bookmarks
        </h1>
        <p className="text-muted-foreground">Articles you saved for later</p>
      </div>

      {bookmarksStore.error ? (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardContent className="pt-6 text-sm text-destructive">{bookmarksStore.error}</CardContent>
        </Card>
      ) : null}

      {bookmarksStore.bookmarks.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            You haven&apos;t bookmarked any articles yet.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {bookmarksStore.bookmarks.map((bookmark) => (
            <ArticleCard
              key={bookmark.id}
              article={typeof bookmark.article === 'object' ? bookmark.article : null}
            />
          ))}
        </div>
      )}
    </div>
  );
});

BookmarksView.displayName = 'BookmarksView';
