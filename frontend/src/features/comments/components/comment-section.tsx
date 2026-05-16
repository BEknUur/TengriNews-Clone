import { observer } from 'mobx-react-lite';
import { useState } from 'react';
import { toast } from 'sonner';

import { Button } from '@/common/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Textarea } from '@/common/components/ui/textarea';
import type { Comment } from '@/common/entities';
import { authStore } from '@/features/auth/stores/auth-store';
import { commentsStore } from '@/features/comments/stores/comments-store';
import { cn } from '@/common/lib/utils';

interface CommentSectionProps {
  articleId: number;
}

export const CommentSection = observer(({ articleId }: CommentSectionProps) => {
  const [commentContent, setCommentContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmitComment = async (e: React.FormEvent, parentId?: number) => {
    e.preventDefault();
    if (!commentContent.trim()) return;

    setIsSubmitting(true);
    try {
      await commentsStore.createComment({
        article: articleId,
        content: commentContent,
        parent: parentId ?? null,
      });
      setCommentContent('');
      toast.success(parentId ? 'Reply posted' : 'Comment posted');
    } catch {
      toast.error('Failed to post comment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (commentId: number) => {
    if (!window.confirm('Delete this comment?')) return;
    await commentsStore.deleteComment(commentId);
    toast.success('Comment deleted');
  };

  const rootComments = commentsStore.comments.filter(
    (comment) => !comment.parent && comment.article === articleId,
  );

  return (
    <Card className="mt-8">
      <CardHeader>
        <CardTitle className="text-lg">Comments</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {authStore.isLoggedIn() ? (
          <form onSubmit={(e) => void handleSubmitComment(e)} className="space-y-3">
            <Textarea
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              placeholder="Share your thoughts..."
              rows={3}
            />
            <Button type="submit" isLoading={isSubmitting} disabled={!commentContent.trim()}>
              Post comment
            </Button>
          </form>
        ) : (
          <p className="text-sm text-muted-foreground">Log in to join the discussion.</p>
        )}

        <div className="space-y-4">
          {rootComments.length === 0 ? (
            <p className="text-sm text-muted-foreground">No comments yet. Be the first!</p>
          ) : (
            rootComments.map((comment) => (
              <CommentItem
                key={comment.id}
                comment={comment}
                articleId={articleId}
                onDelete={handleDelete}
              />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
});

CommentSection.displayName = 'CommentSection';

interface CommentItemProps {
  comment: Comment;
  articleId: number;
  onDelete: (id: number) => void;
  isReply?: boolean;
}

const CommentItem = observer(({ comment, articleId, onDelete, isReply }: CommentItemProps) => {
  const [isReplying, setIsReplying] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const canDelete = authStore.user?.id === comment.user?.id;

  const handleReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyContent.trim()) return;

    setIsSubmitting(true);
    try {
      await commentsStore.createComment({
        article: articleId,
        content: replyContent,
        parent: comment.id,
      });
      setReplyContent('');
      setIsReplying(false);
      toast.success('Reply posted');
    } catch {
      toast.error('Failed to post reply');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-muted/30 p-4',
        isReply && 'ml-6 border-l-2 border-l-primary/40',
      )}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold">{comment.user?.first_name ?? 'Anonymous'}</p>
          <p className="text-xs text-muted-foreground">
            {new Date(comment.created_at).toLocaleDateString()}
          </p>
        </div>
        {canDelete ? (
          <Button variant="ghost" size="sm" className="text-destructive" onClick={() => void onDelete(comment.id)}>
            Delete
          </Button>
        ) : null}
      </div>

      <p className="text-sm leading-relaxed">{comment.content}</p>

      {authStore.isLoggedIn() ? (
        <Button variant="link" size="sm" className="mt-2 h-auto p-0" onClick={() => setIsReplying(!isReplying)}>
          {isReplying ? 'Cancel' : 'Reply'}
        </Button>
      ) : null}

      {isReplying ? (
        <form onSubmit={(e) => void handleReply(e)} className="mt-3 space-y-2">
          <Textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            placeholder="Write a reply..."
            rows={2}
          />
          <div className="flex gap-2">
            <Button type="submit" size="sm" isLoading={isSubmitting} disabled={!replyContent.trim()}>
              Reply
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsReplying(false)}>
              Cancel
            </Button>
          </div>
        </form>
      ) : null}

      {comment.replies?.map((reply) => (
        <CommentItem
          key={reply.id}
          comment={reply}
          articleId={articleId}
          onDelete={onDelete}
          isReply
        />
      ))}
    </div>
  );
});
