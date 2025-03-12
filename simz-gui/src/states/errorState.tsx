import { create } from "zustand";

interface ErrorDisplayI {
  header: string;
  level?: string;
  body: string;
}

type ReactFlowErrorI = {
  error: string;
  errorType: string;
  type: "warning" | "error";
  componentId?: string;
  componentName?: string;
}

type ErrorStateT = {
  error: ErrorDisplayI | null,
  ReactFlowError: ReactFlowErrorI[]
  setError: (err: ErrorDisplayI) => void,
  clearError: () => void,
  addReactFlowError: (err: ReactFlowErrorI) => void,
  removeReactFlowError: (err: ReactFlowErrorI) => void,
  clearReactFlowError: () => void,
  getReactFlowErrorCount: () => number,
  getFlowErrorByErrorType: (errorType: string) => ReactFlowErrorI[],
  getAllFlowErrors: () => ReactFlowErrorI[],
}

export const ErrorState = create<ErrorStateT>((set, get) => ({
  error: null,
  ReactFlowError: [],
  setError: (err: ErrorDisplayI) => set({ error: err }),
  clearError: () => set({ error: null }),
  addReactFlowError: (err: ReactFlowErrorI) => set({ ReactFlowError: [err, ...get().ReactFlowError] }),
  removeReactFlowError: (err: ReactFlowErrorI) => set({ ReactFlowError: get().ReactFlowError.filter((e) => e !== err) }),
  clearReactFlowError: () => set({ ReactFlowError: [] }),
  getReactFlowErrorCount: () => get().ReactFlowError.length,
  getFlowErrorByErrorType: (errorType: string) => get().ReactFlowError.filter((e) => e.errorType === errorType),
  getAllFlowErrors: () => get().ReactFlowError,
}))

