import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Bookmark, LogOut, Menu, X } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui/avatar'
import { useCurrentUser } from '@/entities/user/model/queries'
import { useLogout, isAuthenticated } from '@/features/auth/model/useAuth'

export function Header() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const logout = useLogout()
  const { data: user } = useCurrentUser()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (search.trim()) {
      navigate(`/?search=${encodeURIComponent(search.trim())}`)
    }
  }

  const initials = user
    ? `${user.first_name[0] ?? ''}${user.last_name[0] ?? ''}`.toUpperCase()
    : ''

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-4">
        {/* Logo */}
        <Link to="/" className="font-bold text-lg tracking-tight shrink-0">
          TengriNews
        </Link>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex-1 max-w-md hidden sm:flex">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search articles…"
              className="pl-9 h-9"
            />
          </div>
        </form>

        <div className="ml-auto flex items-center gap-2">
          {isAuthenticated() ? (
            <>
              <Button variant="ghost" size="icon" asChild>
                <Link to="/bookmarks">
                  <Bookmark className="h-5 w-5" />
                </Link>
              </Button>
              <Avatar className="h-8 w-8 cursor-pointer">
                {user?.avatar && <AvatarImage src={user.avatar} />}
                <AvatarFallback className="text-xs">{initials}</AvatarFallback>
              </Avatar>
              <Button variant="ghost" size="icon" onClick={logout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/login">Sign in</Link>
              </Button>
              <Button size="sm" asChild>
                <Link to="/register">Register</Link>
              </Button>
            </>
          )}

          {/* Mobile menu toggle */}
          <Button
            variant="ghost"
            size="icon"
            className="sm:hidden"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile search */}
      {menuOpen && (
        <div className="sm:hidden px-4 pb-3">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search articles…"
                className="pl-9"
              />
            </div>
          </form>
        </div>
      )}
    </header>
  )
}
