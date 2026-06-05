# Localization

Contentstack models multilingual content as a tree rooted at a **master language**, with each language optionally falling back to another. Fields can be localized per language or shared. Entries exist per locale once localized, otherwise inherit from the fallback chain.

## Master language — a permanent choice

The master language is set **at stack creation** and **cannot be changed**. It is the root of every fallback chain.

Pick it deliberately:
- The language of your primary market, OR
- The language in which content is authored first, OR
- `en-us` if in doubt and you're an English-first org

Everything else (add/remove locales, reconfigure fallbacks) is reversible. The master is not.

## Fallback chains

Each non-master language can have **one fallback language**. Inheritance chains follow the fallback pointer until they hit a language with content or reach the master.

Example:

```
fr-ca  →  fr-fr  →  en-us (master)
de-at  →  de-de  →  en-us (master)
ja-jp  →          en-us (master)   # direct fallback
```

Authoring in `fr-fr` automatically flows to `fr-ca` unless `fr-ca` has its own localized version. Changing a fallback relationship later affects inheritance for existing content — do it carefully.

## Localized vs unlocalized entries

This distinction causes most localization confusion.

| | Localized entry | Unlocalized entry |
|---|---|---|
| Exists as | Independent copy with its own fields, version history, publishing status, workflow state | Lives only in the fallback chain |
| Editors | Can edit per locale independently | Edit in the fallback source; changes propagate |
| CDA response | Returns the localized entry directly | Returns the fallback content with `_in_progress` or `locale` metadata indicating inheritance |
| Locked in? | Yes — localizing is one-way per `(entry, locale)` pair | No — you can always localize later |

**Rule of thumb:** only localize when the content genuinely differs. Localizing "just because" creates drift — a change in the master won't reach translated copies anymore.

## Non-localizable fields

Mark these **non-localizable** at the content-type level:

- Identifiers (SKUs, ISBNs, product codes)
- Numeric/boolean data (prices, quantities, flags)
- Dates and timestamps
- Coordinates
- Shared assets (logos, icons that are language-agnostic)
- URLs and slugs that shouldn't differ per locale
- References to shared entities

Keep these **localizable** (default):

- Titles, headlines, body copy
- Descriptions, summaries, meta tags
- Alt text on translated images
- CTAs, button labels
- Language-specific URLs/slugs

## Content Management — locale APIs

```
# List locales configured on the stack
GET /v3/locales

# Create a new locale with a fallback
POST /v3/locales
Body: { "locale": { "code": "fr-ca", "name": "French (Canada)", "fallback_locale": "fr-fr" } }
```

Headers: standard CMA auth (`api_key` + `authorization: <management_token>`).

## Delivery — querying by locale

Pass `locale` explicitly in every CDA call. **Default behavior without `include_fallback=true`: only the exact locale is checked.** A missing localized entry returns nothing.

```
GET /v3/content_types/blog_post/entries?locale=fr-ca
```

To get fallback behavior (the whole chain, first hit wins):

```
GET /v3/content_types/blog_post/entries?locale=fr-ca&include_fallback=true
```

With the TypeScript SDK:

```typescript
const entry = await stack
  .contentType("blog_post")
  .entry(entryUid)
  .locale("fr-ca")
  .includeFallback()
  .fetch();
```

**GraphQL:** pass `locale` as an argument; fallback behavior is controlled per query — check the GraphQL schema for the `include_fallback`/`fallback` argument name on your schema version.

## Multi-locale publishing

From the master-language entry, editors can publish to multiple locales at once:

```json
// CMA publish payload
{
  "entry": {
    "environments": ["production"],
    "locales": ["en-us", "fr-fr", "de-de"]
  }
}
```

Notes:
- Only the **latest version** of each localized entry publishes.
- Plan limits cap simultaneous locale counts — check your plan.
- Scheduled publishing works per-locale.

## Editorial gotchas

- **Localized entry versions can only be deleted from the master-language entry's delete modal.** If you need to remove a stale translation, open the master entry, not the localized one.
- Re-localizing after master changes requires re-copying fields manually (or via a CMA script) — Contentstack does not auto-propagate once localized.
- Workflow state is per-localized-entry — a page can be `Approved` in `en-us` and `Draft` in `fr-fr` simultaneously.

## Strategy patterns

**Global brand, many markets, shared visuals, translated text:**
- Most fields localizable (text).
- Assets, prices, SKUs non-localizable.
- Translation agencies localize entries after master approval.

**Regional sites with divergent layouts:**
- Separate entries per region — not locale-localization.
- Use references and a region field instead.

**Multi-channel (web + mobile + in-store):**
- Don't model channels as locales. Use separate content types or variants (see `../personalization/variants-and-personalize.md`).

## Red flags

- Changing master language post-launch — you can't.
- Localizing entries preemptively before content actually differs — creates maintenance drift.
- Forgetting `include_fallback=true` on CDA calls and wondering why some locales return empty.
- Translating SKUs, prices, or coordinates — mark those non-localizable.
- Expecting master-language edits to propagate to already-localized entries — they don't.
