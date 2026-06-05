# Contentstack Regions Guide

Complete guide to configuring and using Contentstack regions across all SDKs, CLI, and APIs.

## Overview

Contentstack operates in multiple regions worldwide. Your stack's region determines where your data is stored and which API endpoints you'll use. **You must configure the correct region** for all SDKs, CLI tools, and API calls.

## Available Regions

| Region Code | Full Name | Provider | Location |
|-------------|-----------|----------|----------|
| `us` | North America | AWS | United States |
| `eu` | Europe | AWS | Europe |
| `au` | Australia | AWS | Australia |
| `azure-na` | Azure North America | Azure | North America |
| `azure-eu` | Azure Europe | Azure | Europe |
| `gcp-na` | GCP North America | GCP | North America |
| `gcp-eu` | GCP Europe | GCP | Europe |

**Note**: Region codes are case-insensitive. `us`, `US`, and `na` all map to the US region.

## Why Regions Matter

- **Performance**: Closer regions = lower latency
- **Compliance**: Data residency requirements (e.g., GDPR)
- **Endpoints**: Each region has different API endpoints
- **Tokens**: Tokens are region-specific

## Finding Your Stack's Region

1. Log into Contentstack
2. Go to **Settings → Stack**
3. Check the **Region** field

Or check your stack's API key prefix:
- `blt` = US region
- `blteu` = EU region
- `bltau` = AU region
- `bltaz` = Azure
- `bltgcp` = GCP

---

## Delivery SDK (`@contentstack/delivery-sdk`)

### Basic Region Configuration

```typescript
import contentstack from "@contentstack/delivery-sdk";

const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: "us", // or "eu", "au", "azure-na", "azure-eu", "gcp-na", "gcp-eu"
});
```

### Using Endpoints Package (Recommended)

The `@timbenniks/contentstack-endpoints` package automatically resolves correct endpoints for all regions:

```bash
npm install @timbenniks/contentstack-endpoints
```

```typescript
import contentstack from "@contentstack/delivery-sdk";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

// omitHttps: true removes https:// prefix (needed for SDK host parameter)
const endpoints = getContentstackEndpoints(
  process.env.CONTENTSTACK_REGION || "us",
  true // omitHttps = true
);

const stack = contentstack.stack({
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

**Available endpoint properties:**
- `endpoints.contentDelivery` - REST CDN endpoint
- `endpoints.contentManagement` - Management API endpoint
- `endpoints.graphqlDelivery` - GraphQL endpoint
- `endpoints.preview` - REST Preview endpoint
- `endpoints.graphqlPreview` - GraphQL Preview endpoint

**Note**: When `omitHttps: true` is passed, all endpoints return domains without `https://` prefix, which is what SDKs expect for the `host` parameter.

### Region Aliases

The `getRegionForString()` function handles common aliases:

| Input | Resolves To |
|-------|-------------|
| `"us"`, `"na"`, `"aws-na"`, `"AWS-NA"` | `us` |
| `"eu"`, `"aws-eu"`, `"AWS-EU"` | `eu` |
| `"au"`, `"aws-au"`, `"AWS-AU"` | `au` |
| `"azure-na"`, `"AZURE-NA"` | `azure-na` |
| `"azure-eu"`, `"AZURE-EU"` | `azure-eu` |
| `"gcp-na"`, `"GCP-NA"` | `gcp-na` |
| `"gcp-eu"`, `"GCP-EU"` | `gcp-eu` |

---

## Management SDK (`@contentstack/management`)

### Basic Configuration

```typescript
import { client } from "@contentstack/management";

const managementClient = client({
  authtoken: process.env.CONTENTSTACK_MANAGEMENT_TOKEN!,
  host: "api.contentstack.io", // US region
  // For other regions:
  // host: "eu-api.contentstack.com", // EU
  // host: "au-api.contentstack.com", // AU
  // host: "azure-na-api.contentstack.io", // Azure NA
  // host: "azure-eu-api.contentstack.io", // Azure EU
  // host: "gcp-na-api.contentstack.io", // GCP NA
  // host: "gcp-eu-api.contentstack.io", // GCP EU
});

const stack = managementClient.stack({
  api_key: process.env.CONTENTSTACK_API_KEY!,
  management_token: process.env.CONTENTSTACK_MANAGEMENT_TOKEN!,
});
```

### Using Endpoints Package

```typescript
import { client } from "@contentstack/management";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

// omitHttps: true removes https:// prefix (needed for SDK host parameter)
const endpoints = getContentstackEndpoints(
  process.env.CONTENTSTACK_REGION || "us",
  true // omitHttps = true
);

const managementClient = client({
  authtoken: process.env.CONTENTSTACK_MANAGEMENT_TOKEN!,
  host: endpoints.contentManagement, // Already without https://
});

const stack = managementClient.stack({
  api_key: process.env.CONTENTSTACK_API_KEY!,
  management_token: process.env.CONTENTSTACK_MANAGEMENT_TOKEN!,
});
```

---

## Contentstack CLI (`@contentstack/cli`)

### Setting Region

```bash
# Set region globally
csdx config:set:region us

# Available region values:
# us, eu, au, azure-na, azure-eu, gcp-na, gcp-eu
# Or aliases: na, AWS-NA, AWS-EU, etc.
```

### Checking Current Region

```bash
csdx config:get region
```

### Region in CLI Plugins

CLI plugins automatically inherit the configured region:

```typescript
import { Command } from "@contentstack/cli-command";

export default class MyCommand extends Command {
  async run(): Promise<void> {
    // Region is automatically configured from CLI config
    const region = this.region; // Current region
    const cmaHost = this.cmaHost; // Management API host for region
    const cdaHost = this.cdaHost; // Delivery API host for region
    
    // Use endpoints directly
    const client = createClient(flags.stack, token, cmaHost);
  }
}
```

The CLI uses the official [Contentstack Regions JSON](https://artifacts.contentstack.com/regions.json) internally, so endpoints are automatically resolved.

---

## REST API

### Region-Specific Endpoints

| Region | REST CDN | REST Preview | Management API |
|--------|----------|--------------|----------------|
| US | `cdn.contentstack.io` | `rest-preview.contentstack.com` | `api.contentstack.io` |
| EU | `eu-cdn.contentstack.com` | `eu-rest-preview.contentstack.com` | `eu-api.contentstack.com` |
| AU | `au-cdn.contentstack.io` | `au-rest-preview.contentstack.io` | `au-api.contentstack.com` |
| Azure NA | `azure-na-cdn.contentstack.io` | `azure-na-rest-preview.contentstack.com` | `azure-na-api.contentstack.io` |
| Azure EU | `azure-eu-cdn.contentstack.io` | `azure-eu-rest-preview.contentstack.com` | `azure-eu-api.contentstack.io` |
| GCP NA | `gcp-na-cdn.contentstack.io` | `gcp-na-rest-preview.contentstack.com` | `gcp-na-api.contentstack.io` |
| GCP EU | `gcp-eu-cdn.contentstack.io` | `gcp-eu-rest-preview.contentstack.com` | `gcp-eu-api.contentstack.io` |

### Example Request

```bash
# US region
curl -X GET \
  'https://cdn.contentstack.io/v3/content_types/blog_post/entries/blt123?environment=production' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'access_token: YOUR_DELIVERY_TOKEN'

# EU region
curl -X GET \
  'https://eu-cdn.contentstack.com/v3/content_types/blog_post/entries/blt123?environment=production' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'access_token: YOUR_DELIVERY_TOKEN'
```

---

## GraphQL API

### Region-Specific Endpoints

| Region | GraphQL | GraphQL Preview |
|--------|---------|----------------|
| US | `graphql.contentstack.com` | `graphql-preview.contentstack.com` |
| EU | `eu-graphql.contentstack.com` | `eu-graphql-preview.contentstack.com` |
| AU | `au-graphql.contentstack.com` | `au-graphql-preview.contentstack.com` |
| Azure NA | `azure-na-graphql.contentstack.com` | `azure-na-graphql-preview.contentstack.com` |
| Azure EU | `azure-eu-graphql.contentstack.com` | `azure-eu-graphql-preview.contentstack.com` |
| GCP NA | `gcp-na-graphql.contentstack.com` | `gcp-na-graphql-preview.contentstack.com` |
| GCP EU | `gcp-eu-graphql.contentstack.com` | `gcp-eu-graphql-preview.contentstack.com` |

### Example Request

```bash
# US region
curl -X POST \
  'https://graphql.contentstack.com/graphql' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'access_token: YOUR_DELIVERY_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "{ allContentstackPage { nodes { title } } }"}'
```

---

## Environment Variables

### Recommended Setup

```bash
# .env
CONTENTSTACK_REGION=us
CONTENTSTACK_API_KEY=your_api_key
CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token
CONTENTSTACK_PREVIEW_TOKEN=your_preview_token
CONTENTSTACK_MANAGEMENT_TOKEN=your_management_token
CONTENTSTACK_ENVIRONMENT=production
```

### Using in Code

```typescript
// Single source of truth for region
const region = process.env.CONTENTSTACK_REGION || "us";

// Use with endpoints package (simple approach)
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";
// omitHttps: true for SDKs, false for direct API calls
const endpoints = getContentstackEndpoints(region, true);

// Or with validation (if you need explicit type checking)
import { getContentstackEndpoints, getRegionForString } from "@timbenniks/contentstack-endpoints";
const regionObj = getRegionForString(region);
const endpoints = getContentstackEndpoints(regionObj, true);
```

---

## Common Issues

### Wrong Region Error

**Symptom**: `401 Unauthorized` or `Invalid API key`

**Solution**: 
1. Verify your stack's region in Contentstack settings
2. Ensure SDK/CLI is configured with matching region
3. Check tokens are valid for the region

### Region Mismatch

**Symptom**: API calls fail with region-related errors

**Solution**:
- Use `@timbenniks/contentstack-endpoints` package for automatic endpoint resolution
- Verify `region` parameter matches your stack's actual region
- Check CLI region config: `csdx config:get region`

### Token Not Valid for Region

**Symptom**: Authentication fails even with correct credentials

**Solution**:
- Tokens are region-specific
- Generate new tokens in the correct region
- Verify token was created for the same region as your stack

---

## Best Practices

1. **Use Environment Variables**: Store region in `.env`, never hardcode
2. **Use Endpoints Package**: `@timbenniks/contentstack-endpoints` handles all endpoint resolution
3. **Use `omitHttps: true` for SDKs**: SDKs expect domains without `https://` prefix
4. **Use `omitHttps: false` for direct API calls**: When making HTTP requests directly, use full URLs
5. **Verify Region**: Always check your stack's region in Contentstack settings
6. **Consistent Configuration**: Use same region across all SDKs and tools
7. **Document Region**: Note region in project README or documentation

---

## Resources

- [Contentstack Regions Documentation](https://www.contentstack.com/docs/developers/contentstack-regions)
- [Endpoints Package](https://www.npmjs.com/package/@timbenniks/contentstack-endpoints)
- [Official Regions JSON](https://artifacts.contentstack.com/regions.json)
