import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Plus, Trash2 } from "lucide-react";
import { GenAttributes, GenTypes } from "@/types/configGen";
import { Select, SelectContent, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SelectItem } from "@radix-ui/react-select";

const formSchema = z.object({
  intervalTime: z.number().nonnegative(),
  noItem: z.number().nonnegative(),
  isIntervalTimeRandom: z.boolean().default(false),
  intervalTimeRandomFrom: z.number().nonnegative().optional(),
  intervalTimeRandomTo: z.number().nonnegative().optional(),
  timePerNoItem: z.number().nonnegative(),
  isTimePerNoItemRandom: z.boolean().default(false),
  timePerNoItemRandomFrom: z.number().nonnegative().optional(),
  timePerNoItemRandomTo: z.number().nonnegative().optional(),
});

export function TimeStepGenForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      intervalTime: 0,
      noItem: 0,
      isIntervalTimeRandom: false,
      intervalTimeRandomFrom: 0,
      intervalTimeRandomTo: 0,
      timePerNoItem: 0,
      isTimePerNoItemRandom: false,
      timePerNoItemRandomFrom: 0,
      timePerNoItemRandomTo: 0,
    },
  });

  const watchIsIntervalTimeRandom = form.watch("isIntervalTimeRandom");
  const watchIsTimePerNoItemRandom = form.watch("isTimePerNoItemRandom");

  useEffect(() => {
    const subscription = form.watch((value, { name, type }) => {
      if (type === "change") {
        onSubmit(form.getValues());
      }
    });
    return () => subscription.unsubscribe();
  }, [form]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    // Debounce the console.log to avoid too frequent updates
    console.log(values);
  }

  return (
    <div className="mx-auto w-full">
      <Form {...form}>
        <form>
          <div className="overflow-hidden rounded-lg border border-border bg-background [&_tr:last-child]:border-b-0">
            <Table>
              <TableBody>
                <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                  <TableCell className="bg-muted/50 py-2 font-medium">
                    Interval Time
                  </TableCell>
                  <TableCell className="py-0 pr-0">
                    <FormField
                      control={form.control}
                      name="intervalTime"
                      render={({ field }) => (
                        <FormItem>
                          <FormControl>
                            <Input
                              type="number"
                              className="border-none p-0 shadow-none focus-visible:ring-0"
                              {...field}
                              onChange={(e) => {
                                const value =
                                  e.target.value === ""
                                    ? ""
                                    : Number(e.target.value);
                                field.onChange(value);
                              }}
                              onBlur={field.onBlur}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </TableCell>
                </TableRow>
                <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                  <TableCell className="bg-muted/50 py-2 font-medium">
                    Interval Time Random
                  </TableCell>
                  <TableCell className="py-2 px-3">
                    <FormField
                      control={form.control}
                      name="isIntervalTimeRandom"
                      render={({ field }) => (
                        <FormItem>
                          <FormControl>
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                checked={field.value}
                                onCheckedChange={(checked) => {
                                  field.onChange(checked);
                                  form.handleSubmit(onSubmit)();
                                }}
                              />
                            </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </TableCell>
                </TableRow>
                {watchIsIntervalTimeRandom && (
                  <>
                    <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                      <TableCell className="bg-muted/50 py-2 font-medium">
                        Interval Time From
                      </TableCell>
                      <TableCell className="py-0 pr-0">
                        <FormField
                          control={form.control}
                          name="intervalTimeRandomFrom"
                          render={({ field }) => (
                            <FormItem>
                              <FormControl>
                                <Input
                                  type="number"
                                  className="border-none p-0 shadow-none focus-visible:ring-0"
                                  {...field}
                                  onChange={(e) => {
                                    const value =
                                      e.target.value === ""
                                        ? ""
                                        : Number(e.target.value);
                                    field.onChange(value);
                                  }}
                                  onBlur={field.onBlur}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                      <TableCell className="bg-muted/50 py-2 font-medium">
                        Interval Time To
                      </TableCell>
                      <TableCell className="py-0 pr-0">
                        <FormField
                          control={form.control}
                          name="intervalTimeRandomTo"
                          render={({ field }) => (
                            <FormItem>
                              <FormControl>
                                <Input
                                  type="number"
                                  className="border-none p-0 shadow-none focus-visible:ring-0"
                                  {...field}
                                  onChange={(e) => {
                                    const value =
                                      e.target.value === ""
                                        ? ""
                                        : Number(e.target.value);
                                    field.onChange(value);
                                  }}
                                  onBlur={field.onBlur}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </TableCell>
                    </TableRow>
                  </>
                )}
                <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                  <TableCell className="bg-muted/50 py-2 font-medium">
                    Time Per No Item
                  </TableCell>
                  <TableCell className="py-0 pr-0">
                    <FormField
                      control={form.control}
                      name="timePerNoItem"
                      render={({ field }) => (
                        <FormItem>
                          <FormControl>
                            <Input
                              type="number"
                              className="border-none p-0 shadow-none focus-visible:ring-0"
                              {...field}
                              onChange={(e) => {
                                const value =
                                  e.target.value === ""
                                    ? ""
                                    : Number(e.target.value);
                                field.onChange(value);
                              }}
                              onBlur={field.onBlur}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </TableCell>
                </TableRow>
                <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                  <TableCell className="bg-muted/50 py-2 font-medium">
                    Time Per No Item Random
                  </TableCell>
                  <TableCell className="py-2 px-3">
                    <FormField
                      control={form.control}
                      name="isTimePerNoItemRandom"
                      render={({ field }) => (
                        <FormItem>
                          <FormControl>
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                checked={field.value}
                                onCheckedChange={(checked) => {
                                  field.onChange(checked);
                                  form.handleSubmit(onSubmit)();
                                }}
                              />
                            </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </TableCell>
                </TableRow>
                {watchIsTimePerNoItemRandom && (
                  <>
                    <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                      <TableCell className="bg-muted/50 py-2 font-medium">
                        Time Per No Item From
                      </TableCell>
                      <TableCell className="py-0 pr-0">
                        <FormField
                          control={form.control}
                          name="timePerNoItemRandomFrom"
                          render={({ field }) => (
                            <FormItem>
                              <FormControl>
                                <Input
                                  type="number"
                                  className="border-none p-0 shadow-none focus-visible:ring-0"
                                  {...field}
                                  onChange={(e) => {
                                    const value =
                                      e.target.value === ""
                                        ? ""
                                        : Number(e.target.value);
                                    field.onChange(value);
                                  }}
                                  onBlur={field.onBlur}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow className="*:border-border hover:bg-transparent [&>:not(:last-child)]:border-r">
                      <TableCell className="bg-muted/50 py-2 font-medium">
                        Time Per No Item To
                      </TableCell>
                      <TableCell className="py-0 pr-0">
                        <FormField
                          control={form.control}
                          name="timePerNoItemRandomTo"
                          render={({ field }) => (
                            <FormItem>
                              <FormControl>
                                <Input
                                  type="number"
                                  className="border-none p-0 shadow-none focus-visible:ring-0"
                                  {...field}
                                  onChange={(e) => {
                                    const value =
                                      e.target.value === ""
                                        ? ""
                                        : Number(e.target.value);
                                    field.onChange(value);
                                  }}
                                  onBlur={field.onBlur}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </TableCell>
                    </TableRow>
                  </>
                )}
              </TableBody>
            </Table>
          </div>
        </form>
      </Form>
    </div>
  );
}

function AddTypeGenDialogBox() {
  const [typeName, setTypeName] = useState("")
  const [attributes, setAttributes] = useState<{ name: string; type: string; value: string }[]>([
    { name: "", type: "string", value: "" },
  ])

  const handleAddAttribute = () => {
    setAttributes([...attributes, { name: "", type: "string", value: "" }])
  }

  const handleRemoveAttribute = (index: number) => {
    const newAttributes = [...attributes]
    newAttributes.splice(index, 1)
    setAttributes(newAttributes)
  }

  const handleAttributeChange = (index: number, field: string, value: string) => {
    const newAttributes = [...attributes]
    newAttributes[index] = { ...newAttributes[index], [field]: value }
    setAttributes(newAttributes)
  }

  const handleSubmit = () => {
    // Convert the attributes array to the required format
    const formattedAttributes: { [attr: string]: GenAttributes } = {}

    attributes.forEach((attr) => {
      if (attr.name) {
        formattedAttributes[attr.name] = {
          type: attr.type,
          value: attr.type === "number" ? Number(attr.value) : attr.value,
        }
      }
    })

    const genType: GenTypes = {
      typeName,
      attributes: formattedAttributes,
    }

    console.log("Generated Type:", genType)
    // Here you would typically save the data or pass it to a parent component
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Plus className="mr-2 h-4 w-4" />
          Add Type
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[550px]">
        <DialogHeader>
          <DialogTitle>Add New Type</DialogTitle>
          <DialogDescription>
            Create a new type with custom attributes. Fill in the type name and add attributes below.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="typeName" className="text-right">
              Type Name
            </Label>
            <Input
              id="typeName"
              value={typeName}
              onChange={(e) => setTypeName(e.target.value)}
              placeholder="Enter type name"
              className="col-span-3"
            />
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label className="text-base">Attributes</Label>
              <Button type="button" variant="outline" size="sm" onClick={handleAddAttribute}>
                <Plus className="mr-2 h-4 w-4" />
                Add Attribute
              </Button>
            </div>

            {attributes.map((attr, index) => (
              <div key={index} className="grid grid-cols-12 items-center gap-2">
                <div className="col-span-3">
                  <Input
                    placeholder="Name"
                    value={attr.name}
                    onChange={(e) => handleAttributeChange(index, "name", e.target.value)}
                  />
                </div>
                <div className="col-span-3">
                  <Select value={attr.type} onValueChange={(value) => handleAttributeChange(index, "type", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="string">String</SelectItem>
                      <SelectItem value="number">Number</SelectItem>
                      <SelectItem value="boolean">Boolean</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="col-span-5">
                  <Input
                    placeholder="Value"
                    value={attr.value}
                    onChange={(e) => handleAttributeChange(index, "value", e.target.value)}
                    type={attr.type === "number" ? "number" : "text"}
                  />
                </div>
                <div className="col-span-1 flex justify-center">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRemoveAttribute(index)}
                    disabled={attributes.length === 1}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={handleSubmit}>
            Save Type
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


export function AddTypesGen() {
  return (
    <div className="w-full flex flex-col">
      <div className="w-full flex flex-row justify-between">
        <h1 className="font-semibold text-lg text-primary pb-2">
          Add Generator Types
        </h1>
        <div>
          <AddTypeGenDialogBox />
        </div>
      </div>
    </div>
  );
}
