import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { SimPropertyWindowStore } from "@/states/simDataState"
import { CompDataI } from "@/types/component"
import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import DefaultInfoForm from "../formBuilder/defaultInfoForm"
import PropertyBuilderFrom from "../formBuilder/dynPropertyForm"
import { Button } from "@/components/ui/button"
import { Info } from "lucide-react"
import ConnectorForm from "../connectors/connectorForm"
import { ScrollArea } from "@/components/ui/scroll-area"
import { AddTypesGen, TimeStepGenForm } from "../formBuilder/GenConfigForms"



export default function PropertySheet() {
  const { isPropertyWindowOn, setPropertyWindowOn, propertyWindowData } = SimPropertyWindowStore()
  const [content, setContent] = useState<CompDataI | null>(null)

  useEffect(() => {
    if (propertyWindowData) {
      // Simulating an API call or data fetching
      // Replace this with your actual data fetching logic
      const fetchData = async () => {
        try {
          // Simulated API call

          setContent(propertyWindowData)
        } catch (error) {
          console.error("Error fetching data:", error)
        }
      }

      fetchData()
    } else {
      setContent(null)
    }
  }, [propertyWindowData])

  const handleSheetOpenChange = (open: boolean) => {
    setPropertyWindowOn(open)
    // if (!open) {
    //   setContent(null)
    // }
  }

  const ContentGen = () => {
    if (content?.category === "generator") {
      return (
        <>
          <div>
            <AddTypesGen compId={content.id} />
          </div>
          <div>
            <h1 className="font-semibold text-lg text-primary pb-2" >Inputs</h1>
            <TimeStepGenForm />
          </div>
        </>
      )
    } else {
      return (
        <>
          <div>
            <h1 className="font-semibold text-lg text-primary pb-2" >Inputs</h1>
            <PropertyBuilderFrom category={content?.category ?? null} compType={content?.typeName ?? null} id={content?.id ?? null} />
          </div>
          <div>
            <ConnectorForm comId={content?.id ?? ""} />
          </div>
          <div>
            <ConnectorForm comId={content?.id ?? ""} />
          </div>
        </>
      )
    }
  }

  return (
    <Sheet open={isPropertyWindowOn} onOpenChange={handleSheetOpenChange}>
      <SheetContent className=" w-[70vw] sm:max-w-full" >
        <SheetHeader>
          <SheetDescription>{content?.typeName ?? "No content"}</SheetDescription>
          <SheetTitle className="text-2xl items-center justify-center " style={{ color: content?.color ?? "black" }}>
            {content?.compName ?? "No content"}
            {/* TODO: add description view  */}
            <Button variant="ghost" size="icon" > <Info /> </Button>
          </SheetTitle>
        </SheetHeader>
        <Separator className="mt-2" />
        <ScrollArea className="flex-grow  h-[calc(100vh-120px)]">
          <div className="mt-5 grid gap-y-4">
            <div>
              <h1 className="font-semibold text-lg text-primary pb-2" >Default Config</h1>
              <DefaultInfoForm compId={propertyWindowData?.id ?? ""} />
            </div>
            <ContentGen />
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  )
}

