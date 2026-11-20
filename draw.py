"""Draws the 20 November 2026 news poster (1024x1024) with PIL and writes entry.png beside this file.

Fully deterministic: fixed colours, fixed fonts, no randomness, no timestamps in the PNG.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
REG = FONT_DIR + "DejaVuSans.ttf"

NAVY = (10, 20, 44)
PANEL = (19, 32, 64)
WHITE = (255, 255, 255)
GOLD = (240, 190, 70)
GREY = (150, 160, 180)
SUB = (205, 214, 230)


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, max_w, min_size=18):
    """Largest font size <= size whose rendered text fits max_w."""
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


# ---------------------------------------------------------------- icons
# Each icon draws inside a 80x80 box centred at (cx, cy), in white on a coloured disc.

def icon_scales(d, cx, cy):
    d.rectangle([cx - 2, cy - 22, cx + 2, cy + 20], fill=WHITE)  # post
    d.rectangle([cx - 14, cy + 18, cx + 14, cy + 23], fill=WHITE)  # base
    d.rectangle([cx - 24, cy - 20, cx + 24, cy - 16], fill=WHITE)  # beam
    for sx in (-22, 22):
        d.line([cx + sx, cy - 17, cx + sx - 9, cy + 3], fill=WHITE, width=2)
        d.line([cx + sx, cy - 17, cx + sx + 9, cy + 3], fill=WHITE, width=2)
        d.pieslice([cx + sx - 12, cy - 5, cx + sx + 12, cy + 13], 0, 180, fill=WHITE)


def icon_bridge(d, cx, cy):
    d.rectangle([cx - 28, cy + 4, cx + 28, cy + 9], fill=WHITE)  # deck
    for tx in (-14, 14):
        d.rectangle([cx + tx - 3, cy - 20, cx + tx + 3, cy + 22], fill=WHITE)  # towers
    for tx in (-14, 14):
        for ex in (-28, 0, 28):
            if abs(ex - tx) < 40:
                d.line([cx + tx, cy - 18, cx + ex, cy + 4], fill=WHITE, width=2)
    d.rectangle([cx - 28, cy + 22, cx + 28, cy + 25], fill=WHITE)  # water line


def icon_stars(d, cx, cy):
    r = 22
    for i in range(10):
        a = 2 * math.pi * i / 10 - math.pi / 2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        pts = []
        for k in range(10):
            ang = math.pi * k / 5 - math.pi / 2
            rr = 5.2 if k % 2 == 0 else 2.2
            pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
        d.polygon(pts, fill=WHITE)


def icon_chart(d, cx, cy):
    d.line([cx - 26, cy - 22, cx - 26, cy + 22, cx + 28, cy + 22], fill=WHITE, width=3)  # axes
    pts = [(cx - 20, cy - 14), (cx - 8, cy - 4), (cx, cy - 10), (cx + 12, cy + 8), (cx + 22, cy + 14)]
    d.line(pts, fill=WHITE, width=4, joint="curve")
    d.polygon([(cx + 28, cy + 18), (cx + 14, cy + 18), (cx + 26, cy + 4)], fill=WHITE)  # arrowhead


def icon_dome(d, cx, cy):
    d.pieslice([cx - 20, cy - 24, cx + 20, cy + 16], 180, 360, fill=WHITE)  # dome
    d.rectangle([cx - 20, cy - 4, cx + 20, cy], fill=WHITE)
    d.rectangle([cx - 2, cy - 32, cx + 2, cy - 22], fill=WHITE)  # flag mast
    for px in (-16, -6, 4, 14):
        d.rectangle([cx + px, cy + 3, cx + px + 4, cy + 18], fill=WHITE)  # columns
    d.rectangle([cx - 26, cy + 19, cx + 26, cy + 24], fill=WHITE)  # steps


# ---------------------------------------------------------------- content
STORIES = [
    ("JUSTICE", (232, 90, 90), icon_scales,
     "Myanmar, China reject ICJ genocide ruling",
     "20 Nov • Both call the Rohingya verdict “unfair”"),
    ("UKRAINE", (70, 150, 235), icon_bridge,
     "Russia hits Kyiv bridges in massive strikes",
     "20 Nov • 8 killed, 28 hurt; 3 Dnipro bridges struck"),
    ("EUROPE", (80, 190, 140), icon_stars,
     "EU and UK agree Brexit reset package",
     "20 Nov • Brussels summit: food, youth scheme, carbon"),
    ("MARKETS", (235, 140, 60), icon_chart,
     "Nikkei tumbles as AI sell-off deepens",
     "20 Nov • Nikkei down over 4%; Anthropic slides"),
    ("POLITICS", (170, 120, 230), icon_dome,
     "Trump defends Putin ties after Asia trip",
     "20 Nov • White House press briefing on return"),
]

FOOTER = "Sources: Al Jazeera, ABC News (AU), RTE, Moscow Times, Reuters, CNN, European Business Magazine"


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # Header
    f_title = fit(d, "20 NOVEMBER 2026", BOLD, 84, W - 80)
    tw = d.textlength("20 NOVEMBER 2026", font=f_title)
    d.text(((W - tw) / 2, 22), "20 NOVEMBER 2026", font=f_title, fill=WHITE)
    sub = "FRIDAY • THE WORLD IN FIVE STORIES"
    f_sub = fit(d, sub, BOLD, 29, W - 80)
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 120), sub, font=f_sub, fill=GOLD)
    d.rectangle([40, 166, W - 40, 170], fill=GOLD)

    # Rows
    top, rh, gap = 186, 142, 12
    text_x = 182
    max_w = W - text_x - 70  # keep clear padding before the panel's right edge
    for i, (cat, col, icon, head, subhead) in enumerate(STORIES):
        y = top + i * (rh + gap)
        d.rounded_rectangle([40, y, W - 40, y + rh], radius=10, fill=PANEL)
        d.rectangle([40, y, 54, y + rh], fill=col)  # colored left bar
        # number badge + icon disc
        cx, cy = 118, y + rh // 2
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=col)
        icon(d, cx, cy)
        nf = font(BOLD, 20)
        d.ellipse([70, y + 8, 98, y + 36], fill=NAVY)
        ntxt = str(i + 1)
        d.text((84 - d.textlength(ntxt, font=nf) / 2, y + 11), ntxt, font=nf, fill=WHITE)
        # text
        d.text((text_x, y + 14), f"{cat}", font=font(BOLD, 23), fill=col)
        fh = fit(d, head, BOLD, 40, max_w, 28)
        d.text((text_x, y + 46), head, font=fh, fill=WHITE)
        fs = fit(d, subhead, REG, 27, max_w, 20)
        d.text((text_x, y + 100), subhead, font=fs, fill=SUB)

    # Footer
    ff = fit(d, FOOTER, REG, 17, W - 80, 11)
    fw = d.textlength(FOOTER, font=ff)
    d.text(((W - fw) / 2, 988), FOOTER, font=ff, fill=GREY)

    img.save(os.path.join(HERE, "entry.png"), optimize=True)


if __name__ == "__main__":
    main()
