# Visual Builder & Edit Tags

Visual Builder transforms a running website into an interactive editing surface. It sits on top of Live Preview: Live Preview delivers real-time content updates; Visual Builder adds click-to-field navigation and block controls (add/delete/reorder) powered by `data-cslp` edit tags.

This file covers edit tags, the `addEditableTags` utility, Visual Builder-specific features, GraphQL reshaping, and debugging.

## What edit tags do

From the CMS's perspective, your rendered HTML is opaque — it doesn't know which element maps to which field. Edit tags supply that mapping:

```html
<!-- Without edit tags: CMS has no idea which field this is -->
<h1>Welcome</h1>

<!-- With edit tags: click opens the exact field in the entry editor -->
<h1 data-cslp="page.blt80654132ff521260.en-us.title">Welcome</h1>
```

Your site renders correctly without edit tags. Adding them enables click-to-field and Visual Builder controls.

## Anatomy

```
data-cslp="{content_type_uid}.{entry_uid}.{locale}.{field_path}"
```

| Component | Example |
|-----------|---------|
| `content_type_uid` | `page`, `blog_post` |
| `entry_uid` | `blt80654132ff521260` |
| `locale` | `en-us`, `fr-fr` |
| `field_path` | `title`, `page_components.0.hero.headline` |

Wrong `field_path` → the wrong field opens. This is the #1 source of Visual Builder bugs.

## `addEditableTags` — the only way you should do this

`@contentstack/utils` provides `addEditableTags`, which walks the entry and generates correct `data-cslp` values for every field (including nested modular blocks, arrays, and referenced entries). It attaches them to a `$` property on the entry object.

**Never construct `data-cslp` strings by hand.** Use `addEditableTags` in your data layer, immediately after fetching.

```typescript
import contentstack, { QueryOperation } from "@contentstack/delivery-sdk";
import { addEditableTags } from "@contentstack/utils";

export async function getPage(url: string, locale = "en-us") {
  const result = await stack
    .contentType("page")
    .entry()
    .query()
    .where("url", QueryOperation.EQUALS, url)
    .find();

  const entry = result.entries?.[0];

  if (entry) {
    // One call generates edit tags for every field on the entry
    addEditableTags(entry, "page", true, locale);

    // Tag referenced entries with THEIR own content type UID
    if (entry.author) {
      addEditableTags(entry.author, "author", true, locale);
    }
  }

  return entry;
}
```

After this call:
```
entry.$.title                       → { 'data-cslp': 'page.blt123.en-us.title' }
entry.$.page_components__0          → { 'data-cslp': 'page.blt123.en-us.page_components__0' }
entry.author.$.name                 → { 'data-cslp': 'author.blt456.en-us.name' }
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `entry` | object | The entry returned from the Delivery SDK |
| `content_type_uid` | string | Content type identifier |
| `tagsAsObject` | boolean | `true` → `{ 'data-cslp': '...' }` (use for React/Vue spread). `false` → returns a raw string (use for string templating) |
| `locale` | string | Locale code (e.g. `en-us`) |

### Use `$` in components

Components never call `addEditableTags` themselves — they only spread `entry.$?.fieldName`:

```tsx
// React (tagsAsObject: true)
<h1 {...entry.$?.title}>{entry.title}</h1>
<p {...entry.$?.description}>{entry.description}</p>
```

```html
<!-- EJS/Handlebars (tagsAsObject: false) -->
<h1 {{ entry.$.title }}>{{ entry.title }}</h1>
```

```vue
<!-- Vue -->
<h1 v-bind="entry.$?.title">{{ entry.title }}</h1>
```

## Field paths

Flat content: path is just the field name (`title`, `body`).

Nested modular blocks:

```ts
// Content:
{
  page_components: [
    { hero: { headline: "Welcome", subheading: "..." } },
    { features: { items: [{ title: "Fast" }, { title: "Secure" }] } },
  ]
}

// Paths:
// page_components.0.hero.headline
// page_components.1.features.items.0.title
// page_components.1.features.items.1.title
```

`addEditableTags` builds these automatically. You only care when debugging.

## Modular blocks in React

```tsx
function PageComponents({ entry }: { entry: Page }) {
  return entry.page_components?.map((block, index) => {
    // addEditableTags generated the page_components__{index} keys
    const blockTag = entry.$?.[`page_components__${index}`];

    switch (block._content_type_uid) {
      case "hero_block":
        return <HeroBlock key={index} block={block.hero_block} tag={blockTag} />;
      case "features_block":
        return <FeaturesBlock key={index} block={block.features_block} tag={blockTag} />;
      default:
        return null;
    }
  });
}

function HeroBlock({ block, tag }) {
  return (
    <section {...tag}>
      {/* Fields inside the block have their own $ */}
      <h1 {...block.$?.headline}>{block.headline}</h1>
      <p {...block.$?.description}>{block.description}</p>
    </section>
  );
}
```

## Repeated items inside blocks

Arrays inside blocks get per-item `$` properties too:

```tsx
function FeaturesBlock({ block, tag }) {
  return (
    <section {...tag}>
      <h2 {...block.$?.section_title}>{block.section_title}</h2>
      <ul>
        {block.items?.map((item, itemIndex) => (
          <li key={itemIndex}>
            <span {...item.$?.title}>{item.title}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

## Referenced entries

Referenced entries are separate entries with their own UIDs. Tag them independently in the data layer, then spread their `$` like any other entry:

```tsx
function AuthorCard({ author }) {
  return (
    <div>
      <h3 {...author.$?.name}>{author.name}</h3>
      <p {...author.$?.bio}>{author.bio}</p>
    </div>
  );
}
```

Clicking the name opens the **author entry**, not the reference field on the parent page. That's usually what editors want.

## Centralized tag helper

If you fetch several content types, wrap the pattern:

```typescript
import { addEditableTags } from "@contentstack/utils";

export function tagEntry<T>(entry: T, contentTypeUid: string, locale = "en-us") {
  if (!entry) return entry;
  addEditableTags(entry as object, contentTypeUid, true, locale);
  return entry;
}

export async function getPage(url: string) {
  const result = await stack.contentType("page").entry().query()
    .where("url", QueryOperation.EQUALS, url).find();
  return tagEntry(result.entries?.[0], "page");
}

export async function getHeader() {
  const result = await stack.contentType("header").entry().query().find();
  return tagEntry(result.entries?.[0], "header");
}
```

## What to tag, what to skip

**Tag:** headlines, body, images, repeated items, CTAs, metadata editors frequently modify.

**Don't tag:** structural wrappers, derived/computed content (tag the source field), decorative elements.

Over-tagging clutters Visual Builder with hundreds of click targets. Under-tagging forces editors to hunt in the form.

## Enabling Visual Builder

Requires `@contentstack/live-preview-utils` v3.0+ and `@contentstack/delivery-sdk` v3.20.3+ (v4+ recommended — see `../VERSIONS.md`).

```typescript
import ContentstackLivePreview from "@contentstack/live-preview-utils";

ContentstackLivePreview.init({
  mode: "builder", // Enables DOM scanning + click-to-field
  stackDetails: {
    apiKey: process.env.CONTENTSTACK_API_KEY!,
    environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  },
  editInVisualBuilderButton: {
    enable: true,
    position: "bottom-right",
  },
});
```

`mode: "preview"` gives you real-time updates without the builder layer. `mode: "builder"` adds DOM scanning and interactive controls.

## How Visual Builder works

1. **DOM scan** — finds every element with `data-cslp`.
2. **Region detection** — computes each element's position and bounds.
3. **Field mapping** — parses the `data-cslp` value into `(content_type_uid, entry_uid, locale, field_path)`.
4. **Interaction binding** — attaches click/hover handlers.
5. **Continuous monitoring** — re-scans as the page updates.

Stable DOM structure matters. Client-side effects that swap elements after scan can leave the region map stale until the next scan.

## Block-level controls (add / delete / reorder)

For editors to **add, delete, or reorder** modular blocks in Visual Builder, the **parent wrapper** of the block list must carry the block's edit tag:

```tsx
<div className="page-components">
  {entry.page_components?.map((component, index) => (
    <div key={index} {...entry.$[`page_components__${index}`]}>
      <ComponentRenderer component={component} />
    </div>
  ))}
</div>
```

Without the `page_components__{index}` tag on the wrapper, editors can't delete or reorder that block.

## `data-add-direction`

Control the Visual Builder "Add" button placement on a block list:

```html
<div className="page-components" data-add-direction="vertical">
  {/* block components */}
</div>
```

Values: `vertical`, `horizontal`, `none` (hides the add button).

## `VB_EmptyBlockParentClass` — drop zone for empty blocks

When a Modular Blocks field is empty, there's nothing to render and therefore nothing clickable — editors can't insert the first block. Apply `VB_EmptyBlockParentClass` to the parent so Visual Builder shows a placeholder drop zone:

```tsx
import { VB_EmptyBlockParentClass } from "@contentstack/live-preview-utils";

<div
  className={`page-components ${VB_EmptyBlockParentClass}`}
  {...entry.$?.page_components}
>
  {entry.page_components?.map((component, index) => (
    <div key={index} {...entry.$[`page_components__${index}`]}>
      <ComponentRenderer component={component} />
    </div>
  ))}
</div>
```

This is required for empty-state editing. Without it, an editor opens a page with no blocks yet and has no way to add the first one from Visual Builder.

## GraphQL considerations

GraphQL responses have a different shape than REST; `addEditableTags` expects REST shape. Two requirements:

### 1. Request the system fields

Every entry and referenced entry must include `system { uid, content_type_uid }`:

```graphql
query Page($url: String!) {
  all_page(where: { url: $url }) {
    items {
      system { uid, content_type_uid }
      title
      description
      url
      imageConnection {
        edges { node { url, title } }
      }
      blocks {
        ... on PageBlocksBlock {
          __typename
          block {
            title
            copy
            layout
            imageConnection {
              edges { node { url, title } }
            }
          }
        }
      }
    }
  }
}
```

### 2. Reshape before tagging

Hoist `system.uid` to `uid` (and `system.content_type_uid` to `_content_type_uid`) at the root. Flatten `imageConnection.edges[0].node` to a plain `image` field.

```typescript
const fullPage = res?.all_page?.items?.[0];

const entry = fullPage && {
  ...fullPage,
  uid: fullPage.system?.uid,
  _content_type_uid: fullPage.system?.content_type_uid,
  image: fullPage.imageConnection?.edges?.[0]?.node,
  blocks: fullPage.blocks?.map((block) => ({
    ...block,
    block: {
      ...block?.block,
      image: block?.block?.imageConnection?.edges?.[0]?.node || null,
    },
  })),
};

// Then tag as normal
if (entry) addEditableTags(entry, "page", true, "en-us");
```

After reshaping, components use `entry.$?.field` exactly like the REST flow.

## Testing edit tags

1. Open Live Preview with Visual Builder enabled.
2. Click each type of element.
3. Verify the expected field opens in the entry editor.

| Click | Expected |
|-------|----------|
| Headline | Title field opens |
| Body text | Body field opens |
| List item N | That item's field opens (correct index) |
| Referenced content | Referenced entry opens |

Wrong field opens → inspect `data-cslp` in devtools and compare the path to your content model. Common causes: off-by-one index, typo in block type name, missing `addEditableTags` call on referenced entry.

## Preventing drift

- **TypeScript types** that match your content model catch renamed/removed fields at compile time.
- **Integration tests** that assert `data-cslp` is present on rendered elements catch missing tags before deploy.
- Visual Builder's scanner visually highlights tagged vs untagged regions — regressions are visible immediately.

If you rename a field, `entry.$?.old_name` silently returns `undefined` and that element loses its edit tag. TypeScript + tests are your safety net.

## Red flags

- Constructing `data-cslp` strings by hand instead of using `addEditableTags`.
- Calling `addEditableTags` in components instead of in the data layer.
- Missing `VB_EmptyBlockParentClass` on empty modular block parents — editors can't insert the first block.
- Forgetting to tag referenced entries with their own content type UID — clicks open the wrong entry.
- Not including `system { uid, content_type_uid }` in GraphQL queries.
- Tagging structural wrappers and decorative elements — Visual Builder becomes a mess of click targets.
- Rendering critical content only in client-side effects — Visual Builder's DOM scan finishes before your content appears.

## Related

- `./concepts.md` — Live Preview fundamentals.
- `./csr-mode.md`, `./ssr-mode.md` — rendering-strategy-specific setup.
- `./debugging.md` — symptom-based diagnostic guide.
