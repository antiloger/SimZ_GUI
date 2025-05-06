import {
  CompDataI,
  CompRegDataI,
  CompRegStore,
  ConnectorData,
  CustomInputField,
  InputFieldFormat,
  RunnerFile,
} from "@/types/component";
import { create } from "zustand";
import { ErrorState } from "./errorState";
import { FlowNode, FlowState } from "./flowState";
import { v4 as uuidv4 } from "uuid";
import { updateKey } from "@/utils/componentTypeUtil";
import { GenAttributes, GenTypes, GenTypeState, NewTimeStepGenConfigFn } from "@/types/configGen";
import { useSocketStore } from "@/utils/socketIo";
import { initialRunnerFile } from "@/mockData/codemodel";

// TODO: -
// - add create_comp fn
// - add add_data_comp fn
// - add get_comp_data_in fn
// - add get_comp_data_out fn
// - add get_comp_struct_in fn
// - add get_comp_struct_out fn
// - add check_data_comp fn

type SimDataStateT = {
  projectName: string | null;
  componentRegisterI: CompRegStore;
  componentData: { [id: string]: CompDataI };
  genTypesData: GenTypeState;
  getProjectName: () => string | null;
  setProjectName: (name: string) => void;
  loadRegisterData: () => Promise<void>;
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
  addConnector: (compId: string, connector: ConnectorData) => void;
  updateConnector: (compId: string, connectorName: string, connector: ConnectorData) => void;
  deleteConnector: (compId: string, connectorName: string) => void;
  getAllConnectors: (compId: string) => ConnectorData[] | null;
  getConnectorByName: (compId: string, connectorName: string) => ConnectorData | null;
  addGenType: (type: GenTypes, componentId: string) => string;
  updateGenType: (compId: string, typeId: string, genType: GenTypes) => void;
  getAllGenTypeNames: () => string[];
  getGenTypeById: (typeId: string) => GenTypes | null;
  change_comp_input_values: (
    id: string,
    key: string,
    values: any,
  ) => void | string;
  getTypeAttributes: (typename: string) => { [attr: string]: GenAttributes } | null;
  deleteGenType: (typeId: string) => void;
  saveStateAsJson: () => { [id: string]: CompDataI };
  saveGenStateAsJson: () => GenTypeState;
  getCustomInputAsArray: (compId: string) => CustomInputField[] | null;
  addCustomInputField: (compId: string, field: CustomInputField) => void;
  updateCustomInputField: (compId: string, fieldName: string, field: Partial<CustomInputField>) => void;
  deleteCustomInputField: (compId: string, fieldName: string) => void;
  toggleVisibilityCustomInput: (compId: string, filedName: string) => void;
  saveRunnerStr: (compId: string, runnerStr: RunnerFile) => void;
  getRunnerStr: (compId: string) => RunnerFile | null;
  setCustomInput: (
    compId: string,
    fieldName: string,
    value: string | number | boolean | string[] | number[] | null,
  ) => void;
};

export const SimDataState = create<SimDataStateT>((set, get) => ({
  projectName: null,
  componentRegisterI: {},
  componentData: {},
  genTypesData: {},
  getProjectName: () => {
    return get().projectName;
  },
  setProjectName: (name: string) => {
    set({ projectName: name });
  },
  loadRegisterData: async () => {
    const { setError } = ErrorState.getState();
    const { get_registered_component } = useSocketStore.getState();
    try {

      const response = await get_registered_component();

      // if (res.status != 200) {
      //   setError({
      //     header: "Register Component Data Not Found",
      //     body: "check the simulation server is working or config dir are chenging",
      //   });
      //   console.log("not a valid status");
      //   return;
      // }
      console.log("|||response >>", response);
      set({ componentRegisterI: response });
    } catch (err) {
      setError({
        header: "Register Component Data Not Found",
        body: "check the simulation server is working or config dir are chenging",
      });
      console.log(`error from simdatastate: ${err}`);
    }
  },
  loadCompData: async (projectId: string) => {
    const { setError } = ErrorState.getState();

    try {
      const { get_data_state } = useSocketStore.getState();
      const data = await get_data_state(projectId);
      console.log("data >>", data);

      if (!data || Object.keys(data).length === 0) return;

      const isStateEmpty = !data.state_data || Object.keys(data.state_data).length === 0;
      const isGenEmpty = !data.gen_data || Object.keys(data.gen_data).length === 0;

      if (!isGenEmpty) {
        set({ genTypesData: data.gen_data });
      }

      if (!isStateEmpty) {
        set({ componentData: data.state_data });
      }

    } catch (err) {
      setError({
        header: "Component Data Not Found",
        body: "Check if the simulation server is running or config directories have changed",
      });
      console.error(`Error from simdatastate:`, err);
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
      customInput: {},
      connectors: [],
      Runners: initialRunnerFile,
      GenData: { types: [], config: NewTimeStepGenConfigFn() }
    };
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
  addConnector: (compId: string, connector: ConnectorData) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      // Ensure connectors array exists
      if (!comp.connectors) {
        comp.connectors = [];
      }
      if (comp.connectors.find((c) => c.name === connector.name)) {
        return state;
      }
      comp.connectors.push(connector);
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  },
  updateConnector: (compId: string, connectorId: string, connector: ConnectorData) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      const connectorIndex = comp.connectors.findIndex((c) => c.id === connectorId);
      if (connectorIndex === -1) {
        return state;
      }
      comp.connectors[connectorIndex] = connector;
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  },
  deleteConnector: (compId: string, connectorId: string) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      comp.connectors = comp.connectors.filter((c) => c.id !== connectorId);
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  },
  getAllConnectors: (compId: string) => {
    const comp = get().componentData[compId];
    if (!comp) {
      return null;
    }
    return comp.connectors;
  },
  getConnectorByName: (compId: string, connectorId: string) => {
    const comp = get().componentData[compId];
    if (!comp || !comp.connectors) {
      return null;
    }
    const connector = comp.connectors.find((c) => c.id === connectorId);
    return connector || null;
  },
  addGenType: (type: GenTypes, componentId: string) => {
    const typeId = uuidv4();
    set((state) => {
      const comp = state.componentData[componentId];
      if (!comp) {
        return state;
      }
      const istypeexist = comp.GenData?.types?.includes(typeId);
      if (istypeexist) {
        return state;
      }

      comp.GenData = {
        config: comp.GenData?.config ?? NewTimeStepGenConfigFn(),
        types: comp.GenData?.types ? [...comp.GenData.types, typeId] : [typeId]
      }

      return {
        genTypesData: { ...state.genTypesData, [typeId]: type },
        componentData: {
          ...state.componentData,
          [componentId]: comp,
        },
      };
    });
    return typeId;
  },
  updateGenType: (compId: string, typeId: string, genType: GenTypes) => {
    // check if the typeId exists in the component's types
    const comp = get().componentData[compId];
    if (!comp?.GenData?.types?.includes(typeId)) {
      console.log("typeId not found in the component's types");
      return;
    }
    // check if the typeId exists in the genTypesData
    const checkGenType = get().genTypesData[typeId];
    if (!checkGenType) {
      console.log("typeId not found in the genTypesData");
      return;
    }

    set((state) => {
      // If type name has changed, update it in component's types array
      if (checkGenType.typeName !== genType.typeName) {
        comp.GenData = {
          config: comp.GenData?.config ?? NewTimeStepGenConfigFn(),
          types: comp.GenData?.types?.map(type =>
            type === typeId ? typeId : type
          ) ?? []
        };
      }

      // Update the genType in genTypesData
      return {
        genTypesData: { ...state.genTypesData, [typeId]: genType },
        componentData: { ...state.componentData, [compId]: comp }
      };
    });
  },
  getAllGenTypeNames: () => {
    const genTypes = get().genTypesData;
    return Object.values(genTypes).map(type => type.typeName);
  },
  getGenTypeById: (typeId: string) => {
    return get().genTypesData[typeId];
  },
  getTypeAttributes: (typename: string) => {
    const genType = get().genTypesData[typename];
    if (!genType) {
      return null;
    }
    return genType.attributes;
  },
  deleteGenType: (typeId: string) => {
    set((state) => {
      const typeObj = state.genTypesData[typeId];
      if (!typeObj) {
        return state;
      }
      const compId = typeObj.genComponentId;
      const comp = state.componentData[compId];
      if (!comp || !comp.GenData) {
        const { addReactFlowError } = ErrorState.getState();
        addReactFlowError({
          errorType: "Component Not Found When Deleting GenType",
          error: "Component Not Found When Deleting GenType",
          type: "error",
          componentId: compId,
          componentName: comp?.compName ?? "Unknown",
        });
        return state;
      }

      // Remove typeId from component's GenData.types array
      comp.GenData = {
        ...comp.GenData,
        types: comp.GenData.types?.filter((type) => type !== typeId) ?? []
      };

      // Remove type from genTypesData
      const { [typeId]: _, ...restGenTypes } = state.genTypesData;

      return {
        genTypesData: restGenTypes,
        componentData: {
          ...state.componentData,
          [compId]: comp
        }
      };
    });
  },
  saveStateAsJson: () => {
    const { componentData } = get();
    const json = JSON.parse(JSON.stringify(componentData));
    return json;
  },
  saveGenStateAsJson: () => {
    const { genTypesData } = get();
    const json = JSON.parse(JSON.stringify(genTypesData));
    return json;
  },
  getCustomInputAsArray: (compId: string) => {
    const comp = get().componentData[compId];
    if (!comp) {
      return null;
    }
    const customInput = comp.customInput;
    if (!customInput) {
      return null;
    }
    const customInputArray: CustomInputField[] = [];
    Object.entries(customInput).forEach(([_, value]) => {
      customInputArray.push(value);
    });
    return customInputArray;
  },
  addCustomInputField: (compId: string, field: CustomInputField) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      if (!comp.customInput) {
        comp.customInput = {};
      }
      comp.customInput[field.inputName] = {
        ...field,
        defaultValue: field.defaultValue ?? null,
      };
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  },
  updateCustomInputField: (compId: string, fieldName: string, field: Partial<CustomInputField>) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      if (!comp.customInput) {
        return state;
      }
      if (!comp.customInput[fieldName]) {
        return state;
      }
      comp.customInput[fieldName] = {
        ...comp.customInput[fieldName],
        ...field,
        defaultValue: field.defaultValue ?? comp.customInput[fieldName].defaultValue,
      };
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  },
  deleteCustomInputField: (compId: string, fieldName: string) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      if (!comp.customInput) {
        return state;
      }
      if (!comp.customInput[fieldName]) {
        return state;
      }
      delete comp.customInput[fieldName];
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });

  },
  toggleVisibilityCustomInput: (compId: string, filedName: string) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      if (!comp.customInput) {
        return state;
      }
      if (!comp.customInput[filedName]) {
        return state;
      }
      comp.customInput[filedName].visible = !comp.customInput[filedName].visible;
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  },
  saveRunnerStr: (compId: string, runnerStr: RunnerFile) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      comp.Runners = runnerStr;
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  },
  getRunnerStr: (compId: string) => {
    const comp = get().componentData[compId];
    if (!comp) {
      return null;
    }
    return comp.Runners;
  },
  setCustomInput: (compId: string, fieldName: string, value: string | number | boolean | string[] | number[] | null) => {
    set((state) => {
      const comp = state.componentData[compId];
      if (!comp) {
        return state;
      }
      if (!comp.customInput) {
        return state;
      }
      if (!comp.customInput[fieldName]) {
        return state;
      }
      comp.customInput[fieldName].defaultValue = value;
      return {
        componentData: {
          ...state.componentData,
          [compId]: comp,
        },
      };
    });
  }
  // SyncErrorsState: () => {
  //   const { setError } = ErrorState.getState();
  //   const { componentData } = get();

  // }
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
    set({
      propertyWindowData: null
    })
    set({ propertyWindowData: comp });
  },
}));

// function TypeSpecBuilder(type: CompDataI) {
//   const checkType = ["generator"];
//   if (!checkType.includes(type.category)) {
//     return type;
//   }
//   switch (type.category) {
//     case "generator":
//       const configFn = NewTimeStepGenConfigFn();
//       type.GenData = {
//         config: configFn,
//         types: []
//       }
//       return type
//     default:
//       return type;
//   }
// }
//

