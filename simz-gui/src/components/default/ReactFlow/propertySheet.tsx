import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { SimPropertyWindowStore } from "@/states/simDataState"
import { CompDataI } from "@/types/component"
import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import DefaultInfoForm from "../formBuilder/defaultInfoForm"
import PropertyBuilderFrom from "../formBuilder/dynPropertyForm"
import { Button } from "@/components/ui/button"
import { Info } from "lucide-react"



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
        <div className="mt-5 grid gap-y-4">
          <Separator className="mb-5" />
          <div>
            <h1 className="font-semibold text-lg text-primary pb-2" >Default Config</h1>
            <DefaultInfoForm compId={propertyWindowData?.id ?? ""} />
          </div>
          <div>
            <h1 className="font-semibold text-lg text-primary pb-2" >Inputs</h1>
            <PropertyBuilderFrom category={content?.category ?? null} compType={content?.typeName ?? null} id={content?.id ?? null} />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}

