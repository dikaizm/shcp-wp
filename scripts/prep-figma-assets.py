"""Normalise Figma exports in assets/figma -> assets/ (web-ready).

JPEG data saved as .png gets a .jpg name; opaque photos become JPEG (q85);
images keep PNG only when they use transparency. Max width 1920.
Usage: python3 -I scripts/prep-figma-assets.py assets/figma assets
"""
import sys
from pathlib import Path
from PIL import Image

src, out = Path(sys.argv[1]), Path(sys.argv[2])
for f in sorted(src.iterdir()):
    im = Image.open(f)
    im.load()
    if im.width > 1920:
        im = im.resize((1920, round(im.height * 1920 / im.width)), Image.LANCZOS)
    alpha = im.mode in ("RGBA", "LA", "P") and im.convert("RGBA").getextrema()[3][0] < 250
    if alpha:
        im.save(out / f"{f.stem}.png", optimize=True)
    else:
        im.convert("RGB").save(out / f"{f.stem}.jpg", quality=85, optimize=True, progressive=True)
    print(f"{f.name:40} -> {f.stem}.{'png' if alpha else 'jpg'} {im.size}")
