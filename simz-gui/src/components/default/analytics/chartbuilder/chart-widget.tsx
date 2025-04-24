"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AreaChart } from "./charts/area-chart"
import { BarChart } from "./charts/bar-chart"
import { LineChart } from "./charts/line-chart"
import { PieChart } from "./charts/pie-chart"
import { RadarChart } from "./charts/radar-chart"
import { RadialChart } from "./charts/radial-chart"

interface ChartWidgetProps {
  config: {
    subtype: string
    header: string
    description: string
    options?: any
    series: Array<{
      name: string
      data: Array<{
        x: string
        y: number
      }>
      color?: string
    }>
  }
}

export function ChartWidget({ config }: ChartWidgetProps) {
  const { subtype, header, description, options = {}, series } = config

  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle>{header}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="p-0 pb-4">
        <div className="h-[300px] w-full">
          {subtype === "area" && <AreaChart series={series} options={options} />}
          {subtype === "bar" && <BarChart series={series} options={options} />}
          {subtype === "line" && <LineChart series={series} options={options} />}
          {subtype === "pie" && <PieChart series={series} options={options} />}
          {subtype === "radar" && <RadarChart series={series} options={options} />}
          {subtype === "radial" && <RadialChart series={series} options={options} />}
        </div>
      </CardContent>
    </Card>
  )
}
