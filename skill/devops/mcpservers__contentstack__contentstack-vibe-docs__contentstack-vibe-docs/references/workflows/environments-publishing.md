# Environments & Publishing

Environments are deployment targets. Publishing is the act of promoting content to one. This doc covers environment design, publishing lifecycle, the Sync API, and the publish queue.

## Environment design

Treat environments as deployment targets, aligned with your pipeline:

```
development → staging → production
```

- **Max 5 environments per stack** (default plan limit).
- Environments are **global** — shared across all branches (see `./branches-aliases.md` for the module split).
- Each environment has a CDN endpoint and delivery-token scoping.

## Publishing fundamentals

- Content is a **draft** until explicitly published to an environment.
- Publishing can target **multiple environments** and **multiple locales** in a single call.
- **Reference publishing:** use `api_version: 3.2` on the CMA request so the full reference tree is resolved and published. Otherwise, referenced entries must be published separately — a common footgun where a page appears broken because its author or category wasn't published.

```
POST /v3/content_types/{ct_uid}/entries/{entry_uid}/publish
Header: api_version: 3.2
Body:
{
  "entry": {
    "environments": ["production", "staging"],
    "locales": ["en-us", "fr-fr"]
  }
}
```

See `../api/content-management-api.md` for full request/response shapes.

## Token types (summary — full detail in security/)

- **Delivery Token** — reads *published* content. Environment-scoped. Safe client-side.
- **Preview Token** — reads *draft* content. Live Preview only.
- **Management Token** — read/write stack-level access. **Server-side only. Never ship to frontend.**

See `../security/tokens-authentication.md` for a full decision tree.

## CDA base URLs (region-specific)

| Region | Host |
|--------|------|
| AWS NA | `cdn.contentstack.io` |
| AWS EU | `eu-cdn.contentstack.com` |
| AWS AU | `au-cdn.contentstack.com` |
| Azure NA | `azure-na-cdn.contentstack.com` |
| Azure EU | `azure-eu-cdn.contentstack.com` |
| GCP NA | `gcp-na-cdn.contentstack.com` |
| GCP EU | `gcp-eu-cdn.contentstack.com` |

Don't hardcode — use `@timbenniks/contentstack-endpoints` and see `../concepts/regions.md`.

## SDK initialization checklist

Required:
- `apiKey` (stack API key)
- `deliveryToken` (for Delivery SDK) OR `preview_token` (for Live Preview)
- `environment` name
- `region` (so endpoints resolve correctly)

Optional but recommended:
- `branch` (default: `main`) — always pass explicitly in CI/preview envs

## Sync API

The Sync API gives you a delta stream of published content changes. Use it for:
- Static-site generators that rebuild on content change.
- Offline/mobile apps with local content caches.
- Any system that wants near-real-time updates without polling.

**Flow:**

1. First request (init): returns **all published content** for the scope plus a `sync_token`.
2. Subsequent requests with the `sync_token`: return only **created / updated / deleted / published / unpublished** items since last sync.

```
GET /v3/stacks/sync?init=true&content_type_uid=blog_post&environment=production
→ { items: [...], sync_token: "blt..." }

GET /v3/stacks/sync?sync_token=blt...
→ { items: [...delta...], sync_token: "blt..." }
```

**Pagination:** responses over a page size return a `pagination_token`. Follow it until no token is returned, then persist the final `sync_token` for the next run.

## Publish queue

Every publish/unpublish operation lands in the queue. You can:
- Inspect pending/in-progress/completed/failed operations.
- **Cancel a scheduled publish before execution.**
- Query status by UID.

Each branch has its own queue.

## Scheduled publishing

CMA supports `scheduled_at` (ISO-8601) on publish calls to defer execution:

```json
{ "entry": { "environments": ["production"], "scheduled_at": "2026-05-01T09:00:00Z" } }
```

Scheduled publishes can be cancelled from the UI or via CMA until the scheduled time. If the entry is edited after scheduling, the latest version is used at publish time — not the version at scheduling time.

## Rate limits

Platform limits (per organization):
- **10 requests/second** individual ops.
- **1 request/second** bulk ops.
- Responses include `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers on CMA.

On `429`, back off with exponential delay + jitter. The `@contentstack/cli` bulk-publish plugin handles rate limiting automatically — prefer it over hand-rolled loops for large jobs.

```typescript
async function withBackoff<T>(fn: () => Promise<T>, tries = 5): Promise<T> {
  for (let attempt = 0; attempt < tries; attempt++) {
    try {
      return await fn();
    } catch (err: unknown) {
      if (!is429(err) || attempt === tries - 1) throw err;
      const base = 2 ** attempt * 500;
      const jitter = Math.random() * 250;
      await new Promise((r) => setTimeout(r, base + jitter));
    }
  }
  throw new Error("unreachable");
}
```

## Troubleshooting: "I published but content isn't showing"

Check in order:

1. **Right environment?** Entry published to `production` but frontend using delivery token scoped to `staging` → content invisible.
2. **Right branch?** Entry on a feature branch; frontend alias points to `main`.
3. **References unpublished?** Page publishes fine but its author/category weren't published → missing data. Re-publish with `api_version: 3.2`.
4. **Delivery cache?** Contentstack's CDN has short TTLs but not zero — a forced refresh or a few seconds wait clears stale hits.
5. **Using preview token instead of delivery token?** Preview token serves drafts, not published content.

## Red flags

- Using a management token in client code — huge security hole.
- Forgetting `api_version: 3.2` on reference publishes — partial content goes live.
- Polling the CDA for changes when the Sync API exists — rate limit waste.
- Hardcoding region hosts — breaks on region migration.
- Missing exponential backoff on bulk scripts — hits 429 and dies.
