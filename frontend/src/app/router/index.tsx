import { Routes, Route, Navigate } from 'react-router-dom'
import { HomePage } from '@/pages/home/ui/HomePage'
import { ArticleDetailPage } from '@/pages/article-detail/ui/ArticleDetailPage'
import { LoginPage } from '@/pages/login/ui/LoginPage'
import { RegisterPage } from '@/pages/register/ui/RegisterPage'
import { BookmarksPage } from '@/pages/bookmarks/ui/BookmarksPage'
import { getToken } from '@/shared/lib/token'
import type { ReactNode } from 'react'

function ProtectedRoute({ children }: { children: ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />
  return <>{children}</>
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/articles/:id" element={<ArticleDetailPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/bookmarks"
        element={
          <ProtectedRoute>
            <BookmarksPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
