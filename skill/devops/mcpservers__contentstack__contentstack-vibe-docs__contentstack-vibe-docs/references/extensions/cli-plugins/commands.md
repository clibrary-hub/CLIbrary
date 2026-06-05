# CLI Plugins — Commands, Flags, Auth, Patterns

Command structure, flag parsing, auth/region handling, and common implementation patterns for Contentstack CLI plugins.

**See also:** `./overview.md` for architecture, `./publishing.md` for shipping.

## Command lifecycle

1. **Discovery** — CLI reads `oclif.manifest.json`.
2. **Flag parsing** — CLI parses and validates command-line args.
3. **Instantiation** — CLI creates an instance of your command class.
4. **Initialization** — base class sets up region, auth, utilities.
5. **Execution** — your `run()` method runs with parsed flags.
6. **Output** — `this.log()`, `this.warn()`, `this.error()`.
7. **Exit** — 0 on success, non-zero on failure.

## Basic command structure

Extend `Command` from **`@contentstack/cli-command`** (not `@oclif/core`):

```typescript
import { Command } from "@contentstack/cli-command";
import { flags, FlagInput } from "@contentstack/cli-utilities";

export default class MyCommand extends Command {
  static description = "Does something cool with Contentstack";

  static examples = [
    "$ csdx myplugin:do -s blt1234567890abcdef --token-alias my-token",
    "$ csdx myplugin:do -s blt1234567890abcdef -t my-token -r eu",
  ];

  static flags: FlagInput = {
    stack: flags.string({
      char: "s",
      description: "Stack API key",
      required: true,
    }),
    "token-alias": flags.string({
      char: "t",
      description: "Management token alias",
      required: true,
    }),
    region: flags.string({
      char: "r",
      description: "Contentstack region",
    }),
  };

  async run(): Promise<void> {
    const { flags } = await this.parse(MyCommand);

    try {
      this.log(`Working with stack: ${flags.stack}`);

      // Base-class helpers
      const managementToken = this.getToken(flags["token-alias"]);
      const region = this.region;
      const cmaHost = this.cmaHost;
      const cdaHost = this.cdaHost;

      // ... your logic
    } catch (error) {
      this.error(
        `Failed: ${error instanceof Error ? error.message : String(error)}`,
        { exit: 1 }
      );
    }
  }
}
```

## Base-class API

`@contentstack/cli-command` gives you:

**Region:**
- `this.region` — current region config object.
- `this.cmaHost` — Management API host (e.g. `https://api.contentstack.io` for US).
- `this.cdaHost` — Delivery API host (e.g. `https://cdn.contentstack.io` for US).

**Auth:**
- `this.getToken(alias)` — looks up a management token by alias from `~/.csdx/config.json`. Falls back to env vars if alias missing.

**Output:**
- `this.log(message)` — stdout.
- `this.warn(message)` — stderr, non-fatal.
- `this.error(message, { exit })` — stderr and exit (default code 1).

**Config:**
- `this.config` — CLI configuration.
- `this.configHandler` — helpers for reading/writing config.

Using the base class instead of raw `@oclif/core` gives you consistency, security (no raw token exposure), correct region resolution, and automatic benefits from base-class updates.

## Flag types

```typescript
import { flags, FlagInput } from "@contentstack/cli-utilities";

static flags: FlagInput = {
  stack: flags.string({
    char: "s",
    description: "Stack API key",
    required: true,
  }),

  verbose: flags.boolean({
    char: "v",
    description: "Verbose output",
  }),

  mode: flags.string({
    char: "m",
    description: "API mode",
    options: ["delivery", "management"],
    default: "delivery",
  }),

  limit: flags.integer({
    char: "l",
    description: "Limit results",
    default: 100,
  }),
};
```

## Namespacing

**Always prefix your commands** to avoid collisions:

- ✅ `myplugin:do`, `myplugin:list`, `myplugin:generate`
- ❌ `do`, `list`, `generate`

Namespace should match your plugin name (minus the `@contentstack/cli-plugin-` prefix).

## Interactive prompts

Use `ux` from `@oclif/core` for user input:

```typescript
import { ux } from "@oclif/core";

async run(): Promise<void> {
  const { flags } = await this.parse(MyCommand);

  // Prompt for missing values
  const stackKey = flags.stack || await ux.prompt("Enter stack API key");
  const tokenAlias = flags["token-alias"] || await ux.prompt("Enter token alias");

  // Confirmation
  const confirmed = await ux.confirm("Are you sure?");
  if (!confirmed) {
    this.log("Operation cancelled");
    return;
  }

  // Select from options
  const mode = await ux.prompt("Select mode", {
    type: "select",
    options: ["delivery", "management"],
  });

  // Hidden input (for secrets, though see auth rules below)
  const password = await ux.prompt("Enter password", { type: "hide" });
}
```

**Always let flags override prompts** — CI/CD needs non-interactive execution.

## Authentication

Contentstack CLI uses a **token alias** system: tokens live in `~/.csdx/config.json` keyed by an alias; plugins request by alias, never by raw token. Tokens never appear in shell history.

### Token resolution helper

```typescript
import { Command } from "@contentstack/cli-command";
import { configHandler } from "@contentstack/cli-utilities";

function getManagementToken(command: Command, tokenAlias?: string): string {
  if (tokenAlias) {
    try {
      const tokenData = command.getToken(tokenAlias);
      if (typeof tokenData === "object" && tokenData !== null) {
        return (
          (tokenData as { token?: string; authtoken?: string }).authtoken ||
          (tokenData as { token?: string; authtoken?: string }).token ||
          ""
        );
      }
      if (typeof tokenData === "string") return tokenData;
    } catch {
      // fall through to env fallback
    }
  }

  return (
    configHandler.get("authtoken") ||
    process.env.CS_AUTHTOKEN ||
    process.env.CONTENTSTACK_MANAGEMENT_TOKEN ||
    ""
  );
}
```

Never log, echo, or embed the raw token in error messages.

## Region handling

The base class handles region resolution automatically. **Don't hardcode endpoints. Don't fetch `regions.json` yourself.**

```typescript
async run(): Promise<void> {
  const { flags } = await this.parse(MyCommand);

  // Already resolved — just use these
  const cmaHost = this.cmaHost;
  const cdaHost = this.cdaHost;
  const region = this.region;
  // e.g. { name: 'na', cma: 'https://api.contentstack.io', cda: 'https://cdn.contentstack.io' }

  const client = createCMAClient(flags.stack, managementToken, cmaHost);
}
```

**Supported regions:** AWS (`na`, `eu`, `au`), Azure (`azure-na`, `azure-eu`), GCP (`gcp-na`, `gcp-eu`).

**Region aliases resolved automatically:** `us` → `na`, `aws-na` → `na`, `aws-eu` → `eu`, etc.

**Resolution order:**
1. `--region` flag if supported.
2. CLI default from `~/.csdx/config.json` (set via `csdx config:set:region`).
3. Base class reads the official regions.json internally and resolves to canonical `this.cmaHost`/`this.cdaHost`.

## Management API client

Use `@contentstack/management` for typed API access:

```typescript
import { client } from "@contentstack/management";
import type { Stack } from "@contentstack/management/types/stack";

function createCMAClient(
  apiKey: string,
  authtoken: string,
  cmaHost: string,
): Stack {
  return client({
    authtoken,
    host: cmaHost,
  }).stack({
    api_key: apiKey,
    management_token: authtoken,
  });
}

async run(): Promise<void> {
  const { flags } = await this.parse(MyCommand);

  const managementToken = this.getToken(flags["token-alias"]);
  const cmaHost = this.cmaHost;

  const stack = createCMAClient(flags.stack, managementToken, cmaHost);
  const contentTypes = await stack.contentType().query().find();
  this.log(`Found ${contentTypes.items.length} content types`);
}
```

Always pass `this.cmaHost` — ensures correct region endpoint.

## Common patterns

### Paginated fetches

```typescript
import type { ContentType } from "@contentstack/management/types/stack/contentType";
import type { ContentstackCollection } from "@contentstack/management/types/contentstackCollection";

export async function fetchContentTypes(stack: Stack): Promise<ContentType[]> {
  const items: ContentType[] = [];
  let skip = 0;
  const limit = 100;
  let hasMore = true;

  while (hasMore) {
    const response: ContentstackCollection<ContentType> = await stack
      .contentType()
      .query({ skip, limit })
      .find();

    if (response.items && response.items.length > 0) {
      items.push(...response.items);
      skip += response.items.length;
      hasMore = response.items.length === limit;
    } else {
      hasMore = false;
    }
  }

  return items;
}
```

### Progress feedback & indicators

```typescript
import { ux } from "@oclif/core";

async run(): Promise<void> {
  this.log("Fetching data...");
  const items = await fetchItems();
  this.log(`Found ${items.length} item(s)`);

  // Progress bar
  ux.action.start("Processing items");
  for (let i = 0; i < items.length; i++) {
    await processItem(items[i]);
    ux.action.status = `Processing ${i + 1}/${items.length}`;
  }
  ux.action.stop("Complete");

  // Spinner for indeterminate progress
  const spinner = ux.spinner();
  spinner.start("Fetching data");
  const data = await fetchData();
  spinner.stop("Data fetched");
}
```

### Error handling

```typescript
async run(): Promise<void> {
  try {
    // ... logic
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes("authentication")) {
        this.error("Authentication failed. Check your token alias.", { exit: 1 });
      } else if (error.message.includes("not found")) {
        this.error(`Resource not found: ${error.message}`, { exit: 1 });
      } else {
        this.error(`Failed: ${error.message}`, { exit: 1 });
      }
    } else {
      this.error(`Failed: ${String(error)}`, { exit: 1 });
    }
  }
}
```

Principles: catch all errors, never expose sensitive data in error messages, use exit codes (0 success, 1 runtime error, 2 usage error), suggest fixes where you can.

### File operations

Use `fs-extra` for ergonomic async:

```typescript
import * as fs from "fs-extra";
import * as path from "path";

const outputPath = path.resolve(flags.out);
await fs.ensureDir(path.dirname(outputPath));

// JSON with formatting
await fs.writeJson(outputPath, data, { spaces: 2 });
const data = await fs.readJson(inputPath);

// Existence check
if (await fs.pathExists(filePath)) { /* ... */ }

// Copy
await fs.copy(sourcePath, destPath);
```

Always resolve relative paths to absolute before doing file ops. Validate paths (prevent path traversal if input is user-supplied).

### Configuration files

Support an optional config file for common settings:

```typescript
static flags: FlagInput = {
  config: flags.string({
    char: "c",
    description: "Path to configuration file",
  }),
};

async run(): Promise<void> {
  const { flags } = await this.parse(MyCommand);

  let config = {};
  if (flags.config) {
    const configPath = path.resolve(flags.config);
    if (await fs.pathExists(configPath)) {
      config = await fs.readJson(configPath);
    } else {
      this.error(`Config file not found: ${configPath}`, { exit: 1 });
    }
  }

  // Flags override config file values
  const finalConfig = { ...config, ...flags };
}
```

Flags always override config. JSON is the easiest format. Ship example config files in documentation.

### Service layer (for complex plugins)

Separate I/O from business logic so commands stay thin:

```typescript
// src/services/api-service.ts
import { Stack } from "@contentstack/management/types/stack";

export class ApiService {
  constructor(private stack: Stack) {}

  async fetchContentTypes() {
    // API logic
  }

  async createContentType(data: unknown) {
    // API logic
  }
}

// src/commands/myplugin/do.ts
import { ApiService } from "../../services/api-service";

async run(): Promise<void> {
  const { flags } = await this.parse(MyCommand);
  const apiService = new ApiService(stack);
  const contentTypes = await apiService.fetchContentTypes();
  // command-level logic
}
```

Services are easier to unit-test than commands. Reuse services across multiple commands.

## Testing

Use `@oclif/test` with Mocha — designed for testing oclif commands:

```typescript
import { expect } from "chai";
import { test } from "@oclif/test";
import MyCommand from "../../src/commands/myplugin/do";

describe("myplugin:do", () => {
  test
    .stdout()
    .command(["myplugin:do", "--stack", "dummy_key", "--token-alias", "test"])
    .it("runs myplugin:do", (ctx) => {
      expect(ctx.stdout).to.contain("Working with stack: dummy_key");
    });

  test
    .stdout()
    .stderr()
    .command(["myplugin:do"])
    .catch(/required/i)
    .it("requires stack flag");
});
```

Utilities:
- `.stdout()` / `.stderr()` — capture output.
- `.command([...args])` — execute with args.
- `.catch(regex)` — expect error matching.
- `.it(desc, cb)` — test case with captured `ctx`.

Run: `npm test`.

### Test patterns

```typescript
// Flag validation
test.command(["myplugin:do"]).catch(/required/i).it("requires required flags");

// Successful execution (stub .run())
test
  .stdout()
  .stub(MyCommand.prototype, "run", () => Promise.resolve())
  .command(["myplugin:do", "--stack", "test"])
  .it("executes successfully");

// Error handling
test
  .stderr()
  .command(["myplugin:do", "--stack", "invalid"])
  .catch(/error/i)
  .it("handles errors gracefully");
```

### Production smoke test

Before publishing, test end-to-end in a real environment:

```bash
npm i -g @contentstack/cli
csdx config:set:region <region>
csdx login
csdx plugins:link <plugin-local-path>
csdx myplugin:do --help
csdx myplugin:do -s <stack-key> -t <token-alias>
```

See `./publishing.md` for the full pre-publish checklist.
