import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { SaveStateFlowAsJson } from "./saveState"

export function DevPanelSheet() {

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" >Dev Panel</Button>
      </SheetTrigger>
      <SheetContent className=" w-[80vw] sm:max-w-full" >
        <SheetHeader>
          <SheetTitle>Dev Panel</SheetTitle>
          <SheetDescription>
            This is the development panel.In here you can see all the state and some of the dev only actions.
          </SheetDescription>
        </SheetHeader>
        <div className="grid lg:grid-cols-3 md:grid-cols-2 sm:grid-cols-1 mt-10">
          <div className="flex flex-col p-2 border rounded-md" >
            <div className="pb-2" >Actions Panel</div>
            <Separator className="mb-2" />
            <div className="flex flex-col gap-2">
              <Button variant="outline" onClick={SaveStateFlowAsJson} >Save Workflow State </Button>
              <Button variant="outline" >Save Component Data State</Button>
            </div>
          </div>
        </div>
        <SheetFooter>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
