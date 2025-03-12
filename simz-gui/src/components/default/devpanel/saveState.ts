import { FlowState } from "@/states/flowState";

export const SaveStateFlowAsJson = () => {
  const { nodes, edges } = FlowState.getState()
  const state = {
    nodes: nodes,
    edges: edges,
  };

  const json = JSON.stringify(state, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  // Trigger the file download
  const a = document.createElement("a");
  a.href = url;
  a.download = "reactflow-state.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
