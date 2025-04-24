"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowDown, ArrowUp, Briefcase, DollarSign, ThumbsUp, Users } from "lucide-react"
import { cn } from "@/lib/utils"

interface MetricCardProps {
  config: {
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
  }
}

export function MetricCard({ config }: MetricCardProps) {
  const {
    header,
    description,
    value,
    valueSuffix = "",
    valuePrefix = "",
    valueFormatting = "number",
    icon,
    trend,
  } = config

  // Format the value based on valueFormatting
  let formattedValue: string | number = value
  if (valueFormatting === "currency" && typeof value === "number") {
    formattedValue = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value)
  } else if (valueFormatting === "number" && typeof value === "number") {
    formattedValue = new Intl.NumberFormat("en-US").format(value)
  } else if (valueFormatting === "percent" && typeof value === "number") {
    formattedValue = `${value}%`
  }

  // If we have a currency formatting, don't add the prefix (it's already included)
  const displayValue = valueFormatting === "currency" ? formattedValue : `${valuePrefix}${formattedValue}${valueSuffix}`

  // Render the appropriate icon
  const IconComponent =
    {
      DollarSign: DollarSign,
      Users: Users,
      ThumbsUp: ThumbsUp,
      Briefcase: Briefcase,
    }[icon || ""] || null

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>{header}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
        {IconComponent && (
          <div className="rounded-full p-2 bg-muted">
            <IconComponent className="h-4 w-4" />
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{displayValue}</div>
        {trend && (
          <div className="flex items-center mt-2 text-sm">
            <span className={cn("flex items-center", trend.direction === "up" ? "text-emerald-500" : "text-rose-500")}>
              {trend.direction === "up" ? <ArrowUp className="h-4 w-4 mr-1" /> : <ArrowDown className="h-4 w-4 mr-1" />}
              {trend.value}%
            </span>
            <span className="text-muted-foreground ml-1">{trend.label}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
