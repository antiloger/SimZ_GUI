import { Button } from "@/components/ui/button";
import { Handle, Node, NodeProps, Position } from "@xyflow/react"
import { HomeIcon, MoreVertical } from "lucide-react";

export interface NodeDisplayContentI {
  type: string;
  iconName: string;
  lable?: string;
  value?: string | number | string[];
  color: string;
}

export type DynamicComponentNodeT = Node<
  {
    name: string;
    type: string;
    id: string;
    notify: boolean;
    color?: string;
    iconName?: string;
    data: NodeDisplayContentI[];
  },
  'dynComp'
>

export default function DynamicComponentNode(props: NodeProps<DynamicComponentNodeT>) {
  return (
    <div className="flex flex-col gap-y-2">
      <div className="flex flex-col rounded-lg w-[300px] border bg-white drop-shadow-lg " >
        <div className="h-[12px] rounded-t-lg" style={{ backgroundColor: props.data?.color ?? "black" }} ></div>
        <div className="flex flex-col p-3 rounded-lg "  >
          <div className="flex flex-row justify-between items-center " >
            <div className="flex flex-row gap-x-2 " >
              <div className="flex p-1 rounded-lg w-6 h-6 items-center bg-secondary border border-primary justify-center" >
                <HomeIcon />
              </div>
              <h1 className="text-secondary-foreground" > {props.data?.type ?? "N/A"} </h1>
            </div>
            <div className="flex">
              <Button variant="ghost"><MoreVertical /> </Button>
            </div>
          </div>
          <div className="flex flex-col my-1" >
            <h3 className="text-2xl font-semibold" style={{ color: props.data?.color ?? "black" }} > {props.data?.name ?? "N/A"} </h3>
          </div>
          <hr className="mt-2" />
        </div>
        <div className="flex flex-col gap-y-2  mx-3 mb-3 " >
          <div className="flex flex-row items-center justify-between py-2 px-4 rounded-lg bg-secondary " >
            <div className="flex flex-row gap-x-2 text-sm">
              {/* <Cylinder className="w-4 h-4" /> */}
              Runner :
            </div>
            <div>
              {"<N/A>"}
            </div>
          </div>
          <div className="flex flex-row items-center justify-between py-2 px-4 rounded-lg bg-secondary " >
            <div className="flex flex-row gap-x-2 text-sm">
              {/* <Sun className="w-4 h-4" /> */}
              Capacity :
            </div>
            <div>
              02
            </div>
          </div>
        </div>
      </div>
      <div className="flex flex-row border rounded-lg bg-white p-3 drop-shadow-lg" >
        <Handle type="target" id="a" position={Position.Right} isConnectable={true} />
        connector
      </div>

      <div className="flex flex-row border rounded-lg bg-white p-3 drop-shadow-lg" >
        <Handle type="source" id="b" position={Position.Left} isConnectable={true} isConnectableStart={true} />
        connector
      </div>
    </div>
  )
}
