import { createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import { ErrorDialog } from '@/components/default/error/errorDialog'
import { useEffect } from 'react';
import { useSocketStore } from '@/utils/socketIo'
import { ThemeProvider } from '@/components/theme-provider'

export const Route = createRootRoute({
  component: () => {

    const { connectSocket, disconnectSocket } = useSocketStore();

    useEffect(() => {
      console.log('Connecting to socket...');
      connectSocket();
      return () => {
        disconnectSocket();
      }
    }, [connectSocket, disconnectSocket]);

    return (
      <ThemeProvider defaultTheme="system" storageKey="simz-ui-theme">
        <Outlet />
        {/* <TanStackRouterDevtools position='bottom-right' /> */}
        <ErrorDialog />
      </ThemeProvider>
    )
  },
})
