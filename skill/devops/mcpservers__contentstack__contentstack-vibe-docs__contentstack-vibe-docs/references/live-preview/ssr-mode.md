# Live Preview: `ssr: true` Mode

Iframe refresh with query parameters for server-side data fetching.

## What This Mode Does

When `ssr: true`:
1. Editor makes changes in the CMS
2. CMS **refreshes the iframe** with query parameters appended to the URL:
   - `?live_preview=<hash>&entry_uid=<uid>&content_type_uid=<type>`
3. Your server reads these query params
4. Server uses the `live_preview` hash to fetch the preview (unpublished) content
5. Server renders the page with preview data

## When to Use `ssr: true`

- Your preview pages fetch data **server-side** (getServerSideProps, server components, API routes)
- Your server needs to read query params to know which preview content to fetch
- You can't easily trigger client-side re-fetches

## Mental model: why per-request is the whole ballgame

The preview hash is **runtime state**, not config. It is:

- Created by the CMS per editing session.
- Changed every time an editor saves.
- Valid for exactly one editor, in exactly one tab, for a short window.
- **Dangerous** to cache or share.

In SSR mode, the flow is:

```
1. Editor saves                         (CMS)
2. CMS refreshes the preview iframe with
   ?live_preview=<hash>&entry_uid=...&content_type_uid=...
3. Your server receives the request
4. Server reads the hash from query params
5. Server creates a fresh Contentstack client for this request
6. Client.livePreviewQuery(...) attaches the hash
7. Client fetches from the preview host with the hash
8. Server renders with draft content
9. Response returned; client discarded
```

Every one of those steps must be per-request. Share any of them and two editors see each other's drafts under load.

### What goes wrong with a shared client

```typescript
// ❌ module-level stack — the trap
const stack = createStack();

export default async function Page({ searchParams }) {
  const { live_preview } = await searchParams;
  if (live_preview) stack.livePreviewQuery({ live_preview, ... }); // mutates SHARED state
  return await stack.contentType("page").entry(slug).fetch();
}
```

`livePreviewQuery()` mutates the stack's internal config. Under concurrent requests, request A sets its hash, request B sets its hash, request A's fetch runs with B's hash. You get silent data leaks — no error, just wrong content.

### The request-scoped factory

```typescript
// ✅ per-request factory — the only correct pattern for SSR preview
export default async function Page({ searchParams }) {
  const { live_preview, entry_uid, content_type_uid } = await searchParams;
  const stack = createStack();                        // fresh per request
  if (live_preview) {
    stack.livePreviewQuery({ live_preview, contentTypeUid: content_type_uid || "page", entryUid: entry_uid || "" });
  }
  return await stack.contentType("page").entry(slug).fetch();
}
```

Factory call cost is negligible — creating a stack instance is just wiring a config object. The safety is absolute.

### Four non-negotiables for SSR preview

1. **Create the client inside the request handler** — never at module scope.
2. **Extract the hash from `searchParams` on every request** — never cache it.
3. **Bypass every cache when `live_preview` is present** — CDN cache, `fetch` cache, Redis, anything.
4. **Preserve preview query params across navigation** — links, redirects, rewrites, and middleware must all pass `live_preview`, `entry_uid`, `content_type_uid`, `locale` through unchanged.

## Installation

```bash
npm install @contentstack/delivery-sdk @contentstack/live-preview-utils
```

## Key Differences from `ssr: false`

| Aspect | `ssr: false` | `ssr: true` |
|--------|--------------|-------------|
| Update mechanism | postMessage | Iframe refresh with query params |
| How you get preview hash | SDK provides via `ContentstackLivePreview.hash` | Read from URL query params |
| Data fetching | Client re-fetches via `onEntryChange()` | Server reads params and fetches |
| Page refresh | No | Yes (iframe reloads) |
| Stack instance | Can be shared | **New per request** (to avoid cross-session issues) |

## Implementation Steps

### 1. Configure Stack

```typescript
// lib/contentstack.ts
import contentstack from "@contentstack/delivery-sdk";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

const region = process.env.CONTENTSTACK_REGION || "us";
const endpoints = getContentstackEndpoints(region, true); // omitHttps: true

export function createStack() {
  return contentstack.stack({
    apiKey: process.env.CONTENTSTACK_API_KEY!,
    deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
    environment: process.env.CONTENTSTACK_ENVIRONMENT!,
    region,
    live_preview: {
      enable: true,
      preview_token: process.env.CONTENTSTACK_PREVIEW_TOKEN,
      host: endpoints.preview,          // region-aware, not hardcoded
    },
  });
}
```

> The preview host is region-specific. `rest-preview.contentstack.com` is only correct for US. EU, AU, Azure, and GCP regions have different hosts. Resolve via `@timbenniks/contentstack-endpoints` or see `../concepts/regions.md`.

### 2. Server-Side: Handle Preview Hash

**CRITICAL**: Create a new stack instance per request to avoid cross-session data.

```typescript
// Server-side handler
export async function getPageData(searchParams: URLSearchParams) {
  const stack = createStack(); // New instance per request
  
  const live_preview = searchParams.get("live_preview");
  const entry_uid = searchParams.get("entry_uid");
  const content_type_uid = searchParams.get("content_type_uid");

  // Apply preview query if hash exists
  if (live_preview) {
    stack.livePreviewQuery({
      live_preview,
      contentTypeUid: content_type_uid || "page",
      entryUid: entry_uid || "",
    });
  }

  const entry = await stack.contentType("page").entry("entry_uid").fetch();
  return entry;
}
```

### 3. Client-Side: Initialize SDK

**Important**: The client component must create its own stack using `NEXT_PUBLIC_` env vars. Do NOT import server-side `createStack()` — server-only env vars are not available in client bundles.

```typescript
// components/LivePreviewInit.tsx
"use client";
import { useEffect } from "react";
import contentstack from "@contentstack/delivery-sdk";
import ContentstackLivePreview from "@contentstack/live-preview-utils";
import type { IStackSdk } from "@contentstack/live-preview-utils";

export function LivePreviewInit() {
  useEffect(() => {
    const stack = contentstack.stack({
      apiKey: process.env.NEXT_PUBLIC_CONTENTSTACK_API_KEY!,
      deliveryToken: "unused-on-client",
      environment: process.env.NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT!,
      region: process.env.NEXT_PUBLIC_CONTENTSTACK_REGION || "us",
      live_preview: {
        enable: true,
        host: "rest-preview.contentstack.com",
      },
    });

    ContentstackLivePreview.init({
      ssr: true,
      enable: true,
      mode: "preview",  // or "builder" for Visual Builder
      stackSdk: stack.config as unknown as IStackSdk,
      stackDetails: {
        apiKey: process.env.NEXT_PUBLIC_CONTENTSTACK_API_KEY!,
        environment: process.env.NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT!,
      },
      editButton: { enable: true },
    });
  }, []);

  return null;
}
```

### 4. Add to Layout

```tsx
// app/layout.tsx
import { LivePreviewInit } from "@/components/LivePreviewInit";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <LivePreviewInit />
        {children}
      </body>
    </html>
  );
}
```

## Express.js Example

```typescript
import express from "express";
import contentstack from "@contentstack/delivery-sdk";

const app = express();

app.get("*", async (req, res) => {
  // Create new stack per request
  const stack = contentstack.stack({
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

  // Apply preview hash from query params
  if (req.query.live_preview) {
    stack.livePreviewQuery(req.query);
  }

  const entry = await stack.contentType("page").entry("entry_uid").fetch();
  
  // Add editable tags
  contentstack.Utils.addEditableTags(entry, "page", true);

  // Render template with entry data
  res.render("page", { entry });
});
```

## Next.js App Router Example

```typescript
// app/[slug]/page.tsx
import contentstack from "@contentstack/delivery-sdk";
import { createStack } from "@/lib/contentstack";

export default async function Page({ 
  params, 
  searchParams 
}: { 
  params: { slug: string };
  searchParams: Promise<{ [key: string]: string | undefined }>;
}) {
  const stack = createStack();
  const { live_preview, entry_uid, content_type_uid } = await searchParams;

  // Apply preview query
  if (live_preview) {
    stack.livePreviewQuery({
      live_preview,
      contentTypeUid: content_type_uid || "page",
      entryUid: entry_uid || "",
    });
  }

  const entry = await stack.contentType("page").entry(params.slug).fetch();
  contentstack.Utils.addEditableTags(entry, "page", true);

  return (
    <div>
      <h1 {...(entry?.$ && entry?.$.title)}>{entry.title}</h1>
    </div>
  );
}
```

## GraphQL SSR Example

```typescript
import { request } from "graphql-request";

async function fetchPage(searchParams: URLSearchParams) {
  const hash = searchParams.get("live_preview");
  const isPreview = Boolean(hash);
  
  const host = isPreview 
    ? "graphql-preview.contentstack.com" 
    : "graphql.contentstack.com";

  const headers: Record<string, string> = {
    api_key: process.env.CONTENTSTACK_API_KEY!,
    access_token: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  };

  if (isPreview) {
    headers.live_preview = hash!;
    headers.preview_token = process.env.CONTENTSTACK_PREVIEW_TOKEN!;
    headers.include_applied_variants = "true";
  }

  const query = `
    query GetPage($url: String!) {
      allContentstackPage(where: { url: $url }) {
        nodes { uid title url content }
      }
    }
  `;

  return request(`https://${host}/graphql`, query, { url: "/" }, headers);
}
```

## Visual Builder Mode

Visual Builder extends Live Preview with inline editing and drag-and-drop reordering. To enable it, change `mode` from `"preview"` to `"builder"`:

```typescript
ContentstackLivePreview.init({
  ssr: true,
  enable: true,
  mode: "builder",  // enables Visual Builder (vs "preview" for basic Live Preview)
  // ... rest of config
});
```

### URL Field Requirement

Visual Builder identifies entries by matching the iframe URL to the entry's `url` field. Content types must:
- Have `is_page: true` in their options
- Include a `url` field in the schema
- Query entries by `url`, not a custom slug field

### Edit Tags for Multiple Fields (Add/Delete/Reorder)

For multiple group fields (arrays), tag both the container and each item. Use the `field__${index}` pattern on the **parent entry's** `$` object:

```typescript
// Container gets the field-level tag
<div {...(entry.$ && entry.$.page_components)}>
  {entry.page_components?.map((component, index) => (
    // Each item gets field__index from the PARENT entry's $
    <div key={index} {...(entry.$?.[`page_components__${index}`])}>
      <h3 {...(component.$ && component.$.title)}>{component.title}</h3>
    </div>
  ))}
</div>
```

**Important**: The item-level tag uses `entry.$[`field__${index}`]` from the parent, NOT `item.$._`.

---

## Important Notes

### New Stack Per Request

**CRITICAL**: Always create a new stack instance for each request to avoid:
- Cross-session data leakage
- Cached preview content for wrong users
- Security issues

```typescript
// ❌ WRONG - Shared instance
const stack = createStack();

app.get("*", async (req, res) => {
  stack.livePreviewQuery(req.query); // Affects all requests!
});

// ✅ CORRECT - New instance per request
app.get("*", async (req, res) => {
  const stack = createStack();
  stack.livePreviewQuery(req.query);
});
```

### Edit Tags

Edit tags work the same as CSR:

```typescript
import contentstack from "@contentstack/delivery-sdk";

contentstack.Utils.addEditableTags(entry, "page", true, "en-us");
```

## Troubleshooting

### Page not refreshing on changes

1. Verify `ssr: true` is set in client initialization
2. Check SDK is initialized on client side
3. Verify CMS is configured with correct preview URL

### Query params not appearing

1. Check Live Preview is enabled in Contentstack environment settings
2. Verify the preview URL is correctly configured

### Wrong content shown

1. Ensure new stack instance per request (prevents cross-session data)
2. Check `livePreviewQuery` is called with the query params
3. Verify preview token is valid

### Edit buttons not showing

1. SDK must initialize on client side (even for SSR mode)
2. Editable tags must be added to entry
3. Check site loads correctly in iframe

## Important Note

**This is for preview only**. In production:
- Live Preview is disabled
- No `live_preview` query params are added
- Your site fetches published content normally

## Next Steps

- [CSR Mode](./csr-mode.md) - PostMessage-based alternative
- [Framework Patterns](../frameworks/) - Specific framework examples

