"""Draws the app icon: a white clinical note with words highlighted in the app's colours.

Run from the flutter_app folder:  python make_icon.py
Creates assets/icon/icon.png, assets/icon/icon_foreground.png and assets/icon/preview.png
"""
import os

from PIL import Image, ImageDraw

OUT = os.path.join("assets", "icon")
os.makedirs(OUT, exist_ok=True)

TEAL = (13, 148, 136)
YELLOW, BLUE, RED = (253, 230, 138), (147, 197, 253), (252, 165, 165)
GREY = (203, 213, 225)
S = 1024


def draw_note(d, cx, cy, scale):
    w, h = int(520 * scale), int(640 * scale)
    x0, y0 = cx - w // 2, cy - h // 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(56 * scale), fill="white")
    lh, pad, gap = int(38 * scale), int(70 * scale), int(12 * scale)
    rows = [
        [(0.30, GREY), (0.40, YELLOW), (0.30, GREY)],
        [(0.55, GREY), (0.45, None)],
        [(0.25, GREY), (0.45, BLUE), (0.30, GREY)],
        [(0.70, GREY), (0.30, None)],
        [(0.40, GREY), (0.40, RED), (0.20, None)],
        [(0.50, GREY), (0.50, None)],
    ]
    inner = w - 2 * pad
    y = y0 + int(90 * scale)
    for row in rows:
        x = x0 + pad
        for frac, col in row:
            seg = int(inner * frac)
            if col is not None:
                grow = 0 if col == GREY else int(6 * scale)  # highlights stand a little taller
                d.rounded_rectangle([x, y - grow, x + seg - gap, y + lh + grow], radius=int(12 * scale), fill=col)
            x += seg
        y += int(lh + 44 * scale)


# Full icon (older Android, web): teal square with the note
full = Image.new("RGB", (S, S), TEAL)
draw_note(ImageDraw.Draw(full), S // 2, S // 2, 1.0)
full.save(os.path.join(OUT, "icon.png"))

# Adaptive icon foreground (Android 8+): transparent; Android adds the teal background and crops the shape
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
draw_note(ImageDraw.Draw(fg), S // 2, S // 2, 0.9)
fg.save(os.path.join(OUT, "icon_foreground.png"))

# Preview: square icon + circle-cropped adaptive icon
prev = Image.new("RGBA", (S, S), TEAL + (255,))
prev.alpha_composite(fg)
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse([0, 0, S, S], fill=255)
circle = Image.new("RGBA", (S, S), (255, 255, 255, 0))
circle.paste(prev, (0, 0), mask)
sheet = Image.new("RGB", (S * 2 + 60, S), "white")
sheet.paste(full, (0, 0))
sheet.paste(circle, (S + 60, 0), circle)
sheet.resize(((S * 2 + 60) // 2, S // 2)).save(os.path.join(OUT, "preview.png"))
print("Saved icon.png, icon_foreground.png and preview.png in", OUT)