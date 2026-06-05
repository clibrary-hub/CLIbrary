# Contentstack Content Management API

Complete guide to using Contentstack's Content Management API (CMA) for programmatic content operations — create, update, delete, and publish entries, content types, assets, and more.

## Base URL

```
https://api.contentstack.io/v3/{resource}
```

**Regional Base URLs:**

| Region | Base URL |
|--------|----------|
| `us` | `https://api.contentstack.io/v3/` |
| `eu` | `https://eu-api.contentstack.com/v3/` |
| `au` | `https://au-api.contentstack.com/v3/` |
| `azure-na` | `https://azure-na-api.contentstack.com/v3/` |
| `azure-eu` | `https://azure-eu-api.contentstack.com/v3/` |
| `gcp-na` | `https://gcp-na-api.contentstack.com/v3/` |
| `gcp-eu` | `https://gcp-eu-api.contentstack.com/v3/` |

See [Regions Guide](../concepts/regions.md) for finding your stack's region.

---

## Authentication

The CMA supports three authentication methods. All require the `api_key` header. **Header name for the credential differs between methods** — a common copy-paste bug.

| Method | Credential header | Use case |
|--------|-------------------|----------|
| User login | `authtoken: <authtoken>` | Interactive user sessions |
| Management Token | `authorization: <mgmt_token>` | Server-side automation, CI/CD, migrations |
| OAuth | `authorization: Bearer <access_token>` | Third-party apps on behalf of a user |

> Note that Management Tokens use `authorization: <token>` **without** a `Bearer` prefix, while OAuth uses `authorization: Bearer <token>`. They are different headers despite sharing a name.

### Option 1: Authtoken (User-Specific)

```http
api_key: YOUR_API_KEY
authtoken: YOUR_AUTHTOKEN
Content-Type: application/json
```

- Tied to user roles and permissions
- Maximum 20 valid tokens per user
- No time expiration
- Obtain via login: `POST /v3/user-session`

### Option 2: Management Token (Stack-Level)

```http
api_key: YOUR_API_KEY
authorization: YOUR_MANAGEMENT_TOKEN
Content-Type: application/json
```

- Not tied to a specific user
- Maximum 10 tokens per stack
- Can be read-only or read-write
- Assignable to specific branches

**Management token limitations:** Cannot manage organizations, stack operations, user sessions, token management, workflow stage changes, or publish rules requiring user/role approval.

### Option 3: OAuth Bearer Token

```http
api_key: YOUR_API_KEY
authorization: Bearer YOUR_OAUTH_TOKEN
Content-Type: application/json
```

See [OAuth Guide](../authentication/oauth.md) for implementation details.

---

## Entries

Entries are the content items within a content type. This is the most commonly used CMA resource.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/content_types/{ct_uid}/entries` | Get all entries |
| `GET` | `/v3/content_types/{ct_uid}/entries/{entry_uid}` | Get a single entry |
| `POST` | `/v3/content_types/{ct_uid}/entries` | Create an entry |
| `PUT` | `/v3/content_types/{ct_uid}/entries/{entry_uid}` | Update an entry |
| `DELETE` | `/v3/content_types/{ct_uid}/entries/{entry_uid}` | Delete an entry |
| `POST` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/publish` | Publish an entry |
| `POST` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/unpublish` | Unpublish an entry |

### Create an Entry

```bash
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "entry": {
      "title": "My First Blog Post",
      "url": "/blog/my-first-post",
      "body": "<p>Hello world</p>",
      "author": [{ "uid": "blt1234567890", "_content_type_uid": "author" }],
      "tags": ["tutorial", "getting-started"]
    }
  }'
```

**With locale:**

```bash
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries?locale=fr-fr' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "entry": {
      "title": "Mon Premier Article"
    }
  }'
```

### Update an Entry

```bash
curl -X PUT 'https://api.contentstack.io/v3/content_types/blog_post/entries/blt1234567890' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "entry": {
      "title": "Updated Title",
      "body": "<p>Updated content</p>"
    }
  }'
```

### Publish an Entry

```bash
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries/blt1234567890/publish' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "entry": {
      "environments": ["production"],
      "locales": ["en-us"]
    }
  }'
```

**Scheduled publish:**

```bash
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries/blt1234567890/publish' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "entry": {
      "environments": ["production"],
      "locales": ["en-us"],
      "scheduled_at": "2025-06-15T09:00:00.000Z"
    }
  }'
```

### Unpublish an Entry

```bash
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries/blt1234567890/unpublish' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "entry": {
      "environments": ["production"],
      "locales": ["en-us"]
    }
  }'
```

### Query Entries

**Query parameters:**

| Parameter | Description |
|-----------|-------------|
| `locale` | Locale code (e.g., `en-us`, `fr-fr`) |
| `include_publish_details` | Returns publish details per environment |
| `include_workflow` | Include workflow stage information |
| `include_count` | Include total count in response |
| `skip` | Number of entries to skip (pagination) |
| `limit` | Number of entries to return (default: 25) |
| `asc` | Sort ascending by field |
| `desc` | Sort descending by field |
| `query` | JSON query for filtering (MongoDB-style operators) |

**Example — fetch entries with filtering:**

```bash
curl -G 'https://api.contentstack.io/v3/content_types/blog_post/entries' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  --data-urlencode 'query={"status": "published"}' \
  --data-urlencode 'limit=10' \
  --data-urlencode 'skip=0' \
  --data-urlencode 'include_count=true' \
  --data-urlencode 'desc=created_at'
```

### Additional Entry Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/references` | Get entry references |
| `GET` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/languages` | Get entry languages |
| `GET` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/versions` | Get version history |
| `GET` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/export` | Export an entry |
| `POST` | `/v3/content_types/{ct_uid}/entries/import` | Import an entry |
| `POST` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/localize` | Localize an entry |
| `POST` | `/v3/content_types/{ct_uid}/entries/{entry_uid}/workflow` | Set workflow stage |

---

## Content Types

Content types define the schema for your entries.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/content_types` | Get all content types |
| `GET` | `/v3/content_types/{uid}` | Get a single content type |
| `POST` | `/v3/content_types` | Create a content type |
| `PUT` | `/v3/content_types/{uid}` | Update a content type |
| `DELETE` | `/v3/content_types/{uid}` | Delete a content type |
| `POST` | `/v3/content_types/import` | Import a content type |
| `GET` | `/v3/content_types/{uid}/export` | Export a content type |

### Create a Content Type

```bash
curl -X POST 'https://api.contentstack.io/v3/content_types' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "content_type": {
      "title": "Blog Post",
      "uid": "blog_post",
      "schema": [
        {
          "display_name": "Title",
          "uid": "title",
          "data_type": "text",
          "mandatory": true,
          "unique": true,
          "field_metadata": { "description": "The post title" }
        },
        {
          "display_name": "URL",
          "uid": "url",
          "data_type": "text",
          "mandatory": true
        },
        {
          "display_name": "Body",
          "uid": "body",
          "data_type": "json",
          "field_metadata": { "allow_json_rte": true }
        },
        {
          "display_name": "Published Date",
          "uid": "published_date",
          "data_type": "isodate"
        },
        {
          "display_name": "Author",
          "uid": "author",
          "data_type": "reference",
          "reference_to": ["author"],
          "multiple": false
        },
        {
          "display_name": "Featured Image",
          "uid": "featured_image",
          "data_type": "file"
        },
        {
          "display_name": "Tags",
          "uid": "tags",
          "data_type": "text",
          "multiple": true
        },
        {
          "display_name": "Is Featured",
          "uid": "is_featured",
          "data_type": "boolean"
        }
      ],
      "options": {
        "is_page": true,
        "singleton": false,
        "url_pattern": "/:title",
        "url_prefix": "/blog/"
      }
    }
  }'
```

### Field Data Types Reference

| Field Type | `data_type` | Key Properties |
|-----------|-------------|----------------|
| Single Line Text | `text` | `format` (regex validation) |
| Multi Line Text | `text` | `field_metadata.multiline: true` |
| Markdown | `text` | `field_metadata.markdown: true` |
| Rich Text (HTML) | `text` | `allow_rich_text: true` |
| JSON Rich Text | `json` | `field_metadata.allow_json_rte: true` |
| Number | `number` | -- |
| Boolean | `boolean` | -- |
| Date | `isodate` | `startDate`, `endDate` |
| Select/Dropdown | `text` | `enum` with choices array, **requires `display_type: "dropdown"`** |
| File | `file` | `extensions` array for allowed types |
| Link | `link` | -- |
| Reference | `reference` | `reference_to` (array of content type UIDs) |
| Group | `group` | Nested `schema` array |
| Modular Blocks | `blocks` | Nested schema arrays per block |
| Global Field | `global_field` | `reference_to` (global field UID) |

### Universal Field Properties

| Property | Type | Description |
|----------|------|-------------|
| `display_name` | string | Visible label (required) |
| `uid` | string | Unique identifier (required) |
| `data_type` | string | Field data type (required) |
| `mandatory` | boolean | Required field |
| `unique` | boolean | Unique value constraint |
| `multiple` | boolean | Allow multiple values (array) |
| `field_metadata.description` | string | Help text |
| `field_metadata.default_value` | any | Default value |
| `field_metadata.instruction` | string | Editor instruction |
| `field_metadata.placeholder` | string | Input placeholder |

### Modular Blocks field schema

`blocks` data type lets editors choose which block to insert from a set of nested schemas. Each block has its own `uid`, `title`, and a nested `schema` array.

```json
{
  "display_name": "Page Components",
  "uid": "page_components",
  "data_type": "blocks",
  "multiple": true,
  "mandatory": false,
  "blocks": [
    {
      "title": "Hero",
      "uid": "hero",
      "schema": [
        { "display_name": "Headline", "uid": "headline", "data_type": "text", "mandatory": true },
        { "display_name": "Subheading", "uid": "subheading", "data_type": "text" },
        { "display_name": "Image", "uid": "image", "data_type": "file" },
        {
          "display_name": "CTA",
          "uid": "cta",
          "data_type": "group",
          "schema": [
            { "display_name": "Label", "uid": "label", "data_type": "text" },
            { "display_name": "URL", "uid": "url", "data_type": "text" }
          ]
        }
      ]
    },
    {
      "title": "Content",
      "uid": "content",
      "schema": [
        { "display_name": "Title", "uid": "title", "data_type": "text" },
        { "display_name": "Body", "uid": "body", "data_type": "text", "allow_rich_text": true }
      ]
    }
  ]
}
```

At query time, each selected block appears in the entry's `page_components` array keyed by its block `uid`:

```json
{
  "page_components": [
    { "hero": { "headline": "Welcome", "subheading": "...", "image": { "uid": "..." }, "cta": { "label": "...", "url": "..." } } },
    { "content": { "title": "About", "body": "<p>...</p>" } }
  ]
}
```

See `../frameworks/nextjs.md` → Modular Blocks for rendering patterns, and `../live-preview/visual-builder.md` for edit-tag handling.

### Important Notes for Content Type Creation

**Enum/Dropdown fields require `display_type`**: When using `enum` with choices, you must include `display_type: "dropdown"` on the field or the API will reject the request.

```json
{
  "display_name": "Status",
  "uid": "status",
  "data_type": "text",
  "enum": {
    "advanced": false,
    "choices": [
      { "value": "available" },
      { "value": "pending" },
      { "value": "adopted" }
    ]
  },
  "display_type": "dropdown"
}
```

**`is_page: true` requires a `url` field**: If you set `options.is_page` to `true`, the schema **must** include a field with `"uid": "url"`. Without it, the API returns a validation error. This `url` field is also required for **Live Preview** and **Visual Builder** to route correctly to the entry in the preview iframe.

```json
{
  "display_name": "URL",
  "uid": "url",
  "data_type": "text",
  "mandatory": true
}
```

---

## Assets

Assets are files (images, documents, videos) managed in your stack.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/assets` | Get all assets |
| `GET` | `/v3/assets/{asset_uid}` | Get a single asset |
| `POST` | `/v3/assets` | Upload an asset |
| `PUT` | `/v3/assets/{asset_uid}` | Replace an asset |
| `DELETE` | `/v3/assets/{asset_uid}` | Delete an asset |
| `POST` | `/v3/assets/{asset_uid}/publish` | Publish an asset |
| `POST` | `/v3/assets/{asset_uid}/unpublish` | Unpublish an asset |

**Important:** Asset uploads use `multipart/form-data`, not JSON.

### Upload an Asset

```bash
curl -X POST 'https://api.contentstack.io/v3/assets' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -F 'asset[upload]=@/path/to/image.jpg' \
  -F 'asset[parent_uid]=folder_uid' \
  -F 'asset[title]=Hero Image' \
  -F 'asset[description]=Homepage hero banner' \
  -F 'asset[tags]=hero,homepage'
```

### Replace an Asset

```bash
curl -X PUT 'https://api.contentstack.io/v3/assets/blt1234567890' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -F 'asset[upload]=@/path/to/new-image.jpg'
```

### Publish an Asset

```bash
curl -X POST 'https://api.contentstack.io/v3/assets/blt1234567890/publish' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "asset": {
      "environments": ["production"],
      "locales": ["en-us"]
    }
  }'
```

### Asset Constraints

- Maximum 10 assets uploaded at once
- Maximum file size: 700 MB per asset
- Upload uses `multipart/form-data` content type

### Asset Folders

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/assets/folders/{folder_uid}` | Get a folder |
| `POST` | `/v3/assets/folders` | Create a folder |
| `PUT` | `/v3/assets/folders/{folder_uid}` | Update a folder |
| `DELETE` | `/v3/assets/folders/{folder_uid}` | Delete a folder |

---

## Environments

Environments define where content is published (e.g., production, staging).

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/environments` | Get all environments |
| `GET` | `/v3/environments/{environment_uid}` | Get a single environment |
| `POST` | `/v3/environments` | Create an environment |
| `PUT` | `/v3/environments/{environment_uid}` | Update an environment |
| `DELETE` | `/v3/environments/{environment_uid}` | Delete an environment |

### Create an Environment

```bash
curl -X POST 'https://api.contentstack.io/v3/environments' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "environment": {
      "name": "staging",
      "urls": [
        { "locale": "en-us", "url": "https://staging.example.com" }
      ]
    }
  }'
```

---

## Locales

Locales enable multilingual content.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/locales` | Get all locales |
| `GET` | `/v3/locales/{locale_code}` | Get a single locale |
| `POST` | `/v3/locales` | Add a locale |
| `PUT` | `/v3/locales/{locale_code}` | Update a locale |
| `DELETE` | `/v3/locales/{locale_code}` | Delete a locale |

### Add a Locale

```bash
curl -X POST 'https://api.contentstack.io/v3/locales' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "locale": {
      "code": "fr-fr",
      "name": "French - France",
      "fallback_locale": "en-us"
    }
  }'
```

**Important:** A fallback locale is required when adding a new locale.

---

## Global Fields

Reusable field groups shared across content types.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/global_fields` | Get all global fields |
| `GET` | `/v3/global_fields/{uid}` | Get a single global field |
| `POST` | `/v3/global_fields` | Create a global field |
| `PUT` | `/v3/global_fields/{uid}` | Update a global field |
| `DELETE` | `/v3/global_fields/{uid}` | Delete a global field |

**Important:** Pass `api_version: '3.2'` header for nested global fields support.

### Create a Global Field

```bash
curl -X POST 'https://api.contentstack.io/v3/global_fields' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "global_field": {
      "title": "SEO Fields",
      "uid": "seo_fields",
      "schema": [
        {
          "display_name": "Meta Title",
          "uid": "meta_title",
          "data_type": "text"
        },
        {
          "display_name": "Meta Description",
          "uid": "meta_description",
          "data_type": "text",
          "field_metadata": { "multiline": true }
        },
        {
          "display_name": "OG Image",
          "uid": "og_image",
          "data_type": "file"
        }
      ]
    }
  }'
```

---

## Webhooks

Webhooks notify external services when content changes.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/webhooks` | Get all webhooks |
| `GET` | `/v3/webhooks/{webhook_uid}` | Get a single webhook |
| `POST` | `/v3/webhooks` | Create a webhook |
| `PUT` | `/v3/webhooks/{webhook_uid}` | Update a webhook |
| `DELETE` | `/v3/webhooks/{webhook_uid}` | Delete a webhook |
| `GET` | `/v3/webhooks/{webhook_uid}/logs` | Get webhook execution logs |

### Create a Webhook

```bash
curl -X POST 'https://api.contentstack.io/v3/webhooks' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "webhook": {
      "name": "Entry Published",
      "destinations": [
        {
          "target_url": "https://your-api.example.com/webhook",
          "http_basic_auth": "username:password",
          "http_basic_password": "secret",
          "custom_header": [
            { "header_name": "X-Custom-Header", "value": "custom-value" }
          ]
        }
      ],
      "channels": [
        "content_types.blog_post.entries.publish.success"
      ],
      "retry_policy": "manual"
    }
  }'
```

### Common Webhook Event Channels

| Channel Pattern | Description |
|----------------|-------------|
| `content_types.entries.create` | Any entry created |
| `content_types.entries.update` | Any entry updated |
| `content_types.entries.publish.success` | Any entry published |
| `content_types.entries.unpublish.success` | Any entry unpublished |
| `content_types.entries.delete` | Any entry deleted |
| `content_types.{ct_uid}.entries.create` | Entry created in specific content type |
| `content_types.{ct_uid}.entries.publish.success` | Entry published in specific content type |
| `assets.delete` | Asset deleted |
| `assets.publish.success` | Asset published |
| `content_types.create` | Content type created |
| `content_types.update` | Content type updated |

### Webhook Payload Format

Contentstack sends a `POST` request with a JSON body:

```json
{
  "event": "publish",
  "module": "entry",
  "api_key": "your_stack_api_key",
  "data": {
    "entry": { "uid": "blt1234567890", "title": "My Post" },
    "content_type": { "uid": "blog_post" },
    "environment": { "name": "production" },
    "locale": "en-us"
  },
  "triggered_at": "2025-01-15T10:30:00.000Z"
}
```

**Security headers sent:** `Content-Type: application/json`, `X-Contentstack-Request-Signature`

---

## Workflows

Workflows define content review and approval stages.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/workflows` | Get all workflows |
| `GET` | `/v3/workflows/{workflow_uid}` | Get a single workflow |
| `POST` | `/v3/workflows` | Create a workflow |
| `PUT` | `/v3/workflows/{workflow_uid}` | Update a workflow |
| `DELETE` | `/v3/workflows/{workflow_uid}` | Delete a workflow |

### Set Entry Workflow Stage

```bash
curl -X POST 'https://api.contentstack.io/v3/content_types/blog_post/entries/blt1234567890/workflow' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authtoken: YOUR_AUTHTOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "workflow": {
      "workflow_stage": {
        "uid": "blt_workflow_stage_uid"
      }
    }
  }'
```

**Note:** Only Stack Owner, Administrator, and Developer roles can create workflows. Management tokens cannot change workflow stages — use an authtoken instead.

---

## Releases

Releases group entries and assets for batch publishing.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/releases` | Get all releases |
| `GET` | `/v3/releases/{release_uid}` | Get a single release |
| `POST` | `/v3/releases` | Create a release |
| `PUT` | `/v3/releases/{release_uid}` | Update a release |
| `DELETE` | `/v3/releases/{release_uid}` | Delete a release |
| `POST` | `/v3/releases/{release_uid}/deploy` | Deploy a release |
| `GET` | `/v3/releases/{release_uid}/items` | Get release items |
| `POST` | `/v3/releases/{release_uid}/items` | Add items to release |
| `DELETE` | `/v3/releases/{release_uid}/items` | Remove items from release |

### Create and Deploy a Release

```bash
# 1. Create the release
curl -X POST 'https://api.contentstack.io/v3/releases' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "release": {
      "name": "Q1 Product Launch",
      "description": "All content for the product launch"
    }
  }'

# 2. Add items to the release
curl -X POST 'https://api.contentstack.io/v3/releases/{release_uid}/items' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [
      {
        "uid": "entry_uid_1",
        "locale": "en-us",
        "version": 1,
        "content_type_uid": "blog_post",
        "action": "publish"
      },
      {
        "uid": "asset_uid_1",
        "action": "publish"
      }
    ]
  }'

# 3. Deploy the release
curl -X POST 'https://api.contentstack.io/v3/releases/{release_uid}/deploy' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "release": {
      "environments": ["production"],
      "locales": ["en-us"],
      "action": "publish"
    }
  }'
```

---

## Bulk Operations

Perform operations on multiple entries or assets at once.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v3/bulk/publish` | Bulk publish |
| `POST` | `/v3/bulk/unpublish` | Bulk unpublish |
| `POST` | `/v3/bulk/delete` | Bulk delete |
| `POST` | `/v3/bulk/workflow` | Bulk update workflow stage |
| `GET` | `/v3/bulk/{job_id}` | Check job status |

### Bulk Publish

```bash
curl -X POST 'https://api.contentstack.io/v3/bulk/publish' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "entries": [
      { "uid": "entry_uid_1", "content_type": "blog_post", "locale": "en-us" },
      { "uid": "entry_uid_2", "content_type": "blog_post", "locale": "en-us" }
    ],
    "assets": [
      { "uid": "asset_uid_1" }
    ],
    "locales": ["en-us"],
    "environments": ["production"],
    "publish_with_reference": true
  }'
```

**Important:** Bulk operations are rate-limited to 1 request per second.

---

## Branches

Branches allow content versioning and parallel development.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/stacks/branches` | Get all branches |
| `GET` | `/v3/stacks/branches/{branch_uid}` | Get a branch |
| `POST` | `/v3/stacks/branches` | Create a branch |
| `DELETE` | `/v3/stacks/branches/{branch_uid}` | Delete a branch |
| `GET` | `/v3/stacks/branches_compare` | Compare branches |

### Create a Branch

```bash
curl -X POST 'https://api.contentstack.io/v3/stacks/branches' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'authorization: YOUR_MANAGEMENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "branch": {
      "uid": "feature-redesign",
      "source": "main"
    }
  }'
```

**Note:** To target a specific branch in any API call, add the `branch` header:

```http
branch: feature-redesign
```

---

## Tokens

### Management Tokens

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/stacks/management_tokens` | Get all tokens |
| `POST` | `/v3/stacks/management_tokens` | Create a token |
| `PUT` | `/v3/stacks/management_tokens/{token_uid}` | Update a token |
| `DELETE` | `/v3/stacks/management_tokens/{token_uid}` | Delete a token |

### Delivery Tokens

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v3/stacks/delivery_tokens` | Get all tokens |
| `POST` | `/v3/stacks/delivery_tokens` | Create a token |
| `PUT` | `/v3/stacks/delivery_tokens/{token_uid}` | Update a token |
| `DELETE` | `/v3/stacks/delivery_tokens/{token_uid}` | Delete a token |

---

## JavaScript CMA SDK

The `@contentstack/management` SDK provides a typed JavaScript interface for all CMA operations.

### Installation

```bash
npm install @contentstack/management
```

### Initialization

```typescript
import * as contentstack from "@contentstack/management";

// With Management Token (recommended for automation)
const client = contentstack.client();
const stack = client.stack({
  api_key: process.env.CONTENTSTACK_API_KEY!,
  management_token: process.env.CONTENTSTACK_MANAGEMENT_TOKEN!,
});

// With Authtoken (user-specific)
const client = contentstack.client({
  authtoken: process.env.CONTENTSTACK_AUTHTOKEN!,
});
const stack = client.stack({
  api_key: process.env.CONTENTSTACK_API_KEY!,
});
```

### SDK Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `host` | `api.contentstack.io` | API host (set per region) |
| `timeout` | `30000` | Request timeout in ms |
| `retryOnError` | `true` | Enable automatic retries |
| `retryLimit` | `5` | Maximum retry attempts |
| `retryDelay` | `300` | Delay between retries in ms |

### Content Type Operations

```typescript
// Get all content types
const contentTypes = await stack.contentType().query().find();

// Get a single content type
const blogType = await stack.contentType("blog_post").fetch();

// Create a content type
const newType = await stack.contentType().create({
  content_type: {
    title: "Blog Post",
    uid: "blog_post",
    schema: [
      { display_name: "Title", uid: "title", data_type: "text", mandatory: true },
      { display_name: "Body", uid: "body", data_type: "json", field_metadata: { allow_json_rte: true } },
    ],
    options: { is_page: true, url_pattern: "/:title", url_prefix: "/blog/" },
  },
});

// Delete a content type
await stack.contentType("blog_post").delete();
```

### Entry Operations

```typescript
// Create an entry
const entry = await stack.contentType("blog_post").entry().create({
  entry: {
    title: "My Post",
    body: "<p>Hello world</p>",
    tags: ["tutorial"],
  },
});

// Update an entry
const entry = await stack.contentType("blog_post").entry("blt1234567890").fetch();
entry.title = "Updated Title";
await entry.update();

// Publish an entry
await stack.contentType("blog_post").entry("blt1234567890").publish({
  entry: {
    environments: ["production"],
    locales: ["en-us"],
  },
});

// Unpublish an entry
await stack.contentType("blog_post").entry("blt1234567890").unpublish({
  entry: {
    environments: ["production"],
    locales: ["en-us"],
  },
});

// Delete an entry
await stack.contentType("blog_post").entry("blt1234567890").delete();

// Query entries
const entries = await stack
  .contentType("blog_post")
  .entry()
  .query({ query: { title: "My Post" } })
  .find();
```

### Asset Operations

```typescript
import * as fs from "fs";

// Upload an asset
const asset = await stack.asset().create({
  asset: {
    upload: fs.createReadStream("/path/to/image.jpg"),
    title: "Hero Image",
    description: "Homepage hero banner",
    parent_uid: "folder_uid", // optional
    tags: "hero,homepage",
  },
});

// Fetch an asset
const asset = await stack.asset("blt1234567890").fetch();

// Publish an asset
await stack.asset("blt1234567890").publish({
  asset: {
    environments: ["production"],
    locales: ["en-us"],
  },
});

// Delete an asset
await stack.asset("blt1234567890").delete();

// Create a folder
const folder = await stack.asset().folder().create({
  asset: {
    name: "Product Images",
    parent_uid: "parent_folder_uid", // optional
  },
});
```

### Global Field Operations

```typescript
// Create a global field
await stack.globalField().create({
  global_field: {
    title: "SEO Fields",
    uid: "seo_fields",
    schema: [
      { display_name: "Meta Title", uid: "meta_title", data_type: "text" },
      { display_name: "Meta Description", uid: "meta_description", data_type: "text" },
    ],
  },
});

// Fetch a global field
const seoFields = await stack.globalField("seo_fields").fetch();

// Important: pass api_version for nested global fields
const client = contentstack.client({ api_version: "3.2" });
```

### Release Operations

```typescript
// Create a release
const release = await stack.release().create({
  release: {
    name: "Q1 Product Launch",
    description: "All content for the product launch",
  },
});

// Add items to a release
await stack.release("release_uid").item().create({
  items: [
    { uid: "entry_uid_1", locale: "en-us", version: 1, content_type_uid: "blog_post", action: "publish" },
  ],
});

// Deploy a release
await stack.release("release_uid").deploy({
  release: {
    environments: ["production"],
    locales: ["en-us"],
    action: "publish",
  },
});
```

### Bulk Operations

```typescript
// Bulk publish
await stack.bulkOperation().publish({
  entries: [
    { uid: "entry_uid_1", content_type: "blog_post", locale: "en-us" },
    { uid: "entry_uid_2", content_type: "blog_post", locale: "en-us" },
  ],
  locales: ["en-us"],
  environments: ["production"],
});

// Bulk delete
await stack.bulkOperation().delete({
  entries: [
    { uid: "entry_uid_1", content_type: "blog_post", locale: "en-us" },
  ],
});
```

---

## Error Handling

### HTTP Status Codes

| Status | Meaning |
|--------|---------|
| `2xx` | Success |
| `400` | Malformed request |
| `401` | Invalid credentials |
| `403` | Access forbidden |
| `404` | Resource not found |
| `412` | Invalid API key |
| `422` | Validation error |
| `429` | Rate limit exceeded |
| `5xx` | Server error |

### Error Response Format

```json
{
  "error_code": 141,
  "error_message": "Entry not found",
  "errors": {
    "entry_uid": ["Entry does not exist"]
  }
}
```

### SDK Error Handling

```typescript
try {
  const entry = await stack.contentType("blog_post").entry().create({
    entry: { title: "My Post" },
  });
  console.log("Created:", entry.uid);
} catch (error: any) {
  console.error("CMA Error:", error.message);
  console.error("Status:", error.status);
  console.error("Details:", error.errors);
}
```

---

## Rate Limiting

| Operation Type | Limit |
|---------------|-------|
| Read (`GET`) | 10 requests/second/organization |
| Write (`POST`/`PUT`/`DELETE`) | 10 requests/second/organization |
| Bulk operations | 1 request/second |
| Stack creation | 1 per minute |

**Rate limit response headers:**

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
```

When exceeded, the API returns HTTP `429`. The SDK automatically retries with backoff when `retryOnError: true`.

---

## Best Practices

1. **Use management tokens for automation** — prefer stack-scoped tokens over user authtokens for CI/CD and scripts
2. **Use the SDK for JavaScript projects** — handles retries, pagination, and type safety
3. **Implement retry logic** — respect rate limits and use exponential backoff
4. **Use bulk operations for batch tasks** — publish, unpublish, or delete multiple items in one call
5. **Use releases for coordinated publishes** — group related content for atomic deployment
6. **Use branches for parallel development** — create branches for features, merge when ready
7. **Use global fields for reusable schemas** — avoid duplicating field definitions across content types
8. **Never expose management tokens in frontend code** — use server-side only
9. **Use webhooks for event-driven integrations** — avoid polling for changes
10. **Store credentials in environment variables** — never hardcode tokens

---

## Environment Variables

```bash
# Management API
CONTENTSTACK_API_KEY=your_api_key
CONTENTSTACK_MANAGEMENT_TOKEN=your_management_token
CONTENTSTACK_REGION=us

# If using authtoken instead
CONTENTSTACK_AUTHTOKEN=your_authtoken
```

---

See [REST API](rest-api.md) for content delivery, [GraphQL API](graphql-api.md) for GraphQL delivery, and [Delivery SDK](../sdk/delivery-sdk.md) for the TypeScript delivery SDK.
