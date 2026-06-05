# Contentstack with Nuxt 4

Complete patterns for Nuxt 4 with Contentstack and Live Preview.

## Installation

```bash
npm install @contentstack/delivery-sdk @contentstack/live-preview-utils
```

## Plugin Setup

```typescript
// plugins/contentstack.ts
import contentstack from "@contentstack/delivery-sdk";
import ContentstackLivePreview, { type IStackSdk } from "@contentstack/live-preview-utils";

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig();

  const stack = contentstack.stack({
    apiKey: config.public.contentstackApiKey,
    deliveryToken: config.public.contentstackDeliveryToken,
    environment: config.public.contentstackEnvironment,
    region: "us",
    live_preview: {
      enable: true,
      preview_token: config.public.contentstackPreviewToken,
      host: "rest-preview.contentstack.com",
    },
  });

  // Initialize Live Preview on client side only
  // ssr: false = postMessage updates, client re-fetches via onEntryChange()
  // ssr: true = iframe refresh with query params, server reads them
  if (import.meta.client) {
    ContentstackLivePreview.init({
      ssr: false, // false: instant updates via postMessage, true: iframe refresh
      enable: true,
      mode: "preview",
      stackSdk: stack.config as IStackSdk,
      stackDetails: {
        apiKey: config.public.contentstackApiKey,
        environment: config.public.contentstackEnvironment,
      },
      editButton: { enable: true },
    });
  }

  return {
    provide: {
      stack,
      ContentstackLivePreview,
    },
  };
});
```

## Environment Variables

```bash
# .env
NUXT_PUBLIC_CONTENTSTACK_API_KEY=your_api_key
NUXT_PUBLIC_CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token
NUXT_PUBLIC_CONTENTSTACK_PREVIEW_TOKEN=your_preview_token
NUXT_PUBLIC_CONTENTSTACK_ENVIRONMENT=preview
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      contentstackApiKey: "",
      contentstackDeliveryToken: "",
      contentstackPreviewToken: "",
      contentstackEnvironment: "",
    },
  },
});
```

---

## `ssr: false` Pattern (PostMessage Updates)

Best for: Pages that can re-fetch data client-side. Preview updates instantly without iframe refresh.

```vue
<!-- pages/index.vue -->
<script setup lang="ts">
import contentstack from "@contentstack/delivery-sdk";

const { $stack, $ContentstackLivePreview } = useNuxtApp();
const route = useRoute();

const { data: page, refresh } = await useAsyncData("home", async () => {
  // Apply preview query if hash exists
  if (route.query.live_preview) {
    $stack.livePreviewQuery(route.query);
  }

  const entry = await $stack.contentType("page").entry("home").fetch();
  contentstack.Utils.addEditableTags(entry, "page", true);
  return entry;
});

// Handle live preview updates (client-side only)
onMounted(() => {
  $ContentstackLivePreview.onEntryChange(refresh);
});
</script>

<template>
  <main v-if="page">
    <h1 v-bind="page?.$ && page?.$.title">{{ page.title }}</h1>
    <p v-bind="page?.$ && page?.$.description">{{ page.description }}</p>
  </main>
</template>
```

---

## `ssr: true` Pattern (Iframe Refresh)

For iframe refresh mode where CMS adds query params to the URL:

```typescript
// plugins/contentstack.ts (iframe refresh version)
if (import.meta.client) {
  ContentstackLivePreview.init({
    ssr: true, // CMS refreshes iframe with ?live_preview=hash&entry_uid=...
    enable: true,
    mode: "preview",
    stackSdk: stack.config as IStackSdk,
    stackDetails: {
      apiKey: config.public.contentstackApiKey,
      environment: config.public.contentstackEnvironment,
    },
    editButton: { enable: true },
  });
}
```

Then remove the `onMounted` handler from your pages (iframe will refresh with query params instead).

---

## Dynamic Pages

```vue
<!-- pages/[...slug].vue -->
<script setup lang="ts">
import contentstack, { QueryOperation } from "@contentstack/delivery-sdk";

const { $stack, $ContentstackLivePreview } = useNuxtApp();
const route = useRoute();

const { data: page, refresh } = await useAsyncData(
  `page-${route.params.slug}`,
  async () => {
    const slug = Array.isArray(route.params.slug) 
      ? "/" + route.params.slug.join("/") 
      : "/" + route.params.slug;

    // Apply preview query
    if (route.query.live_preview) {
      $stack.livePreviewQuery(route.query);
    }

    const result = await $stack
      .contentType("page")
      .entry()
      .query()
      .where("url", QueryOperation.EQUALS, slug)
      .find();

    const entry = result.entries[0];
    if (entry) {
      contentstack.Utils.addEditableTags(entry, "page", true);
    }
    return entry;
  }
);

onMounted(() => {
  $ContentstackLivePreview.onEntryChange(refresh);
});
</script>

<template>
  <main v-if="page">
    <h1 v-bind="page?.$ && page?.$.title">{{ page.title }}</h1>
  </main>
  <div v-else>Page not found</div>
</template>
```

---

## Composables

### useContentstack

```typescript
// composables/useContentstack.ts
import contentstack, { QueryOperation } from "@contentstack/delivery-sdk";

export function useContentstack() {
  const { $stack } = useNuxtApp();

  async function getPageByUrl(url: string) {
    const result = await $stack
      .contentType("page")
      .entry()
      .query()
      .where("url", QueryOperation.EQUALS, url)
      .find();

    const entry = result.entries[0];
    if (entry) {
      contentstack.Utils.addEditableTags(entry, "page", true);
    }
    return entry;
  }

  async function getBlogPosts(options?: { limit?: number; skip?: number }) {
    const query = $stack
      .contentType("blog_post")
      .entry()
      .includeReference(["author"])
      .query();

    if (options?.limit) query.limit(options.limit);
    if (options?.skip) query.skip(options.skip);

    const result = await query
      .includeCount()
      .orderByDescending("published_date")
      .find();

    result.entries.forEach((entry: any) => {
      contentstack.Utils.addEditableTags(entry, "blog_post", true);
    });

    return result;
  }

  return {
    getPageByUrl,
    getBlogPosts,
    stack: $stack,
  };
}
```

### Usage

```vue
<script setup lang="ts">
const { getBlogPosts } = useContentstack();

const { data: posts } = await useAsyncData("blog-posts", () =>
  getBlogPosts({ limit: 10 })
);
</script>
```

---

## Modular Blocks

```vue
<!-- components/BlockRenderer.vue -->
<script setup lang="ts">
import HeroBlock from "./blocks/HeroBlock.vue";
import ContentBlock from "./blocks/ContentBlock.vue";
import CTABlock from "./blocks/CTABlock.vue";

defineProps<{
  blocks: Array<{
    block: { _content_type_uid: string; [key: string]: any };
    _metadata: { uid: string };
  }>;
}>();

const blockComponents: Record<string, any> = {
  hero_block: HeroBlock,
  content_block: ContentBlock,
  cta_block: CTABlock,
};
</script>

<template>
  <template v-for="item in blocks" :key="item._metadata.uid">
    <component
      :is="blockComponents[item.block._content_type_uid]"
      v-if="blockComponents[item.block._content_type_uid]"
      :block="item.block"
    />
  </template>
</template>
```

---

## Image Component

```vue
<!-- components/ContentstackImage.vue -->
<script setup lang="ts">
interface Asset {
  url: string;
  title?: string;
  filename: string;
  dimension?: { width: number; height: number };
}

const props = defineProps<{
  asset: Asset;
  width?: number;
  height?: number;
  class?: string;
}>();

const src = computed(() => {
  const params = new URLSearchParams();
  if (props.width) params.append("width", props.width.toString());
  if (props.height) params.append("height", props.height.toString());
  
  return params.toString() 
    ? `${props.asset.url}?${params.toString()}` 
    : props.asset.url;
});
</script>

<template>
  <NuxtImg
    :src="src"
    :alt="asset.title || asset.filename"
    :width="width || asset.dimension?.width"
    :height="height || asset.dimension?.height"
    :class="props.class"
  />
</template>
```

---

## TypeScript Types

```typescript
// types/contentstack.d.ts
import type { Entry } from "@contentstack/delivery-sdk";

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
  $?: Record<string, any>;
}

export interface BlogPost extends Entry {
  title: string;
  url: string;
  excerpt: string;
  content: string;
  published_date: string;
  author?: Author;
  $?: Record<string, any>;
}

export interface Author extends Entry {
  name: string;
  bio: string;
  avatar?: Asset;
}
```

---

## Troubleshooting

### Plugin Not Loading

Ensure plugin file is in `plugins/` directory and TypeScript is configured.

### Preview Not Working

1. Check HTTPS is enabled
2. Verify preview token in runtime config
3. Ensure site allows iframe embedding
4. Check route.query contains live_preview hash

### Hydration Mismatches

Wrap client-only logic in `onMounted` or use `<ClientOnly>` component.
