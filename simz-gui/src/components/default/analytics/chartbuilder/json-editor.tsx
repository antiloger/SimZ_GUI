"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

interface JsonEditorProps {
  initialValue: string
  onSave: (value: any) => void
}

export function JsonEditor({ initialValue, onSave }: JsonEditorProps) {
  const [value, setValue] = useState(initialValue)
  const [error, setError] = useState("")

  const handleSave = () => {
    try {
      const parsedValue = JSON.parse(value)
      onSave(parsedValue)
      setError("")
    } catch (e) {
      setError("Invalid JSON format. Please check your input.")
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Widget Configuration</CardTitle>
      </CardHeader>
      <CardContent>
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="min-h-[200px] font-mono text-sm"
        />
        {error && <p className="text-destructive text-sm mt-2">{error}</p>}
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave}>Save Configuration</Button>
      </CardFooter>
    </Card>
  )
}
