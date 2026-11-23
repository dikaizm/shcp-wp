"""Cut placeholder images out of the flattened design PNGs.

Usage: python3 -I scripts/crop-placeholders.py <design_png_dir> <out_dir>
Replace with designer source assets when they arrive.
"""
import sys
from pathlib import Path
from PIL import Image

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(exist_ok=True)

# name: (page, (left, top, right, bottom)) in 1440px design coordinates
BOXES = {
    "logo-shcp": ("Homepage", (100, 30, 220, 92)),
    "logo-nicekyd-red": ("Homepage", (258, 4358, 424, 4418)),
    "logo-nicekyd-grey": ("Homepage", (458, 4358, 626, 4418)),
    "hero-home": ("Homepage", (0, 120, 1440, 840)),
    "home-about": ("Homepage", (0, 1300, 745, 1848)),
    "product-upr": ("Homepage", (170, 2082, 526, 2316)),
    "product-trading": ("Homepage", (570, 2075, 926, 2310)),
    "product-alkyd": ("Homepage", (970, 2075, 1326, 2310)),
    "home-solutions": ("Homepage", (0, 3100, 1425, 3705)),
    "cta-people": ("Homepage", (840, 3740, 1440, 4240)),
    "hero-products": ("Product", (0, 120, 1440, 760)),
    "hero-applications": ("Application", (0, 120, 1440, 760)),
    "hero-about": ("About Us", (0, 120, 1440, 840)),
    "about-vision": ("About Us", (0, 1570, 665, 2055)),
    "niser-bg": ("About Us", (0, 3045, 1440, 3963)),
    "about-plants": ("About Us", (112, 4840, 768, 5278)),
    "contact-people": ("Contact Us", (745, 120, 1440, 760)),
    "office-1": ("Contact Us", (112, 2120, 500, 2400)),
    "office-2": ("Contact Us", (525, 2120, 913, 2400)),
    "office-3": ("Contact Us", (938, 2120, 1328, 2400)),
    "app-hero-default": ("Application Detail", (790, 120, 1440, 720)),
}

# 240px tiles: application grid and strengths cards
COLS = (131, 445, 758, 1073)
APPS = [
    ("marine-boat-building", "pool-water-recreation", "automotive-transportation", "buttons-decorative-accessories"),
    ("sanitary-ware-bathroom", "ipal-wastewater-treatment", "construction-building-materials", "furniture-interior-design"),
    ("industrial-infrastructure", "casting-decorative-resin-art", "electrical-industrial-insulation"),
    ("decorative-wood-steel-coating", "anti-rust-primer", "marine-paint", "wood-finishes"),
    ("industrial-metal", "aerosol-spray-paint"),
]
for top, row in zip((1211, 1595, 1980, 2506, 2891), APPS):
    for x, slug in zip(COLS, row):
        BOXES[f"app-{slug}"] = ("Application", (x, top, x + 236, top + 236))
for x, name in zip(COLS, ("integrated", "manufacturing", "partnerships", "support")):
    BOXES[f"strength-{name}"] = ("About Us", (x, 2671, x + 236, 2904))

for name, (page, box) in BOXES.items():
    im = Image.open(src / f"{page}.png").convert("RGB").crop(box)
    if name == "home-solutions":
        # Paint out the baked-in "View Applications" button with the row's background colour.
        px = im.load()
        # Also paints out the baked subtitle line above it.
        for y in range(0, 140):
            c = px[690, y]
            for x in range(700, im.width):
                px[x, y] = c
    im.save(out / f"{name}.jpg", quality=88) if not name.startswith("logo") else im.save(out / f"{name}.png")
print(len(BOXES), "images")
