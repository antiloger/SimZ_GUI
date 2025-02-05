import { useEffect, useState } from "react"
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { SimDataState } from "@/states/simDataState"
import { CompDataI } from "@/types/component"

interface DefaultInfoProp {
  compId: string
}


export default function DefaultInfoForm({ compId }: DefaultInfoProp) {
  const { get_comp_by_id, componentData, change_comp_default_values } = SimDataState()
  const [formError, setError] = useState({
    compName: null,
    color: null,
  })
  const [compData, setCompData] = useState<CompDataI | null>(null)

  useEffect(() => {
    const data = get_comp_by_id(compId)
    setCompData(data)
  }, [compId, componentData])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    console.log(e.target.name, e.target.value)
    if (compData?.id != null) {

      const res = change_comp_default_values(compData.id, name, value)
      if (!res) {
        setError((prev) => ({
          ...prev,
          [name]: res
        }))
      } else {
        setError((prev) => ({
          ...prev,
          [name]: null
        }))
      }
    }
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
                    name="compName"
                    defaultValue={compData?.compName}
                    onChange={handleInputChange}
                    className="border-none p-0 shadow-none focus-visible:ring-0"
                  />
                  {
                    formError && <p className="text-red-800 text-xs" >{formError.compName}</p>
                  }
                </TableCell>
              </TableRow>
              <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                <TableCell className="bg-muted/50 py-2 font-medium">Id</TableCell>
                <TableCell className="py-0 pr-0">
                  <Input
                    name="id"
                    defaultValue={compData?.id}
                    disabled
                    className="border-none p-0 shadow-none focus-visible:ring-0"
                  />
                </TableCell>
              </TableRow>
              <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                <TableCell className="bg-muted/50 py-2 font-medium">Component Type</TableCell>
                <TableCell className="py-0 pr-0">
                  <Input
                    name="typeName"
                    defaultValue={compData?.typeName}
                    disabled
                    className="border-none p-0 shadow-none focus-visible:ring-0"
                  />
                </TableCell>
              </TableRow>
              <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                <TableCell className="bg-muted/50 py-2 font-medium">Category</TableCell>
                <TableCell className="py-0 pr-0">
                  <Input
                    name="category"
                    defaultValue={compData?.category}
                    disabled
                    onChange={handleInputChange}
                    className="border-none p-0 shadow-none focus-visible:ring-0"
                  />
                </TableCell>
              </TableRow>
              <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                <TableCell className="bg-muted/50 py-2 font-medium">Color</TableCell>
                <TableCell className="py-0 pr-0">
                  <Input
                    name="color"
                    defaultValue={compData?.color}
                    onChange={handleInputChange}
                    className="border-none p-0 shadow-none focus-visible:ring-0"
                  />
                  {
                    formError && <p className="text-red-800 text-xs" >{formError.color}</p>
                  }
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
