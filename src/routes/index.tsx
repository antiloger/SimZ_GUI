import { Button } from '@/components/ui/button'
import { useCounterStore } from '@/state/store'
import { createFileRoute, Link, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  // beforeLoad: async ({ location }) => {
  //   throw redirect({
  //     to: '/login',
  //     search: {
  //       redirect: location.href
  //     },
  //   })
  // },
  component: IndexApp,
})

function IndexApp() {
  const count = useCounterStore((state) => state.count);
  const countInc = useCounterStore((state) => state.increment);
  return (
    <div>
      Home
      <div>{count}</div>
      <Button onClick={countInc} > Inc </Button>
      <Link to='/login' >Login</Link>

    </div>
  )
}
