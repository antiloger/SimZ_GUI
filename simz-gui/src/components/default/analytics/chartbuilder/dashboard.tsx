import { Widget } from "./widget"

interface DashboardProps {
  config: any[] | any
}

export default function Dashboard({ config }: DashboardProps) {
  // Group widgets by row based on their size
  const organizeWidgets = () => {
    // Check if config is an array before calling map
    if (!Array.isArray(config)) {
      console.error("Dashboard config is not an array:", config);
      // If config has a dashboardData property that is an array, use that
      if (config && Array.isArray(config.dashboardData)) {
        return config.dashboardData.map((widget, index) => ({
          ...widget,
          index,
        }));
      }
      // Otherwise return an empty array as fallback
      return [];
    }

    // Sort widgets by their position in the config array
    // This ensures a consistent layout
    return config.map((widget, index) => ({
      ...widget,
      index,
    }));
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
