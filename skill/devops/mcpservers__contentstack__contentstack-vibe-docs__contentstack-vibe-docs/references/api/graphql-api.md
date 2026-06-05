# Contentstack GraphQL API

Complete guide to using Contentstack's GraphQL API for content delivery.

## Base URL

```
https://{region}-graphql.contentstack.com/graphql
```

**Preview URL:**
```
https://{region}-graphql-preview.contentstack.com/graphql
```

## Authentication

```http
api_key: YOUR_API_KEY
access_token: YOUR_DELIVERY_TOKEN
```

**For Preview:**
```http
api_key: YOUR_API_KEY
access_token: YOUR_PREVIEW_TOKEN
live_preview: PREVIEW_HASH
preview_token: YOUR_PREVIEW_TOKEN
include_applied_variants: "true"
```

## Query Structure

### Basic Query

```graphql
query {
  allContentstackPage(where: { url: "/" }) {
    nodes {
      uid
      title
      url
    }
  }
}
```

### Fetch Single Entry

```graphql
query GetEntry($uid: String!) {
  contentstackPage(uid: $uid) {
    uid
    title
    url
    description
    image {
      url
      title
    }
  }
}
```

**Variables:**
```json
{ "uid": "blt123" }
```

### Fetch Multiple Entries

```graphql
query GetEntries {
  allContentstackBlogPost(
    where: { title: { regex: "tutorial", options: "i" } }
    skip: 0
    limit: 10
    sort: [{ published_date: ASC }]
  ) {
    nodes {
      uid
      title
      url
      published_date
    }
    total
  }
}
```

### Query Filters

```graphql
query {
  allContentstackBlogPost(
    where: {
      and: [
        { category: { in: ["tech", "design"] } }
        { published_date: { gte: "2024-01-01" } }
      ]
    }
  ) {
    nodes {
      title
      category
    }
  }
}
```

**Filter Operators:**
| Operator | Description |
|----------|-------------|
| `eq` | Equal to |
| `ne` | Not equal to |
| `gt` | Greater than |
| `gte` | Greater than or equal |
| `lt` | Less than |
| `lte` | Less than or equal |
| `in` | Matches any in array |
| `nin` | Matches none in array |
| `regex` | Regular expression |
| `exists` | Field exists |
| `and` | Logical AND |
| `or` | Logical OR |

### Including References

References are included by querying nested fields:

```graphql
query {
  contentstackBlogPost(uid: "blt123") {
    title
    author {
      uid
      title
      bio
    }
    category {
      uid
      title
    }
  }
}
```

### Fragments

```graphql
fragment BlogPostFields on ContentstackBlogPost {
  uid
  title
  url
  published_date
  excerpt
}

query {
  allContentstackBlogPost {
    nodes {
      ...BlogPostFields
      author {
        title
      }
    }
  }
}
```

### Assets

```graphql
query {
  contentstackAsset(uid: "blt123") {
    url
    title
    filename
    content_type
    file_size
    dimension {
      width
      height
    }
  }
}
```

### Search Assets

```graphql
query {
  allContentstackAsset(
    where: { title: { regex: "logo", options: "i" } }
    limit: 20
  ) {
    nodes {
      uid
      url
      title
    }
    total
  }
}
```

## Error Handling

GraphQL returns `200` with errors in response:

```json
{
  "data": null,
  "errors": [
    {
      "message": "Entry not found",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["contentstackPage"]
    }
  ]
}
```

## JavaScript Example

```typescript
import { request } from "graphql-request";

const GRAPHQL_HOST = "graphql.contentstack.com";

const query = `
  query GetPage($url: String!) {
    allContentstackPage(where: { url: $url }) {
      nodes {
        uid
        title
        url
      }
    }
  }
`;

const headers = {
  api_key: process.env.CONTENTSTACK_API_KEY!,
  access_token: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
};

const data = await request(
  `https://${GRAPHQL_HOST}/graphql`,
  query,
  { url: "/" },
  headers
);
```

## GraphQL vs REST

| Feature | GraphQL | REST |
|---------|---------|------|
| Fetch specific fields | ✅ Built-in | Use `only[]` param |
| References | Auto-included when queried | Use `include[]` param |
| Multiple queries | Single request | Multiple requests |
| Response size | Only requested data | Full entry data |
| Learning curve | Higher | Lower |

## Performance Optimization

### 1. Keep Payloads Under 5 MB

Large payloads slow down API responses and can cause timeouts. GraphQL helps by only fetching requested fields, but still monitor response sizes.

**If payload exceeds 5 MB:**
- Query only needed fields (don't fetch entire entries)
- Reduce depth of nested references
- Implement pagination
- Split queries into smaller requests

### 2. Query Only Needed Fields

GraphQL's main advantage is fetching only what you need. Don't query entire entries:

**Bad - Fetching Everything:**
```graphql
query {
  allContentstackBlogPost {
    nodes {
      # Fetching all fields unnecessarily
      uid
      title
      url
      description
      content
      author { uid title bio email phone address }
      category { uid title description metadata }
      tags { uid title description }
      # ... many more fields
    }
  }
}
```

**Good - Only Needed Fields:**
```graphql
query {
  allContentstackBlogPost {
    nodes {
      uid
      title
      url
      author {
        title
      }
    }
  }
}
```

### 3. Limit Reference Depth

Avoid deep nesting of references:

**Avoid:**
```graphql
query {
  contentstackBlogPost(uid: "blt123") {
    author {
      company {
        employees {
          department {
            manager {
              # Too deep!
            }
          }
        }
      }
    }
  }
}
```

**Prefer:**
```graphql
query {
  contentstackBlogPost(uid: "blt123") {
    author {
      title
    }
  }
}
```

Then fetch nested references separately if needed.

### 4. Use Fragments for Reusability

Fragments help organize queries and reduce duplication:

```graphql
fragment BlogPostFields on ContentstackBlogPost {
  uid
  title
  url
  published_date
  excerpt
}

fragment AuthorFields on ContentstackAuthor {
  uid
  title
  bio
}

query {
  allContentstackBlogPost {
    nodes {
      ...BlogPostFields
      author {
        ...AuthorFields
      }
    }
  }
}
```

### 5. Implement Pagination

Always implement pagination for large datasets:

```graphql
query GetEntries($skip: Int!, $limit: Int!) {
  allContentstackBlogPost(skip: $skip, limit: $limit) {
    nodes {
      title
      url
    }
    total
  }
}
```

**Best Practices:**
- Use reasonable page sizes (10-50 items)
- Always query `total` for pagination UI
- Implement infinite scroll or page-based navigation

### 6. Use Modular Blocks Instead of Multiple References

When building pages with multiple content blocks, use **Modular Blocks** instead of multiple content type references:

**Why Modular Blocks:**
- Reduces query complexity
- All blocks fetched in single query
- More efficient than multiple references
- Better performance

**Example Structure:**
```graphql
query {
  contentstackPage(uid: "page_uid") {
    title
    blocks {
      # All block types automatically included
      ... on ContentstackHeroBlock {
        title
        image { url }
      }
      ... on ContentstackContentBlock {
        content
      }
      ... on ContentstackCTABlock {
        button_text
        button_url
      }
    }
  }
}
```

### 7. Implement Caching Strategy

**CDN Caching:**
- Contentstack automatically caches GraphQL responses via CDN
- Cache is invalidated when content is published
- Leverage CDN for better performance

**Application-Level Caching:**
```typescript
import { request } from "graphql-request";

const cache = new Map();

async function getCachedQuery(query: string, variables: any) {
  const cacheKey = `${query}_${JSON.stringify(variables)}`;

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  const data = await request(endpoint, query, variables, headers);
  cache.set(cacheKey, data);

  // Set TTL
  setTimeout(() => cache.delete(cacheKey), 3600000); // 1 hour

  return data;
}
```

**Cache Frequently-Used Queries:**
- Navigation menus
- Footer content
- FAQ sections
- Content that doesn't change often

### 8. Implement Lazy Loading

Load content progressively instead of all at once:

**Example - Lazy Load Sections:**
```typescript
// Load critical content first
const hero = await queryHero();
const mainContent = await queryMainContent();

// Load secondary content later
setTimeout(async () => {
  const sidebar = await querySidebar();
  const footer = await queryFooter();
}, 100);
```

**Framework-Specific:**
- **React**: Use `React.lazy()` and `Suspense`
- **Vue**: Use dynamic imports
- **Next.js**: Use dynamic imports with `ssr: false`

### 9. Optimize Your Code

**Eliminate Redundancies:**
- Remove duplicate queries
- Check if data is already fetched before requesting
- Avoid making queries unique with random numbers/timestamps
- Cache responses in your application

**Example - Avoid Duplicate Queries:**
```typescript
// BAD: Queries same data multiple times
async function renderPage() {
  const entry = await queryEntry(uid);
  const author = await queryAuthor(entry.author_uid);
  const entry2 = await queryEntry(uid); // Duplicate!
}

// GOOD: Query once, reuse
async function renderPage() {
  const entry = await queryEntry(uid);
  const author = await queryAuthor(entry.author_uid);
  // Reuse entry object
}
```

### 10. Batch Operations When Needed

If you need multiple references that exceed limits, batch them:

```typescript
// Split queries into batches
async function fetchEntryWithBatchedReferences(uid: string) {
  // Batch 1: Core data
  const entry = await request(endpoint, `
    query {
      contentstackBlogPost(uid: "${uid}") {
        title
        author { title }
        category { title }
      }
    }
  `);

  // Batch 2: Additional references
  const tags = await request(endpoint, `
    query {
      allContentstackTag(where: { entries: { in: ["${uid}"] } }) {
        nodes { title }
      }
    }
  `);

  // Merge results
  return { ...entry.contentstackBlogPost, tags: tags.allContentstackTag.nodes };
}
```

### 11. Use Variables for Dynamic Queries

Always use variables instead of string interpolation:

**Bad:**
```graphql
query {
  contentstackPage(uid: "hardcoded_uid") {
    title
  }
}
```

**Good:**
```graphql
query GetPage($uid: String!) {
  contentstackPage(uid: $uid) {
    title
  }
}
```

This enables query caching and prevents injection issues.

### 12. Monitor API Usage

- Check rate limit headers in responses
- Implement retry logic with exponential backoff
- Monitor response times and payload sizes
- Set up alerts for API errors

### Performance Checklist

When making GraphQL queries, ensure:

- ✅ Response payload < 5 MB
- ✅ Querying only needed fields
- ✅ Limiting reference depth
- ✅ Using fragments for reusability
- ✅ Implementing pagination
- ✅ Caching frequently-used queries
- ✅ Using lazy loading for non-critical content
- ✅ Eliminating duplicate queries
- ✅ Handling errors gracefully
- ✅ Using variables for dynamic queries

## Best Practices Summary

1. **Query only needed fields** - Don't fetch entire entries
2. **Use fragments** - For reusable query parts
3. **Implement pagination** - Use `skip` and `limit`
4. **Handle errors** - Check `errors` array in response
5. **Cache queries** - GraphQL responses are cacheable
6. **Use variables** - For dynamic queries instead of string interpolation
7. **Limit reference depth** - Avoid deep nesting

## Regional Considerations

Always specify the correct region in your GraphQL endpoint:

- Use region-specific endpoints (e.g., `eu-graphql.contentstack.com` for EU)
- Ensure tokens are valid for the region
- Consider latency when choosing region
- See [Regions Guide](../concepts/regions.md) for complete configuration details

See [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for more patterns.

