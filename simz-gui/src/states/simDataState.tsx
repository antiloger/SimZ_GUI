import api from "@/lib/axious"
import { CompDataI, CompRegStore } from "@/types/component"
import { create } from "zustand"
import { ErrorState } from "./errorState"

type SimDataStateT = {
  componentRegisterI: CompRegStore,
  componentData: { [id: string]: CompDataI },
  loadRegisterData: (projectId: string) => Promise<void>,
  loadCompData: (projectId: string) => Promise<void>,
}

export const SimDataState = create<SimDataStateT>((set) => ({
  componentRegisterI: {},
  componentData: {},
  loadRegisterData: async (projectId: string) => {
    const { setError } = ErrorState.getState();
    try {
      const res = await api.post<CompRegStore>(`/load-register-data`, { projectId: projectId });

      if (res.status != 200) {
        setError({
          header: "Register Component Data Not Found",
          body: "check the simulation server is working or config dir are chenging"
        })
        console.log("not a valid status")
        return
      }

      const registerData = res.data;
      set({ componentRegisterI: registerData });
    } catch (err) {
      setError({
        header: "Register Component Data Not Found",
        body: "check the simulation server is working or config dir are chenging"
      })
      console.log(`error from simdatastate: ${err}`)
    }
  },
  loadCompData: async (projectId: string) => {
    const { setError } = ErrorState();
    try {
      const res = await api.get<{ [id: string]: CompDataI }>(`/project/get-register-data/${projectId}`);

      const compData = res.data;
      set({ componentData: compData });
    } catch (err) {
      setError({
        header: "Component Data Not Found",
        body: "check the simulation server is working or config dir are chenging"
      })
      console.log(`error from simdatastate: ${err}`)
    }
  }
}))
