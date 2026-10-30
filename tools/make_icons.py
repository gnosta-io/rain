"""Draw the Rain Dashboard app icon and write the PNG sizes phones and browsers use.

Usage: python tools/make_icons.py icons
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

out_dir = sys.argv[1]
os.makedirs(out_dir, exist_ok=True)

S = 2048  # draw large, scale down for smooth edges


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        draw.line([(0, y), (w, y)], fill=lerp(top, bottom, y / (h - 1)))
    return img


# Background: full-bleed dark navy, slightly lighter at the top (phones apply their own corner mask)
bg = vertical_gradient((S, S), (27, 35, 48), (11, 15, 21))

# Teardrop: a circle plus a point, sized to sit inside the maskable safe zone (inner 80% circle)
cx = S / 2
r = S * 0.205
D = r * 1.95                      # distance from circle center to the tip
top = S / 2 - (D + r) / 2 + S * 0.01
cy = top + D
phi = math.acos(r / D)
pts = [(cx, cy - D)]
start = -90 + math.degrees(phi)
end = 270 - math.degrees(phi)
steps = 240
for i in range(steps + 1):
    a = math.radians(start + (end - start) * i / steps)
    pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

mask = Image.new('L', (S, S), 0)
ImageDraw.Draw(mask).polygon(pts, fill=255)

# Soft glow behind the drop
glow = mask.filter(ImageFilter.GaussianBlur(S * 0.05))
bg = Image.composite(Image.new('RGB', (S, S), (78, 168, 255)), bg, glow.point(lambda v: int(v * 0.35)))

# Drop fill: light sky blue at the tip to deeper blue at the base
drop = vertical_gradient((S, S), (125, 196, 255), (37, 120, 230))
img = Image.composite(drop, bg, mask)

# Highlight: a curved white sheen on the left side of the drop
hl = Image.new('L', (S, S), 0)
box = (cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72)
ImageDraw.Draw(hl).arc(box, start=160, end=235, fill=255, width=round(r * 0.16))
hl = ImageChops.multiply(hl.filter(ImageFilter.GaussianBlur(r * 0.03)), mask)
img = Image.composite(Image.new('RGB', (S, S), (255, 255, 255)), img, hl.point(lambda v: int(v * 0.55)))

for name, size in [('icon-512.png', 512), ('icon-192.png', 192), ('apple-touch-icon.png', 180), ('favicon-32.png', 32)]:
    img.resize((size, size), Image.LANCZOS).save(os.path.join(out_dir, name), optimize=True)
    print('wrote', name)
