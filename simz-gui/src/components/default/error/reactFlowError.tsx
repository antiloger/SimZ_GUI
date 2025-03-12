import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { ErrorState } from "@/states/errorState"
import { CircleX } from "lucide-react"
import { useEffect, useState } from "react"

export function FlowErrorPanel() {
    const { getAllFlowErrors, removeReactFlowError } = ErrorState()
    const [errors, setErrors] = useState(getAllFlowErrors())
    useEffect(() => {
        setErrors(getAllFlowErrors())
    }, [getAllFlowErrors])
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="w-full">Errors [ {errors.length} ]</Button>
      </SheetTrigger>
      <SheetContent side="bottom">
        <SheetHeader>
          <SheetTitle>ERROR Panel - {errors.length}</SheetTitle>
        </SheetHeader>

        <div className="flex flex-col gap-2">
        <ScrollArea className="h-[50vh] md:h-[40vh] lg:h-[30vh]">
            {errors.map((error) => {
                switch (error.type) {
                    case "warning":
                        return (
                            <div key={error.error} className="p-2 rounded-md border border-yellow-500 items-center flex flex-col gap-2 text-yellow-500">
                                <div className="flex flex-row gap-2 justify-between items-center">
                                    <h1>{error.errorType}</h1>
                                    <div className="flex flex-row gap-2">
                                        <h1>{error.componentName}</h1>
                                        <h1>{error.componentId}</h1>
                                        <CircleX onClick={() => removeReactFlowError(error)} />
                                    </div>
                                </div>
                                    <h1>{error.error}</h1>
                            </div>
                        )
                    case "error":
                        return (
                            <div key={error.error} className="p-2 rounded-md border border-red-500 items-center flex flex-col gap-2 text-red-500">
                                <div className="flex flex-row gap-2 justify-between items-center">
                                    <h1>{error.errorType}</h1>
                                    <div className="flex flex-row gap-2">
                                        <h1>{error.componentName}</h1>
                                        <h1>{error.componentId}</h1>
                                        <CircleX />
                                    </div>
                                </div>
                                <h1>{error.error}</h1>
                            </div>
                        )
                    default:
                        return (
                            <div key={error.error} className="p-2 rounded-md border border-gray-500 items-center flex flex-col gap-2 text-gray-500">
                                <div className="flex flex-row gap-2 justify-between items-center">
                                    <h1>{error.errorType}</h1>
                                    <div className="flex flex-row gap-2">
                                        <h1>{error.componentName}</h1>
                                        <h1>{error.componentId}</h1>
                                        <CircleX />
                                    </div>
                                </div>
                                <h1>{error.error}</h1>
                            </div>
                        )
                }
            })}
            </ScrollArea>
        </div>

      </SheetContent>
    </Sheet>
  )
}
