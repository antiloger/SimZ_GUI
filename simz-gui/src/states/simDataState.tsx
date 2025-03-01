import api from "@/lib/axious";
import {
  CompDataI,
  CompRegDataI,
  CompRegStore,
  InputFieldFormat,
} from "@/types/component";
import { create } from "zustand";
import { ErrorState } from "./errorState";
import { FlowNode, FlowState } from "./flowState";
import { v4 as uuidv4 } from "uuid";
import { componentData, componentRegStore } from "@/mockData/compData";
import { updateKey } from "@/utils/componentTypeUtil";
import { GenTypes, GenTypeState, NewTimeStepGenConfigFn } from "@/types/configGen";

// TODO: -
// - add create_comp fn
// - add add_data_comp fn
// - add get_comp_data_in fn
// - add get_comp_data_out fn
// - add get_comp_struct_in fn
// - add get_comp_struct_out fn
// - add check_data_comp fn

type SimDataStateT = {
  componentRegisterI: CompRegStore;
  componentData: { [id: string]: CompDataI };
  genTypesData: GenTypeState;
  loadRegisterData: (projectId: string) => Promise<void>;
  loadCompData: (projectId: string) => Promise<void>;
  sync_comp_nodes: () => Promise<void>;
  create_comp: (name: string, type: string, cat: string) => void;
  get_comp_by_id: (id: string) => CompDataI | null;
  get_comp_struct_out: (category: string, type: string) => CompRegDataI | null;
  get_comp_input_by_id: (id: string) => {
    [key: string]: number | string | boolean | string[] | number[] | null;
  } | null;
  get_comp_struct_input_out: (
    category: string,
    type: string,
  ) => InputFieldFormat[] | null;
  change_comp_default_values: (
    id: string,
    key: string,
    values: string,
  ) => void | string;
  change_comp_input_values: (
    id: string,
    key: string,
    values: any,
  ) => void | string;
};

export const SimDataState = create<SimDataStateT>((set, get) => ({
  componentRegisterI: componentRegStore,
  componentData: componentData,
  genTypesData: {},
  loadRegisterData: async (projectId: string) => {
    const { setError } = ErrorState.getState();
    try {
      const res = await api.post<CompRegStore>(`/load-register-data`, {
        projectId: projectId,
      });

      if (res.status != 200) {
        setError({
          header: "Register Component Data Not Found",
          body: "check the simulation server is working or config dir are chenging",
        });
        console.log("not a valid status");
        return;
      }

      const registerData = res.data;
      set({ componentRegisterI: registerData });
    } catch (err) {
      setError({
        header: "Register Component Data Not Found",
        body: "check the simulation server is working or config dir are chenging",
      });
      console.log(`error from simdatastate: ${err}`);
    }
  },
  loadCompData: async (projectId: string) => {
    const { setError } = ErrorState();
    try {
      const res = await api.get<{ [id: string]: CompDataI }>(
        `/project/get-register-data/${projectId}`,
      );

      const compData = res.data;
      set({ componentData: compData });
    } catch (err) {
      setError({
        header: "Component Data Not Found",
        body: "check the simulation server is working or config dir are chenging",
      });
      console.log(`error from simdatastate: ${err}`);
    }
  },
  sync_comp_nodes: async () => {
    const data = get().componentData;
    if (Object.keys(data).length > 0) {
      const { viewport, addNodes } = FlowState.getState();
      const nodeData: FlowNode[] = [];
      // this might change cause i only need id for node not values
      Object.entries(data).forEach(([id, values]) => {
        const nodeBuild = {
          id: id,
          type: "dynComp",
          data: {
            name: values.compName,
            id: id,
            type: values.typeName,
            color: values.color,
            notify: false,
            data: [],
          },
          position: { x: viewport.x, y: viewport.y },
        } as FlowNode;
        nodeData.push(nodeBuild);
      });
      addNodes(nodeData);
      return;
    }

    return;
  },
  create_comp: (name: string, type: string, cat: string) => {
    const { setError } = ErrorState.getState();
    const compStruct = get().componentRegisterI[cat][type] ?? null;
    if (compStruct === null) {
      setError({
        header: "Component Not in the Registery",
        body: `can't initiate the Component. category ${cat} and type ${type} component does not exits!`,
      });
      return;
    }
    console.log("test me");
    const compId = uuidv4();

    let inputBuild: CompDataI["inputData"] = {};
    compStruct.InputForm.forEach((i) => {
      inputBuild[i.inputName] = i.defaultValue ?? null;
    });

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
      Runners: [],
    };
    compBuild = TypeSpecBuilder(compBuild)
    // get current center viewport
    const { viewport, addNodes } = FlowState.getState();
    const nodeBuild = {
      id: compId,
      type: "dynComp",
      data: {
        name: name,
        id: compId,
        type: "queue",
        color: "green",
        notify: false,
        data: [],
      },
      position: { x: viewport.x, y: viewport.y },
    } as FlowNode;
    set((state) => ({
      componentData: {
        ...state.componentData,
        [compId]: compBuild,
      },
    }));
    addNodes([nodeBuild]);
  },
  get_comp_by_id: (id: string) => {
    const component = get().componentData[id] ?? null;
    if (component === null) {
      return null;
    }
    return component;
  },
  get_comp_struct_out: (category: string, type: string) => {
    const struct = get().componentRegisterI[category][type];
    if (!struct) {
      return null;
    }
    return struct;
  },
  get_comp_input_by_id: (id: string) => {
    const component = get().componentData[id] ?? null;
    if (component === null) {
      return null;
    }
    return component.inputData;
  },
  get_comp_struct_input_out: (category: string, type: string) => {
    const struct = get().componentRegisterI[category][type];
    if (!struct) {
      return null;
    }
    return struct.InputForm;
  },
  change_comp_default_values: (id: string, key: string, values: string) => {
    try {
      set((state) => {
        const comp = get().componentData[id];
        if (!comp) {
          throw new Error(`Component with id "${id}" not found`);
        }
        const compUpdate = updateKey(comp, key, values);
        return {
          componentData: {
            ...state.componentData,
            [id]: compUpdate,
          },
        };
      });
    } catch (e) {
      console.log(e);
      return "Internal Error";
    }
    return;
  },
  change_comp_input_values: (id: string, key: string, values: any) => {
    try {
      set((state) => {
        let comp = get().componentData[id];
        if (!comp) {
          throw new Error(`Component with id "${id}" not found`);
        }

        if (!(key in comp.inputData)) {
          throw new Error(`Component with input "${key}" not found`);
        }

        comp.inputData[key] = values;

        return {
          componentData: {
            ...state.componentData,
            [id]: comp,
          },
        };
      });
    } catch (e) {
      console.log(e);
      return "Internal Error";
    }
    return;
  },
  addGenType: (typename: string, type: GenTypes) => {
    set((state) => ({
      genTypesData: { ...state.genTypesData, [typename]: type },
    }));
  },
  addAttrToGen: (
    typename: string,
    name: string,
    type: string,
    value: string | number,
  ) => {
    set((state) => {
      const gentype: GenTypes = state.genTypesData[typename];
      if (!type) {
        return state;
      }
      const updatedGenType: GenTypes = {
        ...gentype,
        attributes: {
          ...gentype.attributes,
          [name]: { type, value },
        },
      };
      return {
        genTypesData: {
          ...state.genTypesData,
          [typename]: updatedGenType,
        },
      };
    });
  },
  getAllGenTypeNames: () => {
    return Object.keys(get().genTypesData);
  },
  getTypeAttributes: (typename: string) => {
    return get().genTypesData[typename].attributes;
  },
}));

type SimPropertyWindowT = {
  isPropertyWindowOn: boolean;
  propertyWindowData: CompDataI | null;
  setPropertyWindowOn: (on: boolean) => void;
  setPropertyWindowData: (comp: CompDataI | null) => void;
};

export const SimPropertyWindowStore = create<SimPropertyWindowT>((set) => ({
  isPropertyWindowOn: false,
  propertyWindowData: null,
  setPropertyWindowOn: (on: boolean) => {
    set({ isPropertyWindowOn: on });
  },
  setPropertyWindowData: (comp: CompDataI | null) => {
    set({ propertyWindowData: comp });
  },
}));

function TypeSpecBuilder(type: CompDataI) {
  const checkType = ["generator"];
  if (!checkType.includes(type.category)) {
    return type;
  }
  switch (type.category) {
    case "generator":
      const configFn = NewTimeStepGenConfigFn();
      type.GenData = {
        config: configFn,
        types: ""
      }
      return type
    default:
      return type;
  }
}
