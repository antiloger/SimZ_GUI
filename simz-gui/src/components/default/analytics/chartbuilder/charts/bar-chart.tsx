"use client"

import {
  Bar,
  BarChart as RechartsBarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { ChartContainer } from "@/components/ui/chart"

interface BarChartProps {
  series: Array<{
    name: string
    data: Array<{
      x: string
      y: number
    }>
    color?: string
  }>
  options?: {
    showGrid?: boolean
    showLegend?: boolean
    showTooltip?: boolean
    yAxisLabel?: string
    xAxisLabel?: string
    layout?: "vertical" | "horizontal"
    barType?: "grouped" | "stacked"
    barSize?: number
    barRadius?: number | [number, number, number, number]
  }
}

export function BarChart({ series, options = {} }: BarChartProps) {
  const {
    showGrid = false,
    showLegend = false,
    showTooltip = true,
    layout = "horizontal",
    xAxisLabel,
    yAxisLabel,
    barType = "grouped",
    barSize,
    barRadius = [4, 4, 0, 0],
  } = options

  // Transform data for the chart config
  const chartConfig = series.reduce(
    (config, serie, index) => {
      config[`data${index}`] = {
        label: serie.name,
        color: serie.color ? `hsl(var(--${serie.color}))` : `hsl(var(--chart-${index + 1}))`,
      }
      return config
    },
    {} as Record<string, { label: string; color: string }>,
  )

  // Transform data for Recharts
  const chartData = series[0].data.map((item, i) => {
    const dataPoint: Record<string, any> = {
      name: item.x,
    }

    series.forEach((serie, serieIndex) => {
      if (serie.data[i]) {
        dataPoint[`data${serieIndex}`] = serie.data[i].y
      }
    })

    return dataPoint
  })

  return (
    <ChartContainer config={chartConfig} className="h-full w-full px-4">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 40 }} layout={layout}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" />}

          <XAxis
            dataKey={layout === "vertical" ? undefined : "name"}
            type={layout === "vertical" ? "number" : "category"}
            tickLine={false}
            axisLine={true}
            tickMargin={10}
            label={xAxisLabel ? { value: xAxisLabel, position: "insideBottom", offset: -10, dy: 10 } : undefined}
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
            height={60}
          />

          <YAxis
            dataKey={layout === "vertical" ? "name" : undefined}
            type={layout === "vertical" ? "category" : "number"}
            tickLine={false}
            axisLine={true}
            tickMargin={10}
            label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: "insideLeft", offset: -5 } : undefined}
            tick={{ fontSize: 12 }}
            width={60}
          />

          {showTooltip && <Tooltip />}

          {series.map((serie, index) => (
            <Bar
              key={`bar-${index}`}
              dataKey={`data${index}`}
              name={serie.name}
              fill={`var(--color-data${index})`}
              radius={barRadius}
              stackId={barType === "stacked" ? "stack" : undefined}
              barSize={barSize}
            />
          ))}

          {showLegend && <Legend verticalAlign="bottom" height={36} wrapperStyle={{ paddingTop: 20, bottom: 0 }} />}
        </RechartsBarChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
