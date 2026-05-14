import { Link } from 'react-router-dom'
import { Eye, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import type { ArticleListItem } from '@/entities/article/model/types'

interface ArticleCardProps {
  article: ArticleListItem
}

export function ArticleCard({ article }: ArticleCardProps) {
  const authorName =
    `${article.author.first_name} ${article.author.last_name}`.trim() ||
    article.author.email

  const date = article.published_at
    ? new Date(article.published_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : null

  return (
    <Card className="group hover:shadow-md transition-shadow h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          {article.category && (
            <Badge variant="secondary" className="text-xs shrink-0">
              {article.category.name}
            </Badge>
          )}
        </div>
        <Link to={`/articles/${article.id}`}>
          <h2 className="text-base font-semibold leading-snug group-hover:underline line-clamp-2 mt-1">
            {article.title}
          </h2>
        </Link>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col justify-between gap-3">
        {article.excerpt && (
          <p className="text-sm text-muted-foreground line-clamp-3">{article.excerpt}</p>
        )}

        {article.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {article.tags.slice(0, 3).map((tag) => (
              <Badge key={tag.id} variant="outline" className="text-xs">
                #{tag.name}
              </Badge>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-muted-foreground pt-1 border-t border-border">
          <span className="font-medium">{authorName}</span>
          <div className="flex items-center gap-3">
            {date && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {date}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Eye className="h-3 w-3" />
              {article.view_count}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
