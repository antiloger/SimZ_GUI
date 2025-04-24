import Dashboard from "./chartbuilder/dashboard";
import ComponentDetailBar from "./componentDetailBar";


const dashboardConfig = [
  // Row 1: Stats cards
  {
    id: "total-revenue",
    type: "card",
    header: "Total Revenue",
    description: "Year to date revenue",
    value: 125000,
    valuePrefix: "$",
    valueFormatting: "currency",
    icon: "DollarSign",
    trend: {
      value: 12.5,
      direction: "up",
      label: "from last month",
    },
    size: {
      cols: 1,
      rows: 1,
    },
  },
  {
    id: "new-customers",
    type: "card",
    header: "New Customers",
    description: "Customers acquired this month",
    value: 1250,
    valueFormatting: "number",
    icon: "Users",
    trend: {
      value: 8.2,
      direction: "up",
      label: "from last month",
    },
    size: {
      cols: 1,
      rows: 1,
    },
  },
  {
    id: "satisfaction",
    type: "card",
    header: "Satisfaction Score",
    description: "Average customer satisfaction",
    value: 85,
    valueSuffix: "%",
    icon: "ThumbsUp",
    trend: {
      value: 2.1,
      direction: "up",
      label: "from last month",
    },
    size: {
      cols: 1,
      rows: 1,
    },
  },
  {
    id: "active-projects",
    type: "card",
    header: "Active Projects",
    description: "Projects currently in progress",
    value: 24,
    icon: "Briefcase",
    trend: {
      value: 3,
      direction: "down",
      label: "from last month",
    },
    size: {
      cols: 1,
      rows: 1,
    },
  },

  // Row 2: Line and Area charts
  {
    id: "monthly-sales",
    type: "chart",
    subtype: "line",
    header: "Monthly Sales",
    description: "Sales performance over the last 7 months",
    options: {
      showGrid: true,
      showLegend: true,
      showTooltip: true,
      yAxisLabel: "Sales ($)",
      xAxisLabel: "Month",
      type: "monotone", // linear, monotone, step, stepBefore, stepAfter, natural, basis
      showDots: true,
      dotSize: 4,
      strokeWidth: 2,
    },
    series: [
      {
        name: "2023",
        data: [
          { x: "Jan", y: 65 },
          { x: "Feb", y: 59 },
          { x: "Mar", y: 80 },
          { x: "Apr", y: 81 },
          { x: "May", y: 56 },
          { x: "Jun", y: 55 },
          { x: "Jul", y: 40 },
        ],
        color: "chart-1",
      },
      {
        name: "2022",
        data: [
          { x: "Jan", y: 45 },
          { x: "Feb", y: 52 },
          { x: "Mar", y: 60 },
          { x: "Apr", y: 70 },
          { x: "May", y: 45 },
          { x: "Jun", y: 50 },
          { x: "Jul", y: 35 },
        ],
        color: "chart-2",
      },
    ],
    size: {
      cols: 2,
      rows: 1,
    },
  },
  {
    id: "website-traffic",
    type: "chart",
    subtype: "area",
    header: "Website Traffic",
    description: "Monthly website visitors",
    options: {
      showGrid: true,
      showTooltip: true,
      yAxisLabel: "Visitors",
      xAxisLabel: "Month",
      stacked: true,
      type: "monotone", // linear, monotone, step, stepBefore, stepAfter, natural
    },
    series: [
      {
        name: "Desktop",
        data: [
          { x: "Jan", y: 1200 },
          { x: "Feb", y: 1900 },
          { x: "Mar", y: 3000 },
          { x: "Apr", y: 4900 },
          { x: "May", y: 3800 },
          { x: "Jun", y: 4200 },
        ],
        color: "chart-1",
      },
      {
        name: "Mobile",
        data: [
          { x: "Jan", y: 800 },
          { x: "Feb", y: 1200 },
          { x: "Mar", y: 1800 },
          { x: "Apr", y: 2400 },
          { x: "May", y: 2200 },
          { x: "Jun", y: 2600 },
        ],
        color: "chart-2",
      },
    ],
    size: {
      cols: 2,
      rows: 1,
    },
  },

  // Row 3: Bar and Pie charts
  {
    id: "quarterly-revenue",
    type: "chart",
    subtype: "bar",
    header: "Quarterly Revenue",
    description: "Revenue by quarter",
    options: {
      showGrid: true,
      showTooltip: true,
      showLegend: true,
      yAxisLabel: "Revenue ($)",
      xAxisLabel: "Quarter",
      layout: "horizontal",
      barType: "stacked", // grouped, stacked
      barSize: 20,
      barRadius: [4, 4, 0, 0],
    },
    series: [
      {
        name: "2023",
        data: [
          { x: "Q1", y: 12500 },
          { x: "Q2", y: 15000 },
          { x: "Q3", y: 18000 },
          { x: "Q4", y: 21000 },
        ],
        color: "chart-1",
      },
      {
        name: "2022",
        data: [
          { x: "Q1", y: 10000 },
          { x: "Q2", y: 12000 },
          { x: "Q3", y: 15000 },
          { x: "Q4", y: 18000 },
        ],
        color: "chart-2",
      },
    ],
    size: {
      cols: 2,
      rows: 1,
    },
  },
  {
    id: "revenue-sources",
    type: "chart",
    subtype: "pie",
    header: "Revenue Sources",
    description: "Revenue breakdown by source",
    options: {
      showTooltip: true,
      showLegend: true,
      innerRadius: 0,
      outerRadius: "80%",
      paddingAngle: 2,
      showLabels: true,
      labelType: "namePercent", // percent, value, name, namePercent
    },
    series: [
      {
        name: "Sources",
        data: [
          { x: "Direct", y: 540 },
          { x: "Affiliate", y: 300 },
          { x: "E-mail", y: 220 },
          { x: "Social", y: 180 },
          { x: "Other", y: 120 },
        ],
      },
    ],
    size: {
      cols: 2,
      rows: 1,
    },
  },

  // Row 4: Radar and Radial charts
  {
    id: "skills-assessment",
    type: "chart",
    subtype: "radar",
    header: "Skills Assessment",
    description: "Team skills evaluation",
    options: {
      showTooltip: true,
      showLegend: true,
      showGrid: true,
      maxValue: 100,
      fillOpacity: 0.2,
      strokeWidth: 2,
    },
    series: [
      {
        name: "Current Team",
        data: [
          { x: "Coding", y: 80 },
          { x: "Design", y: 70 },
          { x: "Marketing", y: 60 },
          { x: "Sales", y: 85 },
          { x: "Support", y: 75 },
          { x: "Research", y: 65 },
        ],
        color: "chart-1",
      },
      {
        name: "Industry Average",
        data: [
          { x: "Coding", y: 65 },
          { x: "Design", y: 60 },
          { x: "Marketing", y: 70 },
          { x: "Sales", y: 75 },
          { x: "Support", y: 65 },
          { x: "Research", y: 60 },
        ],
        color: "chart-2",
      },
    ],
    size: {
      cols: 2,
      rows: 1,
    },
  },
  {
    id: "project-completion",
    type: "chart",
    subtype: "radial",
    header: "Project Completion",
    description: "Current project status",
    options: {
      showTooltip: true,
      showLegend: true,
    },
    series: [
      {
        name: "Projects",
        data: [
          { x: "Project A", y: 75 },
          { x: "Project B", y: 90 },
          { x: "Project C", y: 60 },
        ],
      },
    ],
    size: {
      cols: 2,
      rows: 1,
    },
  },
]

function AnalyticsBuild() {
  return (
    <div className="analytics-build">
      <div className="container mx-auto py-8">
        <ComponentDetailBar componentName="Resource 1" componentType="Resource" />
        // tab need in here
        <Dashboard config={dashboardConfig} />
      </div>
    </div>
  );
}

export default AnalyticsBuild;
