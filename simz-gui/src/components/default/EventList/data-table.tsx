import type React from "react"

import { useState, useEffect } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Search, MoreHorizontal } from "lucide-react"
import { DataTableDialog } from "./data-table-dialog"
import { useSocketStore } from "@/utils/socketIo"
import { SimDataState } from "@/states/simDataState"
import { EventListParams } from "@/types/socketT"

interface DataTableProps {
  runId: string
}

export function DataTable({ runId }: DataTableProps) {
  // Table state
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [totalRecords, setTotalRecords] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [columns, setColumns] = useState<string[]>([])

  //
  // Pagination state
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  // Sorting state
  const [sortColumn, setSortColumn] = useState("time")
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc")

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState("")
  const [searchColumns, setSearchColumns] = useState<string[]>([])
  const [filterConditions, setFilterConditions] = useState<Record<string, any>>({})
  const [showFilters, setShowFilters] = useState(false)

  // Detail dialog state
  const [selectedRow, setSelectedRow] = useState<any | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  const { projectName } = SimDataState()
  const { geteventlist } = useSocketStore()

  // Fetch data
  const fetchData = async () => {
    setLoading(true)

    try {
      // In a real application, you would call your API function here
      // const response = await get_full_tabel("projectName", "runId", {
      //   page,
      //   page_size: pageSize,
      //   sort_column: sortColumn,
      //   sort_direction: sortDirection,
      //   search_query: searchQuery,
      //   search_columns: searchColumns.length > 0 ? searchColumns : undefined,
      //   filter_conditions: Object.keys(filterConditions).length > 0 ? filterConditions : undefined,
      //   include_columns: ["time", "component_id", "component_type", "action", "values", "PDV", "addition"]
      // })

      // For demonstration, we'll use mock data
      if (!projectName) { return}
      console.log("[EVENTLIST] Fetching data for project:", page, pageSize, sortColumn, sortDirection, searchQuery, searchColumns, filterConditions)
      const response = await geteventlist(
        projectName,
        runId,
        {
        page: page,
        page_size: pageSize,
        sort_column: sortColumn,
        sort_direction: sortDirection,
        search_query: searchQuery,
        search_columns: searchColumns.length > 0 ? searchColumns : undefined,
        filter_conditions: Object.keys(filterConditions).length > 0 ? filterConditions : undefined,
        } as EventListParams,
      ) 

      console.log("[EVENTLIST] Fetched data:", response)

      setData(response.data)
      setTotalRecords(response.total)
      setTotalPages(response.totalPages)
      setColumns(response.columns)
    } catch (error) {
      console.error("Error fetching data:", error)
    } finally {
      setLoading(false)
    }
  }

  // Initial data fetch and when dependencies change
  useEffect(() => {
    fetchData()
  }, [page, pageSize, sortColumn, sortDirection, searchQuery, JSON.stringify(filterConditions)])

  // Handle sort
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortColumn(column)
      setSortDirection("asc")
    }
    setPage(1) // Reset to first page when sorting changes
  }

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1) // Reset to first page when search changes
  }

  // Handle row click to show details
  const handleRowDetails = (row: any) => {
    setSelectedRow(row)
    setDialogOpen(true)
  }

  // Visible columns in the main table
  const visibleColumns = ["time", "component_id", "component_type", "action"]

  return (
    <div className="space-y-4">
      {/* Advanced search form */}
      <div className="bg-muted/40 p-4 rounded-lg mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium">Advanced Search</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setFilterConditions({})
              setSearchQuery("")
              setPage(1)
            }}
          >
            Clear All
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {/* Time input */}
          <div>
            <label className="text-sm font-medium mb-1 block">Time</label>
            <Input
              type="number"
              placeholder="Enter time"
              value={filterConditions.time || ""}
              onChange={(e) => {
                const value = e.target.value
                if (value === "") {
                  const newFilters = { ...filterConditions }
                  delete newFilters.time
                  setFilterConditions(newFilters)
                } else {
                  setFilterConditions({ ...filterConditions, time: Number.parseInt(value) })
                }
                setPage(1)
              }}
            />
          </div>

          {/* Component ID input */}
          <div>
            <label className="text-sm font-medium mb-1 block">Component ID</label>
            <Input
              type="text"
              placeholder="Enter component ID"
              value={filterConditions.component_id || ""}
              onChange={(e) => {
                const value = e.target.value
                if (value === "") {
                  const newFilters = { ...filterConditions }
                  delete newFilters.component_id
                  setFilterConditions(newFilters)
                } else {
                  setFilterConditions({ ...filterConditions, component_id: value })
                }
                setPage(1)
              }}
            />
          </div>

          {/* Component Type selector */}
          <div>
            <label className="text-sm font-medium mb-1 block">Component Type</label>
            <Select
              value={filterConditions.component_type || ""}
              onValueChange={(value) => {
                if (value === "") {
                  const newFilters = { ...filterConditions }
                  delete newFilters.component_type
                  setFilterConditions(newFilters)
                } else {
                  setFilterConditions({ ...filterConditions, component_type: value })
                }
                setPage(1)
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All types</SelectItem>
                <SelectItem value="generator">Generator</SelectItem>
                <SelectItem value="resource">Resource</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Action selector */}
          <div>
            <label className="text-sm font-medium mb-1 block">Action</label>
            <Select
              value={filterConditions.action || ""}
              onValueChange={(value) => {
                if (value === "") {
                  const newFilters = { ...filterConditions }
                  delete newFilters.action
                  setFilterConditions(newFilters)
                } else {
                  setFilterConditions({ ...filterConditions, action: value })
                }
                setPage(1)
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select action" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All actions</SelectItem>
                <SelectItem value="GENERATE">GENERATE</SelectItem>
                <SelectItem value="QUEUED">QUEUED</SelectItem>
                <SelectItem value="ENTER">ENTER</SelectItem>
                <SelectItem value="Exit">Exit</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Container ID input */}
          <div>
            <label className="text-sm font-medium mb-1 block">Container ID</label>
            <Input
              type="text"
              placeholder="Enter container ID"
              value={filterConditions.containerId || ""}
              onChange={(e) => {
                const value = e.target.value
                if (value === "") {
                  const newFilters = { ...filterConditions }
                  delete newFilters.containerId
                  setFilterConditions(newFilters)
                } else {
                  setFilterConditions({ ...filterConditions, containerId: value })
                }
                setPage(1)
              }}
            />
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <Button onClick={fetchData} className="ml-auto">
            Search
          </Button>
        </div>
      </div>

      {/* Table controls */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between mb-4">
        <div className="flex items-center gap-2">
          <Input
            type="search"
            placeholder="Quick search..."
            className="w-full sm:w-[300px]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && fetchData()}
          />
          <Button onClick={fetchData} variant="secondary">
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Select
            value={pageSize.toString()}
            onValueChange={(value) => {
              setPageSize(Number.parseInt(value))
              setPage(1)
            }}
          >
            <SelectTrigger className="w-[100px]">
              <SelectValue placeholder="Rows" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="5">5 rows</SelectItem>
              <SelectItem value="10">10 rows</SelectItem>
              <SelectItem value="20">20 rows</SelectItem>
              <SelectItem value="50">50 rows</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Data table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {visibleColumns.map((column) => (
                <TableHead key={column} className="cursor-pointer hover:bg-muted/50" onClick={() => handleSort(column)}>
                  <div className="flex items-center">
                    {column.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                    {sortColumn === column && <span className="ml-1">{sortDirection === "asc" ? "↑" : "↓"}</span>}
                  </div>
                </TableHead>
              ))}
              <TableHead className="w-[80px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={visibleColumns.length + 1} className="h-24 text-center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={visibleColumns.length + 1} className="h-24 text-center">
                  No results found.
                </TableCell>
              </TableRow>
            ) : (
              data.map((row, index) => (
                <TableRow key={index}>
                  {visibleColumns.map((column) => (
                    <TableCell key={column}>
                      {typeof row[column] === "object"
                        ? JSON.stringify(row[column]).substring(0, 30) + "..."
                        : String(row[column])}
                    </TableCell>
                  ))}
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={() => handleRowDetails(row)}>
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing {data.length > 0 ? (page - 1) * pageSize + 1 : 0} to {Math.min(page * pageSize, totalRecords)} of{" "}
          {totalRecords} records
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={() => setPage(1)} disabled={page === 1}>
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={() => setPage(page - 1)} disabled={page === 1}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium">
            Page {page} of {totalPages}
          </span>
          <Button variant="outline" size="sm" onClick={() => setPage(page + 1)} disabled={page === totalPages}>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={() => setPage(totalPages)} disabled={page === totalPages}>
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Detail dialog */}
      <DataTableDialog open={dialogOpen} onOpenChange={setDialogOpen} data={selectedRow} />
    </div>
  )
}
