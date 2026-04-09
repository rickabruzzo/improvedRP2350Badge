#!/usr/bin/env python3
"""
logo_prep.py — Honeycomb London Dinner Badge
Resizes any company logo to badge spec: fit within 220×44px,
maintain aspect ratio, no upscaling, transparency preserved.

Usage:
    python logo_prep.py input_logo.png
    python logo_prep.py input_logo.png --out logo.png
    python logo_prep.py *.png              (batch mode)

Output file is always named 'logo.png' unless --out is specified.
For batch mode, outputs are written as logo_<inputname>.png in ./prepped/
"""

import sys
import os
from pathlib import Path
from PIL import Image

# Badge logo crop constraints
MAX_W = 220
MAX_H = 44


def hex_to_rgba(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r, g, b, 255)


def prep_logo(input_path: str, output_path: str = "logo.png", bg_color: str = None):
    """
    Resize a logo to fit within MAX_W x MAX_H.
    - Maintains aspect ratio
    - No upscaling (only downscales if needed)
    - Preserves transparency
    - If bg_color provided, flattens onto that background (preview only)
    """
    src = Path(input_path)
    if not src.exists():
        print(f"  ERROR: File not found: {input_path}")
        return False

    img = Image.open(src)

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    orig_w, orig_h = img.size

    # Scale down only — never upscale
    scale = min(MAX_W / orig_w, MAX_H / orig_h, 1.0)
    new_w = max(1, round(orig_w * scale))
    new_h = max(1, round(orig_h * scale))

    if scale < 1.0:
        img = img.resize((new_w, new_h), Image.LANCZOS)
        action = f"resized {orig_w}×{orig_h} → {new_w}×{new_h}"
    else:
        action = f"no resize needed ({orig_w}×{orig_h} already within {MAX_W}×{MAX_H})"

    if bg_color:
        bg = Image.new("RGBA", img.size, hex_to_rgba(bg_color))
        bg.paste(img, mask=img.split()[3])
        img = bg.convert("RGB")
        output_path = output_path.replace(".png", "_preview.png")

    img.save(output_path, "PNG")
    print(f"  ✓ {src.name} → {output_path} ({action})")
    return True


def batch_prep(input_paths: list, output_dir: str = "prepped"):
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    success = 0
    for path in input_paths:
        p = Path(path)
        out_path = str(out / f"logo_{p.stem}.png")
        if prep_logo(path, out_path):
            success += 1

    print(f"\n{success}/{len(input_paths)} logos prepped → ./{output_dir}/")


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    out_path = "logo.png"
    if "--out" in args:
        idx = args.index("--out")
        out_path = args[idx + 1]
        args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]

    if len(args) > 1:
        batch_prep(args)
    else:
        prep_logo(args[0], out_path)


if __name__ == "__main__":
    main()
