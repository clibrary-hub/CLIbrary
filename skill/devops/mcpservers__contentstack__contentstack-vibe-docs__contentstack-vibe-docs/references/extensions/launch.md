# Contentstack Launch

Contentstack Launch is the hosting/CDN/serverless platform for Contentstack-powered frontends. It connects to GitHub/GitLab/Bitbucket, builds your app, serves it from a global edge, and runs serverless + edge functions.

This doc covers the Launch concepts, API, deployment triggers, log diagnosis, and environment-variable sync workflows.

## Concepts

| | |
|---|---|
| **Project** | A connected repo. Has one or more environments. Holds build settings, domains, integrations. |
| **Environment** | A deployable target within a project (e.g., `main`, `preview-<branch>`, `staging`, `production`). Each environment has its own URL, env vars, and deployment history. |
| **Deployment** | An immutable artifact built from a git ref. One deployment per successful build. Deployments can be rolled forward or back within an environment. |
| **Custom domain** | A domain attached to an environment. TLS is provisioned automatically. |
| **Serverless Function** | Long-running compute (Node.js). Good for heavier logic, DB access, longer response windows. |
| **Edge Function** | Request-scoped compute on the edge (fast, region-local, limited CPU/memory). Good for routing, A/B, geo, auth. |

## API basics

All endpoints are under the Launch API. Auth uses a user auth token or a Launch-scoped management token:

```
Authorization: Bearer <launch_api_token>
```

Common endpoints (sketch — confirm the exact host/path against current Launch docs):

```
GET    /projects                                                 List projects
GET    /projects/{project_uid}                                   Project details
GET    /projects/{project_uid}/environments                      List environments
GET    /projects/{project_uid}/environments/{env_uid}            Environment details + current vars
PATCH  /projects/{project_uid}/environments/{env_uid}            Update environment (including env vars)
POST   /projects/{project_uid}/environments/{env_uid}/deployments   Trigger a deployment
GET    /projects/{project_uid}/environments/{env_uid}/deployments/{deployment_uid}    Deployment status + log
```

Never hardcode tokens — `process.env.CONTENTSTACK_LAUNCH_TOKEN` or a CI secret.

## Trigger a deployment

```typescript
async function triggerDeployment(projectUid: string, envUid: string) {
  const res = await fetch(
    `${LAUNCH_API}/projects/${projectUid}/environments/${envUid}/deployments`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.CONTENTSTACK_LAUNCH_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}), // optional build reference payload
    }
  );
  if (!res.ok) throw new Error(`trigger failed: ${res.status}`);
  return (await res.json()) as { deployment_uid: string };
}
```

**Production safety gate.** Do not auto-deploy to production without explicit confirmation. If your automation targets a production environment, require an interactive `yes` or an `--confirm-prod` flag.

## Poll until terminal

Terminal states are typically `success`, `failed`, `cancelled`. Poll every 10 seconds. Fail fast on terminal failure — don't keep polling.

```typescript
const TERMINAL = new Set(["success", "failed", "cancelled"]);

async function pollDeployment(
  projectUid: string,
  envUid: string,
  deploymentUid: string,
) {
  while (true) {
    const res = await fetch(
      `${LAUNCH_API}/projects/${projectUid}/environments/${envUid}/deployments/${deploymentUid}`,
      {
        headers: { Authorization: `Bearer ${process.env.CONTENTSTACK_LAUNCH_TOKEN}` },
      },
    );
    const body = (await res.json()) as { status: string; log?: string };

    console.log(`status: ${body.status}`);
    if (TERMINAL.has(body.status)) {
      if (body.status !== "success") {
        console.error("deployment failed");
        console.error(body.log ?? "(no log)");
        process.exit(1);
      }
      return body;
    }
    await new Promise((r) => setTimeout(r, 10_000));
  }
}
```

Exit non-zero on `failed`/`cancelled` so CI flags the job correctly.

## Diagnose deployment failures

On failure, fetch the deployment details and read the `log`. Common root causes and where they show up:

| Log signal | Likely cause | Fix |
|------------|--------------|-----|
| `npm ERR! ENOENT`, `yarn ... ENOENT` | Lockfile missing or wrong package manager detected | Commit lockfile; set build command explicitly |
| `Cannot find module 'X'` | Dependency not in `dependencies` (e.g. in `devDependencies` but used at build time) | Move to `dependencies` or set NODE_ENV correctly |
| `SyntaxError`, `TypeScript error TS...` | Code error that slipped past local checks | Run build locally before pushing |
| `Error: ENOSPC`, OOM kills | Build too large for the Launch build sandbox | Cache, prune, or trim the build artifact |
| Timeout | Build took too long | Add caching, split build steps |
| `403`/`401` on git clone | Token scope or revoked access | Re-authorize the git integration |
| `env variable X not defined` | Missing env var in the environment | `PATCH` the environment vars (see below) |

Summarize the first 2-3 error lines from the log; that's usually the root cause. Later lines are often noise.

## Sync environment variables from `.env.example`

Common CI need: keep the Launch environment's variable list aligned with the keys your app expects. Parse `.env.example` for variable names (never values — `.env.example` should contain only placeholder names), compare against Launch, and `PATCH` missing keys.

```typescript
import { readFileSync } from "node:fs";

function parseEnvExample(path: string): Set<string> {
  const raw = readFileSync(path, "utf8");
  const keys = new Set<string>();
  for (const line of raw.split("\n")) {
    const stripped = line.trim();
    if (!stripped || stripped.startsWith("#")) continue;
    const eq = stripped.indexOf("=");
    if (eq <= 0) continue;
    const key = stripped.slice(0, eq).trim();
    if (/^[A-Z0-9_]+$/.test(key)) keys.add(key);
  }
  return keys;
}

async function getLaunchEnvKeys(projectUid: string, envUid: string): Promise<Set<string>> {
  const res = await fetch(
    `${LAUNCH_API}/projects/${projectUid}/environments/${envUid}`,
    { headers: { Authorization: `Bearer ${process.env.CONTENTSTACK_LAUNCH_TOKEN}` } },
  );
  const body = (await res.json()) as { variables?: Record<string, string> };
  return new Set(Object.keys(body.variables ?? {}));
}

async function patchMissingKeys(
  projectUid: string,
  envUid: string,
  missingKeys: string[],
  dryRun = true,
) {
  if (missingKeys.length === 0) {
    console.log("no missing keys");
    return;
  }
  if (dryRun) {
    console.log(`[dry-run] would add ${missingKeys.length} keys: ${missingKeys.join(", ")}`);
    return;
  }
  // Add with empty values — editors fill them in the Launch UI
  const variables = Object.fromEntries(missingKeys.map((k) => [k, ""]));
  const res = await fetch(
    `${LAUNCH_API}/projects/${projectUid}/environments/${envUid}`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${process.env.CONTENTSTACK_LAUNCH_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ variables }),
    },
  );
  if (!res.ok) throw new Error(`patch failed: ${res.status}`);
  console.log(`added ${missingKeys.length} keys`);
}

// Usage
const expected = parseEnvExample(".env.example");
const present = await getLaunchEnvKeys(projectUid, envUid);
const missing = [...expected].filter((k) => !present.has(k));
await patchMissingKeys(projectUid, envUid, missing, /* dryRun = */ true);
```

**Prefer dry-run by default.** Require an explicit flag to apply changes. Surface validation errors from the PATCH response without retrying blindly.

## Safety rules

- **Never log env var values.** Log only key names and counts. Treat all values as secrets.
- **Never auto-deploy to production** without explicit confirmation — ask, wait, and require the exact project/environment UIDs.
- **Don't broaden the sync update** beyond missing keys unless the user explicitly asked to overwrite existing values.
- **Redact tokens** in all output, including error messages.

## Live Preview + Launch

Launch environments can be used directly as the **Live Preview base URL** for a Contentstack environment. Set the environment's live URL to the Launch preview URL for that environment (usually of the form `https://<project>-<env>.contentstackapps.com`) — see Live Preview setup in `../live-preview/concepts.md`.

For preview branches: each git branch gets its own Launch preview environment. You can wire per-branch preview URLs into Contentstack by creating one Contentstack environment per Launch preview env, or by overriding the preview URL per-session.

## Environment variables for your automation

```bash
CONTENTSTACK_LAUNCH_TOKEN=<user auth token or Launch-scoped token>
CONTENTSTACK_LAUNCH_PROJECT_UID=lp0123...
CONTENTSTACK_LAUNCH_ENVIRONMENT_UID=le0123...
LAUNCH_API_HOST=https://api.contentstack.io   # or regional equivalent
```

See `../security/tokens-authentication.md` for token handling rules.

## Red flags

- Auto-deploying to production without confirmation.
- Logging env var values in CI output.
- Retrying failed deployments in a loop without inspecting the log first.
- Patching env vars in the Launch environment with real values from a local `.env` — `.env` should never be in git, and CI should read secrets from a vault, not from a file.
- Hardcoding Launch API tokens in scripts.
- Polling faster than 10 seconds — wastes quota, doesn't speed up builds.
