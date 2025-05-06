import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from "@/components/ui/dialog"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, CheckCircle, AlertCircle, Play, XCircle } from "lucide-react"

// Mock data to simulate socket.io events
const mockSimulationStages = [
  {
    id: "building",
    name: "Building Simulation",
    logs: [
      "Initializing build environment...",
      "Installing dependencies...",
      "Compiling simulation code...",
      "Preparing simulation assets...",
      "Build completed successfully.",
    ],
    duration: 5000, // 5 seconds
  },
  {
    id: "running",
    name: "Running Simulation",
    logs: [
      "Starting simulation engine...",
      "Loading initial state...",
      "Processing physics calculations...",
      "Rendering frame 1/100...",
      "Rendering frame 50/100...",
      "Rendering frame 100/100...",
      "Simulation completed successfully.",
    ],
    duration: 8000, // 8 seconds
  },
  {
    id: "analyzing",
    name: "Analyzing Results",
    logs: [
      "Collecting simulation data...",
      "Calculating performance metrics...",
      "Generating visualization...",
      "Analysis completed successfully.",
    ],
    duration: 3000, // 3 seconds
  },
]

type SimulationStatus = "idle" | "running" | "completed" | "error"
type StageStatus = "pending" | "running" | "completed" | "error"

interface SimulationStage {
  id: string
  name: string
  status: StageStatus
  logs: string[]
  expandedLogs: string[]
}

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
  const [simulationType, setSimulationType] = useState("seconds")
  const [simulationRuntime, setSimulationRuntime] = useState(0)
  const [status, setStatus] = useState<SimulationStatus>("idle")
  const [stages, setStages] = useState<SimulationStage[]>([])
  const [expandedStages, setExpandedStages] = useState<string[]>([])
  const [_currentStageIndex, setCurrentStageIndex] = useState(-1)

  // Reset the form and state when dialog closes
  useEffect(() => {
    if (!open) {
      setStatus("idle")
      setStages([])
      setExpandedStages([])
      setCurrentStageIndex(-1)
    }
  }, [open])

  // Mock function to start the simulation
  const startSimulation = () => {
    setStatus("running")

    // Initialize stages
    const initialStages = mockSimulationStages.map((stage) => ({
      id: stage.id,
      name: stage.name,
      status: "pending" as StageStatus,
      logs: [],
      expandedLogs: [],
    }))

    setStages(initialStages)
    setCurrentStageIndex(0)
    setExpandedStages([initialStages[0].id])

    // Start the first stage
    runStage(0, initialStages)

    // SOCKET.IO IMPLEMENTATION COMMENT:
    // Replace the mock implementation above with real socket.io code:
    // 1. Emit a 'start-simulation' event with the form data
    // socket.emit('start-simulation', {
    //   name: simulationName,
    //   params: simulationParams,
    //   type: simulationType
    // })
    //
    // 2. Listen for stage updates
    // socket.on('stage-update', (data) => {
    //   // Update the stages state with the received data
    //   setStages(prevStages => {
    //     const updatedStages = [...prevStages]
    //     const stageIndex = updatedStages.findIndex(s => s.id === data.stageId)
    //     if (stageIndex >= 0) {
    //       updatedStages[stageIndex] = {
    //         ...updatedStages[stageIndex],
    //         status: data.status,
    //         logs: [...updatedStages[stageIndex].logs, ...data.newLogs]
    //       }
    //     }
    //     return updatedStages
    //   })
    // })
    //
    // 3. Listen for simulation completion
    // socket.on('simulation-completed', () => {
    //   setStatus('completed')
    // })
    //
    // 4. Listen for errors
    // socket.on('simulation-error', (error) => {
    //   setStatus('error')
    //   // Handle error
    // })
  }

  // Mock function to simulate running a stage
  const runStage = (stageIndex: number, currentStages: SimulationStage[]) => {
    if (stageIndex >= mockSimulationStages.length) {
      setStatus("completed")
      return
    }

    const mockStage = mockSimulationStages[stageIndex]
    const updatedStages = [...currentStages]
    updatedStages[stageIndex] = {
      ...updatedStages[stageIndex],
      status: "running",
    }
    setStages(updatedStages)

    // Simulate log updates
    let logIndex = 0
    const logInterval = mockStage.duration / mockStage.logs.length

    const logTimer = setInterval(() => {
      if (logIndex < mockStage.logs.length) {
        setStages((prevStages) => {
          const newStages = [...prevStages]
          newStages[stageIndex] = {
            ...newStages[stageIndex],
            logs: [...newStages[stageIndex].logs, mockStage.logs[logIndex]],
            expandedLogs: [...newStages[stageIndex].expandedLogs, mockStage.logs[logIndex]],
          }
          return newStages
        })
        logIndex++
      } else {
        clearInterval(logTimer)

        // Mark stage as completed
        setStages((prevStages) => {
          const newStages = [...prevStages]
          newStages[stageIndex] = {
            ...newStages[stageIndex],
            status: "completed",
          }
          return newStages
        })

        // Move to next stage
        if (stageIndex + 1 < mockSimulationStages.length) {
          setCurrentStageIndex(stageIndex + 1)
          setExpandedStages((prev) => [...prev, mockSimulationStages[stageIndex + 1].id])
          setTimeout(() => {
            runStage(stageIndex + 1, updatedStages)
          }, 500)
        } else {
          setStatus("completed")
        }
      }
    }, logInterval)
  }

  const getStageIcon = (stage: SimulationStage) => {
    switch (stage.status) {
      case "pending":
        return <Play className="h-5 w-5 text-muted-foreground" />
      case "running":
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return null
    }
  }



  return (
    <>
      <Button size="sm" onClick={() => setOpen(true)}>Run</Button>

      <Dialog open={open} onOpenChange={setOpen} >
        <DialogContent className="sm:max-w-[800px] sm:h-[80vh] flex flex-col"  >
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
                  <Select value={simulationType} onValueChange={setSimulationType}>
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
                  <Label htmlFor="name">Run time (Optional: 0 means None)</Label>
                  <Input
                    id="name"
                    value={simulationRuntime}
                    type="number"
                    onChange={(e) => setSimulationRuntime(Number(e.target.value))}
                    placeholder="My Simulation"
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

                <Accordion
                  type="multiple"
                  value={expandedStages}
                  onValueChange={setExpandedStages}
                  className="border rounded-md"
                >
                  {stages.map((stage, _index) => (
                    <AccordionItem key={stage.id} value={stage.id}>
                      <AccordionTrigger className="px-4 hover:no-underline hover:bg-muted/50">
                        <div className="flex items-center space-x-2 w-full">
                          {getStageIcon(stage)}
                          <span>{stage.name}</span>
                          {stage.status === "running" && (
                            <span className="ml-auto text-sm text-muted-foreground animate-pulse">In progress...</span>
                          )}
                          {stage.status === "completed" && (
                            <span className="ml-auto text-sm text-muted-foreground">Completed</span>
                          )}
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="px-4 pt-2 pb-4">
                        <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-md h-[200px] overflow-y-auto">
                          {stage.expandedLogs.map((log, i) => (
                            <div key={i} className="py-0.5">
                              {log}
                            </div>
                          ))}
                          {stage.status === "running" && <div className="animate-pulse">_</div>}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </div>
            )}
          </div>

          <DialogFooter>
            {status === "idle" && (
              <Button onClick={startSimulation} disabled={!simulationName}>
                Run Simulation
              </Button>
            )}

            {status === "completed" && (
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
