import type React from "react"

import { useState } from "react"
import { useInputFields, type FieldType } from "./input-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function AddFieldForm() {
  const { addField } = useInputFields()
  const [inputName, setInputName] = useState("")
  const [fieldType, setFieldType] = useState<FieldType>("text")
  const [description, setDescription] = useState("")
  const [required, setRequired] = useState(false)
  const [validation, setValidation] = useState("")
  const [options, setOptions] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    addField({
      inputName,
      fieldType,
      description,
      required,
      validation: validation || undefined,
      options:
        fieldType === "select" || fieldType === "multiselect" ? options.split(",").map((opt) => opt.trim()) : undefined,
    })

    // Reset form
    setInputName("")
    setFieldType("text")
    setDescription("")
    setRequired(false)
    setValidation("")
    setOptions("")
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-2">
        <Label htmlFor="inputName">Field Name</Label>
        <Input id="inputName" value={inputName} onChange={(e) => setInputName(e.target.value)} required />
      </div>

      <div className="space-y-2">
        <Label htmlFor="fieldType">Field Type</Label>
        <Select value={fieldType} onValueChange={(value) => setFieldType(value as FieldType)}>
          <SelectTrigger>
            <SelectValue placeholder="Select field type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="text">Text</SelectItem>
            <SelectItem value="number">Number</SelectItem>
            <SelectItem value="checkbox">Checkbox</SelectItem>
            <SelectItem value="select">Select</SelectItem>
            <SelectItem value="multiselect">Multi-select</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
      </div>

      {(fieldType === "select" || fieldType === "multiselect") && (
        <div className="space-y-2">
          <Label htmlFor="options">Options (comma separated)</Label>
          <Input
            id="options"
            value={options}
            onChange={(e) => setOptions(e.target.value)}
            placeholder="Option 1, Option 2, Option 3"
            required
          />
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="validation">Validation Pattern (regex)</Label>
        <Input
          id="validation"
          value={validation}
          onChange={(e) => setValidation(e.target.value)}
          placeholder="e.g. ^[A-Za-z0-9]+$"
        />
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox id="required" checked={required} onCheckedChange={(checked) => setRequired(checked === true)} />
        <Label htmlFor="required">Required field</Label>
      </div>
      <Button type="submit">Add Field</Button>
    </form>
  )
}
