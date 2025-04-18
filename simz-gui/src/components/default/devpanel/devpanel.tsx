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
import { SimDataState } from "@/states/simDataState"
import { FlowState } from "@/states/flowState"
import { useSocketStore } from "@/utils/socketIo"

export function DevPanelSheet() {
  const { genTypesData, componentRegisterI, componentData } = SimDataState()
  const { nodes, edges } = FlowState()
  const { get_registered_component } = useSocketStore();
  const consolelogstate = () => {
    console.log(`
      genTypesData: ${JSON.stringify(genTypesData, null, 2)}\n
      ------------------------------------------------------------\n
      componentRegisterI: ${JSON.stringify(componentRegisterI, null, 2)}\n
      ------------------------------------------------------------\n
      componentData: ${JSON.stringify(componentData, null, 2)}\n
      ------------------------------------------------------------\n
      nodes: ${JSON.stringify(nodes, null, 2)}\n
      ------------------------------------------------------------\n
      edges: ${JSON.stringify(edges, null, 2)}\n
    `)
  }

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
              <Button variant="outline" onClick={consolelogstate} >Console.log() State</Button>
              <Button variant="outline" onClick={() => { get_registered_component() }} >Console.log() fetch get_registered_component</Button>
            </div>
          </div>
        </div>
        <SheetFooter>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
