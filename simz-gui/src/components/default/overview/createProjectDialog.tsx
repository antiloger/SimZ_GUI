import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useSocketStore } from "@/utils/socketIo"

interface ProjectDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  refresh: () => void;
}

export default function ProjectCreateDialog({ open, onOpenChange, refresh }: ProjectDialogProps) {
  const [projectName, setProjectName] = useState("")
  const [projectDescription, setProjectDescription] = useState("")
  const [loading, setLoading] = useState(false)
  const { create_new_project } = useSocketStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission here
    setLoading(true)
    console.log({ projectName, projectDescription })
    await create_new_project(projectName, projectDescription);
    refresh()
    setLoading(false)
    onOpenChange(false)
    // Reset form
    setProjectName("")
    setProjectDescription("")
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create Project</DialogTitle>
            <DialogDescription>
              Fill in the details for your new project. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="col-span-3"
                placeholder="My Awesome Project"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">
                Description
              </Label>
              <Textarea
                id="description"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                className="col-span-3"
                placeholder="Describe your project..."
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            {
              loading ? (
                <Button disabled> loading ... </Button>
              ) : (<Button type="submit">Save Project</Button>)
            }
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
