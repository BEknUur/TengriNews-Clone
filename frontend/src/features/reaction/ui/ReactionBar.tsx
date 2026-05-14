import { ThumbsUp, ThumbsDown, Heart, Smile } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import type { Reaction } from '@/entities/article/model/types'
import { useReactToArticle } from '../model/useReaction'
import { isAuthenticated } from '@/features/auth/model/useAuth'
import { useNavigate } from 'react-router-dom'

interface ReactionBarProps {
  articleId: number
  reactions: Reaction[]
}

const REACTIONS = [
  { type: 'like' as const, icon: ThumbsUp, label: 'Like' },
  { type: 'dislike' as const, icon: ThumbsDown, label: 'Dislike' },
  { type: 'love' as const, icon: Heart, label: 'Love' },
  { type: 'laugh' as const, icon: Smile, label: 'Laugh' },
]

export function ReactionBar({ articleId, reactions }: ReactionBarProps) {
  const navigate = useNavigate()
  const react = useReactToArticle(articleId)

  const countByType = (type: string) =>
    reactions.filter((r) => r.type === type).length

  const handleClick = (type: 'like' | 'dislike' | 'love' | 'laugh') => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }
    react.mutate(type)
  }

  return (
    <div className="flex items-center gap-2">
      {REACTIONS.map(({ type, icon: Icon, label }) => (
        <Button
          key={type}
          variant="outline"
          size="sm"
          className="gap-1.5"
          onClick={() => handleClick(type)}
          disabled={react.isPending}
        >
          <Icon className="h-4 w-4" />
          <span className="text-xs">{countByType(type)}</span>
          <span className="sr-only">{label}</span>
        </Button>
      ))}
    </div>
  )
}
