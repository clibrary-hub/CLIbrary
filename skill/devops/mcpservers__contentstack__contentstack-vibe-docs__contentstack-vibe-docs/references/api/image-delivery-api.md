# Contentstack Image Delivery API

Complete guide to transforming and optimizing images on-the-fly using Contentstack's Image Delivery API. Resize, crop, convert formats, add overlays, and optimize quality via URL parameters.

## How It Works

Append query parameters to any Contentstack image asset URL to transform it. The source image is never modified — transformations are applied to the delivered version and cached on the CDN.

```
{image_url}?width=800&height=600&format=webp&quality=80
```

**Important:** The `environment` query parameter is required on all asset requests.

---

## Base URL

Image delivery uses a separate domain from the REST API.

**Regional Image URLs:**

| Region | Base URL |
|--------|----------|
| `us` | `https://images.contentstack.io/` |
| `eu` | `https://eu-images.contentstack.com/` |
| `au` | `https://au-images.contentstack.com/` |
| `azure-na` | `https://azure-na-images.contentstack.com/` |
| `azure-eu` | `https://azure-eu-images.contentstack.com/` |
| `gcp-na` | `https://gcp-na-images.contentstack.com/` |
| `gcp-eu` | `https://gcp-eu-images.contentstack.com/` |

**Full URL structure:**

```
https://images.contentstack.io/v3/assets/{stack_api_key}/{asset_uid}/{file_uid}/{filename}?environment=production&{parameters}
```

**Placeholders explained:**

| Placeholder | What it is | Where to get it |
|-------------|------------|-----------------|
| `stack_api_key` | Your Stack API key (the `api_key` env var). Safe in URLs. | Stack Settings → Keys. Same value as `api_key` in REST calls. |
| `asset_uid` | The asset's unique ID, prefixed `blt...` | In the asset response: `asset.uid` |
| `file_uid` | Internal version/file ID for this asset version | In the asset response: `asset.file_uid` (returned by the Assets endpoint). Present for every published asset. |
| `filename` | Original uploaded filename, URL-encoded | `asset.filename`. Cannot be changed after upload. |

Non-image assets (PDFs, videos, etc.) serve from `assets.contentstack.io` (and regional equivalents), not `images.contentstack.io`. Transforms only apply to images.

**Typical flow:**

1. Fetch the entry or asset via CDA → receive asset object with `url`, `uid`, `file_uid`, `filename`, `dimension`.
2. Use `asset.url` as the base and append Image Delivery transform params. The CDA asset `url` already contains the correct stack / asset / file / filename structure.

```typescript
// asset comes from an entry's asset reference
const src = `${asset.url}?width=800&format=webp&quality=80`;
```

See [Regions Guide](../concepts/regions.md) for finding your stack's region.

### RTE-inline images don't transform

Images **inserted directly into Rich Text Editor fields** serve as-is and **do not honor Image Delivery transform params**. For transform-ready images, reference assets via asset fields on the content type, not via RTE embeds.

---

## Supported Formats and Limits

**Input formats:** JPEG, PNG, WEBP, GIF, AVIF

**Output formats:** JPEG, Progressive JPEG, PNG, WebP (lossy), WebP (lossless), GIF, AVIF

**Constraints:**

| Limit | Value |
|-------|-------|
| Maximum input file size | 50 MB |
| Maximum input dimensions | 12,000 x 12,000 px |
| Maximum output dimensions | 8,192 x 8,192 px |
| Maximum AVIF output | 4,096 x 4,096 px |
| Maximum animated GIF frames | 1,000 |

---

## Resize

Control the output dimensions of an image.

| Parameter | Values | Description |
|-----------|--------|-------------|
| `width` | `1`–`8192` (pixels), `0.0`–`0.99` (percentage), or `Np` (e.g., `200p` = 200%) | Output width |
| `height` | `1`–`8192` (pixels), `0.0`–`0.99` (percentage), or `Np` | Output height |
| `disable` | `upscale` | Prevent enlargement beyond original dimensions |

**Examples:**

```
// Fixed pixel dimensions
?width=300&height=200

// Percentage of original (50%)
?width=0.5

// Scale up to 200%
?width=200p

// Prevent upscaling — image won't exceed original size
?width=1200&disable=upscale
```

When only `width` or `height` is specified, the other dimension scales proportionally.

### Resize Filter

| Parameter | Values | Description |
|-----------|--------|-------------|
| `resize-filter` | `nearest`, `bilinear`, `bicubic`, `lanczos2`, `lanczos3` | Algorithm for resizing. Default: `lanczos3` |

| Filter | Best For |
|--------|----------|
| `nearest` | Speed, pixel art |
| `bilinear` | Enlarging images |
| `bicubic` | Shrinking images |
| `lanczos2` | Preserving edges |
| `lanczos3` | Best quality (default) |

```
?width=500&height=550&resize-filter=nearest
```

---

## Fit

Controls how the image fits within specified dimensions. Requires both `width` and `height`.

| Value | Behavior |
|-------|----------|
| `bounds` | Constrains image within dimensions (no exceeding). Preserves aspect ratio. |
| `crop` | Crops to exact dimensions. |
| `cover` | Fills dimensions completely, cropping centrally if needed. |

**Examples:**

```
// Fit within 400x300 box, preserving aspect ratio
?width=400&height=300&fit=bounds

// Crop to exact 400x300
?width=400&height=300&fit=crop

// Cover the full 400x300 area
?width=400&height=300&fit=cover
```

---

## Crop

Four crop syntaxes are available.

### Region Crop (by dimensions)

```
?crop={width},{height}
```

Crops from center. Values in pixels or percentage (`0.0`–`0.99`).

### Aspect Ratio Crop

```
?crop={width}:{height}
```

Crops to specific aspect ratio (note the colon separator).

### Sub-Region Crop (x,y positioning)

```
?crop={width},{height},x{value},y{value}
```

Defines top-left corner of the crop region in pixels.

### Offset Crop (center-point positioning)

```
?crop={width},{height},offset-x{value},offset-y{value}
```

Defines center point of the crop. Offset values are percentages.

### Crop Modifiers

| Modifier | Description |
|----------|-------------|
| `safe` | Prevents out-of-bounds errors. Returns intersection of source and crop area. |
| `smart` | Enables content-aware cropping. |

**Examples:**

```
// Center crop 300x400
?crop=300,400

// 16:9 aspect ratio
?crop=16:9

// Crop starting at x=50, y=100
?crop=300,400,x50,y100

// Crop centered at 50%, 50%
?crop=300,400,offset-x50,offset-y50

// Safe crop (won't error if dimensions exceed source)
?crop=1000,1000,safe

// Content-aware smart crop
?crop=300,400,smart
```

---

## Trim

Trims pixels from image edges. Follows CSS shorthand conventions.

| Values | Behavior |
|--------|----------|
| `trim=25` | 25px from all edges |
| `trim=25,50` | 25px top/bottom, 50px left/right |
| `trim=25,50,75` | 25px top, 50px left/right, 75px bottom |
| `trim=25,50,75,100` | Top, right, bottom, left (clockwise) |

```
?trim=50
?trim=25,50,75,100
```

---

## Orient

Rotate and flip images.

| Value | Transformation |
|-------|---------------|
| `1` | No change (default) |
| `2` | Horizontal flip |
| `3` | 180 degree rotation |
| `4` | Vertical flip |
| `5` | Horizontal flip + 90 degree left rotation |
| `6` | 90 degree clockwise rotation |
| `7` | Horizontal flip + 90 degree right rotation |
| `8` | 90 degree counter-clockwise rotation |

```
?orient=6    // Rotate 90° clockwise
?orient=2    // Mirror horizontally
```

---

## Format Conversion

| Parameter | Value | Description |
|-----------|-------|-------------|
| `format` | `jpg` | Baseline JPEG |
| `format` | `pjpg` | Progressive JPEG |
| `format` | `png` | PNG |
| `format` | `webp` | WebP |
| `format` | `webpll` | WebP Lossless |
| `format` | `webply` | WebP Lossy |
| `format` | `gif` | GIF |
| `format` | `avif` | AVIF |

```
?format=webp
?format=pjpg&quality=80
```

### Auto Format

Automatically serve modern formats to supporting browsers.

| Parameter | Behavior |
|-----------|----------|
| `auto=webp` | Serves WebP to browsers that support it |
| `auto=avif` | Serves AVIF to browsers that support it |

When combined with `format`, `auto` takes precedence for supporting browsers. Non-supporting browsers fall back to the `format` value.

```
// AVIF for modern browsers, JPG fallback
?auto=avif&format=jpg
```

---

## Quality

Controls compression level for lossy formats only (`jpg`, `pjpg`, `avif`, `webply`).

| Parameter | Values | Description |
|-----------|--------|-------------|
| `quality` | `1`–`100` | Compression quality. Higher = better quality, larger file. |

```
?format=pjpg&quality=75
?format=webply&quality=80
```

---

## Blur

| Parameter | Values | Description |
|-----------|--------|-------------|
| `blur` | `1`–`1000` | Blur intensity. Higher = more blur. Decimals supported. |

```
?blur=20
?blur=5.5
```

---

## Sharpen

| Parameter | Syntax | Description |
|-----------|--------|-------------|
| `sharpen` | `a{amount},r{radius},t{threshold}` | Increase edge definition |

| Sub-parameter | Range | Description |
|---------------|-------|-------------|
| `a` (amount) | `0`–`10` | Edge contrast intensity |
| `r` (radius) | `1`–`1000` | Area affected. Lower = edges only. |
| `t` (threshold) | `0`–`255` | Minimum brightness difference for sharpening |

```
?sharpen=a5,r2,t0
```

---

## Brightness, Contrast, Saturation

| Parameter | Range | Description |
|-----------|-------|-------------|
| `brightness` | `-100` to `100` | Light intensity. `0` = unchanged, `100` = white, `-100` = black. |
| `contrast` | `-100` to `100` | Tone difference. `0` = unchanged, `-100` = neutral gray. |
| `saturation` | `-100` to `100` | Color intensity. `0` = unchanged, `-100` = grayscale. |

```
// Slightly brighter and more vivid
?brightness=10&saturation=20

// Convert to grayscale
?saturation=-100

// Increase contrast
?contrast=30
```

---

## Overlay (Watermark)

Place one image on top of another.

| Parameter | Values | Description |
|-----------|--------|-------------|
| `overlay` | Relative URL path (from `/v3/assets/...`) | The overlay image |
| `overlay-align` | `top`, `bottom`, `left`, `right`, `middle`, `center` | Position. Default: `middle,center`. Combine vertical + horizontal. |
| `overlay-repeat` | `x`, `y`, `both` | Repeat the overlay |
| `overlay-width` | Pixels or percentage | Overlay width |
| `overlay-height` | Pixels or percentage | Overlay height |
| `overlay-pad` | Pixels (CSS shorthand) | Padding around overlay |

**Example:**

```
// Watermark in bottom-right corner
?overlay=/v3/assets/{stack_api_key}/{asset_uid}/{file_uid}/watermark.png&overlay-align=bottom,right&overlay-width=100&overlay-pad=10

// Repeating watermark
?overlay=/v3/assets/.../logo.png&overlay-repeat=both
```

---

## Background Color

Sets the background color for transparent images or padding.

| Format | Syntax |
|--------|--------|
| Hex (3 or 6 digit) | `bg-color=ff0000` (no `#` prefix) |
| RGB | `bg-color=140,220,123` |
| RGBA | `bg-color=140,220,123,0.5` (alpha: `0.0`–`1.0`) |

```
?bg-color=cccccc
?bg-color=140,220,123,0.5
```

---

## Canvas

Expand the canvas around an image (adds space around it).

| Syntax | Description |
|--------|-------------|
| `canvas={width},{height}` | Fixed dimensions |
| `canvas={width}:{height}` | Aspect ratio |
| `canvas={width},{height},x{val},y{val}` | With top-left positioning |
| `canvas={width},{height},offset-x{val},offset-y{val}` | With center-point positioning |

Canvas dimensions must be greater than or equal to the image dimensions. Image is centered by default.

```
?canvas=800,600
?canvas=16:9
?canvas=800,600,x100,y50
```

**Note:** If `canvas` and `pad` are used together, `pad` is ignored.

---

## Padding

| Parameter | Values | Description |
|-----------|--------|-------------|
| `pad` | Pixels (CSS shorthand: 1-4 values) | Add extra pixels to image edges |

```
// 20px all sides
?pad=20

// 10px top/bottom, 20px left/right
?pad=10,20
```

---

## Device Pixel Ratio

Deliver resolution-appropriate images for high-DPI displays. Requires `width` or `height`.

| Parameter | Values | Description |
|-----------|--------|-------------|
| `dpr` | `1`–`10000` | Device pixel ratio multiplier |

```
// Deliver 800px wide image for 2x Retina displays
?width=400&dpr=2
```

---

## Animated GIF: Extract Frame

| Parameter | Description |
|-----------|-------------|
| `frame` | Extracts the first frame from an animated GIF |

```
?frame
```

**Note:** Width and height parameters are not recommended for GIF files.

---

## Common Patterns

### Responsive Image with Modern Format

```typescript
// Serve optimized WebP with AVIF for supporting browsers
const heroUrl = `${asset.url}?width=1200&auto=avif&format=webp&quality=80&environment=production`;
```

### Thumbnail Generation

```typescript
const thumbnailUrl = `${asset.url}?width=200&height=200&fit=cover&format=webp&quality=75&environment=production`;
```

### Retina-Ready Images

```typescript
// Standard and 2x versions
const imgSrc = `${asset.url}?width=400&format=webp&quality=80&environment=production`;
const imgSrcSet = `${asset.url}?width=400&dpr=2&format=webp&quality=80&environment=production 2x`;
```

### Grayscale Effect

```typescript
const grayscaleUrl = `${asset.url}?saturation=-100&environment=production`;
```

### Blurred Placeholder (LQIP)

```typescript
const placeholderUrl = `${asset.url}?width=40&blur=20&quality=30&format=webp&environment=production`;
```

### Watermarked Image

```typescript
const watermarkedUrl = `${asset.url}?overlay=/v3/assets/${stackApiKey}/${watermarkUid}/${watermarkFileUid}/watermark.png&overlay-align=bottom,right&overlay-width=150&overlay-pad=20&environment=production`;
```

### React/Next.js srcSet Pattern

```typescript
function ContentstackImage({ asset, widths = [400, 800, 1200] }: { asset: Asset; widths?: number[] }) {
  const baseParams = "format=webp&quality=80&environment=production";

  const srcSet = widths
    .map((w) => `${asset.url}?width=${w}&${baseParams} ${w}w`)
    .join(", ");

  const sizes = "(max-width: 640px) 400px, (max-width: 1024px) 800px, 1200px";

  return (
    <img
      src={`${asset.url}?width=${widths[widths.length - 1]}&${baseParams}`}
      srcSet={srcSet}
      sizes={sizes}
      alt={asset.title}
      loading="lazy"
    />
  );
}
```

### Vue/Nuxt Responsive Image

```typescript
function getImageUrl(asset: Asset, width: number, options: Record<string, string | number> = {}) {
  const params = new URLSearchParams({
    width: String(width),
    format: "webp",
    quality: "80",
    environment: process.env.CONTENTSTACK_ENVIRONMENT || "production",
    ...Object.fromEntries(Object.entries(options).map(([k, v]) => [k, String(v)])),
  });
  return `${asset.url}?${params.toString()}`;
}
```

---

## Parameter Interaction Rules

1. `fit` requires both `width` and `height`
2. `dpr` requires `width` or `height`
3. `resize-filter` requires `width` or `height`
4. `quality` only works with lossy formats: `jpg`, `pjpg`, `avif`, `webply`
5. `auto` takes precedence over `format` for supporting browsers
6. `canvas` and `pad` together: `pad` is ignored
7. `disable=upscale` prevents enlargement beyond original dimensions
8. `frame` only works with animated GIFs
9. `environment` is mandatory on all requests

---

## Best Practices

1. **Always specify `format=webp` or `auto=webp`** — reduces file size by 25-35% compared to JPEG
2. **Set `quality` between 75-85** — optimal balance of quality and file size
3. **Use `disable=upscale`** — prevents blurry enlargements
4. **Use `fit=cover` for thumbnails** — ensures consistent dimensions
5. **Implement `srcSet` for responsive images** — serve appropriate sizes per viewport
6. **Use `dpr=2` for Retina displays** — deliver crisp images on high-DPI screens
7. **Generate LQIP placeholders** — small, blurred images for progressive loading
8. **Chain parameters efficiently** — combine all transformations in a single URL
9. **Use `auto=avif` with `format=webp` fallback** — best compression with broad compatibility
10. **Always include the `environment` parameter** — required for all asset delivery

---

## Asset organization & limits

### Folder structure

Plan a folder hierarchy early. Moving assets between folders **preserves UIDs and references** — you can always reorganize later, but it's cheaper to do once.

A workable default:

```
/images
  /heroes           ← page heroes, banners
  /products         ← product shots
  /og               ← social share images
  /team             ← people photos
  /icons            ← UI icons
/documents
  /legal
  /whitepapers
/video
```

### Asset constraints

| Limit | Value |
|-------|-------|
| Max file size (UI upload) | **700 MB** |
| Max file size (API upload) | **100 MB** |
| Max assets per batch upload | **10** |
| Max assets per stack (default) | **10,000** |
| Max assets per organization (default) | **500,000** |
| Filename | **Cannot be changed after upload** |

### Replacing vs deleting

- **Replacing** an asset creates a new version but keeps the same `asset.uid` — all entry references stay intact. Use this to update an image in place.
- **Deleting** an asset **breaks every reference** to it in entries. Check references before deletion.

Asset versioning: `GET /v3/assets/{asset_uid}/versions` returns version history. Retrieve a specific version by appending `?version={n}` on the asset endpoint.

### Rate limits

Image delivery requests count against the delivery rate limits on your plan. On `429`, back off — don't busy-retry. For build-time image pipelines that generate many variants, cache aggressively on your side and don't treat Image Delivery as a per-request transform service for every user.

---

See [REST API](rest-api.md) for content delivery endpoints, [Delivery SDK](../sdk/delivery-sdk.md) for SDK-based asset fetching, and [Practical Examples](../examples/practical-examples.md) for more patterns.
