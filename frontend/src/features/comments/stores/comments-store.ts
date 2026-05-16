import { makeAutoObservable } from 'mobx';
import type { Comment } from '@/common/entities';
import { commentsApi } from '@/features/comments/data/comments-api';

export class CommentsStore {
  comments: Comment[] = [];
  currentArticleId: number | null = null;
  isLoading = false;
  isCreating = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
  }

  async fetchComments(articleId: number) {
    this.currentArticleId = articleId;
    this.isLoading = true;
    this.error = null;
    try {
      const comments = await commentsApi.list(articleId);
      this.comments = comments.filter((comment) => comment.article === articleId);
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load comments';
    } finally {
      this.isLoading = false;
    }
  }

  async createComment(data: { article: number; content: string; parent?: number | null }) {
    this.isCreating = true;
    this.error = null;
    try {
      const newComment = await commentsApi.create(data);
      this.comments.push(newComment);
      return newComment;
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to create comment';
      throw error;
    } finally {
      this.isCreating = false;
    }
  }

  async deleteComment(id: number) {
    this.error = null;
    try {
      await commentsApi.delete(id);
      this.comments = this.comments.filter((c) => c.id !== id);
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to delete comment';
    }
  }

  clearComments() {
    this.comments = [];
    this.currentArticleId = null;
  }

  clearError() {
    this.error = null;
  }
}

export const commentsStore = new CommentsStore();
