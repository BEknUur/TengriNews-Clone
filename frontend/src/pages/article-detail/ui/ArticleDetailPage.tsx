import { useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Eye, Clock } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Separator } from '@/shared/ui/separator'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui/avatar'
import { useArticle } from '@/entities/article/model/queries'
import { incrementView } from '@/entities/article/api/articleApi'
import { BookmarkButton } from '@/features/bookmark/ui/BookmarkButton'
import { ReactionBar } from '@/features/reaction/ui/ReactionBar'
import { CommentList } from '@/features/comment/ui/CommentList'
import { CommentForm } from '@/features/comment/ui/CommentForm'
import { Loader2 } from 'lucide-react'
import { isAuthenticated } from '@/features/auth/model/useAuth'

export function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const articleId = Number(id)
  const { data: article, isLoading, isError } = useArticle(articleId)

  useEffect(() => {
    if (articleId) {
      incrementView(articleId).catch(() => null)
    }
  }, [articleId])

  if (isLoading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (isError || !article) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-muted-foreground">Article not found.</p>
        <Button variant="ghost" size="sm" className="mt-4" asChild>
          <Link to="/">Back to home</Link>
        </Button>
      </div>
    )
  }

  const authorName =
    `${article.author.first_name} ${article.author.last_name}`.trim() ||
    article.author.email

  const date = article.published_at
    ? new Date(article.published_at).toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      })
    : null

  // Placeholder bookmark state (ideally tracked via bookmarks endpoint)
  const isBookmarked = false

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Back */}
      <Button variant="ghost" size="sm" className="mb-6 -ml-2" asChild>
        <Link to="/">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Link>
      </Button>

      {/* Category + tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {article.category && (
          <Badge variant="secondary">{article.category.name}</Badge>
        )}
        {article.tags.map((tag) => (
          <Badge key={tag.id} variant="outline">#{tag.name}</Badge>
        ))}
      </div>

      {/* Title */}
      <h1 className="text-3xl font-bold tracking-tight leading-tight mb-4">
        {article.title}
      </h1>

      {/* Meta */}
      <div className="flex items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <Avatar className="h-9 w-9">
            {article.author.avatar && <AvatarImage src={article.author.avatar} />}
            <AvatarFallback className="text-xs">
              {article.author.first_name[0]}{article.author.last_name[0]}
            </AvatarFallback>
          </Avatar>
          <div>
            <p className="text-sm font-medium">{authorName}</p>
            {date && (
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {date}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground flex items-center gap-1">
            <Eye className="h-4 w-4" />
            {article.view_count}
          </span>
          <BookmarkButton articleId={article.id} isBookmarked={isBookmarked} />
        </div>
      </div>

      <Separator className="mb-6" />

      {/* Content */}
      <div className="prose prose-sm max-w-none text-foreground leading-relaxed whitespace-pre-wrap mb-8">
        {article.content}
      </div>

      <Separator className="mb-6" />

      {/* Reactions */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold mb-3">Reactions</h3>
        <ReactionBar articleId={article.id} reactions={article.reactions} />
      </div>

      <Separator className="mb-6" />

      {/* Comments */}
      <div>
        <h3 className="text-sm font-semibold mb-4">
          Comments ({article.comments.filter((c) => !c.parent).length})
        </h3>

        {isAuthenticated() && (
          <div className="mb-6">
            <CommentForm articleId={article.id} />
          </div>
        )}

        <CommentList comments={article.comments} articleId={article.id} />
      </div>
    </div>
  )
}
