"use client"

import { Widget } from "./widget"


interface DashboardProps {
  config: any[]
}

export default function Dashboard({ config }: DashboardProps) {
  // Group widgets by row based on their size
  const organizeWidgets = () => {
    // Sort widgets by their position in the config array
    // This ensures a consistent layout
    return config.map((widget, index) => ({
      ...widget,
      index,
    }))
  }

  const widgets = organizeWidgets()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {widgets.map((widget) => (
        <Widget key={widget.id || widget.index} config={widget} />
      ))}
    </div>
  )
}
