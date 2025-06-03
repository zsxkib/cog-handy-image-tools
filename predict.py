# Prediction interface for Cog ⚙️
# https://cog.run/python
"""
Merge up to five images into one horizontal or vertical strip.

• Drop-in defaults — upload a single picture, hit Run, and get the same image back
  (optionally ring-fenced by a border).
• Multi-image — upload 2-5 images to create a strip with alignment, size
  harmonisation and border control.
• Export — PNG (lossless), JPG/JPEG (quality), WebP (lossless at Q 100 or lossy).
"""

from __future__ import annotations

import tempfile
from typing import List, Optional

from cog import BasePredictor, Input, Path
from PIL import Image, ImageColor


class Predictor(BasePredictor):
    """Stitch 1-5 images into a single strip."""

    # ------------------------------------------------------------------ #
    # 🔮 predict                                                          #
    # ------------------------------------------------------------------ #
    def predict(  # noqa: PLR0913 - user-facing API needs several knobs
        self,
        image1: Path = Input(description="First image (required)"),
        image2: Optional[Path] = Input(description="Second image (optional)", default=None),
        image3: Optional[Path] = Input(description="Third image (optional)", default=None),
        image4: Optional[Path] = Input(description="Fourth image (optional)", default=None),
        image5: Optional[Path] = Input(description="Fifth image (optional)", default=None),
        orientation: str = Input(
            description="Direction of the strip",
            choices=["horizontal", "vertical"],
            default="horizontal",
        ),
        alignment: str = Input(
            description="Alignment perpendicular to orientation",
            choices=["start", "center", "end"],
            default="center",
        ),
        resize_strategy: str = Input(
            description="How to equalise sizes along the orientation axis",
            choices=["none", "magnify_smaller", "reduce_larger", "crop_larger"],
            default="reduce_larger",
        ),
        keep_aspect_ratio: bool = Input(
            description="Maintain aspect ratio when resizing", default=True
        ),
        border_thickness: int = Input(
            description="Border thickness (px) — around and between images",
            ge=0,
            default=0,
        ),
        border_color: str = Input(
            description="Border colour (hex or Pillow keyword)", default="#ffffff"
        ),
        output_format: str = Input(
            description="Output format",
            choices=["webp", "jpg", "jpeg", "png"],
            default="webp",
        ),
        output_quality: int = Input(
            description="Lossy quality 1-100 (ignored for PNG)",
            ge=1,
            le=100,
            default=90,
        ),
    ) -> Path:
        """Merge images and return the resulting file path."""
        # Gather all supplied images -------------------------------------
        images = [img for img in (image1, image2, image3, image4, image5) if img is not None]

        # 1️⃣ load --------------------------------------------------------
        pics = [Image.open(p).convert("RGBA") for p in images]

        # 2️⃣ harmonise sizes --------------------------------------------
        pics = self._harmonise(pics, orientation, resize_strategy, keep_aspect_ratio)

        # 3️⃣ canvas size -------------------------------------------------
        inner = border_thickness
        if orientation == "horizontal":
            cw = sum(im.width for im in pics) + inner * (len(pics) + 1)
            ch = max(im.height for im in pics) + inner * 2
        else:  # vertical
            cw = max(im.width for im in pics) + inner * 2
            ch = sum(im.height for im in pics) + inner * (len(pics) + 1)

        canvas = Image.new("RGBA", (cw, ch), ImageColor.getcolor(border_color, "RGBA"))

        # 4️⃣ paste -------------------------------------------------------
        ox, oy = inner, inner
        for im in pics:
            if orientation == "horizontal":
                y = oy + self._aligned_offset(ch - inner * 2, im.height, alignment)
                canvas.paste(im, (ox, y), mask=im)
                ox += im.width + inner
            else:
                x = ox + self._aligned_offset(cw - inner * 2, im.width, alignment)
                canvas.paste(im, (x, oy), mask=im)
                oy += im.height + inner

        # 5️⃣ export ------------------------------------------------------
        ext = output_format.lower()
        if ext == "jpeg":
            ext = "jpg"
        outfile = Path(tempfile.mkdtemp()) / f"merged.{ext}"

        final = canvas.convert("RGB") if ext == "jpg" else canvas
        save_params: dict[str, int | bool] = {}
        if ext in {"jpg", "webp"}:
            save_params["quality"] = output_quality
            save_params["optimize"] = True
            if ext == "webp" and output_quality == 100:
                save_params["lossless"] = True

        final.save(outfile, **save_params)
        print(
            f"[+] {len(pics)} image(s) → {final.width}×{final.height} "
            f"{ext.upper()} (Q={output_quality})"
        )
        return outfile

    # ------------------------------------------------------------------ #
    # 🛠 helpers                                                          #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _aligned_offset(container: int, item: int, align: str) -> int:
        if align == "start":
            return 0
        if align == "center":
            return (container - item) // 2
        if align == "end":
            return container - item
        raise ValueError("alignment must be 'start', 'center', or 'end'")

    @staticmethod
    def _harmonise(
        images: List[Image.Image],
        orientation: str,
        strategy: str,
        keep_ar: bool,
    ) -> List[Image.Image]:
        """Resize/crop so each image shares size along *orientation* axis."""
        if len(images) == 1 or strategy == "none":
            return images

        axis = 1 if orientation == "horizontal" else 0  # 0 → width, 1 → height
        sizes = [im.size[axis] for im in images]
        if len(set(sizes)) == 1:
            return images

        if strategy == "magnify_smaller":
            target = max(sizes)
            cmp = lambda s: s < target  # noqa: E731
            op = Predictor._resize_axis
        elif strategy == "reduce_larger":
            target = min(sizes)
            cmp = lambda s: s > target  # noqa: E731
            op = Predictor._resize_axis
        elif strategy == "crop_larger":
            target = min(sizes)
            cmp = lambda s: s > target  # noqa: E731
            op = Predictor._crop_axis
        else:
            raise ValueError("Unknown resize_strategy")

        return [
            op(im, axis, target, keep_ar) if cmp(sz) else im
            for im, sz in zip(images, sizes)
        ]

    # -- low-level ops ---------------------------------------------------
    @staticmethod
    def _resize_axis(im: Image.Image, ax: int, target: int, keep_ar: bool) -> Image.Image:
        w, h = im.size
        if ax == 0:  # adjust width
            h = round(h * target / w) if keep_ar else h
            w = target
        else:  # adjust height
            w = round(w * target / h) if keep_ar else w
            h = target
        return im.resize((w, h), Image.LANCZOS)

    @staticmethod
    def _crop_axis(im: Image.Image, ax: int, target: int, _: bool) -> Image.Image:
        if ax == 0:  # crop width
            left = (im.width - target) // 2
            box = (left, 0, left + target, im.height)
        else:  # crop height
            top = (im.height - target) // 2
            box = (0, top, im.width, top + target)
        return im.crop(box)
