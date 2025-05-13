import { CalendarRange, Codesandbox, Container, PuzzleIcon } from "lucide-react"

import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import AnalyticsBuild from "./analyticsBuild"
import { DataTable } from "../EventList/data-table"
import SimulationOverviewAnalyticsBuild from "./simOverviewAnalytics"
import ContainerDataViewer from "./containerSearcch"

interface DataTableProps {
  project_name: string
  runId: string
}

export default function SimulationTab({ project_name, runId }: DataTableProps) {
  return (
    <Tabs defaultValue="tab-1">
      <ScrollArea>
        <TabsList className="mb-3">
          <TabsTrigger value="tab-1">
            <Codesandbox
              className="-ms-0.5 me-1.5 opacity-60"
              size={16}
              aria-hidden="true"
            />
            Simulation Overview
          </TabsTrigger>
          <TabsTrigger value="tab-2" className="group">
            <PuzzleIcon
              className="-ms-0.5 me-1.5 opacity-60"
              size={16}
              aria-hidden="true"
            />
            Component Overview
          </TabsTrigger>
          <TabsTrigger value="tab-3" className="group">
            <CalendarRange
              className="-ms-0.5 me-1.5 opacity-60"
              size={16}
              aria-hidden="true"
            />
            Event List
          </TabsTrigger>
          <TabsTrigger value="tab-4" className="group">
            <Container
              className="-ms-0.5 me-1.5 opacity-60"
              size={16}
              aria-hidden="true"
            />
            Container Search
          </TabsTrigger>
        </TabsList>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
      <TabsContent value="tab-1">
        <SimulationOverviewAnalyticsBuild project_name={project_name} runId={runId} />
      </TabsContent>
      <TabsContent value="tab-2">
        <AnalyticsBuild />
      </TabsContent>
      <TabsContent value="tab-3">
        <DataTable runId={runId} />
      </TabsContent>
      <TabsContent value="tab-4">
        <ContainerDataViewer projcetName={project_name} runId={runId} />
      </TabsContent>
    </Tabs>
  )
}
