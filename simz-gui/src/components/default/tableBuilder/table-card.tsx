import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { DynamicTable, type TableData } from "@/components/default/tableBuilder/dynamic-table"

export interface TableCardProps {
  id: string
  title: string
  description: string
  data: TableData
  columnOrder?: string[]
  columnLabels?: Record<string, string>
  className?: string
}

export function TableCard({
  id,
  title,
  description,
  data,
  columnOrder = [],
  columnLabels = {},
  className,
}: TableCardProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length > 0 ? (
          <DynamicTable
            data={data}
            columnOrder={columnOrder}
            columnLabels={columnLabels}
            emptyMessage="No data available for this table"
            rowClassName={(index) => (index % 2 === 0 ? "bg-muted/50" : undefined)}
          />
        ) : (
          <div className="text-center py-8 text-muted-foreground">No data available for this table</div>
        )}
      </CardContent>
    </Card>
  )
}
