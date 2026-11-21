"""make.fun news poster, Friday 20 November 2026: a modern data broadsheet (1024x1024).

Round 3 design: pure white page, ink-black grotesque sans, signal-red accents, thin black rules.
Pure PIL drawing, no external images, no network, no randomness, no timestamps.
Usage: python3 draw.py [output_dir]   (default: directory of this file)
Writes <output_dir>/entry.png
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FL = "/usr/share/fonts/truetype/liberation/"
SANS_B = FL + "LiberationSans-Bold.ttf"
SANS = FL + "LiberationSans-Regular.ttf"
if not os.path.exists(SANS_B):
    SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (255, 255, 255)
INK = (10, 10, 10)
RED = (217, 35, 15)
GREY = (52, 52, 52)
RULE = (10, 10, 10)
SEA = (226, 232, 240)
LAND = (196, 200, 208)

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
        self.im = Image.new("RGB", (int(w * K), int(h * K)), bg)
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon(self._p(pts), fill=fill, outline=outline, width=int(width * K))

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=outline, width=int(width * K))

    def ell(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=outline, width=int(width * K))

    def line(self, pts, fill, width=1):
        self.d.line(self._p(pts), fill=fill, width=max(1, int(width * K)), joint="curve")

    def pie(self, box, a0, a1, fill):
        self.d.pieslice([v * K for v in box], a0, a1, fill=fill)

    def out(self):
        return self.im.resize((int(self.w), int(self.h)), Image.LANCZOS)


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


def lit_windows(s, bx, top, bw, bot, seed, col=(240, 190, 90)):
    for wy in range(int(top + 5), int(bot - 4), 8):
        for wx in range(int(bx + 3), int(bx + bw - 4), 6):
            if (wx * 3 + wy * seed) % 5 < 2:
                s.rect(wx, wy, wx + 2.4, wy + 3.4, fill=col)


def person(s, x, yb, ph, col, skin=(226, 192, 162)):
    s.ell(x - ph * 0.17, yb - ph, x + ph * 0.17, yb - ph * 0.66, fill=skin)
    s.rect(x - ph * 0.22, yb - ph * 0.66, x + ph * 0.22, yb, fill=col)


def eu_flag(s, x, y, w, h):
    s.rect(x, y, x + w, y + h, fill=(0, 51, 153))
    for i in range(12):
        a = math.radians(i * 30)
        s.poly(star(x + w / 2 + h * 0.34 * math.cos(a), y + h / 2 + h * 0.34 * math.sin(a), max(1.6, h * 0.07)), fill=(255, 204, 0))


def uk_flag(s, x, y, w, h):
    s.rect(x, y, x + w, y + h, fill=(1, 33, 105))
    for wd, col in ((h * 0.19, (255, 255, 255)), (h * 0.09, (200, 16, 46))):
        s.line([(x, y), (x + w, y + h)], col, wd)
        s.line([(x + w, y), (x, y + h)], col, wd)
    s.rect(x, y + h / 2 - h * 0.16, x + w, y + h / 2 + h * 0.16, fill=(255, 255, 255))
    s.rect(x + w / 2 - h * 0.16, y, x + w / 2 + h * 0.16, y + h, fill=(255, 255, 255))
    s.rect(x, y + h / 2 - h * 0.09, x + w, y + h / 2 + h * 0.09, fill=(200, 16, 46))
    s.rect(x + w / 2 - h * 0.09, y, x + w / 2 + h * 0.09, y + h, fill=(200, 16, 46))


def pole_flag(s, x, ytop, ybot, fw, fh, stripes, vertical=False):
    s.line([(x, ytop - 2), (x, ybot)], (70, 70, 76), 1.4)
    n = len(stripes)
    for i, c in enumerate(stripes):
        if vertical:
            s.rect(x + i * fw / n, ytop, x + (i + 1) * fw / n, ytop + fh, fill=c)
        else:
            s.rect(x, ytop + i * fh / n, x + fw, ytop + (i + 1) * fh / n, fill=c)


def frame_panel(page, img, x, y, num):
    page.paste(img, (x, y))
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + img.width - 1, y + img.height - 1], outline=INK, width=2)
    nf = F(SANS_B, 11)
    bw = int(nf.getlength(str(num))) + 9
    d.rectangle([x, y, x + bw, y + 15], fill=RED)
    d.text((x + bw / 2 + 0.5, y + 8), str(num), font=nf, fill=(255, 255, 255), anchor="mm")


# ---------- LEAD illustrations (about 322 x 120) ----------
def ill_kyiv(w, h):
    s = SD(w, h, (14, 20, 44))
    hor = h * 0.70
    vgrad(s, 0, hor, (10, 14, 38), (150, 62, 36))
    for i in range(34):
        sx = (i * 97) % w
        sy = (i * 53) % int(h * 0.42)
        s.ell(sx, sy, sx + 1.4, sy + 1.4, fill=(230, 225, 200))
    s.rect(0, hor, w, h, fill=(26, 32, 60))
    for i in range(12):  # river sheen
        s.rect(10 + i * 27, hor + 12 + (i * 7) % 18, 26 + i * 27, hor + 13.4 + (i * 7) % 18, fill=(52, 62, 100))
    bl = [(0, 44, 22), (22, 66, 26), (48, 36, 20), (68, 56, 24), (92, 82, 18), (110, 46, 30), (148, 60, 26), (176, 42, 22),
          (260, 52, 24), (284, 38, 20), (304, 60, 18)]
    for bx, bh, bw in bl:
        s.rect(bx, hor - bh, bx + bw, hor, fill=(18, 16, 30))
        lit_windows(s, bx, hor - bh, bw, hor, 1)
    cx = 226  # golden-domed church
    s.rect(cx - 16, hor - 38, cx + 16, hor, fill=(30, 22, 36))
    s.rect(cx - 8, hor - 52, cx + 8, hor - 38, fill=(30, 22, 36))
    for dx, top in ((-12, 62), (0, 72), (12, 62)):
        s.pie([cx + dx - 6, hor - top, cx + dx + 6, hor - top + 12], 180, 360, (232, 178, 56))
        s.line([(cx + dx, hor - top), (cx + dx, hor - top - 6)], (232, 178, 56), 1)
    # bridge: pylon + cables + arches
    by = hor + 3
    s.rect(0, by, w, by + 5, fill=(8, 8, 14))
    for i in range(0, int(w), 52):
        s.pie([i - 2, by - 2, i + 50, by + 40], 180, 360, (8, 8, 14))
        s.pie([i + 4, by + 3, i + 44, by + 34], 180, 360, (26, 32, 60))
    px = 70
    s.rect(px - 2, by - 62, px + 2, by, fill=(8, 8, 14))
    for k in range(1, 8):
        s.line([(px, by - 62 + k * 3), (px - k * 8.5, by)], (8, 8, 14), 0.8)
        s.line([(px, by - 62 + k * 3), (px + k * 8.5, by)], (8, 8, 14), 0.8)
    # burning section
    for fx, fh in ((150, 32), (160, 46), (170, 30), (180, 38), (190, 24), (200, 18)):
        s.poly([(fx - 6, by + 2), (fx, by + 2 - fh), (fx + 6, by + 2)], fill=(255, 120, 20))
        s.poly([(fx - 3, by + 2), (fx, by + 2 - fh * 0.6), (fx + 3, by + 2)], fill=(255, 224, 96))
    for i in range(7):
        s.rect(146 + i * 8, by + 9 + i * 4, 160 + i * 8, by + 12 + i * 4, fill=(200, 96, 30))
    for x0, y0, x1, y1 in ((40, 4, 118, 80), (130, 0, 168, 70), (215, 6, 188, 82), (276, 2, 236, 62)):
        for t in range(0, 18):
            a = t / 17
            qx, qy = x0 + (x1 - x0) * a, y0 + (y1 - y0) * a
            c = (255, int(110 + 120 * a), int(50 + 90 * a))
            s.ell(qx - 1.6 - 1.4 * a, qy - 1.6 - 1.4 * a, qx + 1.6 + 1.4 * a, qy + 1.6 + 1.4 * a, fill=c)
        s.ell(x1 - 4, y1 - 4, x1 + 4, y1 + 4, fill=(255, 250, 200))
    return s.out()


def ill_cyclone(w, h):
    s = SD(w, h, (60, 70, 92))
    vgrad(s, 0, h, (44, 52, 78), (128, 146, 168))
    ex, ey = w * 0.50, h * 0.42
    for arm in range(5):
        for i in range(52):
            t = i / 51
            a = math.radians(arm * 72 + t * 260)
            rr = 12 + t * 88
            qx, qy = ex + rr * math.cos(a), ey + rr * math.sin(a) * 0.58
            sz = 3 + 10 * (1 - t)
            c = int(238 - 44 * t)
            s.ell(qx - sz, qy - sz * 0.6, qx + sz, qy + sz * 0.6, fill=(c, c, min(255, c + 8)))
    s.ell(ex - 9, ey - 6, ex + 9, ey + 6, fill=(40, 50, 74))
    # sea + waves
    s.rect(0, h * 0.78, w, h, fill=(46, 88, 124))
    for k in range(10):
        wx = 8 + k * 32
        s.line([(wx, h * 0.86), (wx + 8, h * 0.83), (wx + 16, h * 0.86)], (190, 214, 232), 1.2)
    # coast + shelters + palms
    s.poly([(w * 0.58, h), (w * 0.64, h * 0.84), (w * 0.82, h * 0.78), (w, h * 0.72), (w, h)], fill=(72, 112, 74))
    s.line([(w * 0.64, h * 0.84), (w * 0.82, h * 0.78), (w, h * 0.72)], (232, 232, 222), 1.6)
    for k, (bx, by_) in enumerate(((0.72, 0.88), (0.80, 0.84), (0.88, 0.80))):
        x0, y0 = w * bx, h * by_
        s.rect(x0, y0 - 9, x0 + 15, y0 + 4, fill=(236, 236, 230), outline=(80, 80, 90), width=1)
        s.poly([(x0 - 2, y0 - 9), (x0 + 7.5, y0 - 15), (x0 + 17, y0 - 9)], fill=(190, 40, 36))
        s.rect(x0 + 5, y0 - 3, x0 + 10, y0 + 4, fill=(60, 70, 90))
    for k in range(6):
        qx = w * 0.62 + k * 17
        qy = h * (0.96 - 0.01 * k)
        s.line([(qx, qy), (qx - 3, qy - 17)], (30, 58, 34), 1.6)
        for ang in (-150, -120, -60, -30):
            a = math.radians(ang)
            s.line([(qx - 3, qy - 17), (qx - 3 + 11 * math.cos(a), qy - 17 + 8 * math.sin(a) + 3)], (40, 96, 46), 1.5)
    # evacuees queue
    for k in range(9):
        person(s, w * 0.07 + k * 8, h * 0.97, 15, ((226, 90, 50), (240, 240, 240), (60, 120, 200))[k % 3])
    return s.out()


def ill_markets(w, h):
    s = SD(w, h, (20, 22, 30))
    for gy in range(14, int(h), 24):
        s.line([(0, gy), (w, gy)], (46, 50, 64), 0.8)
    for gx in range(20, int(w), 40):
        s.line([(gx, 0), (gx, h)], (38, 42, 56), 0.8)
    pts = [(8, 20), (34, 28), (58, 22), (84, 46), (110, 42), (138, 70), (166, 62), (196, 92), (226, 86), (262, 112), (306, 118)]
    pts = [(px, py * h / 130.0) for px, py in pts]
    s.poly(pts + [(w, h), (8, h)], fill=(70, 24, 30))
    # volume bars
    for i in range(26):
        bh = 6 + (i * 37) % 22
        s.rect(6 + i * 12, h - bh, 12 + i * 12, h, fill=(90, 36, 42))
    for px, py in pts[:-1]:
        c = (214, 54, 54)
        s.line([(px, py - 10), (px, py + 22)], c, 1.2)
        s.rect(px - 4, py, px + 4, py + 14, fill=c)
    s.line(pts, (255, 96, 86), 3)
    s.ell(pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5, fill=(255, 130, 120))
    s.poly([(w - 34, h * 0.18), (w - 10, h * 0.18), (w - 22, h * 0.36)], fill=(255, 96, 86))
    return s.out(), pts


# ---------- FEATURE illustrations (about 188 x 76) ----------
def ic_cop(w, h):
    s = SD(w, h, (170, 214, 226))
    vgrad(s, 0, h, (150, 204, 226), (232, 244, 238))
    s.poly([(0, h * 0.7), (w * 0.18, h * 0.38), (w * 0.34, h * 0.6), (w * 0.5, h * 0.3), (w * 0.7, h * 0.7)], fill=(96, 138, 150))
    s.poly([(w * 0.5, h * 0.3), (w * 0.46, h * 0.4), (w * 0.52, h * 0.38), (w * 0.55, h * 0.42)], fill=(240, 246, 248))
    s.rect(0, h * 0.7, w, h, fill=(38, 112, 170))  # Mediterranean
    for k in range(6):
        s.line([(10 + k * 30, h * 0.8), (18 + k * 30, h * 0.77), (26 + k * 30, h * 0.8)], (180, 214, 236), 1.1)
    # conference hall
    s.rect(16, h * 0.52, 92, h * 0.76, fill=(236, 238, 240), outline=(80, 84, 92), width=1)
    s.pie([26, h * 0.34, 82, h * 0.7], 180, 360, (210, 224, 232))
    for k in range(7):
        s.line([(30 + k * 8, h * 0.52), (30 + k * 8, h * 0.76)], (120, 130, 140), 0.8)
    for k, c in enumerate(((200, 16, 46), (0, 51, 153), (0, 130, 60), (250, 200, 0), (30, 30, 30))):  # flags
        pole_flag(s, 22 + k * 14, h * 0.24 + (k % 2) * 3, h * 0.52, 10, 7, [c])
    # globe + thermometer
    cx, cy, r = w - 56, h * 0.46, 22
    s.ell(cx - r, cy - r, cx + r, cy + r, fill=(40, 104, 170))
    s.poly([(cx - 14, cy - 12), (cx - 2, cy - 18), (cx + 6, cy - 6), (cx - 4, cy + 4), (cx - 14, cy - 2)], fill=(70, 160, 90))
    s.poly([(cx + 6, cy + 6), (cx + 16, cy), (cx + 14, cy + 14), (cx + 6, cy + 14)], fill=(70, 160, 90))
    s.ell(cx - r, cy - r, cx + r, cy + r, outline=(20, 50, 90), width=1.2)
    tx = w - 16
    s.rect(tx - 4, 10, tx + 4, h - 16, fill=(250, 250, 250), outline=(90, 90, 96), width=1)
    s.rect(tx - 2, 24, tx + 2, h - 14, fill=(200, 30, 30))
    s.ell(tx - 8, h - 20, tx + 8, h - 4, fill=(200, 30, 30), outline=(90, 90, 96), width=1)
    return s.out()


def ic_scales(w, h):
    s = SD(w, h, (214, 224, 232))
    vgrad(s, 0, h, (232, 238, 244), (178, 194, 208))
    bx0, bx1 = w * 0.30, w * 0.70
    s.rect(bx0 - 6, h - 10, bx1 + 6, h, fill=(120, 124, 132))
    s.rect(bx0 - 3, h - 15, bx1 + 3, h - 10, fill=(150, 154, 160))
    s.poly([(bx0 - 4, 30), ((bx0 + bx1) / 2, 12), (bx1 + 4, 30)], fill=(240, 236, 228), outline=(90, 90, 96), width=1.4)
    s.rect(bx0 - 2, 30, bx1 + 2, 35, fill=(226, 222, 212), outline=(90, 90, 96), width=1)
    n = 6
    for i in range(n):
        cx = bx0 + 6 + i * (bx1 - bx0 - 12) / (n - 1)
        s.rect(cx - 3.5, 35, cx + 3.5, h - 15, fill=(240, 236, 228), outline=(120, 120, 126), width=1)
    cxm = (bx0 + bx1) / 2
    s.ell(cxm - 4, 20, cxm + 4, 28, fill=(176, 150, 70))
    # Myanmar flag (left)
    fx, fy = 14, 16
    pole_flag(s, fx, fy, h - 4, 40, 26, [(254, 203, 0), (52, 177, 102), (234, 40, 57)])
    s.poly(star(fx + 20, fy + 13, 7.5), fill=(255, 255, 255))
    # China flag (right)
    gx = w - 54
    s.line([(gx, 14), (gx, h - 4)], (70, 70, 76), 1.4)
    s.rect(gx, fy, gx + 40, fy + 26, fill=(222, 41, 16))
    s.poly(star(gx + 8, fy + 8, 5.4), fill=(255, 222, 0))
    for sx, sy in ((16, 4), (20, 8), (20, 13), (16, 17)):
        s.poly(star(gx + sx, fy + sy, 1.8), fill=(255, 222, 0))
    # gavel
    s.rect(w * 0.43, h - 20, w * 0.57, h - 16, fill=(120, 84, 40))
    return s.out()


def ic_euuk(w, h):
    s = SD(w, h, (226, 234, 242))
    vgrad(s, 0, h, (210, 224, 240), (180, 196, 214))
    # Brussels skyline: glass HQ + Atomium
    s.rect(w * 0.36, h * 0.40, w * 0.64, h, fill=(120, 140, 166))
    for gx in range(int(w * 0.36) + 3, int(w * 0.64) - 3, 7):
        s.line([(gx, h * 0.42), (gx, h)], (176, 196, 220), 0.8)
    for gy in range(int(h * 0.46), int(h), 9):
        s.line([(w * 0.36, gy), (w * 0.64, gy)], (176, 196, 220), 0.8)
    s.rect(w * 0.64, h * 0.62, w * 0.76, h, fill=(104, 122, 146))
    for k, (ax, ay) in enumerate(((0.86, 0.30), (0.80, 0.52), (0.92, 0.52), (0.86, 0.70))):
        s.ell(w * ax - 5, h * ay - 5, w * ax + 5, h * ay + 5, fill=(186, 192, 202), outline=(100, 106, 116), width=1)
    s.line([(w * 0.86, h * 0.30), (w * 0.86, h * 0.70)], (120, 126, 136), 1.4)
    s.line([(w * 0.80, h * 0.52), (w * 0.92, h * 0.52)], (120, 126, 136), 1.4)
    # flags on poles
    s.line([(14, 10), (14, h - 4)], (70, 70, 76), 1.4)
    eu_flag(s, 14, 10, 46, 30)
    s.line([(w * 0.76 + 6, 10), (w * 0.76 + 6, h - 4)], (70, 70, 76), 1.4)
    uk_flag(s, w * 0.76 + 6 - 46, 4, 46, 28)
    # deal handshake badge
    s.ell(w / 2 - 12, h - 24, w / 2 + 12, h, fill=(255, 255, 255), outline=(60, 60, 70), width=1.2)
    s.line([(w / 2 - 7, h - 11), (w / 2 + 7, h - 11)], (60, 60, 70), 2)
    s.line([(w / 2 - 3, h - 15), (w / 2 + 3, h - 7)], (60, 60, 70), 1.4)
    return s.out()


def ic_japan(w, h):
    s = SD(w, h, (250, 244, 244))
    vgrad(s, 0, h, (255, 255, 255), (226, 232, 244))
    s.ell(w * 0.34, h * 0.14, w * 0.34 + 36, h * 0.14 + 36, fill=(200, 0, 40))  # rising sun
    s.poly([(w * 0.18, h * 0.82), (w * 0.44, h * 0.30), (w * 0.52, h * 0.30), (w * 0.78, h * 0.82)], fill=(104, 124, 168))  # Fuji
    s.poly([(w * 0.44, h * 0.30), (w * 0.42, h * 0.40), (w * 0.455, h * 0.37), (w * 0.48, h * 0.42), (w * 0.505, h * 0.37), (w * 0.53, h * 0.40), (w * 0.52, h * 0.30)], fill=(248, 250, 255))
    # Tokyo Tower
    tx = w * 0.84
    s.poly([(tx - 9, h), (tx, h * 0.08), (tx + 9, h)], fill=(214, 40, 24))
    for k in range(1, 6):
        yy = h * 0.08 + k * (h * 0.92) / 6
        hw = 9 * (yy - h * 0.08) / (h * 0.92)
        s.rect(tx - hw, yy, tx + hw, yy + 2.4, fill=(255, 255, 255))
    s.line([(tx, h * 0.08), (tx, h * 0.0)], (60, 60, 60), 1.2)
    # skyline
    for k, (bx, bh, bw) in enumerate(((52, 22, 14), (66, 32, 12), (78, 20, 16), (94, 28, 12), (106, 18, 14), (120, 34, 12), (132, 22, 14), (146, 16, 12))):
        s.rect(bx, h - bh, bx + bw, h, fill=(64, 70, 90))
        lit_windows(s, bx, h - bh, bw, h, 2, (230, 220, 160))
    # rising CPI bars (bottom left) + tag
    for i in range(5):
        bh = 8 + i * 6
        s.rect(8 + i * 9, h - 4 - bh, 15 + i * 9, h - 4, fill=(200, 0, 40) if i > 2 else (110, 114, 124))
    s.line([(8, h - 8), (52, h - 40)], (10, 10, 10), 1.4)
    return s.out()


def ic_cricket(w, h):
    s = SD(w, h, (140, 190, 232))
    vgrad(s, 0, h, (122, 178, 230), (214, 232, 246))
    # stands with crowd
    s.rect(0, h * 0.30, w, h * 0.58, fill=(70, 74, 92))
    cols = ((226, 70, 60), (240, 240, 240), (60, 110, 200), (250, 200, 60), (30, 30, 36))
    for r in range(3):
        for k in range(46):
            s.ell(2 + k * 4.1, h * 0.33 + r * 6, 5 + k * 4.1, h * 0.33 + r * 6 + 3, fill=cols[(k * 3 + r * 2) % 5])
    for tx in (14, w - 14):  # floodlights
        s.line([(tx, h * 0.3), (tx, 4)], (80, 80, 90), 1.6)
        s.rect(tx - 7, 2, tx + 7, 9, fill=(250, 250, 220), outline=(80, 80, 90), width=1)
    s.rect(0, h * 0.58, w, h, fill=(78, 152, 70))
    for k in range(0, int(w), 24):
        s.rect(k, h * 0.58, k + 12, h, fill=(88, 164, 78))
    s.rect(w * 0.22, h * 0.82, w * 0.78, h * 0.9, fill=(212, 196, 150))  # pitch
    for k in range(3):  # stumps
        s.rect(w * 0.70 + k * 4, h * 0.60, w * 0.70 + k * 4 + 1.6, h * 0.84, fill=(246, 238, 206))
    # batter (NZ black) with bat
    person(s, w * 0.52, h * 0.92, 36, (24, 24, 28))
    s.poly([(w * 0.55, h * 0.74), (w * 0.57, h * 0.72), (w * 0.64, h * 0.92), (w * 0.62, h * 0.94)], fill=(224, 182, 110), outline=(120, 80, 30), width=1)
    s.ell(w * 0.34, h * 0.60, w * 0.34 + 6, h * 0.60 + 6, fill=(200, 30, 40))
    # scoreboard
    s.rect(w - 52, h * 0.6, w - 8, h * 0.8, fill=(20, 22, 26), outline=(200, 200, 200), width=1)
    return s.out()


def ic_italy(w, h):
    s = SD(w, h, (236, 240, 246))
    vgrad(s, 0, h, (190, 214, 240), (240, 244, 248))
    # Colosseum
    s.rect(w * 0.30, h * 0.14, w * 0.96, h * 0.80, fill=(212, 206, 204))
    for row in range(3):
        for k in range(10):
            ax = w * 0.32 + k * (w * 0.62) / 10
            ay = h * 0.18 + row * h * 0.19
            s.rect(ax, ay + 4, ax + 8, ay + h * 0.15, fill=(96, 88, 92))
            s.pie([ax, ay, ax + 8, ay + 8], 180, 360, (96, 88, 92))
        s.line([(w * 0.30, h * 0.14 + (row + 1) * h * 0.19 - 2), (w * 0.96, h * 0.14 + (row + 1) * h * 0.19 - 2)], (170, 164, 164), 1.2)
    # tricolore + CGIL banner + crowd
    pole_flag(s, 12, 8, h, 28, 18, [(0, 146, 70), (252, 252, 252), (206, 43, 55)], vertical=True)
    s.line([(w * 0.34, h * 0.52), (w * 0.34, h)], (80, 60, 40), 1.6)
    s.rect(w * 0.34, h * 0.52, w * 0.34 + 54, h * 0.52 + 16, fill=(206, 43, 55))
    for k in range(26):
        px = 6 + k * 7.2
        col = ((60, 70, 100), (100, 60, 60), (50, 90, 80), (30, 30, 36))[k % 4]
        person(s, px, h - 1, 20 + (k * 5) % 6, col)
    for k in (3, 9, 15, 21):
        s.line([(6 + k * 7.2, h - 14), (6 + k * 7.2, h - 34)], (80, 60, 40), 1.2)
        s.rect(6 + k * 7.2, h - 34, 6 + k * 7.2 + 8, h - 28, fill=((0, 146, 70), (206, 43, 55))[k % 2])
    return s.out()


def ic_kenya(w, h):
    s = SD(w, h, (250, 190, 120))
    vgrad(s, 0, h, (244, 164, 104), (252, 232, 178))
    s.ell(w * 0.66 - 14, h * 0.50 - 14, w * 0.66 + 14, h * 0.50 + 14, fill=(255, 244, 200))
    s.poly([(0, h * 0.74), (w * 0.2, h * 0.58), (w * 0.4, h * 0.72), (w * 0.62, h * 0.56), (w, h * 0.72), (w, h), (0, h)], fill=(176, 120, 84))
    s.rect(0, h * 0.78, w, h, fill=(196, 152, 98))
    # derrick
    cx = w * 0.42
    s.poly([(cx - 17, h * 0.9), (cx, h * 0.1), (cx + 17, h * 0.9)], outline=(44, 36, 32), width=1.8)
    for k in range(1, 7):
        yy = h * 0.1 + k * h * 0.8 / 7
        hw = 17 * (yy - h * 0.1) / (h * 0.8)
        s.line([(cx - hw, yy), (cx + hw, yy - 5)], (44, 36, 32), 1)
        s.line([(cx + hw, yy), (cx - hw, yy - 5)], (44, 36, 32), 1)
    s.rect(cx - 5, h * 0.06, cx + 5, h * 0.12, fill=(44, 36, 32))
    s.line([(cx, h * 0.12), (cx, h * 0.9)], (44, 36, 32), 1.4)
    s.rect(cx - 24, h * 0.84, cx + 26, h * 0.92, fill=(60, 54, 48))
    # barrels + flag + acacia
    for k in range(3):
        s.rect(w * 0.68 + k * 12, h * 0.78, w * 0.68 + k * 12 + 10, h * 0.94, fill=(30, 30, 34), outline=(180, 40, 30), width=1)
    pole_flag(s, w - 30, 14, h * 0.8, 24, 16, [(20, 20, 20), (200, 30, 36), (0, 120, 56)])
    s.line([(14, h), (16, h * 0.62)], (50, 36, 26), 1.8)
    s.ell(2, h * 0.5, 32, h * 0.64, fill=(60, 84, 40))
    return s.out()


def ic_poland(w, h):
    s = SD(w, h, (24, 30, 56))
    vgrad(s, 0, h * 0.72, (14, 18, 44), (82, 66, 84))
    for i in range(14):
        s.ell((i * 71) % w, (i * 29) % (h * 0.4), (i * 71) % w + 1.2, (i * 29) % (h * 0.4) + 1.2, fill=(230, 225, 205))
    s.rect(0, h * 0.72, w, h, fill=(66, 94, 60))
    for k in range(0, int(w), 14):
        s.line([(k, h * 0.76), (k + 8, h)], (52, 78, 48), 1)
    # missile and trail
    for t in range(18):
        a = t / 17
        qx, qy = 24 + a * 80, 6 + a * 26
        s.ell(qx - 2 - a * 1.6, qy - 2 - a * 1.6, qx + 2 + a * 1.6, qy + 2 + a * 1.6, fill=(255, int(110 + 110 * a), 60))
    s.poly([(106, 28), (128, 40), (122, 46), (100, 34)], fill=(214, 218, 224))
    s.poly([(128, 40), (138, 48), (123, 45)], fill=(190, 40, 40))
    # farmhouse + crater glow
    s.rect(w * 0.55, h * 0.58, w * 0.55 + 28, h * 0.74, fill=(150, 130, 120))
    s.poly([(w * 0.55 - 3, h * 0.58), (w * 0.55 + 14, h * 0.44), (w * 0.55 + 31, h * 0.58)], fill=(120, 50, 42))
    s.rect(w * 0.55 + 18, h * 0.62, w * 0.55 + 23, h * 0.68, fill=(240, 190, 90))
    s.ell(w * 0.50, h * 0.84, w * 0.50 + 40, h * 0.94, fill=(40, 36, 34))
    s.ell(w * 0.50 + 12, h * 0.86, w * 0.50 + 28, h * 0.92, fill=(255, 140, 40))
    # airport tower + plane
    s.rect(w * 0.84, h * 0.46, w * 0.84 + 7, h * 0.80, fill=(150, 156, 168))
    s.rect(w * 0.84 - 5, h * 0.36, w * 0.84 + 12, h * 0.46, fill=(190, 200, 214))
    s.ell(w * 0.84 + 3, h * 0.30, w * 0.84 + 9, h * 0.36, fill=(230, 40, 40))
    s.rect(w * 0.70, h * 0.76, w * 0.80, h * 0.82, fill=(236, 238, 242))
    s.poly([(w * 0.74, h * 0.78), (w * 0.72, h * 0.66), (w * 0.76, h * 0.78)], fill=(200, 204, 212))
    pole_flag(s, 14, 20, h * 0.8, 26, 8, [(252, 252, 252), (220, 20, 60)])
    return s.out()


def ic_iraq(w, h):
    s = SD(w, h, (226, 204, 160))
    vgrad(s, 0, h, (238, 222, 190), (214, 190, 148))
    # mud-brick compound with walls + gate
    s.rect(w * 0.52, h * 0.38, w * 0.98, h * 0.82, fill=(196, 168, 128))
    for k in range(7):
        s.rect(w * 0.52 + k * 12, h * 0.32, w * 0.52 + k * 12 + 7, h * 0.38, fill=(196, 168, 128))
    s.rect(w * 0.70, h * 0.52, w * 0.82, h * 0.82, fill=(70, 56, 44))
    s.pie([w * 0.70, h * 0.44, w * 0.82, h * 0.6], 180, 360, (70, 56, 44))
    for k in range(3):
        s.rect(w * 0.56 + k * 7, h * 0.50, w * 0.56 + k * 7 + 3, h * 0.58, fill=(80, 64, 50))
    # palms
    for px in (w * 0.46, w * 0.99):
        s.line([(px, h * 0.84), (px - 2, h * 0.46)], (70, 52, 34), 2)
        for ang in (-160, -130, -100, -50, -20):
            a = math.radians(ang)
            s.line([(px - 2, h * 0.46), (px - 2 + 13 * math.cos(a), h * 0.46 + 9 * math.sin(a) + 3)], (60, 110, 56), 1.6)
    s.rect(0, h * 0.82, w, h, fill=(206, 178, 132))
    # Iraqi flag
    pole_flag(s, 14, 12, h * 0.84, 34, 21, [(206, 17, 38), (252, 252, 252), (20, 20, 20)])
    # tanks column
    for tx in (w * 0.04, w * 0.28):
        yb = h * 0.96
        s.rect(tx, yb - 15, tx + 52, yb - 4, fill=(86, 92, 62))
        s.rect(tx + 12, yb - 24, tx + 36, yb - 15, fill=(98, 104, 72))
        s.rect(tx + 36, yb - 22, tx + 66, yb - 19, fill=(70, 76, 52))
        for k in range(5):
            s.ell(tx + 3 + k * 9.6, yb - 10, tx + 11.6 + k * 9.6, yb - 2, fill=(50, 54, 38))
    for k in range(4):  # dust
        s.ell(w * 0.02 + k * 8, h * 0.90, w * 0.02 + k * 8 + 22, h * 0.99, fill=(222, 204, 170))
    return s.out()


def ic_whitehouse(w, h):
    s = SD(w, h, (170, 205, 235))
    vgrad(s, 0, h, (116, 168, 222), (220, 234, 246))
    u = h / 76.0
    s.rect(0, h - 10 * u, w, h, fill=(92, 140, 80))
    cx = w * 0.42
    wall, shade = (246, 244, 238), (186, 184, 178)
    s.rect(cx - 70, h - 34 * u, cx + 70, h - 10 * u, fill=wall, outline=shade, width=1)
    for x in range(int(cx - 66), int(cx + 66), 9):
        if abs(x - cx) > 28:
            s.rect(x, h - 29 * u, x + 4, h - 20 * u, fill=(90, 110, 140))
    s.rect(cx - 30, h - 46 * u, cx + 30, h - 34 * u, fill=wall, outline=shade, width=1)
    s.poly([(cx - 34, h - 46 * u), (cx, h - 58 * u), (cx + 34, h - 46 * u)], fill=wall, outline=shade, width=1)
    for i in range(6):
        x = cx - 24 + i * 9.6
        s.rect(x - 2, h - 45 * u, x + 2, h - 34 * u, fill=(255, 255, 255), outline=shade, width=1)
    s.line([(cx, h - 58 * u), (cx, h - 72 * u)], (60, 60, 60), 1.2)
    s.poly([(cx, h - 72 * u), (cx + 16, h - 68 * u), (cx, h - 64 * u)], fill=(190, 30, 45))
    s.ell(cx - 20, h - 9 * u, cx + 20, h - 3 * u, fill=(150, 196, 232), outline=(220, 230, 240), width=1)  # fountain pool
    # podium, microphones, flags
    px = w * 0.86
    s.rect(px - 15, h - 28 * u, px + 15, h - 10 * u, fill=(34, 40, 64))
    s.rect(px - 18, h - 30 * u, px + 18, h - 28 * u, fill=(70, 78, 110))
    s.line([(px - 4, h - 30 * u), (px - 4, h - 36 * u)], (20, 20, 20), 1.2)
    s.ell(px - 6, h - 39 * u, px - 2, h - 36 * u, fill=(20, 20, 20))
    s.line([(px + 5, h - 30 * u), (px + 5, h - 37 * u)], (20, 20, 20), 1.2)
    s.ell(px + 3, h - 40 * u, px + 7, h - 37 * u, fill=(20, 20, 20))
    s.line([(w - 6, h - 8 * u), (w - 6, 8)], (70, 70, 76), 1.4)
    s.poly([(w - 6, 8), (w - 28, 12), (w - 6, 16 + 4)], fill=(190, 30, 45))
    s.line([(px - 24, h - 8 * u), (px - 24, 14)], (70, 70, 76), 1.4)
    s.rect(px - 24, 14, px - 4, 26, fill=(0, 40, 104))
    return s.out()


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


def draw_map(page, x, y, w, h):
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 78.0, -52.0

    def pr(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * w, (lat0 - lat) / (lat0 - lat1) * h)

    s = SD(w, h, SEA)
    for lon in range(-150, 190, 30):
        s.line([pr(lon, lat0), pr(lon, lat1)], (206, 214, 226), 0.7)
    for lat in range(60, -52, -30):
        s.line([pr(lon0, lat), pr(lon1, lat)], (206, 214, 226), 0.7)
    for pts in MAP.values():
        s.poly([pr(*p) for p in pts], fill=LAND, outline=(120, 126, 138), width=1)
    page.paste(s.out(), (x, y))
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)
    r = 6.2
    true = [pr(lon, lat) for n, lon, lat in PINS]
    pos = place_pins(true, w, h, r)
    for (tx, ty), (cx_, cy_) in zip(true, pos):
        d.line([x + tx, y + ty, x + cx_, y + cy_], fill=INK, width=1)
        d.ellipse([x + tx - 1.5, y + ty - 1.5, x + tx + 1.5, y + ty + 1.5], fill=INK)
    nf = F(SANS_B, 8)
    for (n, _, _), (cx_, cy_) in zip(PINS, pos):
        d.ellipse([x + cx_ - r, y + cy_ - r, x + cx_ + r, y + cy_ + r], fill=RED, outline=(255, 255, 255), width=1)
        d.text((x + cx_, y + cy_ + 0.5), str(n), font=nf, fill=(255, 255, 255), anchor="mm")


def tag(d, x, y, text, font, fg, bg=(10, 10, 10)):
    tw = int(font.getlength(text))
    d.rectangle([x, y, x + tw + 8, y + font.size + 4], fill=bg)
    d.text((x + 4, y + 2), text, font=font, fill=fg)


def overlay(d, n, x0, y0, w, h, pts):
    f9 = F(SANS_B, 9)
    if n == 1:
        tag(d, x0 + 20, y0 + 1, "KYIV \u2022 OVERNIGHT", f9, (255, 214, 160))
    elif n == 2:
        tag(d, x0 + 20, y0 + 1, "BAY OF BENGAL \u2022 FRI 8AM", f9, (255, 255, 255))
    elif n == 3:
        for (px, py), name in ((pts[2], "TAIPEI"), (pts[5], "SEOUL"), (pts[8], "TOKYO")):
            d.text((x0 + px - 12, y0 + max(22, py - 20)), name, font=f9, fill=(255, 224, 214))
        tag(d, x0 + 8, y0 + h - 18, "AI SELL-OFF", F(SANS_B, 10), (255, 130, 120), (40, 12, 14))
    elif n == 4:
        bf = F(SANS_B, 10)
        bw = int(bf.getlength("NO DEAL")) + 8
        bx = x0 + w // 2 - bw // 2 + 6
        d.rectangle([bx, y0 + h - 17, bx + bw, y0 + h - 4], fill=RED)
        d.text((bx + bw / 2, y0 + h - 10), "NO DEAL", font=bf, fill=(255, 255, 255), anchor="mm")
    elif n == 7:
        d.rectangle([x0 + 24, y0 + 3, x0 + 62, y0 + 17], fill=INK)
        d.text((x0 + 43, y0 + 10.5), "2.3%", font=F(SANS_B, 11), fill=(255, 255, 255), anchor="mm")
    elif n == 8:
        d.text((x0 + w - 30, y0 + h * 0.7), "118", font=F(SANS_B, 14), fill=(255, 255, 255), anchor="mm")


RCOL = [INK, RED, (80, 80, 80), INK, RED, (80, 80, 80), INK]


def rule(d, x0, x1, y, wd=1):
    d.line([x0, y, x1, y], fill=RULE, width=wd)


def main(outdir):
    allnums = sorted(n for _, ns, _ in REGIONS for n in ns)
    assert allnums == list(range(1, 34)), allnums
    assert len(LEADS) + len(FEATS) + len(BRIEFS) == 33
    assert [p[0] for p in PINS] == list(range(1, 34))

    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    d.rectangle([5, 5, W - 6, H - 6], outline=INK, width=2)
    L, R = 24, W - 24
    CW = R - L
    cx = W // 2

    # kicker
    kf = F(SANS_B, 11)
    d.rectangle([L, 14, L + 10, 25], fill=RED)
    d.text((L + 16, 13), "THE WORLD IN ONE DAY", font=kf, fill=INK)
    rt = "FRIDAY'S NEWS • ONE PAGE • 33 STORIES"
    d.text((R - kf.getlength(rt), 13), rt, font=kf, fill=RED)
    rule(d, L, R, 30, 1)

    # masthead: huge bold sans, red underline bar
    mtxt = "Friday 20 November 2026"
    mf = fit_line(mtxt, SANS_B, CW, 60, 40)
    d.text((L - 2, 24), mtxt, font=mf, fill=INK)
    y = 24 + int(mf.size * 1.12) + 2
    d.rectangle([L, y, R, y + 5], fill=RED)
    y += 11
    sf = "Russia's barrage hits Kyiv's bridges • Cyclone Akvan strikes Odisha • An AI sell-off sinks Asia's markets • COP31 reaches its final day with no deal"
    f_sf, lines, lh = fit_block(sf, SANS_B, CW, 1, 14, 9)
    d.text((L, y), lines[0], font=f_sf, fill=INK)
    y += lh + 3
    rule(d, L, R, y, 1)
    y += 6

    # by the numbers
    stats = [("3", "Dnipro bridges struck in Kyiv", INK), ("300,000+", "moved to shelters before Akvan", INK),
             ("−6.2%", "Taiwan's TAIEX on Friday", RED), ("−14%", "Nvidia on Wall Street", RED),
             ("2.3%", "Japan's October inflation", INK), ("118", "Phillips' runs against India", INK)]
    cw = CW / len(stats)
    nf = F(SANS_B, 32)
    cf = F(SANS, 10)
    sy = y
    for i, (num, cap, col) in enumerate(stats):
        ccx = L + cw * i + cw / 2
        ctext(d, ccx, sy - 2, num, fit_line(num, SANS_B, cw - 12, 32, 14), col)
        cl = wrap(cap, cf, cw - 14)
        assert len(cl) <= 2
        for j, c in enumerate(cl):
            ctext(d, ccx, sy + 34 + j * 12, c, cf, GREY)
        if i:
            d.line([L + cw * i, sy + 2, L + cw * i, sy + 58], fill=RULE, width=1)
    y = sy + 62
    rule(d, L, R, y, 1)
    y += 6

    # region bar
    bh = 18
    base = 46
    unit = (CW - base * len(REGIONS)) / 33.0
    x = L
    for i, (name, ns, _col) in enumerate(REGIONS):
        wseg = int(round(base + unit * len(ns)))
        if i == len(REGIONS) - 1:
            wseg = R - x
        d.rectangle([x, y, x + wseg - 1, y + bh], fill=RCOL[i])
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
    ih = LEAD_H
    ly = y
    ty_max = 0
    for i, (kick, head, body, fn) in enumerate(LEADS):
        x0 = L + i * (colw + gap)
        res = fn(colw, ih)
        img, pts = res if isinstance(res, tuple) else (res, None)
        frame_panel(page, img, x0, ly, i + 1)
        overlay(d, i + 1, x0, ly, colw, ih, pts)
        ty = ly + ih + 6
        d.text((x0, ty), kick, font=F(SANS_B, 10), fill=RED)
        ty += 14
        hf, hl, hlh = fit_block(head, SANS_B, colw, 2, 19, 13, 1.1)
        for ln in hl:
            d.text((x0, ty), ln, font=hf, fill=INK)
            ty += hlh
        ty += 3
        bf, bl, blh = fit_block(body, SANS, colw, 4, 11, 9, 1.22)
        for ln in bl:
            d.text((x0, ty), ln, font=bf, fill=GREY)
            ty += blh
        ty_max = max(ty_max, ty)
    for i in range(2):
        xx = L + (i + 1) * (colw + gap) - gap // 2
        d.line([xx, ly, xx, ty_max], fill=RULE, width=1)
    y = ty_max + 3
    rule(d, L, R, y, 2)
    y += 6

    # features: two rows of five
    fgap = 10
    fw = (CW - 4 * fgap) // 5
    for r in range(2):
        ry = y
        rmax = 0
        for c in range(5):
            n = 4 + r * 5 + c
            kick, head, body, fn = FEATS[r * 5 + c]
            x0 = L + c * (fw + fgap)
            img = fn(fw, FEAT_H)
            frame_panel(page, img, x0, ry, n)
            overlay(d, n, x0, ry, fw, FEAT_H, None)
            ty = ry + FEAT_H + 4
            d.text((x0, ty), kick, font=fit_line(kick, SANS_B, fw, 9, 6), fill=RED)
            ty += 12
            hf, hl, hlh = fit_block(head, SANS_B, fw, 2, 14, 10, 1.1)
            for ln in hl:
                d.text((x0, ty), ln, font=hf, fill=INK)
                ty += hlh
            ty += 2
            bf, bl, blh = fit_block(body, SANS, fw, 4, 10, 8, 1.2)
            for ln in bl:
                d.text((x0, ty), ln, font=bf, fill=GREY)
                ty += blh
            rmax = max(rmax, ty)
        for c in range(1, 5):
            xx = L + c * (fw + fgap) - fgap // 2
            d.line([xx, ry, xx, rmax], fill=RULE, width=1)
        y = rmax + 3
        rule(d, L, R, y, 2 if r == 1 else 1)
        y += 6

    # bottom: map (left), briefs (right)
    mw, mh = 322, MAP_H
    d.text((L, y), "WHERE IT HAPPENED", font=F(SANS_B, 10), fill=RED)
    bx = L + mw + 14
    bw = R - bx
    d.text((bx, y), "ALSO ON FRIDAY 20 NOVEMBER — 20 MORE STORIES", font=F(SANS_B, 10), fill=RED)
    y0 = y + 14
    draw_map(page, L, y0, mw, mh)
    d.text((L, y0 + mh + 3), "Numbers mark all 33 stories; positions approximate.", font=F(SANS, 9), fill=GREY)

    colb = (bw - 12) // 2
    bsize = BRIEF_PT
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
    y = max(y0 + mh + 14, brief_bottom) + 4

    # DATE CHECK box (full width, red)
    dc = ("DATE CHECK — First reported Thursday 19 Nov, so NOT shown as Friday's news: Bukele's third-term filing "
          "• Anthropic's IPO debut (+17%) • the ICJ's Rohingya genocide verdict itself • GTA VI's midnight launch • the Trump–Xi–Putin Shenzhen summit itself.")
    dcf, dcl, dclh = fit_block(dc, SANS, CW - 20, 2, 12, 8, 1.3)
    boxh = len(dcl) * dclh + 8
    d.rectangle([L, y, R, y + boxh], fill=(255, 255, 255), outline=RED, width=2)
    d.rectangle([L, y, L + 6, y + boxh], fill=RED)
    yy = y + 4
    for ln in dcl:
        if ln.startswith("DATE CHECK"):
            bfnt = F(SANS_B, dcf.size)
            d.text((L + 14, yy), "DATE CHECK", font=bfnt, fill=RED)
            d.text((L + 14 + bfnt.getlength("DATE CHECK"), yy), ln[len("DATE CHECK"):], font=dcf, fill=INK)
        else:
            d.text((L + 14, yy), ln, font=dcf, fill=INK)
        yy += dclh
    y += boxh + 6

    # footer
    rule(d, L, R, y, 2)
    y += 4
    src = ("Sources: Al Jazeera, ABC News (AU), RTE, Moscow Times, Reuters, CNN, European Business Magazine, Deccan Herald, IMD, Korea Times, "
           "24/7 Wall St, Climate Change News, Agence Europe, FXStreet, Statistics Bureau of Japan, Sportskeeda, Bloomberg, Mwakilishi, France 24, Kyiv Post, "
           "The National, CBS News, Globe and Mail, Korea Herald, People's Daily, Al Arabiya, Formula1.com, Yahoo News, Anadolu, Leadership, NPR")
    sfnt, sl, slh = fit_block(src, SANS, CW, 2, 9, 7, 1.2)
    for ln in sl:
        ctext(d, cx, y, ln, sfnt, GREY)
        y += slh
    y += 1
    ev = "Every story here happened, or was first reported, on Friday 20 November 2026."
    efnt = fit_line(ev, SANS_B, CW, 11, 8)
    ctext(d, cx, y, ev, efnt, INK)
    y += 14
    print("content ends at y=", y, "mast", mf.size, "brief_bottom", brief_bottom, "dc", dcf.size, "src", sfnt.size)
    assert y <= H - 8, y

    os.makedirs(outdir, exist_ok=True)
    page.save(os.path.join(outdir, "entry.png"), optimize=True)


LEAD_H, FEAT_H, MAP_H, BRIEF_PT = 108, 66, 118, 10

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
