import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"

interface TableData {
  time: number
  component_id: string
  component_type: string
  action: string
  values: { [key: string]: any }
  PDV: { [key: string]: { [key: string]: any } }
  addition: { [key: string]: any }
}

interface DataDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  data: TableData | null
}

export function DataDialog({ open, onOpenChange, data }: DataDialogProps) {
  if (!data) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Data Details</DialogTitle>
          <DialogDescription>Complete information for the selected record</DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[60vh] pr-4">
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <h3 className="text-sm font-medium text-muted-foreground">Time</h3>
                <p>{data.time}</p>
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-medium text-muted-foreground">Component ID</h3>
                <p>{data.component_id}</p>
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-medium text-muted-foreground">Component Type</h3>
                <p>{data.component_type}</p>
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-medium text-muted-foreground">Action</h3>
                <p>{data.action}</p>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium">Values</h3>
              <div className="rounded-md bg-muted p-4">
                <pre className="text-xs overflow-auto whitespace-pre-wrap">{JSON.stringify(data.values, null, 2)}</pre>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium">PDV (Property-Dependent Values)</h3>
              <div className="rounded-md bg-muted p-4">
                <pre className="text-xs overflow-auto whitespace-pre-wrap">{JSON.stringify(data.PDV, null, 2)}</pre>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium">Additional Information</h3>
              <div className="rounded-md bg-muted p-4">
                <pre className="text-xs overflow-auto whitespace-pre-wrap">
                  {JSON.stringify(data.addition, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
