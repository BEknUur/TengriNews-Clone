import { makeAutoObservable } from 'mobx';
import type { Bookmark } from '@/common/entities';
import { bookmarksApi } from '@/features/bookmarks/data/bookmarks-api';

function getArticleId(bookmark: Bookmark): number {
  return typeof bookmark.article === 'object' ? bookmark.article.id : bookmark.article;
}

export class BookmarksStore {
  bookmarks: Bookmark[] = [];
  isLoading = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
  }

  async fetchBookmarks() {
    this.isLoading = true;
    this.error = null;
    try {
      this.bookmarks = await bookmarksApi.list();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load bookmarks';
    } finally {
      this.isLoading = false;
    }
  }

  async addBookmark(articleId: number) {
    this.error = null;
    try {
      const existing = this.bookmarks.find((bookmark) => getArticleId(bookmark) === articleId);
      if (existing) {
        return existing;
      }

      const newBookmark = await bookmarksApi.create(articleId);
      this.bookmarks.push(newBookmark);
      return newBookmark;
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to add bookmark';
      throw error;
    }
  }

  async removeBookmark(articleId: number) {
    const bookmark = this.bookmarks.find((item) => getArticleId(item) === articleId);
    if (!bookmark) {
      return;
    }

    this.error = null;
    try {
      await bookmarksApi.delete(articleId);
      this.bookmarks = this.bookmarks.filter((item) => item.id !== bookmark.id);
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to remove bookmark';
      throw error;
    }
  }

  isBookmarked(articleId: number): boolean {
    return this.bookmarks.some((bookmark) => getArticleId(bookmark) === articleId);
  }

  clearError() {
    this.error = null;
  }
}

export const bookmarksStore = new BookmarksStore();
