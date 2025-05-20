import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import 'github-markdown-css/github-markdown-light.css';
import 'highlight.js/styles/github.css';

interface MarkdownPreviewerProps {
  filePath: string; // path relative to public folder, e.g. '/docs/guide.md'
}

const MarkdownPreviewer: React.FC<MarkdownPreviewerProps> = ({ filePath }) => {
  const [content, setContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(filePath)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to load markdown file: ${res.statusText}`);
        }
        return res.text();
      })
      .then((text) => setContent(text))
      .catch((err) => setError(err.message));
  }, [filePath]);

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="prose max-w-none p-4">

      <article className="markdown-body bg-white dark:bg-gray-800 prose prose-headings:text-gray-900 prose-p:text-gray-700 dark:prose-headings:text-gray-100 dark:prose-p:text-gray-300 mx-auto p-6 rounded-lg shadow">
        <ReactMarkdown children={content} remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight, rehypeRaw]} />
      </article>
    </div>
  );
};

export default MarkdownPreviewer;
