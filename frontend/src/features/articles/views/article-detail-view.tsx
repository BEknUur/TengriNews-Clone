import { observer } from 'mobx-react-lite';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { ArticleDetail } from '@/features/articles/components/article-detail';
import { articlesStore } from '@/features/articles/stores/articles-store';
import { CommentSection } from '@/features/comments/components/comment-section';
import { commentsStore } from '@/features/comments/stores/comments-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Loader } from '@/common/components/ui/loader';

export const ArticleDetailView = observer(() => {
  const { id } = useParams<{ id: string }>();

  useEffect(() => {
    if (id) {
      void articlesStore.fetchArticleDetail(id);
      void commentsStore.fetchComments(Number(id));
    }
  }, [id]);

  if (articlesStore.isLoadingDetail) {
    return (
      <div className="flex justify-center py-20">
        <Loader />
      </div>
    );
  }

  if (articlesStore.error) {
    return (
      <Card className="border-destructive/30 bg-destructive/5">
        <CardContent className="pt-6 text-sm text-destructive">{articlesStore.error}</CardContent>
      </Card>
    );
  }

  if (!articlesStore.currentArticle) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">Article not found</CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
      <div className="space-y-6 lg:col-span-2">
        <ArticleDetail article={articlesStore.currentArticle} />
        <CommentSection articleId={articlesStore.currentArticle.id} />
      </div>

      <aside>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Related</CardTitle>
            <CardDescription>More stories coming soon</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Related articles will appear here based on category and tags.
            </p>
          </CardContent>
        </Card>
      </aside>
    </div>
  );
});

ArticleDetailView.displayName = 'ArticleDetailView';
