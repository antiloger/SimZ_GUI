"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

export type ComboboxItem = {
  value: string
  label: string
}

interface ComboboxProps {
  items: ComboboxItem[]
  placeholder?: string
  emptyMessage?: string
  searchPlaceholder?: string
  value?: string
  onValueChange?: (value: string) => void
  className?: string
  disabled?: boolean
}

export function Combobox({
  items,
  placeholder = "Select an item...",
  emptyMessage = "No items found.",
  searchPlaceholder = "Search...",
  value,
  onValueChange,
  className,
  disabled = false,
}: ComboboxProps) {
  const [open, setOpen] = React.useState(false)
  const [selectedValue, setSelectedValue] = React.useState(value || "")

  React.useEffect(() => {
    if (value !== undefined) {
      setSelectedValue(value)
    }
  }, [value])

  const handleSelect = React.useCallback(
    (currentValue: string) => {
      const newValue = currentValue === selectedValue ? "" : currentValue
      setSelectedValue(newValue)
      onValueChange?.(newValue)
      setOpen(false)
    },
    [selectedValue, onValueChange],
  )

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("w-full justify-between", className)}
          disabled={disabled}
        >
          {selectedValue ? items.find((item) => item.value === selectedValue)?.label || placeholder : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder={searchPlaceholder} />
          <CommandList>
            <CommandEmpty>{emptyMessage}</CommandEmpty>
            <CommandGroup>
              {items.map((item) => (
                <CommandItem key={item.value} value={item.value} onSelect={handleSelect}>
                  <Check className={cn("mr-2 h-4 w-4", selectedValue === item.value ? "opacity-100" : "opacity-0")} />
                  {item.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

