import { Button } from "@/components/ui/button";
import { Pencil, Plus, Trash, X } from "lucide-react";
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
import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { SimDataState } from "@/states/simDataState";
import { ConnectorData } from "@/types/component";
import { v4 as uuidv4 } from "uuid";

interface ConnectorFormProps {
  comId: string
}

export default function ConnectorForm({ comId }: ConnectorFormProps) {
  const { getAllConnectors } = SimDataState()
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [connectors, setConnectors] = useState<ConnectorData[] | null>(null)
  useEffect(() => {
    const data = getAllConnectors(comId)
    setConnectors(data)
  }, [isAddOpen, getAllConnectors])

  return (
    <div className="flex flex-col gap-y-2 mt-4" >
      <div className="flex flex-row justify-between items-center">
        <div>
          <h1 className="font-semibold text-lg text-primary pb-2" >Connectors</h1>
        </div>
        <div>
          <AddConnectorForm
            isOpen={isAddOpen}
            setIsOpen={setIsAddOpen}
            comId={comId}
            triggerComponent={<Button size="sm" variant="outline">
              <Plus className="mr-2 h-4 w-4" />
              Connectors
            </Button>}
          />
        </div>
      </div>
      <div className="flex flex-col gap-y-2" >
        {connectors ? (
          connectors.map((connector) => (
            <div key={connector.name} className="flex flex-row justify-between   bg-muted/50 items-center px-4 py-2 hover:bg-muted/100 border  rounded-md" >
              <p>{connector.name}</p>
              <div className="px-2 bg-gray-100 border rounded-md text-gray-500 border-gray-500" > {connector.flow} </div>
              <div className="flex flex-row gap-x-2" >
                <AddConnectorForm
                  comId={comId}
                  connectorId={connector.id}
                  triggerComponent={<Button variant="outline" size="sm" >
                    <Pencil className="h-4 w-4" />
                  </Button>}
                  isOpen={isEditOpen}
                  setIsOpen={setIsEditOpen}
                />
                <Button variant="outline" size="sm" >
                  <Trash className="h-4 w-4" color="red" />
                </Button>
              </div>
            </div>
          ))
        ) : (
          <div className="flex rounded-lg border border-dashed h-10 bg-gray-100 items-center justify-center" >
            <p className="text-sm ">Add Connectors</p>
          </div>
        )}
      </div>
    </div>
  )
}


// const connectorOptions = [
//   { value: "mysql", label: "MySQL" },
//   { value: "postgres", label: "PostgreSQL" },
//   { value: "mongodb", label: "MongoDB" },
//   { value: "redis", label: "Redis" },
// ]

interface AddConnectorFormProps {
  isOpen: boolean,
  setIsOpen: (isOpen: boolean) => void,
  comId: string,
  triggerComponent: React.ReactNode,
  connectorId?: string
}

export function AddConnectorForm({ comId, connectorId, triggerComponent, isOpen, setIsOpen }: AddConnectorFormProps) {
  const [selectedConnector, setSelectedConnector] = useState("")
  const [connectionTypes, setConnectionTypes] = useState<string[]>([])
  const [queue, setQueue] = useState<string[]>([])
  const [onCheck, setOnCheck] = useState<string | undefined>("inout")
  const [conName, setConName] = useState<string>("")
  const [error, setError] = useState<string | null>(null)
  const { getAllGenTypeNames, addConnector, getConnectorByName, updateConnector } = SimDataState()

  useEffect(() => {
    const data = getAllGenTypeNames()
    setConnectionTypes(data)
    if (connectorId) {
      console.log("Connection id", connectorId)
      const connector = getConnectorByName(comId, connectorId)
      if (connector) {
        setQueue(connector.type)
        setOnCheck(connector.flow)
        setConName(connector.name)
      } else {
        setError("Connector not found")
      }
    }
  }, [])

  const handleAdd = () => {
    setError(null)
    if (selectedConnector && !queue.includes(selectedConnector)) {
      setQueue([...queue, selectedConnector])
      setSelectedConnector("")
    }
  }

  const onSubmit = () => {
    setError(null)
    if (!comId) return

    if (conName.trim() === "") {
      setError("Set Connection Name")
    } else if (queue.length === 0) {
      setError("Add connection types")
    } else {
      console.log(conName, onCheck, queue)
      if (!onCheck) {
        setError("Select direction")
        return
      }
      if (connectorId) {
        updateConnector(comId, connectorId, {
          id: connectorId,
          name: conName,
          type: queue,
          flow: onCheck,
          validation: ""
        })
        setIsOpen(false)
        setQueue([])
        setOnCheck("in&out")
        setConName("")
        return
      }
      const connectorExt = getConnectorByName(comId, conName)
      if (connectorExt) {
        setError("Connector already exists")
        return
      }
      const connectorIdNew = uuidv4()
      // TODO: Add validation
      const connector: ConnectorData = {
        id: connectorIdNew,
        name: conName,
        type: queue,
        flow: onCheck,
        validation: ""
      }
      console.log(connector)
      addConnector(comId, connector)
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
        {triggerComponent}
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
                <RadioGroupItem value="inout" id="r3" />
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
                {connectionTypes.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
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
                    <span>{connectionTypes.find((option) => option === connector)}</span>
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
          <Button onClick={onSubmit} >{connectorId ? "Update Connector" : "Add Connector"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
