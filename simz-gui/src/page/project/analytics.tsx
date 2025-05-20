import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import { AnalyticNavCombo } from "@/components/default/analytics/nav-bar/runCombo"
import SimulationTab from "@/components/default/analytics/simulationTab"
import { SimDataState } from "@/states/simDataState"
import { useSocketStore } from "@/utils/socketIo"
import { RunList } from "@/types/socketT"

export default function AnalyticsPage() {
  const [runComboOpen, setRunComboOpen] = useState(false)
  const [runList, setRunList] = useState<RunList[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string>("")
  const [isLoading, setIsLoading] = useState(true)
  const { projectName } = SimDataState()
  const { get_run_list } = useSocketStore()

  const fetchRunList = async () => {
    if (!projectName) {
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    try {
      const data = await get_run_list(projectName)
      setRunList(data)

      // Only set the selectedRunId if it hasn't been selected yet or is invalid
      if (selectedRunId === "" || !data.some(run => run.id === selectedRunId)) {
        const lastRunIndex = data.length > 0 ? data.length - 1 : -1
        if (lastRunIndex >= 0) {
          setSelectedRunId(data[lastRunIndex].id)
        }
      }
    } catch (error) {
      console.error("Error fetching run list:", error)
      setSelectedRunId("")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRunList()
  }, [projectName])

  // Manage the run selection
  const handleRunChange = (runId: string) => {
    setSelectedRunId(runId)
  }

  return (
    <div className="flex flex-col w-full h-screen">
      <div className="flex flex-row items-center justify-between p-2 border-b">
        <div className="flex flex-row items-center gap-x-2">
          <h1 className="text-2xl font-bold">{projectName || "No Project Selected"}</h1>
          <Separator orientation="vertical" />
          <div className="flex flex-col">
            <h2 className="text-sm text-gray-600">
              Last Run: {runList.length > 0 ? runList[runList.length - 1]?.name || "N/A" : "N/A"}
            </h2>
            <h2 className="text-sm text-gray-600">Run Id: {selectedRunId || "None"}</h2>
          </div>
        </div>

        <div className="flex flex-row gap-x-2 items-center">
          <div className="flex flex-col">
            <h2 className="text-sm text-gray-600">current run:</h2>
            <AnalyticNavCombo
              runList={runList}
              selectedRunId={selectedRunId}
              setSelectedRunId={handleRunChange}
              open={runComboOpen}
              setOpen={setRunComboOpen}
              placeholder="Select a run"
            />
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col w-full h-full items-center justify-center">
          <h2 className="text-xl">Loading...</h2>
        </div>
      ) : (selectedRunId && projectName) ? (
        <div className="flex flex-col w-full p-2">
          <SimulationTab project_name={projectName} runId={selectedRunId} />
        </div>
      ) : (
        <div className="flex flex-col w-full h-full items-center justify-center">
          <h1 className="text-2xl font-bold">No Run Found</h1>
          <h2 className="text-sm text-gray-600">Please create a run to view analytics</h2>
        </div>
      )}
    </div>
  )
}
