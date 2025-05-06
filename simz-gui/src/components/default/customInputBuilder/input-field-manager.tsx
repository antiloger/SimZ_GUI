"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AddFieldForm } from "./add-field-form"
import { FieldsTable } from "./fields-table"

export function InputFieldManager() {
  return (
    <Tabs defaultValue="fields" className="w-full">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="fields">Fields</TabsTrigger>
        <TabsTrigger value="add">Add Field</TabsTrigger>
      </TabsList>
      <TabsContent value="fields">
        <FieldsTable />
      </TabsContent>
      <TabsContent value="add">
        <AddFieldForm />
      </TabsContent>
    </Tabs>
  )
}
