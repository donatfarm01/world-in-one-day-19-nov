#!/usr/bin/env python3
"""The World in One Day -- Thursday 19 November 2026.

Draws one 1024x1024 newspaper-style poster summing up the world's news of
Thursday 19 November 2026 and writes it to /output/entry.png
(MAKEFUN_OUTPUT_DIR overrides /output when set).

Pure Python 3.13 standard library: no network, no files read, no randomness,
no clock. Two runs produce byte-identical PNGs.

The five stories (each verified against a reputable source on 19 Nov 2026):

1. CULTURE -- Grand Theft Auto VI launches worldwide today, at midnight
   local time, on PlayStation 5 and Xbox Series X|S, 13 years after GTA V.
   Standard edition $79.99; pre-orders already past $1.5 billion.
   (Reuters, CNN, People, 19 Nov 2026)
2. DIPLOMACY -- Donald Trump, Xi Jinping and Vladimir Putin meet in
   Shenzhen today, the first-ever trilateral summit of the three leaders,
   on the sidelines of the APEC summit. Nuclear arms are the stated focus;
   New START lapsed in February 2026. (Reuters, 18 Nov 2026; White House
   confirmation 13 Nov 2026; The Hindu BusinessLine)
3. MARKETS -- Anthropic starts trading on the Nasdaq today as ANT. The
   Claude maker priced its IPO at $83 a share on Wednesday, above its
   $70-78 range, upsized to 980 million shares -- about $81 billion
   raised, the largest IPO ever. (ZeroHedge, NY Post, Phillip Nova, SEC
   filing, 18 Nov 2026)
4. JUSTICE -- The International Court of Justice delivers its ruling today
   in The Hague in The Gambia's case accusing Myanmar of genocide against
   the Rohingya. The reading starts at 08:00 GMT; the case was filed in
   2019, seven years ago. (BBC-style reporting via St Kitts Gazette,
   Pollar, CrisisBrief, bdjam/UNB, 18 Nov 2026)
5. WEATHER -- Severe Cyclonic Storm Akvan bears down on India's east coast
   today, with extremely heavy rain (21 cm or more) over coastal Andhra
   Pradesh and Odisha. Landfall is forecast around noon on Friday
   20 November, at 90-100 km/h. (India Meteorological Department
   bulletins, 18-19 Nov 2026)

SPDX-License-Identifier: MIT
"""

import math
import os
import struct
import zlib

W = H = 1024

# ---------------------------------------------------------------- font
# A 5x7 bitmap font, drawn as filled blocks. '1' is ink, '0' is blank.
# Only the glyphs this poster uses: A-Z, 0-9 and . , : ; ! ? - ' " / ( ) $ % + =
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00100", "00100"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    ":": ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ";": ("00000", "00100", "00000", "00000", "00100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00011", "00100", "00100", "00100", "00100", "00100", "00011"),
    ")": ("11000", "00100", "00100", "00100", "00100", "00100", "11000"),
    "$": ("00100", "01111", "10000", "01110", "00001", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text drawn at the given scale (6 units per char)."""
    return len(text) * 6 * scale - scale

# ---------------------------------------------------------------- canvas
class Canvas:
    """A plain RGB framebuffer with small vector drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y - t // 2, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x - t // 2, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        """Bresenham line with a square brush of side t."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = t // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, pts, c, t=1):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, t)

    def circle(self, cx, cy, r, c):
        """Filled circle."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        """Circle outline of thickness t."""
        for k in range(t):
            rr = r - k
            if rr <= 0:
                break
            for a in range(360):
                rad = math.radians(a)
                self.set(cx + int(rr * math.cos(rad)),
                         cy + int(rr * math.sin(rad)), c)

    def polygon(self, pts, c):
        """Filled polygon (scanline, even-odd)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                x0 = int(math.ceil(xs[i]))
                x1 = int(math.floor(xs[i + 1]))
                if x1 >= x0:
                    self.fill_rect(x0, y, x1 - x0 + 1, 1, c)

    def vgrad(self, x, y, w, h, stops):
        """Vertical gradient. stops: [(pos 0..1, (r,g,b)), ...] sorted."""
        for yy in range(h):
            p = yy / max(1, h - 1)
            for i in range(len(stops) - 1):
                p0, c0 = stops[i]
                p1, c1 = stops[i + 1]
                if p0 <= p <= p1:
                    f = 0.0 if p1 == p0 else (p - p0) / (p1 - p0)
                    c = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
                    break
            else:
                c = stops[-1][1] if p >= stops[-1][0] else stops[0][1]
            self.fill_rect(x, y + yy, w, 1, c)

    def text(self, x, y, scale, c, s):
        """Draw text at top-left (x, y); unknown chars render blank."""
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale

    def text_center(self, cx, y, scale, c, s):
        self.text(cx - text_width(s, scale) // 2, y, scale, c, s)


# ---------------------------------------------------------------- png
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: None
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
           _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- art
def star(cv, cx, cy, r, c):
    """Five-point star, filled."""
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang))))
    cv.polygon(pts, c)


def palm(cv, bx, by, h, c, lean):
    """A palm silhouette: leaning trunk, five drooping curved fronds."""
    tx = bx + lean
    ty = by - h
    # Slightly curved trunk (two segments).
    mx, my = bx + lean // 2, by - h // 2
    cv.line(bx, by, mx, my, c, 5)
    cv.line(mx, my, tx, ty, c, 5)
    for k in range(-2, 3):
        # Each frond is a quadratic curve from the crown, arcing out
        # and drooping down to its tip.
        fx = tx + k * 24
        fy = ty + 34 + abs(k) * 6
        cxp = tx + k * 20
        cyp = ty - 18 - abs(k) * 3
        pts = []
        for i in range(9):
            t = i / 8.0
            px = int((1 - t) * (1 - t) * tx + 2 * (1 - t) * t * cxp + t * t * fx)
            py = int((1 - t) * (1 - t) * ty + 2 * (1 - t) * t * cyp + t * t * fy)
            pts.append((px, py))
        cv.polyline(pts, c, 3)


def skyline(cv, x, y_base, w, c, win_a, win_b):
    """Dark building silhouettes with a few lit windows (fixed pattern)."""
    bx = x
    n = 0
    while bx < x + w:
        bw = 34 + (n * 37) % 42
        bh = 46 + (n * 53) % 96
        cv.fill_rect(bx, y_base - bh, bw, bh, c)
        for wy in range(y_base - bh + 8, y_base - 6, 14):
            for wx in range(bx + 6, bx + bw - 6, 12):
                if (wx * 7 + wy * 13) % 5 == 0:
                    cv.fill_rect(wx, wy, 4, 5, win_a if (wx + wy) % 2 else win_b)
        bx += bw + 4
        n += 1


def courthouse(cv, x, y, w, h, c):
    """A small classical courthouse: pediment, columns, steps."""
    cv.polygon([(x, y + h // 3), (x + w // 2, y), (x + w, y + h // 3)], c)
    cv.fill_rect(x, y + h // 3, w, 6, c)
    col_w = 12
    gap = (w - 4 * col_w) // 5
    for i in range(4):
        cx = x + gap + i * (col_w + gap)
        cv.fill_rect(cx, y + h // 3 + 8, col_w, h - h // 3 - 26, c)
    cv.fill_rect(x, y + h - 18, w, 6, c)
    cv.fill_rect(x - 8, y + h - 10, w + 16, 5, c)
    cv.fill_rect(x - 16, y + h - 3, w + 32, 4, c)


def spiral(cv, cx, cy, c, c2):
    """A cyclone spiral: two interleaved Archimedean arms."""
    for arm, col in ((0.0, c), (math.pi, c2)):
        pts = []
        steps = 90
        for i in range(steps + 1):
            t = arm + i * (3.6 * math.pi) / steps
            r = 6 + 62 * i / steps
            pts.append((cx + int(r * math.cos(t)), cy + int(r * math.sin(t))))
        cv.polyline(pts, col, 3)
    cv.circle(cx, cy, 9, c2)


def chart(cv, x, y, w, h, bars, up, c_bar, c_arrow):
    """Rising bars with an arrow shooting up-right."""
    bw = w // len(bars)
    base = y + h
    tops = []
    for i, v in enumerate(bars):
        bh = int(h * v)
        bx = x + i * bw + 3
        cv.fill_rect(bx, base - bh, bw - 6, bh, c_bar)
        tops.append((bx + (bw - 6) // 2, base - bh))
    pts = [(tops[0][0] - 14, tops[0][1] + 16)] + tops
    pts.append((tops[-1][0] + 16, tops[-1][1] - 18))
    cv.polyline(pts, c_arrow, 4)
    ex, ey = pts[-1]
    cv.polygon([(ex, ey), (ex - 16, ey + 2), (ex - 2, ey + 16)], c_arrow)
    cv.hline(x, base, w, up, 2)


# ---------------------------------------------------------------- palette
PAPER = (250, 244, 230)
INK = (20, 24, 38)
NAVY = (18, 33, 61)
NAVY2 = (26, 48, 88)
GOLD = (201, 162, 39)
RED = (198, 47, 47)
PINK = (255, 122, 184)
TEAL = (13, 92, 99)
TEAL_D = (9, 58, 66)
GREEN_D = (11, 46, 37)
GREEN = (47, 191, 113)
WHITE = (255, 255, 255)
CREAM = (255, 251, 240)
SKY = (255, 214, 140)

# ---------------------------------------------------------------- layout
def panel_border(cv, x, y, w, h, c, t=3):
    cv.fill_rect(x, y, w, t, c)
    cv.fill_rect(x, y + h - t, w, t, c)
    cv.fill_rect(x, y, t, h, c)
    cv.fill_rect(x + w - t, y, t, h, c)


def draw_poster():
    cv = Canvas(W, H, PAPER)
    # Thin frame around the whole page.
    panel_border(cv, 8, 8, W - 16, H - 16, INK, 2)

    # ---- masthead ------------------------------------------------------
    cv.fill_rect(20, 20, 984, 112, NAVY)
    cv.hline(20, 28, 984, GOLD, 3)
    cv.hline(20, 124, 984, GOLD, 3)
    cv.text_center(512, 38, 6, WHITE, "THE WORLD IN ONE DAY")
    cv.text_center(512, 94, 3, SKY, "THURSDAY 19 NOVEMBER 2026")

    # ---- hero: GTA VI --------------------------------------------------
    hx, hy, hw, hh = 20, 144, 984, 368
    ax = hx  # art area: x 20..560
    aw = 540
    # Sunset sky.
    cv.vgrad(ax, hy, aw, hh, [
        (0.00, (43, 27, 78)),
        (0.45, (184, 59, 94)),
        (0.70, (240, 138, 93)),
        (1.00, (249, 196, 107)),
    ])
    # Retro sun with slits.
    cv.circle(290, 330, 64, (255, 233, 168))
    for sy in (306, 322, 338, 354):
        cv.fill_rect(226, sy, 128, 5, (240, 138, 93))
    # Neon sign.
    cv.text_center(290, 164, 3, PINK, "VICE CITY")
    cv.hline(201, 192, 178, GOLD, 2)
    # Skyline + sea.
    skyline(cv, ax, 470, aw, (29, 21, 51), (89, 213, 224), (255, 92, 138))
    cv.fill_rect(ax, 470, aw, hh - (470 - hy), (18, 59, 92))
    for i, ry in enumerate((484, 494, 504)):
        cv.hline(ax + 30 + i * 60, ry, 220 - i * 40, (60, 120, 160), 2)
    palm(cv, 100, 470, 108, (29, 21, 51), -18)
    palm(cv, 508, 470, 88, (29, 21, 51), 14)
    # Text side.
    cv.fill_rect(ax + aw, hy, hw - aw, hh, CREAM)
    cv.text(584, 166, 2, RED, "CULTURE")
    cv.text(584, 196, 8, INK, "GTA VI")
    cv.text(584, 256, 8, INK, "IS HERE")
    cv.hline(584, 330, 396, GOLD, 3)
    cv.text(584, 348, 3, INK, "AFTER 13 YEARS,")
    cv.text(584, 374, 3, INK, "VICE CITY OPENS")
    cv.text(584, 400, 3, INK, "WORLDWIDE TODAY")
    cv.text(584, 440, 2, (90, 90, 90), "PS5 + XBOX - $79.99")
    cv.text(584, 462, 2, (90, 90, 90), "PRE-ORDERS TOP $1.5BN")
    panel_border(cv, hx, hy, hw, hh, INK, 3)

    # ---- middle row ----------------------------------------------------
    my, mh = 524, 224
    # Trilateral (left).
    cv.fill_rect(20, my, 480, mh, NAVY)
    # US flag banner.
    fx, fy, fw, fh = 32, 536, 146, 64
    for i in range(7):
        cv.fill_rect(fx, fy + i * 9, fw, 9, RED if i % 2 == 0 else WHITE)
    cv.fill_rect(fx, fy, 58, 36, NAVY2)
    for r in range(3):
        for c_ in range(4):
            cv.fill_rect(fx + 8 + c_ * 13, fy + 7 + r * 10, 3, 3, WHITE)
    # China flag banner.
    cv.fill_rect(185, fy, fw, fh, (222, 41, 16))
    star(cv, 218, 568, 13, (255, 222, 0))
    for sx, sy in ((248, 550), (260, 562), (260, 578), (248, 588)):
        star(cv, sx, sy, 5, (255, 222, 0))
    # Russia flag banner.
    cv.fill_rect(338, fy, fw, 22, WHITE)
    cv.fill_rect(338, fy + 22, fw, 21, (0, 57, 166))
    cv.fill_rect(338, fy + 43, fw, 21, (213, 0, 0))
    cv.text(32, 608, 2, GOLD, "DIPLOMACY - APEC")
    cv.text(32, 632, 4, WHITE, "THREE LEADERS,")
    cv.text(32, 664, 4, WHITE, "ONE TABLE")
    cv.text(32, 700, 3, SKY, "TRUMP, XI, PUTIN")
    cv.text(32, 724, 3, SKY, "MEET IN SHENZHEN")
    panel_border(cv, 20, my, 480, mh, INK, 3)

    # Anthropic IPO (right).
    cv.fill_rect(524, my, 480, mh, GREEN_D)
    cv.text(548, 544, 2, GOLD, "MARKETS")
    cv.text(548, 570, 4, WHITE, "ANT DEBUTS")
    cv.text(548, 602, 4, WHITE, "AT $83")
    cv.text(548, 646, 3, SKY, "RECORD $81BN IPO")
    cv.text(548, 672, 3, SKY, "HITS NASDAQ TODAY")
    cv.text(548, 706, 5, GOLD, "ANT")
    chart(cv, 880, 560, 104, 156,
          (0.35, 0.50, 0.45, 0.70, 0.92), WHITE, GREEN, GOLD)
    panel_border(cv, 524, my, 480, mh, INK, 3)

    # ---- bottom row ----------------------------------------------------
    by, bh = 760, 204
    # ICJ (left).
    cv.fill_rect(20, by, 480, bh, PAPER)
    courthouse(cv, 192, 766, 136, 64, NAVY)
    cv.text_center(260, 836, 2, RED, "JUSTICE")
    cv.text_center(260, 854, 4, INK, "WORLD COURT")
    cv.text_center(260, 886, 4, INK, "DECIDES")
    cv.text_center(260, 920, 3, INK, "MYANMAR RULING DUE TODAY")
    panel_border(cv, 20, by, 480, bh, INK, 3)

    # Cyclone Akvan (right).
    cv.fill_rect(524, by, 480, bh, TEAL_D)
    spiral(cv, 915, 858, WHITE, (120, 220, 215))
    for rx in (862, 884, 906, 928, 950, 968):
        cv.line(rx, 934, rx + 8, 950, (200, 240, 240), 2)
    cv.text(548, 784, 2, SKY, "WEATHER")
    cv.text(548, 808, 4, WHITE, "STORM OVER")
    cv.text(548, 840, 4, WHITE, "THE BAY")
    cv.text(548, 882, 3, WHITE, "AKVAN NEARS INDIA")
    cv.text(548, 908, 3, WHITE, "LANDFALL FRIDAY")
    panel_border(cv, 524, by, 480, bh, INK, 3)

    # ---- footer ---------------------------------------------------------
    cv.text_center(512, 980, 2, INK,
                   "FIVE STORIES - ONE DAY - SOURCES: REUTERS, CNN, SEC FILING, IMD")
    return cv


def main():
    import hashlib

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, draw_poster())
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (path, size, digest))


if __name__ == "__main__":
    main()
