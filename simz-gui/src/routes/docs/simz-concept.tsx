import MarkdownPreviewer from '@/components/default/docViewer/comp-func'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/docs/simz-concept')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <MarkdownPreviewer filePath="/public/SimZ_Conceptual_Guide.md" />
  )
}
