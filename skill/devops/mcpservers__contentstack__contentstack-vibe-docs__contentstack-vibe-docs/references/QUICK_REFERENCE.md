# Contentstack Quick Reference for AI Agents

Condensed patterns for common Contentstack operations. Use this for quick lookups.

## Routing Note

For content modeling, schema design, references vs modular blocks, global fields, taxonomy, or localization strategy, read [concepts/data-modeling-best-practices.md](concepts/data-modeling-best-practices.md) before this file. This quick reference is for implementation patterns after the model is already decided.

## Stack Initialization (Use Once)

### Basic (Manual Region)

```typescript
// lib/contentstack.ts - Import this everywhere, don't repeat
import contentstack from "@contentstack/delivery-sdk";

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: process.env.CONTENTSTACK_REGION || "us", // us, eu, au, azure-na, azure-eu, gcp-na, gcp-eu
  live_preview: {
    enable: true,
    preview_token: process.env.CONTENTSTACK_PREVIEW_TOKEN,
    host: "rest-preview.contentstack.com", // Manual - must match region!
  },
});
```

### With Endpoints Package (Recommended)

```typescript
import contentstack from "@contentstack/delivery-sdk";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

// omitHttps: true removes https:// prefix (needed for SDK host parameter)
const endpoints = getContentstackEndpoints(
  process.env.CONTENTSTACK_REGION || "us",
  true // omitHttps = true
);

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: process.env.CONTENTSTACK_REGION || "us",
  live_preview: {
    enable: true,
    preview_token: process.env.CONTENTSTACK_PREVIEW_TOKEN,
    host: endpoints.preview, // Already without https://
  },
});
```

---

## Fetching Entries

### Single Entry by UID

```typescript
const entry = await stack.contentType("blog_post").entry("entry_uid").fetch();
```

### Single Entry with References

**Important**: `includeReference()` is called on `entry()`, before `.query()` or `.fetch()`.

```typescript
const entry = await stack
  .contentType("blog_post")
  .entry("entry_uid")
  .includeReference(["author", "category"])
  .fetch();
```

### Entry by URL

```typescript
import { QueryOperation } from "@contentstack/delivery-sdk";

const result = await stack
  .contentType("page")
  .entry()
  .query()
  .where("url", QueryOperation.EQUALS, "/about")
  .find();

const entry = result.entries[0];
```

### Multiple Entries with Pagination

```typescript
const result = await stack
  .contentType("blog_post")
  .entry()
  .query()
  .skip(0)
  .limit(10)
  .includeCount()
  .orderByDescending("published_date")
  .find();

// result.entries = array of entries
// result.count = total count
```

### Entry in Specific Locale

```typescript
const entry = await stack
  .contentType("page")
  .entry("entry_uid")
  .language("fr-fr")
  .fetch();
```

---

## Query Operations

```typescript
import { QueryOperation } from "@contentstack/delivery-sdk";

// Equals
.where("status", QueryOperation.EQUALS, "published")

// Not equals (note: NOT_EQUALS, not NOT_EQUAL)
.where("status", QueryOperation.NOT_EQUALS, "draft")

// Greater/Less than (note: IS_ prefix)
.where("price", QueryOperation.IS_GREATER_THAN, 100)
.where("price", QueryOperation.IS_LESS_THAN_OR_EQUAL, 500)

// In array (note: INCLUDES/EXCLUDES, not IN/NOT_IN)
.where("category", QueryOperation.INCLUDES, ["tech", "design"])

// Regex match
.where("title", QueryOperation.MATCHES, "tutorial")

// Convenience methods (alternative to .where with QueryOperation)
query.equalTo("status", "published")
query.notEqualTo("status", "draft")
query.containedIn("category", ["tech", "design"])

// Complex query
.addQuery({
  $or: [
    { category: { $in: ["tech", "design"] } },
    { tags: { $regex: "javascript", $options: "i" } }
  ]
})
```

---

## Sorting

```typescript
// Ascending (note: orderByAscending, not ascending)
.orderByAscending("published_date")

// Descending (note: orderByDescending, not descending)
.orderByDescending("published_date")

// Multiple
.orderByAscending("category").orderByDescending("published_date")
```

---

## Field Selection

```typescript
// Only specific fields
.only(["title", "url", "published_date"])

// Exclude fields
.except(["internal_notes", "draft_content"])
```

---

## Live Preview

**Note**: Live Preview is for development/preview only. Never enabled in production.

### The `ssr` Setting

- `ssr: false` → Uses postMessage. Client re-fetches via `onEntryChange()`. No page refresh.
- `ssr: true` → CMS refreshes iframe with query params. Server reads params to fetch preview data.

### Initialize (Client-Side)

```typescript
import ContentstackLivePreview, {
  IStackSdk,
} from "@contentstack/live-preview-utils";

ContentstackLivePreview.init({
  ssr: false, // false: postMessage updates, true: iframe refresh with query params
  enable: true,
  stackSdk: stack.config as IStackSdk,
  stackDetails: {
    apiKey: process.env.CONTENTSTACK_API_KEY!,
    environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  },
  editButton: { enable: true },
});
```

### Handle Entry Changes (`ssr: false`)

```typescript
// CMS sends postMessage, SDK triggers this callback
ContentstackLivePreview.onEntryChange(async () => {
  const updated = await fetchData();
  setEntry(updated);
});
```

### Handle Query Params (`ssr: true`)

```typescript
// CMS refreshes iframe with: ?live_preview=hash&entry_uid=...&content_type_uid=...
// Read from URL and apply to stack
const { live_preview, entry_uid, content_type_uid } = searchParams;

if (live_preview) {
  stack.livePreviewQuery({
    live_preview,
    contentTypeUid: content_type_uid || "page",
    entryUid: entry_uid || "",
  });
}
```

### Add Editable Tags

```typescript
import contentstack from "@contentstack/delivery-sdk";

contentstack.Utils.addEditableTags(entry, "content_type_uid", true, "en-us");

// In JSX:
<h1 {...(entry?.$ && entry?.$.title)}>{entry.title}</h1>;
```

---

## Assets

### Fetch Asset

```typescript
const asset = await stack.asset("asset_uid").fetch();
console.log(asset.url, asset.title, asset.filename);
```

### Image Transformations

```typescript
// Resize
`${asset.url}?width=800&height=600&environment=production`

// WebP format with quality
`${asset.url}?format=webp&quality=85&environment=production`

// Crop to exact dimensions
`${asset.url}?width=400&height=300&fit=crop&environment=production`

// Cover (fill area, crop overflow)
`${asset.url}?width=400&height=300&fit=cover&environment=production`

// Auto-serve modern format with fallback
`${asset.url}?auto=avif&format=webp&quality=80&environment=production`

// Retina 2x
`${asset.url}?width=400&dpr=2&format=webp&environment=production`

// Aspect ratio crop
`${asset.url}?crop=16:9&environment=production`

// Grayscale
`${asset.url}?saturation=-100&environment=production`

// LQIP placeholder (tiny + blurred)
`${asset.url}?width=40&blur=20&quality=30&format=webp&environment=production`

// Prevent upscaling
`${asset.url}?width=1200&disable=upscale&environment=production`
```

See [Image Delivery API](api/image-delivery-api.md) for all parameters.

---

## Region Configuration

### Using Endpoints Package (Recommended)

```typescript
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

// omitHttps: true for SDKs (removes https:// prefix)
// omitHttps: false for direct API calls (includes https://)
const endpoints = getContentstackEndpoints("us", true); // or "eu", "au", "azure-na", etc.

// Available endpoints:
endpoints.contentDelivery; // REST CDN
endpoints.contentManagement; // Management API
endpoints.graphqlDelivery; // GraphQL
endpoints.preview; // REST Preview
endpoints.graphqlPreview; // GraphQL Preview
```

### Region Codes

| Code       | Full Name           | Aliases        |
| ---------- | ------------------- | -------------- |
| `us`       | AWS North America   | `na`, `aws-na` |
| `eu`       | AWS Europe          | `aws-eu`       |
| `au`       | AWS Australia       | `aws-au`       |
| `azure-na` | Azure North America | `azure_na`     |
| `azure-eu` | Azure Europe        | `azure_eu`     |
| `gcp-na`   | GCP North America   | `gcp_na`       |
| `gcp-eu`   | GCP Europe          | `gcp_eu`       |

See [Regions Guide](../concepts/regions.md) for complete details.

---

## TypeScript Types

```typescript
import { Entry } from "@contentstack/delivery-sdk";

interface BlogPost extends Entry {
  title: string;
  url: string;
  content: string;
  published_date: string;
  author?: Author;
  featured_image?: Asset;
}

interface Asset {
  uid: string;
  url: string;
  title: string;
  filename: string;
  dimension?: { width: number; height: number };
}
```

---

## Error Handling Pattern

```typescript
try {
  const entry = await stack.contentType("page").entry(uid).fetch();
  return entry;
} catch (error) {
  console.error(
    "Error fetching entry:",
    error instanceof Error ? error.message : error
  );
  return null;
}
```

---

## Content Management API (CRUD)

### Initialize Management SDK

```typescript
// lib/contentstack-management.ts
import * as contentstack from "@contentstack/management";

const client = contentstack.client();
export const stack = client.stack({
  api_key: process.env.CONTENTSTACK_API_KEY!,
  management_token: process.env.CONTENTSTACK_MANAGEMENT_TOKEN!,
});
```

### Create an Entry

```typescript
const entry = await stack.contentType("blog_post").entry().create({
  entry: {
    title: "My Post",
    url: "/blog/my-post",
    body: "<p>Hello world</p>",
  },
});
```

### Update an Entry

```typescript
const entry = await stack.contentType("blog_post").entry("blt1234567890").fetch();
entry.title = "Updated Title";
await entry.update();
```

### Publish an Entry

```typescript
await stack.contentType("blog_post").entry("blt1234567890").publish({
  entry: {
    environments: ["production"],
    locales: ["en-us"],
  },
});
```

### Delete an Entry

```typescript
await stack.contentType("blog_post").entry("blt1234567890").delete();
```

### Upload an Asset

```typescript
import * as fs from "fs";

const asset = await stack.asset().create({
  asset: {
    upload: fs.createReadStream("/path/to/image.jpg"),
    title: "Hero Image",
  },
});
```

### Bulk Publish

```typescript
await stack.bulkOperation().publish({
  entries: [
    { uid: "entry_uid_1", content_type: "blog_post", locale: "en-us" },
    { uid: "entry_uid_2", content_type: "blog_post", locale: "en-us" },
  ],
  locales: ["en-us"],
  environments: ["production"],
});
```

### REST API (curl)

```bash
# Create entry
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"entry": {"title": "My Post"}}'

# Publish entry
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries/ENTRY_UID/publish' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"entry": {"environments": ["production"], "locales": ["en-us"]}}'
```

See [Content Management API](api/content-management-api.md) for full reference.

---

## Webhooks — verify signature

```typescript
// app/api/webhooks/contentstack/route.ts
import { createHmac, timingSafeEqual } from "node:crypto";

export async function POST(req: Request) {
  const raw = await req.text();
  const sig = req.headers.get("x-contentstack-signature") ?? "";
  const secret = process.env.CONTENTSTACK_WEBHOOK_SECRET!;
  const expected = createHmac("sha256", secret).update(raw).digest("hex");
  const ok = sig.length === expected.length &&
    timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
  if (!ok) return new Response("invalid signature", { status: 401 });

  const payload = JSON.parse(raw);
  if (payload.source?.type === "release") {
    // Debounce release storms
    await debouncedTrigger(`release:${payload.source.uid}`);
  } else {
    await triggerOnce();
  }
  return new Response("ok", { status: 200 });
}
```

See [webhooks.md](workflows/webhooks.md) for release-storm handling and retry behavior.

---

## Releases — create and deploy (CMA sketch)

```typescript
// Create release, add items, deploy
async function deployCampaign(itemUids: string[]) {
  const release = await cma.post("/v3/releases", {
    release: { name: "Summer campaign", description: "2026-07-01 launch" },
  });
  await cma.post(`/v3/releases/${release.uid}/items`, {
    items: itemUids.map((uid) => ({ uid, content_type_uid: "page", locale: "en-us", version: null })),
  }); // max 100 items per call
  await cma.post(`/v3/releases/${release.uid}/deploy`, {
    environments: ["production"], locales: ["en-us"],
  });
}
```

See [releases.md](workflows/releases.md) for version-pinning gotchas.

---

## Branches — switch alias (zero-downtime)

```typescript
// SDK reads the alias from env; no code change to flip production
// .env
// CONTENTSTACK_BRANCH=deploy
//
// Reassign the `deploy` alias to a new branch via CMA to switch:
await cma.put("/v3/aliases/deploy", { alias: { target_branch: "release-2026-q2" } });
// Rollback: point it back
await cma.put("/v3/aliases/deploy", { alias: { target_branch: "main" } });
```

Always pass `branch` in SDK init and REST calls, even for `main`. See [branches-aliases.md](workflows/branches-aliases.md).

---

## Variants — fetch with resolved variant aliases

```typescript
import { Personalize } from "@contentstack/personalize-edge-sdk";

const personalize = Personalize.init(process.env.PERSONALIZE_PROJECT_UID!);
const variantAlias = await personalize.getVariantAliases({
  userUid: cookieUserUid,
  attributes: { country: "US", plan: "enterprise" },
});

const entry = await stack
  .contentType("landing_page")
  .entry(entryUid)
  .variants(variantAlias)          // SDK merges variant fields into the base entry
  .fetch();
```

See [variants-and-personalize.md](personalization/variants-and-personalize.md).

---

## Sync API — incremental content sync

```typescript
// First run: get everything + a sync_token
const init = await fetch(
  `https://cdn.contentstack.io/v3/stacks/sync?init=true&environment=${env}&content_type_uid=blog_post`,
  { headers: { api_key, access_token } },
).then((r) => r.json());

persist(init.sync_token);       // save for next run

// Subsequent runs: deltas only
const delta = await fetch(
  `https://cdn.contentstack.io/v3/stacks/sync?sync_token=${loadToken()}`,
  { headers: { api_key, access_token } },
).then((r) => r.json());
```

Prefer Sync over polling for SSG rebuilds. See [environments-publishing.md](workflows/environments-publishing.md).

---

## Environment Variables

```bash
# Content Delivery
CONTENTSTACK_API_KEY=your_api_key
CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token
CONTENTSTACK_PREVIEW_TOKEN=your_preview_token
CONTENTSTACK_ENVIRONMENT=production
CONTENTSTACK_REGION=us

# Content Management (server-side only)
CONTENTSTACK_MANAGEMENT_TOKEN=your_management_token
```
