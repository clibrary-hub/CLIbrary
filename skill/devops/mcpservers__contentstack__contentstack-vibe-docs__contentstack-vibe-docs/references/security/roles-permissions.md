# Roles & Permissions

Contentstack access control has three layers: **built-in roles**, **custom roles**, and **teams** for scale. Tokens inherit permissions from the identity or scope they represent. Design for least privilege.

## Built-in roles

Try these first — most cases don't need custom roles.

| Role | Capabilities |
|------|--------------|
| **Owner** | Full access; stack billing; only one per stack; cannot be removed |
| **Admin** | Everything except billing and transferring ownership |
| **Developer** | Content types, global fields, extensions, webhooks, environments, workflows, publish rules |
| **Content Manager** | Entries, assets, locales, workflows (cannot modify schema or settings) |

Use the narrowest built-in role that covers the user's responsibilities. Only reach for custom roles when the built-ins are too broad.

## Custom roles

Use when access must be scoped by:

- **Content type** — e.g., a marketing editor can only touch `blog_post` and `landing_page`.
- **Environment** — e.g., a junior editor can publish to `staging` but not `production`.
- **Locale** — e.g., a regional team manages only `fr-fr`.
- **Branch** — e.g., agency reviewers see only their feature branch.
- **Action** — read / create / update / delete / publish, independently.

Permissions are expressed per module + instance + action. Use the `$all` instance selector to grant across all instances of a module:

```
Module: entry
Content type: blog_post
Locale: $all
Actions: read, create, update
```

Keep custom roles small and composable — 2-4 narrowly-scoped roles are easier to reason about than one 20-permission mega-role.

## Permission merging

When a user has multiple roles:

- **Allowed actions merge permissively.** Role A grants `read`, role B grants `create` → user has both.
- **Explicit denials override grants.** If any role denies `publish`, user cannot publish even if another role allows it.

This becomes risky fast when roles are reused across teams or stacks. Audit role overlaps when adding users to new teams. A user who picks up an `Admin` role from team X will inherit full admin on every stack that team has access to.

## Teams

Teams map users → stack roles in bulk. Strongly prefer teams over per-user role assignment at scale:

- One change to a team membership propagates to all stacks that team has access to.
- Onboarding/offboarding is one step instead of N.
- Audit trail is cleaner — team roles are visible in one place.

Small org (≤10 users, 1-2 stacks): per-user assignment is fine. Bigger: use teams.

## Tokens inherit from identity

Tokens don't have their own role system — they inherit from the identity or scope they were created under:

- **Delivery Token** — scoped to an environment and a set of branches. Read-only. Published content only.
- **Preview Token** — scoped to an environment. Read-only. Draft content (Live Preview).
- **Management Token** — stack-scoped. Read/write across everything the stack holds. **Server-side only.** Cannot cross stacks.
- **Authtoken** — user-scoped. Inherits all the user's roles. Short-lived.
- **OAuth token** — scoped via OAuth scopes + user's roles. Third-party-app pattern.

See `./tokens-authentication.md` for selecting the right token.

## SSO edge cases

In SSO-enabled organizations:

- **Authtokens may be restricted or disabled.** Automation that relied on authtokens breaks.
- Switch automation to **management tokens** (for stack-scoped server work) or **OAuth tokens with scoped access** (for third-party integrations).
- Org owners can override some SSO restrictions — coordinate with the Contentstack org admin.

## Rate limits

Rate limits are per-org, not per-token, but you'll hit them fastest with high-privilege automation tokens. Headers on every CMA response:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

On `429`, back off with exponential delay + jitter. See `../workflows/environments-publishing.md` → Rate limits for a reference implementation.

## Least-privilege checklist

- [ ] User has the narrowest built-in role that covers their work.
- [ ] Custom roles are scoped by content type + environment + locale where possible.
- [ ] Automation uses a **separate** management token per integration so one leak doesn't compromise everything.
- [ ] Management tokens are stored in env vars or a secret manager — never in code, never in git.
- [ ] Delivery tokens in frontend code are scoped to the minimum branches + environments needed.
- [ ] Role overlaps are audited when users join new teams.
- [ ] Rotation schedule exists for long-lived tokens (quarterly minimum).

## Red flags

- One shared "automation" management token used by every script — leak = full compromise.
- Giving Content Managers the Developer role "just in case" — expands blast radius.
- Relying on authtokens in SSO orgs — will break on SSO rollout.
- Custom roles with `$all` in every field — that's just a built-in role with extra steps.
- Forgetting that explicit deny wins — users mysteriously can't publish because a secondary role denies it.
