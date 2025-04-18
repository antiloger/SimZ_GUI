import OverviewPage from '@/page/overview'
import { createLazyFileRoute } from '@tanstack/react-router'

export const Route = createLazyFileRoute('/')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <>
      <div>
        <OverviewPage />
      </div>
    </>
  )

}
