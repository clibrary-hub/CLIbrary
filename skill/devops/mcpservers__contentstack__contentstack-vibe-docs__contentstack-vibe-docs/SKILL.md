---
name: contentstack-vibe-docs
description: >-
  Comprehensive Contentstack CMS documentation for building web applications.
  Covers REST API, GraphQL API, Content Management API, Image Delivery API,
  TypeScript SDKs, Live Preview, Visual Builder, OAuth authentication, data
  modeling, webhooks, releases, workflows, branches, roles, localization,
  variants/personalization, Launch deployments, and framework patterns for
  Next.js, Nuxt, and Gatsby. Use when implementing any Contentstack feature.
license: MIT
metadata:
  author: timbenniks
  version: "2.1"
---

# Contentstack Documentation for AI Agents

This skill contains ~13,500 lines across 30+ reference files. **Read the routing table, pick the 1-3 files you actually need, and stop.** Never read everything.

## Routing table

| Task | File |
|------|------|
| Quick code pattern lookup | [QUICK_REFERENCE.md](references/QUICK_REFERENCE.md) |
| Contentstack basics | [concepts/base-concepts.md](references/concepts/base-concepts.md) |
| Design content models, choose references vs modular blocks vs global fields, taxonomy | [concepts/data-modeling-best-practices.md](references/concepts/data-modeling-best-practices.md) |
| Localization, fallback chains, non-localizable fields | [concepts/localization.md](references/concepts/localization.md) |
| Regions, endpoints, region-aware hosts | [concepts/regions.md](references/concepts/regions.md) |
| Fetch content (REST) | [api/rest-api.md](references/api/rest-api.md) |
| Fetch content (GraphQL) | [api/graphql-api.md](references/api/graphql-api.md) |
| Create/update/delete/publish, modular block schema, CMA headers | [api/content-management-api.md](references/api/content-management-api.md) |
| Transform images, asset folders, asset limits, file_uid | [api/image-delivery-api.md](references/api/image-delivery-api.md) |
| TypeScript Delivery SDK | [sdk/delivery-sdk.md](references/sdk/delivery-sdk.md) |
| Live Preview overview | [live-preview/concepts.md](references/live-preview/concepts.md) |
| Live Preview CSR (`ssr: false`) | [live-preview/csr-mode.md](references/live-preview/csr-mode.md) |
| Live Preview SSR (`ssr: true`), per-request factory, hash isolation | [live-preview/ssr-mode.md](references/live-preview/ssr-mode.md) |
| Visual Builder, edit tags, `addEditableTags`, `VB_EmptyBlockParentClass` | [live-preview/visual-builder.md](references/live-preview/visual-builder.md) |
| Debug Live Preview / Visual Builder failures | [live-preview/debugging.md](references/live-preview/debugging.md) |
| Next.js patterns, Draft Mode, `revalidateTag` | [frameworks/nextjs.md](references/frameworks/nextjs.md) |
| Nuxt patterns | [frameworks/nuxt.md](references/frameworks/nuxt.md) |
| Gatsby patterns | [frameworks/gatsby.md](references/frameworks/gatsby.md) |
| Pick the right token (delivery/preview/management/authtoken/OAuth) | [security/tokens-authentication.md](references/security/tokens-authentication.md) |
| Roles, custom permissions, teams | [security/roles-permissions.md](references/security/roles-permissions.md) |
| OAuth login with Auth.js v5 (Next.js) | [authentication/oauth.md](references/authentication/oauth.md) |
| Webhooks: signatures, event channels, release storms | [workflows/webhooks.md](references/workflows/webhooks.md) |
| Releases: atomic coordinated deploys | [workflows/releases.md](references/workflows/releases.md) |
| Workflows & publish rules | [workflows/content-workflows.md](references/workflows/content-workflows.md) |
| Branches & aliases: zero-downtime deploys | [workflows/branches-aliases.md](references/workflows/branches-aliases.md) |
| Environments, publishing, Sync API, rate limits | [workflows/environments-publishing.md](references/workflows/environments-publishing.md) |
| Variants & Personalize | [personalization/variants-and-personalize.md](references/personalization/variants-and-personalize.md) |
| CLI plugins — overview & quickstart | [extensions/cli-plugins/overview.md](references/extensions/cli-plugins/overview.md) |
| CLI plugins — commands, flags, arguments | [extensions/cli-plugins/commands.md](references/extensions/cli-plugins/commands.md) |
| CLI plugins — publishing, testing, troubleshooting | [extensions/cli-plugins/publishing.md](references/extensions/cli-plugins/publishing.md) |
| Developer Hub apps (App SDK, UI locations, API proxy) | [extensions/devhub-apps.md](references/extensions/devhub-apps.md) |
| Contentstack Launch: deployments, env sync | [extensions/launch.md](references/extensions/launch.md) |
| Real-world code patterns | [examples/practical-examples.md](references/examples/practical-examples.md) |
| Package versions | [VERSIONS.md](references/VERSIONS.md) |

## Common task combinations

| Scenario | Files (in order) |
|----------|------------------|
| New Next.js project | base-concepts → delivery-sdk → nextjs |
| New Nuxt project | base-concepts → delivery-sdk → nuxt |
| Add Live Preview to Next.js | live-preview/concepts → live-preview/ssr-mode → nextjs |
| Add Visual Builder to existing site | live-preview/visual-builder |
| Debug broken preview | live-preview/debugging |
| Build a CRUD/migration script | content-management-api → security/tokens-authentication |
| Full-stack with user login | delivery-sdk → nextjs → oauth |
| Webhook-driven rebuild | workflows/webhooks → workflows/environments-publishing |
| Zero-downtime content deploy | workflows/branches-aliases → workflows/releases |
| Multi-locale rollout | concepts/localization → workflows/environments-publishing |
| Deploy to Launch from CI | extensions/launch → workflows/webhooks |
| Responsive image optimization | api/image-delivery-api |
| Quick snippet | QUICK_REFERENCE.md |

## Decision helpers

**Which API?**
Read published content → REST / GraphQL / Delivery SDK. Write content → Content Management API. Transform images → Image Delivery API.

**Which SDK?**
`@contentstack/delivery-sdk` for reads (frontend/backend). `@contentstack/management` for writes (server-only, never frontend).

**Which Live Preview mode?**
The `ssr` flag controls how the CMS iframe updates, not your app's rendering strategy.
- `ssr: false` — postMessage. CMS sends data to iframe, client re-fetches and updates without reload.
- `ssr: true` — iframe reload with `?live_preview=<hash>&entry_uid=...`. Server reads params per request.

For `ssr: true`, **create a fresh Contentstack client per request** (factory pattern). Sharing one global client leaks preview state between concurrent editors. See `live-preview/ssr-mode.md`.

**Which token?**
Frontend reads → Delivery Token (safe). Preview reads → Preview Token (safe). Server writes → Management Token (NEVER frontend). User sessions → Authtoken or OAuth. Full decision tree in `security/tokens-authentication.md`.

## Ask before coding

Before implementing, confirm with the developer:

- **Region** (US, EU, AU, Azure NA/EU, GCP NA/EU) — affects every endpoint.
- **Framework** (Next.js, Nuxt, Gatsby, etc.) — determines Live Preview mode.
- **Environment** (dev/staging/production) — scopes the delivery token.
- **Credentials in env vars?** — never ask for the values themselves.

## Security (summary)

Never ask for, log, output, or hardcode API keys, tokens, or secrets. Always use `process.env.*` references. Never use Management Tokens in frontend code. If a developer pastes a real token, warn them and recommend rotating it. Full rules: `security/tokens-authentication.md`.

## Red flags

- Reading all reference files instead of routing to 1-3.
- Hardcoding credentials or exposing management tokens to the browser.
- Hardcoding region hosts instead of using `@timbenniks/contentstack-endpoints`.
- Mixing Delivery SDK patterns with Management SDK patterns.
- Mixing REST and GraphQL patterns in one query.
- Sharing a module-level Contentstack client across SSR preview requests.
- Forgetting `api_version: 3.2` for reference publishing.
- Forgetting `.includeReference()` then wondering why references are undefined.
- Ignoring `X-RateLimit-Reset` and busy-looping on 429s.
