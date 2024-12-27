import { createFileRoute } from '@tanstack/react-router'
import { AppSidebar } from '@/components/default/project/side-bar-left'
import { SidebarProvider } from '@/components/ui/sidebar'
import { Outlet } from '@tanstack/react-router'


export const Route = createFileRoute('/project/$projectid/_layout')({
  component: RouteComponent,
  loader: async ({ params }) => {
    return {
      simulationId: params.projectid,
    }
  }

})

function RouteComponent() {
  const { simulationId } = Route.useLoaderData();
  return (
    <SidebarProvider >
      <AppSidebar simulationId={simulationId} />
      <main className='flex flex-col w-full' >
        <Outlet />
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
