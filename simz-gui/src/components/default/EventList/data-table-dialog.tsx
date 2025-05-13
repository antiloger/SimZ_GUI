
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface DataTableDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  data: any | null
}

export function DataTableDialog({ open, onOpenChange, data }: DataTableDialogProps) {
  if (!data) return null

  // Format JSON data for display
  const formatJsonData = (data: any) => {
    if (typeof data === "object" && data !== null) {
      return JSON.stringify(data, null, 2)
    }
    return String(data)
  }

  // Extract container ID from PDV if available
  const containerId = data.PDV && data.PDV.containerId ? data.PDV.containerId : "N/A"

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[900px] lg:max-w-[1000px] max-h-[90vh] p-0">
        <div className="max-h-[90vh] overflow-auto">
          <div className="sticky top-0 z-10 bg-background p-6 pb-2 border-b flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold">Record Details</h2>
              <div className="flex flex-wrap gap-2 mt-3">
                <Badge variant="outline" className="bg-primary/10 text-sm px-3 py-1">
                  Time: {data.time}
                </Badge>
                <Badge variant="outline" className="bg-primary/10 text-sm px-3 py-1">
                  Type: {data.component_type}
                </Badge>
                <Badge variant="outline" className="bg-primary/10 text-sm px-3 py-1">
                  Action: {data.action}
                </Badge>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => onOpenChange(false)}>
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </Button>
          </div>

          <Tabs defaultValue="overview" className="w-full">
            <div className="px-6 pt-4">
              <TabsList className="grid grid-cols-3 mb-4 w-full">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="values">Values</TabsTrigger>
                <TabsTrigger value="pdv">PDV & Addition</TabsTrigger>
              </TabsList>
            </div>

            <div className="px-6 pb-6">
              <TabsContent value="overview" className="mt-0">
                <Card className="border-2">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xl">Basic Information</CardTitle>
                    <CardDescription>Essential details about this record</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="text-sm font-medium text-muted-foreground mb-1">Time</h3>
                        <p className="text-xl">{data.time}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-muted-foreground mb-1">Component Type</h3>
                        <p className="text-xl">{data.component_type}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-muted-foreground mb-1">Component ID</h3>
                        <p className="text-sm break-all font-mono bg-muted p-3 rounded-md">{data.component_id}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-muted-foreground mb-1">Action</h3>
                        <p className="text-xl">{data.action}</p>
                      </div>
                      <div className="md:col-span-2">
                        <h3 className="text-sm font-medium text-muted-foreground mb-1">Container ID</h3>
                        <p className="text-sm break-all font-mono bg-muted p-3 rounded-md">{containerId}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="values" className="mt-0">
                <Card className="border-2">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xl">Values</CardTitle>
                    <CardDescription>Detailed values for this record</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[400px] rounded-md border-2 p-4 bg-muted/50 overflow-auto">
                      <pre className="text-sm whitespace-pre-wrap break-all font-mono">
                        {formatJsonData(data.values)}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="pdv" className="mt-0">
                <div className="space-y-6">
                  <Card className="border-2">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xl">PDV (Process Data Variables)</CardTitle>
                      <CardDescription>Process data variables for this record</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[300px] rounded-md border-2 p-4 bg-muted/50 overflow-auto">
                        <pre className="text-sm whitespace-pre-wrap break-all font-mono">
                          {formatJsonData(data.PDV)}
                        </pre>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-2">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xl">Addition</CardTitle>
                      <CardDescription>Additional data for this record</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[300px] rounded-md border-2 p-4 bg-muted/50 overflow-auto">
                        <pre className="text-sm whitespace-pre-wrap break-all font-mono">
                          {formatJsonData(data.addition)}
                        </pre>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  )
}
