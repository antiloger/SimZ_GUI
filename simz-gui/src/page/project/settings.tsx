import { useEffect, useState } from "react"
import { AlertCircle, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { SimDataState } from "@/states/simDataState"
import { useSocketStore } from "@/utils/socketIo"

// This would typically come from props or context in a real application

interface Run {
  name: string
}

interface ProjectData {
  name: string
  created_at: string
  description: string
  version: string
  components: any[]
  runs: Run[]
}

export default function SettingsPage() {
  const [projectData, setProjectData] = useState<ProjectData>()
  const [runs, setRuns] = useState<string[]>()
  const [isDeleteRunDialogOpen, setIsDeleteRunDialogOpen] = useState(false)
  const [isDeleteProjectDialogOpen, setIsDeleteProjectDialogOpen] = useState(false)
  const [runToDelete, setRunToDelete] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [projectNameConfirmation, setProjectNameConfirmation] = useState("")

  const { projectName } = SimDataState()
  const { check_socket_endpoint } = useSocketStore()

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    } catch (error) {
      return dateString
    }
  }

  const fetchProjectData = async () => {
    try {

      const data = await check_socket_endpoint("project_config", { "project_name": projectName })
      setProjectData(data)
      setRuns(data.runs)
    } catch (error) {
      console.error("Error fetching project data:", error)
    }
  }

  useEffect(() => {
    console.log("Fetching project data...")
    fetchProjectData()
  }, [projectName, check_socket_endpoint])

  const handleDeleteRun = async (runId: string) => {
    setIsDeleting(true)
    try {
      // This would be an API call in a real application
      await check_socket_endpoint("delete_run", { "project_name": projectName, "run_id": runId })
    } catch (error) {
      console.error("Error deleting run:", error)
      // toast({
      //   variant: "destructive",
      //   title: "Error",
      //   description: "Failed to delete run. Please try again.",
      // })
    } finally {
      setIsDeleting(false)
      setIsDeleteRunDialogOpen(false)
      setRunToDelete(null)
    }
  }

  const handleDeleteProject = async () => {
    if (!projectData) return
    if (projectNameConfirmation !== projectData.name) {
      // toast({
      //   variant: "destructive",
      //   title: "Error",
      //   description: "Project name confirmation doesn't match. Please try again.",
      // })
      return
    }

    setIsDeleting(true)
    try {
      // This would be an API call in a real application
      await check_socket_endpoint("delete_project", { "project_name": projectName })
      // toast({
      //   title: "Project deleted",
      //   description: `Project ${projectData.project_name} has been deleted successfully.`,
      // })

    } catch (error) {
      console.error("Error deleting project:", error)
    } finally {
      setIsDeleting(false)
      setIsDeleteProjectDialogOpen(false)
      setProjectNameConfirmation("")
    }
  }

  const confirmDeleteRun = (runId: string) => {
    setRunToDelete(runId)
    setIsDeleteRunDialogOpen(true)
  }

  if (!projectData || !runs) {
    return (
      <div className="container mx-auto py-10">
        <h1 className="text-3xl font-bold">Loading...</h1>
        <p className="text-lg text-muted-foreground">Please wait while we load your project settings.</p>
      </div>
    )
  }

  return (
    <div className="m-10 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Project Settings</h1>
      </div>

      {/* Project Information */}
      <Card>
        <CardHeader>
          <CardTitle>Project Information</CardTitle>
          <CardDescription>View and manage your project details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Project Name</h3>
              <p className="text-lg font-medium">{projectData.name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Created At</h3>
              <p className="text-lg font-medium">{formatDate(projectData.created_at)}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Version</h3>
              <p className="text-lg font-medium">{projectData.version}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Description</h3>
              <p className="text-lg font-medium">{projectData.description || "No description"}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Runs Management */}
      <Card>
        <CardHeader>
          <CardTitle>Runs Management</CardTitle>
          <CardDescription>View and delete runs associated with this project</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border rounded-md">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Run ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-4">
                      No runs found
                    </TableCell>
                  </TableRow>
                ) : (
                  runs.map((run) => (
                    <TableRow key={run}>
                      <TableCell className="font-medium">{run}</TableCell>
                      <TableCell>{run}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="destructive" size="sm" onClick={() => confirmDeleteRun(run)}>
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200">
        <CardHeader className="text-red-500">
          <CardTitle>Danger Zone</CardTitle>
          <CardDescription className="text-red-400">Destructive actions that cannot be undone</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Warning</AlertTitle>
            <AlertDescription>
              Deleting a project will permanently remove all associated data, including runs, components, and settings.
              This action cannot be undone.
            </AlertDescription>
          </Alert>
        </CardContent>
        <CardFooter>
          <Button variant="destructive" onClick={() => setIsDeleteProjectDialogOpen(true)}>
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Project
          </Button>
        </CardFooter>
      </Card>

      {/* Delete Run Dialog */}
      <Dialog open={isDeleteRunDialogOpen} onOpenChange={setIsDeleteRunDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Run</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this run? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="font-medium">Run ID: {runToDelete}</p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteRunDialogOpen(false)} disabled={isDeleting}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => runToDelete && handleDeleteRun(runToDelete)}
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting..." : "Delete Run"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Project Dialog */}
      <Dialog open={isDeleteProjectDialogOpen} onOpenChange={setIsDeleteProjectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Project</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this project? This action cannot be undone and will permanently delete all
              associated data.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Warning</AlertTitle>
              <AlertDescription>
                You are about to delete project <span className="font-bold">{projectData.name}</span>. This will
                delete all runs, components, and settings associated with this project.
              </AlertDescription>
            </Alert>
            <div className="border rounded-md p-4">
              <p className="text-sm text-muted-foreground mb-2">To confirm, type the project name below:</p>
              <input
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder={projectData.name}
                value={projectNameConfirmation}
                onChange={(e) => setProjectNameConfirmation(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteProjectDialogOpen(false)} disabled={isDeleting}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteProject}
              disabled={isDeleting || projectNameConfirmation !== projectData.name}
            >
              {isDeleting ? "Deleting..." : "Delete Project"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
