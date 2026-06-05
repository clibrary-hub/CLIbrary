# Contentstack REST API

Complete guide to using Contentstack's REST API for content delivery.

## Base URL

```
https://{region}-cdn.contentstack.io/v3/{resource}
```

**Preview URL** (for unpublished content):
```
https://{region}-rest-preview.contentstack.com/v3/{resource}
```

## Authentication

All requests require headers:

```http
api_key: YOUR_API_KEY
access_token: YOUR_DELIVERY_TOKEN
```

**For Preview:**
```http
api_key: YOUR_API_KEY
access_token: YOUR_PREVIEW_TOKEN
live_preview: PREVIEW_HASH
```

## Common Endpoints

### Fetch Single Entry

```http
GET /v3/content_types/{content_type_uid}/entries/{entry_uid}?environment=production
```

**Example:**
```bash
curl -X GET \
  'https://cdn.contentstack.io/v3/content_types/blog_post/entries/blt123?environment=production' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'access_token: YOUR_DELIVERY_TOKEN'
```

### Fetch Multiple Entries

```http
GET /v3/content_types/{content_type_uid}/entries?environment=production
```

**Query Parameters:**
| Parameter | Description |
|-----------|-------------|
| `environment` | Environment name (required) |
| `locale` | Locale code (optional, defaults to default locale) |
| `query` | JSON query for filtering (optional) |
| `skip` | Number of entries to skip (pagination) |
| `limit` | Number of entries to return (pagination, max 100) |
| `include_count` | Include total count in response |
| `asc` | Field to sort ascending |
| `desc` | Field to sort descending |

**Example Query:**
```json
{
  "query": {
    "title": { "$regex": "tutorial", "$options": "i" },
    "published_date": { "$lte": "2024-01-01" }
  },
  "skip": 0,
  "limit": 10,
  "asc": "published_date"
}
```

### Query Operators

```json
{
  "query": {
    "$or": [
      { "category": { "$in": ["tech", "design"] } },
      { "tags": { "$regex": "javascript" } }
    ],
    "published_date": { "$gte": "2024-01-01" }
  }
}
```

| Operator | Description |
|----------|-------------|
| `$eq` | Equal to |
| `$ne` | Not equal to |
| `$gt` | Greater than |
| `$gte` | Greater than or equal |
| `$lt` | Less than |
| `$lte` | Less than or equal |
| `$in` | Matches any in array |
| `$nin` | Matches none in array |
| `$exists` | Field exists |
| `$regex` | Regular expression |
| `$and` | Logical AND |
| `$or` | Logical OR |

### Including References

**Single Reference:**
```http
GET /v3/content_types/blog_post/entries/blt123?include[]=author
```

**Multiple References:**
```http
GET /v3/content_types/blog_post/entries/blt123?include[]=author&include[]=category&include[]=tags
```

**Deep Includes** (include references within references):
```http
GET /v3/content_types/blog_post/entries/blt123?include[]=author.published_date
```

**Note**: Keep total includes to 10 or fewer for optimal performance.

### Field Selection

**Only specific fields:**
```http
?only[BASE][]=title&only[BASE][]=url
```

**Exclude fields:**
```http
?except[BASE][]=internal_notes
```

### Fetch Assets

**Single Asset:**
```http
GET /v3/assets/{asset_uid}?environment=production
```

**Query Parameters:**
- `environment`: Environment name (required)
- `version`: Asset version (optional)

**Search Assets:**
```http
GET /v3/assets?environment=production
```

**Query Parameters:**
- `environment`: Environment name (required)
- `query`: JSON query for filtering (optional)
- `skip`: Pagination offset
- `limit`: Max assets (max 100)

**Example Query:**
```json
{
  "query": {
    "title": { "$regex": "logo", "$options": "i" }
  },
  "skip": 0,
  "limit": 20
}
```

## Response Format

**Single Entry:**
```json
{
  "entry": {
    "uid": "blt123",
    "title": "Entry Title",
    "url": "/entry-url",
    "publish_details": {
      "environment": "production",
      "locale": "en-us",
      "time": "2024-01-01T00:00:00.000Z"
    },
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z",
    "created_by": "user_uid",
    "updated_by": "user_uid",
    "ACL": {},
    "_version": 1,
    "field_name": "field_value"
  }
}
```

**Multiple Entries:**
```json
{
  "entries": [
    { "uid": "blt123", "title": "..." },
    { "uid": "blt456", "title": "..." }
  ],
  "count": 2
}
```

## Error Handling

| Status | Description |
|--------|-------------|
| `200` | Success |
| `400` | Bad Request |
| `401` | Unauthorized |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Server Error |

**Error Response:**
```json
{
  "error_code": 141,
  "error_message": "Entry not found",
  "errors": { "entry_uid": ["Entry does not exist"] }
}
```

## Rate Limiting

Check headers:
```http
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9950
X-RateLimit-Reset: 1640995200
```

On `429`, back off with exponential delay + jitter. Never busy-loop.

## Pagination

- **Default page size:** 25 entries.
- **Maximum `limit`:** 100 entries per request.
- **No cursor pagination** on REST. Use `skip` + `limit`, and `include_count=true` to know when to stop.

```http
GET /v3/content_types/blog_post/entries?limit=100&skip=0&include_count=true
→ { entries: [...], count: 347 }

GET /v3/content_types/blog_post/entries?limit=100&skip=100
GET /v3/content_types/blog_post/entries?limit=100&skip=200
GET /v3/content_types/blog_post/entries?limit=100&skip=300
```

For deltas (site rebuilds, incremental caches), prefer the **Sync API** over polling — see `../workflows/environments-publishing.md` → Sync API.

## Region aliases

Some responses and tooling accept region codes via aliases (e.g. `na` ↔ `us`, `AWS-NA` ↔ `us`). The canonical region codes and hosts are in `../concepts/regions.md`. Stick to the canonical codes in code (`us`, `eu`, `au`, `azure-na`, `azure-eu`, `gcp-na`, `gcp-eu`) to avoid edge cases.

## Query operator gotchas

- `regex` accepts a case-insensitivity modifier via `options: "i"`:
  ```json
  { "title": { "$regex": "tutorial", "$options": "i" } }
  ```
  Without `options`, matching is case-sensitive.
- GraphQL's `regex` argument name may vary — check the GraphQL schema you're querying.

## Performance Optimization

### 1. Keep Payloads Under 5 MB

Large payloads slow down API responses and can cause timeouts. Monitor response sizes:

```bash
# Check response size
curl -I 'https://cdn.contentstack.io/v3/content_types/blog_post/entries?environment=production' \
  -H 'api_key: YOUR_API_KEY' \
  -H 'access_token: YOUR_DELIVERY_TOKEN' | grep -i content-length
```

**If payload exceeds 5 MB:**
- Use projection queries to limit fields
- Reduce number of includes
- Implement pagination
- Split requests into smaller batches

### 2. Limit Includes to 10 or Fewer

Each include adds overhead. Keep total includes to **10 or fewer**:

**Example - Too Many Includes (Avoid):**
```http
GET /v3/content_types/blog_post/entries/entry_uid?include[]=author&include[]=category&include[]=tags&include[]=related_posts&include[]=comments&include[]=likes&include[]=shares&include[]=metadata&include[]=translations&include[]=variants
```

**Example - Optimized Includes:**
```http
GET /v3/content_types/blog_post/entries/entry_uid?include[]=author&include[]=category
```

**Split Large Includes:**
If you need many references, split them into multiple calls:

```typescript
// Instead of one call with 10 includes
const entry = await fetchEntryWithManyIncludes(uid);

// Split into multiple calls
const entry = await fetchEntry(uid);
const author = await fetchAuthor(entry.author_uid);
const category = await fetchCategory(entry.category_uid);
// ... fetch other references as needed
```

### 3. Optimize Includes and Reference Depth

**Limit Includes:**
- Keep total number of includes to **10 or fewer**
- Avoid deep nesting of references
- Only include references you actually need

**Avoid Deep Reference Nesting:**
```http
# Avoid
GET /v3/content_types/blog_post/entries/entry_uid?include[]=author.company.employees.department.manager

# Prefer
GET /v3/content_types/blog_post/entries/entry_uid?include[]=author
```

Then fetch nested references separately if needed.

### 4. Use Projection Queries

Use `only` and `except` parameters to limit response size:

**Only Specific Fields:**
```http
GET /v3/content_types/blog_post/entries?only[BASE][]=title&only[BASE][]=url&only[BASE][]=published_date
```

**Exclude Fields:**
```http
GET /v3/content_types/blog_post/entries?except[BASE][]=internal_notes&except[BASE][]=draft_content
```

### 5. Implement Pagination

Always implement pagination for large datasets:

```http
GET /v3/content_types/blog_post/entries?skip=0&limit=10&include_count=true
```

**Best Practices:**
- Use reasonable page sizes (10-50 items)
- Always include `include_count=true` for pagination UI
- Implement infinite scroll or page-based navigation

### 6. Use Modular Blocks Instead of Multiple References

When building pages with multiple content blocks, use **Modular Blocks** instead of multiple content type references:

**Why Modular Blocks:**
- Reduces number of includes needed
- All blocks fetched in single call
- More efficient than multiple references
- Better performance

**Example Structure:**
```typescript
// Content Type: Page
// Field: blocks (Modular Block)
// Blocks: HeroBlock, ContentBlock, CTABlock, GalleryBlock

// Single call fetches all blocks
const page = await fetchPage("page_uid");
// All blocks are included automatically, no includes needed
```

### 7. Implement Caching Strategy

**CDN Caching:**
- Contentstack automatically caches API responses via CDN
- Cache is invalidated when content is published
- Leverage CDN for better performance

**Application-Level Caching:**
```typescript
// Cache frequently-used data
const cache = new Map();

async function getCachedEntry(uid: string) {
  const cacheKey = `entry_${uid}`;

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  const entry = await fetchEntry(uid);
  cache.set(cacheKey, entry);

  // Set TTL (time to live)
  setTimeout(() => cache.delete(cacheKey), 3600000); // 1 hour

  return entry;
}
```

**Cache Frequently-Used Data:**
- User groups, titles, metadata
- FAQ sections
- Navigation menus
- Content that doesn't change often

### 8. Implement Lazy Loading

Load content progressively instead of all at once:

**Example - Lazy Load Sections:**
```typescript
// Load critical content first
const hero = await fetchHero();
const mainContent = await fetchMainContent();

// Load secondary content later
setTimeout(async () => {
  const sidebar = await fetchSidebar();
  const footer = await fetchFooter();
}, 100);
```

### 9. Optimize Your Code

**Eliminate Redundancies:**
- Remove duplicate API calls
- Check if data is already fetched before requesting
- Avoid making queries unique with random numbers/timestamps
- Cache responses in your application

**Example - Avoid Duplicate Calls:**
```typescript
// BAD: Fetches same data multiple times
function renderPage() {
  const entry = await fetchEntry(uid);
  const author = await fetchAuthor(entry.author_uid);
  const entry2 = await fetchEntry(uid); // Duplicate!
}

// GOOD: Fetch once, reuse
function renderPage() {
  const entry = await fetchEntry(uid);
  const author = await fetchAuthor(entry.author_uid);
  // Reuse entry object
}
```

### 10. Batch Operations When Needed

If you need multiple includes that exceed limits, batch them:

```typescript
// Split includes into batches
async function fetchEntryWithBatchedIncludes(uid: string) {
  // Batch 1: Core references
  const entry = await fetchEntry(uid, ["author", "category"]);

  // Batch 2: Additional references
  const tags = await fetchTags(entry.tag_uids);

  // Merge results
  return { ...entry, tags };
}
```

### 11. Monitor API Usage

- Check rate limit headers in responses
- Implement retry logic with exponential backoff
- Monitor response times and payload sizes
- Set up alerts for API errors

### Performance Checklist

When making API calls, ensure:

- ✅ Response payload < 5 MB
- ✅ Total includes ≤ 10
- ✅ Using projection queries (`only`/`except`)
- ✅ Implementing pagination
- ✅ Avoiding deep reference nesting
- ✅ Caching frequently-used data
- ✅ Using lazy loading for non-critical content
- ✅ Eliminating duplicate calls
- ✅ Handling errors gracefully
- ✅ Using SDK when possible

## Best Practices Summary

1. **Keep payloads under 5 MB**
2. **Limit includes to 10 or fewer**
3. **Use projection queries** (`only`/`except`)
4. **Always implement pagination**
5. **Cache frequently-used data**
6. **Handle errors gracefully**
7. **Use SDK when possible** - Prefer `@contentstack/delivery-sdk` over direct API calls

## Regional Considerations

Always specify the correct region in your API calls:

- Use region-specific endpoints (e.g., `eu-cdn.contentstack.io` for EU)
- Ensure tokens are valid for the region
- Consider latency when choosing region
- See [Regions Guide](../concepts/regions.md) for complete configuration details

See [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for code patterns.

