# Contentstack Data Modeling Best Practices

Practical guidance for modeling content in Contentstack so editors can work quickly and delivery code stays simple.

## When to Read This

Read this before creating or changing content types, global fields, references, or page composition patterns.

Use [base-concepts.md](./base-concepts.md) first if you need a refresher on stacks, entries, field types, or APIs.

Use [content-management-api.md](../api/content-management-api.md) when you need schema export, migration, or content type CRUD details. Use [practical-examples.md](../examples/practical-examples.md) when you need frontend rendering patterns after the model is decided.

## Quick Chooser

| Use this | When it is the right choice | Avoid when |
|---|---|---|
| **Content type** | The thing has its own identity, lifecycle, permissions, or URL | You are modeling a page section that only exists inside one parent entry |
| **Reference** | The content is reused, updated independently, or queried independently | The data only makes sense inside one page or one entry |
| **Global field** | The same nested field set appears in 3+ content types with the same shape | Only one content type needs it, or each consumer needs a different variation |
| **Group** | Related fields belong together inside one content type and are not shared globally | You need independent reuse or cross-content-type governance |
| **Modular blocks** | Editors need to assemble pages from a known set of section types in variable order | You need shared content with its own lifecycle or heavy cross-page reuse |
| **Plain field** | The value is simple, atomic, and directly rendered or queried | You are packing several concepts into one blob |
| **JSON RTE** | Editors need formatted longform content with headings, links, embeds, or inline assets | The content should be filterable, sortable, or rendered as discrete UI fields |
| **Taxonomy** | You need governed classification, shared filters, or faceted navigation across content | The labels are informal, temporary, or only used by one team internally |
| **Tags** | You need lightweight editorial labels with low governance overhead | The values power public navigation, search facets, or analytics contracts |

### Fast Decisions

- **Reference vs modular blocks**: reference shared content; use modular blocks for page-local composition.
- **Global field vs group**: global field for reused schema; group for one content type only.
- **Taxonomy vs free-text tags**: taxonomy for controlled vocabularies; tags for loose internal labeling.
- **Structured fields vs rich text**: if the frontend needs to query it separately, do not hide it in rich text.

## Modeling Principles

- Model **domain concepts**, not page-shaped blobs. `product`, `author`, `category`, and `promotion` age better than `product_page`.
- Treat every content type as an **API contract**. Field UIDs become response keys. Renaming or retyping them is a breaking change.
- Prefer **structured content over presentation-coupled content**. Store meaning, not markup or layout assumptions.
- Optimize for **reuse, clarity, and retrieval**. A slightly less "DRY" model is often better if it is easier to query and explain.
- Design for **real editorial workflows**, not just schema elegance.

### Rules of Thumb

- Prefer one clear content type over one giant content type or five speculative micro-types.
- Default to **non-localizable** unless editors actually translate the field.
- Keep reference depth to **two levels or less** for common delivery paths.
- Use the rule of three before extracting a pattern into its own content type or global field.

## Choosing the Right Construct

### Content Types

Use a content type when the thing:

- exists independently of a single page
- has its own lifecycle or permissions
- should be queried directly
- may be referenced by other entries

Prefer:

- `author`, `category`, `product`, `landing_page`

Avoid:

- `homepage_hero_component`, `card_item_v2`, `footer_link_group_module`

### References

Use references when:

- multiple entries reuse the same content
- editors need one source of truth
- the referenced thing deserves its own URL, workflow, or publishing lifecycle

Prefer:

- `blog_post -> author`
- `product -> category`
- `page -> shared_testimonial`

Avoid:

- creating references to tiny one-off objects that only exist inside one page

### Global Fields

Use global fields for nested field sets that must stay consistent across content types.

Good fits:

- SEO metadata
- CTA fields
- address fields
- shared social link sets

Prefer:

- one well-governed `seo` global field reused across page-like types

Avoid:

- turning every nested field group into a global field
- stuffing unrelated concerns into one global field just to reduce field count

### Groups

Use groups for parent-owned nested data that is not reused outside that content type.

Good fits:

- product dimensions
- repeatable FAQ items inside a single settings entry
- store opening hours inside a store entry

Prefer:

- groups when editors always manage the data with the parent entry

Avoid:

- groups for content that later needs independent pages, filters, or governance

### Modular Blocks

Use modular blocks for flexible page assembly from a controlled set of section types.

Good fits:

- landing page sections
- article body callouts
- marketing campaign layouts

Prefer:

- a `page_sections` modular blocks field with a small, intentional block set

Avoid:

- using modular blocks as a replacement for every reference or content type
- giant blocks with 20+ optional fields each

### JSON RTE

Use JSON RTE for longform editorial content where formatting matters.

Good fits:

- article body
- campaign copy with headings and links
- rich descriptions with embedded assets or entries

Prefer:

- JSON RTE for narrative content

Avoid:

- storing filterable facts like specs, FAQs, pricing tiers, authors, or CTAs inside rich text

### Taxonomy and Tags

Use taxonomy when classification needs governance, shared filters, or cross-content-type consistency.

Use tags when labels are informal and low risk.

Prefer:

- taxonomy for `topic`, `audience`, `campaign`, `region`
- tags for temporary editorial organization

Avoid:

- using free-text tags for customer-facing navigation

### Extensions

Use custom fields or extensions only when native fields, references, modular blocks, and taxonomy cannot capture the data or editorial UI you need.

Prefer:

- native modeling first

Avoid:

- building custom fields to compensate for a weak content model

## Normalization vs Denormalization

Normalize when the content:

- changes independently
- appears in many places
- needs its own page, workflow, or analytics identity
- should be queried by itself

Denormalize when the value:

- is display-only
- changes rarely
- is cheap to duplicate
- saves a reference hop on a hot delivery path

### Practical Guidance

- Create reusable referenced entries for authors, categories, brands, product lines, and shared promos.
- Inline repeated low-risk display data when it keeps queries simple.
- Avoid premature abstraction. Two similar fields do not automatically justify a new content type.
- Duplicate intentionally when the operational cost is lower than the query cost.

Example:

- Keep `brand` as a reference if brand pages, logos, and descriptions are shared everywhere.
- It can still be reasonable to denormalize `brand_name` onto product cards if list views only need the label and you want to avoid extra includes.

## Page Composition Patterns

### Landing Pages

Use a `landing_page` content type with:

- core page metadata fields
- a `page_sections` modular blocks field
- references only for genuinely shared content such as testimonials, product collections, or reusable promo banners

Prefer:

- a small library of purposeful blocks: `hero`, `feature_grid`, `rich_text`, `cta`, `testimonial_strip`

Avoid:

- one page content type with dozens of optional fields like `hero_title`, `hero_title_variant_2`, `section_7_body`, `cta_3_label`

### Reusable Page Sections

If the same section appears on many pages and editors update it centrally, make it a referenced content type.

Examples:

- a compliance disclaimer used on many pages
- a shared promo ribbon
- a testimonial pool reused across campaigns

If the section is tuned per page, keep it inline as a modular block.

### Content-Driven Layouts

Use modular blocks to express page order, but keep business entities outside the page type.

Good pattern:

- `page.sections[]` contains `featured_products`
- the block references `product_collection` or `product` entries

Bad pattern:

- `page` also stores every product detail inline just because the products appear on that one page

## Localization and Multi-Channel Delivery

### Localized Fields vs Separate Entries

Use localized fields when the entry is the same thing in every locale and only the translatable values change.

Good fits:

- title
- description
- CTA label
- image alt text
- SEO metadata

Use separate entries only when locales need materially different entities, relationships, or governance.

Good fits:

- country-specific legal pages with different structure
- region-specific campaigns with different audiences, schedules, and references

### Reusable Global Content Across Locales

- Keep shared structural references non-localizable unless the relationship truly changes per locale.
- Localize the text fields inside referenced entries instead of cloning the entry structure.
- Define fallback locales early. Retrofitting locale strategy later is migration work.

### Multi-Channel Modeling

- Keep field names channel-agnostic: `short_description`, not `mobile_description`.
- Store one meaning-rich model and let web, app, email, and kiosk clients fetch different fields.
- Use JSON RTE plus frontend renderers instead of storing channel-specific HTML.
- Use Image Delivery transforms rather than separate image fields for each channel.

Avoid channel pollution:

- `web_title`
- `app_summary`
- `email_body`
- `mobile_cta`

Those fields usually signal presentation logic leaking into the schema.

## Performance and Query Design

Modeling choices show up in every Delivery API and GraphQL request.

### Prefer

- reference depth of 1-2 levels for common views
- field projection for lists and cards
- fewer, clearer references over long chains of tiny types
- denormalized display data on hot paths when it removes expensive includes

### Avoid

- deeply nested references everywhere
- large multi-reference arrays resolved on every page
- giant modular block payloads for simple listing views
- hiding structured facts inside JSON RTE when the UI needs them individually

### For REST and GraphQL

- Design list views around minimal field sets.
- Treat content types as contracts that should be easy to select from GraphQL without deeply nested fragments.
- Keep reference graphs understandable enough that REST `include[]` or SDK `.includeReference()` stays predictable.
- Test with realistic entry counts, not just sample content.

## Taxonomy and Classification

Use the simplest classification system that still gives you consistent filtering.

### Prefer Taxonomy When

- the values must be governed
- the same vocabulary applies across content types
- you need faceted navigation or cross-content-type filtering
- hierarchy matters

### Prefer References When

- the category itself is rich content with image, description, SEO, and landing pages

### Prefer Tags When

- editors need lightweight labels for internal organization
- inconsistency is acceptable

Do not overcomplicate classification:

- one or two customer-facing categories often do not need a full taxonomy system if referenced category entries already solve the problem
- informal editorial labels rarely need first-class modeled entities

### Taxonomy hierarchy design

- Plan the tree before creating it. Retrofitting a flat taxonomy into a hierarchy is painful.
- Keep depth practical — **3 to 4 levels max**. Deeper trees confuse editors and query patterns.
- Terms are parent-child ordered. Moving a term with children is **blocked by default** — opt in via the `force` flag.
- Localized terms **share the master term's UID** (plan-dependent — not available on all plans).
- Import/export supports JSON and CSV. Invalid CSV rows are skipped; valid rows are processed.

### CDA filtering operators (taxonomy)

Use these instead of pulling all entries and filtering client-side:

| Operator | Matches |
|----------|---------|
| `$taxonomy_exists` | Entries tagged with **any** term in the taxonomy |
| `$taxonomy_equal` | Entries tagged with a **specific term** (exact) |
| `$taxonomy_below` | Entries tagged with a term OR any of its **descendants** |
| `$taxonomy_above` | Entries tagged with a term OR any of its **ancestors** |

```
GET /v3/content_types/blog_post/entries?query={
  "$taxonomy_below": { "taxonomy_uid": "topics", "term_uid": "frontend" }
}
```

`$taxonomy_below` is the most common — "give me everything under Frontend, including React, Vue, Angular, and their children."

## Governance and Maintainability

### Naming Conventions

- Use snake_case UIDs for content types and fields.
- Keep display names editor-friendly and UIDs developer-friendly.
- Avoid `_v2`, `temp_`, and vague names like `misc_data`.
- Add field descriptions and instructions for non-obvious inputs.

### Avoid Model Sprawl

- Do not map frontend components 1:1 to content types.
- Consolidate tiny types that have no independent lifecycle.
- Use the rule of three before extracting reusable abstractions.
- Audit content types with low entry counts, high field counts, or unclear ownership.

### Schema Review Practices

Before adding a new type or major field:

1. Write 2-3 sample entries with realistic content.
2. Sketch the API response the frontend actually needs.
3. Check whether an existing type, group, or global field already solves it.
4. Decide the locale strategy before launch.

### Migration and Versioning Mindset

- Adding fields is usually safe.
- Removing fields deletes data.
- Renaming field UIDs is a breaking API change.
- Changing field type is usually a create-migrate-remove operation, not an edit.

Use [content-management-api.md](../api/content-management-api.md) for schema export, migration, and bulk updates when evolving models.

## Editor Experience

Good models are easier to author, not just easier to query.

### Prefer

- clear field labels and help text
- focused content types with obvious purpose
- logical grouping of fields
- defaults and validation where they reduce ambiguity
- one obvious place to enter a piece of information

### Avoid

- huge forms with many optional fields
- near-duplicate fields with unclear differences
- required fields that editors cannot reasonably populate
- field names that encode frontend implementation details

If a non-developer editor cannot explain where to update something, the model probably needs simplification.

## Examples

### 1. Blog Post with Author and Category

**Prefer**

- `blog_post` with plain fields for title, slug, excerpt, body
- reference to `author`
- reference or taxonomy for `category`

Why:

- authors change independently and appear across many posts
- categories are shared filters, not copy-pasted text
- the post stays queryable for lists and detail pages

**Avoid**

- embedding author bio and avatar into every post
- storing categories only as free-text tags if they drive navigation

### 2. Marketing Landing Page with Modular Sections

**Prefer**

- `landing_page` with page metadata plus `page_sections` modular blocks
- block types like `hero`, `feature_grid`, `logo_strip`, `cta`
- references only for shared content such as reusable testimonials

Why:

- editors can reorder sections without opening six separate content types
- the page stays flexible without turning into a giant optional-field schema
- shared content can still update centrally where it matters

**Avoid**

- a separate content type for every page section by default
- one massive `landing_page` type with `section_1_*` through `section_12_*`

### 3. Product or Storefront Model

**Prefer**

- `product` as the main entity
- references to `brand`, `product_line`, and rich `category` entries when those have their own pages or metadata
- taxonomy for governed filters like audience, collection, or merch theme when shared across multiple content types
- groups for repeatable inline data such as variants or dimensions when editors manage them with the product

Why:

- rich domain entities stay reusable and queryable
- storefront filters stay consistent
- delivery code can fetch a product card without resolving a deep graph for every label

**Avoid**

- category names duplicated everywhere with no source of truth
- five levels of nested references just to render a PDP
- rich text used for specs that should be structured fields

## Common Modeling Mistakes

- **Page-shaped everything**: content types mirror templates instead of domain concepts.
- **Too many optional fields**: giant schemas become editor-hostile and API-heavy.
- **Deep reference chains everywhere**: clean in theory, slow and fragile in delivery.
- **Using modular blocks for everything**: page composition is not the same as reusable content modeling.
- **Using rich text where structured fields are better**: impossible to filter, sort, or reuse reliably.
- **Premature reuse abstractions**: micro-types and global fields created for hypothetical future needs.
- **Unclear taxonomy**: free-text tags pretending to be a controlled vocabulary.
- **Locale strategy bolted on too late**: field localization and fallback rules become migration work.
- **Channel-specific schema pollution**: `mobile_*`, `web_*`, and `email_*` fields for the same concept.

## Checklist

- Does each content type represent a real domain concept?
- Are field UIDs stable, clear, and safe to treat as API keys?
- Did you choose references only where reuse or independent lifecycle actually exists?
- Did you keep page composition flexible without making the model sprawl?
- Is localization enabled only on fields that need translation?
- Can common REST and GraphQL queries stay shallow and predictable?
- Is classification governed at the right level: taxonomy, references, or tags?
- Can editors tell where to create and update each piece of content?
- Do sample entries and sample API responses look sane before launch?
