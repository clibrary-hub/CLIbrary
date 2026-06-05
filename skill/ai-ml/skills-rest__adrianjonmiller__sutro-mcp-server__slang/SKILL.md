---
name: slang
description: SLang language reference for defining Sutro backends — entities, relations, actions, triggers, queues, security, files, and AI.
---

# SLang Language Reference

SLang is the programming language for defining [Sutro](https://withsutro.com) backends. It provides a simple but powerful way to define entire backends—including entities, logic, and security—without boilerplate or complex syntax.

For official documentation, tutorials, and getting started guides, visit: **https://docs.withsutro.com/docs/SLang/introduction**

This skill provides a comprehensive syntax reference for AI agents working with SLang files.

## Syntax Fundamentals

- **Indentation-significant**: Blocks are delimited by indentation (like Python), not braces.
- **Comments**: `;;` starts a line comment. Comments work at all levels (top-level, inside blocks, etc.).
- **Identifiers**: `[_a-zA-Z0-9]+` (alphanumeric with underscores).
- **Strings**: Double-quoted `"like this"`.
- **Numbers**: Integer literals (`0`, `42`).
- **Booleans**: `true`, `false`.
- **Null**: `null`.
- **Assignment**: `:=` (not `=`).

## Top-Level Constructs

A SLang file contains zero or more of these, in any order:

1. `entity` — define a data model (persisted to database)
2. `schema` — define a named, reusable type (not persisted)
3. `relation` — define a relationship between two models
4. `action` — define a named operation with a body or external implementation
5. `trigger` — bind an action to an HTTP endpoint, queue, or event
6. `queue` — declare a named async queue
7. `permissions` — define role-based permission grants
8. `constant` — define a named literal value
9. `import` — import a module or built-in (e.g., `import "AI"`)
10. `namespace` — group declarations under a namespace
11. `deployment` — deployment configuration with version and ID mappings

Any top-level construct (except `relation`, `queue`, `import`, `namespace`, `deployment`) can be prefixed with `export` to make it available to other modules.

---

## Import & Export

### Import

Import external modules or built-in modules:

```slang
import "AI"
import "slang:AI"
import "./models" as Models
```

- `import "AI"` and `import "slang:AI"` both resolve to the built-in AI module.
- `import "path" as Alias` imports a module with an alias for namespaced access.

### Export

Prefix any entity, schema, action, trigger, permission, or constant with `export` to make it available to importing modules:

```slang
export entity User
  fields
    name: TEXT

export action GetUser(): User
  body
    return single User where @id == id

export constant MaxRetries := 5
```

---

## Entity (Model) Definition

```slang
entity ModelName
  description "Human-readable description."
  identity email        ;; marks this as the identity/user model
  subject               ;; marks this as the subject (authenticated user) model
  group @id             ;; scoping/grouping marker
  role rolefield        ;; marks a field as a role field
  fields
    FieldName: TYPE
      description "Field description."
      minLength 2
    OptionalField: TYPE?
    FieldWithDefault: TYPE := "default value"
    EnumField: ENUM("val1", "val2", "val3") := "val1"
    ComputedField: BOOLEAN
      computed SomeOtherField == "approved"
    Avatar: FILE
    AttachedDoc: FILE?
```

### Entity Block Keywords

| Keyword | Purpose |
|---------|---------|
| `description` | Human-readable description string |
| `identity` | Marks the model as the identity model (e.g. `identity email`) |
| `subject` | Marks the model as the authenticated-user model |
| `group` | Scoping marker (e.g. `group @id`) |
| `role` | Marks a field as a role field (e.g. `role roleName`) |
| `fields` | Begins the field definitions block |

### Field Modifiers

| Modifier | Syntax | Purpose |
|----------|--------|---------|
| Optional | `TYPE?` | Field is not required |
| Default | `TYPE := "value"` | Default value when not provided |
| Description | `description "..."` | Human-readable field description |
| Min length | `minLength N` | Minimum string length constraint |
| Max length | `maxLength N` | Maximum string length constraint |
| Computed | `computed <expression>` | Derived value (read-only) — see Known Limitations |

### Primitive Types

| Type | Description | SCode Mapping |
|------|-------------|---------------|
| `TEXT` | String text | `p_TEXT` |
| `EMAIL` | Email address | `p_TEXT` |
| `PHONE_NUMBER` | Phone number | `p_PHONE_NUMBER` |
| `ADDRESS` | Physical address | `p_ADDRESS` |
| `NUMBER` | Numeric value | `p_NUMBER` |
| `CURRENCY_AMOUNT` | Monetary amount | `p_CURRENCY_AMOUNT` |
| `BOOLEAN` | True/false | `p_BOOLEAN` |
| `DATE` | Calendar date | `p_DATE` |
| `TIME` | Time of day | `p_TIME` |
| `DATE_TIME` | Combined date and time | `p_DATE_TIME` |
| `URL` | Web URL | `p_LINK` |
| `FILE` | File attachment | `p_FILE` |

**Note**: `EMAIL` is a semantic alias that maps to `p_TEXT` in SCode.

### Enum Type

```slang
Status: ENUM("draft", "uploaded", "approved", "archived") := "draft"
```

Enums define a fixed set of allowed string values. An optional default can follow `:=`.

---

## Schema Definition

Schemas define named, reusable types without persistence — unlike entities, they do **not** create database tables. Use schemas for action params/returns, AI structured output, and embedded JSONB fields on entities.

```slang
schema Address
  description "A physical mailing address."
  fields
    Street: TEXT
    City: TEXT
    State: TEXT
    ZipCode: TEXT
    Country: TEXT?
```

### Schema Field Types

Schema fields support the same primitives as entity fields, plus:

- **Schema references**: A field can reference another schema by name: `Shipping: Address`
- **Array-of-schema**: A field can hold an array of schema values: `Items: [LineItem]`
- **Namespaced references**: A field can reference a schema from another module: `Billing: Models::Address`

### Nested Schema Example

```slang
schema LineItem
  description "A single line item in an order."
  fields
    ProductName: TEXT
    Quantity: NUMBER
    Price: CURRENCY_AMOUNT

schema OrderSummary
  description "A customer order summary."
  fields
    OrderNumber: TEXT
    Shipping: Address
    Items: [LineItem]
    TotalAmount: CURRENCY_AMOUNT
    Status: ENUM("pending", "confirmed", "shipped", "delivered") := "pending"
    Notes: TEXT?
```

### Schema Rules

- Maximum nesting depth: 4 levels
- No circular references (schema A referencing schema B which references schema A)
- Schema names cannot conflict with entity names
- Only `description` is valid in the schema block (no `subject`, `group`, or `identity`)

---

## Relation Definition

Relations connect two entities. Syntax:

```slang
relation ModelA[FieldOnA] CardinalityA --- CardinalityB ModelB[FieldOnB]
  description "Description of the relationship."
```

### Cardinality Formats

| Syntax | Meaning |
|--------|---------|
| `1` | Exactly one |
| `*` | Zero or more (unbounded) |
| `0..1` | Zero or one |
| `0..*` | Zero or more |
| `1..*` | One or more |
| `N..M` | Range from N to M |

### Relationship Ownership Rules (how SCode determines the owner)

- **Many-to-many**: Both models are owners.
- **One-to-one**: The left (first) model is the owner.
- **One-to-many / many-to-one**: The "one" side owns the relationship.

### Example

```slang
relation User[Memberships] 1 --- 0..* Membership[Member]
  description "Each Membership belongs to one User."
```

This means:
- A `User` has 0..* `Memberships` (accessed via `user.memberships`)
- A `Membership` belongs to exactly 1 `User` (accessed via `membership.member`)

---

## Constant Definition

Constants define named literal values at the top level.

```slang
constant MaxRetries := 5
constant AppName := "My App"
constant Debug := false
constant Config := { retryDelay := 1000 debug := true }
constant Tags := ["alpha", "beta"]
constant Empty := null
```

Supported value types: numbers, strings, booleans, null, objects, and arrays.

---

## Action Definition

Actions define named operations with typed parameters and a body of statements.

```slang
action ActionName(param1: TYPE, param2?: TYPE := "default"): ReturnType
  description "What this action does."
  body
    ;; statements here
```

Actions with no parameters use empty parentheses:

```slang
action ListItems(): [Item]
  description "List all items for the current user."
  body
    items := pageOf Item where owner == @subject
    return items
```

### Action-Only Types

The following types are supported for action parameters and return types, in addition to the Sutro primitives:

| Type | Description |
|------|-------------|
| `BYTE_STREAM` | Binary data / file upload (converted to FILE internally) |
| `VOID` | No value (for action returns) |
| `FILE` | File reference (also usable on entity fields) |

### Action Parameters

- Required: `name: TYPE`
- Optional: `name?: TYPE`
- Optional with default: `name?: TYPE := "default"`
- Model type: `name: ModelName`
- Model field type: `name: ModelName[FieldName]` (constrains to that field's enum values)
- Array return type: `[ModelName]`
- Optional return type: `ReturnType?`
- Schema type: `name: SchemaName`

### External Actions

Actions can delegate to external TypeScript implementations instead of using a SLang body:

```slang
action MyAction(message: TEXT): TEXT
  external
    file := "./my-implementation.ts"
    impl := "MyActionFunction"
```

- `file` — path to the TypeScript implementation file
- `impl` — name of the exported function

External actions are used by built-in modules like the AI module. See the [AI Module](#ai-module) section.

### Action Body Statements

#### Create

```slang
variable := create ModelName {
  field1 := value1
  field2 := value2
}
```

#### Update

```slang
update variable {
  field1 := newValue
}
```

#### Delete

```slang
delete variable
```

#### Query (paginated)

```slang
result := pageOf ModelName where fieldName == value
result := pageOf ModelName    ;; no filter — returns all
```

#### Query (single record)

```slang
result := single ModelName where fieldName == value
```

Use `single` when you expect exactly one result (e.g., lookup by ID or unique field).

#### Assert

```slang
assert(description := "Error message shown to user.",
       rule := someCondition)
```

#### Enqueue

```slang
enqueue QueueName with variable
```

#### Store (file persistence)

```slang
storedFile := store uploadedFile
```

The `store` expression persists a file (e.g., from a `BYTE_STREAM` parameter) to object storage and returns a `FILE` reference with a URL.

#### Clone

```slang
copy := clone original
```

Creates a deep copy of an object.

#### For Loop

```slang
for item in collection
  ;; loop body using item
```

#### While Loop

```slang
while condition
  ;; loop body
```

#### If / Else

```slang
if condition
  ;; then block

if condition
  ;; then block
else
  ;; else block

if condition
  ;; then block
else if otherCondition
  ;; else-if block
else
  ;; final else block
```

#### Break / Continue

```slang
for item in collection
  if item.skip
    continue
  if item.done
    break
```

`break` and `continue` must be inside a `for` or `while` loop.

#### Return

```slang
return expression
```

#### Function Call

```slang
result := SomeService.method(param1 := value1, param2 := value2)
```

Namespaced calls use dot notation (e.g., `AI.prompt(...)`).

---

## AI Module

SLang includes a built-in AI module for LLM integration. Import it to call AI models from action bodies.

### Import

```slang
import "AI"
```

### AI.prompt()

```slang
result := AI.prompt(
  message := "Summarize this document",
  system := "You are a helpful assistant",
  attachments := [document.file],
  provider := "openai",
  modelName := "gpt-4o",
  temperature := 0.7,
  maxTokens := 500
)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | TEXT | Yes | The user prompt to send to the AI model |
| `system` | TEXT | No | System prompt defining the AI's behavior |
| `attachments` | [FILE] | No | Array of files to send (images, PDFs, etc.) |
| `provider` | TEXT | No | `"openai"` (default) or `"anthropic"` |
| `modelName` | TEXT | No | Specific model name for the provider |
| `temperature` | NUMBER | No | Controls output randomness |
| `maxTokens` | NUMBER | No | Maximum tokens to generate |

**Returns:** `TEXT` (the AI's response)

### Supported Providers

| Provider | Keyword | Default Model |
|----------|---------|---------------|
| OpenAI | `"openai"` | Default OpenAI model |
| Anthropic | `"anthropic"` | Default Anthropic model |

### Attachment Support

The `attachments` parameter accepts an array of `FILE` values. Supported file types:

- **Images** (PNG, JPG, etc.) — sent as image content parts
- **Documents** (PDF, text, etc.) — sent as file content parts with metadata

### Example: AI-Powered Review

```slang
import "AI"

schema AIReviewResult
  description "Structured output from AI review."
  fields
    Summary: TEXT
    Pros: TEXT
    Cons: TEXT
    Score: NUMBER

action SummarizeDocument(doc: Document): TEXT
  description "Use AI to summarize a document."
  body
    summary := AI.prompt(
      message := "Summarize the following document concisely.",
      attachments := [doc.file],
      provider := "openai"
    )
    return summary
```

---

## File Handling

SLang supports file uploads and storage through the `FILE` and `BYTE_STREAM` types.

### FILE Type

`FILE` is a primitive type for file references. Use it on entity fields to store file attachments:

```slang
entity Document
  fields
    Title: TEXT
    Attachment: FILE
    Thumbnail: FILE?
```

### BYTE_STREAM Type

`BYTE_STREAM` is used in action parameters to accept raw file upload data. It is converted to a `FILE` internally:

```slang
action UploadDocument(title: TEXT, file: BYTE_STREAM): Document
  description "Upload a document."
  body
    doc := create Document {
      title := title
      owner := @subject
    }
    storedFile := store file
    return doc
```

### Accessing Files from HTTP Requests

In HTTP trigger arguments, uploaded files are accessed via `@request.files`:

```slang
trigger UploadDocument on HttpRequest
  endpoint POST /documents
  arguments
    title := @request.body.title
    file := @request.files.files
  auth
    @subject can "doc:upload"
```

### The `store` Expression

The `store` expression persists a file to object storage and returns a `FILE` reference:

```slang
storedFile := store uploadedFile
```

Files are stored in S3-compatible object storage with presigned URLs for access.

---

## Trigger Definition

Triggers bind actions to external event sources.

```slang
trigger ActionName on TriggerType
  description "Description."
  ;; type-specific blocks
  arguments
    param := expression
  auth
    ;; auth rules
```

### Trigger Types

| SLang Name | Internal Type | Purpose |
|------------|---------------|---------|
| `HttpRequest` | `http` | HTTP API endpoint |
| `Queue` | `queue` | Async queue consumer |
| `Event` | `event` | Event bus listener |

### HTTP Trigger

```slang
trigger CreateUser on HttpRequest
  description "Create a new user."
  endpoint POST /users
  arguments
    name := @request.body.name
    email := @request.body.email
  auth
    @subject can "user:create"
```

**HTTP methods**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` (any valid method).

**Path parameters**: Use `{paramName}` in the path, reference via `@request.path.paramName`. Hyphens are supported in URL segments (e.g., `/delete-user`).

```slang
trigger GetUser on HttpRequest
  endpoint GET /users/{userId}
  arguments
    userId := @request.path.userId
```

**Whole-body mapping**: Pass the entire request body to an action parameter:

```slang
trigger CreateUser on HttpRequest
  endpoint POST /users
  arguments
    data := @request.body
```

Triggers that don't need arguments (e.g., list endpoints where the action derives data from `@subject`) can omit the `arguments` block:

```slang
trigger ListItems on HttpRequest
  description "List all items."
  endpoint GET /items
  auth
    @subject can "item:read"
```

### Queue Trigger

```slang
trigger ProcessJob on Queue
  description "Background job processor."
  queue jobQueue
  arguments
    job := @message
```

### Event Trigger

```slang
trigger OnJobCreated on Event
  description "Handle job creation event."
  event jobCreated
  arguments
    job := @message
```

### Auth Rules

Auth rules control who can invoke a trigger. They support:

| Rule | Syntax |
|------|--------|
| Permission check | `@subject can "permission:string"` |
| Scoped permission | `@subject can "permission" in GroupName` |
| Role check | `@subject is RoleName` |
| Scoped role | `@subject is RoleName in GroupName` |
| Anonymous access | `@subject is @anonymous` |
| Authenticated access | `@subject is @defined` |


Auth rules can be combined with `and`, `or`, and parenthesized grouping:

```slang
auth
  (@subject can "doc:read" or @subject is Admin) and @subject is @defined
```

---

## Queue Declaration

Queues are declared at the top level and referenced by actions and triggers.

```slang
queue queueName with ModelName
```

- `queueName` is the queue identifier.
- `ModelName` is the type of message the queue carries.
- Actions enqueue with: `enqueue queueName with variable`
- Queue triggers consume with: `trigger ActionName on Queue` + `queue queueName`

### When to Use Queues

Use queues for any operation that might take longer than a few seconds. HTTP requests have timeouts, so long-running work should be offloaded to a queue and processed asynchronously. Common cases:

- **AI calls** — LLM prompts can take several seconds or longer, especially with large attachments or high `maxTokens`. Wrap AI work in a queue-triggered action.
- **File processing** — Parsing, transforming, or analyzing uploaded files.
- **External API calls** — Any third-party integration with unpredictable latency.
- **Batch operations** — Iterating over many records to update or generate data.

**Pattern**: The HTTP-triggered action creates a job record, enqueues it, and returns the job handle immediately. A separate queue-triggered action does the heavy lifting and updates the job status when done.

```slang
queue reviewQueue with ReviewJob

action RequestReview(doc: Document): ReviewJob
  description "Queue a review and return immediately."
  body
    job := create ReviewJob {
      document := doc
      status := "queued"
    }
    enqueue reviewQueue with job
    return job

action RunReview(job: ReviewJob): VOID
  description "Background: perform the actual AI review."
  body
    update job { status := "running" }
    result := AI.prompt(
      message := "Review this document.",
      attachments := [job.document.attachment]
    )
    update job { status := "succeeded" }

trigger RequestReview on HttpRequest
  endpoint POST /documents/{docId}/reviews
  arguments
    doc := @request.path.docId
  auth
    @subject can "review:create"

trigger RunReview on Queue
  queue reviewQueue
  arguments
    job := @message
```

---

## Permissions

The syntax:

```slang
permissions MemberModel -> GroupModel
  "permission:action"
  "another:permission"
```

Example:

```slang
permissions User -> Organization
  "doc:read"
  "doc:write"
  "doc:delete"
```

---

## Expressions

### Operators (precedence, lowest to highest)

1. `or` — logical or
2. `and` — logical and
3. `==`, `!=` — equality
4. `>=`, `<=`, `>`, `<` — comparison
5. `in` — membership test
6. `+`, `-` — addition/subtraction
7. `*`, `/` — multiplication/division
8. `!` — logical not (unary)
9. `.` — property access
10. `()` — function call

### Special References

| Reference | Meaning |
|-----------|---------|
| `@subject` | The authenticated user |
| `@request` | The incoming HTTP request |
| `@request.body.*` | Request body fields |
| `@request.body` | Entire request body (for whole-body mapping) |
| `@request.path.*` | URL path parameters |
| `@request.files.*` | Uploaded files |
| `@request.query.*` | Query string parameters |
| `@message` | Queue/event message payload |
| `@id` | Internal ID reference |
| `@anonymous` | Anonymous user marker (auth rules only) |
| `@defined` | Any authenticated user marker (auth rules only) |

### Literals

- Strings: `"hello"`
- Numbers: `42`
- Booleans: `true`, `false`
- Null: `null`
- Objects: `{ key := value }`
- Arrays: `[expr1, expr2]`

---

## Keywords Reference

### Active Keywords

```
action, and, anonymous, as, arguments, assert, auth, body, break, can,
clone, computed, constant, continue, create, defined, delete, deployment,
else, endpoint, enqueue, entity, event, export, external, fields, file,
for, group, if, impl, import, in, is, model, namespace, on, of, or,
pageOf, params, permissions, queue, relation, return, role, schema,
single, store, subject, trigger, update, version, while, with, where
```

### Reserved (not yet implemented)

```
bus, case, concurrent, emit, helper, include, lambda,
publish, switch, topic, yield
```

Do not use reserved words as identifiers. If you must use a reserved word as a field name, the SLang generator will automatically wrap it in backticks (e.g., `` `role` ``).

---

## Naming Conventions

- **Entity and action names**: Use **PascalCase** (e.g., `UserProfile`, `CreateInvoice`, `SendNotification`).
- **Entity fields and action variables**: Use **camelCase** (e.g., `firstName`, `isActive`).

---

## Known Limitations

1. **Backtick identifiers with spaces**: The current lexer does not support spaces inside backticks. Use camelCase or PascalCase instead.

2. **Computed fields**: The `computed` keyword parses correctly, but computed expressions are not fully serialized to SCode output.

3. **Round-trip field casing**: When generating SLang from SCode, field names are normalized to camelCase. This is valid SLang but may differ from the original casing.

---

## Deployment Block

The `deployment` block maps entity and field names to stable database IDs, ensuring data persists across edits:

```slang
deployment
  appId "my-app-id"
  version v1.0.0
  User -> urn:sutro:model:abc123
    Name -> urn:sutro:edge:def456
    Email -> urn:sutro:edge:ghi789
  Post -> urn:sutro:model:jkl012
    Title -> urn:sutro:edge:mno345
```

### Editing Rules

- **Rename**: Update the name (left of `->`) to the new name. Keep the ID (right of `->`) unchanged.
  - Entity rename: `Post -> urn:sutro:model:jkl012` becomes `Article -> urn:sutro:model:jkl012`
  - Field rename: `Title -> urn:sutro:edge:mno345` becomes `Headline -> urn:sutro:edge:mno345`
- **Remove**: Delete the entry from the deployment block.
- **Add**: Do not add new entries. The system assigns IDs for new entities/fields automatically.
- Never modify `urn:sutro:...` values, `appId`, or `version`.

---

## SCode Output Overview

SLang compiles to SCode, a JSON structure with this shape:

```json
{
  "appId": "uuid",
  "version": "1.0.0",
  "userModelId": "urn:sutro:model:<uuid>",
  "groupModelId": "urn:sutro:model:<uuid>",
  "models": [ ... ],
  "schemas": [ ... ],
  "actions": [ ... ],
  "triggers": [ ... ],
  "queues": [ ... ],
  "securitySubjects": [ ... ],
  "requirements": [],
  "personas": [],
  "appOverview": null,
  "appDescription": "",
  "appDraft": null,
  "appViews": null,
  "domainModel": null
}
```

### ID Formats

| Entity | Format |
|--------|--------|
| Model | `urn:sutro:model:<uuid>` |
| Field/Edge | `urn:sutro:edge:<uuid>` |
| Action | `urn:sutro:action:<uuid>` |
| Trigger | `urn:sutro:trigger:<uuid>` |
| Effect | `urn:sutro:effect:<uuid>` |

### SCode Models

Each model has:
- `id` — Model ID (`urn:sutro:model:...`)
- `name` — Display name
- `fields` — Array of edges, each with `id`, `name`, `to` (type reference), `min`, `max`, `relationshipOwner`, `accessControl`

Field `to` values: primitive types are `p_TEXT`, `p_NUMBER`, `p_FILE`, etc. Relation fields point to model IDs.

When creating fields, DO NOT add `createdAt`, `updatedAt`, `deletedAt` fields. The platform will add those automatically. 
Adding these fields will result in a SLang error and the only way to fix that error is to remove these fields.

### SCode Actions

Each action has:
- `id` — Action ID
- `name` — Display name
- `effects` — Array of effect objects (create, update, delete, assert, return, `@sutro/executeSlang` for SLang bodies, or `@sutro/executeExternalSlang` for external actions)

### SCode Triggers

Each trigger mapping has:
- `actionId` — References an action
- `trigger` — Object with `type` (`http`, `queue`, `event`), `method`, `path`, `initialState`, etc.

---

## Further Reading

For more detailed documentation, tutorials, and guides:

- [Introduction to SLang](https://docs.withsutro.com/docs/SLang/introduction) — Overview and core concepts
- [Data Modeling](https://docs.withsutro.com/docs/SLang/data-modeling) — Entities, fields, and relationships
- [Logic & Actions](https://docs.withsutro.com/docs/SLang/logic) — Business logic and control flow
- [Security](https://docs.withsutro.com/docs/SLang/security) — Permissions and authentication
- [API & Triggers](https://docs.withsutro.com/docs/SLang/triggers) — HTTP endpoints and queues
- [Quickstart Guide](https://docs.withsutro.com/docs/getting-started/slang-quickstart) — Get started with SLang

---

## Full Example

```slang
import "AI"

entity Organization
  description "Tenant workspace."
  group @id
  fields
    Name: TEXT
      description "Organization name."
      minLength 2
    Plan: ENUM("free", "team", "enterprise") := "free"

entity User
  description "Authenticated user."
  identity email
  subject
  fields
    Email: EMAIL
    DisplayName: TEXT
      minLength 1

entity Membership
  fields
    Role: ENUM("viewer", "admin", "owner")

entity Document
  fields
    Title: TEXT
      minLength 1
    Status: ENUM("draft", "uploaded", "published") := "draft"
    Reviewable: BOOLEAN
      computed Status == "published"
    Attachment: FILE?

relation User[Memberships] 1 --- 0..* Membership[Member]
relation Organization[Members] 1 --- 0..* Membership[Organization]
relation Organization[Documents] 1 --- 0..* Document[Organization]
relation User[OwnedDocuments] 1 --- 0..* Document[Owner]

queue documentQueue with Document

action CreateDocument(organization: Organization, title: TEXT): Document
  description "Create a new document."
  body
    doc := create Document {
      title := title
      organization := organization
      owner := @subject
    }
    return doc

action UploadDocument(organization: Organization, title: TEXT, file: BYTE_STREAM): Document
  description "Upload a document with a file attachment."
  body
    doc := create Document {
      title := title
      organization := organization
      owner := @subject
      status := "draft"
    }
    storedFile := store file
    update doc { status := "uploaded" }
    return doc

action SummarizeDocument(doc: Document): TEXT
  description "Use AI to summarize a document."
  body
    summary := AI.prompt(
      message := "Summarize this document concisely.",
      attachments := [doc.attachment],
      provider := "openai"
    )
    return summary

action ProcessDocument(doc: Document): VOID
  description "Background document processor."
  body
    if doc.status == "uploaded"
      update doc { status := "published" }
    else
      assert(description := "Document must be uploaded first.", rule := false)

trigger CreateDocument on HttpRequest
  endpoint POST /organizations/{organizationId}/documents
  arguments
    organization := @subject.organization
    title := @request.body.title
  auth
    @subject can "doc:create"

trigger UploadDocument on HttpRequest
  endpoint POST /organizations/{organizationId}/documents/upload
  arguments
    organization := @subject.organization
    title := @request.body.title
    file := @request.files.files
  auth
    @subject can "doc:upload"

trigger ProcessDocument on Queue
  queue documentQueue
  arguments
    doc := @message
```
