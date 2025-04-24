"use client"

import { ResponsiveContainer } from "recharts"
import { ChartContainer } from "@/components/ui/chart"

interface RadialChartProps {
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
    startAngle?: number
    endAngle?: number
    innerRadius?: string | number
    outerRadius?: string | number
  }
}

export function RadialChart({ series, options = {} }: RadialChartProps) {
  const { showLegend = false } = options

  // We only support one series for radial charts
  const data = series[0].data

  // Create a config with multiple colors for radial segments
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

  // Calculate average for center label
  const total = data.reduce((sum, item) => sum + item.y, 0)
  const average = Math.round(total / data.length)

  return (
    <ChartContainer config={chartConfig} className="h-full w-full">
      <ResponsiveContainer width="100%" height="100%">
        <div className="flex flex-col h-full w-full">
          {/* Custom radial chart implementation */}
          <div className="flex-1 flex items-center justify-center relative">
            {/* Center label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
              <div className="text-3xl font-bold">{average}%</div>
              <div className="text-sm text-muted-foreground">Average</div>
            </div>

            {/* Radial bars */}
            <div className="w-full h-full flex items-center justify-center">
              <div className="relative w-4/5 h-4/5">
                {data.map((item, index) => (
                  <RadialProgressBar
                    key={index}
                    value={item.y}
                    index={index}
                    total={data.length}
                    color={`var(--color-segment${index})`}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Legend */}
          {showLegend && (
            <div className="mt-4 flex flex-wrap justify-center gap-4">
              {data.map((item, index) => (
                <div key={index} className="flex items-center">
                  <div
                    className="w-3 h-3 mr-2 rounded-full"
                    style={{ backgroundColor: `var(--color-segment${index})` }}
                  />
                  <span className="text-sm">
                    {item.x}: {item.y}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </ResponsiveContainer>
    </ChartContainer>
  )
}

// Custom radial progress bar component
function RadialProgressBar({
  value,
  index,
  total,
  color,
}: {
  value: number
  index: number
  total: number
  color: string
}) {
  // Calculate the thickness of each ring
  const thickness = 20

  // Calculate the radius based on index (outer rings are larger)
  const size = 100 - index * (thickness + 5)

  // Calculate the circumference
  const radius = size / 2
  const circumference = 2 * Math.PI * radius

  // Calculate the dash offset based on the value (0-100)
  const dashOffset = circumference - (value / 100) * circumference

  return (
    <div
      className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
      style={{
        width: `${size}%`,
        height: `${size}%`,
      }}
    >
      <svg width="100%" height="100%" viewBox="0 0 100 100" className="rotate-[-90deg]">
        {/* Background circle */}
        <circle cx="50" cy="50" r={radius} fill="transparent" stroke="rgba(0,0,0,0.1)" strokeWidth={thickness} />

        {/* Progress circle */}
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth={thickness}
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
        />

        {/* Value label */}
        <text
          x="50"
          y="50"
          textAnchor="middle"
          dominantBaseline="middle"
          className="fill-foreground text-xs font-medium rotate-90"
          style={{ transform: "rotate(90deg)", transformOrigin: "center" }}
        >
          {value}%
        </text>
      </svg>
    </div>
  )
}
