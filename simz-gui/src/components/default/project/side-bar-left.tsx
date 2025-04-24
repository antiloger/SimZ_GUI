import { AreaChartIcon as ChartArea, Codesandbox, ComponentIcon, Settings } from 'lucide-react'
import React from "react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { CustomSideBarHeader } from './side-bar-header'

// Menu items with component names
const items = [
  {
    title: "Workflow",
    componentName: "FlowPage",
    icon: ComponentIcon,
  },
  {
    title: "Analysis",
    componentName: "AnalyticsPage",
    icon: ChartArea,
  },
  {
    title: "Settings",
    componentName: "SettingsPage",
    icon: Settings,
  },
]

interface AppSidebarProp {
  simulationId: string
  activeComponent: string
  setActiveComponent: (componentName: string) => void
}

export function AppSidebar({ simulationId, activeComponent, setActiveComponent }: AppSidebarProp) {
  console.log(simulationId)
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            {/* Add header content if needed */}
            <CustomSideBarHeader />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    onClick={() => setActiveComponent(item.componentName)}
                    isActive={activeComponent === item.componentName}
                  >
                    <item.icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarTrigger />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}


// import { ChartArea, Component, Settings } from "lucide-react"
//
// import {
//   Sidebar,
//   SidebarContent,
//   SidebarFooter,
//   SidebarGroup,
//   SidebarGroupContent,
//   SidebarGroupLabel,
//   SidebarHeader,
//   SidebarMenu,
//   SidebarMenuButton,
//   SidebarMenuItem,
//   SidebarTrigger,
// } from "@/components/ui/sidebar"
// import { Link } from "@tanstack/react-router"
//
// // Menu items.
// const items = [
//   {
//     title: "Workflow",
//     url: "",
//     icon: Component,
//   },
//   {
//     title: "Analysis",
//     url: "analitics",
//     icon: ChartArea,
//   },
//   {
//     title: "Settings",
//     url: "#",
//     icon: Settings,
//   },
// ]
//
// interface AppSidebarProp {
//   simulationId: string
// }
//
// export function AppSidebar({ simulationId }: AppSidebarProp) {
//   return (
//     <Sidebar collapsible="icon">
//       <SidebarHeader>
//         <SidebarMenu>
//           <SidebarMenuItem>
//           </SidebarMenuItem>
//         </SidebarMenu>
//       </SidebarHeader>
//       <SidebarContent>
//         <SidebarGroup>
//           <SidebarGroupLabel>Application</SidebarGroupLabel>
//           <SidebarGroupContent>
//             <SidebarMenu>
//               {items.map((item) => (
//                 <SidebarMenuItem key={item.title}>
//                   <SidebarMenuButton asChild>
//                     <Link to={`/project/$projectid/${item.url}`} params={{ projectid: simulationId }}>
//                       <item.icon />
//                       <span>{item.title}</span>
//                     </Link>
//                   </SidebarMenuButton>
//                 </SidebarMenuItem>
//               ))}
//             </SidebarMenu>
//           </SidebarGroupContent>
//         </SidebarGroup>
//       </SidebarContent>
//       <SidebarFooter>
//         <SidebarMenu>
//           <SidebarMenuItem>
//             <SidebarTrigger />
//           </SidebarMenuItem>
//         </SidebarMenu>
//       </SidebarFooter>
//     </Sidebar>
//   )
// }


{/* <Link to={`/project/$projectid/${item.url}`} params={{ projectid: simulationId }}> */ }
{/*   <item.icon /> */ }
{/*   <span>{item.title}</span> */ }
{/* </Link> */ }
