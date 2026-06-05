# Practical Examples

Real-world implementation patterns for Contentstack. All examples assume you've created a shared stack instance.

## Shared Stack Instance

```typescript
// lib/contentstack.ts - Import this in all examples
import contentstack from "@contentstack/delivery-sdk";

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: process.env.CONTENTSTACK_REGION || "us",
});
```

---

## Rendering Rich Text

### React

```typescript
import DOMPurify from "isomorphic-dompurify";

function RichText({ content }: { content: string }) {
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: DOMPurify.sanitize(content),
      }}
    />
  );
}
```

### Vue

```vue
<script setup>
import DOMPurify from "dompurify";
const props = defineProps<{ content: string }>();
const sanitized = computed(() => DOMPurify.sanitize(props.content));
</script>

<template>
  <div v-html="sanitized"></div>
</template>
```

---

## Working with References

### Single Reference

```typescript
import { stack } from "@/lib/contentstack";

const entry = await stack
  .contentType("blog_post")
  .entry("entry_uid")
  .includeReference(["author"])
  .fetch();

// Access
console.log(entry.author.name);
```

### Multiple References

```typescript
const entry = await stack
  .contentType("blog_post")
  .entry("entry_uid")
  .includeReference(["author", "category", "tags"])
  .fetch();
```

### Render Reference Array

```tsx
function RelatedPosts({ posts }: { posts: Post[] }) {
  return (
    <ul>
      {posts?.map((post) => (
        <li key={post.uid}>
          <a href={post.url}>{post.title}</a>
        </li>
      ))}
    </ul>
  );
}
```

---

## Handling Modular Blocks

### Block Structure

Contentstack returns modular blocks as:

```typescript
{
  blocks: [
    { 
      hero_block: { title: "...", image: {...} }
    },
    { 
      content_block: { title: "...", body: "..." }
    }
  ]
}
```

### React Block Renderer

```tsx
function BlockRenderer({ blocks }: { blocks: any[] }) {
  return (
    <>
      {blocks?.map((item, index) => {
        if (item.hero_block) {
          return <HeroBlock key={index} data={item.hero_block} />;
        }
        if (item.content_block) {
          return <ContentBlock key={index} data={item.content_block} />;
        }
        if (item.cta_block) {
          return <CTABlock key={index} data={item.cta_block} />;
        }
        return null;
      })}
    </>
  );
}
```

### Block Components

```tsx
function HeroBlock({ data }: { data: HeroBlockData }) {
  return (
    <section className="hero">
      <h1>{data.title}</h1>
      {data.image && <img src={data.image.url} alt={data.title} />}
      {data.description && <p>{data.description}</p>}
    </section>
  );
}

function ContentBlock({ data }: { data: ContentBlockData }) {
  return (
    <section className="content">
      <h2>{data.title}</h2>
      <RichText content={data.body} />
    </section>
  );
}
```

---

## Asset Transformations

### Transform Function

```typescript
interface TransformOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: "auto" | "webp" | "jpeg" | "png";
  fit?: "bounds" | "crop" | "pad";
}

function transformImage(url: string, options: TransformOptions): string {
  const params = new URLSearchParams();
  
  if (options.width) params.append("width", options.width.toString());
  if (options.height) params.append("height", options.height.toString());
  if (options.quality) params.append("quality", options.quality.toString());
  if (options.format) params.append("format", options.format);
  if (options.fit) params.append("fit", options.fit);

  return params.toString() ? `${url}?${params.toString()}` : url;
}

// Usage
const thumbnail = transformImage(asset.url, { width: 400, height: 300, fit: "crop" });
const optimized = transformImage(asset.url, { width: 800, format: "webp", quality: 85 });
```

### Responsive Image Component

```tsx
function ResponsiveImage({ asset }: { asset: Asset }) {
  const srcSet = [
    `${asset.url}?width=400 400w`,
    `${asset.url}?width=800 800w`,
    `${asset.url}?width=1200 1200w`,
  ].join(", ");

  return (
    <img
      src={asset.url}
      srcSet={srcSet}
      sizes="(max-width: 768px) 400px, (max-width: 1200px) 800px, 1200px"
      alt={asset.title || asset.filename}
    />
  );
}
```

---

## Common Patterns

### Blog Listing with Pagination

```typescript
import { stack } from "@/lib/contentstack";

async function getBlogPosts(page = 1, pageSize = 10) {
  const skip = (page - 1) * pageSize;

  const result = await stack
    .contentType("blog_post")
    .entry()
    .includeReference(["author"])
    .query()
    .skip(skip)
    .limit(pageSize)
    .includeCount()
    .orderByDescending("published_date")
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

### Get Entry by URL

```typescript
import { QueryOperation } from "@contentstack/delivery-sdk";
import { stack } from "@/lib/contentstack";

async function getPageByUrl(url: string) {
  const result = await stack
    .contentType("page")
    .entry()
    .query()
    .where("url", QueryOperation.EQUALS, url)
    .find();

  return result.entries[0] || null;
}
```

### Navigation Menu

```typescript
async function getNavigation() {
  const result = await stack
    .contentType("navigation_item")
    .entry()
    .query()
    .orderByAscending("order")
    .find();

  return result.entries;
}
```

### Related Posts

```typescript
async function getRelatedPosts(currentUid: string, category: string) {
  const result = await stack
    .contentType("blog_post")
    .entry()
    .query()
    .where("category", QueryOperation.EQUALS, category)
    .addQuery({ uid: { $ne: currentUid } })
    .limit(3)
    .find();

  return result.entries;
}
```

---

## TypeScript Types

```typescript
import { Entry } from "@contentstack/delivery-sdk";

interface Asset {
  uid: string;
  url: string;
  title: string;
  filename: string;
  dimension?: { width: number; height: number };
}

interface BlogPost extends Entry {
  title: string;
  url: string;
  excerpt: string;
  content: string;
  published_date: string;
  featured_image?: Asset;
  author?: Author;
  category?: Category;
  tags?: Tag[];
}

interface Author extends Entry {
  name: string;
  bio: string;
  avatar?: Asset;
}

interface Page extends Entry {
  title: string;
  url: string;
  blocks?: ModularBlock[];
}

interface ModularBlock {
  hero_block?: HeroBlockData;
  content_block?: ContentBlockData;
  cta_block?: CTABlockData;
}
```

---

## Locale Handling

### Fetch in Specific Locale

```typescript
const entry = await stack
  .contentType("page")
  .entry("entry_uid")
  .language("fr-fr")
  .fetch();
```

### Locale Switcher

```tsx
const LOCALES = ["en-us", "fr-fr", "de-de"];

function LocaleSwitcher({ current }: { current: string }) {
  return (
    <select value={current} onChange={(e) => switchLocale(e.target.value)}>
      {LOCALES.map((locale) => (
        <option key={locale} value={locale}>
          {locale.toUpperCase()}
        </option>
      ))}
    </select>
  );
}
```

---

## Error Handling

### Safe Fetch Pattern

```typescript
async function safeFetch<T>(
  fetcher: () => Promise<T>
): Promise<{ data: T | null; error: string | null }> {
  try {
    const data = await fetcher();
    return { data, error: null };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("Contentstack fetch error:", message);
    return { data: null, error: message };
  }
}

// Usage
const { data: post, error } = await safeFetch(() =>
  stack.contentType("blog_post").entry("uid").fetch()
);

if (error) {
  return <ErrorMessage message={error} />;
}
```
