import { useState, useEffect } from "react"
import type { InputFieldFormat } from "../types/inputFieldFormat"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface DynamicFormProps {
  fields: InputFieldFormat[]
  onSubmit: (data: any) => void
}

export function DynamicForm({ fields, onSubmit }: DynamicFormProps) {
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    // Initialize form data with default values
    const initialData: Record<string, any> = {}
    fields.forEach((field) => {
      if (field.display) {
        initialData[field.inputName] = field.defaultValue
      }
    })
    setFormData(initialData)
  }, [fields])

  const validateField = (field: InputFieldFormat, value: any): string => {
    if (field.required && (value === "" || value === null || value === undefined)) {
      return `${field.inputName} is required`
    }
    if (field.validation && typeof value === "string") {
      const regex = new RegExp(field.validation)
      if (!regex.test(value)) {
        return `Invalid ${field.inputName}`
      }
    }
    return ""
  }

  const handleChange = (fieldName: string, value: any) => {
    const field = fields.find((f) => f.inputName === fieldName)
    if (field) {
      const error = validateField(field, value)
      setErrors((prev) => ({ ...prev, [fieldName]: error }))
      setFormData((prev) => ({ ...prev, [fieldName]: value }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newErrors: Record<string, string> = {}
    fields.forEach((field) => {
      if (field.display) {
        const error = validateField(field, formData[field.inputName])
        if (error) {
          newErrors[field.inputName] = error
        }
      }
    })
    setErrors(newErrors)
    if (Object.keys(newErrors).length === 0) {
      onSubmit(formData)
    }
  }

  const renderField = (field: InputFieldFormat) => {
    if (!field.display) return null

    return (
      <div key={field.inputName} className="mb-4">
        <Label htmlFor={field.inputName} className="block text-sm font-medium text-gray-700">
          {field.inputName}
        </Label>
        <div className="mt-1">
          {field.fieldType === "text" && (
            <Input
              id={field.inputName}
              value={formData[field.inputName] || ""}
              onChange={(e) => handleChange(field.inputName, e.target.value)}
              className={errors[field.inputName] ? "border-red-500" : ""}
            />
          )}
          {field.fieldType === "number" && (
            <Input
              type="number"
              id={field.inputName}
              value={formData[field.inputName] || ""}
              onChange={(e) => handleChange(field.inputName, e.target.value)}
              className={errors[field.inputName] ? "border-red-500" : ""}
            />
          )}
          {field.fieldType === "checkbox" && (
            <Checkbox
              id={field.inputName}
              checked={formData[field.inputName] || false}
              onCheckedChange={(checked) => handleChange(field.inputName, checked)}
            />
          )}
          {(field.fieldType === "select" || field.fieldType === "multiselect") && (
            <Select value={formData[field.inputName]} onValueChange={(value) => handleChange(field.inputName, value)}>
              <SelectTrigger className={errors[field.inputName] ? "border-red-500" : ""}>
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((option) => (
                  <SelectItem key={option} value={option.toString()}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
        {field.description && <p className="mt-1 text-sm text-gray-500">{field.description}</p>}
        {errors[field.inputName] && <p className="mt-1 text-sm text-red-500">{errors[field.inputName]}</p>}
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {fields.map(renderField)}
      <Button type="submit">Submit</Button>
    </form>
  )
}

