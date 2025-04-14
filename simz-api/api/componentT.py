from typing import Optional
from pydantic import BaseModel

class ComponentInputType(BaseModel):
    inputName: str
    fieldType: str
    defaultValue: str | float | int | list[str | int | float]
    validation: str
    display: bool
    discription: Optional[str]
    required: bool

class ComponentOutputType(BaseModel):
    typeOut: str

class ComponentRegisterType(BaseModel):
    typeName: str
    discription: Optional[str]
    color: Optional[str]
    category: str
    InputForm: list[ComponentInputType]
    OutputForm: list[ComponentOutputType]
