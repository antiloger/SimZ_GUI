import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import Dashboard from "./chartbuilder/dashboard"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CalendarRange, BarChartIcon as ChartSpline } from "lucide-react"
import { useEffect, useState } from "react"
import { useSocketStore } from "@/utils/socketIo"
import ComponentDetailBar from "./componentDetailBar"
import { AnalyticNavCombo, type RunList } from "./nav-bar/runCombo"
import { DataTableComponent } from "../EventList/data-table-component"

interface AnalyticsBuildProps {
  projectName: string
  runId: string
}


// id
// : 
// "41b79005-4612-4ce5-8d6a-a79ec43328e4"
// name
// : 
// "Resource 41b79005-4612-4ce5-8d6a-a79ec43328e4"
// type
// : 
// "resource"
interface CompData {
  id: string
  name: string
  type: string
}

function AnalyticsBuild({ projectName, runId }: AnalyticsBuildProps) {
  const [componentComboOpen, setComponentComboOpen] = useState(false)
  const [compList, setCompList] = useState<RunList[]>([])
  const [selectedCompId, setSelectedCompId] = useState<string>("")
  const [isLoading, setIsLoading] = useState(true)
  const [selectedCompData, setSelectedCompData] = useState<CompData>()

  const [dashboardData, setDashboardData] = useState(null)
  const { check_socket_endpoint } = useSocketStore()

  // Function to handle component selection change
  const handleComponentChange = (componentId: string) => {
    setSelectedCompId(componentId)
    // You might want to fetch new data based on the selected component
    fetchComponentData(componentId)
  }

  // Function to fetch component data
  const fetchComponentData = async (componentId: string) => {
    try {
      const data = await check_socket_endpoint("get_component_analytics", {
        project_name: projectName,
        run_id: runId,
        component_id: componentId,
      })
      console.log("Component Data:", data.dashboradData)
      setDashboardData(data.dashboradData)
      setSelectedCompData({
        id: data.id,
        name: data.name,
        type: data.type,
      })
    } catch (error) {
      console.error("Error fetching component data:", error)
    }
  }

  useEffect(() => {
    const fetchComponentList = async () => {
      setIsLoading(true)
      try {
        // Assuming you have an endpoint to get the component list
        const response = await check_socket_endpoint("get_component_names", {
          project_name: projectName,
          run_id: runId,
        })

        // Transform the data from object format to array format
        // Example: { "id1": "name1", "id2": "name2" } => [{ id: "id1", name: "name1" }, { id: "id2", name: "name2" }]
        const transformedData = Object.entries(response).map(([id, name]) => ({
          id,
          name: name as string,
        }))
        console.log("Transformed Data:", transformedData)
        setCompList(transformedData)

        // Set the first component as selected by default if available
        if (transformedData.length > 0 && !selectedCompId) {
          setSelectedCompId(transformedData[0].id)
          fetchComponentData(transformedData[0].id)
        }
      } catch (error) {
        console.error("Error fetching component list:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchComponentList()
  }, [projectName, runId, check_socket_endpoint])

  useEffect(() => {
    // Initial data fetch for the dashboard
    const fetchData = async () => {
      try {
        const data = await check_socket_endpoint("get_component_analytics", {
          project_name: projectName,
          run_id: runId,
          component_id: selectedCompId || 12, // Fallback to 12 if no component is selected
        })
        // Ensure we're consistently using data.dashboardData
        setDashboardData(data.dashboradData)
        setSelectedCompData({
          id: data.id,
          name: data.name,
          type: data.type,
        })
      } catch (error) {
        console.error("Error fetching dashboard data:", error)
      }
    }

    if (runId) {
      fetchData()
    }
  }, [projectName, runId, selectedCompId, check_socket_endpoint])

  // no data page
  if (!dashboardData || !selectedCompData) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <h1 className="text-2xl font-bold">No Data Available</h1>
        <p className="text-gray-500">Please check back later.</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <h1 className="text-2xl font-bold">Loading...</h1>
      </div>
    )
  }

  return (
    <div className="analytics-build  gap-y-2">
      <div className="flex w-full" >
        <AnalyticNavCombo
          runList={compList}
          selectedRunId={selectedCompId}
          setSelectedRunId={handleComponentChange}
          open={componentComboOpen}
          setOpen={setComponentComboOpen}
          placeholder="Select a component"
          searchPlaceholder="Search components..."
          emptyMessage="No components found."
          width="w-full"
        />
      </div>

      <ComponentDetailBar componentName={selectedCompId} componentType={selectedCompData.type} />
      <Tabs defaultValue="tab-1">
        <ScrollArea>
          <TabsList className="mb-3">
            <TabsTrigger value="tab-1">
              <ChartSpline className="-ms-0.5 me-1.5 opacity-60" size={16} aria-hidden="true" />
              Analytics Visualization
            </TabsTrigger>
            <TabsTrigger value="tab-2" className="group">
              <CalendarRange className="-ms-0.5 me-1.5 opacity-60" size={16} aria-hidden="true" />
              Event List
            </TabsTrigger>
          </TabsList>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
        <TabsContent value="tab-1">
          <Dashboard config={dashboardData} />
        </TabsContent>
        <TabsContent value="tab-2">
          <DataTableComponent runId={runId} componentId={selectedCompId} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AnalyticsBuild
