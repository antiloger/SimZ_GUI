import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronDown, Component, Play, Plus } from "lucide-react";

export default function PanelTopRight() {
  return (
    <div className="flex items-center space-x-2">
      <AddComponentBtn />
      <RunComponentBtn />
    </div>
  )
}

interface componetTypes {
  type: string;
  name: string;
  id: string;
}

interface componentSlots {
  type: string;
  slots: componetTypes[];
}

function AddComponentBtn() {

  const tpp: componentSlots[] = [];
  for (let i = 0; i < 4; i++) {
    const types: componetTypes[] = []
    for (let k = 0; k < 7; k++) {
      types.push(
        {
          type: `sub_type_${k}`,
          id: `${k}`,
          name: `name_${k}`,
        }
      )
    }
    tpp.push({
      type: `type_${i}`,
      slots: types
    })
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">Add Component</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] h-2/3">
        <DialogHeader>
          <DialogTitle>Add Component</DialogTitle>
          <DialogDescription>
            Make changes to your profile here. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <div>
          <Input placeholder="Search component" />
        </div>
        <ScrollArea className="flex flex-col" >
          <div className="flex flex-col" >
            {
              tpp.map((item) => (
                <Collapsible className="group/collapsible">
                  <div className="flex flex-col mb-2">
                    <CollapsibleTrigger>
                      <div className="flex flex-row justify-between items-center py-2 gap-x-2 font-semibold" >
                        <Component className="w-4 h-4" />
                        {item.type}
                        <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
                      </div>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <div className="w-full flex flex-col" >
                        {
                          item.slots.map((itx) => (
                            <div className="flex flex-row justify-between pl-6 pr-2 items-center py-2 rounded-md hover:bg-secondary hover:font-semibold" >
                              <div>
                                {itx.type}
                              </div>
                              <div>
                                <Plus className="w-4 h-4" />
                              </div>
                            </div>
                          ))
                        }
                      </div>
                    </CollapsibleContent>
                    <hr />
                  </div>
                </Collapsible>
              ))
            }
          </div>
        </ScrollArea>
        {/* <DialogFooter> */}
        {/*   <Button type="submit">Add</Button> */}
        {/* </DialogFooter> */}
      </DialogContent>
    </Dialog>
  )
}


function RunComponentBtn() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm"> <Play /> Run</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit profile</DialogTitle>
          <DialogDescription>
            Make changes to your profile here. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input
              id="name"
              defaultValue="Pedro Duarte"
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="username" className="text-right">
              Username
            </Label>
            <Input
              id="username"
              defaultValue="@peduarte"
              className="col-span-3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Save changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
