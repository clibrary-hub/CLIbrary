# Live Preview Debugging

Preview symptoms rarely point directly at the cause. This is a symptom-first, systematic diagnostic guide. Classify the symptom, pick a rendering-strategy branch, trace the broken contract, apply the smallest fix, verify.

## Classify the symptom first

Six buckets cover almost every case:

| Bucket | Typical symptom |
|--------|-----------------|
| **1. Blank preview / setup error** | Iframe empty, "can't reach the website", setup status errors |
| **2. Published content in preview** | Preview loads but shows live content, not drafts |
| **3. Edits don't update** | Preview shows drafts but stays stale after edits |
| **4. Breaks after navigation** | First page works, links lose preview |
| **5. Wrong entry / wrong draft / leaks** | See someone else's edits, or the wrong entry content |
| **6. Visual Builder tagging failure** | Preview works but click opens wrong field |

Don't branch until the bucket is clear. Asking broad questions wastes the user's time.

## Classify the rendering strategy

The `ssr` init flag controls preview behavior, not your whole app:

- `ssr: false` → **CSR preview**: SDK listens for change events, re-fetches client-side, replaces state.
- `ssr: true` → **SSR preview**: iframe reloads with a `live_preview` hash on every change; server reads the hash and fetches drafts per request.
- **SSG preview mode**: Next.js Draft Mode, Pages Router Preview Mode, or Astro hybrid rendering to escape cached static output.
- **Middleware / BFF**: extra layer that can strip or forward the hash.

Ask only what you need to determine which.

## Five root-cause categories

### 1. Missing or dropped hash

**Symptoms:** published content in preview; works on first page, fails after navigation; "randomly stops working".

**Causes:** hash not in URL → not extracted → not forwarded to fetch, or navigation loses it, or middleware strips query params, or a redirect drops it.

**Investigate:**
- Check iframe URL: is `live_preview=...` present?
- Check network requests: are they hitting preview or delivery hosts?

### 2. Cached preview responses

**Symptoms:** preview feels connected but edits don't appear; old content sticks; different editors see each other's drafts.

**Causes:** CDN caches the preview endpoint; app-level cache doesn't bypass on hash; preview data accidentally persisted to DB.

**Investigate:**
- Check response `Cache-Control` headers.
- Check your caching code: does it bypass when `live_preview` is present?

### 3. Shared SDK instances in SSR

**Symptoms:** editor A sees editor B's drafts; inconsistent behavior under load.

**Causes:** a module-level global SDK instance is mutated per request by `livePreviewQuery()`, leaking state between concurrent requests.

**Investigate:**
- Is the Contentstack client created once at module scope and reused, or created fresh per request?
- Is `livePreviewQuery()` called on the shared instance?

See `./ssr-mode.md` for the request-scoped factory pattern.

### 4. Incorrect SDK configuration

**Symptoms:** preview panel loads but produces no updates.

**Causes:** `ssr: true` on a CSR site or vice versa; SDK not initialized in browser; wrong preview host for your region; SDK initialized too late (after content fetch).

**Investigate:**
- Read the `ContentstackLivePreview.init()` call.
- Confirm the `ssr` flag matches the architecture.
- Confirm the preview host matches the region (see `../concepts/regions.md`).

### 5. Wrong API endpoint

**Symptoms:** preview shows published content; API succeeds but returns old data.

**Causes:** hitting the delivery endpoint when the preview endpoint is required; preview token missing; `live_preview` header missing.

**Investigate:**
- What hostname are requests hitting (`cdn.contentstack.io` vs `rest-preview.contentstack.com`)?
- Are `preview_token` and `live_preview` in request headers?

## 6-step diagnostic walk

Walk in order. Stop at the first failing step.

### Step 1 — is the hash in the URL?

Open devtools, inspect the preview iframe's `src`:
- Has `live_preview=...` → continue.
- No hash → check **Settings → Live Preview → Environment Base URL** in Contentstack. Enable **Display Setup Status** for real-time feedback.

### Step 1b — can the iframe load your site?

If the panel is blank, check:
- `X-Frame-Options: DENY` on your site → remove or allow `https://*.contentstack.com`.
- Strict `Content-Security-Policy: frame-ancestors` → same.
- Or switch to "Always Open in New Tab" (Live Preview Utils v4.0.0+) to sidestep iframe restrictions.

### Step 2 — is the SDK initializing?

```typescript
console.log("SDK hash:", ContentstackLivePreview.hash);
console.log("SDK config:", ContentstackLivePreview.config);
```

- Empty hash and no config → init didn't run, or ran too early/too late, or ran server-side only. Confirm it runs in browser code (React/Vue component effect, Nuxt plugin `client: true`, etc.).

### Step 3 — are change events firing?

```typescript
ContentstackLivePreview.onEntryChange(() => {
  console.log("Entry change event received");
});
```

Edit something in the CMS. If no log appears:
- Handshake didn't complete → check console for SDK errors.
- `ssr` flag mismatches architecture.
- SDK init ran on the server but the callback registered only on the client.

### Step 4 — is the correct API being used?

Log your fetch calls. Preview requests should hit `rest-preview.contentstack.com` (or regional equivalent, e.g. `eu-rest-preview.contentstack.com`). Headers must include `preview_token` AND `live_preview=<hash>`.

If it's hitting `cdn.contentstack.io` → delivery endpoint; preview mode is not being applied to fetch.

### Step 5 — is caching disabled during preview?

Response headers on preview requests should include `Cache-Control: no-store`. Any cache (Next.js cache, Redis, CDN) must bypass when `live_preview` is in the URL.

### Step 6 — is the new data being rendered?

If fetches return correct draft data but the UI doesn't update:
- State isn't being replaced atomically (merging instead of replacing causes ghost fields).
- Framework-level cache (Next.js `fetch` cache, React Query) is returning stale data.
- Re-render isn't being triggered (stale closure, forgotten `key` prop).

## Common pitfalls by architecture

### CSR (`ssr: false`)

- Initializing the SDK after first fetch — the first fetch misses preview context.
- Never calling `onEntryChange()` — edits don't trigger a refetch.
- Stale closures capturing old state in the callback.
- Missing cleanup → duplicate listeners → duplicate fetches.

### SSR (`ssr: true`)

- Global SDK instance instead of request-scoped → state leaks between editors.
- Hash not extracted from `searchParams` per request.
- Navigation drops the `live_preview` query param.
- Caching preview responses at any layer.

### SSG

- No preview mode — static files never show drafts.
- Client-side patching drafts onto SSG output → hydration mismatches.
- Preview mode cookie set but never checked during fetch.
- `draftMode()` check missing → static build wins.

### Middleware / edge

- Middleware strips query params during URL rewrites.
- URL normalization removes the hash.
- Auth redirects lose the preview context during sign-in dance.

## Symptom → first check quick table

| Symptom | First check | Likely cause |
|---------|-------------|--------------|
| Published content in preview | URL has `live_preview`? | Hash missing or dropped |
| Old content persists after edit | `Cache-Control` header? | Caching not bypassed |
| Wrong entry / leaks | SDK per-request? | Shared SDK instance |
| No updates after edit | `onEntryChange` fires? | SDK not initialized or wrong `ssr` flag |
| Works then stops | Hash in nav URLs? | Hash lost on navigation |
| Iframe blank | `X-Frame-Options`/CSP? | Site blocks iframe |
| "SDK not initialized" in setup UI | init code present? | SDK missing or server-only |
| "Outdated SDK" | SDK version? | Update to `@contentstack/live-preview-utils` v4+ |
| "Preview Service not enabled" | Using new preview endpoints? | Migrate to Preview Service |

## Built-in Setup Status

Contentstack surfaces configuration errors in real time. Enable at **Settings → Live Preview → Display Setup Status**. It checks:

- Could not connect to website (CORS, `X-Frame-Options`, wrong base URL)
- Live Preview SDK not initialized (no init `postMessage` received)
- Outdated SDK version (update to v4.0.0+)
- Preview Service not enabled (migrate guide)
- Default environment not set

Make this the first place you look.

## Preview checklist

Apply to every preview-capable page:

- [ ] SDK initialized **before** first content fetch, in browser context.
- [ ] Hash extracted per request (SSR) or read from `ContentstackLivePreview.hash` (CSR).
- [ ] Preview API is used when hash is present.
- [ ] All caching bypassed when hash is present.
- [ ] Navigation preserves `live_preview`, `content_type_uid`, `entry_uid`, `locale`.
- [ ] Edit tags applied via `addEditableTags` in the data layer if Visual Builder is used.
- [ ] For SSR: Contentstack client created per request, not globally.
- [ ] For SSG: preview mode (Draft Mode / Preview Mode) detected and used for the fetch path.

## Verification after a fix

Short checklist to confirm the fix:

1. Reopen the entry in the CMS.
2. Confirm `live_preview=...` is in the iframe URL.
3. Edit a field, confirm the preview updates without reload.
4. Navigate to another page; confirm preview context persists.
5. If Visual Builder: click an element, confirm the correct field opens.

## When to escalate

- Configuration is correct but the Setup Status says "Preview Service not enabled" — stack migration needed, not a code fix.
- Iframe hits your domain but the host blocks embedding via organizational policy — coordinate with platform/security.
- Preview works in dev but not in Vercel preview deployments — check `X-Frame-Options` being injected by hosting middleware.

## Related

- `./concepts.md` — Live Preview fundamentals (the five components, session hash).
- `./csr-mode.md`, `./ssr-mode.md` — strategy-specific setup.
- `./visual-builder.md` — edit tags, `addEditableTags`, VB_EmptyBlockParentClass.
