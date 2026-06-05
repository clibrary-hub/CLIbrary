---
name: sutro-mcp-setup
description: Wire the local Sutro MCP server into the user’s editor — security bundle path, env vars, build steps for mcp/sutro.
---

# Sutro MCP setup

Use this skill when the user needs to connect **Cursor**, **Claude Code**, or **VS Code** MCP clients to Sutro tooling.

## Prerequisites

- Download **security-bundle.zip** from [Sutro Console](https://console.withsutro.com/) and extract it to a stable directory (for example `~/.config/sutro/security-bundle`). Do not commit the bundle; it contains private keys and JWTs.
- For production-style auth (sign your own Builder JWT), see [How to secure connections](https://docs.withsutro.com/docs/getting-started/auth/how-to-secure-connections).

## Build the MCP server

From the repo root:

```bash
cd mcp/sutro && npm install && npm run build
```

## Configure the client

1. Point **command** / **args** at `mcp/sutro/dist/index.js` with `node` (see `config/mcp.cursor-sample.json`, `config/mcp.vscode-sample.json`, `config/mcp.claude-sample.json`).
2. Set **`SUTRO_SECURITY_BUNDLE_DIR`** to the directory that contains `ca.crt`, `mtls.crt`, `mtls.key`, `builder.jwt`, and `apiClient.id`. Use an **absolute** path in MCP `env` if your client does not expand `~`. A leading `~/` in the value is expanded by the server using `$HOME`.
3. Optionally set **`SUTRO_API_BASE`** (default `https://sapi.withsutro.com`).

## Verify

Use **`sutro_validate_bundle`** first to check local bundle readiness (required files + JWT refresh prerequisites), then run **`sutro_hello`** (calls `GET /hello`) to verify end-to-end connectivity.

## Probe live response shapes

When docs are unclear, treat live responses as the contract source of truth:

1. From `mcp/sutro`, run `npm run sutro-probe-shapes` (uses mTLS + bundle bearer auth).
2. Optional flags:
   - `--project-id=<uuid>` to probe `/projects/:id/applications` for a specific project
   - `--timeout-ms=10000` to tune request timeout per endpoint
   - `--snapshot=./tmp/sutro-shapes.json` to save a sanitized shape report for comparisons
3. Update tool parsers in `mcp/sutro/src/` to match observed top-level shapes before trusting docs.
4. Run `npm test` in `mcp/sutro` to verify normalizers and compatibility fallbacks.

## Refresh `builder.jwt` locally (optional)

If the bundle’s **`builder.jwt`** expired but you still have a signing key (**`signing.pem`** preferred, fallback **`mtls.key`**) and the correct **issuer** + **builder `sub`**, you can mint a short-lived token without pasting passwords into chat:

1. Copy [`mcp/sutro/.env.example`](mcp/sutro/.env.example) to **`mcp/sutro/.env`** (never commit `.env`).
2. Set `SUTRO_SECURITY_BUNDLE_DIR`, `SUTRO_PROVISION_MODE=sign-only`. Ensure `jwtIssuer.id` and either `.sutro-builder-sid` or `builder.id` (or `SUTRO_BUILDER_SID`) match what Sutro expects for `iss` / `sub` on the Builder JWT ([How to secure connections](https://docs.withsutro.com/docs/getting-started/auth/how-to-secure-connections)).
3. From `mcp/sutro`: `npm install` then `node --env-file=.env scripts/sutro-provision-from-env.mjs` (or `npm run sutro-provision` with the same env loaded).

For a **full** org init + new builder (only when your org can run `/initialization`), set `SUTRO_PROVISION_MODE=full` plus `SUTRO_ORG_EMAIL`, `SUTRO_ORG_PASSWORD`, `SUTRO_COMMON_NAME`, and `SUTRO_JWT_ISSUER` per the doc.

## Adding more tools

- Implement additional Sutro HTTP calls via the same bundle auth pattern in `mcp/sutro/src/`; keep tool names stable and extend `rules/sutro.mdc` when you add tools.
- Use **zod** input schemas per tool.

## Edit and ship workflow

- Use `sutro_list_projects` and `sutro_list_apps` for discovery (`includeScode=false` by default for lighter payloads).
- Use `sutro_pull_project_data` or `sutro_pull_app_for_edit` when you need full SCode context before making changes.
- Apply changes with `sutro_deploy_slang`, or use `sutro_apply_slang_changes` for deploy + status verification (+ optional publish) in one call. For release workflows, publish options include `versionType` and `replacePublishedVersion`.
- If the SLang file is already on disk, use `sutro_apply_slang_from_file` to avoid sending large inline payloads through tool arguments.

## References

- [Sutro docs](https://docs.withsutro.com)
- [Official SLang skills](https://github.com/SutroOrg/sutro-skills)
