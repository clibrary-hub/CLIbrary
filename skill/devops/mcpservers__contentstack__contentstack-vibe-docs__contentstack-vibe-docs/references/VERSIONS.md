# Package Versions & Compatibility

Always install the latest version of each package. The minimum versions listed below are the oldest known to work with this documentation.

## Core Packages

| Package                            | Recommended | Minimum    | Notes                   |
| ---------------------------------- | ----------- | ---------- | ----------------------- |
| `@contentstack/delivery-sdk`       | `latest`    | `>=4.10.3` | TypeScript Delivery SDK |
| `@contentstack/live-preview-utils` | `latest`    | `>=4.1.2`  | Live Preview SDK v4     |
| `@contentstack/utils`              | `latest`    | `>=1.6.2`  | Utility functions       |
| `@contentstack/app-sdk`            | `latest`    | `>=2.3.4`  | Developer Hub App SDK   |

## CLI & Plugin Development

| Package                       | Recommended | Minimum     | Notes                  |
| ----------------------------- | ----------- | ----------- | ---------------------- |
| `@contentstack/cli`           | `latest`    | `>=1.52.0`  | Contentstack CLI       |
| `@contentstack/cli-command`   | `latest`    | `>=1.6.1`   | CLI command base class |
| `@contentstack/cli-utilities` | `latest`    | `>=1.14.4`  | CLI utility functions  |
| `@contentstack/management`    | `latest`    | `>=1.25.1`  | Management SDK         |
| `@oclif/core`                 | `latest`    | `>=4.8.0`   | oclif framework        |

## Framework Integrations

| Package                      | Recommended | Minimum   | Notes                |
| ---------------------------- | ----------- | --------- | -------------------- |
| `gatsby-source-contentstack` | `latest`    | `>=5.4.0` | Gatsby source plugin |

## Utilities

| Package                              | Recommended | Minimum   | Notes                             |
| ------------------------------------ | ----------- | --------- | --------------------------------- |
| `@timbenniks/contentstack-endpoints` | `latest`    | `>=2.1.0` | Region endpoint resolution helper |

## Runtime Requirements

| Requirement | Version    |
| ----------- | ---------- |
| Node.js     | `>=20.0.0` |
| npm         | `>=10.0.0` |

## Installation Commands

### For Content Delivery (Websites/Apps)

```bash
npm install @contentstack/delivery-sdk @contentstack/live-preview-utils
```

### For CLI Plugin Development

```bash
npm install @contentstack/cli-command @contentstack/cli-utilities @contentstack/management @oclif/core
```

### For Developer Hub Apps

```bash
npm install @contentstack/app-sdk
```

## Version Compatibility Notes

### Live Preview Utils v4

Version 4.x features:

- `mode` property (`"preview"` or `"builder"`)
- Improved Edit button configuration
- `cleanCslpOnProduction` option
- Better TypeScript support
- Enhanced postMessage handling

### Delivery SDK v4

Version 4.x features:

- Full TypeScript support
- Improved query builder
- Better error handling
- `QueryOperation` enum for type-safe queries
- Enhanced Live Preview integration

## Checking Installed Versions

```bash
# Check all Contentstack packages
npm list | grep contentstack

# Check specific package
npm list @contentstack/delivery-sdk
```

## Updating Packages

```bash
# Update to latest compatible versions
npm update @contentstack/delivery-sdk @contentstack/live-preview-utils

# Check for outdated packages
npm outdated
```
