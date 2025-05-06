import AnalyticsBuild from "@/components/default/analytics/analyticsBuild"
import { AnalyticNavCombo } from "@/components/default/analytics/nav-bar/runCombo"
import SimulationTab from "@/components/default/analytics/simulationTab"
import { Separator } from "@/components/ui/separator"
import { SimDataState } from "@/states/simDataState"
import { useState } from "react"

export default function AnalyticsPage() {
  const [simId, setSimId] = useState<string | null>(null)
  const [compId, setCompId] = useState<string | null>(null)
  const { projectName } = SimDataState()


  return (
    <>
      <div className="flex flex-col w-full  h-screen">
        <div className="flex flex-row items-center justify-between p-2 border-b">
          <div className="flex flex-row items-center gap-x-2">
            <h1 className="text-2xl font-bold">{projectName}</h1>
            <Separator orientation="vertical" />
            <div className="flex flex-col ">
              <h2 className="text-sm text-gray-600">Last Run: 2025-02-24</h2>
              <h2 className="text-sm text-gray-600">Run Id: eq21343swsdfa23</h2>
            </div>
          </div>
          <div className="flex flex-row gap-x-2 items-center">
            <div className="flex flex-col">
              <h2 className="text-sm text-gray-600">current run:</h2>
              <AnalyticNavCombo />
            </div>
            {/* <div className="flex flex-col"> */}
            {/*   <h2 className="text-sm text-gray-600">component:</h2> */}
            {/*   <AnalyticNavCombo /> */}
            {/* </div> */}
          </div>
        </div>
        <div className="flex flex-col w-full p-2">
          <SimulationTab />
        </div>
      </div>
    </>
  )
}
