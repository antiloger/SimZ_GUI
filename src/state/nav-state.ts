import { create } from "zustand";

type NavProjectState = {
  btn: string[];
  selectedBtn: string;
  setSelectedBtn: (s_name: string) => void,
  add: (s_name: string) => Promise<void>;
  remove: (s_name: string) => Promise<void>; // Remove by specific name
}

export const useNavProjectState = create<NavProjectState>((set) => ({
  btn: ["Overview", "Settings"],
  selectedBtn: "Overview",
  setSelectedBtn: (s_name: string) => {
    set(() => ({
      selectedBtn: s_name,
    }))
  },
  add: async (s_name: string) => {
    set((state) => ({
      btn: [s_name, ...state.btn] // Create a new array with the new item
    }));
  },
  remove: async (s_name: string) => {
    set((state) => ({
      btn: state.btn.filter((item) => item !== s_name) // Filter out the specific item
    }));
  }
}));

// const project_category = {
//   "test": ["Simulation", "Analysis", "Input/Output", "Settings"],
//   "static": ["Simulation", "Analysis", "Input/Output", "Settings"],
// }


type ProjectOptState = {
  cat: string[];
  selectedBtn: string;
  setSelectedBtn: (s_name: string) => void,
  add: (s_name: string[]) => Promise<void>;
}


export const useProjectOptState = create<ProjectOptState>((set) => ({
  cat: ["Simulation", "Analysis", "Input/Output", "Settings"],
  selectedBtn: "Simulation",
  setSelectedBtn: (s_name: string) => {
    set(() => ({
      selectedBtn: s_name,
    }))
  },
  add: async (s_name: string[]) => {
    set(() => ({
      cat: s_name // Create a new array with the new item
    }));
  },
}));
