import { Button } from "@/components/ui/button";
import { Plus, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";


export default function ConnectorForm() {
  return (
    <div className="flex flex-col gap-y-2 mt-4" >
      <div className="flex flex-row justify-between items-center">
        <div>
          <h1 className="font-semibold text-lg text-primary pb-2" >Connectors</h1>
        </div>
        <div>
          <AddConnectorForm />
        </div>
      </div>
      <div>
        <div className="flex rounded-lg border border-dashed h-10 bg-gray-100 items-center justify-center" >
          <p className="text-sm ">Add Connectors</p>
        </div>
      </div>
    </div>
  )
}


const connectorOptions = [
  { value: "mysql", label: "MySQL" },
  { value: "postgres", label: "PostgreSQL" },
  { value: "mongodb", label: "MongoDB" },
  { value: "redis", label: "Redis" },
]

export function AddConnectorForm() {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedConnector, setSelectedConnector] = useState("")
  const [queue, setQueue] = useState<string[]>([])
  const [onCheck, setOnCheck] = useState<string | undefined>("in&out")
  const [conName, setConName] = useState<string>("")
  const [error, setError] = useState<string | null>(null)

  const handleAdd = () => {
    setError(null)
    if (selectedConnector && !queue.includes(selectedConnector)) {
      setQueue([...queue, selectedConnector])
      setSelectedConnector("")
    }
  }

  const onSubmit = () => {
    setError(null)
    if (conName.trim() === "") {
      setError("Set Connection Name")
    } else if (queue.length === 0) {
      setError("Add connection types")
    } else {
      console.log(conName, onCheck, queue)
      setIsOpen(false)
      setQueue([])
      setOnCheck("in&out")
      setConName("")
    }
  }

  const handleRemove = (connector: string) => {
    setQueue(queue.filter((item) => item !== connector))
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen} >
      <DialogTrigger asChild>
        <Button size="sm" variant="secondary">
          <Plus className="mr-2 h-4 w-4" />
          Add
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Connectors</DialogTitle>
          <DialogDescription>Select connectors to add to Pool.</DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div>
            <Input placeholder="connection name" value={conName} onChange={(e) => setConName(e.target.value)} ></Input>
          </div>
          <div>
            <RadioGroup className="flex flex-row gap-x-4" value={onCheck} onValueChange={setOnCheck} >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="in" id="r1" />
                <Label htmlFor="r1">In</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="out" id="r2" />
                <Label htmlFor="r2">Out</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="in&out" id="r3" />
                <Label htmlFor="r3">In & Out</Label>
              </div>
            </RadioGroup>
          </div>
          <div className="flex w-full items-center gap-4">
            <Select value={selectedConnector} onValueChange={setSelectedConnector}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select connector" />
              </SelectTrigger>
              <SelectContent>
                {connectorOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleAdd} disabled={!selectedConnector}>
              Add to Pool
            </Button>
          </div>
          {queue.length > 0 && (
            <div className="border rounded-md p-4">
              <h4 className="text-sm font-medium mb-2">Connector Pool</h4>
              <ul className="space-y-2">
                {queue.map((connector) => (
                  <li key={connector} className="flex items-center justify-between bg-muted p-2 rounded-md">
                    <span>{connectorOptions.find((option) => option.value === connector)?.label}</span>
                    <Button variant="ghost" size="sm" onClick={() => handleRemove(connector)}>
                      <X className="h-4 w-4" />
                    </Button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <DialogFooter>
          {
            error && (
              <p className="text-red-400">{error}</p>
            )
          }
          <Button onClick={onSubmit} >Add Connector</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
