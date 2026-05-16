export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  username?: string;
  role?: string;
  preferred_language?: string;
  avatar?: string | null;
}

export interface AuthTokens {
  access: string;
  refresh?: string;
}

export interface RegisterResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  tokens: AuthTokens;
}
