# Workflows & Publish Rules

Contentstack workflows gate content through named stages (e.g., Draft → Review → Approved → Published). Publish rules gate the actual publish action to environments. They solve different problems and compose.

## Workflows vs publish rules

| | Workflows | Publish rules |
|---|-----------|---------------|
| **Controls** | Who can move an entry between stages | Who can publish/unpublish an entry, and to which environment |
| **Attached to** | One per content type, per branch | Content type + environment + locale + action |
| **Audit** | Every transition logged | Every publish gated |
| **Use for** | Editorial review flow | Last-mile environment protection (e.g., "only leads can push to prod") |

You commonly use both: a workflow for Draft→Review→Approved, and a publish rule that only lets `Approved` entries publish to `production`.

## Designing workflow stages

**Keep it simple — 3 to 5 stages handles most cases.** Typical shape:

```
Draft  →  In Review  →  Approved  →  Published
```

Platform limit: **20 stages max per stack**. One workflow per content type per branch.

Each stage defines:
- **Who can advance** — role or specific users who can move entries out of this stage.
- **Allowed next stages** — constrain transitions (e.g., Review can go to Approved or back to Draft, but not straight to Published).
- **Due dates / assignments** (optional) — SLA on time in stage.
- **Notifications** — webhook and email hooks per stage.

## Prevent self-advancement

Stops the person who just edited an entry from also approving it — required for real review processes.

Requires **at least two distinct reviewers**. If your reviewer role has only one user, prevent-self-advancement does nothing useful.

Recommendation: either a reviewer role with ≥2 members, or two separate reviewer roles with at least one human in each.

## Automation via webhooks

Subscribe to `entries.workflow_stage_change` to trigger external automation when entries move stages. Payload includes the old stage, new stage, entry UID, and user who performed the transition.

Common patterns:
- **Draft → Review** → ping the review Slack channel.
- **Approved → Published** → trigger build pipeline.
- **Any stage → Rejected** → email the author.

See `./webhooks.md` for receiver design.

## Publish rules

Scope fields:

| Field | Purpose |
|-------|---------|
| Branch | Which branch the rule applies to |
| Content type | Which content type |
| Language / locale | Which locale |
| Environment | Which environment |
| Action | `publish` or `unpublish` |
| Required workflow stage | Entry must be in this stage |
| Approvers | Specific users/roles who must approve |
| Prevent self-approval | Author cannot approve their own entry |

Example rule: "Blog posts can only publish to `production` if they're in the `Approved` stage, and prevent self-approval."

## Permission constraints

- **Only Owner, Admin, Developer** roles can create or modify workflows and publish rules.
- **Management tokens cannot change workflow stages or approve publish rules** that require user-scoped approval. Programmatic stage transitions need a user-scoped auth token or OAuth with the right scopes. See `../security/tokens-authentication.md`.
- Branch-aware: workflows and publish rules are scoped to a branch, so a workflow on `main` is not automatically present on a feature branch (see `./branches-aliases.md` for the branch-specific vs global module split).

## Publish queue

The publish queue shows pending publish/unpublish actions, status (scheduled, in-progress, completed, failed), and cancellation ability. Each branch has its own queue.

## Red flags

- Too many stages (8+) — users will bypass or resent the process.
- Relying on `prevent-self-advancement` with a single-user reviewer role — it does nothing.
- Using a management token to try to approve stages — it can't. Use a user auth token or OAuth.
- Forgetting that workflows are branch-scoped — creating a workflow on a feature branch and expecting it on `main`.
- Not wiring `entries.workflow_stage_change` webhooks when automation is needed.
