import { Button } from "@/components/ui/button";
import { SimDataState, SimPropertyWindowStore } from "@/states/simDataState";
import { CompDataI } from "@/types/component";
import { Handle, Node, NodeProps, Position } from "@xyflow/react"
import { Blocks, ChevronsLeft, ChevronsLeftRightEllipsis, ChevronsRight, HomeIcon, MoreVertical } from "lucide-react";
import { useEffect, useState } from "react";

export interface NodeDisplayContentI {
  type: string;
  id: string;
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
  const { get_comp_by_id, componentData } = SimDataState()
  const { setPropertyWindowOn, setPropertyWindowData } = SimPropertyWindowStore()
  const [content, setContent] = useState<CompDataI | null>(null);
  useEffect(() => {
    const data = get_comp_by_id(props.id)
    setContent(data)
  }, [componentData])
  const onDoubleClick = () => {
    if (content != null) {
      setPropertyWindowData(content)
      setPropertyWindowOn(true)
    }
  }
  return (
    <div className="flex flex-col gap-y-2" onDoubleClick={onDoubleClick}>
      <div className="flex flex-col rounded-lg w-[300px] border bg-white drop-shadow-lg " >
        <div className="h-[12px] rounded-t-lg" style={{ backgroundColor: content?.color ?? "black" }} ></div>
        <div className="flex flex-col p-3 rounded-lg "  >
          <div className="flex flex-row justify-between items-center " >
            <div className="flex flex-row gap-x-2 " >
              <div className="flex p-1 rounded-lg w-6 h-6 items-center bg-secondary border border-primary justify-center" >
                <HomeIcon />
              </div>
              <h1 className="text-secondary-foreground" > {content?.typeName ?? "N/A"} </h1>
            </div>
            <div className="flex">
              <Button variant="ghost"><MoreVertical /> </Button>
            </div>
          </div>
          <div className="flex flex-col my-1" >
            <h3 className="text-2xl font-semibold" style={{ color: content?.color ?? "black" }} > {content?.compName ?? "N/A"} </h3>
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
      {content?.connectors?.map((c) => {
        switch (c.flow) {
          case "inout":
            return (
              <div className="flex flex-row border rounded-lg bg-white p-3 drop-shadow-lg" >
                <Handle type="target" id={`${c.name}-in`} position={Position.Left} isConnectable={true} />
                <Handle type="source" id={`${c.name}-out`} position={Position.Right} isConnectable={true} isConnectableStart={true} />
                <div className="flex flex-row gap-x-2 items-center justify-between w-full" >
                  {c.name}
                  <ChevronsLeftRightEllipsis />
                </div>
              </div>
            )
          case "in":
            return (
              <div className="flex flex-row border rounded-lg bg-white p-3 drop-shadow-lg" >
                <Handle type="target" id={`${c.name}-in`} position={Position.Left} isConnectable={true} />
                <div className="flex flex-row gap-x-2 items-center justify-between w-full" >

                  {c.name}
                  <ChevronsLeft />
                </div>
              </div>
            )
          case "out":
            return (
              <div className="flex flex-row border rounded-lg bg-white p-3 drop-shadow-lg" >
                <Handle type="source" id={`${c.name}-out`} position={Position.Right} isConnectable={true} isConnectableStart={true} />
                <div className="flex flex-row gap-x-2 items-center justify-between w-full" >
                  {c.name}
                  <ChevronsRight />
                </div>
              </div>
            )
          default:
            return null
        }
      })}
      {
        content?.GenData?.types?.map((t) => {
          return (
            <div className="flex flex-row border rounded-lg bg-white p-3 drop-shadow-lg" >
              <Handle type="source" id={`${t}-out`} position={Position.Right} isConnectable={true} isConnectableStart={true} />
              <div className="flex flex-row gap-x-2 items-center justify-between w-full" >
                {t}
                <Blocks className="w-4 h-4" />
              </div>
            </div>
          )
        })
      }
      {/* <div className="flex flex-row border rounded-lg bg-white p-3 drop-shadow-lg" >
        <Handle type="source" id="b" position={Position.Left} isConnectable={true} isConnectableStart={true} />
        connector
      </div> */}
    </div>
  )
}
