import { Node, NodeProps } from "@xyflow/react";

export type LogicalComponentNodeT = Node<
  {
    logicName: string;
    logicId: string;
  },
  'logicalComp'
>

export default function LogicalComponentNode(props: NodeProps<LogicalComponentNodeT>) {
  console.log(props.data.logicId)
  return (

    <div className="flex flex-col rounded-lg w-[300px] border bg-white drop-shadow-lg " >
      {props.data.logicName}
    </div>
  )
}
