import { ViewPortData } from '@/types/flow';
import { useSocketStore } from '@/utils/socketIo';
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
import { ErrorState } from './errorState';

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
  getJsonNodes: () => FlowNode[];
  getJsonEdges: () => Edge[];
  loadNodesEdges: (projectName: string) => Promise<void>;
  setViewport: (newViewport: any) => void
  addNodes: (nodes: FlowNode[]) => void;
  removeNode: (nodeId: string) => void;
  removeEdge: (edgeId: string) => void;
}


export const FlowState = create<FlowStateT>((set, get) => ({
  nodes: [],
  edges: [],
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
  getJsonNodes: () => {
    return JSON.parse(JSON.stringify(get().nodes));
  },
  getJsonEdges: () => {
    return JSON.parse(JSON.stringify(get().edges));
  },
  loadNodesEdges: async (projectName: string) => {
    const { get_data_edge, get_data_node } = useSocketStore.getState();
    try {
      const nodes = await get_data_node(projectName);
      const edges = await get_data_edge(projectName);
      set({ nodes, edges });
    } catch (error) {
      const { setError } = ErrorState.getState();
      setError({
        header: 'Error loading nodes and edges',
        body: 'Failed to load nodes and edges. Please try again.',
      })
    }
  },
  setViewport: (newViewport) => set({ viewport: newViewport }),
  addNodes: (nodes: FlowNode[]) => {
    set((s) => ({
      nodes: [...s.nodes, ...nodes]
    }))
  },
  removeNode: (nodeId: string) => {
    set((s) => ({
      nodes: s.nodes.filter((node) => node.id !== nodeId)
    }))
  },
  removeEdge: (edgeId: string) => {
    set((s) => ({
      edges: s.edges.filter((edge) => edge.id !== edgeId)
    }))
  }
}))
