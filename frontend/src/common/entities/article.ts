import type { Category } from './category';
import type { Comment } from './comment';
import type { Tag } from './tag';
import type { User } from './user';

export type ArticleStatus = 'published' | 'draft' | 'archived';

export interface Article {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  author: User;
  category?: Category | null;
  tags: Tag[];
  is_published: boolean;
  published_at?: string | null;
  view_count: number;
  created_at: string;
  updated_at?: string;
}

export interface ArticleListItem extends Omit<Article, 'content'> {}

export interface ArticleDetail extends Article {
  comments?: Comment[];
  reactions_count?: Record<string, number>;
}
