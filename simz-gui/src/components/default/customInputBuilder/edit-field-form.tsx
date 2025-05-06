import type React from "react"

import { useState, useEffect } from "react"
import { useInputFields, type InputField } from "./input-context.tsx"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface EditFieldDialogProps {
  fieldId: string
  open: boolean
  onClose: () => void
}

export function EditFieldDialog({ fieldId, open, onClose }: EditFieldDialogProps) {
  const { fields, updateField } = useInputFields()
  const [field, setField] = useState<InputField | null>(null)

  useEffect(() => {
    const currentField = fields.find((f) => f.id === fieldId)
    if (currentField) {
      setField(currentField)
    }
  }, [fieldId, fields])

  if (!field) return null

  const handleChange = (key: keyof InputField, value: any) => {
    setField((prev) => (prev ? { ...prev, [key]: value } : null))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (field) {
      updateField(fieldId, field)
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit Field</DialogTitle>
            <DialogDescription>Make changes to the field properties.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-inputName">Field Name</Label>
              <Input
                id="edit-inputName"
                value={field.inputName}
                onChange={(e) => handleChange("inputName", e.target.value)}
                required
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={field.description || ""}
                onChange={(e) => handleChange("description", e.target.value)}
              />
            </div>

            {(field.fieldType === "select" || field.fieldType === "multiselect") && (
              <div className="grid gap-2">
                <Label htmlFor="edit-options">Options (comma separated)</Label>
                <Input
                  id="edit-options"
                  value={field.options?.join(", ") || ""}
                  onChange={(e) =>
                    handleChange(
                      "options",
                      e.target.value.split(",").map((opt) => opt.trim()),
                    )
                  }
                  placeholder="Option 1, Option 2, Option 3"
                  required
                />
              </div>
            )}

            <div className="grid gap-2">
              <Label htmlFor="edit-validation">Validation Pattern (regex)</Label>
              <Input
                id="edit-validation"
                value={field.validation || ""}
                onChange={(e) => handleChange("validation", e.target.value)}
                placeholder="e.g. ^[A-Za-z0-9]+$"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="edit-required"
                checked={field.required || false}
                onCheckedChange={(checked) => handleChange("required", checked === true)}
              />
              <Label htmlFor="edit-required">Required field</Label>
            </div>
          </div>
          <DialogFooter>
            <Button type="submit">Save changes</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
