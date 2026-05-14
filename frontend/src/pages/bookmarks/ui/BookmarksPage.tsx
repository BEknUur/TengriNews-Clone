import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/client'
import { ArticleCard } from '@/widgets/article-card/ui/ArticleCard'
import type { ArticleListItem } from '@/entities/article/model/types'
import { Loader2 } from 'lucide-react'
import { Button } from '@/shared/ui/button'

interface BookmarkItem {
  id: number
  article: ArticleListItem
  created_at: string
}

const useBookmarks = () =>
  useQuery({
    queryKey: ['bookmarks'],
    queryFn: () =>
      apiClient
        .get<BookmarkItem[]>('/bookmarks/')
        .then((r) => r.data),
  })

export function BookmarksPage() {
  const { data, isLoading, isError } = useBookmarks()

  if (isLoading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-muted-foreground">Failed to load bookmarks.</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Bookmarks</h1>
        <Button variant="ghost" size="sm" asChild>
          <Link to="/">Browse articles</Link>
        </Button>
      </div>

      {!data || data.length === 0 ? (
        <div className="py-16 text-center">
          <p className="text-muted-foreground">No bookmarks yet.</p>
          <Button variant="outline" size="sm" className="mt-4" asChild>
            <Link to="/">Explore articles</Link>
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((item) => (
            <ArticleCard key={item.id} article={item.article} />
          ))}
        </div>
      )}
    </div>
  )
}
