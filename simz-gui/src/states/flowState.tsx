import { initialEdges, initialNodes } from '@/mockData/flowState';
import { ViewPortData } from '@/types/flow';
import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Edge,
  type Node,
  type OnConnect,
  type OnEdgesChange,
  type OnNodesChange
} from '@xyflow/react';
import { create } from 'zustand'

export type FlowNode = Node;

export type FlowStateT = {
  nodes: FlowNode[];
  edges: Edge[];
  viewport: ViewPortData;
  onNodesChange: OnNodesChange<FlowNode>;
  onEdgesChange: OnEdgesChange<Edge>;
  onConnect: OnConnect;
  setNodes: (nodes: FlowNode[]) => void;
  setEdges: (edges: Edge[]) => void;
  setViewport: (newViewport: any) => void
  addNodes: (nodes: FlowNode[]) => void;
}


export const FlowState = create<FlowStateT>((set, get) => ({
  nodes: initialNodes,
  edges: initialEdges,
  viewport: { x: 0, y: 0, zoom: 1 },
  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    })
  },
  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  onConnect: (connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
  },
  setNodes: (nodes) => {
    set({ nodes });
  },
  setEdges: (edges) => {
    set({ edges });
  },
  setViewport: (newViewport) => set({ viewport: newViewport }),
  addNodes: (nodes: FlowNode[]) => {
    set((s) => ({
      nodes: [...s.nodes, ...nodes]
    }))
  }
}))
