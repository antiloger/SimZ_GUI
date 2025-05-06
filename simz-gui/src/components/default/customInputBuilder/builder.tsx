import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import TableInputForm from "./table-input-form";
import { InputFieldProvider } from "./input-context";
import { InputFieldManager } from "./input-field-manager";
import { Plus } from "lucide-react";

function CustomeInputBuilder({ compId }: { compId: string }) {
  return (
    <div className="flex flex-col w-full gap-y-2">
      <InputFieldProvider compId={compId} >
        <div className="flex flex-row justify-between" >
          <div className="flex flex-row" >
            <h2 className="text-lg font-semibold">Custom Input</h2>
          </div>
          <div className="flex flex-row" >
            <DialogCustomInput />
          </div>
        </div>
        <TableInputForm compId={compId} />
      </InputFieldProvider>
    </div>
  )
}

export function DialogCustomInput() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Plus /> Add Input
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Share link</DialogTitle>
        </DialogHeader>
        <InputFieldManager />
      </DialogContent>
    </Dialog>
  )
}

export default CustomeInputBuilder;
