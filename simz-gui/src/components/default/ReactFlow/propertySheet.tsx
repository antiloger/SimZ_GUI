import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { SimPropertyWindowStore } from "@/states/simDataState"
import { CompDataI } from "@/types/component"
import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import PropteryForms from "./propertyFrom"



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
      <SheetContent className=" my-2 rounded-lg w-[70vw] sm:max-w-full" >
        <SheetHeader>
          <SheetDescription>{content?.typeName ?? "No content"}</SheetDescription>
          <SheetTitle className="text-2xl" >{content?.compName ?? "No content"}</SheetTitle>
        </SheetHeader>
        <div className="mt-5 grid">
          <Separator />
          <PropteryForms />
        </div>
      </SheetContent>
    </Sheet>
  )
}

