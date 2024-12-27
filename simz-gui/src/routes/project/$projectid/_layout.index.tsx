import Flow from '@/components/default/ReactFlow/flow'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/project/$projectid/_layout/')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className='flex flex-col' >
      {/* <div> <MainMenubar /> </div> */}
      <div>
        <Flow />
      </div>
    </div>
  )
}
