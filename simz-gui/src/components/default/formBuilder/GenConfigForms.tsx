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
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Code, Eye, Pencil, Plus, Trash } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import ReactCodeMirror from "@uiw/react-codemirror";
import { json } from "@codemirror/lang-json";
import { SimDataState } from "@/states/simDataState";
import { CompDataI } from "@/types/component";

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
    const subscription = form.watch((_value, { type }) => {
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

interface AddTypesGenProps {
  compId: string | undefined;
}

export function AddTypesGen({ compId }: AddTypesGenProps) {
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedTypeId, setSelectedTypeId] = useState<string | undefined>(undefined)
  const [compData, setCompData] = useState<CompDataI | null>(null)
  const { get_comp_by_id, deleteGenType, getGenTypeById } = SimDataState();

  if (compId === undefined || compId === null) {
    console.log("error in AddTypesGen Component [compId is null or undefined]")
    return
  }

  useEffect(() => {
    const compData = get_comp_by_id(compId)
    if (compData === null) {
      console.log("error in AddTypesGen Component [Component doesn't exists]")
      return
    }
    setCompData(compData)
  }, [compId])

  const deleteGenTypeFn = (typeId: string) => {
    deleteGenType(typeId)
    setCompData(get_comp_by_id(compId))
  }

  const handleEditClick = (typeId: string) => {
    setSelectedTypeId(typeId);
    setEditDialogOpen(true);
  }

  return (
    <div className="w-full flex flex-col">
      <div className="w-full flex flex-row justify-between">
        <h1 className="font-semibold text-lg text-primary pb-2">
          Add Generator Types
        </h1>
        <div>
          <JsonViewerDialog
            open={addDialogOpen}
            onOpenChange={setAddDialogOpen}
            compId={compId}
            triggerComponent={<Button variant="outline" size="sm"><Plus /> Type</Button>}
            genTypesId={undefined}
          />
        </div>
      </div>
      <div className="w-full flex flex-col gap-2 mt-2">
        {compData?.GenData?.types?.map((typeId) => {
          const genTypeName = getGenTypeById(typeId)?.typeName
          return (
            <div className="w-full flex flex-row justify-between bg-muted/50 items-center px-4 py-2 hover:bg-muted/100 border rounded-md" id={typeId} key={typeId}>
              <h1>{genTypeName ?? "No Type Name"}</h1>
              <div className="flex flex-row gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEditClick(typeId)}
                >
                  <Pencil />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deleteGenTypeFn(typeId)}
                >
                  <Trash color="red" />
                </Button>
              </div>
            </div>
          )
        }) ?? (
            <div className="flex rounded-lg border border-dashed h-10 bg-gray-100 items-center justify-center">
              <p className="text-sm">Add Gen type</p>
            </div>
          )}
      </div>

      {/* Edit Dialog */}
      <JsonViewerDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        compId={compId}
        triggerComponent={<div />}
        genTypesId={selectedTypeId}
      />
    </div>
  );
}

// Define the structure for an attribute value
interface AttributeValue {
  type: string;
  value: string | number | boolean | object | null;
}

// The new structure is an object with attribute names as keys
interface AttributeMap {
  [name: string]: AttributeValue;
}

interface JsonViewerDialogProps {
  triggerComponent: React.ReactNode;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  compId: string | undefined;
  genTypesId?: string;
}

// Updated default JSON structure
const DefaultLayoutJson: string = `
{
  "attr_name": {
    "type": "string",
    "value": "test"
  }
}
`;

function JsonViewerDialog({ triggerComponent, open, onOpenChange, compId, genTypesId }: JsonViewerDialogProps) {
  const [activeTab, setActiveTab] = useState<"view" | "json">("view");
  const [jsonValue, setJsonValue] = useState<string>(DefaultLayoutJson);
  const [typeName, setTypeName] = useState<string>("Example");
  const [parsedJson, setParsedJson] = useState<AttributeMap | null>({});
  const [jsonError, setJsonError] = useState<string | null>(null);
  const { addGenType, updateGenType, getGenTypeById } = SimDataState();

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      // Reset to default state first
      formClear();

      // If we have a genTypesId, load its data
      if (genTypesId) {
        const genType = getGenTypeById(genTypesId);
        if (genType) {
          setTypeName(genType.typeName);
          setJsonValue(JSON.stringify(genType.attributes, null, 2));
          setParsedJson(genType.attributes);
        }
      }
    } else {
      // Reset everything when dialog closes
      formClear();
      setActiveTab("view");
    }
  }, [open, genTypesId]);

  const onChange = useCallback((val: string, _viewUpdate: any) => {
    setJsonValue(val);
  }, []);

  // Parse JSON when it changes
  useEffect(() => {
    if (activeTab !== "json") return;

    try {
      const parsed: AttributeMap = JSON.parse(jsonValue);

      // Ensure we have an object, not an array
      if (typeof parsed !== "object" || Array.isArray(parsed)) {
        setJsonError("JSON must be an object with named attributes");
        setParsedJson(null);
        return;
      }

      // Validate each attribute property
      for (const [key, attr] of Object.entries(parsed)) {
        if (typeof attr !== "object" || attr === null) {
          setJsonError(`Attribute "${key}" must be an object`);
          setParsedJson(null);
          return;
        }
        if (!attr.hasOwnProperty("type") || typeof attr.type !== "string") {
          setJsonError(`Attribute "${key}" must have a valid "type" property`);
          setParsedJson(null);
          return;
        }
      }

      setJsonError(null);
      setParsedJson(parsed as AttributeMap);
    } catch (e) {
      console.error(e);
      const errorMessage = e instanceof Error ? e.message : String(e);
      setJsonError(`Invalid JSON format: \n${errorMessage}`);
      setParsedJson(null);
    }
  }, [jsonValue, activeTab]);

  const formClear = () => {
    setJsonValue(DefaultLayoutJson);
    setParsedJson(null);
    setJsonError(null);
    setTypeName("Example");
  };

  const handleSave = () => {
    if (compId === undefined || compId === null) {
      console.log("error in JsonViewerDialog Component [compId is null or undefined]");
      return;
    }
    if (genTypesId) {
      if (parsedJson) {
        updateGenType(compId, genTypesId, {
          typeName: typeName,
          genComponentId: compId,
          attributes: parsedJson
        });
        onOpenChange(false);
      }
      return;
    }
    if (parsedJson) {
      addGenType({
        typeName: typeName,
        genComponentId: compId,
        attributes: parsedJson
      }, compId);
      onOpenChange(false);
    }
  };

  const handleCancel = () => {
    formClear();
    onOpenChange(false);
  };

  const getTypeColor = (type: string) => {
    console.log(type)
    switch (type) {
      case "string":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 px-2 rounded-md";
      case "number":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300  px-2 rounded-md";
      case "boolean":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300  px-2 rounded-md";
      case "object":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300  px-2 rounded-md";
      case "array":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300  px-2 rounded-md";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300  px-2 rounded-md";
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        {triggerComponent}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[550px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>{genTypesId ? "Edit Type" : "Add New Type"}</DialogTitle>
          </div>
          <DialogDescription>
            {genTypesId ? "Edit the type structure." : "Create a new type by defining its structure."} Toggle between JSON and visual view.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid w-full items-center gap-1.5">
            <Label htmlFor="typeName">Type Name</Label>
            <Input
              id="typeName"
              value={typeName}
              onChange={(e) => setTypeName(e.target.value)}
              className="col-span-3"
              placeholder="Enter type name"
            />
          </div>

          <Tabs
            value={activeTab}
            onValueChange={(value) => setActiveTab(value as "view" | "json")}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="view" className="flex items-center gap-1">
                <Eye className="h-4 w-4" />
                Visual Mode
              </TabsTrigger>
              <TabsTrigger value="json" className="flex items-center gap-1">
                <Code className="h-4 w-4" />
                JSON Mode
              </TabsTrigger>
            </TabsList>

            <TabsContent value="json" className="space-y-4">
              <div className="grid w-full gap-1.5">
                <Label htmlFor="jsonEditor">JSON Structure</Label>
                <ReactCodeMirror
                  value={jsonValue}
                  height="200px"
                  onChange={onChange}
                  extensions={[json()]}
                />
                {jsonError && (
                  <Alert variant="destructive" className="mt-2">
                    <AlertDescription>{jsonError}</AlertDescription>
                  </Alert>
                )}
              </div>
            </TabsContent>

            <TabsContent value="view" className="space-y-4">
              <div className="space-y-4">
                <h3 className="text-sm font-medium">Attributes</h3>
                {parsedJson && Object.keys(parsedJson).length ? (
                  <div className="space-y-2">
                    {Object.entries(parsedJson).map(([name, type]) => (
                      <div key={name} className="flex items-center gap-2 p-3 border rounded-md">
                        <div className="flex-1 font-medium truncate">{name}</div>
                        <div className={getTypeColor(type.type)}>{type.type}</div>
                        <div className="flex-1 text-right truncate text-muted-foreground">{JSON.stringify(type.value).slice(0, 30)}...</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">No attributes defined</div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={handleCancel}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!parsedJson}>
            {genTypesId ? "Update" : "Save"} Type
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
