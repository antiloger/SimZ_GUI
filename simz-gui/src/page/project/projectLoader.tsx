import { Loader2 } from 'lucide-react'

interface LoadingScreenProps {
  message?: string
}

export function ProjectLoadingScreen({ message = "Loading..." }: LoadingScreenProps) {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-background">
      <Loader2 className="h-12 w-12 animate-spin text-primary" aria-hidden="true" />
      <p className="mt-4 text-lg font-medium text-foreground" aria-live="polite">
        {message}
      </p>
    </div>
  )
}
