import { Button } from "@/components/ui/button"
import { MoreVertical, Workflow } from "lucide-react"

interface ComponentDetailBarProps {
  componentName: string
  componentType: string
}

export default function ComponentDetailBar({ componentName, componentType }: ComponentDetailBarProps) {
  return (
    <div className="flex flex-row items-center justify-between p-4 border rounded-lg my-6 ">
      <div className="flex flex-row gap-2 items-center">
        <div className="bg-black w-10 h-10 rounded-lg items-center justify-center" >
          <Workflow color="white" />
        </div>
        <div className="flex flex-col  gap-x-2">
          <h1 className="text-gray-700 font-bold text-sm">Compoenet Name</h1>
          <h1 className=" font-semibold text-lg">{componentName}</h1>
        </div>
      </div>
      <div className="flex flex-col  gap-x-2">
        <div className="flex flex-col items-end gap-2">
          <h1 className="text-gray-700 font-bold text-sm">
            {componentType}
          </h1>
          <Button size="sm">
            <MoreVertical />
          </Button>
        </div>
      </div>
    </div>
  )
}
