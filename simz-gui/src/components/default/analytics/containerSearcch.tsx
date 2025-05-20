import { useState } from "react"
import { Search, Clock, Database, Cpu, Activity, ChevronDown, ChevronUp } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { useSocketStore } from "@/utils/socketIo"

// Define the type for container data
interface ContainerType {
  typeName: string;
  genComponentId: string;
  attributes: {
    [key: string]: {
      type: string;
      value: number | string;
    }
  }
}

interface ContainerAction {
  action: string;
  timestamp: number;
  attributes: {
    [key: string]: {
      [key: string]: number | string;
    }
  };
  values: {
    [key: string]: number | string;
  }
}

interface ComponentWorkflow {
  component_id: string;
  component_type: string;
  actions: ContainerAction[];
}

interface ContainerData {
  container_id: string;
  start_time: number;
  end_time: number;
  total_processing_time: number;
  attributes: {
    [key: string]: {
      [key: string]: number | string;
    }
  };
  types: {
    [key: string]: ContainerType;
  };
  combined_workflow: ComponentWorkflow[];
}

interface ContainerDataProps {
  projcetName: string;
  runId: string;
  componentId?: string; // Optional componentId for filtering
}

export default function ContainerDataViewer({ projcetName, runId, componentId }: ContainerDataProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [data, setData] = useState<ContainerData | null>(null)
  const [isSearched, setIsSearched] = useState(false)
  const [expandedRow, setExpandedRow] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [componentNames, setComponentNames] = useState<{[key: string]: string}>({})

  const { check_socket_endpoint } = useSocketStore()

  const toggleRow = (componentId: string) => {
    if (expandedRow === componentId) {
      setExpandedRow(null)
    } else {
      setExpandedRow(componentId)
    }
  }

  // Helper function to get unique action names for a component
  const getUniqueActionNames = (component: ComponentWorkflow) => {
    return [...new Set(component.actions.map((action) => action.action))]
  }

  // Function to fetch component names
  const fetchComponentNames = async () => {
    try {
      const namesData = await check_socket_endpoint("get_component_names", {
        project_name: projcetName,
        run_id: runId,
      })
      setComponentNames(namesData || {})
    } catch (error) {
      console.error("Error fetching component names:", error)
    }
  }

  const getData = async () => {
    if (searchQuery) {
      setIsLoading(true)
      setIsSearched(true)
      try {
        // Fetch container data
        const result = await check_socket_endpoint("get_container_data", {
          "project_name": projcetName,
          "run_id": runId,
          "container_id": searchQuery
        })
        setData(result)

        // Fetch component names
        await fetchComponentNames()
      } catch (error) {
        console.error("Error fetching container data:", error)
        setData(null)
      } finally {
        setIsLoading(false)
      }
    }
  }


  return (
    <div className="container mx-auto py-8 px-4">

      {/* Search Bar */}
      <div className="flex flex-row gap-4 mb-8">
        <Input
          type="text"
          placeholder="Search by container ID..."
          className=""
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <Button onClick={getData} disabled={isLoading || !searchQuery}>
          {isLoading ? "Searching..." : "Search"}
        </Button>
      </div>

      {isLoading ? (
        <div className="text-center py-12 border rounded-lg">
          <h2 className="text-xl font-medium">Loading...</h2>
          <p className="text-muted-foreground mt-2">Searching for container data</p>
        </div>
      ) : !isSearched ? (
        <div className="text-center py-12 border rounded-lg">
          <h2 className="text-xl font-medium">Enter a container ID to search</h2>
          <p className="text-muted-foreground mt-2">Enter a container ID in the search box above and click Search</p>
        </div>
      ) : data ? (
        <div className="space-y-8">
          {/* Container Details Card */}
          <Card>
            <CardHeader className="bg-muted/50">
              <CardTitle className="text-xl flex items-center gap-2">
                <Database className="h-5 w-5" /> Container Details
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">Container ID</p>
                    <p className="font-mono text-lg">{data.container_id}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">Start Time</p>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <p className="text-lg">{data.start_time}</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">End Time</p>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <p className="text-lg">{data.end_time}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">Total Processing Time</p>
                    <div className="flex items-center gap-2">
                      <Activity className="h-4 w-4 text-muted-foreground" />
                      <p className="text-lg">{data.total_processing_time}</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Types and Attributes Card */}
          <Card>
            <CardHeader className="bg-muted/50">
              <CardTitle className="text-xl flex items-center gap-2">
                <Cpu className="h-5 w-5" /> Types and Attributes
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {Object.entries(data.types).map(([typeId, typeInfo]) => (
                <div key={typeId} className="mb-4 p-6 border rounded-lg">
                  <div className="flex items-center gap-2 mb-4">
                    <h3 className="text-xl font-bold">{typeInfo.typeName}</h3>
                    <Badge variant="outline" className="font-mono text-xs">
                      ID: {typeId.substring(0, 8)}...
                    </Badge>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Generated by component</p>
                    <p className="font-mono bg-muted p-2 rounded">{typeInfo.genComponentId}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">Attributes</p>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(typeInfo.attributes).map(([attrName, attrInfo]) => (
                        <div key={attrName} className="border rounded p-4">
                          <p className="text-sm font-medium mb-1">{attrName}</p>
                          <div className="flex justify-between items-center">
                            <span className="text-lg font-bold">{attrInfo.value}</span>
                            <Badge variant="secondary" className="text-xs">
                              {attrInfo.type}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Components Table Card */}
          <Card>
            <CardHeader className="bg-muted/50">
              <CardTitle className="text-xl flex items-center gap-2">
                <Cpu className="h-5 w-5" /> Components
                {componentId && (
                  <Badge variant="outline" className="ml-2">
                    Filtered by component: {componentNames[componentId] || componentId.substring(0, 8) + '...'}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="border rounded-md">
                {/* Table Header */}
                <div className="grid grid-cols-12 gap-4 p-4 bg-muted/50 font-medium">
                  <div className="col-span-5">Component Name & ID</div>
                  <div className="col-span-2">Type</div>
                  <div className="col-span-4">Actions</div>
                  <div className="col-span-1 text-right">Details</div>
                </div>

                {/* Filter components based on componentId if provided */}
                {(() => {
                  const filteredWorkflow = componentId
                    ? data.combined_workflow.filter(comp => comp.component_id === componentId)
                    : data.combined_workflow;

                  if (filteredWorkflow.length === 0) {
                    return (
                      <div className="p-8 text-center text-muted-foreground">
                        {componentId
                          ? `No components found matching ID: ${componentId}`
                          : "No components found in this container"}
                      </div>
                    );
                  }

                  return filteredWorkflow.map((component: ComponentWorkflow) => (
                    <div key={String(component.component_id)} className="border-t">
                      {/* Main Row */}
                      <div className="grid grid-cols-12 gap-4 p-4 items-center">
                        <div className="col-span-5">
                          {componentNames[component.component_id] ? (
                            <>
                              <span className="font-medium">{componentNames[component.component_id]}</span>
                              <span className="text-xs text-muted-foreground ml-1 font-mono">
                                ({component.component_id.substring(0, 8)}...)
                              </span>
                            </>
                          ) : (
                            <span className="font-mono">{component.component_id}</span>
                          )}
                        </div>
                        <div className="col-span-2">
                          <Badge variant={component.component_type === "generator" ? "default" : "secondary"}>
                            {component.component_type}
                          </Badge>
                        </div>
                        <div className="col-span-4">
                          <div className="flex flex-wrap gap-1">
                            {getUniqueActionNames(component).map((action, idx) => (
                              <Badge key={idx} variant="outline">
                                {String(action)}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div className="col-span-1 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleRow(component.component_id)}
                            className="h-8 w-8 p-0"
                          >
                            {expandedRow === component.component_id ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <ChevronDown className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>

                    {/* Expanded Content */}
                    {expandedRow === component.component_id && (
                      <div className="border-t bg-muted/20 p-4">
                        <Tabs defaultValue="timeline" className="w-full">
                          <TabsList className="grid w-full grid-cols-2 mb-4">
                            <TabsTrigger value="timeline">Timeline</TabsTrigger>
                            <TabsTrigger value="actions">Actions</TabsTrigger>
                          </TabsList>

                          <TabsContent value="timeline">
                            <div className="space-y-4">
                              <h4 className="font-medium">Action Timeline</h4>
                              <div className="grid gap-3">
                                {component.actions.map((action: ContainerAction, index: number) => (
                                  <div
                                    key={index}
                                    className="flex items-start gap-3 p-3 border rounded-md bg-background"
                                  >
                                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-medium">
                                      {index + 1}
                                    </div>
                                    <div className="flex-1">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium">{action.action}</span>
                                        <span className="text-sm text-muted-foreground">
                                          Timestamp: {action.timestamp}
                                        </span>
                                      </div>

                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                                        <div>
                                          <h5 className="text-sm font-medium mb-2">Values</h5>
                                          <div className="bg-muted/30 p-3 rounded-md">
                                            {Object.entries(action.values).map(([key, value]) => (
                                              <div key={key} className="flex justify-between mb-1">
                                                <span className="text-sm text-muted-foreground">{key}:</span>
                                                <span className="text-sm font-medium">{String(value)}</span>
                                              </div>
                                            ))}
                                          </div>
                                        </div>

                                        <div>
                                          <h5 className="text-sm font-medium mb-2">Attributes</h5>
                                          <div className="bg-muted/30 p-3 rounded-md">
                                            {Object.entries(action.attributes).map(([attrName, attrValue]) => (
                                              <div key={attrName} className="mb-2">
                                                <div className="flex justify-between mb-1">
                                                  <span className="text-sm font-medium">{attrName}</span>
                                                </div>
                                                {Object.entries(attrValue as Record<string, unknown>).map(([key, value]) => (
                                                  <div key={key} className="flex justify-between pl-2 mb-1">
                                                    <span className="text-sm text-muted-foreground">{key}:</span>
                                                    <span className="text-sm">{String(value)}</span>
                                                  </div>
                                                ))}
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </TabsContent>

                          <TabsContent value="actions">
                            <div className="space-y-6">
                              {getUniqueActionNames(component).map((actionName) => {
                                const actionInstances = component.actions.filter(
                                  (action: ContainerAction) => action.action === actionName,
                                )

                                return (
                                  <div key={String(actionName)} className="space-y-3">
                                    <div className="flex items-center gap-2">
                                      <h4 className="font-medium">{String(actionName)}</h4>
                                      <Badge variant="outline" className="text-xs">
                                        {actionInstances.length} occurrence{actionInstances.length !== 1 ? "s" : ""}
                                      </Badge>
                                    </div>

                                    <div className="grid gap-4">
                                      {actionInstances.map((action: ContainerAction, index: number) => (
                                        <div key={index} className="border rounded-md overflow-hidden">
                                          <div className="bg-muted/30 p-3 flex justify-between items-center">
                                            <span className="font-medium">Occurrence {index + 1}</span>
                                            <span className="text-sm text-muted-foreground">
                                              Timestamp: {action.timestamp}
                                            </span>
                                          </div>

                                          <div className="p-4">
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                              <div>
                                                <h5 className="text-sm font-medium mb-2">Values</h5>
                                                <div className="bg-muted/20 p-3 rounded-md">
                                                  {Object.entries(action.values).map(([key, value]) => (
                                                    <div key={key} className="flex justify-between mb-1">
                                                      <span className="text-sm text-muted-foreground">{key}:</span>
                                                      <span className="text-sm font-medium">{String(value)}</span>
                                                    </div>
                                                  ))}
                                                </div>
                                              </div>

                                              <div>
                                                <h5 className="text-sm font-medium mb-2">Attributes</h5>
                                                <div className="bg-muted/20 p-3 rounded-md">
                                                  {Object.entries(action.attributes).map(([attrName, attrValue]) => (
                                                    <div key={attrName} className="mb-2">
                                                      <div className="flex justify-between mb-1">
                                                        <span className="text-sm font-medium">{attrName}</span>
                                                      </div>
                                                      {Object.entries(attrValue as Record<string, unknown>).map(([key, value]) => (
                                                        <div key={key} className="flex justify-between pl-2 mb-1">
                                                          <span className="text-sm text-muted-foreground">{key}:</span>
                                                          <span className="text-sm">{String(value)}</span>
                                                        </div>
                                                      ))}
                                                    </div>
                                                  ))}
                                                </div>
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )
                              })}
                            </div>
                          </TabsContent>
                        </Tabs>
                      </div>
                    )}
                  </div>
                ))
              })()}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="text-center py-12 border rounded-lg">
          <h2 className="text-xl font-medium">No container found with ID: {searchQuery}</h2>
          <p className="text-muted-foreground mt-2">Try searching with a different container ID</p>
        </div>
      )}
    </div>
  )
}
