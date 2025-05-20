import { useEffect, useState } from "react";
import Dashboard from "./chartbuilder/dashboard";
import { useSocketStore } from "@/utils/socketIo";
import { TableCard, TableCardProps } from "../tableBuilder/table-card";

interface AnalyticsProps {
  project_name: string
  runId: string
}

function SimulationOverviewAnalyticsBuild({ project_name, runId }: AnalyticsProps) {
  const [dashboardData, setDashboardData] = useState(null);
  const [dashboardTable, setDashboardTable] = useState<TableCardProps[]>([]);
  const { check_socket_endpoint } = useSocketStore()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await check_socket_endpoint("get_sim_data", { "project_name": project_name, "run_id": runId });
        // Ensure we're consistently handling the data
        // If data.dashboardData exists, use it, otherwise use data directly
        console.log("Fetched data:", data);
        setDashboardData(data.charts);
        setDashboardTable(data.tables)
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    }
    fetchData();
  }, [project_name, runId, check_socket_endpoint]);

  // no data page
  if (!dashboardData) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <h1 className="text-2xl font-bold">No Data Available</h1>
        <p className="text-gray-500">Please check back later.</p>
      </div>
    );
  }
  return (
    <div>
      <Dashboard config={dashboardData as any[]} />
      <div className="flex flex-col gap-4 mt-4">
        {dashboardTable.length > 0 &&
          dashboardTable.map((tableConfig) => (
            <TableCard
              key={tableConfig.id}
              id={tableConfig.id}
              title={tableConfig.title}
              description={tableConfig.description}
              data={tableConfig.data}
              columnOrder={tableConfig.columnOrder}
              columnLabels={tableConfig.columnLabels}
              className="h-full"
            />
          ))
        }
      </div>
    </div>
  );
}

export default SimulationOverviewAnalyticsBuild;
