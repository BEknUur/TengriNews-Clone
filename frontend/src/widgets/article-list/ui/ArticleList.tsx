import { ArticleCard } from '@/widgets/article-card/ui/ArticleCard'
import { Button } from '@/shared/ui/button'
import { useArticles } from '@/entities/article/model/queries'
import type { ArticleFilters } from '@/entities/article/model/types'
import { Loader2 } from 'lucide-react'

const PAGE_SIZE = 20

interface ArticleListProps {
  filters?: ArticleFilters
  page: number
  onPageChange: (page: number) => void
}

export function ArticleList({ filters, page, onPageChange }: ArticleListProps) {
  const { data, isLoading, isError } = useArticles({ ...filters, page: String(page) })

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="py-16 text-center">
        <p className="text-muted-foreground">Failed to load articles.</p>
      </div>
    )
  }

  const articles = data?.results ?? []
  const totalPages = data?.count ? Math.ceil(data.count / PAGE_SIZE) : 1

  if (articles.length === 0) {
    return (
      <div className="py-16 text-center">
        <p className="text-muted-foreground">No articles found.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => onPageChange(page - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page === totalPages}
            onClick={() => onPageChange(page + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
