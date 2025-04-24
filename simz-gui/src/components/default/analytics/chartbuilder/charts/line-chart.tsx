"use client"

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart as RechartsLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { ChartContainer } from "@/components/ui/chart"

interface LineChartProps {
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
    type?: "linear" | "monotone" | "step" | "stepBefore" | "stepAfter" | "natural" | "basis"
    showDots?: boolean
    dotSize?: number
    activeDotSize?: number
    strokeWidth?: number
  }
}

export function LineChart({ series, options = {} }: LineChartProps) {
  const {
    showGrid = false,
    showLegend = false,
    showTooltip = true,
    xAxisLabel,
    yAxisLabel,
    type = "monotone",
    showDots = true,
    dotSize = 4,
    activeDotSize = 6,
    strokeWidth = 2,
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
        <RechartsLineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
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
            <Line
              key={`line-${index}`}
              type={type}
              dataKey={`data${index}`}
              name={serie.name}
              stroke={`var(--color-data${index})`}
              strokeWidth={strokeWidth}
              dot={showDots ? { r: dotSize, strokeWidth: 2 } : false}
              activeDot={showDots ? { r: activeDotSize, strokeWidth: 2 } : false}
            />
          ))}

          {showLegend && <Legend verticalAlign="bottom" height={36} wrapperStyle={{ paddingTop: 20, bottom: 0 }} />}
        </RechartsLineChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
