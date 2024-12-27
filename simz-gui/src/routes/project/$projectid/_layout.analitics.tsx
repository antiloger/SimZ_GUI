import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/project/$projectid/_layout/analitics')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/project/$projectid/analitics"!</div>
}
