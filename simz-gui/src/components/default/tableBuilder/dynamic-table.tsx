import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { cn } from "@/lib/utils"

// Type for the data that will be passed to the table
export type TableData = Record<string, any>[]

// Props for the DynamicTable component
export interface DynamicTableProps {
  data: TableData
  className?: string
  tableClassName?: string
  headerClassName?: string
  rowClassName?: (index: number) => string | undefined
  cellClassName?: (key: string, value: any, index: number) => string | undefined
  excludeColumns?: string[]
  columnOrder?: string[]
  columnLabels?: Record<string, string>
  emptyMessage?: string
}

export function DynamicTable({
  data,
  className,
  tableClassName,
  headerClassName,
  rowClassName,
  cellClassName,
  excludeColumns = [],
  columnOrder = [],
  columnLabels = {},
  emptyMessage = "No data available",
}: DynamicTableProps) {
  // Return early if no data is provided
  if (!data || data.length === 0) {
    return <div className="text-center py-4">{emptyMessage}</div>
  }

  // Get all unique keys from all objects in the data array
  const allKeys = Array.from(
    new Set(data.flatMap((item) => Object.keys(item)).filter((key) => !excludeColumns.includes(key))),
  )

  // Determine the final column order
  const finalColumnOrder = [
    // First include columns specified in columnOrder (if they exist in the data)
    ...columnOrder.filter((key) => allKeys.includes(key)),
    // Then include any remaining columns not specified in columnOrder
    ...allKeys.filter((key) => !columnOrder.includes(key)),
  ]

  return (
    <div className={cn("relative w-full overflow-auto", className)}>
      <Table className={cn("w-full", tableClassName)}>
        <TableHeader>
          <TableRow className={headerClassName}>
            {finalColumnOrder.map((key) => (
              <TableHead key={key}>{columnLabels[key] || key}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((row, rowIndex) => (
            <TableRow key={rowIndex} className={rowClassName ? rowClassName(rowIndex) : undefined}>
              {finalColumnOrder.map((key) => (
                <TableCell
                  key={`${rowIndex}-${key}`}
                  className={cellClassName ? cellClassName(key, row[key], rowIndex) : undefined}
                >
                  {row[key] !== undefined ? String(row[key]) : "—"}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
