export interface ProjectRowList {
  projects: ProjectList[];
}

export interface ProjectList {
  name: string;
  description: string;
  created_at: string;
  runs_count: number;
}
