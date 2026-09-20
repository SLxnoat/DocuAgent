/**
 * Utilities for parsing and rewriting Markdown content for DocuAgent.
 */

/**
 * Extracts all screenshot image URLs and step indices from Markdown text.
 * Pattern matches: ![Step 1: Description](/assets/job_123/step_001.png)
 */
export function extractScreenshotReferences(markdown: string): Array<{
  alt: string;
  src: string;
  stepIndex: number | null;
}> {
  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  const matches: Array<{ alt: string; src: string; stepIndex: number | null }> =
    [];
  let match;

  while ((match = imageRegex.exec(markdown)) !== null) {
    const alt = match[1];
    const src = match[2];
    // Try to extract step index from URL: e.g. step_002.png -> 2
    const stepMatch = src.match(/step_(\d+)\.png/i);
    const stepIndex = stepMatch ? parseInt(stepMatch[1], 10) : null;
    matches.push({ alt, src, stepIndex });
  }

  return matches;
}

/**
 * Normalizes image paths in Markdown so that relative or bare /assets/ paths
 * resolve correctly against the API or assets root.
 */
export function normalizeImagePaths(markdown: string, apiBase: string): string {
  // If image points to /assets/..., ensure it points to the proxy or host
  return markdown.replace(
    /!\[([^\]]*)\]\(\/assets\/([^)]+)\)/g,
    (_match, alt, path) => {
      const baseUrl = apiBase.replace(/\/api\/v1\/?$/, "");
      return `![${alt}](${baseUrl}/assets/${path})`;
    },
  );
}
