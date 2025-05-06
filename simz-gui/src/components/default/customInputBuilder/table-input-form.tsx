"use client"

import { useState } from "react"
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { useInputFields } from "./input-context"
import { SimDataState } from "@/states/simDataState"

interface TableInputFormProps {
  compId: string
  category?: string | null
  compType?: string | null
  id?: string | null
}

export default function TableInputForm({
  // category = "default",
  // compType = "default",
  compId,
  id = "default",
}: TableInputFormProps) {
  const { fields } = useInputFields()
  const [formData, setFormData] = useState<{ [key: string]: number | string | boolean | string[] | number[] | null }>(
    {},
  )
  const [errors, setErrors] = useState<Record<string, string>>({})
  const visibleFields = fields.filter((field) => field.visible)
  const { setCustomInput } = SimDataState()
  // Mock implementation of the state functions
  const change_comp_input_values = (id: string, name: string, value: any) => {
    console.log("Changing value for", id, name, value)
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

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

  const handleChange = (name: string, value: string | number | boolean) => {
    console.log("Manual", name, value)
    const field = visibleFields.find((f) => f.inputName === name)
    if (field) {
      const error = validateField(field, value)
      setErrors((prev) => ({ ...prev, [name]: error }))
      change_comp_input_values(id || "default", name, value)
    }
    setCustomInput(
      compId,
      name,
      value
    )
  }

  const renderField = (field: (typeof fields)[0]) => {
    return (
      <TableRow key={field.id} className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
        <TableCell className="bg-muted/50 py-2 font-medium">{field.inputName}</TableCell>
        {field.fieldType === "text" && (
          <TableCell className="py-0 pr-0">
            <Input
              type="text"
              value={formData[field.inputName]?.toString() ?? field.defaultValue?.toString() ?? ""}
              onChange={(e) => handleChange(field.inputName, e.target.value)}
              className="border-none p-0 shadow-none focus-visible:ring-0"
            />
            {errors[field.inputName] && <p className="mt-1 text-sm text-red-500">{errors[field.inputName]}</p>}
          </TableCell>
        )}
        {field.fieldType === "number" && (
          <TableCell className="py-0 pr-0">
            <Input
              type="number"
              value={Number(formData[field.inputName] ?? field.defaultValue ?? 0)}
              onChange={(e) => handleChange(field.inputName, Number(e.target.value))}
              className="border-none p-0 shadow-none focus-visible:ring-0"
            />
            {errors[field.inputName] && <p className="mt-1 text-sm text-red-500">{errors[field.inputName]}</p>}
          </TableCell>
        )}
        {field.fieldType === "checkbox" && (
          <TableCell className="py-2 px-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                checked={Boolean(formData[field.inputName] ?? field.defaultValue) ?? false}
                onCheckedChange={(value) => handleChange(field.inputName, value)}
              />
              <Label htmlFor={field.id}>{field.description}</Label>
            </div>
            {errors[field.inputName] && <p className="mt-1 text-sm text-red-500">{errors[field.inputName]}</p>}
          </TableCell>
        )}
        {(field.fieldType === "select" || field.fieldType === "multiselect") && (
          <TableCell className="p-0">
            <Select
              value={formData[field.inputName]?.toString() ?? field.defaultValue?.toString()}
              onValueChange={(value) => handleChange(field.inputName, value)}
            >
              <SelectTrigger className="w-full border-0 focus:ring-0">
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
            {errors[field.inputName] && <p className="mt-1 text-sm text-red-500">{errors[field.inputName]}</p>}
          </TableCell>
        )}

        {/* Visibility checkbox */}
        <TableCell>
          <Checkbox />
        </TableCell>
      </TableRow>
    )
  }

  if (visibleFields.length === 0) {
    return (
      <div className="mx-auto w-full">
        <div className="overflow-hidden rounded-lg border border-border bg-background">
          <div className="p-4 text-center text-muted-foreground">
            No fields have been defined yet. Use the field manager to add fields.
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full">
      <form>
        <div className="overflow-hidden rounded-lg border border-border bg-background [&_tr:last-child]:border-b-0">
          <Table>
            <TableBody>{visibleFields.map(renderField)}</TableBody>
          </Table>
        </div>
      </form>
    </div>
  )
}
