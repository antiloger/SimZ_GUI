export interface RunList {
  id: string;
  name: string;
}

export interface EventListData {
  data: [];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  columns: [];
}

export interface EventListParams {
  page: number;
  page_size: number;
  sort_column?: string;
  sort_direction?: string;
  search_query?: string;
  search_columns?: string[];
  filter_conditions?: { [key: string]: any },
  include_columns: string[];
}
