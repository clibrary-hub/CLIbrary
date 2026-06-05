# Tokens & Authentication

Contentstack has five credential types. Picking the wrong one is the most common security mistake. This doc gives you a decision tree, safety rules, and rate-limit guidance.

## Decision tree

```
What are you doing?
├── Reading published content for a website/app
│   └── Delivery Token (client-safe)
│
├── Reading draft content in Live Preview
│   └── Preview Token (client-safe for preview only)
│
├── Writing content from a server (CMS operations, migrations, imports)
│   └── Management Token (server-side only)
│
├── An interactive user session in a tool/UI
│   └── Authtoken (short-lived, user-scoped)
│   └── NOTE: may be disabled in SSO orgs — fall back to OAuth or Management Token
│
└── A third-party app calling Contentstack on behalf of users
    └── OAuth token (scoped, user consent)
```

## Token types at a glance

| Token | Reads | Writes | Client-safe? | Scope | Lifetime |
|-------|-------|--------|--------------|-------|----------|
| **Delivery Token** | Published only | No | ✅ Yes | Environment + branches | Long-lived |
| **Preview Token** | Drafts (Live Preview) | No | ✅ Yes (preview only) | Environment | Long-lived |
| **Management Token** | Everything in stack | Yes | ❌ Server-only | Stack | Long-lived |
| **Authtoken** | Inherits user permissions | Yes (as user) | ❌ Server-only | User session | Short-lived |
| **OAuth token** | Scoped + user permissions | Yes (as user) | ❌ Server-only | OAuth scopes | Access + refresh cycle |

## Header / env var conventions

```bash
# Frontend-safe
CONTENTSTACK_API_KEY=blt0123...
CONTENTSTACK_DELIVERY_TOKEN=cs0123...
CONTENTSTACK_PREVIEW_TOKEN=cspv0123...
CONTENTSTACK_ENVIRONMENT=production
CONTENTSTACK_REGION=us

# Server-only — never prefix with NEXT_PUBLIC_, NUXT_PUBLIC_, or equivalent
CONTENTSTACK_MANAGEMENT_TOKEN=csm0123...
```

Request headers:

```
# CDA (read published)
api_key: $CONTENTSTACK_API_KEY
access_token: $CONTENTSTACK_DELIVERY_TOKEN

# Preview
api_key: $CONTENTSTACK_API_KEY
preview_token: $CONTENTSTACK_PREVIEW_TOKEN

# CMA (management token)
api_key: $CONTENTSTACK_API_KEY
authorization: $CONTENTSTACK_MANAGEMENT_TOKEN

# CMA (user auth)
api_key: $CONTENTSTACK_API_KEY
authtoken: <authtoken from login>

# CMA (OAuth)
api_key: $CONTENTSTACK_API_KEY
authorization: Bearer <access_token>
```

## Hard rules

1. **Never expose Management Tokens or Authtokens in client code.** Not in JS bundles, not in public env vars, not in source control.
2. **Delivery Tokens are safe in frontend code** — they're read-only and scoped to an environment. But still load them from env vars so you can rotate without a code change.
3. **Preview Tokens are safe in frontend Live Preview code** — they only work against the preview host.
4. **Use a distinct management token per integration.** One leak shouldn't compromise everything.
5. **Rotate long-lived tokens at least quarterly** — or on any role change, employee departure, or incident.
6. **Store in a secret manager** in production (AWS Secrets Manager, Vercel env vars, 1Password, Doppler, etc).

## Frontend / server boundary example

```typescript
// ✅ lib/contentstack.ts — client-safe
import contentstack from "@contentstack/delivery-sdk";

export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,          // ok
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!, // ok
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  region: process.env.CONTENTSTACK_REGION || "us",
});

// ✅ server/contentstack-admin.ts — server-only, never imported by client code
import contentstackManagement from "@contentstack/management";

export const mgmt = contentstackManagement.client().stack({
  api_key: process.env.CONTENTSTACK_API_KEY!,
  management_token: process.env.CONTENTSTACK_MANAGEMENT_TOKEN!, // must stay server-side
});

// ❌ Never do this
export const badStack = contentstack.stack({
  apiKey: process.env.NEXT_PUBLIC_API_KEY!,
  deliveryToken: process.env.NEXT_PUBLIC_MANAGEMENT_TOKEN!, // exposed to browser!
  environment: "production",
});
```

## OAuth (third-party apps)

For apps installed into a customer's stack: OAuth with scopes. See `../authentication/oauth.md` for the full Auth.js v5 implementation pattern. Key points:

- Request only the scopes you need (e.g., `content_type:read`, `entry:write`). See `../authentication/oauth.md` scope table.
- Store refresh tokens in a DB, not cookies, for long-lived integrations.
- Rotate access tokens near expiry with the refresh token before calling CMA.
- Prefer PKCE for public clients (SPAs, mobile).

## Rate limits

Platform defaults per organization:

- **10 req/s individual operations**
- **1 req/s bulk operations**

Responses include:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset` (seconds until reset)

On `429`, back off exponentially with jitter. Don't retry faster than `X-RateLimit-Reset`. See `../workflows/environments-publishing.md` for reference implementation.

Automation tokens hit limits first because they do bulk work. Consider:
- Batching CMA calls (e.g., 100 items per release add-call).
- Using the `@contentstack/cli` bulk plugins, which handle rate limits automatically.
- Serializing writes per content type to avoid conflict retries.

## SSO organizations

When the org enables SSO:

- **Authtokens may be restricted or disabled entirely.** Scripts relying on authtokens stop working.
- Migrate automation to **Management Tokens** (for server-side stack operations).
- Migrate interactive/third-party flows to **OAuth** with appropriate scopes.
- Coordinate with the Contentstack org admin — they can clarify policy for your org.

## Red flags

- `NEXT_PUBLIC_CONTENTSTACK_MANAGEMENT_TOKEN` — a fatal mistake.
- One "god token" shared across CI, backend, and migration scripts.
- Tokens committed to git, even in `.env.example`.
- Using a management token in the browser by routing through a public API route without auth — you've just built a proxy to full write access.
- Ignoring `X-RateLimit-Reset` and busy-looping on 429s.
- Assuming authtokens work in SSO orgs.
