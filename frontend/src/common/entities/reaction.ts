export type ReactionType = 'like' | 'dislike' | 'love' | 'laugh';

export interface Reaction {
  id: number;
  user: number;
  article?: number;
  comment?: number;
  type: ReactionType;
  created_at: string;
}

export interface ReactionCreate {
  type: ReactionType;
  article?: number;
  comment?: number;
}

export interface ReactionCount {
  like: number;
  dislike: number;
  love: number;
  laugh: number;
}
