import { createFileRoute, useBlocker } from '@tanstack/react-router'
import { AppSidebar } from '@/components/default/project/side-bar-left'
import { SidebarProvider } from '@/components/ui/sidebar'
// import { Outlet } from '@tanstack/react-router'
import { useCallback, useEffect, useState } from 'react'
import FlowPage from '@/page/project/flow'
import AnalyticsPage from '@/page/project/analytics'
import SettingsPage from '@/page/project/settings'
import { ProjectLoadingScreen } from '@/page/project/projectLoader'
import { SimDataState } from '@/states/simDataState'
import { FlowState } from '@/states/flowState'
import { ErrorState } from '@/states/errorState'

export const Route = createFileRoute('/project/$projectid/')({
  component: RouteComponent,
  loader: async ({ params }) => {
    const { setProjectName } = SimDataState.getState();
    try {
      setProjectName(params.projectid);
      await SimDataState.getState().loadRegisterData();
      await FlowState.getState().loadNodesEdges(params.projectid);
      await SimDataState.getState().loadCompData(params.projectid);
    } catch (error) {
      console.error('Error loading simulation data:', error);
      const { setError } = ErrorState.getState();
      setError({
        header: 'Error loading simulation',
        body: 'Failed to load simulation data. Please try again.',
      })
    }

    // await sync_comp_nodes()
    return {
      simulationId: params.projectid,
    }
  },
  pendingComponent: () => <ProjectLoadingScreen message={`loading simulation ...`} />,
})

function RouteComponent() {
  const { componentRegisterI } = SimDataState();
  console.log(componentRegisterI)
  const { simulationId } = Route.useLoaderData()
  const [currentPage, setCurrnetPage] = useState<string>("FlowPage")
  useBlocker({
    shouldBlockFn: () =>
      window.confirm(
        'u need to save the file in order to exit otherwise your project will be unsave!',
      ),
  })

  useEffect(() => { }, [simulationId])

  const getComponentByName = useCallback((name: string) => {
    switch (name) {
      case "FlowPage":
        return <FlowPage />
      case "AnalyticsPage":
        return <AnalyticsPage />
      case "SettingsPage":
        return <SettingsPage />
      default:
        return <FlowPage />
    }
  }, [])

  return (
    <SidebarProvider>
      <AppSidebar
        simulationId={simulationId}
        activeComponent={currentPage}
        setActiveComponent={setCurrnetPage}
      />
      <main className="flex flex-col w-full">
        {getComponentByName(currentPage)}
      </main>
    </SidebarProvider>
  )
}

// export const Route = createRootRoute({
//   component: () => (
//     <>
//       <SidebarProvider>
//         <AppSidebar />
//         <main>
//           <SidebarTrigger />
//           <Outlet />
//         </main>
//       </SidebarProvider>
//     </>
//   ),
// })
