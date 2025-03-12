import { DevPanelSheet } from "../devpanel/devpanel";
import { FlowErrorPanel } from "../error/reactFlowError";

export default function PanelBottomCenter() {
  return (
    <div className="flex items-center space-x-2">
      <FlowErrorPanel />
      <DevPanelSheet />
    </div>
  )
}
