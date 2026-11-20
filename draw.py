"""make.fun news poster, Friday 20 November 2026: a newspaper front page (1024x1024).

Pure PIL drawing, no external images, no network, no randomness, no timestamps.
Usage: python3 draw.py [output_dir]   (default: directory of this file)
Writes <output_dir>/entry.png
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SERIF = FD + "DejaVuSerif.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

PAPER = (247, 241, 227)
INK = (24, 22, 20)
RED = (150, 28, 28)
GREY = (90, 84, 76)
RULE = (60, 54, 48)
TAN = (214, 196, 156)
SEA = (205, 216, 222)

_fc = {}


def F(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def wrap(text, font, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit_block(text, path, maxw, maxlines, start, minsize, lead=1.28):
    """Largest size whose wrapped text fits maxw within maxlines. Returns (font, lines, lineheight)."""
    for s in range(start, minsize - 1, -1):
        f = F(path, s)
        lines = wrap(text, f, maxw)
        if len(lines) <= maxlines and all(f.getlength(l) <= maxw for l in lines):
            return f, lines, int(s * lead)
    raise ValueError("text does not fit: " + text)


def fit_line(text, path, maxw, start, minsize=8):
    for s in range(start, minsize - 1, -1):
        if F(path, s).getlength(text) <= maxw:
            return F(path, s)
    raise ValueError("line does not fit: " + text)


def ctext(d, cx, y, text, font, fill):
    d.text((cx - font.getlength(text) / 2, y), text, font=font, fill=fill)


# ---------- supersampled vector helper ----------
K = 4


class SD:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (w * K, h * K), bg)
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon(self._p(pts), fill=fill, outline=outline, width=width * K)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=outline, width=width * K)

    def ell(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=outline, width=width * K)

    def line(self, pts, fill, width=1):
        self.d.line(self._p(pts), fill=fill, width=max(1, int(width * K)), joint="curve")

    def pie(self, box, a0, a1, fill):
        self.d.pieslice([v * K for v in box], a0, a1, fill=fill)

    def out(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def vgrad(s, y0, y1, c0, c1, x0=0, x1=None):
    x1 = s.w if x1 is None else x1
    n = int((y1 - y0) * 2)
    for i in range(n):
        t = i / max(1, n - 1)
        c = tuple(int(c0[j] + (c1[j] - c0[j]) * t) for j in range(3))
        s.rect(x0, y0 + i / 2, x1, y0 + (i + 1) / 2 + 0.2, fill=c)


def star(cx, cy, r, rot=-90):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.4
        a = math.radians(rot + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def frame_panel(page, img, x, y):
    page.paste(img, (x, y))
    ImageDraw.Draw(page).rectangle([x, y, x + img.width - 1, y + img.height - 1], outline=INK, width=2)


# ---------- illustrations ----------
def ill_kyiv(w, h):
    s = SD(w, h, (14, 20, 44))
    vgrad(s, 0, h * 0.72, (12, 16, 40), (120, 52, 36))
    # stars
    for i in range(26):
        sx = (i * 97) % w
        sy = (i * 53) % int(h * 0.45)
        s.ell(sx, sy, sx + 1.4, sy + 1.4, fill=(230, 225, 200))
    # river
    s.rect(0, h * 0.72, w, h, fill=(28, 34, 62))
    # skyline
    hor = h * 0.72
    bl = [(0, 40, 22), (22, 62, 26), (48, 34, 20), (68, 52, 24), (92, 78, 18), (110, 44, 30)]
    for bx, bh, bw in bl:
        s.rect(bx, hor - bh, bx + bw, hor, fill=(18, 16, 30))
        for wy in range(int(hor - bh + 6), int(hor - 6), 9):
            for wx in range(bx + 4, bx + bw - 4, 7):
                if (wx * 3 + wy) % 5 < 2:
                    s.rect(wx, wy, wx + 2.5, wy + 3.5, fill=(240, 190, 90))
    # golden-domed church (right side)
    cx = 226
    s.rect(cx - 16, hor - 38, cx + 16, hor, fill=(26, 20, 34))
    s.rect(cx - 8, hor - 52, cx + 8, hor - 38, fill=(26, 20, 34))
    for dx, top in ((-12, 62), (0, 70), (12, 62)):
        s.pie([cx + dx - 6, hor - top, cx + dx + 6, hor - top + 12], 180, 360, (222, 170, 52))
        s.line([(cx + dx, hor - top), (cx + dx, hor - top - 5)], (222, 170, 52), 1)
    for bx, bh, bw in ((260, 50, 24), (284, 36, 20), (150, 58, 26), (176, 40, 22)):
        s.rect(bx, hor - bh, bx + bw, hor, fill=(18, 16, 30))
        for wy in range(int(hor - bh + 6), int(hor - 6), 9):
            for wx in range(bx + 4, bx + bw - 4, 7):
                if (wx + wy * 2) % 5 < 2:
                    s.rect(wx, wy, wx + 2.5, wy + 3.5, fill=(240, 190, 90))
    # bridge with arches
    by = hor + 4
    s.rect(0, by, w, by + 5, fill=(10, 10, 16))
    for i in range(0, w, 52):
        s.pie([i - 2, by - 2, i + 50, by + 40], 180, 360, (10, 10, 16))
        s.pie([i + 4, by + 3, i + 44, by + 34], 180, 360, (28, 34, 62))
    # burning section
    for fx, fh in ((150, 30), (160, 42), (170, 28), (180, 36), (190, 22)):
        s.poly([(fx - 6, by + 2), (fx, by + 2 - fh), (fx + 6, by + 2)], fill=(255, 120, 20))
        s.poly([(fx - 3, by + 2), (fx, by + 2 - fh * 0.6), (fx + 3, by + 2)], fill=(255, 220, 90))
    # reflection of fire
    for i in range(6):
        s.rect(148 + i * 8, by + 8 + i * 4, 160 + i * 8, by + 11 + i * 4, fill=(190, 90, 30))
    # missile trails
    for x0, y0, x1, y1 in ((40, 4, 118, 84), (130, 0, 170, 70), (215, 6, 188, 86)):
        for t in range(0, 16):
            a = t / 15
            px, py = x0 + (x1 - x0) * a, y0 + (y1 - y0) * a
            c = (255, int(110 + 120 * a), int(50 + 90 * a))
            s.ell(px - 1.6 - 1.4 * a, py - 1.6 - 1.4 * a, px + 1.6 + 1.4 * a, py + 1.6 + 1.4 * a, fill=c)
        s.ell(x1 - 4, y1 - 4, x1 + 4, y1 + 4, fill=(255, 250, 200))
    return s.out()


def ill_icj(w, h):
    s = SD(w, h, (200, 212, 222))
    vgrad(s, 0, h, (222, 230, 236), (176, 192, 206))
    # court building
    bx0, bx1 = 14, 162
    s.rect(bx0 - 6, h - 16, bx1 + 6, h, fill=(120, 124, 132))
    s.rect(bx0 - 2, h - 24, bx1 + 2, h - 16, fill=(150, 154, 160))
    s.poly([(bx0 - 4, 56), ((bx0 + bx1) / 2, 22), (bx1 + 4, 56)], fill=(236, 232, 222), outline=(90, 90, 96), width=2)
    s.rect(bx0 - 2, 56, bx1 + 2, 64, fill=(226, 222, 212), outline=(90, 90, 96), width=1)
    n = 6
    for i in range(n):
        cx = bx0 + 8 + i * (bx1 - bx0 - 16) / (n - 1)
        s.rect(cx - 6, 64, cx + 6, h - 24, fill=(238, 234, 224), outline=(120, 120, 126), width=1)
        s.line([(cx - 2, 66), (cx - 2, h - 26)], (205, 200, 190), 1)
    s.ell(((bx0 + bx1) / 2) - 6, 36, ((bx0 + bx1) / 2) + 6, 48, fill=(176, 150, 70))
    # scales of justice
    cx = 226
    gold, dk = (170, 126, 30), (120, 86, 20)
    s.rect(cx - 22, h - 12, cx + 22, h - 4, fill=dk)
    s.rect(cx - 14, h - 22, cx + 14, h - 12, fill=gold)
    s.rect(cx - 3, 30, cx + 3, h - 22, fill=gold)
    s.ell(cx - 7, 24, cx + 7, 38, fill=gold)
    s.line([(cx - 56, 46), (cx + 56, 46)], dk, 4)
    s.ell(cx - 5, 42, cx + 5, 52, fill=gold)
    for sx in (cx - 54, cx + 54):
        s.line([(sx, 46), (sx - 22, 96)], dk, 1.4)
        s.line([(sx, 46), (sx + 22, 96)], dk, 1.4)
        s.pie([sx - 26, 80, sx + 26, 114], 0, 180, gold)
        s.line([(sx - 26, 97), (sx + 26, 97)], dk, 1.5)
    return s.out()


def ill_markets(w, h):
    s = SD(w, h, (20, 22, 30))
    s.rect(0, 0, w, h, fill=(22, 24, 34))
    for gy in range(14, h, 26):
        s.line([(0, gy), (w, gy)], (46, 50, 64), 0.8)
    for gx in range(20, w, 40):
        s.line([(gx, 0), (gx, h)], (38, 42, 56), 0.8)
    pts = [(8, 18), (34, 26), (58, 20), (84, 44), (110, 40), (138, 70), (166, 62), (196, 98), (226, 90), (262, 138), (300, 148)]
    pts = [(px, py * h / 150.0) for px, py in pts]
    # area fill
    s.poly(pts + [(300, h), (8, h)], fill=(70, 24, 30))
    # candles
    for i, (px, py) in enumerate(pts[:-1]):
        c = (214, 54, 54)
        s.line([(px, py - 10), (px, py + 22)], c, 1.2)
        s.rect(px - 4, py, px + 4, py + 14, fill=c)
    s.line(pts, (255, 86, 80), 3)
    s.ell(pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5, fill=(255, 120, 110))
    s.poly([(284, 106 * h / 150.0), (308, 106 * h / 150.0), (296, 124 * h / 150.0)], fill=(255, 86, 80))
    return s.out(), pts


def ill_eu_uk(w, h):
    s = SD(w, h, (236, 228, 208))
    vgrad(s, 0, h, (226, 234, 242), (196, 208, 222))
    # EU flag
    ex, ey, ew, eh = 6, 8, 90, 60
    s.rect(ex, ey, ex + ew, ey + eh, fill=(0, 51, 153))
    for i in range(12):
        a = math.radians(i * 30)
        s.poly(star(ex + ew / 2 + 20 * math.cos(a), ey + eh / 2 + 20 * math.sin(a), 4.2), fill=(255, 204, 0))
    s.rect(ex, ey, ex + ew, ey + eh, outline=(40, 40, 50), width=1)
    # Union Jack
    ux, uy, uw, uh = 56, 44, 90, 56
    s.rect(ux, uy, ux + uw, uy + uh, fill=(1, 33, 105))
    for wd, col in ((11, (255, 255, 255)), (5, (200, 16, 46))):
        s.line([(ux, uy), (ux + uw, uy + uh)], col, wd)
        s.line([(ux + uw, uy), (ux, uy + uh)], col, wd)
    s.rect(ux, uy + uh / 2 - 9, ux + uw, uy + uh / 2 + 9, fill=(255, 255, 255))
    s.rect(ux + uw / 2 - 9, uy, ux + uw / 2 + 9, uy + uh, fill=(255, 255, 255))
    s.rect(ux, uy + uh / 2 - 5, ux + uw, uy + uh / 2 + 5, fill=(200, 16, 46))
    s.rect(ux + uw / 2 - 5, uy, ux + uw / 2 + 5, uy + uh, fill=(200, 16, 46))
    s.rect(ux, uy, ux + uw, uy + uh, outline=(40, 40, 50), width=1)
    return s.out()


def ill_whitehouse(w, h):
    s = SD(w, h, (170, 205, 235))
    vgrad(s, 0, h, (120, 170, 220), (214, 230, 244))
    s.rect(0, h - 14, w, h, fill=(96, 140, 84))
    cx = w / 2
    wall = (244, 242, 236)
    shade = (190, 188, 182)
    # wings
    s.rect(6, h - 44, w - 6, h - 14, fill=wall, outline=shade, width=1)
    for x in range(14, w - 10, 12):
        if abs(x - cx) > 36:
            s.rect(x, h - 38, x + 5, h - 28, fill=(90, 110, 140))
    # centre block + columns
    s.rect(cx - 36, h - 62, cx + 36, h - 44, fill=wall, outline=shade, width=1)
    s.poly([(cx - 40, h - 62), (cx, h - 78), (cx + 40, h - 62)], fill=wall, outline=shade, width=1)
    for i in range(6):
        x = cx - 30 + i * 12
        s.rect(x - 2, h - 60, x + 2, h - 44, fill=(255, 255, 255), outline=shade, width=1)
    # flag
    s.line([(cx, h - 78), (cx, h - 98)], (60, 60, 60), 1.2)
    s.poly([(cx, h - 98), (cx + 14, h - 94), (cx, h - 90)], fill=(190, 30, 45))
    # capitol-style dome behind
    return s.out()


def ill_dome(w, h):
    s = SD(w, h, (170, 205, 235))
    vgrad(s, 0, h, (120, 170, 220), (214, 230, 244))
    s.rect(0, h - 12, w, h, fill=(96, 140, 84))
    cx = w / 2
    wall = (244, 242, 236)
    shade = (180, 178, 172)
    s.rect(8, h - 36, w - 8, h - 12, fill=wall, outline=shade, width=1)
    for x in range(16, w - 12, 10):
        s.rect(x, h - 31, x + 4, h - 20, fill=(90, 110, 140))
    s.rect(cx - 24, h - 48, cx + 24, h - 36, fill=wall, outline=shade, width=1)
    s.rect(cx - 15, h - 62, cx + 15, h - 48, fill=wall, outline=shade, width=1)
    for i in range(5):
        x = cx - 12 + i * 6
        s.line([(x, h - 60), (x, h - 49)], shade, 1)
    s.pie([cx - 22, h - 98, cx + 22, h - 54], 180, 360, (236, 234, 228))
    s.pie([cx - 22, h - 98, cx + 22, h - 54], 180, 360, None) if False else None
    for i in range(-3, 4):
        s.line([(cx + i * 6, h - 76 - (22 - abs(i) * 3) * 0), (cx + i * 6 * 0.25, h - 98)], shade, 0.8)
    s.rect(cx - 5, h - 108, cx + 5, h - 98, fill=wall, outline=shade, width=1)
    s.poly([(cx - 4, h - 108), (cx, h - 118), (cx + 4, h - 108)], fill=(226, 224, 218))
    return s.out()


# ---------- world map ----------
MAP = {
    "na": [(-168, 66), (-156, 71), (-125, 70), (-95, 70), (-80, 63), (-65, 60), (-56, 52), (-66, 45), (-70, 42), (-76, 35), (-81, 30), (-80, 25), (-84, 30), (-90, 29), (-97, 26), (-97, 20), (-90, 21), (-87, 21), (-83, 10), (-78, 8), (-85, 10), (-92, 15), (-105, 20), (-112, 28), (-117, 32), (-124, 40), (-124, 48), (-135, 57), (-150, 60), (-160, 58), (-165, 62)],
    "gl": [(-72, 78), (-55, 82), (-25, 82), (-20, 72), (-40, 64), (-50, 62), (-58, 70)],
    "sa": [(-78, 8), (-72, 12), (-62, 10), (-50, 0), (-35, -6), (-39, -15), (-48, -26), (-58, -35), (-65, -42), (-68, -52), (-74, -50), (-73, -40), (-71, -20), (-76, -14), (-81, -5), (-79, 1)],
    "eu": [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (2, 51), (8, 54), (8, 57), (12, 56), (14, 54), (22, 55), (28, 60), (22, 63), (18, 60), (16, 56), (10, 58), (5, 60), (5, 62), (14, 68), (25, 71), (31, 70), (40, 67), (60, 69), (70, 73), (80, 73), (100, 77), (115, 74), (140, 72), (160, 70), (180, 68), (180, 65), (165, 60), (156, 51), (150, 59), (140, 54), (135, 44), (129, 41), (129, 35), (126, 35), (125, 39), (121, 40), (122, 31), (120, 25), (110, 20), (108, 16), (109, 11), (105, 9), (100, 13), (100, 5), (104, 1), (98, 8), (98, 16), (94, 17), (92, 22), (87, 21), (80, 15), (77, 8), (73, 17), (72, 21), (67, 24), (57, 26), (50, 30), (48, 29), (51, 25), (56, 26), (58, 23), (52, 16), (43, 13), (35, 28), (34, 31), (36, 36), (28, 37), (26, 40), (23, 38), (22, 37), (19, 41), (18, 40), (13, 44), (9, 44), (3, 43), (0, 39), (-6, 36)],
    "af": [(-17, 21), (-6, 35), (10, 37), (32, 31), (43, 12), (51, 12), (40, -5), (40, -15), (35, -25), (27, -34), (18, -34), (12, -17), (9, -1), (8, 4), (-8, 4), (-17, 14)],
    "au": [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -27), (150, -37), (141, -38), (131, -31), (115, -34)],
    "uk": [(-6, 50), (2, 51), (0, 53), (-3, 58), (-6, 57), (-5, 54), (-3, 54)],
    "ie": [(-10, 52), (-6, 52), (-6, 55), (-9, 54)],
    "jp": [(131, 34), (135, 34), (140, 35), (142, 38), (141, 41), (139, 40), (136, 37), (132, 35)],
    "hk": [(140, 42), (145, 43), (142, 45)],
    "su": [(95, 5), (104, -5), (106, -6), (98, 2)],
    "bo": [(109, 1), (117, 7), (119, 1), (116, -4), (110, -3)],
    "mg": [(44, -13), (50, -15), (47, -25), (44, -22)],
    "nz": [(172, -35), (178, -38), (174, -42), (170, -46), (167, -45)],
}
# (pin data, map drawing and small illustration banners for the 33-story page)
# story number, lon, lat
PINS = [
    (1, 30.5, 50.4), (2, 84.9, 19.3), (3, 139.7, 35.7), (4, 30.7, 36.9), (5, 96.1, 19.7),
    (6, 4.35, 50.85), (7, 139.7, 35.7), (8, 174.8, -41.3), (9, 12.5, 41.9), (10, 35.6, 3.1),
    (11, 22.5, 50.0), (12, 44.2, 32.9), (13, -77.0, 38.9), (14, 24.0, 49.8), (15, -74.0, 40.7),
    (16, -121.9, 37.4), (17, -122.4, 37.8), (18, 121.5, 25.0), (19, 139.7, 35.7), (20, 127.0, 37.5),
    (21, 116.4, 39.9), (22, 2.2, 41.4), (23, 42.5, 17.0), (24, 33.8, -14.0), (25, -115.1, 36.2),
    (26, 114.1, 22.5), (27, 56.3, 26.6), (28, 49.1, 14.5), (29, 7.5, 9.1), (30, 13.4, 52.5),
    (31, 30.7, 46.5), (32, 21.0, 52.2), (33, -75.7, 45.4),
]


def place_pins(pts, w, h, r):
    """Deterministic relaxation: push overlapping pin circles apart (fixed iteration order)."""
    pos = [[px, py - 9.0] for px, py in pts]
    md = 2 * r + 1.5
    for _ in range(400):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx = pos[j][0] - pos[i][0]
                dy = pos[j][1] - pos[i][1]
                dd = math.hypot(dx, dy)
                if dd < md:
                    if dd < 1e-6:
                        dx, dy, dd = 1.0, 0.3 * (1 if (i + j) % 2 else -1), 1.04
                    push = (md - dd) / 2 + 0.05
                    ux, uy = dx / dd, dy / dd
                    pos[i][0] -= ux * push
                    pos[i][1] -= uy * push
                    pos[j][0] += ux * push
                    pos[j][1] += uy * push
                    moved = True
        for p in pos:
            p[0] = min(max(p[0], r + 2), w - r - 2)
            p[1] = min(max(p[1], r + 2), h - r - 2)
        if not moved:
            break
    return pos


def draw_map(page, x, y, w, h):
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 78.0, -52.0

    def pr(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * w, (lat0 - lat) / (lat0 - lat1) * h)

    s = SD(w, h, SEA)
    for lon in range(-150, 190, 30):
        s.line([pr(lon, lat0), pr(lon, lat1)], (190, 202, 210), 0.7)
    for lat in range(60, -52, -30):
        s.line([pr(lon0, lat), pr(lon1, lat)], (190, 202, 210), 0.7)
    for pts in MAP.values():
        s.poly([pr(*p) for p in pts], fill=TAN, outline=(170, 150, 110), width=1)
    img = s.out()
    page.paste(img, (x, y))
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)
    r = 6.2
    true = [pr(lon, lat) for n, lon, lat in PINS]
    pos = place_pins(true, w, h, r)
    for (tx, ty), (cx_, cy_) in zip(true, pos):
        d.line([x + tx, y + ty, x + cx_, y + cy_], fill=RED, width=1)
        d.ellipse([x + tx - 1.5, y + ty - 1.5, x + tx + 1.5, y + ty + 1.5], fill=RED)
    nf = F(SANS_B, 8)
    for (n, _, _), (cx_, cy_) in zip(PINS, pos):
        d.ellipse([x + cx_ - r, y + cy_ - r, x + cx_ + r, y + cy_ + r], fill=RED, outline=(255, 255, 255), width=1)
        d.text((x + cx_, y + cy_ + 0.5), str(n), font=nf, fill=(255, 255, 255), anchor="mm")


# ---------- small banner illustrations (w x h) ----------
def ill_cyclone(w, h):
    s = SD(w, h, (60, 70, 92))
    vgrad(s, 0, h, (52, 60, 84), (120, 138, 160))
    ex, ey = w * 0.58, h * 0.46
    for arm in range(4):
        for i in range(46):
            t = i / 45
            a = math.radians(arm * 90 + t * 250)
            rr = 14 + t * 74
            px, py = ex + rr * math.cos(a), ey + rr * math.sin(a) * 0.62
            sz = 3 + 9 * (1 - t)
            c = int(236 - 40 * t)
            s.ell(px - sz, py - sz * 0.6, px + sz, py + sz * 0.6, fill=(c, c, min(255, c + 8)))
    s.ell(ex - 8, ey - 5, ex + 8, ey + 5, fill=(44, 56, 80))
    # coast
    s.poly([(w * 0.62, h), (w * 0.70, h * 0.86), (w * 0.86, h * 0.80), (w, h * 0.74), (w, h)], fill=(70, 110, 72))
    s.line([(w * 0.70, h * 0.86), (w * 0.86, h * 0.80), (w, h * 0.74)], (230, 230, 220), 1.5)
    for k in range(5):
        px = w * 0.76 + k * 14
        s.line([(px, h * 0.94), (px - 3, h * 0.84)], (30, 60, 34), 1.4)
        s.poly([(px - 3, h * 0.84), (px - 10, h * 0.86), (px - 4, h * 0.82), (px + 3, h * 0.80)], fill=(40, 90, 44))
    return s.out()


def ic_cop(w, h):
    s = SD(w, h, (200, 224, 226))
    vgrad(s, 0, h, (170, 214, 222), (226, 238, 232))
    cx, cy, r = 46, h / 2, h * 0.42
    s.ell(cx - r, cy - r, cx + r, cy + r, fill=(40, 104, 170))
    s.poly([(cx - 14, cy - 12), (cx - 2, cy - 18), (cx + 6, cy - 6), (cx - 4, cy + 4), (cx - 14, cy - 2)], fill=(70, 160, 90))
    s.poly([(cx + 6, cy + 6), (cx + 16, cy), (cx + 14, cy + 14), (cx + 6, cy + 14)], fill=(70, 160, 90))
    # thermometer
    tx = 94
    s.rect(tx - 4, 8, tx + 4, h - 16, fill=(250, 250, 250), outline=(90, 90, 96), width=1)
    s.rect(tx - 2, 20, tx + 2, h - 14, fill=(200, 40, 40))
    s.ell(tx - 8, h - 20, tx + 8, h - 4, fill=(200, 40, 40), outline=(90, 90, 96), width=1)
    # barred table / stamp
    s.rect(122, 10, w - 8, h - 10, outline=(170, 30, 30), width=2)
    return s.out()


def ic_scales(w, h):
    s = SD(w, h, (214, 224, 232))
    vgrad(s, 0, h, (226, 234, 240), (186, 200, 212))
    cx = w / 2
    gold, dk = (170, 126, 30), (120, 86, 20)
    s.rect(cx - 18, h - 8, cx + 18, h - 2, fill=dk)
    s.rect(cx - 2.5, 8, cx + 2.5, h - 8, fill=gold)
    s.line([(cx - 46, 14), (cx + 46, 14)], dk, 3)
    for sx in (cx - 44, cx + 44):
        s.line([(sx, 14), (sx - 16, 34)], dk, 1)
        s.line([(sx, 14), (sx + 16, 34)], dk, 1)
        s.pie([sx - 18, 26, sx + 18, 46], 0, 180, gold)
    return s.out()


def ic_euuk(w, h):
    s = SD(w, h, (226, 234, 242))
    vgrad(s, 0, h, (226, 234, 242), (196, 208, 222))
    ex, ey, ew, eh = 14, 8, 72, h - 16
    s.rect(ex, ey, ex + ew, ey + eh, fill=(0, 51, 153))
    for i in range(12):
        a = math.radians(i * 30)
        s.poly(star(ex + ew / 2 + 14 * math.cos(a), ey + eh / 2 + 14 * math.sin(a), 3.4), fill=(255, 204, 0))
    ux, uy, uw, uh = w - 86, 8, 72, h - 16
    s.rect(ux, uy, ux + uw, uy + uh, fill=(1, 33, 105))
    for wd, col in ((9, (255, 255, 255)), (4, (200, 16, 46))):
        s.line([(ux, uy), (ux + uw, uy + uh)], col, wd)
        s.line([(ux + uw, uy), (ux, uy + uh)], col, wd)
    s.rect(ux, uy + uh / 2 - 7, ux + uw, uy + uh / 2 + 7, fill=(255, 255, 255))
    s.rect(ux + uw / 2 - 7, uy, ux + uw / 2 + 7, uy + uh, fill=(255, 255, 255))
    s.rect(ux, uy + uh / 2 - 4, ux + uw, uy + uh / 2 + 4, fill=(200, 16, 46))
    s.rect(ux + uw / 2 - 4, uy, ux + uw / 2 + 4, uy + uh, fill=(200, 16, 46))
    # clasped hands marker
    s.ell(w / 2 - 7, h / 2 - 7, w / 2 + 7, h / 2 + 7, fill=(255, 255, 255), outline=(60, 60, 70), width=1)
    s.line([(w / 2 - 4, h / 2), (w / 2 + 4, h / 2)], (60, 60, 70), 1.6)
    return s.out()


def ic_japan(w, h):
    s = SD(w, h, (250, 246, 238))
    s.rect(0, 0, w, h, fill=(250, 246, 238))
    s.ell(30, 6, 30 + h - 12, h - 6, fill=(188, 0, 45))
    # rising bars
    for i in range(6):
        bh = 8 + i * 6
        s.rect(w - 110 + i * 17, h - 6 - bh, w - 110 + i * 17 + 11, h - 6, fill=(188, 0, 45) if i > 3 else (120, 120, 130))
    s.line([(w - 112, h - 12), (w - 20, 10)], (30, 30, 36), 1.4)
    return s.out()


def ic_cricket(w, h):
    s = SD(w, h, (140, 190, 232))
    vgrad(s, 0, h, (130, 184, 232), (214, 232, 244))
    s.rect(0, h - 16, w, h, fill=(80, 150, 70))
    s.rect(w * 0.18, h - 16, w * 0.82, h - 10, fill=(206, 184, 130))
    for k in range(3):
        s.rect(w * 0.82 + k * 5, h - 40, w * 0.82 + k * 5 + 2, h - 14, fill=(240, 228, 190))
    # bat
    s.poly([(52, h - 12), (60, h - 12), (86, 16), (78, 14)], fill=(214, 170, 96), outline=(120, 80, 30), width=1)
    s.rect(76, 6, 87, 18, fill=(60, 60, 70))
    s.ell(106, h - 38, 120, h - 24, fill=(190, 30, 40))
    return s.out()


def ic_italy(w, h):
    s = SD(w, h, (240, 236, 224))
    fx, fw = 12, 62
    s.rect(fx, 8, fx + fw / 3, h - 8, fill=(0, 146, 70))
    s.rect(fx + fw / 3, 8, fx + 2 * fw / 3, h - 8, fill=(252, 252, 252))
    s.rect(fx + 2 * fw / 3, 8, fx + fw, h - 8, fill=(206, 43, 55))
    # crowd + banner
    s.line([(98, 8), (98, h - 4)], (90, 70, 40), 1.6)
    s.rect(98, 8, 170, 24, fill=(206, 43, 55))
    for k in range(9):
        px = 92 + k * 10
        col = ((60, 70, 100), (100, 60, 60), (50, 90, 80))[k % 3]
        s.ell(px - 3.5, h - 24, px + 3.5, h - 17, fill=(224, 190, 160))
        s.rect(px - 4.5, h - 17, px + 4.5, h - 2, fill=col)
    return s.out()


def ic_kenya(w, h):
    s = SD(w, h, (240, 190, 120))
    vgrad(s, 0, h, (240, 176, 110), (250, 224, 170))
    s.rect(0, h - 12, w, h, fill=(190, 140, 80))
    cx = w / 2
    s.poly([(cx - 22, h - 12), (cx, 6), (cx + 22, h - 12)], outline=(50, 40, 34), width=2)
    for k in range(1, 4):
        yy = 6 + k * (h - 18) / 4
        hw = 22 * (yy - 6) / (h - 18)
        s.line([(cx - hw, yy), (cx + hw, yy)], (50, 40, 34), 1.2)
    s.line([(cx - 22, h - 12), (cx + 13, 6 + (h - 18) * 0.5)], (50, 40, 34), 1)
    s.line([(cx + 22, h - 12), (cx - 13, 6 + (h - 18) * 0.5)], (50, 40, 34), 1)
    s.line([(cx, 6), (cx, h - 12)], (50, 40, 34), 2)
    s.ell(cx + 50, h - 22, cx + 76, h - 12, fill=(30, 28, 28))
    s.ell(cx + 60, h - 30, cx + 66, h - 22, fill=(30, 28, 28))
    return s.out()


def ic_poland(w, h):
    s = SD(w, h, (24, 30, 56))
    vgrad(s, 0, h * 0.72, (18, 22, 48), (70, 62, 80))
    s.rect(0, h * 0.72, w, h, fill=(70, 96, 62))
    s.rect(0, h * 0.72, w, h * 0.72 + 3, fill=(52, 74, 48))
    # missile with trail, falling
    for t in range(14):
        a = t / 13
        px, py = 40 + a * 70, 4 + a * 22
        s.ell(px - 2 - a, py - 2 - a, px + 2 + a, py + 2 + a, fill=(255, int(120 + 100 * a), 60))
    s.poly([(112, 26), (128, 34), (122, 38), (106, 30)], fill=(210, 214, 220))
    s.poly([(128, 34), (136, 40), (124, 38)], fill=(190, 40, 40))
    # flag
    s.rect(w - 56, 8, w - 14, 20, fill=(252, 252, 252))
    s.rect(w - 56, 20, w - 14, 32, fill=(220, 20, 60))
    s.line([(w - 56, 8), (w - 56, 40)], (200, 200, 200), 1.2)
    # crater
    s.ell(w - 70, h - 12, w - 24, h - 4, fill=(40, 40, 38))
    return s.out()


def ic_iraq(w, h):
    s = SD(w, h, (226, 204, 160))
    vgrad(s, 0, h, (232, 214, 176), (212, 186, 140))
    # flag
    s.rect(14, 8, 66, 18, fill=(206, 17, 38))
    s.rect(14, 18, 66, 28, fill=(252, 252, 252))
    s.rect(14, 28, 66, 38, fill=(20, 20, 20))
    s.line([(14, 8), (14, h - 4)], (80, 60, 30), 1.6)
    # tank
    tx = 102
    s.rect(tx, h - 22, tx + 62, h - 8, fill=(86, 92, 62))
    s.rect(tx + 14, h - 32, tx + 44, h - 22, fill=(96, 102, 70))
    s.rect(tx + 44, h - 29, tx + 76, h - 26, fill=(70, 76, 52))
    for k in range(5):
        s.ell(tx + 4 + k * 12, h - 14, tx + 14 + k * 12, h - 5, fill=(50, 54, 38))
    return s.out()


def ic_whitehouse(w, h):
    img = ill_whitehouse(w, 100)
    return img.crop((0, 100 - h, w, 100))


# ---------- page ----------
def sheared_text(page, cx, y, text, font, fill, shear=0.2):
    tw = int(font.getlength(text)) + 12
    th = int(font.size * 1.5)
    layer = Image.new("L", (tw * 2, th), 0)
    ImageDraw.Draw(layer).text((tw // 2 + 4, 2), text, font=font, fill=255)
    layer = layer.transform(layer.size, Image.AFFINE, (1, shear, -shear * th * 0.6, 0, 1, 0), Image.BICUBIC)
    page.paste(Image.new("RGB", layer.size, fill), (int(cx - layer.width / 2), y), layer)


LEADS = [
    ("1 • KYIV • WAR", "Russia hits Kyiv bridges in massive strikes",
     "Over 400 drones and 110 missiles, 27 of them ballistic, hit Ukraine; the PM counts 8 dead and 28 hurt, two of them in Lviv. (RTÉ)", ill_kyiv),
    ("2 • ODISHA • DISASTER", "Cyclone Akvan makes landfall near Gopalpur",
     "The storm crossed the coast around 8am with 70–80 km/h winds after 300,000+ were moved to shelters; no major damage reported. (Deccan Herald)", ill_cyclone),
    ("3 • TOKYO • MARKETS", "Nikkei tumbles as AI sell-off deepens",
     "Nikkei fell over 4%, Seoul's KOSPI 5.2% and Taiwan's TAIEX 6.2%; SoftBank dropped about 15% and Anthropic 9%. (Korea Times, Reuters)", ill_markets),
]

FEATS = [
    ("4 • ANTALYA • CLIMATE", "COP31 hits final day with no deal",
     "New draft drops fossil-fuel wording and the $120bn adaptation figure. (Climate Change News)", ic_cop),
    ("5 • MYANMAR • JUSTICE", "Myanmar, China reject ICJ genocide ruling",
     "Both call the Rohingya verdict “unfair”, a day after the court ruled. (Al Jazeera)", ic_scales),
    ("6 • BRUSSELS • EUROPE", "EU and UK agree Brexit reset package",
     "Brussels summit: food, youth scheme, carbon. (European Business Magazine)", ic_euuk),
    ("7 • TOKYO • ECONOMY", "Japan inflation rises to 2.3%",
     "October CPI up from 2.1%, core 2.2%; a BoJ hike looks likelier. (FXStreet)", ic_japan),
    ("8 • WELLINGTON • CRICKET", "Phillips hits 118 against India",
     "First Test: reportedly the first with centuries vs India in all three formats in a year. (Sportskeeda)", ic_cricket),
    ("9 • ROME • LABOUR", "Italy's biggest union strikes over 2027 budget",
     "CGIL rallies nationwide; leader Landini claims over a million marchers. (Bloomberg)", ic_italy),
    ("10 • TURKANA • ENERGY", "Kenya drills its first oil well",
     "Amosing-1 spudded in South Lokichar; first crude still due 1 December. (Mwakilishi)", ic_kenya),
    ("11 • POLAND • NATO", "Poland says Russian missile fell on its soil",
     "Warsaw reports a Kh-101 near Nowy Lipowiec; two airports paused flights. (France 24)", ic_poland),
    ("12 • JURF AL-SAKHAR • IRAQ", "Iraqi army enters militia stronghold",
     "Troops move in under a deal with Kataib Hezbollah, which is to withdraw. (The National)", ic_iraq),
    ("13 • WASHINGTON • POLITICS", "Trump defends Putin ties after Asia trip",
     "At a White House briefing he called his ties with Putin and Xi “fantastic”. (CBS News)", ic_whitehouse),
]

BRIEFS = [
    "Lviv Rail station strike kills two (RTÉ)",
    "Wall St S&P 500 falls into correction (Reuters)",
    "Nvidia Shares drop about 14% (Reuters)",
    "Anthropic Shares slide 9.1% in day two (Reuters)",
    "Taipei Taiex −6.2%, worst week since 1991 (24/7 Wall St)",
    "Tokyo SoftBank sinks about 15% (24/7 Wall St)",
    "Seoul Ruling party seeks chief justice's impeachment (Korea Herald)",
    "Beijing PBOC holds lending rates at 3.0%/3.5% (People's Daily)",
    "Barcelona Pancreatic pill shrinks tumours in 60.7% of patients in early trial (RTÉ)",
    "Jizan Coalition says it downed Houthi missile (Al Arabiya)",
    "Malawi Fuel queues deepen crisis (Al Jazeera)",
    "Las Vegas Russell fastest in wet F1 practice (Formula1.com)",
    "Shenzhen Xi hails “full turnaround” in Australia ties (Yahoo News)",
    "Hormuz Brent near $91, third weekly fall (RTÉ)",
    "Mukalla Armed skiff fires on cargo ship (Anadolu)",
    "Abuja Court bars Atiku's fresh Tinubu evidence (Leadership)",
    "Berlin Pupils join nationwide protest (Reuters)",
    "Odesa Strikes cut power in city and region (Kyiv Post)",
    "Warsaw Tusk calls Poland missile “provocation” (France 24)",
    "New York Nasdaq falls 5.3%, erasing 2026 gains (NPR)",
]

# region -> story numbers (1-33)
REGIONS = [
    ("EUROPE", (1, 6, 9, 11, 14, 22, 30, 31, 32), (34, 74, 140)),
    ("ASIA-PACIFIC", (2, 3, 5, 7, 18, 19, 20, 21, 26), (176, 54, 40)),
    ("MIDDLE EAST", (12, 23, 28), (150, 110, 30)),
    ("AFRICA", (10, 24, 29), (96, 70, 40)),
    ("AMERICAS", (13, 15, 16, 17, 25, 33), (40, 110, 80)),
    ("OCEANIA", (8,), (110, 70, 140)),
    ("GLOBAL", (4, 27), (70, 74, 84)),
]


def main(outdir):
    # sanity: every story 1..33 is in exactly one region
    allnums = sorted(n for _, ns, _ in REGIONS for n in ns)
    assert allnums == list(range(1, 34)), allnums
    assert len(LEADS) + len(FEATS) + len(BRIEFS) == 33
    assert [p[0] for p in PINS] == list(range(1, 34))

    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=3)
    d.rectangle([12, 12, W - 13, H - 13], outline=INK, width=1)
    L, R = 28, W - 28
    CW = R - L
    cx = W // 2

    # kicker
    kf = F(SANS_B, 11)
    d.text((L, 18), "THE WORLD IN ONE DAY", font=kf, fill=RED)
    rt = "FRIDAY'S NEWS • ONE PAGE • 33 STORIES"
    d.text((R - kf.getlength(rt), 18), rt, font=kf, fill=RED)
    d.line([L, 34, R, 34], fill=RULE, width=1)

    # masthead
    mf = F(SERIF_B, 42)
    assert mf.getlength("Friday 20 November 2026") <= CW - 20
    ctext(d, cx, 36, "Friday 20 November 2026", mf, INK)
    sf = "Russia's barrage hits Kyiv's bridges • Cyclone Akvan strikes Odisha • An AI sell-off sinks Asia's markets • COP31 reaches its final day with no deal"
    f_sf, lines, lh = fit_block(sf, SERIF, CW - 40, 1, 14, 10)
    y = 36 + 42 + 14
    for ln in lines:
        sheared_text(page, cx, y, ln, f_sf, RED)
        y += lh
    y += 2
    d.line([L, y, R, y], fill=RULE, width=2)
    d.line([L, y + 3, R, y + 3], fill=RULE, width=1)
    y += 8

    # by the numbers
    stats = [("3", "Dnipro bridges struck in Kyiv", INK), ("300,000+", "moved to shelters before Akvan", INK),
             ("−6.2%", "Taiwan's TAIEX on Friday", RED), ("−14%", "Nvidia on Wall Street", RED),
             ("2.3%", "Japan's October inflation", INK), ("118", "Phillips' runs against India", INK)]
    cw = CW / len(stats)
    nf = F(SERIF_B, 26)
    cf = F(SANS, 10)
    sy = y
    for i, (num, cap, col) in enumerate(stats):
        ccx = L + cw * i + cw / 2
        ctext(d, ccx, sy, num, nf, col)
        cl = wrap(cap, cf, cw - 14)
        assert len(cl) <= 2
        for j, c in enumerate(cl):
            ctext(d, ccx, sy + 32 + j * 12, c, cf, GREY)
        if i:
            d.line([L + cw * i, sy + 2, L + cw * i, sy + 56], fill=RULE, width=1)
    y = sy + 60
    d.line([L, y, R, y], fill=RULE, width=1)
    y += 6

    # region bar (widths: floor + share of stories)
    bh = 18
    rf = F(SANS_B, 10)
    base = 46
    unit = (CW - base * len(REGIONS)) / 33.0
    x = L
    for i, (name, ns, col) in enumerate(REGIONS):
        wseg = int(round(base + unit * len(ns)))
        if i == len(REGIONS) - 1:
            wseg = R - x
        d.rectangle([x, y, x + wseg - 1, y + bh], fill=col)
        lab = "%s %d" % (name, len(ns))
        lf = fit_line(lab, SANS_B, wseg - 8, 10, 7)
        d.text((x + wseg / 2, y + bh / 2 + 1), lab, font=lf, fill=(255, 255, 255), anchor="mm")
        if x > L:
            d.line([x, y, x, y + bh], fill=PAPER, width=2)
        x += wseg
    y += bh + 8

    # lead stories
    gap = 14
    colw = (CW - 2 * gap) // 3
    ih = 96
    ly = y
    lead_end = 0
    ty_max = 0
    for i, (kick, head, body, fn) in enumerate(LEADS):
        x0 = L + i * (colw + gap)
        res = fn(colw, ih)
        img, pts = res if isinstance(res, tuple) else (res, None)
        frame_panel(page, img, x0, ly)
        lf9 = F(SANS_B, 9)
        if i == 0:
            d.text((x0 + 6, ly + 5), "KYIV • OVERNIGHT", font=lf9, fill=(255, 214, 160))
        if i == 1:
            d.text((x0 + 6, ly + 5), "BAY OF BENGAL • FRI 8AM", font=lf9, fill=(255, 255, 255))
        if i == 2:
            for (px, py), name in ((pts[2], "TAIPEI"), (pts[5], "SEOUL"), (pts[8], "TOKYO")):
                d.text((x0 + px - 10, ly + max(3, py - 20)), name, font=lf9, fill=(255, 220, 210))
            d.text((x0 + 8, ly + ih - 16), "AI SELL-OFF", font=F(SANS_B, 10), fill=(255, 120, 110))
        ty = ly + ih + 6
        d.text((x0, ty), kick, font=F(SANS_B, 9), fill=RED)
        ty += 13
        hf, hl, hlh = fit_block(head, SERIF_B, colw, 2, 16, 13, 1.2)
        for ln in hl:
            d.text((x0, ty), ln, font=hf, fill=INK)
            ty += hlh
        ty += 2
        bf, bl, blh = fit_block(body, SERIF, colw, 4, 11, 9, 1.28)
        for ln in bl:
            d.text((x0, ty), ln, font=bf, fill=GREY)
            ty += blh
        ty_max = max(ty_max, ty)
    for i in range(2):
        xx = L + (i + 1) * (colw + gap) - gap // 2
        d.line([xx, ly, xx, ty_max], fill=RULE, width=1)
    y = ty_max + 3
    d.line([L, y, R, y], fill=RULE, width=2)
    y += 6

    # feature stories: two rows of five
    fgap = 10
    fw = (CW - 4 * fgap) // 5
    bnh = 46
    row_h = []
    for r in range(2):
        ry = y
        rmax = 0
        for c in range(5):
            kick, head, body, fn = FEATS[r * 5 + c]
            x0 = L + c * (fw + fgap)
            img = fn(fw, bnh)
            frame_panel(page, img, x0, ry)
            if r == 0 and c == 0:
                ctext(d, x0 + 150, ry + 17, "NO DEAL", F(SANS_B, 9), (170, 30, 30))
            if r == 0 and c == 3:
                ctext(d, x0 + 54, ry + 17, "2.3%", F(SANS_B, 10), (255, 255, 255))
            if r == 0 and c == 4:
                ctext(d, x0 + 150, ry + 8, "118", F(SANS_B, 12), (255, 255, 255))
            ty = ry + bnh + 4
            d.text((x0, ty), kick, font=fit_line(kick, SANS_B, fw, 8, 6), fill=RED)
            ty += 11
            hf, hl, hlh = fit_block(head, SERIF_B, fw, 3, 12, 10, 1.15)
            for ln in hl:
                d.text((x0, ty), ln, font=hf, fill=INK)
                ty += hlh
            ty += 1
            bf, bl, blh = fit_block(body, SERIF, fw, 5, 10, 9, 1.22)
            for ln in bl:
                d.text((x0, ty), ln, font=bf, fill=GREY)
                ty += blh
            rmax = max(rmax, ty)
        for c in range(1, 5):
            xx = L + c * (fw + fgap) - fgap // 2
            d.line([xx, ry, xx, rmax], fill=RULE, width=1)
        y = rmax + 3
        d.line([L, y, R, y], fill=RULE, width=2 if r == 1 else 1)
        y += 6

    # bottom: map + date check (left), briefs (right)
    mw, mh = 322, 119
    d.text((L, y), "WHERE IT HAPPENED", font=F(SANS_B, 10), fill=RED)
    bx = L + mw + 14
    bw = R - bx
    d.text((bx, y), "ALSO ON FRIDAY 20 NOVEMBER — 20 MORE STORIES", font=F(SANS_B, 10), fill=RED)
    y0 = y + 14
    draw_map(page, L, y0, mw, mh)
    capf = F(SERIF, 10)
    d.text((L, y0 + mh + 3), "Numbers mark all 33 stories; positions approximate.", font=capf, fill=GREY)

    # briefs: two columns, 10 each, hanging indent, 12px
    colb = (bw - 12) // 2
    bsize = 12
    bf = F(SANS, bsize)
    indent = 20
    items = [(str(14 + k), wrap(t, bf, colb - indent)) for k, t in enumerate(BRIEFS)]
    lhb = bsize + 2
    cols = [items[:10], items[10:]]
    brief_bottom = 0
    for ci, col in enumerate(cols):
        yy = y0
        xx = bx + ci * (colb + 12)
        for num, ls in col:
            d.text((xx, yy), num, font=F(SANS_B, bsize), fill=RED)
            for ln in ls:
                d.text((xx + indent, yy), ln, font=bf, fill=INK)
                yy += lhb
            yy += 1
        brief_bottom = max(brief_bottom, yy)
    d.line([bx + colb + 6, y0, bx + colb + 6, brief_bottom], fill=RULE, width=1)

    dc = ("DATE CHECK — First reported Thursday 19 Nov, so NOT shown as Friday's news: Bukele's third-term filing "
          "• Anthropic's IPO debut (+17%) • the ICJ's Rohingya genocide verdict itself • GTA VI's midnight launch • the Trump–Xi–Putin Shenzhen summit itself.")
    dcf, dcl, dclh = fit_block(dc, SANS, mw - 16, 9, 11, 8, 1.3)
    boxh = len(dcl) * dclh + 8
    ty = y0 + mh + 18
    d.rectangle([L, ty, L + mw, ty + boxh], fill=(251, 236, 228), outline=RED, width=2)
    yy = ty + 5
    for ln in dcl:
        if ln.startswith("DATE CHECK"):
            bfnt = F(SANS_B, dcf.size)
            d.text((L + 8, yy), "DATE CHECK", font=bfnt, fill=RED)
            d.text((L + 8 + bfnt.getlength("DATE CHECK"), yy), ln[len("DATE CHECK"):], font=dcf, fill=INK)
        else:
            d.text((L + 8, yy), ln, font=dcf, fill=INK)
        yy += dclh
    y = max(ty + boxh, brief_bottom) + 6
    print("briefs font", bsize, "brief_bottom", brief_bottom, "datebox", ty, ty + boxh, "dc font", dcf.size)

    # footer
    d.line([L, y, R, y], fill=RULE, width=2)
    y += 5
    src = ("Sources: Al Jazeera, ABC News (AU), RTE, Moscow Times, Reuters, CNN, European Business Magazine, Deccan Herald, IMD, Korea Times, "
           "24/7 Wall St, Climate Change News, Agence Europe, FXStreet, Statistics Bureau of Japan, Sportskeeda, Bloomberg, Mwakilishi, France 24, Kyiv Post, "
           "The National, CBS News, Globe and Mail, Korea Herald, People's Daily, Al Arabiya, Formula1.com, Yahoo News, Anadolu, Leadership, NPR")
    sfnt, sl, slh = fit_block(src, SANS, CW, 2, 9, 7, 1.25)
    for ln in sl:
        ctext(d, cx, y, ln, sfnt, GREY)
        y += slh
    y += 2
    ev = "Every story here happened, or was first reported, on Friday 20 November 2026."
    efnt = fit_line(ev, SERIF_B, CW, 12, 8)
    ctext(d, cx, y, ev, efnt, INK)
    y += 16
    print("content ends at y=", y)
    assert y <= H - 14, y

    os.makedirs(outdir, exist_ok=True)
    page.save(os.path.join(outdir, "entry.png"), optimize=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
