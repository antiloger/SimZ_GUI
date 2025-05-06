"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Search, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const searchFormSchema = z.object({
  componentId: z.string().optional(),
  componentType: z.string().optional(),
  action: z.string().optional(),
  timeSearchType: z.enum(["range", "specific"]).default("specific"),
  // Time range fields
  startTimeValue: z.string().optional(),
  endTimeValue: z.string().optional(),
  // Specific time field
  specificTimeValue: z.string().optional(),
  // Time unit for all time values
  timeUnit: z.string().default("seconds"),
  pdvKey: z.string().optional(),
  pdvValue: z.string().optional(),
})

type SearchFormValues = z.infer<typeof searchFormSchema>

interface SearchFormProps {
  onSearch: (searchData: SearchFormValues) => void
  onReset: () => void
}

export function SearchForm({ onSearch, onReset }: SearchFormProps) {
  const [advancedOpen, setAdvancedOpen] = useState(false)

  // Initialize form with default values
  const form = useForm<SearchFormValues>({
    resolver: zodResolver(searchFormSchema),
    defaultValues: {
      componentId: "",
      componentType: "",
      action: "",
      timeSearchType: "specific",
      startTimeValue: "",
      endTimeValue: "",
      specificTimeValue: "",
      timeUnit: "seconds",
      pdvKey: "",
      pdvValue: "",
    },
  })

  const timeSearchType = form.watch("timeSearchType")

  function onSubmit(data: SearchFormValues) {
    // Send search data to parent component
    onSearch(data)
  }

  function resetSearch() {
    form.reset({
      componentId: "",
      componentType: "",
      action: "",
      timeSearchType: "specific",
      startTimeValue: "",
      endTimeValue: "",
      specificTimeValue: "",
      timeUnit: "seconds",
      pdvKey: "",
      pdvValue: "",
    })

    // Notify parent component about reset
    onReset()
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          <FormField
            control={form.control}
            name="componentId"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormLabel>Component ID</FormLabel>
                <FormControl>
                  <Input placeholder="Search by component ID..." {...field} />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="componentType"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormLabel>Component Type</FormLabel>
                <FormControl>
                  <Input placeholder="Search by component type..." {...field} />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="action"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormLabel>Action</FormLabel>
                <FormControl>
                  <Input placeholder="Search by action..." {...field} />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <Accordion
          type="single"
          collapsible
          value={advancedOpen ? "advanced" : ""}
          onValueChange={(value) => setAdvancedOpen(value === "advanced")}
        >
          <AccordionItem value="advanced">
            <AccordionTrigger>Advanced Search Options</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-6 pt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="timeUnit"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Time Unit</FormLabel>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select unit" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="hours">Hours</SelectItem>
                              <SelectItem value="minutes">Minutes</SelectItem>
                              <SelectItem value="seconds">Seconds</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="timeSearchType"
                  render={({ field }) => (
                    <FormItem className="space-y-3">
                      <FormLabel>Time Search Type</FormLabel>
                      <FormControl>
                        <RadioGroup
                          onValueChange={field.onChange}
                          defaultValue={field.value}
                          className="flex flex-row space-x-4"
                        >
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="range" id="range" />
                            <span className="text-sm font-medium">Time Range</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="specific" id="specific" />
                            <span className="text-sm font-medium">Specific Time</span>
                          </div>
                        </RadioGroup>
                      </FormControl>
                    </FormItem>
                  )}
                />

                {timeSearchType === "range" ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="startTimeValue"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Start Time</FormLabel>
                          <FormControl>
                            <Input type="number" placeholder="Enter value..." {...field} />
                          </FormControl>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="endTimeValue"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>End Time</FormLabel>
                          <FormControl>
                            <Input type="number" placeholder="Enter value..." {...field} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                  </div>
                ) : (
                  <FormField
                    control={form.control}
                    name="specificTimeValue"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Specific Time</FormLabel>
                        <FormControl>
                          <Input type="number" placeholder="Enter value..." {...field} />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="pdvKey"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>PDV Key</FormLabel>
                        <FormControl>
                          <Input placeholder="Search by PDV key..." {...field} />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="pdvValue"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>PDV Value</FormLabel>
                        <FormControl>
                          <Input placeholder="Search by PDV value..." {...field} />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <div className="flex justify-between">
          <Button type="button" variant="outline" onClick={resetSearch} className="gap-2">
            <X className="h-4 w-4" />
            Clear
          </Button>
          <Button type="submit" className="gap-2">
            <Search className="h-4 w-4" />
            Search
          </Button>
        </div>
      </form>
    </Form>
  )
}
