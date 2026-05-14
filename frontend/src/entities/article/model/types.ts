export interface Author {
  id: number
  email: string
  first_name: string
  last_name: string
  avatar: string | null
}

export interface Category {
  id: number
  name: string
  slug: string
  parent: number | null
}

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface CommentUser {
  id: number
  email: string
  first_name: string
  last_name: string
  avatar: string | null
}

export interface Comment {
  id: number
  article: number
  user: CommentUser | null
  parent: number | null
  content: string
  is_active: boolean
  created_at: string
  updated_at: string
  replies: Comment[]
}

export interface Reaction {
  id: number
  user: number
  article: number | null
  comment: number | null
  type: 'like' | 'dislike' | 'love' | 'laugh'
  created_at: string
}

export interface ArticleListItem {
  id: number
  title: string
  slug: string
  excerpt: string
  author: Author
  category: Category | null
  tags: Tag[]
  is_published: boolean
  published_at: string | null
  view_count: number
  created_at: string
}

export interface ArticleDetail extends ArticleListItem {
  content: string
  comments: Comment[]
  reactions: Reaction[]
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ArticleFilters {
  search?: string
  category?: string
  tags?: string
  author?: string
  page?: string
  ordering?: string
  is_published?: string
}
