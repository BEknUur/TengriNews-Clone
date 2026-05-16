export const ROUTES = {
  HOME: '/',
  ARTICLES: '/articles',
  ARTICLE_DETAIL: '/article/:id',
  SEARCH: '/search',
  CATEGORIES: '/categories/:id',
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
  },
  ACCOUNT: {
    PROFILE: '/profile',
    BOOKMARKS: '/bookmarks',
  },
};

export const REACTION_TYPES = {
  LIKE: 'like' as const,
  DISLIKE: 'dislike' as const,
  LOVE: 'love' as const,
  LAUGH: 'laugh' as const,
};

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 12,
  MIN_PAGE_SIZE: 6,
  MAX_PAGE_SIZE: 50,
};
