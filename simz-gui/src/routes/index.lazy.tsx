import OverviewPage from '@/page/overview'
import { useSocketStore } from '@/utils/socketIo'
import { createLazyFileRoute } from '@tanstack/react-router'
import { useEffect } from 'react';

export const Route = createLazyFileRoute('/')({
  component: RouteComponent,
})

function RouteComponent() {
  const { connectSocket, disconnectSocket } = useSocketStore();

  useEffect(() => {
    console.log('Connecting to socket...');
    connectSocket();
    return () => {
      disconnectSocket();
    }
  }, [connectSocket, disconnectSocket]);

  return (
    <>
      <div>
        <OverviewPage />
      </div>
    </>
  )

}
