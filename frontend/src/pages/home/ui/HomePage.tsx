import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ArticleList } from '@/widgets/article-list/ui/ArticleList'
import { Sidebar } from '@/widgets/sidebar/ui/Sidebar'
import type { ArticleFilters } from '@/entities/article/model/types'
import { useDebounce } from '@/shared/hooks/useDebounce'

export function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1)

  const search = searchParams.get('search') ?? undefined
  const category = searchParams.get('category') ?? undefined
  const tags = searchParams.get('tags') ?? undefined

  const debouncedSearch = useDebounce(search)

  const filters: ArticleFilters = {
    search: debouncedSearch,
    category,
    tags,
    is_published: 'true',
  }

  // Reset page when filters change
  useEffect(() => {
    setPage(1)
  }, [search, category, tags])

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
    const p = new URLSearchParams(searchParams)
    p.set('page', String(newPage))
    setSearchParams(p)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex gap-8">
        {/* Sidebar */}
        <div className="hidden lg:block w-56 shrink-0">
          <Sidebar />
        </div>

        {/* Main content */}
        <main className="flex-1 min-w-0">
          {search && (
            <p className="text-sm text-muted-foreground mb-4">
              Results for: <span className="font-medium text-foreground">"{search}"</span>
            </p>
          )}
          <ArticleList filters={filters} page={page} onPageChange={handlePageChange} />
        </main>
      </div>
    </div>
  )
}
