import { Bookmark } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { cn } from '@/shared/lib/cn'
import { useToggleBookmark } from '../model/useBookmark'
import { isAuthenticated } from '@/features/auth/model/useAuth'
import { useNavigate } from 'react-router-dom'

interface BookmarkButtonProps {
  articleId: number
  isBookmarked: boolean
  className?: string
}

export function BookmarkButton({ articleId, isBookmarked, className }: BookmarkButtonProps) {
  const navigate = useNavigate()
  const toggle = useToggleBookmark(articleId)

  const handleClick = () => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }
    toggle.mutate(isBookmarked)
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      className={cn(className)}
      onClick={handleClick}
      disabled={toggle.isPending}
    >
      <Bookmark
        className={cn('h-5 w-5', isBookmarked ? 'fill-foreground' : '')}
      />
    </Button>
  )
}
