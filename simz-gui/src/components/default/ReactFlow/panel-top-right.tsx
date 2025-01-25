import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FlowState } from "@/states/flowState";
import { SimDataState } from "@/states/simDataState";
import { ChevronDown, Play, Plus } from "lucide-react";
import { useState } from "react";

export default function PanelTopRight() {
  return (
    <div className="flex items-center space-x-2">
      <AddComponentBtn />
      <RunComponentBtn />
    </div>
  )
}

function AddComponentBtn() {


  const { componentRegisterI } = SimDataState(); // Accessing Zustand store
  const [searchQuery, setSearchQuery] = useState("");
  const { setNodes } = FlowState();

  // Filter categories and compTypes based on the search query
  const filteredData = Object.entries(componentRegisterI).reduce((acc, [category, compTypes]) => {
    const filteredCompTypes = Object.keys(compTypes).filter((compType) =>
      compType.toLowerCase().includes(searchQuery.toLowerCase())
    );
    if (filteredCompTypes.length > 0) {
      acc[category] = filteredCompTypes;
    }
    return acc;
  }, {} as { [category: string]: string[] });

  // const onClickCompType = (cat: string, type: string) => {
  //   const TypeData = componentRegisterI[cat][type];
  //   setNodes([{
  //     type: 
  //   }])
  // }

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
          <Input
            placeholder="Search component"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <ScrollArea className="flex flex-col" >
          <div className="flex flex-col">
            {Object.entries(filteredData).map(([category, compTypes]) => (
              <Collapsible key={category} className="group/collapsible">
                <div className="flex flex-col mb-2">
                  <CollapsibleTrigger>
                    <div className="flex flex-row justify-between items-center py-2 gap-x-2 font-semibold">
                      {category}
                      <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
                    </div>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="w-full flex flex-col">
                      {compTypes.map((compType) => (
                        <div
                          key={compType}
                          className="flex flex-row justify-between pl-6 pr-2 items-center py-2 rounded-md hover:bg-secondary hover:font-semibold"
                        // onClick={ }
                        >
                          <div>{compType}</div>
                          <div>
                            <Plus className="w-4 h-4" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </CollapsibleContent>
                  <hr />
                </div>
              </Collapsible>
            ))}
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


{/* <div className="flex flex-col" > */ }
{/*   { */ }
{/*     tpp.map((item) => ( */ }
{/*       <Collapsible className="group/collapsible"> */ }
{/*         <div className="flex flex-col mb-2"> */ }
{/*           <CollapsibleTrigger> */ }
{/*             <div className="flex flex-row justify-between items-center py-2 gap-x-2 font-semibold" > */ }
{/*               <Component className="w-4 h-4" /> */ }
{/*               {item.type} */ }
{/*               <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" /> */ }
{/*             </div> */ }
{/*           </CollapsibleTrigger> */ }
{/*           <CollapsibleContent> */ }
{/*             <div className="w-full flex flex-col" > */ }
{/*               { */ }
{/*                 item.slots.map((itx) => ( */ }
{/*                   <div className="flex flex-row justify-between pl-6 pr-2 items-center py-2 rounded-md hover:bg-secondary hover:font-semibold" > */ }
{/*                     <div> */ }
{/*                       {itx.type} */ }
{/*                     </div> */ }
{/*                     <div> */ }
{/*                       <Plus className="w-4 h-4" /> */ }
{/*                     </div> */ }
{/*                   </div> */ }
{/*                 )) */ }
{/*               } */ }
{/*             </div> */ }
{/*           </CollapsibleContent> */ }
{/*           <hr /> */ }
{/*         </div> */ }
{/*       </Collapsible> */ }
{/*     )) */ }
{/*   } */ }
{/* </div> */ }
