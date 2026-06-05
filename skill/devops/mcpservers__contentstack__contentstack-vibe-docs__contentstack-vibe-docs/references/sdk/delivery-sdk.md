# Contentstack Delivery SDK

Complete guide to using the TypeScript Delivery SDK (`@contentstack/delivery-sdk`).

## Installation

```bash
npm install @contentstack/delivery-sdk
```

## Stack Initialization

### Basic Configuration

```typescript
import contentstack from "@contentstack/delivery-sdk";

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: "us", // or "eu", "au", "azure-na", "azure-eu", "gcp-na", "gcp-eu"
});
```

### With Live Preview

> **⚠ Security:** only use a **Preview Token** for `live_preview.preview_token`. Never use a Management Token — that's a read/write credential and putting it in a client-exposed stack config is a serious leak. See `../security/tokens-authentication.md` for the full decision tree.

> **⚠ Region-aware host:** the `host` below is **US-only**. EU, AU, Azure, and GCP regions each have their own preview host. Hardcoding `rest-preview.contentstack.com` breaks preview on every non-US stack. Resolve via `@timbenniks/contentstack-endpoints` (preferred) or see the region table in `../concepts/regions.md`.

```typescript
import contentstack from "@contentstack/delivery-sdk";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

const region = process.env.CONTENTSTACK_REGION || "us";
const endpoints = getContentstackEndpoints(region, true); // omitHttps: true

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region,
  live_preview: {
    enable: true,
    preview_token: process.env.CONTENTSTACK_PREVIEW_TOKEN,
    host: endpoints.preview,       // region-aware
  },
});
```

**Important**: For SSR Live Preview (`ssr: true`) or Visual Builder, create a **new stack instance per request** to avoid cross-session data leakage. Use a factory function:

```typescript
export function createStack() {
  return contentstack.stack({
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
}
```

### Using Endpoints Package (Recommended)

The `@timbenniks/contentstack-endpoints` package (v2.1.0+) automatically resolves correct endpoints for all regions:

```bash
npm install @timbenniks/contentstack-endpoints
```

**Simple approach** (recommended):

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

**With region validation** (if you need explicit type checking):

```typescript
import contentstack from "@contentstack/delivery-sdk";
import {
  getContentstackEndpoints,
  getRegionForString,
} from "@timbenniks/contentstack-endpoints";

const region = getRegionForString(process.env.CONTENTSTACK_REGION || "us");
// omitHttps: true removes https:// prefix (needed for SDK host parameter)
const endpoints = getContentstackEndpoints(region, true);

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: region,
  live_preview: {
    enable: true,
    preview_token: process.env.CONTENTSTACK_PREVIEW_TOKEN,
    host: endpoints.preview, // Already without https://
  },
});
```

**Available endpoint properties:**

- `endpoints.contentDelivery` - REST CDN endpoint
- `endpoints.contentManagement` - Management API endpoint
- `endpoints.graphqlDelivery` - GraphQL endpoint
- `endpoints.preview` - REST Preview endpoint
- `endpoints.graphqlPreview` - GraphQL Preview endpoint

**Note**: When `omitHttps: true` is passed, all endpoints return domains without `https://` prefix, which is what SDKs expect for the `host` parameter.

See [Regions Guide](../concepts/regions.md) for complete region configuration details.

## Fetching Entries

### Single Entry by UID

```typescript
const entry = await stack.contentType("blog_post").entry("entry_uid").fetch();
```

### With Locale

```typescript
const entry = await stack
  .contentType("blog_post")
  .entry("entry_uid")
  .language("fr-fr")
  .fetch();
```

### With References

**Important**: `includeReference()` is called on `entry()`, before `.query()` or `.fetch()`.

```typescript
const entry = await stack
  .contentType("blog_post")
  .entry("entry_uid")
  .includeReference(["author", "category"])
  .fetch();

// Access referenced entries
console.log(entry.author.title);
console.log(entry.category.title);
```

When querying multiple entries with references:

```typescript
const result = await stack
  .contentType("blog_post")
  .entry()
  .includeReference(["author"])  // before .query()
  .query()
  .find();
```

### Multiple Entries

```typescript
const result = await stack.contentType("blog_post").entry().query().find();

console.log(result.entries); // Array of entries
console.log(result.count); // Total count (if includeCount() was called)
```

## Query Building

### Basic Query

```typescript
const result = await stack.contentType("blog_post").entry().query().find();
```

### Filtering with Where

```typescript
import { QueryOperation } from "@contentstack/delivery-sdk";

const result = await stack
  .contentType("blog_post")
  .entry()
  .query()
  .where("title", QueryOperation.EQUALS, "My Post")
  .find();
```

### Multiple Conditions (AND)

```typescript
const result = await stack
  .contentType("blog_post")
  .entry()
  .query()
  .where("category", QueryOperation.EQUALS, "tech")
  .where("published_date", QueryOperation.IS_LESS_THAN_OR_EQUAL, "2024-01-01")
  .find();
```

### Complex Queries

```typescript
const result = await stack
  .contentType("blog_post")
  .entry()
  .query()
  .addQuery({
    $or: [
      { category: { $in: ["tech", "design"] } },
      { tags: { $regex: "javascript", $options: "i" } },
    ],
  })
  .find();
```

### Query Operations

```typescript
import { QueryOperation } from "@contentstack/delivery-sdk";

QueryOperation.EQUALS;                    // ==
QueryOperation.NOT_EQUALS;                // != (note: NOT_EQUALS, not NOT_EQUAL)
QueryOperation.IS_GREATER_THAN;           // >
QueryOperation.IS_GREATER_THAN_OR_EQUAL;  // >=
QueryOperation.IS_LESS_THAN;              // <
QueryOperation.IS_LESS_THAN_OR_EQUAL;     // <=
QueryOperation.INCLUDES;                  // in array
QueryOperation.EXCLUDES;                  // not in array
QueryOperation.EXISTS;                    // field exists
QueryOperation.MATCHES;                   // regex match
```

The query object also has convenience methods that can be chained:

```typescript
query.equalTo("field", value);
query.notEqualTo("field", value);
query.lessThan("field", value);
query.greaterThan("field", value);
query.containedIn("field", [values]);
query.notContainedIn("field", [values]);
query.exists("field");
query.notExists("field");
```

### Sorting

**Important**: The methods are `orderByAscending` and `orderByDescending` (not `ascending`/`descending`).

```typescript
// Ascending
.orderByAscending("published_date")

// Descending
.orderByDescending("published_date")

// Multiple
.orderByAscending("category").orderByDescending("published_date")
```

### Pagination

```typescript
const result = await stack
  .contentType("blog_post")
  .entry()
  .query()
  .skip(0)
  .limit(10)
  .includeCount()
  .find();

// result.entries.length = current page
// result.count = total matching entries
```

### Field Selection

```typescript
// Only specific fields
.only(["title", "url", "published_date"])

// Exclude fields
.except(["internal_notes", "draft_content"])
```

## Working with Assets

```typescript
// Fetch single asset
const asset = await stack.asset("asset_uid").fetch();
console.log(asset.url, asset.title, asset.filename);

// Query assets
const result = await stack
  .asset()
  .query()
  .where("content_type", QueryOperation.EQUALS, "image/jpeg")
  .find();
```

## TypeScript Support

```typescript
import contentstack, { Entry } from "@contentstack/delivery-sdk";

interface BlogPost extends Entry {
  title: string;
  url: string;
  content: string;
  author: Author;
  published_date: string;
}

interface Author extends Entry {
  name: string;
  bio: string;
  avatar?: Asset;
}

interface Asset {
  uid: string;
  url: string;
  title: string;
  filename: string;
  dimension?: { width: number; height: number };
}

// Type-safe fetch
const result = await stack.contentType("blog_post").entry().query().find();
const entries = result.entries as BlogPost[];
```

## Error Handling

```typescript
try {
  const entry = await stack.contentType("blog_post").entry("entry_uid").fetch();
  return entry;
} catch (error) {
  if (error instanceof Error) {
    console.error("Error fetching entry:", error.message);
  }
  return null;
}
```

## Live Preview Integration

### Apply Live Preview Query (`ssr: true` mode)

When using `ssr: true`, the CMS refreshes the iframe with query params. Read them and apply:

```typescript
// CMS adds: ?live_preview=hash&entry_uid=...&content_type_uid=...
const { live_preview, entry_uid, content_type_uid } = searchParams;

if (live_preview) {
  stack.livePreviewQuery({
    live_preview,
    contentTypeUid: content_type_uid || "blog_post",
    entryUid: entry_uid || "",
  });
}

const entry = await stack.contentType("blog_post").entry("entry_uid").fetch();
```

### Add Editable Tags

```typescript
import contentstack from "@contentstack/delivery-sdk";

const entry = await stack.contentType("blog_post").entry("entry_uid").fetch();

// Add editable tags for Live Preview
contentstack.Utils.addEditableTags(entry, "blog_post", true, "en-us");

// In JSX:
<h1 {...(entry?.$ && entry?.$.title)}>{entry.title}</h1>;
```

## Advanced Configuration

### Custom Headers

```typescript
const stack = contentstack.stack({
  // ... basic config
  headers: {
    "X-Custom-Header": "custom-value",
  },
});
```

### Retry Configuration

```typescript
const stack = contentstack.stack({
  // ... basic config
  retryOptions: {
    retryDelayOptions: { base: 1000 },
    maxRetries: 3,
  },
});
```

## Helper Functions Pattern

```typescript
// lib/contentstack.ts
import contentstack, { QueryOperation } from "@contentstack/delivery-sdk";

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: "us",
});

export async function getEntryByUrl(contentType: string, url: string) {
  const result = await stack
    .contentType(contentType)
    .entry()
    .query()
    .where("url", QueryOperation.EQUALS, url)
    .find();
  return result.entries[0] || null;
}

export async function getEntries(
  contentType: string,
  options?: {
    limit?: number;
    skip?: number;
    references?: string[];
  }
) {
  const query = stack.contentType(contentType).entry().query();

  if (options?.limit) query.limit(options.limit);
  if (options?.skip) query.skip(options.skip);
  if (options?.references) {
    // Note: includeReference is on entry(), not query()
    // For queries with references, call it before .query()
  }

  return query.includeCount().find();
}
```

## Best Practices

1. **Create single stack instance** - Reuse across your application
2. **Use environment variables** - Never hardcode credentials
3. **Handle errors gracefully** - Wrap API calls in try-catch
4. **Use TypeScript** - Define interfaces for type safety
5. **Include only needed references** - Keep includes under 10
6. **Implement pagination** - Don't fetch all entries at once
7. **Chain order matters** - `includeReference()` goes on `entry()` before `.query()`, sorting/pagination go on `.query()`
