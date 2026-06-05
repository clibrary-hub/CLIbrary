# Contentstack with Next.js

Complete patterns for Next.js App Router with Contentstack and Live Preview.

## Installation

```bash
npm install @contentstack/delivery-sdk @contentstack/live-preview-utils
```

## Stack Configuration

Use a **factory** that creates a fresh stack per call. A shared module-level stack is safe for CSR, but for SSR preview it causes data leaks across concurrent requests (one editor sees another editor's drafts). Always use the factory in server code paths.

```typescript
// lib/contentstack.ts
import contentstack from "@contentstack/delivery-sdk";
import ContentstackLivePreview, {
  IStackSdk,
} from "@contentstack/live-preview-utils";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

const region = process.env.NEXT_PUBLIC_CONTENTSTACK_REGION || "us";
const endpoints = getContentstackEndpoints(region, true);

export function createStack() {
  return contentstack.stack({
    apiKey: process.env.NEXT_PUBLIC_CONTENTSTACK_API_KEY!,
    deliveryToken: process.env.NEXT_PUBLIC_CONTENTSTACK_DELIVERY_TOKEN!,
    environment: process.env.NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT!,
    region,
    live_preview: {
      enable: true,
      preview_token: process.env.NEXT_PUBLIC_CONTENTSTACK_PREVIEW_TOKEN,
      host: endpoints.preview,
    },
  });
}

// Client-side singleton is fine for CSR. Import `createStack()` in server code.
export const stack = createStack();

// ssr: false = postMessage updates, client re-fetches via onEntryChange()
// ssr: true = iframe refresh with query params, server reads them
export function initLivePreview(ssrMode: boolean = false) {
  ContentstackLivePreview.init({
    ssr: ssrMode,
    enable: true,
    mode: "preview",
    stackSdk: stack.config as IStackSdk,
    stackDetails: {
      apiKey: process.env.NEXT_PUBLIC_CONTENTSTACK_API_KEY!,
      environment: process.env.NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT!,
    },
    editButton: { enable: true },
  });
}
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_CONTENTSTACK_API_KEY=your_api_key
NEXT_PUBLIC_CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token
NEXT_PUBLIC_CONTENTSTACK_PREVIEW_TOKEN=your_preview_token
NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT=preview
NEXT_PUBLIC_CONTENTSTACK_REGION=us
```

---

## `ssr: false` Pattern (Client-Side Data Fetching)

Best for: Pages that fetch data client-side. Preview updates instantly via postMessage without iframe refresh.

```typescript
// app/page.tsx
"use client";
import { useEffect, useState } from "react";
import contentstack from "@contentstack/delivery-sdk";
import ContentstackLivePreview from "@contentstack/live-preview-utils";
import { stack, initLivePreview } from "@/lib/contentstack";

interface PageEntry {
  title: string;
  description: string;
  $?: Record<string, any>;
}

export default function HomePage() {
  const [page, setPage] = useState<PageEntry | null>(null);

  useEffect(() => {
    initLivePreview(false); // postMessage mode - client re-fetches on changes

    async function fetchPage() {
      const entry = await stack.contentType("page").entry("home").fetch();
      contentstack.Utils.addEditableTags(entry, "page", true);
      setPage(entry as PageEntry);
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

---

## `ssr: true` Pattern (Server-Side Data Fetching)

Best for: Pages that fetch data server-side. CMS refreshes iframe with query params (`?live_preview=...`).

> **⚠ Use a per-request stack.** `createStack()` returns a fresh instance. `livePreviewQuery()` mutates the stack's internal state — calling it on a shared module-level stack leaks preview context across concurrent requests (editor A sees editor B's drafts under load). Always call `createStack()` inside the request handler.

### Server Component (Page)

```typescript
// app/[slug]/page.tsx
import contentstack from "@contentstack/delivery-sdk";
import { createStack } from "@/lib/contentstack";

interface PageProps {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{
    live_preview?: string;
    entry_uid?: string;
    content_type_uid?: string;
  }>;
}

export default async function Page({ params, searchParams }: PageProps) {
  const { slug } = await params;              // Next.js 15+: await (sync in Next.js 14)
  const { live_preview, entry_uid, content_type_uid } = await searchParams;

  const stack = createStack();                // fresh per request — critical for SSR preview

  if (live_preview) {
    stack.livePreviewQuery({
      live_preview,
      contentTypeUid: content_type_uid || "page",
      entryUid: entry_uid || "",
    });
  }

  const entry = await stack.contentType("page").entry(slug).fetch();
  contentstack.Utils.addEditableTags(entry, "page", true);

  return (
    <main>
      <h1 {...(entry?.$ && entry?.$.title)}>{entry.title}</h1>
      <p {...(entry?.$ && entry?.$.description)}>{entry.description}</p>
    </main>
  );
}
```

**Next.js 15+ note:** `params` and `searchParams` are async Promises — `await` them. On Next.js 14 they are sync objects. Copy-pasting Next.js 15 patterns into a Next.js 14 project causes an "await is only valid in async functions" error or silent undefined behavior.

### Client Component (SDK Init)

```typescript
// components/LivePreviewProvider.tsx
"use client";
import { useEffect } from "react";
import { initLivePreview } from "@/lib/contentstack";

export function LivePreviewProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    initLivePreview(true); // iframe refresh mode - CMS adds query params
  }, []);

  return <>{children}</>;
}
```

### Layout

```typescript
// app/layout.tsx
import { LivePreviewProvider } from "@/components/LivePreviewProvider";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body>
        <LivePreviewProvider>{children}</LivePreviewProvider>
      </body>
    </html>
  );
}
```

---

## Fetching Patterns

### Get Entry by URL

```typescript
// lib/contentstack.ts
import contentstack, { QueryOperation } from "@contentstack/delivery-sdk";

export async function getPageByUrl(url: string) {
  const result = await stack
    .contentType("page")
    .entry()
    .query()
    .where("url", QueryOperation.EQUALS, url)
    .find();

  const entry = result.entries?.[0];
  if (entry) {
    contentstack.Utils.addEditableTags(entry, "page", true);
  }
  return entry || null;
}
```

### Get Blog Posts with Pagination

**Note**: `includeReference()` is on `entry()`, before `.query()`. Sorting uses `orderByDescending`, not `descending`.

```typescript
export async function getBlogPosts(page: number = 1, pageSize: number = 10) {
  const skip = (page - 1) * pageSize;

  const result = await stack
    .contentType("blog_post")
    .entry()
    .includeReference(["author"])    // before .query()
    .query()
    .skip(skip)
    .limit(pageSize)
    .includeCount()
    .orderByDescending("published_date")  // not .descending()
    .find();

  return {
    posts: result.entries,
    pagination: {
      currentPage: page,
      totalPages: Math.ceil(result.count / pageSize),
      totalEntries: result.count,
    },
  };
}
```

---

## Modular Blocks

```typescript
// components/BlockRenderer.tsx
import { HeroBlock } from "./blocks/HeroBlock";
import { ContentBlock } from "./blocks/ContentBlock";
import { CTABlock } from "./blocks/CTABlock";

interface Block {
  block: {
    _content_type_uid: string;
    [key: string]: any;
  };
  _metadata: { uid: string };
}

export function BlockRenderer({ blocks }: { blocks: Block[] }) {
  return (
    <>
      {blocks?.map((item) => {
        const blockType = item.block._content_type_uid;

        switch (blockType) {
          case "hero_block":
            return <HeroBlock key={item._metadata.uid} block={item.block} />;
          case "content_block":
            return <ContentBlock key={item._metadata.uid} block={item.block} />;
          case "cta_block":
            return <CTABlock key={item._metadata.uid} block={item.block} />;
          default:
            return null;
        }
      })}
    </>
  );
}
```

---

## Image Optimization

```typescript
// components/ContentstackImage.tsx
import Image from "next/image";

interface Asset {
  url: string;
  title?: string;
  filename: string;
  dimension?: { width: number; height: number };
}

export function ContentstackImage({
  asset,
  width,
  height,
  className,
}: {
  asset: Asset;
  width?: number;
  height?: number;
  className?: string;
}) {
  // Add Contentstack image params
  const src =
    width || height
      ? `${asset.url}?${width ? `width=${width}` : ""}${
          height ? `&height=${height}` : ""
        }`
      : asset.url;

  return (
    <Image
      src={src}
      alt={asset.title || asset.filename}
      width={width || asset.dimension?.width || 800}
      height={height || asset.dimension?.height || 600}
      className={className}
    />
  );
}
```

---

## TypeScript Types

```typescript
// types/contentstack.ts
import { Entry } from "@contentstack/delivery-sdk";

export interface Asset {
  uid: string;
  url: string;
  title: string;
  filename: string;
  dimension?: { width: number; height: number };
}

export interface PageEntry extends Entry {
  title: string;
  url: string;
  description?: string;
  featured_image?: Asset;
  blocks?: Array<{
    block: any;
    _metadata: { uid: string };
  }>;
  $?: Record<string, any>;
}

export interface BlogPost extends Entry {
  title: string;
  url: string;
  excerpt: string;
  content: string;
  published_date: string;
  author?: Author;
  featured_image?: Asset;
  $?: Record<string, any>;
}

export interface Author extends Entry {
  name: string;
  bio: string;
  avatar?: Asset;
}
```

---

## Next.js Config

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.contentstack.io",
      },
      {
        protocol: "https",
        hostname: "**.contentstack.com",
      },
    ],
  },
};

export default nextConfig;
```

---

## ISR & Draft Mode

For production pages you usually want **cached production content** that invalidates on publish. Use `fetch` tags + `revalidateTag` for that, and use **Next.js Draft Mode** for editor previews that opt into fresh drafts.

### Cache + on-demand revalidation via webhooks

Tag every Contentstack fetch so a webhook can invalidate the right entries:

```typescript
// lib/contentstack.ts — server-only fetch with tags
export async function fetchPageByUrl(url: string) {
  // Contentstack REST example — same idea with SDK, tag through a thin wrapper.
  const res = await fetch(
    `https://cdn.contentstack.io/v3/content_types/page/entries?query={"url":"${url}"}&environment=${process.env.CONTENTSTACK_ENVIRONMENT}`,
    {
      headers: {
        api_key: process.env.CONTENTSTACK_API_KEY!,
        access_token: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
      },
      next: { tags: [`page:${url}`, "page:all"] },
    },
  );
  return res.json();
}
```

Then the webhook receiver revalidates the tag when an entry publishes:

```typescript
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { verifyContentstackSignature } from "@/lib/verify";

export async function POST(req: Request) {
  const raw = await req.text();
  if (!verifyContentstackSignature(raw, req.headers.get("x-contentstack-signature"))) {
    return new Response("invalid signature", { status: 401 });
  }
  const payload = JSON.parse(raw);
  const url = payload?.data?.entry?.url;
  if (url) revalidateTag(`page:${url}`);
  revalidateTag("page:all");
  return Response.json({ ok: true });
}
```

See `../workflows/webhooks.md` for signature verification and release-storm debouncing.

### Draft Mode for editor previews

`draftMode()` lets editors opt into uncached fetches. Wire it to the preview button in Contentstack:

```typescript
// app/api/draft/route.ts
import { draftMode } from "next/headers";
import { redirect } from "next/navigation";

export async function GET(req: Request) {
  const token = new URL(req.url).searchParams.get("token");
  const redirectTo = new URL(req.url).searchParams.get("redirect") ?? "/";
  if (token !== process.env.DRAFT_MODE_TOKEN) {
    return new Response("unauthorized", { status: 401 });
  }
  (await draftMode()).enable();
  redirect(redirectTo);
}
```

```typescript
// In a server component: skip the cache when draft mode is on
import { draftMode } from "next/headers";

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { isEnabled: isDraft } = await draftMode();

  const res = await fetch(someUrl, {
    cache: isDraft ? "no-store" : "force-cache",
    next: isDraft ? undefined : { tags: [`page:${slug}`] },
  });
  // ...
}
```

Live Preview and Draft Mode compose: Draft Mode gets you fresh content on the server, Live Preview layers real-time updates on top via the preview hash.

---

## Visual Builder (`mode: "builder"`)

Visual Builder extends Live Preview with inline editing, drag-and-drop reordering of multiple fields, and a visual editing UI inside the CMS. It uses `ssr: true` mode (iframe refresh) and requires specific setup.

### Prerequisites

1. Content types that should be visually editable **must** have a `url` field (`is_page: true`). Visual Builder uses this field to match the iframe URL to the correct entry.
2. Environment variables must be split: server-only vars for data fetching, `NEXT_PUBLIC_` vars for client-side SDK init.

```bash
# Server-side only
CONTENTSTACK_API_KEY=your_api_key
CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token
CONTENTSTACK_PREVIEW_TOKEN=your_preview_token
CONTENTSTACK_ENVIRONMENT=production
CONTENTSTACK_REGION=us

# Client-side (for Visual Builder SDK init)
NEXT_PUBLIC_CONTENTSTACK_API_KEY=your_api_key
NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT=production
NEXT_PUBLIC_CONTENTSTACK_REGION=us
```

### Client Component — SDK Init

**Important**: The client component must create its own stack using `NEXT_PUBLIC_` env vars. Do NOT import the server-side `createStack()` — server-only env vars are not available in client bundles.

```typescript
// components/ContentstackVisualBuilder.tsx
"use client";

import { useEffect } from "react";
import contentstack from "@contentstack/delivery-sdk";
import ContentstackLivePreview from "@contentstack/live-preview-utils";
import type { IStackSdk } from "@contentstack/live-preview-utils";

export default function ContentstackVisualBuilder() {
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
      mode: "builder",  // "builder" for Visual Builder, "preview" for Live Preview
      stackSdk: stack.config as unknown as IStackSdk,
      stackDetails: {
        apiKey: process.env.NEXT_PUBLIC_CONTENTSTACK_API_KEY!,
        environment: process.env.NEXT_PUBLIC_CONTENTSTACK_ENVIRONMENT!,
      },
      editButton: { enable: true },
      cleanCslpOnProduction: true,
    });
  }, []);

  return null;
}
```

### Add to Layout

```typescript
// app/layout.tsx
import ContentstackVisualBuilder from "@/components/ContentstackVisualBuilder";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ContentstackVisualBuilder />
        {children}
      </body>
    </html>
  );
}
```

### Server-Side: Handle Preview Params

Pages must read `searchParams` and pass them to your data-fetching functions. Create a new stack per preview request.

```typescript
// app/[slug]/page.tsx
import contentstack from "@contentstack/delivery-sdk";
import { createStack } from "@/lib/contentstack";

interface PageProps {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{
    live_preview?: string;
    entry_uid?: string;
    content_type_uid?: string;
  }>;
}

export default async function Page({ params, searchParams }: PageProps) {
  const [{ slug }, { live_preview, entry_uid, content_type_uid }] =
    await Promise.all([params, searchParams]);

  // New stack per preview request
  const stack = live_preview ? createStack() : defaultStack;

  if (live_preview) {
    stack.livePreviewQuery({
      live_preview,
      contentTypeUid: content_type_uid || "page",
      entryUid: entry_uid || "",
    });
  }

  const result = await stack
    .contentType("page")
    .entry()
    .query()
    .where("url", QueryOperation.EQUALS, `/pages/${slug}`)
    .find();

  const entry = result.entries?.[0];
  if (entry) {
    contentstack.Utils.addEditableTags(entry, "page", true, "en-us");
  }

  return (
    <main>
      <h1 {...(entry?.$ && entry.$.title)}>{entry.title}</h1>
      <p {...(entry?.$ && entry.$.description)}>{entry.description}</p>
    </main>
  );
}
```

### Edit Tags for Multiple Fields (Reorder Support)

For multiple group fields (arrays), Visual Builder supports add, delete, and reorder when you tag both the container and each item using the `field__${index}` pattern on the **parent entry's** `$` object.

```typescript
// entry.$ contains edit tags from addEditableTags()
// Container: tag with entry.$.field_name
// Each item: tag with entry.$[`field_name__${index}`]

export function BlockList({ blocks, editTags }) {
  return (
    <div {...(editTags && editTags.blocks)}>
      {blocks.map((block, index) => (
        <div
          key={index}
          {...(editTags && editTags[`blocks__${index}`])}
        >
          <h3 {...(block.$ && block.$.title)}>{block.title}</h3>
          <p {...(block.$ && block.$.description)}>{block.description}</p>
        </div>
      ))}
    </div>
  );
}
```

**Important**: The item-level tag uses `editTags[`field__${index}`]` from the **parent entry's** `$`, NOT `item.$._`.

### URL Field Requirement

Visual Builder identifies which entry to load by matching the iframe URL against the entry's `url` field. Content types used with Visual Builder **must**:

1. Have `is_page: true` in options
2. Include a `url` field in the schema
3. Have the `url` populated on every entry (e.g., `/dogs/biscuit-golden-retriever`)
4. Query entries by `url` field, not a custom slug field

---

## Troubleshooting

### Hydration Errors

Ensure client components are properly marked with `"use client"` directive.

### Preview Not Working

1. Check HTTPS is enabled
2. Verify preview token is correct
3. Ensure site allows iframe embedding
4. Check `searchParams` is awaited (Next.js 15+)

### Images Not Loading

Add Contentstack domains to `next.config.ts` image configuration.
