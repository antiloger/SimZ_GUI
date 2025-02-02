import { useState } from "react"
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function PropertyBuilder() {
  const [formData, setFormData] = useState({
    name: "David Kim",
    email: "d.kim@company.com",
    location: "Seoul, KR",
    status: "Active",
    balance: "$1,000.00",
  })
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.name, e.target.value)
  }

  return (
    <div className="mx-auto w-full">
      <form>
        <div className="overflow-hidden rounded-lg border border-border bg-background [&_tr:last-child]:border-b-0">
          <Table>
            <TableBody>
              <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                <TableCell className="bg-muted/50 py-2 font-medium">Name</TableCell>
                <TableCell className="py-0 pr-0">
                  <Input
                    name="name"
                    defaultValue={formData.name}
                    onChange={handleInputChange}
                    className="border-none p-0 shadow-none focus-visible:ring-0"
                  />
                </TableCell>
              </TableRow>
              <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                <TableCell className="bg-muted/50 py-2 font-medium">Email</TableCell>
                <TableCell className="py-0 pr-0">
                  <Input
                    name="email"
                    type="email"
                    defaultValue={formData.email}
                    onChange={handleInputChange}
                    className="border-none p-0 shadow-none focus-visible:ring-0"
                  />
                </TableCell>
              </TableRow>
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



interface RowInputProps {
  label: string;
  name: string;
  type: string;
  defaultValue: string | number | undefined;
  onChange: React.ChangeEventHandler<HTMLInputElement> | undefined;
}

function RowInput({ label, name, type, defaultValue, onChange }: RowInputProps) {
  return (
    <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
      <TableCell className="bg-muted/50 py-2 font-medium">{label}</TableCell>
      <TableCell className="py-0 pr-0">
        <Input
          name={name}
          type={type}
          defaultValue={defaultValue}
          onChange={onChange}
          className="border-none p-0 shadow-none focus-visible:ring-0"
        />
      </TableCell>
    </TableRow>
  )
}

interface RowSelectProps {
  label: string;
  options: { name: string, value: string }[]
  defaultValue: string;
  onChange: (value: string) => void;
}

function RowSelect({ label, options, defaultValue, onChange }: RowSelectProps) {
  return (
    <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
      <TableCell className="bg-muted/50 py-2 font-medium">{label}</TableCell>
      <TableCell className="p-0">
        <Select defaultValue={defaultValue} onValueChange={onChange}>
          <SelectTrigger className="w-full border-0 focus:ring-0">
            <SelectValue placeholder="Select location" />
          </SelectTrigger>
          <SelectContent>
            {
              options.map(({ name, value }) => (
                <SelectItem value={value} >{name}</SelectItem>
              ))
            }
          </SelectContent>
        </Select>
      </TableCell>
    </TableRow>
  )
}
