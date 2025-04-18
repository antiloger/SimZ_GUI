import { Button } from "@/components/ui/button";
import { DevPanelSheet } from "../devpanel/devpanel";
import { FlowErrorPanel } from "../error/reactFlowError";
import { Save } from "lucide-react";
import { SaveSimulationData } from "@/utils/projectAction";

export default function PanelBottomCenter() {
  return (
    <div className="flex items-center space-x-2">
      <Button variant="outline" size="sm" className="w-full" onClick={() => SaveSimulationData()} > <Save /> save</Button>
      <FlowErrorPanel />
      <DevPanelSheet />
    </div>
  )
}
