# CLI Plugins — Overview

Develop external plugins for the Contentstack CLI (`csdx`). Plugins add custom commands, integrate with Contentstack APIs, and automate workflows. They're built on **oclif** and extend the CLI seamlessly.

**See also:** `./commands.md` for command implementation, `./publishing.md` for shipping/CI.

## Why build a plugin

- Add custom commands not in the core CLI.
- Automate repetitive content operations or migrations.
- Integrate Contentstack with other tools in your pipeline.
- Share tooling across a team or the community.
- Maintain CLI consistency while adding custom logic.

## How it works

When you install a plugin (`csdx plugins:install` or `csdx plugins:link`):

1. **Discovery** — CLI reads the plugin's `oclif.manifest.json` for available commands.
2. **Registration** — commands become available as `csdx <plugin>:<command>`.
3. **Shared context** — plugins get access to CLI config, auth tokens, region, utilities.
4. **Execution** — plugin code runs in the same Node.js process as the CLI, same privileges.

## Reference plugins to study

- **`@contentstack/apps-cli`** — [GitHub](https://github.com/contentstack/contentstack-apps-cli) — multi-command app with a services layer and interactive prompts.
- **`@contentstack/cli-tsgen`** — [GitHub](https://github.com/contentstack/contentstack-cli-tsgen) — TypeScript-type generation, file ops.
- **`@contentstack/cli-content-type`** — [GitHub](https://github.com/contentstack/contentstack-cli-content-type) — content-type utilities.
- **`@contentstack/cli-plugin-openapi`** — [GitHub](https://github.com/timbenniks/contentstack-cli-plugin-openapi) — OpenAPI spec generation.

## Prerequisites

- **Node.js v20.x+** (active or LTS only).
- TypeScript (recommended) or JavaScript.
- Familiarity with oclif.
- Contentstack CLI installed globally:
  ```bash
  npm install -g @contentstack/cli
  ```
- A Contentstack account with a stack to test against.

## Architecture

### Plugin discovery locations

CLI scans:
- Global plugins: `~/.csdx/node_modules/@contentstack/*`
- Local plugins: `./node_modules/@contentstack/*`
- Linked plugins (dev): `~/.csdx/plugins/`

### Command execution flow

```
User runs: csdx myplugin:do --stack blt123 --token-alias mytoken
    ↓
CLI parses command and flags
    ↓
CLI loads plugin from node_modules or linked path
    ↓
CLI instantiates command class (extends @contentstack/cli-command)
    ↓
Command.run() executes with:
    - Parsed flags
    - Access to CLI config (~/.csdx/config.json)
    - Access to auth tokens
    - Region-resolved endpoints (this.cmaHost, this.cdaHost)
    ↓
Command outputs via this.log() / this.error()
```

### Base command class

Extend `Command` from **`@contentstack/cli-command`** — not `@oclif/core` directly. The base class provides:

- **Region management** — automatic region detection and endpoint resolution.
- **Authentication** — token lookup via aliases.
- **Configuration** — access to `~/.csdx/config.json`.
- **Logging/error helpers** — `this.log()`, `this.warn()`, `this.error()`.
- **Consistency** — all plugins follow the same patterns.

### Core vs plugin commands

Both share the same execution environment and utilities. The difference is just where they ship from:

- **Core:** `csdx login`, `csdx config:set:region`, `csdx plugins:install`, `csdx stacks:list`
- **Plugin:** `csdx apps:create` (from `apps-cli`), `csdx tsgen:generate` (from `cli-tsgen`), `csdx myplugin:do` (from yours)

## Project structure

Based on `@contentstack/apps-cli`:

```
my-plugin/
├── bin/                       # Optional executable scripts
│   └── run
├── src/
│   ├── commands/
│   │   └── myplugin/
│   │       ├── do.ts          # Command implementation
│   │       └── list.ts
│   ├── services/              # Optional: business logic layer
│   │   ├── api-service.ts
│   │   └── data-service.ts
│   ├── utils/                 # Pure helpers
│   │   ├── helper.ts
│   │   └── validators.ts
│   └── index.ts               # Plugin entry point
├── test/
│   └── commands/
│       └── myplugin/
│           └── do.test.ts
├── .github/workflows/ci.yml   # CI/CD
├── lib/                       # Compiled output (auto-generated)
├── .editorconfig
├── .eslintrc.js
├── .gitignore
├── .mocharc.json              # Mocha config
├── .snyk                      # Optional — security scanning
├── package.json
├── tsconfig.json
├── README.md
├── SECURITY.md                # Recommended for public packages
└── oclif.manifest.json        # Auto-generated
```

### Service layer pattern

For complex plugins, separate concerns:

- **Commands** → CLI I/O, flag parsing, user interaction.
- **Services** → business logic, API interactions.
- **Utils** → pure, reusable helpers.

```
src/
├── commands/myplugin/do.ts         # Thin command layer
├── services/
│   ├── api-service.ts              # API calls
│   ├── transform-service.ts        # Data transformation
│   └── validation-service.ts       # Business rules
└── utils/helpers.ts                # Pure helpers
```

## Bootstrap a new plugin

### Option A — Contentstack generator (recommended)

```bash
csdx plugins:create
```

Interactive prompts for name, description, version, license, GitHub repo, TypeScript/ESLint/Mocha preferences. Generates a ready-to-run boilerplate with Contentstack-specific defaults.

### Option B — oclif directly

```bash
npx oclif generate @contentstack/myplugin
cd myplugin
```

Lighter — basic oclif scaffold without Contentstack-specific configuration. Prefer Option A unless you have a reason not to.

## `package.json` configuration

The `package.json` tells oclif how to integrate with `csdx`:

```json
{
  "name": "@contentstack/myplugin",
  "version": "1.0.0",
  "description": "Your plugin description",
  "author": "Your Name",
  "license": "MIT",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "oclif": {
    "commands": "./lib/commands",
    "bin": "csdx",
    "plugins": []
  },
  "files": ["/lib", "/oclif.manifest.json"],
  "scripts": {
    "build": "tsc",
    "prepack": "npm run build && oclif manifest",
    "test": "mocha --forbid-only \"test/**/*.test.ts\"",
    "lint": "eslint . --ext .ts",
    "lint:fix": "eslint . --ext .ts --fix"
  },
  "dependencies": {
    "@contentstack/cli-command": "^1.6.1",
    "@contentstack/cli-utilities": "^1.14.4",
    "@contentstack/management": "^1.25.1",
    "@oclif/core": "^4.8.0"
  },
  "devDependencies": {
    "@oclif/test": "^3.0.0",
    "@types/node": "^20.11.0",
    "@typescript-eslint/eslint-plugin": "^6.19.0",
    "@typescript-eslint/parser": "^6.19.0",
    "eslint": "^8.56.0",
    "eslint-config-oclif": "^5.0.0",
    "mocha": "^10.3.0",
    "ts-node": "^10.9.2",
    "typescript": "^5.3.3"
  },
  "engines": { "node": ">=20.0.0" }
}
```

**Key fields:**

- `name` — use `@contentstack/` for official, your namespace for private.
- `oclif.bin: "csdx"` — declares this plugin integrates with the Contentstack CLI.
- `oclif.commands` — points at compiled output directory.
- `oclif.plugins` — usually empty for standalone plugins.
- `prepack` — runs before `npm publish`: builds TypeScript + generates manifest.
- `files` — only ship compiled code + manifest (not source).

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "declaration": true,
    "outDir": "./lib",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "types": ["node", "mocha"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "lib", "test"]
}
```

## Plugin entry point

`src/index.ts` exports your commands:

```typescript
// Single command
export { default } from "./commands/myplugin/do";

// Multiple commands
export { default as Do } from "./commands/myplugin/do";
export { default as List } from "./commands/myplugin/list";
```

## Registration & local dev

### Link locally for development

```bash
# From your plugin directory
csdx plugins:link .
```

This:
- Creates a symlink in `~/.csdx/plugins/` pointing at your local code.
- Builds the plugin if needed.
- Generates the manifest.
- Registers all commands.

After code changes, rebuild:

```bash
npm run build
# Linked commands pick up changes automatically
```

Verify registration:

```bash
csdx myplugin:do --help     # confirm command is registered
csdx plugins:list           # confirm plugin appears
```

### Install a published plugin

```bash
# Global install (system-wide)
csdx plugins:install @contentstack/myplugin

# Or install locally in a project
npm install @contentstack/myplugin
csdx plugins:install
```

### Unlink during dev

```bash
csdx plugins:unlink myplugin
```

## Next steps

- **`./commands.md`** — command structure, flag types, auth, region handling, patterns, testing.
- **`./publishing.md`** — publishing, CI/CD, best practices, troubleshooting, checklist.
