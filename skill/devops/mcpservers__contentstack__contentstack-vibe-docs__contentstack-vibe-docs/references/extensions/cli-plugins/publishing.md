# CLI Plugins — Publishing, CI/CD, Best Practices, Troubleshooting

Shipping a Contentstack CLI plugin. Covers the pre-publish checklist, npm publishing, CI/CD setup, best-practice dos/don'ts, troubleshooting common failures, and a new-plugin checklist.

**See also:** `./overview.md` for architecture, `./commands.md` for command implementation.

## Pre-publish checklist

- [ ] Build: `npm run build`
- [ ] Tests: `npm test`
- [ ] Lint: `npm run lint`
- [ ] Bump version in `package.json` (semver)
- [ ] `README.md` with usage examples
- [ ] `oclif.manifest.json` is generated (happens automatically in `prepack`)
- [ ] `SECURITY.md` for public packages
- [ ] `npm audit` clean (or documented exceptions)
- [ ] Pack dry-run: `npm pack` — verify contents include only `lib/` and manifest

## Security before shipping

### `SECURITY.md`

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report vulnerabilities to security@contentstack.com
```

### Vulnerability scanning

```bash
npm install -g snyk
snyk test
snyk wizard      # interactive setup → generates .snyk file
```

### Dependency audit

```bash
npm audit
npm audit fix
```

## Publishing to npm

```bash
npm login
npm publish --access public
```

Scoped packages (`@contentstack/...`) usually need `--access public` the first time.

After publishing:

```bash
csdx plugins:install @contentstack/myplugin
```

## Semver

- **Patch** `1.0.1` — bug fixes, no API changes.
- **Minor** `1.1.0` — new features, backwards-compatible.
- **Major** `2.0.0` — breaking changes.

## CI/CD — GitHub Actions

Official plugins use GitHub Actions. Minimal `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20.x]
    steps:
      - uses: actions/checkout@v3
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run build
      - run: npm test
      - name: Security audit
        run: npm audit --audit-level=moderate
        continue-on-error: true
```

## Pre-commit hooks (optional)

```bash
npm install --save-dev husky
npx husky install
npx husky add .husky/pre-commit "npm run lint && npm test"
```

## Best practices

### Do

| Practice | Why |
|----------|-----|
| Use namespacing | Avoid command collisions (`myplugin:action`) |
| Follow oclif conventions | Users get consistent behavior across plugins |
| Use `this.log`, `this.error`, `ux.prompt` | Proper CLI feedback |
| Validate inputs early | Fail fast with clear messages |
| Add tests for every command | Catches regressions |
| Document commands with `description` + `examples` | `--help` becomes useful |
| Use official SDKs (`@contentstack/management`) | Type-safe, supported |
| Respect `~/.csdx/config.json` | Don't overwrite shared user state |
| Use `this.cmaHost` / `this.cdaHost` | Correct endpoints in all regions |
| Use TypeScript | Catches bugs at compile time |

### Don't

| Practice | Reason |
|----------|--------|
| Overwrite global config | Breaks other tools sharing the config |
| Hardcode endpoints or region info | Fails in non-US regions |
| Manually fetch `regions.json` | Base class already does this |
| Log tokens, passwords, or secrets | Security hole |
| Ignore errors / bare `try/catch` | Users get no useful feedback |
| Skip pagination | Missing data silently on large stacks |
| Bypass CLI output patterns | Inconsistent UX across plugins |

## Troubleshooting

### Command not found after linking

```bash
npm run build
csdx plugins:unlink myplugin
csdx plugins:link .
```

### Authentication errors

```bash
# Verify alias exists
csdx config:get tokens

# Or set via env var (fallback)
export CS_AUTHTOKEN=your-management-token
```

### Region not found

```bash
# Set explicitly (aliases like 'us', 'na', 'eu', 'azure-na' all work)
csdx config:set:region eu

# Or pass via flag if the command supports it
csdx myplugin:do -s <key> -t <alias> -r eu
```

The base class resolves region aliases automatically using the [official regions.json](https://artifacts.contentstack.com/regions.json) — you don't need to manage this in plugin code.

### TypeScript compilation errors

- Install deps: `npm install`
- Check `tsconfig.json` for `rootDir`/`outDir` mismatches.
- Verify Node: `node --version` ≥ 20.

### Manifest not generated

```bash
npx oclif manifest
# Or trigger via prepack
npm run prepack
```

## New-plugin checklist

### Setup

- [ ] Bootstrapped via `csdx plugins:create` (or `oclif generate`)
- [ ] `package.json` has correct name + `oclif.bin: "csdx"` + `oclif.commands` path
- [ ] `tsconfig.json` with `rootDir: "./src"`, `outDir: "./lib"`
- [ ] ESLint + `.editorconfig` configured
- [ ] `.gitignore` includes `lib/`, `node_modules/`

### Code

- [ ] Commands extend `@contentstack/cli-command` (not `@oclif/core`)
- [ ] Commands namespaced (`myplugin:action`)
- [ ] Service layer for non-trivial logic
- [ ] `src/utils/` for pure helpers
- [ ] `src/index.ts` exports commands

### Functionality

- [ ] Auth via token aliases (`this.getToken(alias)`)
- [ ] Region via `this.cmaHost` / `this.cdaHost` — no hardcoded endpoints
- [ ] Error handling with helpful messages
- [ ] Interactive prompts for missing inputs (with flag overrides for CI)
- [ ] Config file support if the plugin has many flags

### Quality

- [ ] Tests in `test/` — at minimum, flag validation and a happy-path test
- [ ] `.mocharc.json` configured
- [ ] Lint passes
- [ ] `npm audit` clean

### Docs

- [ ] `README.md` with install + usage + examples
- [ ] `description` + `examples` on every command
- [ ] `SECURITY.md` for public packages
- [ ] Comments on non-obvious logic

### CI/CD

- [ ] `.github/workflows/ci.yml` runs lint + build + test on PRs
- [ ] Pre-commit hooks (optional, husky)

### Publish

- [ ] Works locally via `csdx plugins:link .`
- [ ] Smoke-tested against a real stack
- [ ] Version bumped
- [ ] Ready for `npm publish`

## Lessons from official plugins

### From `apps-cli`

- Use a service layer for complex business logic.
- Support external config files.
- Interactive prompts for better UX; flag overrides for CI.
- `bin/` for executable scripts when needed.

### From `cli-tsgen`

- Organize file ops into utilities.
- Proper TypeScript types throughout.
- Handle large datasets efficiently (pagination, streaming).

### From `cli-content-type`

- Keep commands focused and single-purpose.
- Clear validation messages.
- Consistent naming conventions.

### Common pitfalls

1. Hardcoded endpoints — always use `this.cmaHost` / `this.cdaHost`.
2. Skipping error handling — users need actionable messages.
3. Logging tokens or sensitive data.
4. Forgetting pagination — silent data loss on large stacks.
5. Skipping tests — even two tests catch regressions.
6. Skipping CI — automate quality checks.
7. Fetching `regions.json` manually — base class handles it.

## Resources

**Official docs:**
- [oclif docs](https://oclif.io/docs)
- [Contentstack CLI](https://www.contentstack.com/docs/developers/cli)
- [Configure regions](https://www.contentstack.com/docs/developers/cli/configure-regions)
- [CLI authentication](https://www.contentstack.com/docs/developers/cli/authentication)

**Packages:**
- [`@contentstack/management`](https://www.npmjs.com/package/@contentstack/management)
- [`@contentstack/cli-command`](https://www.npmjs.com/package/@contentstack/cli-command)
- [`@contentstack/cli-utilities`](https://www.npmjs.com/package/@contentstack/cli-utilities)

**Reference plugins to study:**
- [`@contentstack/apps-cli`](https://github.com/contentstack/contentstack-apps-cli) — complex multi-command plugin with services layer.
- [`@contentstack/cli-tsgen`](https://github.com/contentstack/contentstack-cli-tsgen) — TypeScript generation + file ops.
- [`@contentstack/cli-content-type`](https://github.com/contentstack/contentstack-cli-content-type) — content-type utilities.
- [`@contentstack/cli-plugin-openapi`](https://github.com/timbenniks/contentstack-cli-plugin-openapi) — OpenAPI spec generation.

**API docs:**
- [Management API](https://www.contentstack.com/docs/developers/apis/content-management-api)
- [Delivery API](https://www.contentstack.com/docs/developers/apis/content-delivery-api)
