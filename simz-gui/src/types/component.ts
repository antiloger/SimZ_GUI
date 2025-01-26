type DynArray = (string | number | DynArray)[];

export type CompRegStore = {
  [category: string]: {
    [compType: string]: CompRegDataI
  }
}

interface InputFieldFormat {
  inputName: string;
  fieldType: "number" | "text" | "select" | "checkbox" | "multiselect";
  defaultValue: number | string | string[] | number[];
  validation: string[];
  display: boolean;
  discription?: string;
  required: boolean;
}

interface OutputDataFormats {
  typeOut: "Chart-Pie" | "Table" | "Card";
}

export interface CompRegDataI {
  typeName: string;
  discription?: string;
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
  inputData: { [key: string]: number | string | string[] | number[] | null }
  inputConn: ConnectorData[];
  outpuConn: ConnectorData[];
  Runners: RunnerFn[];
}
