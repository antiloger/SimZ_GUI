"use client"

import {
  Area,
  AreaChart as RechartsAreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { ChartContainer } from "@/components/ui/chart"

interface AreaChartProps {
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
    stacked?: boolean
    type?: "linear" | "monotone" | "step" | "stepBefore" | "stepAfter" | "natural"
  }
}

export function AreaChart({ series, options = {} }: AreaChartProps) {
  const {
    showGrid = false,
    showLegend = false,
    showTooltip = true,
    stacked = false,
    xAxisLabel,
    yAxisLabel,
    type = "monotone",
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
        <RechartsAreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" vertical={false} />}

          <XAxis
            dataKey="name"
            tickLine={false}
            axisLine={true}
            tickMargin={10}
            label={xAxisLabel ? { value: xAxisLabel, position: "insideBottom", offset: -10, dy: 10 } : undefined}
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />

          <YAxis
            tickLine={false}
            axisLine={true}
            tickMargin={10}
            label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: "insideLeft", offset: -5 } : undefined}
            tick={{ fontSize: 12 }}
            width={60}
          />

          {showTooltip && <Tooltip />}

          {series.map((serie, index) => (
            <Area
              key={`area-${index}`}
              type={type}
              dataKey={`data${index}`}
              name={serie.name}
              stackId={stacked ? "stack" : undefined}
              fill={`var(--color-data${index})`}
              fillOpacity={0.2}
              stroke={`var(--color-data${index})`}
              strokeWidth={2}
            />
          ))}

          {showLegend && <Legend verticalAlign="bottom" height={36} wrapperStyle={{ paddingTop: 20, bottom: 0 }} />}
        </RechartsAreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
