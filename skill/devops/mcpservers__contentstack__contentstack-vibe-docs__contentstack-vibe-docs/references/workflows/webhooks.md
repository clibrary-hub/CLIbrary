# Webhooks

Contentstack webhooks push real-time event notifications to your systems. Use them for site rebuilds, search-index updates, Slack/Teams notifications, CI/CD triggers, and CDN invalidation.

## Event channels

Channels use the format `{module}.{action}`. Common examples:

| Channel | Fires on |
|---------|----------|
| `entries.create` | New entry saved |
| `entries.update` | Entry edited |
| `entries.publish` | Entry published to an environment |
| `entries.unpublish` | Entry unpublished |
| `entries.delete` | Entry deleted |
| `entries.workflow_stage_change` | Workflow stage transition |
| `assets.publish` | Asset published |
| `assets.unpublish` | Asset unpublished |
| `content_types.update` | Content type schema changed |
| `releases.deploy` | Release deployed |
| `$all` | Every event (use only if truly needed) |

Start narrow. Add `$all` only when the integration genuinely needs every event — otherwise you'll burn quota and drown your receiver.

## Payload shape

Every payload includes:

```json
{
  "module": "entry",
  "api_key": "blt0123...",
  "event": "publish",
  "triggered_at": "2026-04-24T10:00:00.000Z",
  "data": { "...": "entry or asset object" },
  "branch": "main"
}
```

Set `concise_payload: true` on the webhook if the receiver only needs identifiers — keeps payloads small and reduces PII exposure. Use full payloads only when the receiver needs the complete entry/asset data and can't re-fetch.

A `source` key appears when the event was triggered by a **release deploy**. Use it to detect release storms (see below).

## Signature verification (required)

Every webhook POST includes an `X-Contentstack-Signature` header. It is an HMAC-SHA256 signature computed over the raw request body using your webhook secret.

```typescript
// Next.js App Router — app/api/webhooks/contentstack/route.ts
import { createHmac, timingSafeEqual } from "node:crypto";

export async function POST(req: Request) {
  const raw = await req.text();
  const signature = req.headers.get("x-contentstack-signature") ?? "";
  const secret = process.env.CONTENTSTACK_WEBHOOK_SECRET!;

  const expected = createHmac("sha256", secret).update(raw).digest("hex");
  const ok =
    signature.length === expected.length &&
    timingSafeEqual(Buffer.from(signature), Buffer.from(expected));

  if (!ok) return new Response("invalid signature", { status: 401 });

  // Acknowledge fast, process async (see next section).
  const payload = JSON.parse(raw);
  queueWork(payload);
  return new Response("ok", { status: 200 });
}
```

Reject anything with a missing or invalid signature. Use `timingSafeEqual` — never string equality.

## Reliable receiver design

Four rules:

1. **Verify the signature first.** Drop unverified requests before any work.
2. **Return 2xx within 30 seconds.** Contentstack retries if the response is slow or non-2xx. Acknowledge the request, then process asynchronously on a queue (SQS, BullMQ, Cloud Tasks, Vercel Queues, etc).
3. **Process async.** Never call external APIs, rebuild sites, or run DB migrations in the request handler.
4. **Be idempotent.** Duplicate deliveries happen. Key on `data.uid + event + triggered_at` or similar and skip if already processed.

## Release-triggered webhook storms

A release with 50 items deploying to production fires **50 webhook events** — one per item. Naive receivers trigger 50 site rebuilds.

Detect and collapse:

```typescript
function isReleaseEvent(payload: { source?: { type?: string } }) {
  return payload.source?.type === "release";
}

// In your queue worker:
if (isReleaseEvent(payload)) {
  // Debounce: coalesce all events from the same release within a 60s window
  await debouncedTrigger("site-rebuild", { windowMs: 60_000 });
} else {
  await triggerNow("site-rebuild");
}
```

Debouncing keys: `source.uid` (release UID), `api_key` (stack), or environment name depending on your integration.

## Retries

- **Auto retries** — exponential backoff when Contentstack receives a non-2xx or times out. Limited attempts, then the delivery is marked failed.
- **Manual retries** — trigger re-execution of a specific failed delivery from the Contentstack UI execution logs.

Debug failed deliveries in the **Webhooks → Executions** log. Each row has the request URL, status code, response body, and retry history.

## Limits & scope

- Max **100 webhooks per stack**.
- Webhooks are a **global module** — configured on the stack, visible across branches — but each webhook can be scoped to a specific branch via the `branches` field.
- Organization-level **Webhook Configuration** sets max concurrent connections; bump it if you're seeing `429`s at the receiver side.

## Environment variables

```bash
CONTENTSTACK_WEBHOOK_SECRET=the_secret_you_set_when_creating_the_webhook
```

Never commit webhook secrets. Never log the raw signature or secret.

## Common integrations

| Target | Trigger | Notes |
|--------|---------|-------|
| Next.js ISR | `entries.publish`, `entries.unpublish` | Call `revalidateTag()` or `revalidatePath()` |
| Vercel / Netlify rebuild | `entries.publish` | POST to deploy hook URL |
| Algolia / Elasticsearch | `entries.publish/update/unpublish` | Upsert/delete documents |
| Slack / Teams | `entries.workflow_stage_change` | Route by workflow name |
| CDN purge | `entries.publish` | Purge by entry URL / tags |

## Red flags

- Using `$all` for narrow integrations — floods your receiver.
- Synchronous heavy work in the request handler — Contentstack retries, creates duplicate work.
- Comparing signatures with `===` instead of `timingSafeEqual`.
- Ignoring release storms — turns every release into N rebuilds.
- Hardcoding the webhook secret or echoing it in logs/errors.
