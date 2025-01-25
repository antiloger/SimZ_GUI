import { create } from "zustand";

interface ErrorDisplayI {
  header: string;
  level?: string;
  body: string;
}

type ErrorStateT = {
  error: ErrorDisplayI | null,
  setError: (err: ErrorDisplayI) => void,
  clearError: () => void,
}

export const ErrorState = create<ErrorStateT>((set) => ({
  error: null,
  setError: (err: ErrorDisplayI) => set({ error: err }),
  clearError: () => set({ error: null })
}))

