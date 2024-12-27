import { createLazyFileRoute } from '@tanstack/react-router'

export const Route = createLazyFileRoute('/tpp')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/tpp"!</div>
}
