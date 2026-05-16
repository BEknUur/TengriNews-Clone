import { makeAutoObservable } from 'mobx';
import type { AuthTokens, User } from '@/common/entities';
import { setToken, removeToken, setUser, removeUser } from '@/common/lib';

export class AuthStore {
  token: string | null = null;
  user: User | null = null;
  isAuthenticated = false;
  isLoading = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
    this.loadFromStorage();
  }

  private loadFromStorage() {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('auth_user');

    if (token) {
      this.token = token;
      this.isAuthenticated = true;
    }

    if (user) {
      try {
        this.user = JSON.parse(user) as User;
      } catch {
        removeUser();
      }
    }
  }

  setTokens(tokens: AuthTokens) {
    this.token = tokens.access;
    this.isAuthenticated = true;
    this.error = null;
    setToken(tokens.access);

    if (tokens.refresh) {
      localStorage.setItem('auth_refresh', tokens.refresh);
    }
  }

  setUser(user: User) {
    this.user = user;
    setUser(user);
  }

  setAuth(tokens: AuthTokens, user: User) {
    this.setTokens(tokens);
    this.setUser(user);
  }

  clearAuth() {
    this.token = null;
    this.user = null;
    this.isAuthenticated = false;
    this.error = null;
    removeToken();
    removeUser();
    localStorage.removeItem('auth_refresh');
  }

  setError(error: string) {
    this.error = error;
  }

  setLoading(loading: boolean) {
    this.isLoading = loading;
  }

  getToken(): string | null {
    return this.token;
  }

  isLoggedIn(): boolean {
    return this.isAuthenticated && !!this.token;
  }
}

export const authStore = new AuthStore();
