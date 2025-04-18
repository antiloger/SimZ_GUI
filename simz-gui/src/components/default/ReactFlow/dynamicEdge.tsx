import { BaseEdge } from '@xyflow/react';

export default function DynCompEdge(props: any) {
  return (
    <>
      <BaseEdge {...props} />
      {/* Optional: Add custom rendering */}
      {/* <EdgeLabelRenderer>custom stuff</EdgeLabelRenderer> */}
    </>
  );
}
