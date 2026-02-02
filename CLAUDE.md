# Web Content Extraction Workflows

## Recommended approach: MCP playwright (for live URLs)

**Load tools first**: `ToolSearch` with query `playwright navigate`

**Workflow**:
1. `browser_navigate` - Visit URL with full JS rendering
2. `browser_snapshot` - Get clean text/markdown snapshot
3. Structure extracted content into organized markdown sections

**Advantages**: Works with JS-heavy sites, ChatGPT shared links, authenticated content

## Fallback: webarchive files (for saved Safari pages)

`python3 + plistlib` - Extract HTML from .webarchive binary plist format
`HTMLParser` - Strip scripts/styles to get clean text content

**Workflow**:
1. Use `plistlib.load()` to read webarchive binary plist
2. Extract `WebMainResource['WebResourceData']` as HTML bytes
3. Parse HTML with `HTMLParser`, skip `<script>` and `<style>` tags
4. Save cleaned text to intermediate .txt file
5. Read and structure into markdown sections

## File size limits

- Read tool: 256KB file size limit, 25K token limit
- Strategy: Extract → intermediate files → chunked reading
- Use `offset` and `limit` parameters for large files

## WebFetch vs playwright

**WebFetch**: Good for simple static pages, quick queries
**Playwright**: Required for JS-rendered content (ChatGPT links, SPAs, auth sites)

**WebFetch fails** → Use playwright instead

## MCP playwright tools for web extraction

**Must load first**: `ToolSearch` with `playwright` query before using

**Key tools**:
- `browser_navigate` - Visit URL with JS rendering
- `browser_snapshot` - Get page text/markdown (best for content extraction)
- `browser_screenshot` - Capture visuals
- `browser_run_code` - Custom Playwright scripts for complex extraction
- `browser_evaluate` - Run JavaScript on page

**Example workflow**:
```bash
ToolSearch "playwright navigate"  # Load tools
browser_navigate url="https://..."
browser_snapshot  # Get clean markdown/text
```

## Decision tree: Which method to use?

- **Live URL** → Use MCP playwright (handles JS, auth, dynamic content)
- **Already have .webarchive** → Use plistlib extraction (faster, offline)
- **WebFetch failing** → Switch to playwright (likely needs JS rendering)
- **Need screenshots** → Use playwright browser_screenshot
