import { CalendarRange, Codesandbox, PuzzleIcon } from "lucide-react"

import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import AnalyticsBuild from "./analyticsBuild"
import { EventListTable } from "../EventList/data-table"
import SimulationOverviewAnalyticsBuild from "./simOverviewAnalytics"


export default function SimulationTab() {
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
        </TabsList>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
      <TabsContent value="tab-1">
        <SimulationOverviewAnalyticsBuild />
      </TabsContent>
      <TabsContent value="tab-2">
        <AnalyticsBuild />
      </TabsContent>
      <TabsContent value="tab-3">
        <EventListTable />
      </TabsContent>
    </Tabs>
  )
}
