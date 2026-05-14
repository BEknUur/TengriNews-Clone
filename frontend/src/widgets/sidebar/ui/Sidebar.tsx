import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Separator } from '@/shared/ui/separator'
import { useCategories } from '@/entities/category/model/queries'
import { useTags } from '@/entities/tag/model/queries'
import { cn } from '@/shared/lib/cn'

export function Sidebar() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const activeCategory = params.get('category')
  const activeTag = params.get('tags')

  const { data: categories } = useCategories()
  const { data: tags } = useTags()

  const setFilter = (key: string, value: string | null) => {
    const p = new URLSearchParams(params)
    if (value) {
      p.set(key, value)
    } else {
      p.delete(key)
    }
    p.delete('page')
    navigate(`/?${p.toString()}`)
  }

  return (
    <aside className="space-y-5">
      {/* Categories */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
          Categories
        </h3>
        <div className="space-y-1">
          <Button
            variant="ghost"
            size="sm"
            className={cn('w-full justify-start', !activeCategory && 'bg-accent')}
            onClick={() => setFilter('category', null)}
          >
            All
          </Button>
          {categories?.map((cat) => (
            <Button
              key={cat.id}
              variant="ghost"
              size="sm"
              className={cn(
                'w-full justify-start',
                activeCategory === String(cat.id) && 'bg-accent font-medium'
              )}
              onClick={() => setFilter('category', String(cat.id))}
            >
              {cat.name}
            </Button>
          ))}
        </div>
      </div>

      <Separator />

      {/* Tags */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
          Tags
        </h3>
        <div className="flex flex-wrap gap-2">
          {tags?.map((tag) => (
            <Badge
              key={tag.id}
              variant={activeTag === String(tag.id) ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() =>
                setFilter('tags', activeTag === String(tag.id) ? null : String(tag.id))
              }
            >
              #{tag.name}
            </Badge>
          ))}
        </div>
      </div>
    </aside>
  )
}
