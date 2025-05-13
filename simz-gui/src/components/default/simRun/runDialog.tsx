import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, CheckCircle, AlertCircle } from "lucide-react"
import { useSocketStore } from "@/utils/socketIo"
import { SimDataState } from "@/states/simDataState"
import { SaveSimulationData } from "@/utils/projectAction"

type SimulationStatus = "idle" | "running" | "completed" | "error"

const defaultSimName = () => {
  const date = new Date()
  const formattedDate = date.toISOString().split("T")[0]
  const formattedTime = date.toTimeString().split(" ")[0].replace(/:/g, "-")
  return `${formattedDate}-${formattedTime}`
}

export function SimulationRunDialog() {
  const [open, setOpen] = useState(false)
  const [simulationName, setSimulationName] = useState(() => defaultSimName())
  const [simulationParams, setSimulationParams] = useState("")
  const [countType, setCountType] = useState("seconds")
  const [simulationRuntime, setSimulationRuntime] = useState(0)
  const [status, setStatus] = useState<SimulationStatus>("idle")
  const [logs, setLogs] = useState<string[]>([])
  const [allowClose, setAllowClose] = useState(true)

  const { run_simulation, on_simulation_run_log, on_sim_run_status, connected } = useSocketStore()
  const { projectName } = SimDataState()

  // Reset the form and state when dialog closes
  useEffect(() => {
    if (!open) {
      setSimulationName(defaultSimName())
      setSimulationParams("")
      setCountType("seconds")
      setSimulationRuntime(0)
      setStatus("idle")
      setLogs([])
      setAllowClose(true)
    }
  }, [open])

  // Set up socket listeners
  useEffect(() => {
    if (connected) {
      // Listen for log updates
      const logHandler = (data: any) => {
        if (typeof data === "string") {
          setLogs((prev) => [...prev, data])
        } else if (data.message) {
          setLogs((prev) => [...prev, data.message])
        }
      }

      // Listen for status updates
      const statusHandler = (data: any) => {
        const newStatus = data.status || data
        setStatus(newStatus as SimulationStatus)

        // Allow closing dialog when simulation is completed or error
        if (newStatus === "completed" || newStatus === "error") {
          setAllowClose(true)
        }
      }

      on_simulation_run_log(logHandler)
      on_sim_run_status(statusHandler)

      return () => {
        // Clean up listeners if needed
        // This depends on how your socket store is implemented
      }
    }
  }, [connected, on_simulation_run_log, on_sim_run_status])

  // Handle dialog open state changes
  const handleOpenChange = (newOpen: boolean) => {
    // Only allow closing if not in running state
    if (!newOpen && status === "running") {
      return // Prevent closing
    }
    setOpen(newOpen)
  }

  // Start the simulation
  const startSimulation = async () => {
    await SaveSimulationData()
    setStatus("running")
    setLogs([])
    setAllowClose(false)

    try {
      // Call the socket function to run the simulation
      if (projectName === null) {
        return
      }
      await run_simulation(
        projectName,
        simulationName,
        countType,
        simulationRuntime
      )
    } catch (error) {
      setLogs((prev) => [...prev, `Error starting simulation: ${error}`])
      setStatus("error")
      setAllowClose(true)
    }
  }

  return (
    <>
      <Button size="sm" onClick={() => setOpen(true)}>
        Run
      </Button>

      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-[800px] sm:h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>{status === "idle" ? "Run Simulation" : "Simulation Progress"}</DialogTitle>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto p-2">
            {status === "idle" ? (
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Simulation Name</Label>
                  <Input
                    id="name"
                    value={simulationName}
                    onChange={(e) => setSimulationName(e.target.value)}
                    placeholder="My Simulation"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="type">Count Time Unit</Label>
                  <Select value={countType} onValueChange={setCountType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Time Unit" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="seconds">Seconds (s)</SelectItem>
                      <SelectItem value="minutes">Minutes (min)</SelectItem>
                      <SelectItem value="hours">Hours (hr)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="runtime">Run time (Optional: 0 means None)</Label>
                  <Input
                    id="runtime"
                    value={simulationRuntime}
                    type="number"
                    onChange={(e) => setSimulationRuntime(Number(e.target.value))}
                    placeholder="0"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="params">Simulation Parameters</Label>
                  <Textarea
                    id="params"
                    value={simulationParams}
                    onChange={(e) => setSimulationParams(e.target.value)}
                    placeholder="Enter simulation parameters as JSON or configuration text"
                    rows={8}
                  />
                </div>
              </div>
            ) : (
              <div className="py-4 space-y-4">
                <div className="flex items-center space-x-2">
                  {status === "running" && (
                    <div className="flex items-center text-blue-500">
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      <span>Simulation in progress...</span>
                    </div>
                  )}
                  {status === "completed" && (
                    <div className="flex items-center text-green-500">
                      <CheckCircle className="h-5 w-5 mr-2" />
                      <span>Simulation completed successfully!</span>
                    </div>
                  )}
                  {status === "error" && (
                    <div className="flex items-center text-red-500">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      <span>Simulation failed. See logs for details.</span>
                    </div>
                  )}
                </div>

                {/* Single log output area */}
                <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-md h-[400px] overflow-y-auto">
                  {logs.map((log, i) => (
                    <div key={i} className="py-0.5">
                      {log}
                    </div>
                  ))}
                  {status === "running" && <div className="animate-pulse">_</div>}
                </div>
              </div>
            )}
          </div>

          <DialogFooter>
            {status === "idle" && (
              <Button onClick={startSimulation} disabled={!simulationName}>
                Run Simulation
              </Button>
            )}

            {(status === "completed" || status === "error") && (
              <DialogClose asChild>
                <Button>Close</Button>
              </DialogClose>
            )}

            {status === "running" && (
              <Button variant="outline" disabled>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running...
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
