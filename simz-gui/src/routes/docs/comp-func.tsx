import MarkdownPreviewer from '@/components/default/docViewer/comp-func'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/docs/comp-func')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <MarkdownPreviewer filePath="/public/component_helper_methods.md" />
  )
}
