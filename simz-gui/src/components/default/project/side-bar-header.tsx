import { ChevronsUpDown, Codesandbox, LogOut } from "lucide-react"

import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar"
import { SimDataState } from "@/states/simDataState"
import { useNavigate } from "@tanstack/react-router"

export function CustomSideBarHeader() {
  const { projectName } = SimDataState()
  const navigate = useNavigate()
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                <Codesandbox className="size-4" />
              </div>
              <div className="flex flex-col gap-0.5 leading-none">
                <span className="font-semibold">SimZ</span>
                <span className="">Project: {projectName}</span>
              </div>
              <ChevronsUpDown className="ml-auto" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-[--radix-dropdown-menu-trigger-width]" align="start">
            <DropdownMenuItem onClick={() => {
              navigate({ to: '/' })
            }} >
              <div className="flex size-6 items-center justify-center rounded-sm border">
                <LogOut className="size-4 shrink-0" />
              </div>
              Project
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
