import { Background, Controls, Panel, ReactFlow } from "@xyflow/react"
import '@xyflow/react/dist/style.css'
import PanelTopRight from "./panel-top-right"
import { FlowState } from "@/states/flowState";
import { useShallow } from 'zustand/react/shallow';
import DynamicComponentNode from "./dynamicComponentNode";

const flowSelector = (state) => ({
  nodes: state.nodes,
  edges: state.edges,
  onNodesChange: state.onNodesChange,
  onEdgesChange: state.onEdgesChange,
  onConnect: state.onConnect,
});

const NodeType = {
  dynComp: DynamicComponentNode,
}

export default function Flow() {

  const { nodes, edges, onNodesChange, onEdgesChange, onConnect } = FlowState(
    useShallow(flowSelector),
  );

  // const defaultEdgeOptions: DefaultEdgeOptions = {
  //   label: 
  // }

  return (
    <div style={{ height: '100vh' }} >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={NodeType}
      >
        <Background />
        <Controls />
        <Panel position="top-right"><PanelTopRight /></Panel>
      </ReactFlow>
    </div>
  )
}
