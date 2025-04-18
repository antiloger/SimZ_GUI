import { Background, Controls, Panel, ReactFlow } from "@xyflow/react"
import '@xyflow/react/dist/style.css'
import PanelTopRight from "./panel-top-right"
import { FlowState } from "@/states/flowState";
import { useShallow } from 'zustand/react/shallow';
import DynamicComponentNode from "./dynamicComponentNode";
import { useCallback } from "react";
import { ViewPortData } from "@/types/flow";
import PanelBottomCenter from "./panel-bottom-center";
import DynCompEdge from "./dynamicEdge";

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

const EdgeType = {
  dynComp: DynCompEdge
}

export default function Flow() {

  const { nodes, edges, onNodesChange, onEdgesChange, onConnect } = FlowState(
    useShallow(flowSelector),
  );
  const { setViewport } = FlowState();

  // const defaultEdgeOptions: DefaultEdgeOptions = {
  //   label: 
  // }
  const handleMove = useCallback((_: any, viewport: ViewPortData) => {
    setViewport(viewport); // Sync viewport details to Zustand
  }, []);

  // console.log(`node - ${JSON.stringify(nodes, null, 2)}\nedges - ${JSON.stringify(edges, null, 2)}`)

  return (
    <div style={{ height: '100vh' }} >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={NodeType}
        edgeTypes={EdgeType}
        onMove={handleMove}
      >
        <Background />
        <Controls />
        <Panel position="top-right"><PanelTopRight /></Panel>
        <Panel position="bottom-center"> <PanelBottomCenter /> </Panel>
      </ReactFlow>
    </div>
  )
}
