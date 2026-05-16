import type { User } from './user';

export interface Comment {
  id: number;
  article: number;
  user?: User | null;
  parent?: number | null;
  content: string;
  is_active: boolean;
  created_at: string;
  replies?: Comment[];
}

export interface CommentCreate {
  article: number;
  parent?: number | null;
  content: string;
}
