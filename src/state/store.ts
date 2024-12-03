import { create } from "zustand";

type CounterStore = {
  count: number;
  increment: () => Promise<void>;
}

export const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: async () => {
    set((state) => ({ count: state.count + 1 }));
  },
}))
