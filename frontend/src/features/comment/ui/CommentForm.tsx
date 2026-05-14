import { useState } from 'react'
import { Button } from '@/shared/ui/button'
import { useAddComment } from '../model/useComments'
import { isAuthenticated } from '@/features/auth/model/useAuth'
import { useNavigate } from 'react-router-dom'

interface CommentFormProps {
  articleId: number
  parentId?: number
  onSuccess?: () => void
}

export function CommentForm({ articleId, parentId, onSuccess }: CommentFormProps) {
  const [text, setText] = useState('')
  const navigate = useNavigate()
  const addComment = useAddComment(articleId)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }
    addComment.mutate(
      { content: text, parent: parentId },
      {
        onSuccess: () => {
          setText('')
          onSuccess?.()
        },
      }
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={parentId ? 'Write a reply…' : 'Write a comment…'}
        rows={3}
        className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      />
      <Button type="submit" size="sm" disabled={addComment.isPending || !text.trim()}>
        {addComment.isPending ? 'Posting…' : 'Post'}
      </Button>
    </form>
  )
}
