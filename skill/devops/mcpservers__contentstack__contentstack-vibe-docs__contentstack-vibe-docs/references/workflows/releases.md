# Releases

Releases group multiple entries and assets so they deploy together atomically. Use them for campaign launches, coordinated redesigns, multi-locale content rollouts, or any change where related content must go live at the same time.

## When to use releases

**Use releases when:**
- A marketing campaign spans multiple entries that must publish together.
- A site redesign touches many pages and you want a single go/no-go moment.
- You need a repeatable artifact you can deploy first to staging, then to production.
- A CI/CD pipeline coordinates content with code deployments.

**Do NOT use releases for:**
- Routine single-entry publishes — just publish directly.
- Ongoing editorial workflow — use workflows for per-entry review and publishing.

## Release workflow

1. **Create** a release with a descriptive name (max 50 chars).
2. **Add items** — specify the entry/asset UID, content type, locale, and which *version* to deploy.
3. **Deploy to staging** environment → validate in preview.
4. **Deploy to production** on success.

Releases are **branch-specific**. A release on `main` cannot be deployed against `feature-x`.

## Version pinning matters

When you add an entry to a release, you pin it to a specific version. If the entry is edited later:

- The release still contains the pinned version.
- Updating the release item to the **latest version** does NOT automatically add any new references introduced by that update. You must add those references manually.

This is the most common footgun — a release deploys successfully but a newly-referenced entry is missing because it wasn't added to the release.

## Limits

- Max **100 items per single API call** when adding items. Batch larger sets.
- Release titles: **50 characters max**.
- Auto-reference inclusion is not automatic on version bumps — see above.

## Webhook storms

Release deployment fires **one webhook event per item**. A 50-item release = 50 webhook deliveries. Uncoordinated receivers can trigger 50 site rebuilds.

Collapse by detecting `source.type === "release"` and `source.uid === <release_uid>` in the webhook payload, then debouncing downstream actions on the release UID. See `../workflows/webhooks.md` → "Release-triggered webhook storms".

## CI/CD integration pattern

```
1. Developer opens PR touching content + code
2. CI creates a release via CMA, adds changed entries/assets
3. Deploy release → staging environment
4. Run E2E tests against staging
5. On green → deploy release → production
6. On red → leave release, deploy nothing, fail the PR
```

Combine with **branches + aliases** for zero-downtime content+schema deployment:
- Create branch `feature-x`, make schema and content changes there.
- Create a release on that branch with the new content.
- On merge: reassign the production alias to `feature-x`, deploy the release.
- Rollback: reassign the alias back.

See `./branches-aliases.md`.

## CMA endpoints (sketch)

```
POST   /v3/releases                              Create a release
POST   /v3/releases/{release_uid}/items          Add items (max 100 per call)
POST   /v3/releases/{release_uid}/deploy         Deploy to an environment/locale
DELETE /v3/releases/{release_uid}                Delete the release
```

See `../api/content-management-api.md` for full CMA request/response shapes and auth headers.

Release deployments are auditable — every deploy appears in audit logs and execution history. For token handling see `../security/tokens-authentication.md`.

## Red flags

- Treating a release as "just a publish button" — it's a versioned artifact, and version pinning behavior surprises people.
- Forgetting to add newly-referenced entries when bumping release item versions.
- Not debouncing webhooks on release deploys — floods rebuilders.
- Using releases for single-entry publishes — unnecessary overhead.
