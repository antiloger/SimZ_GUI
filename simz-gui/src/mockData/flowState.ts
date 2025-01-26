import { FlowNode } from "@/states/flowState";


export const initialNodes = [
  {
    id: '4',
    type: 'dynComp',
    data: {
      name: 'Machine 01',
      type: 'Resource',
      color: "blue",
      notify: false,
      data: []
    },
    position: { x: 350, y: 350 },

  },
  {
    id: '5',
    type: 'dynComp',
    data: {
      name: 'Machine 02',
      type: 'queue',
      color: "green",
      notify: false,
      data: []
    },
    position: { x: 350, y: 350 },

  }
] as FlowNode[];

import { type Edge } from '@xyflow/react';

export const initialEdges = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
] as Edge[];
