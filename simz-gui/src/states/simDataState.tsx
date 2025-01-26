import api from "@/lib/axious"
import { CompDataI, CompRegStore } from "@/types/component"
import { create } from "zustand"
import { ErrorState } from "./errorState"
import { FlowNode, FlowState } from "./flowState"
import { v4 as uuidv4 } from 'uuid';

// TODO: -
// - add create_comp fn
// - add add_data_comp fn
// - add get_comp_data_in fn
// - add get_comp_data_out fn
// - add get_comp_struct_in fn
// - add get_comp_struct_out fn
// - add check_data_comp fn


type SimDataStateT = {
  componentRegisterI: CompRegStore,
  componentData: { [id: string]: CompDataI },
  loadRegisterData: (projectId: string) => Promise<void>,
  loadCompData: (projectId: string) => Promise<void>,
  create_comp: (name: string, type: string, cat: string) => Promise<void>
}

export const SimDataState = create<SimDataStateT>((set, get) => ({
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
  },
  create_comp: async (name: string, type: string, cat: string) => {
    const { setError } = ErrorState();
    const compStruct = get().componentRegisterI[cat][type] ?? null;
    if (compStruct === null) {
      setError({
        header: "Component Not in the Registery",
        body: `can't initiate the Component. category ${cat} and type ${type} component does not exits!`
      })
      return
    }

    const compId = uuidv4();

    let inputBuild: CompDataI['inputData'] = {};
    compStruct.InputForm.forEach((i) => {
      inputBuild[i.inputName] = i.defaultValue ?? null;
    })

    let compBuild: CompDataI = {
      id: compId,
      compName: name,
      typeName: type,
      category: cat,
      color: compStruct.color,
      notification: [],
      inputData: inputBuild,
      inputConn: [],
      outpuConn: [],
      Runners: []
    };
    // get current center viewport
    const { viewport, setNodes } = FlowState.getState()
    const nodeBuild = {
      id: compId,
      type: 'dynComp',
      data: {
        name: name,
        id: compId,
        type: 'queue',
        color: "green",
        notify: false,
        data: []
      },
      position: { x: viewport.x, y: viewport.y },

    } as FlowNode;
    set((state) => ({
      componentData: {
        ...state.componentData,
        [compId]: compBuild
      }
    }))
    setNodes([nodeBuild]);
  },
  get_comp_by_id: (id: string) {
  }
}))
