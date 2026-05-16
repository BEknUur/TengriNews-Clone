import { observer } from 'mobx-react-lite';
import { useEffect, useState } from 'react';

import { ArticleCard } from '@/features/articles/components/article-card';
import { articlesStore } from '@/features/articles/stores/articles-store';
import { Button } from '@/common/components/ui/button';
import { Card, CardContent } from '@/common/components/ui/card';
import { Loader } from '@/common/components/ui/loader';
import { Skeleton } from '@/common/components/ui/skeleton';

export const HomeView = observer(() => {
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    void articlesStore.fetchArticles({ page: currentPage });
  }, [currentPage]);

  const totalPages = Math.max(1, Math.ceil(articlesStore.totalCount / articlesStore.pageSize));

  if (articlesStore.isLoading && articlesStore.articles.length === 0) {
    return (
      <div className="space-y-8">
        <PageHeader title="Latest news" description="Stay up to date with the newest stories" />
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-52 w-full" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader title="Latest news" description="Stay up to date with the newest stories" />

      {articlesStore.error ? (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardContent className="pt-6 text-sm text-destructive">{articlesStore.error}</CardContent>
        </Card>
      ) : null}

      {articlesStore.articles.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">No articles yet.</CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {articlesStore.articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}

      {totalPages > 1 ? (
        <div className="flex flex-wrap justify-center gap-2">
          {Array.from({ length: totalPages }).map((_, index) => {
            const page = index + 1;
            return (
              <Button
                key={page}
                variant={currentPage === page ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </Button>
            );
          })}
        </div>
      ) : null}

      {articlesStore.isLoading ? (
        <div className="flex justify-center py-4">
          <Loader size="sm" />
        </div>
      ) : null}
    </div>
  );
});

HomeView.displayName = 'HomeView';

function PageHeader({ title, description }: { title: string; description: string }) {
  return (
    <div className="space-y-1 border-b border-border pb-6">
      <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}
