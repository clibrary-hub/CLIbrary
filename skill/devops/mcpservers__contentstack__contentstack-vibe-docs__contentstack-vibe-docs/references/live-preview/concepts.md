# Live Preview Concepts

Understanding Contentstack's Live Preview feature before implementation.

## What is Live Preview?

Live Preview lets content managers see changes **instantly before publishing**. When an editor opens an entry, the CMS generates a preview hash that links the editor with a website preview loaded in an iframe.

## How It Works

```
Editor opens entry in CMS
        ↓
CMS generates Live Preview hash
        ↓
Website loads in iframe
        ↓
Live Preview SDK initializes and connects to CMS
        ↓
Editor makes changes to content
        ↓
ssr:false → CMS sends data via postMessage, client re-fetches
ssr:true  → CMS refreshes iframe with query params, server reads them
```

**Important**: Live Preview is a development/preview feature only. It is never enabled in production builds.

## Key Concepts

### Live Preview Hash

A session-specific ID appended to preview URLs (e.g., `?live_preview=abc123`). Identifies the editor session and ensures the preview shows latest unpublished changes.

### Preview Token

A special API token (generated from **Settings → Tokens → Delivery Tokens**) that allows calling preview endpoints. Associated with a delivery token.

### Live Preview Utils SDK

JavaScript library (`@contentstack/live-preview-utils`) that connects CMS and frontend:
- Listens for entry-change events
- Injects updated content
- Adds edit buttons
- Supports edit tags

### Live Edit Tags

Special `data-cslp` attributes pointing to field paths:
```html
<h1 data-cslp="blog_post.blt123.en-us.title">Welcome!</h1>
```

The SDK reads these to highlight fields and show Edit buttons.

### The `ssr` Setting

The `ssr` setting in the Live Preview SDK controls **how the preview iframe receives content updates from the CMS**. This is NOT about your website's rendering strategy.

| Setting | Update Mechanism | What Happens |
|---------|------------------|--------------|
| `ssr: false` | postMessage | CMS sends change event → SDK triggers `onEntryChange()` callback → Your client code re-fetches and updates UI |
| `ssr: true` | Iframe refresh | CMS reloads iframe with query params (`?live_preview=hash&entry_uid=...&content_type_uid=...`) → Server reads params and fetches preview data |

**Note**: Your production website can use any rendering strategy (SSR, CSR, SSG, ISR). The `ssr` setting only affects Live Preview behavior during content editing.

## Prerequisites

### 1. Enable Live Preview in Contentstack

1. Navigate to **Settings → Environments**
2. Set **base URL** for each locale (e.g., `https://your-site.com`)
3. Tick **Enable Live Preview**
4. Select default preview environment
5. Save settings

### 2. Generate Preview Token

1. Go to **Settings → Tokens → Delivery Tokens**
2. Select or create a delivery token
3. Toggle **Create preview token**
4. Copy the preview token

### 3. Host Requirements

Your website must:
- **Use HTTPS** (required for iframe embedding)
- **Allow iframe embedding** (configure headers if needed)
- **Be publicly accessible** (Contentstack loads it in iframe)

**Hosting Options:**
- Contentstack Launch (recommended)
- Vercel, Netlify, AWS, etc.
- Local dev with tunneling (ngrok, Cloudflare Tunnel)

## Choosing the `ssr` Setting

### Use `ssr: false` when:
- Your preview pages fetch data **client-side** (useEffect, useSWR, etc.)
- You want instant updates without iframe refresh
- You're using `onEntryChange()` callback to re-fetch data

### Use `ssr: true` when:
- Your preview pages fetch data **server-side** (getServerSideProps, server components, etc.)
- Your server needs to read the `live_preview` query param to fetch preview content
- You can't easily re-fetch data client-side

**Remember**: This only affects preview behavior. Production doesn't use Live Preview at all.

## Region Hosts

| Region | REST Preview | GraphQL Preview |
|--------|--------------|-----------------|
| US | `rest-preview.contentstack.com` | `graphql-preview.contentstack.com` |
| EU | `eu-rest-preview.contentstack.com` | `eu-graphql-preview.contentstack.com` |
| Azure NA | `azure-na-rest-preview.contentstack.com` | `azure-na-graphql-preview.contentstack.com` |
| Azure EU | `azure-eu-rest-preview.contentstack.com` | `azure-eu-graphql-preview.contentstack.com` |
| GCP NA | `gcp-na-rest-preview.contentstack.com` | `gcp-na-graphql-preview.contentstack.com` |
| GCP EU | `gcp-eu-rest-preview.contentstack.com` | `gcp-eu-graphql-preview.contentstack.com` |

## SDK Version 3 Features

- **Mode Property**: `"preview"` for Live Preview, `"builder"` for Visual Builder
  - `"preview"`: Basic Live Preview with edit buttons and field highlighting
  - `"builder"`: Full Visual Builder with inline editing, drag-and-drop reordering of multiple fields, and a visual editing UI
- **Edit Button Config**: Customizable position and behavior
- **Clean Production Tags**: `cleanCslpOnProduction` removes `data-cslp` in production

## Visual Builder Requirements

Visual Builder (`mode: "builder"`) has additional requirements beyond basic Live Preview:

1. **URL field required**: Content types must have `is_page: true` and a `url` field. Visual Builder matches the iframe URL to the entry's `url` field to identify which entry is being edited.
2. **Edit tags for multiple fields**: To enable add/delete/reorder on multiple group fields, use the `field__${index}` pattern:
   - Container element: `{...(entry.$ && entry.$.field_name)}`
   - Each item: `{...(entry.$?.[`field_name__${index}`])}`
   - Item fields: `{...(item.$ && item.$.sub_field)}`

## Next Steps

- [CSR Implementation](./csr-mode.md) - Client-side rendering setup
- [SSR Implementation](./ssr-mode.md) - Server-side rendering setup
- [Framework Patterns](../frameworks/) - Next.js, Nuxt, Gatsby examples

