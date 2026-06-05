# Contentstack Base Concepts

Core concepts every AI agent needs to understand when working with Contentstack.

## What is Contentstack?

Contentstack is a **headless CMS** that separates content management from content presentation. It provides REST and GraphQL APIs to deliver content to any platform.

## Core Concepts

### Stack

The **top-level container** for all content. Contains content types, entries, assets, environments, and configurations.

- **API Key**: Unique identifier (required for all API calls)
- **Region**: Data center location (US, EU, AU, Azure, GCP)
- **Access Token**: Authentication token (Delivery or Management)

### Content Types

**Schema definitions** for content structure. Like a database table schema.

- **UID**: Unique identifier (e.g., `blog_post`, `page`)
- **Fields**: Individual data fields with types and validation

**Common Field Types:**
| Type | Description |
|------|-------------|
| `text` | Single-line text |
| `textarea` | Multi-line text |
| `richtext` | Rich text editor |
| `number` | Numeric values |
| `date` | Date and time |
| `file` | File uploads |
| `reference` | Link to other entries |
| `modular_block` | Reusable content blocks |
| `group` | Group of related fields |
| `json` | Raw JSON data |

### Entries

**Instances of content types** containing actual content data.

- **UID**: Unique identifier
- **Title**: Display name
- **Locale**: Language variant (e.g., `en-us`, `fr-fr`)
- **Published**: Whether entry is live

### Environments

**Stages in content lifecycle:**

- **Development**: Testing and development
- **Staging**: Pre-production testing
- **Production**: Live environment

Each environment can have different content versions and separate delivery tokens.

### Locales

**Language or regional variations:**

- Each entry can exist in multiple locales
- Codes follow ISO format (e.g., `en-us`, `de-de`)
- Default locale set at stack level

### Assets

**Files stored in Contentstack:**

- Images, videos, documents
- Automatically served via CDN
- Support for image transformations
- Versioning and metadata

### References

**Links between entries:**

- Single reference: Links to one entry
- Multiple references: Links to multiple entries
- Cross-content-type references supported

### Modular Blocks

**Reusable content components:**

- Can be added/removed dynamically
- Each block has its own schema
- Enable flexible page building

## API Types

### Delivery API (CDA)

- **Purpose**: Read-only access to published content
- **Token**: Delivery Token
- **Speed**: Fast, cached, CDN-delivered
- **Use**: Production applications

### Preview API

- **Purpose**: Access unpublished content
- **Token**: Preview Token
- **Use**: Live Preview, development

### Management API (CMA)

- **Purpose**: Full CRUD operations
- **Token**: Management Token
- **Security**: **NEVER expose in frontend**
- **Use**: Backend/server-side only

## Tokens Summary

| Token Type | Purpose | Client-safe? |
|------------|---------|--------------|
| Delivery Token | Read published content | ✅ yes |
| Preview Token | Read draft content (Live Preview) | ✅ yes (preview only) |
| Management Token | Full CRUD | ❌ server only |

For the full decision tree (including Authtoken and OAuth), see [security/tokens-authentication.md](../security/tokens-authentication.md).

## Regions & Endpoints

Contentstack operates in multiple regions. Each region has specific API endpoints.

| Region | REST CDN | GraphQL |
|--------|----------|---------|
| US (AWS) | `cdn.contentstack.io` | `graphql.contentstack.com` |
| EU (AWS) | `eu-cdn.contentstack.com` | `eu-graphql.contentstack.com` |
| AU (AWS) | `au-cdn.contentstack.io` | `au-graphql.contentstack.com` |
| Azure NA | `azure-na-cdn.contentstack.io` | `azure-na-graphql.contentstack.com` |
| Azure EU | `azure-eu-cdn.contentstack.io` | `azure-eu-graphql.contentstack.com` |
| GCP NA | `gcp-na-cdn.contentstack.io` | `gcp-na-graphql.contentstack.com` |
| GCP EU | `gcp-eu-cdn.contentstack.io` | `gcp-eu-graphql.contentstack.com` |

**Important**: You must configure the correct region for your stack. See the [Regions Guide](./regions.md) for complete configuration details across all SDKs and tools.

## Content Workflow

```
Content Manager creates entry in CMS
        ↓
Entry saved as draft
        ↓
Entry previewed (Live Preview)
        ↓
Entry published to environment
        ↓
Content available via Delivery API
        ↓
Frontend fetches and displays
```

## Key Terminology

| Term | Description |
|------|-------------|
| **Stack** | Top-level container for all content |
| **Content Type** | Schema definition for content structure |
| **Entry** | Instance of content type with data |
| **Environment** | Stage of content lifecycle |
| **Locale** | Language or regional variation |
| **Asset** | File stored in Contentstack |
| **Reference** | Link between entries |
| **Modular Block** | Reusable content component |

