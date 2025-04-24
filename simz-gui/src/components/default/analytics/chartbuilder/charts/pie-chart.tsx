"use client"

import { Cell, Legend, Pie, PieChart as RechartsPieChart, ResponsiveContainer, Tooltip } from "recharts"
import { ChartContainer } from "@/components/ui/chart"

interface PieChartProps {
  series: Array<{
    name: string
    data: Array<{
      x: string
      y: number
    }>
  }>
  options?: {
    showLegend?: boolean
    showTooltip?: boolean
    innerRadius?: number | string
    outerRadius?: number | string
    paddingAngle?: number
    showLabels?: boolean
    labelType?: "percent" | "value" | "name" | "namePercent"
  }
}

export function PieChart({ series, options = {} }: PieChartProps) {
  const {
    showLegend = false,
    showTooltip = true,
    innerRadius = 0,
    outerRadius = "80%",
    paddingAngle = 0,
    showLabels = true,
    labelType = "namePercent",
  } = options

  // We only support one series for pie charts
  const data = series[0].data

  // Create a config with multiple colors for pie segments
  const chartConfig = data.reduce(
    (acc, item, index) => {
      acc[`segment${index}`] = {
        label: item.x,
        color: `hsl(var(--chart-${(index % 5) + 1}))`,
      }
      return acc
    },
    {} as Record<string, { label: string; color: string }>,
  )

  // Transform data for Recharts
  const chartData = data.map((item, index) => ({
    name: item.x,
    value: item.y,
    dataKey: `segment${index}`,
  }))

  // Calculate total for percentages
  const total = data.reduce((sum, item) => sum + item.y, 0)

  // Custom label formatter
  const renderCustomizedLabel = ({ name, value, percent }: { name: string; value: number; percent: number }) => {
    const formattedPercent = `${(percent * 100).toFixed(0)}%`

    switch (labelType) {
      case "percent":
        return formattedPercent
      case "value":
        return value
      case "name":
        return name
      case "namePercent":
      default:
        return `${name}: ${formattedPercent}`
    }
  }

  return (
    <ChartContainer config={chartConfig} className="h-full w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart margin={{ top: 10, right: 10, left: 10, bottom: 30 }}>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={outerRadius}
            innerRadius={innerRadius}
            paddingAngle={paddingAngle}
            label={showLabels ? renderCustomizedLabel : undefined}
            labelLine={showLabels}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={`var(--color-segment${index})`} />
            ))}
          </Pie>

          {showTooltip && <Tooltip />}

          {showLegend && (
            <Legend
              layout="horizontal"
              verticalAlign="bottom"
              align="center"
              wrapperStyle={{ paddingTop: 20, bottom: 0 }}
            />
          )}
        </RechartsPieChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
