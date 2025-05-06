import { useInputFields } from "./input-context"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Pencil, Trash2, Eye, EyeOff } from "lucide-react"
import { useState } from "react"
import { EditFieldDialog } from "./edit-field-form"

export function FieldsTable() {
  const { fields, removeField, toggleVisibility } = useInputFields()
  const [editingField, setEditingField] = useState<string | null>(null)

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[200px]">Field Name</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Required</TableHead>
            <TableHead>Visible</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fields.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="h-24 text-center">
                No fields added yet. Use the form to add fields.
              </TableCell>
            </TableRow>
          ) : (
            fields.map((field) => (
              <TableRow key={field.id}>
                <TableCell className="font-medium">{field.inputName}</TableCell>
                <TableCell>{field.fieldType}</TableCell>
                <TableCell>{field.description || "-"}</TableCell>
                <TableCell>
                  <Checkbox checked={field.required} disabled />
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleVisibility(field.id)}
                    title={field.visible ? "Hide field" : "Show field"}
                  >
                    {field.visible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  </Button>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="icon" onClick={() => setEditingField(field.inputName)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => removeField(field.inputName)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {editingField && (
        <EditFieldDialog fieldId={editingField} open={!!editingField} onClose={() => setEditingField(null)} />
      )}
    </div>
  )
}
