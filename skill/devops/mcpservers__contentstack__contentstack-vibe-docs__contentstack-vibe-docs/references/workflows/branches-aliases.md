# Branches & Aliases

Branches give you an isolated workspace for schema and content changes. Aliases give you zero-downtime deployment and instant rollback.

## Mental model

- **Branch** = a full copy of a subset of stack modules (content types, entries, assets, etc.) for isolated development.
- **Alias** = a named pointer to a branch. Frontend code references the alias; you swap which branch it points to without touching code.

Analogy: branches are git branches; aliases are DNS records.

## Branch basics

- Creating a branch copies the source branch's content types, global fields, entries, and assets.
- **Max 5 branches per stack.** Plan lifetimes accordingly.
- Only **one branch create/delete at a time per organization** — concurrent operations are serialized.
- Only Owner, Admin, Developer roles can create/delete/manage branches.

## Branch-specific vs global modules

**Branch-specific** (copied/isolated per branch):
- Content types, global fields
- Entries, assets
- Publish queue, releases
- Languages, extensions, audit logs, labels, search

**Global** (shared across all branches):
- Environments
- Webhooks (can be scoped to a branch via the `branches` field)
- Workflows, publish rules
- Users, roles, teams
- Tokens (delivery, management, preview)

This split matters: creating a new content type on `feature-x` has no effect on `main` until merged, but creating a webhook on `feature-x` makes it visible on `main` too (unless branch-scoped).

## Aliases

Aliases are named pointers. Hardcode the alias — `deploy`, `prod`, `live` — in your frontend SDK init, not a branch UID. To switch which branch is live, reassign the alias. No code change needed.

```typescript
// lib/contentstack.ts
export const stack = contentstack.stack({
  apiKey: process.env.CONTENTSTACK_API_KEY!,
  deliveryToken: process.env.CONTENTSTACK_DELIVERY_TOKEN!,
  environment: process.env.CONTENTSTACK_ENVIRONMENT!,
  branch: process.env.CONTENTSTACK_BRANCH ?? "deploy", // alias, not branch UID
});
```

**Constraints:**
- Two aliases can point to the same branch.
- A branch and an alias **cannot share the same UID**.
- Reassigning an alias is instant — no propagation delay for subsequent API calls.

## Zero-downtime deployment pattern

```
1. Create feature branch `feature-redesign` from `main`
2. Make schema + content changes on `feature-redesign`
3. Deploy a preview site pointing at `branch: "feature-redesign"`
4. QA validates preview
5. Reassign the `deploy` alias from `main` → `feature-redesign`
6. Production site now sees new content, zero deploy downtime
7. Rollback: reassign `deploy` back to `main`
```

Because the SDK is initialized with an alias (not a branch UID), no code change or redeploy is needed for the switch.

## CI/CD pattern

```yaml
# Simplified CI
- name: Create branch
  run: curl -X POST $CMA_HOST/branches -d '{"branch":{"uid":"ci-$SHA","source":"main"}}'
- name: Apply schema + content changes
  run: node scripts/apply-changes.mjs --branch=ci-$SHA
- name: Preview deploy
  run: vercel --build-env CONTENTSTACK_BRANCH=ci-$SHA
- name: E2E tests
  run: npm run test:e2e -- --base-url=$PREVIEW_URL
- name: Promote on success
  run: curl -X PUT $CMA_HOST/aliases/deploy -d '{"alias":{"target_branch":"ci-$SHA"}}'
```

Pair this with **releases** for atomic content deployment inside the branch (see `./releases.md`).

## Branch strategy

- **Keep branch lifetimes short.** Long-lived branches drift from `main` and create merge conflicts on content types.
- **Trunk-based is preferred.** Short feature branches, fast merge.
- **Do not use branches as permanent environments.** Use environments for that. Branches are for changes-in-flight.

## SDK initialization — always pass the branch

Always pass `branch` explicitly, even when targeting `main`:

```typescript
contentstack.stack({
  apiKey: ...,
  deliveryToken: ...,
  environment: ...,
  branch: process.env.CONTENTSTACK_BRANCH ?? "main",
});
```

If omitted, SDKs default to `main`, but explicit is safer (CI envs, preview envs, and rollbacks all rely on the env var).

For REST calls, the header name is `branch`:

```
curl -H "api_key: $API_KEY" \
     -H "access_token: $DELIVERY_TOKEN" \
     -H "branch: deploy" \
     https://cdn.contentstack.io/v3/content_types/blog_post/entries
```

## Red flags

- Using a long-lived branch as a permanent environment — drift compounds.
- Hardcoding a branch UID (e.g. `feature-redesign`) in frontend code — defeats alias-based rollback.
- Forgetting that webhooks are global — a webhook created on a feature branch fires for `main` too unless branch-scoped.
- Expecting content-type schema changes on a feature branch to be queryable via `main` — they aren't until merged.
- Running more than one create/delete branch op concurrently per org — they serialize and can appear stuck.
