import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { Eye } from 'lucide-react';

import { Badge } from '@/common/components/ui/badge';
import { Card, CardContent } from '@/common/components/ui/card';
import { ROUTES } from '@/common/constants';
import { cn } from '@/common/lib/utils';
import type { ArticleListItem } from '@/common/entities';

interface ArticleCardProps {
  article: ArticleListItem | null;
}

export const ArticleCard = ({ article }: ArticleCardProps) => {
  if (!article) return null;

  const date = article.published_at
    ? formatDistanceToNow(new Date(article.published_at), { addSuffix: true })
    : null;

  return (
    <Link
      to={ROUTES.ARTICLE_DETAIL.replace(':id', String(article.id))}
      className="group block h-full"
    >
      <Card
        className={cn(
          'h-full gap-0 overflow-hidden py-0 transition-all duration-200',
          'hover:border-primary/30 hover:shadow-md',
        )}
      >
        <div className="h-1 bg-gradient-to-r from-primary via-primary/70 to-chart-2 opacity-80 transition-opacity group-hover:opacity-100" />
        <CardContent className="flex flex-col gap-3 p-5">
          {article.category ? (
            <Badge variant="blue" className="w-fit">
              {article.category.name}
            </Badge>
          ) : null}

          <h3 className="line-clamp-2 text-lg font-semibold leading-snug transition-colors group-hover:text-primary">
            {article.title}
          </h3>

          <p className="line-clamp-2 text-sm text-muted-foreground">{article.excerpt}</p>

          <div className="mt-auto flex items-center justify-between pt-2 text-xs text-muted-foreground">
            <span>{date ?? 'Draft'}</span>
            <span className="inline-flex items-center gap-1">
              <Eye className="size-3.5" />
              {article.view_count}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};
