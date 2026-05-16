import type { Article } from './article';

export interface Bookmark {
  id: number;
  user: number;
  article: Article | number;
  created_at: string;
}

export interface BookmarkCreate {
  article: number;
}
