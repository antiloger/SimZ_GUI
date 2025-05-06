import { SimDataState } from "@/states/simDataState"
import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

export type FieldType = "text" | "number" | "checkbox" | "select" | "multiselect"

export interface InputField {
  id: string
  inputName: string
  fieldType: FieldType
  description?: string
  required?: boolean
  validation?: string
  options?: string[]
  visible?: boolean
  defaultValue?: string | number | boolean | string[] | number[] | null
}

interface InputFieldContextType {
  fields: InputField[]
  addField: (field: Omit<InputField, "id">) => void
  updateField: (id: string, field: Partial<InputField>) => void
  removeField: (id: string) => void
  toggleVisibility: (id: string) => void
}

const InputFieldContext = createContext<InputFieldContextType | undefined>(undefined)

export function InputFieldProvider({ children, compId }: { children: ReactNode, compId: string }) {
  const [fields, setFields] = useState<InputField[]>([])
  const {
    componentData,
    getCustomInputAsArray,
    addCustomInputField,
    updateCustomInputField,
    deleteCustomInputField
  } = SimDataState()

  useEffect(() => {
    const data = getCustomInputAsArray(compId)
    if (data) {
      setFields(data)
    }
  }, [getCustomInputAsArray, componentData])

  const addField = (field: Omit<InputField, "id">) => {
    const id = crypto.randomUUID()
    const newField = { ...field, id, visible: true }
    console.log("Adding field:", newField)
    addCustomInputField(compId, newField)
    console.log("Field added ===> :", fields)
  }

  const updateField = (id: string, updatedField: Partial<InputField>) => {
    updateCustomInputField(compId, id, updatedField)
  }

  const removeField = (id: string) => {
    deleteCustomInputField(compId, id)
  }

  const toggleVisibility = (id: string) => {
    setFields((prev) => prev.map((field) => (field.id === id ? { ...field, visible: !field.visible } : field)))
  }

  return (
    <InputFieldContext.Provider value={{ fields, addField, updateField, removeField, toggleVisibility }}>
      {children}
    </InputFieldContext.Provider>
  )
}

export function useInputFields() {
  const context = useContext(InputFieldContext)
  if (context === undefined) {
    throw new Error("useInputFields must be used within an InputFieldProvider")
  }
  return context
}
