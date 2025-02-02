type DynArray = (object | string | number | DynArray)[];

export type CompRegStore = {
  [category: string]: {
    [compType: string]: CompRegDataI
  }
}

interface InputFieldFormat {
  inputName: string;
  fieldType: "number" | "text" | "select" | "checkbox" | "multiselect";
  defaultValue: number | string | boolean | string[] | number[] | null;
  validation: string; // regex
  display: boolean;
  description?: string;
  required: boolean;
  options?: string[] | number[]
}

interface OutputDataFormats {
  typeOut: "Chart-Pie" | "Table" | "Card";
}

export interface CompRegDataI {
  typeName: string;
  description?: string;
  color?: string;
  category: "generator" | "model" | "distributer";
  InputForm: InputFieldFormat[];
  OutputData: OutputDataFormats[];
}

interface ConnectorData {
  from: string;
  type: string[];
  validation: string;
}

interface RunnerFn {
  type: "ML" | "PreFunc" | "DynCode" | "SubProcess";
  name: string;
  args: DynArray;
}

export interface CompDataI {
  typeName: string;
  compName: string;
  id?: string;
  category: string;
  color?: string;
  notification?: string[];
  inputData: { [key: string]: number | string | boolean | string[] | number[] | null }
  inputConn: ConnectorData[];
  outpuConn: ConnectorData[];
  Runners: RunnerFn[];
}
