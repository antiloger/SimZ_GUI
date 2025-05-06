import Dashboard from "./chartbuilder/dashboard";

const dashboardConfig = [
  // Row 1: Key Stats Cards
  {
    id: "total-entities",
    type: "card",
    header: "Total Entities Generated",
    description: "All items produced by the Generator",
    value: 5000,
    valueFormatting: "number",
    icon: "Box",
    trend: {
      value: 5.0,
      direction: "up",
      label: "from last run",
    },
    size: { cols: 1, rows: 1 }
  },
  {
    id: "water-produced",
    type: "card",
    header: "Water Entities",
    description: "Count of Water items",
    value: 3000,
    valueFormatting: "number",
    icon: "Droplet",
    trend: {
      value: 3.3,
      direction: "up",
      label: "from last run",
    },
    size: { cols: 1, rows: 1 }
  },
  {
    id: "salt-produced",
    type: "card",
    header: "Salt Entities",
    description: "Count of Salt items",
    value: 2000,
    valueFormatting: "number",
    icon: "Cube",
    trend: {
      value: -1.5,
      direction: "down",
      label: "from last run",
    },
    size: { cols: 1, rows: 1 }
  },
  {
    id: "polluted-produced",
    type: "card",
    header: "Polluted Water",
    description: "Count of Polluted Water output",
    value: 1200,
    valueFormatting: "number",
    icon: "AlertCircle",
    trend: {
      value: 2.0,
      direction: "up",
      label: "from last run",
    },
    size: { cols: 1, rows: 1 }
  },

  // Row 2: Flow Rate Line Chart
  {
    id: "flow-rate",
    type: "chart",
    subtype: "line",
    header: "Component Flow Rate",
    description: "Items processed per minute",
    options: {
      showGrid: true,
      showLegend: true,
      showTooltip: true,
      yAxisLabel: "Items / min",
      xAxisLabel: "Time (min)",
      type: "monotone",
      showDots: false,
      strokeWidth: 2
    },
    series: [
      {
        name: "Generator",
        data: [
          { x: 0, y: 50 },
          { x: 1, y: 52 },
          { x: 2, y: 48 },
          { x: 3, y: 55 },
          { x: 4, y: 53 },
        ]
      },
      {
        name: "Mixer",
        data: [
          { x: 0, y: 48 },
          { x: 1, y: 50 },
          { x: 2, y: 47 },
          { x: 3, y: 53 },
          { x: 4, y: 51 },
        ]
      },
      {
        name: "Refactor",
        data: [
          { x: 0, y: 30 },
          { x: 1, y: 32 },
          { x: 2, y: 28 },
          { x: 3, y: 35 },
          { x: 4, y: 33 },
        ]
      },
      {
        name: "Machine01",
        data: [
          { x: 0, y: 20 },
          { x: 1, y: 18 },
          { x: 2, y: 19 },
          { x: 3, y: 22 },
          { x: 4, y: 21 },
        ]
      }
    ],
    size: { cols: 2, rows: 1 }
  },

  // Row 3: Utilization Bar Chart
  {
    id: "component-utilization",
    type: "chart",
    subtype: "bar",
    header: "Component Utilization",
    description: "Percentage busy time per component",
    options: {
      showGrid: true,
      showTooltip: true,
      yAxisLabel: "Utilization (%)",
      xAxisLabel: "Component",
      layout: "horizontal",
      barType: "grouped",
      barSize: 20
    },
    series: [
      {
        name: "Utilization",
        data: [
          { x: "Generator", y: 95 },
          { x: "Mixer", y: 88 },
          { x: "Refactor", y: 72 },
          { x: "Machine01", y: 65 },
        ]
      }
    ],
    size: { cols: 2, rows: 1 }
  },

  // Row 4: Distribution Pie Chart
  {
    id: "output-distribution",
    type: "chart",
    subtype: "pie",
    header: "Output Distribution",
    description: "Final products as percent of total",
    options: {
      showTooltip: true,
      showLegend: true,
      innerRadius: 0,
      outerRadius: "70%",
      paddingAngle: 4,
      showLabels: true,
      labelType: "namePercent"
    },
    series: [
      {
        name: "Products",
        data: [
          { x: "Salt Water", y: 1800 },
          { x: "Polluted Water", y: 1200 }
        ]
      }
    ],
    size: { cols: 2, rows: 1 }
  }
];

function SimulationOverviewAnalyticsBuild() {
  return (

    <Dashboard config={dashboardConfig} />
  );
}

export default SimulationOverviewAnalyticsBuild;
