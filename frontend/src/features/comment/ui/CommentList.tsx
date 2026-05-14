import { useState } from 'react'
import type { Comment } from '@/entities/article/model/types'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui/avatar'
import { Button } from '@/shared/ui/button'
import { CommentForm } from './CommentForm'

interface CommentItemProps {
  comment: Comment
  articleId: number
  depth?: number
}

function CommentItem({ comment, articleId, depth = 0 }: CommentItemProps) {
  const [showReply, setShowReply] = useState(false)
  const initials = comment.user
    ? `${comment.user.first_name[0] ?? ''}${comment.user.last_name[0] ?? ''}`
    : '?'

  return (
    <div className={depth > 0 ? 'ml-8 border-l border-border pl-4' : ''}>
      <div className="flex gap-3 py-3">
        <Avatar className="h-8 w-8 shrink-0">
          {comment.user?.avatar && <AvatarImage src={comment.user.avatar} />}
          <AvatarFallback className="text-xs">{initials}</AvatarFallback>
        </Avatar>
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">
              {comment.user
                ? `${comment.user.first_name} ${comment.user.last_name}`.trim() || comment.user.email
                : 'Anonymous'}
            </span>
            <span className="text-xs text-muted-foreground">
              {new Date(comment.created_at).toLocaleDateString()}
            </span>
          </div>
          <p className="text-sm leading-relaxed">{comment.content}</p>
          {depth === 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs text-muted-foreground"
              onClick={() => setShowReply(!showReply)}
            >
              Reply
            </Button>
          )}
          {showReply && (
            <div className="mt-2">
              <CommentForm
                articleId={articleId}
                parentId={comment.id}
                onSuccess={() => setShowReply(false)}
              />
            </div>
          )}
        </div>
      </div>

      {comment.replies?.map((reply) => (
        <CommentItem key={reply.id} comment={reply} articleId={articleId} depth={depth + 1} />
      ))}
    </div>
  )
}

interface CommentListProps {
  comments: Comment[]
  articleId: number
}

export function CommentList({ comments, articleId }: CommentListProps) {
  if (comments.length === 0) {
    return <p className="text-sm text-muted-foreground py-4">No comments yet. Be the first!</p>
  }

  return (
    <div className="divide-y divide-border">
      {comments
        .filter((c) => !c.parent)
        .map((comment) => (
          <CommentItem key={comment.id} comment={comment} articleId={articleId} />
        ))}
    </div>
  )
}
