import { observer } from 'mobx-react-lite';
import { formatDistanceToNow } from 'date-fns';
import { Bookmark, Eye } from 'lucide-react';
import { toast } from 'sonner';

import { Avatar, AvatarFallback } from '@/common/components/ui/avatar';
import { Badge } from '@/common/components/ui/badge';
import { Button } from '@/common/components/ui/button';
import { Separator } from '@/common/components/ui/separator';
import type { Article } from '@/common/entities';
import { authStore } from '@/features/auth/stores/auth-store';
import { bookmarksStore } from '@/features/bookmarks/stores/bookmarks-store';

interface ArticleDetailProps {
  article: Article;
}

export const ArticleDetail = observer(({ article }: ArticleDetailProps) => {
  const date = article.published_at
    ? formatDistanceToNow(new Date(article.published_at), { addSuffix: true })
    : null;
  const authorName = `${article.author.first_name} ${article.author.last_name}`;
  const initials = `${article.author.first_name[0] ?? ''}${article.author.last_name[0] ?? ''}`;
  const isBookmarked = bookmarksStore.isBookmarked(article.id);

  const handleBookmark = async () => {
    if (!authStore.isLoggedIn()) {
      toast.info('Please log in to bookmark articles');
      return;
    }

    try {
      if (isBookmarked) {
        await bookmarksStore.removeBookmark(article.id);
        toast.success('Removed from bookmarks');
      } else {
        await bookmarksStore.addBookmark(article.id);
        toast.success('Saved to bookmarks');
      }
    } catch {
      toast.error('Failed to update bookmark');
    }
  };

  return (
    <article className="space-y-6">
      <header className="space-y-4">
        {article.category ? (
          <Badge variant="blue">{article.category.name}</Badge>
        ) : null}

        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{article.title}</h1>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Avatar className="size-10">
              <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{authorName}</p>
              {date ? <p className="text-xs text-muted-foreground">{date}</p> : null}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
              <Eye className="size-4" />
              {article.view_count} views
            </span>
            <Button
              variant={isBookmarked ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => void handleBookmark()}
            >
              <Bookmark className={isBookmarked ? 'fill-current' : ''} />
              {isBookmarked ? 'Saved' : 'Bookmark'}
            </Button>
          </div>
        </div>
      </header>

      <Separator />

      <div className="prose prose-neutral max-w-none text-base leading-relaxed whitespace-pre-wrap text-foreground">
        {article.content}
      </div>

      {article.tags.length > 0 ? (
        <>
          <Separator />
          <div className="flex flex-wrap gap-2">
            {article.tags.map((tag) => (
              <Badge key={tag.id} variant="outline">
                #{tag.name}
              </Badge>
            ))}
          </div>
        </>
      ) : null}
    </article>
  );
});

ArticleDetail.displayName = 'ArticleDetail';
