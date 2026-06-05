# Live Preview: `ssr: false` Mode

PostMessage-based updates for instant preview without iframe refresh.

## What This Mode Does

When `ssr: false`:
1. CMS sends content changes via `postMessage` to the iframe
2. The Live Preview SDK receives the message
3. Your `onEntryChange()` callback fires
4. Your client-side code re-fetches data and updates the UI
5. **No page refresh** - updates happen via JavaScript

## When to Use `ssr: false`

- Your preview pages fetch data **client-side** (useEffect, React Query, etc.)
- You want instant updates without iframe refresh
- You can implement an `onEntryChange()` callback to re-fetch data

## Installation

```bash
npm install @contentstack/delivery-sdk @contentstack/live-preview-utils
```

## Implementation Steps

### 1. Configure Stack with Live Preview

```typescript
// lib/contentstack.ts
import contentstack from "@contentstack/delivery-sdk";

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: "us",
  live_preview: {
    enable: true,
    preview_token: process.env.CONTENTSTACK_PREVIEW_TOKEN,
    host: "rest-preview.contentstack.com",
  },
});
```

### 2. Initialize Live Preview SDK

```typescript
// lib/contentstack.ts (continued)
import ContentstackLivePreview, { IStackSdk } from "@contentstack/live-preview-utils";

export function initLivePreview() {
  ContentstackLivePreview.init({
    ssr: false, // CSR mode
    enable: true,
    mode: "preview",
    stackSdk: stack.config as IStackSdk,
    stackDetails: {
      apiKey: process.env.CONTENTSTACK_API_KEY!,
      environment: process.env.CONTENTSTACK_ENVIRONMENT!,
    },
    editButton: { enable: true },
  });
}
```

### 3. Fetch Data and Handle Updates

```typescript
// components/Page.tsx
import { useEffect, useState } from "react";
import contentstack from "@contentstack/delivery-sdk";
import ContentstackLivePreview from "@contentstack/live-preview-utils";
import { stack, initLivePreview } from "@/lib/contentstack";

export default function Page() {
  const [entry, setEntry] = useState(null);

  useEffect(() => {
    // Initialize Live Preview once
    initLivePreview();

    // Fetch data function
    const fetchData = async () => {
      const result = await stack
        .contentType("page")
        .entry("entry_uid")
        .fetch();
      
      // Add editable tags
      contentstack.Utils.addEditableTags(result, "page", true);
      setEntry(result);
    };

    // Register for content changes
    ContentstackLivePreview.onEntryChange(fetchData);
    
    // Initial fetch
    fetchData();
  }, []);

  if (!entry) return <div>Loading...</div>;

  return (
    <div>
      <h1 {...(entry?.$ && entry?.$.title)}>{entry.title}</h1>
      <div {...(entry?.$ && entry?.$.content)}>{entry.content}</div>
    </div>
  );
}
```

## GraphQL CSR Example

```typescript
import { request } from "graphql-request";
import ContentstackLivePreview from "@contentstack/live-preview-utils";

const GRAPHQL_HOST = "graphql.contentstack.com";
const PREVIEW_HOST = "graphql-preview.contentstack.com";

async function fetchGraphQL(query: string, variables = {}) {
  const hash = ContentstackLivePreview.hash;
  const isPreview = Boolean(hash);
  const host = isPreview ? PREVIEW_HOST : GRAPHQL_HOST;

  const headers: Record<string, string> = {
    api_key: process.env.CONTENTSTACK_API_KEY!,
    access_token: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  };

  if (isPreview) {
    headers.live_preview = hash;
    headers.preview_token = process.env.CONTENTSTACK_PREVIEW_TOKEN!;
    headers.include_applied_variants = "true";
  }

  return request(`https://${host}/graphql`, query, variables, headers);
}
```

## Edit Tags

### Automatic Tags (Recommended)

```typescript
import contentstack from "@contentstack/delivery-sdk";

const entry = await stack.contentType("page").entry("uid").fetch();

// Add editable tags - true = object format for JSX
contentstack.Utils.addEditableTags(entry, "page", true, "en-us");
```

### Using in JSX

```tsx
// entry.$ contains the editable tag objects
<h1 {...(entry?.$ && entry?.$.title)}>{entry.title}</h1>
<p {...(entry?.$ && entry?.$.description)}>{entry.description}</p>
```

### Manual Tags

```html
<h1 data-cslp="page.blt123.en-us.title">Title Here</h1>
```

Format: `{content_type_uid}.{entry_uid}.{locale}.{field_uid}`

## Complete React Example

```tsx
"use client";
import { useEffect, useState } from "react";
import contentstack from "@contentstack/delivery-sdk";
import ContentstackLivePreview, { IStackSdk } from "@contentstack/live-preview-utils";

// Stack instance
const stack = contentstack.stack({
  apiKey: process.env.NEXT_PUBLIC_CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.NEXT_PUBLIC_CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT!,
  region: "us",
  live_preview: {
    enable: true,
    preview_token: process.env.NEXT_PUBLIC_CONTENTSTACK_PREVIEW_TOKEN,
    host: "rest-preview.contentstack.com",
  },
});

// Initialize once
let initialized = false;
function initOnce() {
  if (initialized) return;
  ContentstackLivePreview.init({
    ssr: false,
    enable: true,
    stackSdk: stack.config as IStackSdk,
    stackDetails: {
      apiKey: process.env.NEXT_PUBLIC_CONTENTSTACK_API_KEY!,
      environment: process.env.NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT!,
    },
    editButton: { enable: true },
  });
  initialized = true;
}

export default function HomePage() {
  const [page, setPage] = useState<any>(null);

  useEffect(() => {
    initOnce();

    async function fetchPage() {
      const entry = await stack.contentType("page").entry("home").fetch();
      contentstack.Utils.addEditableTags(entry, "page", true);
      setPage(entry);
    }

    ContentstackLivePreview.onEntryChange(fetchPage);
    fetchPage();
  }, []);

  if (!page) return <div>Loading...</div>;

  return (
    <main>
      <h1 {...(page?.$ && page?.$.title)}>{page.title}</h1>
      <p {...(page?.$ && page?.$.description)}>{page.description}</p>
    </main>
  );
}
```

## Troubleshooting

### Content not updating

1. Verify `ssr: false` is set
2. Check `onEntryChange` is registered and calls your fetch function
3. Verify preview token is correct
4. Check browser console for errors or postMessage issues

### Edit buttons not showing

1. Verify `editButton: { enable: true }`
2. Check editable tags are added via `addEditableTags()`
3. Verify site is loaded in Contentstack iframe

### HTTPS errors

- Site must be served over HTTPS
- Use ngrok or similar for local development

## Important Note

**This is for preview only**. In production:
- Live Preview is disabled
- No postMessage communication happens
- Your site works normally without any Live Preview code executing

## Next Steps

- [SSR Mode](./ssr-mode.md) - Iframe refresh with query params
- [Framework Patterns](../frameworks/) - Next.js, Nuxt examples

