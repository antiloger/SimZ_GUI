import { TimeStepGenConfig } from "./configGen";

export type FieldType = "text" | "number" | "checkbox" | "select" | "multiselect"
// type DynArray = (object | string | number | DynArray)[];

export type CompRegStore = {
  [category: string]: {
    [compType: string]: CompRegDataI
  }
}

export interface InputFieldFormat {
  inputName: string;
  fieldType: "number" | "text" | "select" | "checkbox" | "multiselect";
  defaultValue: number | string | boolean | string[] | number[] | null;
  validation: string; // regex
  display: boolean;
  description?: string;
  required: boolean;
  options?: string[] | number[]
}

export interface CustomInputField {
  id: string
  inputName: string
  fieldType: FieldType
  defaultValue: string | number | boolean | string[] | number[] | null
  description?: string
  required?: boolean
  validation?: string
  options?: string[]
  visible?: boolean
}

interface OutputDataFormats {
  typeOut: "Chart-Pie" | "Table" | "Card";
}

export interface ConfigGenerator {
  genFn: string;
  config: TimeStepGenConfig;
}

export interface DataGenerator {
  config: ConfigGenerator;
  types: string[] | null;
}

export interface CompRegDataI {
  typeName: string;
  description?: string;
  color?: string;
  category: "generator" | "model" | "distributer" | "resource";
  InputForm: InputFieldFormat[];
  OutputData: OutputDataFormats[];
  isGenerator?: boolean
}

// in - target
// out - source
export interface ConnectorData {
  id: string;
  name: string;
  flow: string; // in, out, inout
  type: string[];
  validation: string;
}

// interface RunnerFn {
//   type: "ML" | "PreFunc" | "DynCode" | "SubProcess";
//   name: string;
//   args: DynArray;
// }
export interface RunnerFile {
  run: string;
  generator: string;
  model: string;
  event: string;
}


export interface CompDataI {
  typeName: string;
  compName: string;
  id?: string;
  category: string;
  color?: string;
  notification?: string[];
  inputData: { [key: string]: number | string | boolean | string[] | number[] | null }
  customInput: { [key: string]: CustomInputField }
  connectors: ConnectorData[];
  Runners: RunnerFile;
  GenData?: DataGenerator;
}
