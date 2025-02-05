import { useEffect, useState } from "react"
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { SimDataState } from "@/states/simDataState";
import { InputFieldFormat } from "@/types/component";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

interface PropertyBuilderPops {
  category: string | null;
  compType: string | null;
  id: string | null;
}

export default function PropertyBuilderFrom({ category, compType, id }: PropertyBuilderPops) {
  const {
    get_comp_input_by_id,
    get_comp_struct_input_out,
    change_comp_input_values,
    componentData
  } = SimDataState()
  const [formStruct, setFormStruct] = useState<InputFieldFormat[]>([])
  const [formData, setFormData] = useState<{ [key: string]: number | string | boolean | string[] | number[] | null }>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (category === null || compType === null || id === null) return
    const compIStruct = get_comp_struct_input_out(category, compType);
    const compIData = get_comp_input_by_id(id);
    if (compIStruct != null) {
      setFormStruct(compIStruct)
    }
    if (compIData != null) {
      setFormData(compIData)
    }
  }, [componentData, category, compType, id])

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

  const handleChange = (name: string, value: string | number | boolean) => {
    if (category === null || compType === null || id === null) return
    console.log("Manual", name, value)
    const field = formStruct.find((f) => f.inputName === name)
    if (field) {
      const error = validateField(field, value)
      setErrors((prev) => ({ ...prev, [name]: error }))
      // setFormData((prev) => ({ ...prev, [name]: value }))
      change_comp_input_values(id, name, value)
    }
  }

  const renderField = (field: InputFieldFormat) => {

    return (
      <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
        <TableCell className="bg-muted/50 py-2 font-medium">{field.inputName}</TableCell>
        {field.fieldType === "text" && (
          <TableCell className="py-0 pr-0">
            <Input
              type="text"
              value={formData[field.inputName]?.toString() ?? ""}
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
              value={Number(formData[field.inputName]) ?? 0}
              onChange={(e) => handleChange(field.inputName, e.target.value)}
              className="border-none p-0 shadow-none focus-visible:ring-0"
            />
            {errors[field.inputName] && <p className="mt-1 text-sm text-red-500">{errors[field.inputName]}</p>}
          </TableCell>
        )}
        {field.fieldType === "checkbox" && (
          <TableCell className="py-2 px-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                checked={Boolean(formData[field.inputName]) ?? false}
                onCheckedChange={(value) => handleChange(field.inputName, value)}
              />
              <Label htmlFor="notifications">{field.description}</Label>
            </div>
            {errors[field.inputName] && <p className="mt-1 text-sm text-red-500">{errors[field.inputName]}</p>}
          </TableCell>
        )}
        {(field.fieldType === "select" || field.fieldType === "multiselect") && (
          <TableCell className="p-0">
            <Select value={formData[field.inputName]?.toString()} onValueChange={(value) => handleChange(field.inputName, value)}>
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

        {/* TODO: add fn to Display checkbox */}
        <TableCell >
          <Checkbox />
        </TableCell>
      </TableRow>
    )
  }

  return (
    <div className="mx-auto w-full">
      <form>
        <div className="overflow-hidden rounded-lg border border-border bg-background [&_tr:last-child]:border-b-0">
          <Table>
            <TableBody>
              {formStruct.map(renderField)}
            </TableBody>
          </Table>
        </div>
        {/* <div className="mt-4 flex justify-end"> */}
        {/*   <Button type="submit">Save Changes</Button> */}
        {/* </div> */}
      </form>
    </div>
  )
}
