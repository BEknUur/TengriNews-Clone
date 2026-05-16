import { makeAutoObservable } from 'mobx';
import type { Article, ArticleListItem, Category, Tag, PaginationParams } from '@/common/entities';
import { getApiErrorMessage } from '@/common/utils/api-error';
import { articlesApi, categoriesApi, tagsApi } from '@/features/articles/data/articles-api';

export class ArticlesStore {
  articles: ArticleListItem[] = [];
  currentArticle: Article | null = null;
  categories: Category[] = [];
  tags: Tag[] = [];

  isLoading = false;
  isLoadingDetail = false;
  error: string | null = null;

  // Pagination
  totalCount = 0;
  currentPage = 1;
  pageSize = 12;

  // Filters
  selectedCategory: number | null = null;
  selectedTags: number[] = [];
  searchQuery = '';

  constructor() {
    makeAutoObservable(this);
  }

  async fetchArticles(params?: PaginationParams) {
    this.isLoading = true;
    this.error = null;
    try {
      const filterParams = {
        ...params,
        page_size: this.pageSize,
        search: this.searchQuery || undefined,
        category: this.selectedCategory || undefined,
      };
      const result = await articlesApi.list(filterParams);
      this.articles = result.results;
      this.totalCount = result.count;
    } catch (error) {
      this.error = getApiErrorMessage(error, 'Failed to load articles');
    } finally {
      this.isLoading = false;
    }
  }

  async fetchArticleDetail(id: number | string) {
    this.isLoadingDetail = true;
    this.error = null;
    try {
      this.currentArticle = await articlesApi.detail(id);
    } catch (error) {
      this.error = getApiErrorMessage(error, 'Failed to load article');
    } finally {
      this.isLoadingDetail = false;
    }
  }

  async fetchCategories() {
    try {
      this.categories = await categoriesApi.list();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load categories';
    }
  }

  async fetchTags() {
    try {
      this.tags = await tagsApi.list();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load tags';
    }
  }

  setSelectedCategory(categoryId: number | null) {
    this.selectedCategory = categoryId;
    this.currentPage = 1;
  }

  setSelectedTags(tagIds: number[]) {
    this.selectedTags = tagIds;
    this.currentPage = 1;
  }

  setSearchQuery(query: string) {
    this.searchQuery = query;
    this.currentPage = 1;
  }

  setCurrentPage(page: number) {
    this.currentPage = page;
  }

  clearCurrentArticle() {
    this.currentArticle = null;
  }

  clearError() {
    this.error = null;
  }
}

export const articlesStore = new ArticlesStore();
