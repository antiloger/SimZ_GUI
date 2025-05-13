import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

export interface RunList {
  id: string
  name: string
}

interface AnalyticNavComboProps {
  runList: RunList[]
  selectedRunId: string
  setSelectedRunId: (id: string) => void
  open: boolean
  setOpen: (open: boolean) => void
  placeholder?: string
  width?: string
  emptyMessage?: string
  searchPlaceholder?: string
}

export function AnalyticNavCombo({
  runList,
  selectedRunId,
  setSelectedRunId,
  open,
  setOpen,
  placeholder = "Select a run",
  width = "w-[200px]",
  emptyMessage = "No runs found.",
  searchPlaceholder = "Search runs...",
}: AnalyticNavComboProps) {
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" role="combobox" aria-expanded={open} className={`${width} justify-between`}>
          {selectedRunId ? runList.find((run) => run.id === selectedRunId)?.name : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className={`${width} p-0`}>
        <Command>
          <CommandInput placeholder={searchPlaceholder} className="h-9" />
          <CommandList>
            <CommandEmpty>{emptyMessage}</CommandEmpty>
            <CommandGroup>
              {runList.map((run) => (
                <CommandItem
                  key={run.id}
                  value={run.id}
                  onSelect={(currentValue) => {
                    setSelectedRunId(currentValue === selectedRunId ? "" : currentValue)
                    setOpen(false)
                  }}
                >
                  {run.name}
                  <Check className={cn("ml-auto", selectedRunId === run.id ? "opacity-100" : "opacity-0")} />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
