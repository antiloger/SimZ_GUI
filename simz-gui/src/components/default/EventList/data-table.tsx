"use client"

import { useState, useEffect } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import { Eye, AlertCircle } from "lucide-react"
import { DataDialog } from "./data-dialog"
import { SearchForm } from "./search-form"
import { Badge } from "@/components/ui/badge"

// Define the table data interface
interface TableData {
  time: number
  component_id: string
  component_type: string
  action: string
  values: { [key: string]: any }
  PDV: { [key: string]: { [key: string]: any } }
  addition: { [key: string]: any }
}

// Define the search form values interface
interface SearchFormValues {
  componentId?: string
  componentType?: string
  action?: string
  timeSearchType: "range" | "specific"
  startTimeValue?: string
  endTimeValue?: string
  specificTimeValue?: string
  timeUnit: string
  pdvKey?: string
  pdvValue?: string
}

export function EventListTable() {
  // State for pagination
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(10)
  const [totalPages, setTotalPages] = useState(1)

  // State for table data
  const [tableData, setTableData] = useState<TableData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // State for dialog
  const [selectedRow, setSelectedRow] = useState<TableData | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  // State for current search
  const [currentSearch, setCurrentSearch] = useState<SearchFormValues | null>(null)

  // Initialize socket connection and fetch data
  useEffect(() => {
    // // Connect to socket
    // socketClient.connect()
    //
    // // Initial data fetch
    // fetchData()
    //
    // // Listen for data updates
    // socketClient.on("dataUpdate", handleDataUpdate)
    //
    // // Cleanup on unmount
    // return () => {
    //   socketClient.off("dataUpdate", handleDataUpdate)
    // }
  }, [])

  // Fetch data when page or search changes
  useEffect(() => {
    fetchData()
  }, [page, limit, currentSearch])

  // Handle data update from socket
  const handleDataUpdate = (data: { tableData: TableData[]; totalPages: number }) => {
    setTableData(data.tableData)
    setTotalPages(data.totalPages)
    setIsLoading(false)
  }

  // Fetch data function
  const fetchData = () => {
    setIsLoading(true)
    setError(null)

    try {
      // Prepare request payload
      const payload = {
        page,
        limit,
        filters: currentSearch || {},
      }

      // Emit socket event to fetch data
      // socketClient.emit("fetchData", payload)

      // For demo purposes, we'll simulate a response
      simulateSocketResponse()
    } catch (err) {
      console.error("Error fetching data:", err)
      setError("Failed to connect to the server. Please try again.")
      setIsLoading(false)
    }
  }

  // Simulate socket response (for demo only)
  const simulateSocketResponse = () => {
    setTimeout(() => {
      // Generate mock data
      const mockData: TableData[] = Array.from({ length: limit }, (_, i) => ({
        time: Math.floor(Math.random() * 100), // Random time value between 0-100
        component_id: `comp-${i + (page - 1) * limit}`,
        component_type: ["Button", "Form", "Table", "Modal", "Card"][Math.floor(Math.random() * 5)],
        action: ["Click", "Submit", "Load", "Close", "Update"][Math.floor(Math.random() * 5)],
        values: {
          value1: `Value ${i}`,
          value2: Math.random() * 100,
        },
        PDV: {
          property1: {
            key1: "value1",
            key2: "value2",
          },
          property2: {
            key3: "value3",
            key4: "value4",
          },
        },
        addition: {
          metadata: {
            timestamp: Date.now(),
            user: "user123",
          },
        },
      }))

      // Apply filters if search is active
      let filteredData = mockData
      if (currentSearch) {
        if (currentSearch.componentId) {
          filteredData = filteredData.filter((item) =>
            item.component_id.toLowerCase().includes(currentSearch.componentId!.toLowerCase()),
          )
        }

        if (currentSearch.componentType) {
          filteredData = filteredData.filter((item) =>
            item.component_type.toLowerCase().includes(currentSearch.componentType!.toLowerCase()),
          )
        }

        if (currentSearch.action) {
          filteredData = filteredData.filter((item) =>
            item.action.toLowerCase().includes(currentSearch.action!.toLowerCase()),
          )
        }

        // Time filters would be handled on the server in a real implementation
      }

      setTableData(filteredData)
      setTotalPages(10) // Mock total pages
      setIsLoading(false)
    }, 800)
  }

  // Handle search form submission
  const handleSearch = (searchData: SearchFormValues) => {
    setCurrentSearch(searchData)
    setPage(1) // Reset to first page on new search
  }

  // Handle search form reset
  const handleReset = () => {
    setCurrentSearch(null)
    setPage(1) // Reset to first page
  }

  // Handle page change
  const handlePageChange = (newPage: number) => {
    setPage(newPage)
  }

  // Open dialog with row data
  const handleViewDetails = (row: TableData) => {
    setSelectedRow(row)
    setDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <SearchForm onSearch={handleSearch} onReset={handleReset} />

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>Component ID</TableHead>
              <TableHead>Component Type</TableHead>
              <TableHead>Action</TableHead>
              <TableHead className="w-[80px]">Details</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, index) => (
                <TableRow key={`loading-${index}`} className="animate-pulse">
                  <TableCell>
                    <div className="h-4 w-32 bg-muted rounded"></div>
                  </TableCell>
                  <TableCell>
                    <div className="h-4 w-24 bg-muted rounded"></div>
                  </TableCell>
                  <TableCell>
                    <div className="h-4 w-20 bg-muted rounded"></div>
                  </TableCell>
                  <TableCell>
                    <div className="h-4 w-16 bg-muted rounded"></div>
                  </TableCell>
                  <TableCell>
                    <div className="h-8 w-8 bg-muted rounded-full"></div>
                  </TableCell>
                </TableRow>
              ))
            ) : tableData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  No results found. Try adjusting your search filters.
                </TableCell>
              </TableRow>
            ) : (
              tableData.map((row, index) => (
                <TableRow key={index} className="hover:bg-muted/50">
                  <TableCell>{row.time}</TableCell>
                  <TableCell>{row.component_id}</TableCell>
                  <TableCell>{row.component_type}</TableCell>
                  <TableCell>
                    <Badge>
                      {row.action}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleViewDetails(row)}
                      aria-label="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {!isLoading && tableData.length > 0 && (
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  if (page > 1) handlePageChange(page - 1)
                }}
                className={page <= 1 ? "pointer-events-none opacity-50" : ""}
              />
            </PaginationItem>

            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNumber = page <= 3 ? i + 1 : page >= totalPages - 2 ? totalPages - 4 + i : page - 2 + i

              if (pageNumber <= 0 || pageNumber > totalPages) return null

              return (
                <PaginationItem key={i}>
                  <PaginationLink
                    href="#"
                    onClick={(e) => {
                      e.preventDefault()
                      handlePageChange(pageNumber)
                    }}
                    isActive={page === pageNumber}
                  >
                    {pageNumber}
                  </PaginationLink>
                </PaginationItem>
              )
            })}

            <PaginationItem>
              <PaginationNext
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  if (page < totalPages) handlePageChange(page + 1)
                }}
                className={page >= totalPages ? "pointer-events-none opacity-50" : ""}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}

      <DataDialog open={dialogOpen} onOpenChange={setDialogOpen} data={selectedRow} />
    </div>
  )
}
