"use client"

import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart as RechartsRadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts"
import { ChartContainer } from "@/components/ui/chart"

interface RadarChartProps {
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
    maxValue?: number
    fillOpacity?: number
    strokeWidth?: number
  }
}

export function RadarChart({ series, options = {} }: RadarChartProps) {
  const {
    showGrid = true,
    showLegend = false,
    showTooltip = true,
    maxValue = 100,
    fillOpacity = 0.2,
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
  // For radar charts, we need to transform the data differently
  const chartData = series[0].data.map((item, i) => {
    const dataPoint: Record<string, any> = {
      subject: item.x,
      fullMark: maxValue,
    }

    series.forEach((serie, serieIndex) => {
      if (serie.data[i]) {
        dataPoint[`data${serieIndex}`] = serie.data[i].y
      }
    })

    return dataPoint
  })

  return (
    <ChartContainer config={chartConfig} className="h-full w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          {showGrid && <PolarGrid />}
          <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, maxValue]} tick={{ fontSize: 12 }} />

          {series.map((serie, index) => (
            <Radar
              key={`radar-${index}`}
              name={serie.name}
              dataKey={`data${index}`}
              stroke={`var(--color-data${index})`}
              fill={`var(--color-data${index})`}
              fillOpacity={fillOpacity}
              strokeWidth={strokeWidth}
            />
          ))}

          {showTooltip && <Tooltip />}

          {showLegend && <Legend verticalAlign="bottom" align="center" wrapperStyle={{ paddingTop: 20, bottom: 0 }} />}
        </RechartsRadarChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
