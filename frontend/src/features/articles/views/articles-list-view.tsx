import { observer } from 'mobx-react-lite';
import { useEffect, useState } from 'react';

import { ArticleCard } from '@/features/articles/components/article-card';
import { articlesStore } from '@/features/articles/stores/articles-store';
import { Button } from '@/common/components/ui/button';
import { Card, CardContent } from '@/common/components/ui/card';
import { Loader } from '@/common/components/ui/loader';

export const ArticlesListView = observer(() => {
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    void articlesStore.fetchArticles({ page: currentPage });
  }, [currentPage]);

  const totalPages = Math.max(1, Math.ceil(articlesStore.totalCount / articlesStore.pageSize));

  if (articlesStore.isLoading && articlesStore.articles.length === 0) {
    return (
      <div className="space-y-8">
        <div className="space-y-1 border-b border-border pb-6">
          <h1 className="text-3xl font-bold tracking-tight">All articles</h1>
          <p className="text-muted-foreground">Browse the full archive</p>
        </div>
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="space-y-1 border-b border-border pb-6">
        <h1 className="text-3xl font-bold tracking-tight">All articles</h1>
        <p className="text-muted-foreground">Browse the full archive</p>
      </div>

      {articlesStore.error ? (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardContent className="pt-6 text-sm text-destructive">{articlesStore.error}</CardContent>
        </Card>
      ) : null}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {articlesStore.articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

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
    </div>
  );
});

ArticlesListView.displayName = 'ArticlesListView';
