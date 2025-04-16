import { createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import { ErrorDialog } from '@/components/default/error/errorDialog'

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <TanStackRouterDevtools position='bottom-right' />
      <ErrorDialog />
    </>
  ),
})
