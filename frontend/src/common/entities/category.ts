export interface Category {
  id: number;
  name: string;
  slug: string;
  parent?: number | null;
  children?: Category[];
  created_at: string;
  updated_at: string;
}
