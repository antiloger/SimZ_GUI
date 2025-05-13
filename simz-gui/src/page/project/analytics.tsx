import AnalyticsBuild from "@/components/default/analytics/analyticsBuild"
import { AnalyticNavCombo } from "@/components/default/analytics/nav-bar/runCombo"
import SimulationTab from "@/components/default/analytics/simulationTab"
import { Separator } from "@/components/ui/separator"
import { SimDataState } from "@/states/simDataState"
import { RunList } from "@/types/socketT"
import { useSocketStore } from "@/utils/socketIo"
import { useEffect, useState } from "react"

export default function AnalyticsPage() {
  const [runComboOpen, setRunComboOpen] = useState(false)
  const [runList, setRunList] = useState<RunList[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string>("")
  const { projectName } = SimDataState()
  const { get_run_list } = useSocketStore()

  useEffect(() => {
    const fetchRunList = async () => {
      if (!projectName) {
        return
      }
      try {
        const data = await get_run_list(projectName)
        setRunList(data)
        const lastRunId = data.length > 0 ? data.length - 1 : undefined
        if (lastRunId !== undefined) {
          setSelectedRunId(data[lastRunId].id)
        }
      } catch (error) {
        selectedRunId !== "" && setSelectedRunId("")
        console.error("Error fetching run list:", error)
      }
    }
    fetchRunList()
    console.log("Fetching run list for project:", runList)
  }, [projectName, selectedRunId])
  console.log("Selected Run ID:", selectedRunId)
  // if (selectedRunId === "") {
  //   return (
  //     <div className="flex flex-col w-full h-screen items-center justify-center">
  //       <h1 className="text-2xl font-bold">No Run Found</h1>
  //       <h2 className="text-sm text-gray-600">Please create a run to view analytics</h2>
  //     </div>
  //   )
  // }
  
  return (
    <>
      <div className="flex flex-col w-full  h-screen">
        <div className="flex flex-row items-center justify-between p-2 border-b">
          <div className="flex flex-row items-center gap-x-2">
            <h1 className="text-2xl font-bold">{projectName}</h1>
            <Separator orientation="vertical" />
            <div className="flex flex-col ">
              <h2 className="text-sm text-gray-600">Last Run: {runList.at(-1)?.name ?? ""}</h2>
              <h2 className="text-sm text-gray-600">Run Id: {selectedRunId}</h2>
            </div>
          </div>
          <div className="flex flex-row gap-x-2 items-center">
            <div className="flex flex-col">
              <h2 className="text-sm text-gray-600">current run:</h2>
              <AnalyticNavCombo
                runList={runList}
                selectedRunId={selectedRunId}
                setSelectedRunId={setSelectedRunId}
                open={runComboOpen}
                setOpen={setRunComboOpen}
                placeholder="Select a run"
              />
            </div>
            {/* <div className="flex flex-col"> */}
            {/*   <h2 className="text-sm text-gray-600">component:</h2> */}
            {/*   <AnalyticNavCombo /> */}
            {/* </div> */}
          </div>
        </div>
        { (selectedRunId !== "" && projectName) ? (
        <div className="flex flex-col w-full p-2">
          <SimulationTab project_name={projectName} runId={selectedRunId} />
        </div>) : (
          <div className="flex flex-col w-full h-screen items-center justify-center">
            <h1 className="text-2xl font-bold">No Run Found</h1>
            <h2 className="text-sm text-gray-600">Please create a run to view analytics</h2>
          </div>)
        }
      </div>
    </>
  )
}
