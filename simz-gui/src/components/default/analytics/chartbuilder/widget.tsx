"use client"

import { ChartWidget } from "./chart-widget"
import { MetricCard } from "./metric-card"

// Define chart-specific config properties
interface ChartConfig {
  type: "chart"
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
  size?: {
    cols?: 1 | 2 | 3 | 4
    rows?: 1 | 2 | 3 | 4
  }
}

// Define card-specific config properties to match MetricCard requirements
interface CardConfig {
  type: "card"
  header: string
  description: string
  value: number | string
  valueSuffix?: string
  valuePrefix?: string
  valueFormatting?: "number" | "currency" | "percent"
  icon?: string
  trend?: {
    value: number
    direction: "up" | "down"
    label: string
  }
  size?: {
    cols?: 1 | 2 | 3 | 4
    rows?: 1 | 2 | 3 | 4
  }
}

// Union type for all widget configurations
type WidgetConfig = ChartConfig | CardConfig

interface WidgetProps {
  config: WidgetConfig
}

export function Widget({ config }: WidgetProps) {
  const { type, size = { cols: 1, rows: 1 } } = config

  // Calculate column span based on size.cols
  const colSpan = size.cols || 1
  const rowSpan = size.rows || 1

  // Create responsive column classes with type safety
  const colClasses = {
    1: "col-span-1",
    2: "col-span-1 md:col-span-2",
    3: "col-span-1 md:col-span-2 lg:col-span-3",
    4: "col-span-1 md:col-span-2 lg:col-span-4",
  }[colSpan as 1 | 2 | 3 | 4] || "col-span-1"

  // Create row span classes with type safety
  const rowClasses = {
    1: "row-span-1",
    2: "row-span-2",
    3: "row-span-3",
    4: "row-span-4",
  }[rowSpan as 1 | 2 | 3 | 4] || "row-span-1"

  // Combine classes
  const sizeClasses = `${colClasses} ${rowClasses}`

  return (
    <div className={sizeClasses}>
      {type === "chart" && <ChartWidget config={config as ChartConfig} />}
      {type === "card" && <MetricCard config={config as CardConfig} />}
    </div>
  )
}
