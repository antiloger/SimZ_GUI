import { ScrollArea } from "@/components/ui/scroll-area";
import { SimDataState } from "@/states/simDataState";
import { CompDataI } from "@/types/component";
import { useEffect, useState } from "react";
import DefaultInfoForm from "../formBuilder/defaultInfoForm";

interface PropteryFormsProps {
  compId: string
}

export default function PropteryForms({ compId }: PropteryFormsProps) {

  return (
    <ScrollArea className="flex-grow  h-[calc(100vh-120px)]">
      <div className="grid grid-cols-2 gap-2" >
        <div className="col-span-2 w-full" >
          <h1 className="text-lg py-4 font-semibold" >Inputs</h1>
        </div>
      </div>
    </ScrollArea>
  )
}
