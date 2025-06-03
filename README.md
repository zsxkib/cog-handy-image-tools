# Image Strip Merger 🖼️

A practical tool for combining multiple images into clean horizontal or vertical strips. Perfect for creating before/after comparisons, image galleries, or social media collages.

## Quick start

Clone this repository and run a prediction:

```bash
git clone https://github.com/zsxkib/cog-handy-image-tools.git
cd cog-handy-image-tools
```

### Basic example

Merge two images horizontally:

```bash
cog predict \
  -i 'images=["https://replicate.delivery/pbxt/N7iomkdKPMydXErUUHqC1AC0KNoucPaUimMEJW5NroJAUpl7/beast.jpg","https://replicate.delivery/pbxt/N7iomMkoAdSUO7MUDky8R3rfxjmSUu0iumxwkewCsA4as3v0/shadowmere.jpg"]'
```

### Full example with all options

```bash
cog predict \
  -i 'images=["https://replicate.delivery/pbxt/N7iomkdKPMydXErUUHqC1AC0KNoucPaUimMEJW5NroJAUpl7/beast.jpg","https://replicate.delivery/pbxt/N7iomMkoAdSUO7MUDky8R3rfxjmSUu0iumxwkewCsA4as3v0/shadowmere.jpg"]' \
  -i 'alignment="center"' \
  -i 'orientation="horizontal"' \
  -i 'border_color="#ffffff"' \
  -i 'output_format="webp"' \
  -i 'output_quality=90' \
  -i 'resize_strategy="reduce_larger"' \
  -i 'border_thickness=0' \
  -i 'keep_aspect_ratio=true'
```

You can also use local files by prefixing with `@`:

```bash
cog predict -i 'images=["@image1.jpg","@image2.png","@image3.webp"]'
```

## What it does

Upload 2 or more images and this tool will:

- **Merge them into strips** - Horizontal or vertical layouts
- **Smart resizing** - Automatically harmonize image sizes with multiple strategies  
- **Precise alignment** - Control how images align within the strip (start, center, end)
- **Border control** - Add consistent borders around and between images
- **Format flexibility** - Export as WebP, PNG, or JPEG with quality control

## Parameters

- **`images`** - List of image URLs or local file paths (required)
- **`orientation`** - `"horizontal"` or `"vertical"` (default: `"horizontal"`)
- **`alignment`** - `"start"`, `"center"`, or `"end"` (default: `"center"`)
- **`resize_strategy`** - How to handle different image sizes:
  - `"none"` - Keep original sizes
  - `"magnify_smaller"` - Scale smaller images up to match largest
  - `"reduce_larger"` - Scale larger images down to match smallest (default)
  - `"crop_larger"` - Crop larger images to match smallest
- **`keep_aspect_ratio`** - Maintain aspect ratio when resizing (default: `true`)
- **`border_thickness`** - Border width in pixels (default: `0`)
- **`border_color`** - Hex color or CSS color name (default: `"#ffffff"`)
- **`output_format`** - `"webp"`, `"jpg"`, `"jpeg"`, or `"png"` (default: `"webp"`)
- **`output_quality`** - Quality for lossy formats, 1-100 (default: `90`)

## Use cases

- **Before/after comparisons** - Show transformations side by side
- **Product showcases** - Display multiple angles or variations
- **Social media content** - Create Instagram-style multi-image posts
- **Documentation** - Combine screenshots or diagrams
- **Art portfolios** - Display multiple works in one frame

## How it works

The tool automatically handles the tricky parts of image merging:

1. **Size harmonization** - When images have different dimensions, you can choose to magnify smaller images, reduce larger ones, crop them, or keep original sizes

2. **Smart alignment** - Images align perfectly whether you want them at the start, center, or end of the strip

3. **Border consistency** - Borders are applied uniformly around the entire strip and between individual images

## Tips for best results

- **Similar aspect ratios** work best for clean strips
- **High resolution images** will give you crisp output
- **WebP format** provides the best balance of quality and file size
- **Horizontal strips** work great for before/after shots
- **Vertical strips** are perfect for mobile-friendly content

## Technical details

Built with:
- **PIL (Python Imaging Library)** for robust image processing
- **Cog** for easy deployment and API access
- **Smart memory management** for handling large image sets

The tool preserves image quality while optimizing file sizes, and handles transparency properly when working with PNG images.

## Deploying to Replicate

You can push this model to Replicate:

```bash
cog login
cog push r8.im/your-username/your-model-name
```

## License

MIT

---

Made by [zsxkib](https://x.com/zsakib_) • Follow for more AI tools 🚀
