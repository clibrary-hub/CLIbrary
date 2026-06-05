# Variants & Personalize

Contentstack has two mechanisms for audience-targeted content: **Variants** (lightweight field overrides on a single entry) and **Personalize** (the runtime engine that evaluates audiences and selects which variant to serve). They are used together.

## Variants vs separate entries — decision rule

**Use variants** when:
- 80%+ of the content is the same across audiences.
- Only specific fields differ: headline, hero image, CTA copy, price, etc.
- You want a single source of truth with per-audience overrides.

**Use separate entries** when:
- The structure differs significantly (different modular blocks, different references).
- Each audience needs its own editorial lifecycle, workflow, or SEO metadata.
- The content is genuinely a different page, not a variation.

Start with variants. Split into separate entries only if variants start feeling forced.

## Variants on an entry

A variant is a field-level override on a parent entry. Content editors create one or more variants, each scoped to an **audience** (or audience group). When the Personalize engine decides audience X matches, the SDK returns the parent entry with variant X's fields merged in.

Structure:
```
Entry (base)
├── Field: title = "Welcome"
├── Field: cta  = "Sign up"
└── Variants
    ├── audience:us_enterprise
    │   ├── cta = "Request a demo"
    │   └── hero_image = <us-enterprise-hero>
    └── audience:eu_smb
        └── cta = "Start free trial"
```

Fields not overridden in a variant fall through to the base entry.

## Audiences

Audiences are rule-based segments evaluated at request time: geo, traits, cookies, UTM params, logged-in user attributes, etc. They're configured in the Personalize project, not the stack.

Experiences bundle (audience + variant-selection strategy) and can be A/B tested (split-traffic), targeted (all-of-audience), or multivariate.

## Integration pattern

High-level flow:

```
1. User request arrives
2. Personalize SDK evaluates audiences → resolves variant alias(es) for user
3. Contentstack SDK fetches the entry with the variant alias(es) applied
4. Render
```

**Runtime evaluation (client-side or server-side):**

```typescript
import { Personalize } from "@contentstack/personalize-edge-sdk"; // or client SDK
import contentstack from "@contentstack/delivery-sdk";

const personalize = Personalize.init(process.env.PERSONALIZE_PROJECT_UID!, {
  edgeApiUrl: "https://personalize-edge.contentstack.com",
});

// 1. Resolve variants for this user
const userContext = {
  userUid: cookieUserUid,
  attributes: { country: geoCountry, plan: "enterprise" },
};
const variantAlias = await personalize.getVariantAliases(userContext);
// e.g. "cs_personalize_variant_uid_abc,cs_personalize_variant_uid_xyz"

// 2. Fetch entry with variants applied
const entry = await stack
  .contentType("landing_page")
  .entry(entryUid)
  .variants(variantAlias) // SDK merges variant fields into the base entry
  .fetch();
```

The SDK handles the merge — your rendering code is unchanged, fields just contain the variant values.

## SSR on the edge (recommended for performance)

For server-rendered sites, call the **Personalize Edge API** at the CDN layer instead of evaluating audiences in your app server. This keeps audience evaluation fast (low-latency edge KV lookups) and keeps user attributes close to the edge.

Vercel Edge Middleware example:

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import { Personalize } from "@contentstack/personalize-edge-sdk";

export async function middleware(req: NextRequest) {
  const personalize = Personalize.init(process.env.PERSONALIZE_PROJECT_UID!);
  const variantAlias = await personalize.getVariantAliases({
    userUid: req.cookies.get("cs_user")?.value,
    attributes: { country: req.geo?.country ?? "US" },
  });

  const res = NextResponse.next();
  res.headers.set("x-variant-alias", variantAlias);
  res.cookies.set("cs_user", userUid, { path: "/" });
  return res;
}
```

Then in your page/route:

```typescript
const variantAlias = headers().get("x-variant-alias") ?? "";
const entry = await stack
  .contentType("landing_page")
  .entry(entryUid)
  .variants(variantAlias)
  .fetch();
```

## Client-side rendering

If you must resolve variants client-side (pure SPA, no SSR), use the client SDK and a loading state while audiences resolve. Expect a flash of base content on first render.

## Publishing variants

Each variant is a separate publishable unit on the entry. From the CMS, editors can publish a subset of variants to an environment. The parent entry must also be published — variants don't publish orphaned.

## Environment variables

```bash
PERSONALIZE_PROJECT_UID=pz0123...
# Contentstack creds are the same as always
CONTENTSTACK_API_KEY=blt0123...
CONTENTSTACK_DELIVERY_TOKEN=cs0123...
CONTENTSTACK_ENVIRONMENT=production
```

The Personalize project UID is not secret (it's visible in client requests) but keeping it in env vars lets you swap projects between dev/staging/prod.

## Live Preview + variants

When previewing an entry, pass both the preview hash AND the variant alias you want to preview. Editors can select a variant from the preview UI; your app should respect the variant alias in the URL or preview context.

## Red flags

- Using variants when you actually need separate entries — you end up with a 30-field entry where 25 fields have overrides, and the override noise becomes unmanageable.
- Evaluating audiences client-side on SSR pages — creates hydration mismatches.
- Forgetting to publish the parent entry after publishing variants — users see nothing.
- Hardcoding audience UIDs in code instead of using human-readable aliases from the Personalize project.
- Shipping variants without any analytics to measure whether they actually improved the target metric.
