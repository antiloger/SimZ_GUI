import { useState, useEffect } from "react"

interface TableData {
  time: number
  component_id: string
  component_type: string
  action: string
  values: { [key: string]: any }
  PDV: { [key: string]: { [key: string]: any } }
  addition: { [key: string]: any }
}

interface FilterOptions {
  componentId?: string
  componentType?: string
  action?: string
  timeStart?: string
  timeEnd?: string
  specificTime?: string
  pdvKey?: string
  pdvValue?: string
}

interface FetchOptions {
  page: number
  limit: number
  filters: FilterOptions
}

export function useDataFetch({ page, limit, filters }: FetchOptions) {
  const [data, setData] = useState<TableData[]>([])
  const [loading, setLoading] = useState(true)
  const [totalPages, setTotalPages] = useState(1)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)

    async function fetchData() {
      try {
        // Build query parameters
        const params = new URLSearchParams()
        params.append("page", page.toString())
        params.append("limit", limit.toString())

        // Add filters to query params
        if (filters.componentId) params.append("component_id", filters.componentId)
        if (filters.componentType) params.append("component_type", filters.componentType)
        if (filters.componentType) params.append("component_type", filters.componentType)
        if (filters.action) params.append("action", filters.action)
        if (filters.timeStart) params.append("time_start", filters.timeStart)
        if (filters.timeEnd) params.append("time_end", filters.timeEnd)
        if (filters.specificTime) params.append("specific_time", filters.specificTime)
        if (filters.pdvKey) params.append("pdv_key", filters.pdvKey)
        if (filters.pdvValue) params.append("pdv_value", filters.pdvValue)

        // In a real app, you would fetch from your API
        // const response = await fetch(`/api/data?${params.toString()}`)
        // if (!response.ok) throw new Error(`API error: ${response.status}`)
        // const result = await response.json()

        // For demo purposes, we'll simulate API response with mock data
        const result = await mockFetchData(page, limit, filters)

        if (isMounted) {
          setData(result.data)
          setTotalPages(result.totalPages)
          setLoading(false)
        }
      } catch (error) {
        console.error("Error fetching data:", error)
        if (isMounted) {
          setError(error instanceof Error ? error.message : "Failed to fetch data")
          setData([])
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      isMounted = false
    }
  }, [page, limit, filters])

  return { data, loading, error, totalPages }
}

// Mock data function - replace with actual API call in production
async function mockFetchData(page: number, limit: number, filters: FilterOptions) {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 800))

  // Generate mock data
  const mockData: TableData[] = Array.from({ length: limit }, (_, i) => ({
    time: Date.now() - i * 3600000,
    component_id: `comp-${i + (page - 1) * limit}`,
    component_type: ["Button", "Form", "Table", "Modal", "Card"][Math.floor(Math.random() * 5)],
    action: ["Click", "Submit", "Load", "Close", "Update"][Math.floor(Math.random() * 5)],
    values: {
      value1: `Value ${i}`,
      value2: Math.random() * 100,
      nested: {
        prop1: "test",
        prop2: true,
      },
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
        session: "sess456",
      },
      performance: {
        loadTime: Math.random() * 1000,
        renderTime: Math.random() * 500,
      },
    },
  }))

  // Apply filters (simplified for demo)
  let filteredData = mockData

  if (filters.componentId) {
    filteredData = filteredData.filter((item) =>
      item.component_id.toLowerCase().includes(filters.componentId!.toLowerCase()),
    )
  }

  if (filters.componentType) {
    filteredData = filteredData.filter((item) =>
      item.component_type.toLowerCase().includes(filters.componentType!.toLowerCase()),
    )
  }

  if (filters.action) {
    filteredData = filteredData.filter((item) => item.action.toLowerCase().includes(filters.action!.toLowerCase()))
  }

  // In a real implementation, you would handle time range and PDV filters on the server
  // This is a simplified example for demonstration

  // Simulate occasional empty results for testing
  if (Math.random() < 0.1 && filters.specificTime) {
    return {
      data: [],
      totalPages: 0,
    }
  }

  return {
    data: filteredData,
    totalPages: 10, // Mock total pages
  }
}
