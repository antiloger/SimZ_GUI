import MarkdownPreviewer from '@/components/default/docViewer/comp-func'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/docs/code-arch')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <MarkdownPreviewer filePath="/public/SimZ_Architecture.md" />
  )
}
