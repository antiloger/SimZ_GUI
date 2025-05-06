import type React from "react"

import { useState } from "react"
import { useInputFields } from "./input-context.tsx"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export function DynamicInputForm({ title = "Input Form" }: { title?: string }) {
  const { fields } = useInputFields()
  console.log("DynamicInputForm received fields:", fields)
  const visibleFields = fields.filter((field) => field.visible)

  const [formValues, setFormValues] = useState<Record<string, any>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateField = (field: (typeof fields)[0], value: any): string => {
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

  const handleChange = (fieldId: string, value: any) => {
    const field = fields.find((f) => f.id === fieldId)
    if (field) {
      const error = validateField(field, value)
      setErrors((prev) => ({ ...prev, [fieldId]: error }))
      setFormValues((prev) => ({ ...prev, [fieldId]: value }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    const newErrors: Record<string, string> = {}
    let hasErrors = false

    visibleFields.forEach((field) => {
      const value = formValues[field.id]
      const error = validateField(field, value)
      if (error) {
        newErrors[field.id] = error
        hasErrors = true
      }
    })

    setErrors(newErrors)

    if (!hasErrors) {
      // Here you would typically submit the form data
      console.log("Form submitted with values:", formValues)
      // You could also reset the form if needed
      // setFormValues({})
    }
  }

  if (visibleFields.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground">
            No fields have been defined yet. Use the field manager to add fields.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {visibleFields.map((field) => (
            <div key={field.id} className="space-y-2">
              <Label htmlFor={field.id}>{field.inputName}</Label>

              {field.fieldType === "text" && (
                <Input
                  id={field.id}
                  value={formValues[field.id] || ""}
                  onChange={(e) => handleChange(field.id, e.target.value)}
                  placeholder={field.description}
                />
              )}

              {field.fieldType === "number" && (
                <Input
                  id={field.id}
                  type="number"
                  value={formValues[field.id] || ""}
                  onChange={(e) => handleChange(field.id, e.target.value)}
                  placeholder={field.description}
                />
              )}

              {field.fieldType === "checkbox" && (
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id={field.id}
                    checked={formValues[field.id] || false}
                    onCheckedChange={(checked) => handleChange(field.id, checked === true)}
                  />
                  <Label htmlFor={field.id}>{field.description}</Label>
                </div>
              )}

              {field.fieldType === "select" && (
                <Select value={formValues[field.id] || ""} onValueChange={(value) => handleChange(field.id, value)}>
                  <SelectTrigger>
                    <SelectValue placeholder={field.description || "Select an option"} />
                  </SelectTrigger>
                  <SelectContent>
                    {field.options?.map((option) => (
                      <SelectItem key={option} value={option}>
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              {errors[field.id] && <p className="text-sm text-red-500">{errors[field.id]}</p>}
            </div>
          ))}
        </CardContent>
        <CardFooter>
          <Button type="submit">Submit</Button>
        </CardFooter>
      </form>
    </Card>
  )
}
