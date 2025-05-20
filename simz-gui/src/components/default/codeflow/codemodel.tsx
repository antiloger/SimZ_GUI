import { CodeXml, FileText, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import ReactCodeMirror from "@uiw/react-codemirror"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useEffect, useState } from "react"
import { pythonLanguage } from "@codemirror/lang-python"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SimDataState } from "@/states/simDataState"
import { RunnerFile } from "@/types/component"
import { initialRunnerFile } from "@/mockData/codemodel"

interface CodeEditorModelProps {
  componentId: string
}

// Initial code templates for each file type in the RunnerFile interface

// File keys for the tabs
const fileKeys: (keyof RunnerFile)[] = ["run", "generator", "model", "event"]

export function CodeEditorModel({ componentId }: CodeEditorModelProps) {
  // State to store code using the RunnerFile interface
  const [runnerFile, setRunnerFile] = useState<RunnerFile>(initialRunnerFile)
  // Currently selected file key
  const [currentFileKey, setCurrentFileKey] = useState<keyof RunnerFile>("run")
  const { saveRunnerStr, getRunnerStr } = SimDataState()

  useEffect(() => {
    if (componentId) {
      const existingCode = getRunnerStr(componentId)
      if (existingCode) {
        setRunnerFile(existingCode)
      } else {
        setRunnerFile(initialRunnerFile)
      }
    } else {
      setRunnerFile(initialRunnerFile)
    }
  }, [componentId, getRunnerStr])

  if (componentId === "") {
    return <div>No component selected</div>
  }

  // Handle code change
  const handleCodeChange = (value: string) => {
    setRunnerFile((prev) => ({
      ...prev,
      [currentFileKey]: value,
    }))
  }

  // Handle save
  const handleSave = () => {
    console.log("Saving code...")
    console.log(runnerFile)
    saveRunnerStr(componentId, runnerFile)
  }

  const navigateTodocs = () => {
    window.open('/docs/comp-func', '_blank');
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="default" className="w-full">
          <CodeXml className="mr-2" />
          Code In Editor
        </Button>
      </DialogTrigger>
      <DialogContent className="w-full max-w-full h-screen">
        <DialogHeader>
          <DialogTitle>Component Editor</DialogTitle>
        </DialogHeader>
        <Separator />

        <div className="flex items-center justify-between mt-2">
          <Tabs value={currentFileKey} onValueChange={(value) => setCurrentFileKey(value as keyof RunnerFile)}>
            <TabsList>
              {fileKeys.map((fileKey) => (
                <TabsTrigger key={fileKey} value={fileKey}>
                  {fileKey}.py
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
          <div className="flex items-center gap-2">
            <Button onClick={navigateTodocs} variant="outline" size="sm" >
              <FileText className="h-4 w-4 mr-2" />
              Documentation
            </Button>
            <Button onClick={handleSave} variant="outline" size="sm">
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
          </div>
        </div>

        <ScrollArea className="bg-primary-foreground flex-grow h-[calc(100vh-12rem)]">
          <ReactCodeMirror
            className="bg-primary-foreground"
            height="calc(100vh - 12rem)"
            value={runnerFile[currentFileKey]}
            onChange={handleCodeChange}
            extensions={[pythonLanguage]}
          />
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
