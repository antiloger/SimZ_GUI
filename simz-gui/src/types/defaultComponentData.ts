import { CompRegDataI } from "./component";

export const LogicalRegisterComponent: CompRegDataI = {
  typeName: "LogicBlock_V1",
  description:
    "This component represents a logic block in the simulation. Using python users can create a logic. each input send this to this component. user must return output as Output array and it need to be in type Output",
  color: "gray",
  category: "logical",
  InputForm: [],
  OutputData: [],
  isGenerator: false,
};
