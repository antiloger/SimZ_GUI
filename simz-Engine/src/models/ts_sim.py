from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


# Placeholder for TimeStepGenConfig (import this or define it as needed)
class TimeStepGenConfig(BaseModel):
    # Define your specific fields here
    pass


# A DynArray is defined recursively in TS.
# Here, we treat it as a List of generic JSON types.
DynArray = List[Any]


# -----------------------------
# InputFieldFormat and dependencies
# -----------------------------
class FieldType(str, Enum):
    number = "number"
    text = "text"
    select = "select"
    checkbox = "checkbox"
    multiselect = "multiselect"


class InputFieldFormat(BaseModel):
    inputName: str
    fieldType: FieldType
    # defaultValue can be a number, string, boolean, list (of strings or numbers), or None
    defaultValue: Union[int, str, bool, List[str], List[int], None]
    validation: str  # a regex pattern or similar
    display: bool
    description: Optional[str] = None
    required: bool
    options: Optional[Union[List[str], List[int]]] = None


# -----------------------------
# OutputDataFormats
# -----------------------------
class OutputType(str, Enum):
    chart_pie = "Chart-Pie"
    table = "Table"
    card = "Card"


class OutputDataFormats(BaseModel):
    typeOut: OutputType


# -----------------------------
# ConfigGenerator and DataGenerator
# -----------------------------
class ConfigGenerator(BaseModel):
    genFn: str
    config: TimeStepGenConfig


class DataGenerator(BaseModel):
    config: ConfigGenerator
    types: Optional[List[str]]  # represents TS: string[] | null


# -----------------------------
# CompRegDataI
# -----------------------------
class CompCategory(str, Enum):
    generator = "generator"
    model = "model"
    distributer = "distributer"


class CompRegDataI(BaseModel):
    typeName: str
    description: Optional[str] = None
    color: Optional[str] = None
    category: CompCategory
    InputForm: List[InputFieldFormat]
    OutputData: List[OutputDataFormats]
    isGenerator: Optional[bool] = None


# Example for a registry store:
# Mapping: { category: { compType: CompRegDataI } }
CompRegStore = Dict[str, Dict[str, CompRegDataI]]


# -----------------------------
# ConnectorData
# -----------------------------
class FlowType(str, Enum):
    in_flow = "in"
    out_flow = "out"
    inout = "inout"


class ConnectorData(BaseModel):
    id: str
    name: str
    flow: FlowType  # use FlowType if your valid flows are "in", "out", "inout"
    type: List[str]
    validation: str


# -----------------------------
# RunnerFn
# -----------------------------
class RunnerFnType(str, Enum):
    ML = "ML"
    PreFunc = "PreFunc"
    DynCode = "DynCode"
    SubProcess = "SubProcess"


class RunnerFn(BaseModel):
    type: RunnerFnType
    name: str
    args: DynArray


# -----------------------------
# CompDataI
# -----------------------------
class CompDataI(BaseModel):
    typeName: str
    compName: str
    id: Optional[str] = None
    category: str  # if there is a limited set of categories, you could use an Enum here as well
    color: Optional[str] = None
    notification: Optional[List[str]] = None
    # inputData: values can be number, string, bool, list of strings/numbers, or None
    inputData: Dict[str, Union[int, str, bool, List[str], List[int], None]]
    # customInput maps keys to InputFieldFormat instances
    customInput: Dict[str, InputFieldFormat]
    connectors: List[ConnectorData]
    Runners: List[RunnerFn]
    GenData: Optional[DataGenerator] = None
