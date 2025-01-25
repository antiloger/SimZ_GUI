import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { ErrorState } from "@/states/errorState"

export function ErrorDialog() {
  const { error, clearError } = ErrorState();
  return (
    <AlertDialog open={!!error} onOpenChange={(isOpen) => !isOpen && clearError()}>
      {/* <AlertDialogTrigger asChild> */}
      {/*   <Button variant="outline">Show Dialog</Button> */}
      {/* </AlertDialogTrigger> */}
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{error?.header ?? "N/A"}</AlertDialogTitle>
          <AlertDialogDescription>
            {error?.body ?? "N?A"}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={clearError} >Continue</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
