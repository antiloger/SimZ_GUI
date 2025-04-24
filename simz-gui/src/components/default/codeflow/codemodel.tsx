import { CodeXml, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import ReactCodeMirror from "@uiw/react-codemirror"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useState } from "react"
import { pythonLanguage } from "@codemirror/lang-python"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface CodeEditorModelProps {
  componentId: string
}

// Initial code templates for each file
const initialFileContents = {
  "run.py": `
# u must return input if not the resource process not gonna work
def main():
    print("Running main application")
    
if __name__ == "__main__":
    main()`,
  "generate.py": `def generate_data():
    print("Generating data...")
    return {"status": "success"}`,
  "model.py": `class Model:
    def __init__(self):
        self.name = "Default Model"
        
    def train(self, data):
        print(f"Training {self.name} with data")
        
    def predict(self, input_data):
        return "Prediction result"`,
  "internal.py": `# Internal utility functions

def process_data(data):
    print("Processing data internally")
    return data`,
}

const fileList = ["run.py", "generate.py", "model.py", "internal.py"]

export function CodeEditorModel({ componentId }: CodeEditorModelProps) {
  // State to store code for each file
  const [fileContents, setFileContents] = useState<Record<string, string>>(initialFileContents)
  // Currently selected file
  const [currentFile, setCurrentFile] = useState<string>("run.py")

  if (componentId === "") {
    return <div>No component selected</div>
  }

  // Handle code change
  const handleCodeChange = (value: string) => {
    setFileContents((prev) => ({
      ...prev,
      [currentFile]: value,
    }))
  }

  // Handle save
  const handleSave = () => {
    // In a real application, you might want to save to a backend or localStorage
  }

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
          <Tabs value={currentFile} onValueChange={setCurrentFile}>
            <TabsList>
              {fileList.map((file) => (
                <TabsTrigger key={file} value={file}>
                  {file}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          <Button onClick={handleSave} variant="outline" size="sm">
            <Save className="h-4 w-4 mr-2" />
            Save
          </Button>
        </div>

        <ScrollArea className="flex-grow h-[calc(100vh-12rem)]">
          <ReactCodeMirror
            height="calc(100vh - 12rem)"
            value={fileContents[currentFile]}
            onChange={handleCodeChange}
            extensions={[pythonLanguage]}
          />
        </ScrollArea>
        {/**/}
        {/* <DialogFooter className="mt-4"> */}
        {/*   <DialogClose asChild> */}
        {/*     <Button type="button" variant="secondary"> */}
        {/*       Close */}
        {/*     </Button> */}
        {/*   </DialogClose> */}
        {/* </DialogFooter> */}
      </DialogContent>
    </Dialog>
  )
}
