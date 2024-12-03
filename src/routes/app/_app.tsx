import AppNavBar from '@/components/default/app-navbar'
import { createFileRoute, Outlet } from '@tanstack/react-router'

export const Route = createFileRoute('/app/_app')({
  component: AppPage,
})

export default function AppPage() {
  return (
    <div className="flex flex-col w-full">
      <AppNavBar />
      <Outlet />
    </div>
  )
}
