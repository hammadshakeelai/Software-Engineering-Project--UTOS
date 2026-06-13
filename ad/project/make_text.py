"""Render premium motion-typography overlays (1920x1080 RGBA PNGs) for the UTOS ad.
Lower-third captions with a baked navy scrim for legibility over any background,
brand teal accents, Segoe UI Bold (clean match for the app's Inter). Plus a
centered closing brand card. Composited over video in the assembly step.
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "clips")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)

W, H = 1920, 1080
TEAL = (22, 184, 166, 255)     # #16b8a6
TEAL_SOFT = (160, 226, 218, 255)
WHITE = (255, 255, 255, 255)
NAVY = (8, 22, 30)             # scrim base
SEGB = "C:/Windows/Fonts/segoeuib.ttf"
SEG = "C:/Windows/Fonts/segoeui.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def scrim(img, top=540, strength=225):
    g = Image.new("L", (1, H), 0)
    px = g.load()
    for y in range(H):
        a = 0 if y < top else int(strength * (((y - top) / (H - top)) ** 1.25))
        px[0, y] = min(255, a)
    g = g.resize((W, H))
    layer = Image.new("RGBA", (W, H), NAVY + (0,))
    layer.putalpha(g)
    img.alpha_composite(layer)


def text_sh(d, xy, s, fnt, fill, sh=(0, 0, 0, 170), off=3):
    d.text((xy[0] + off, xy[1] + off), s, font=fnt, fill=sh)
    d.text(xy, s, font=fnt, fill=fill)


def ctext_sh(d, cx, y, s, fnt, fill, sh=(0, 0, 0, 170), off=3):
    b = d.textbbox((0, 0), s, font=fnt)
    x = cx - (b[2] - b[0]) // 2 - b[0]
    text_sh(d, (x, y), s, fnt, fill, sh, off)


def lower_third(name, headline, sub=None, hsize=66):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scrim(img)
    d = ImageDraw.Draw(img)
    x = 150
    lines = headline.split("\n")
    bar_y = H - 130 - len(lines) * (hsize + 18)
    d.rectangle([x, bar_y, x + 78, bar_y + 9], fill=TEAL)        # teal accent bar
    y = bar_y + 34
    hf = F(SEGB, hsize)
    for ln in lines:
        text_sh(d, (x, y), ln, hf, WHITE)
        y += hsize + 18
    if sub:
        text_sh(d, (x + 2, y + 4), sub, F(SEG, 36), TEAL_SOFT)
    img.save(os.path.join(OUT, "text_" + name + ".png"))
    print("text_" + name)


def logo_mark(d, cx, top, s=96):
    # teal rounded square with white "U"
    d.rounded_rectangle([cx - s // 2, top, cx + s // 2, top + s], radius=22, fill=TEAL)
    f = F(SEGB, int(s * 0.62))
    ctext_sh(d, cx, top + int(s * 0.16), "U", f, WHITE, sh=(0, 0, 0, 0), off=0)


def closing():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W // 2
    logo_mark(d, cx, 300, 104)
    ctext_sh(d, cx, 430, "UTOS", F(SEGB, 150), WHITE)
    d.rectangle([cx - 70, 624, cx + 70, 632], fill=TEAL)
    ctext_sh(d, cx, 660, "Timetables that just work.", F(SEGB, 54), WHITE)
    ctext_sh(d, cx, 752, "utos.onrender.com", F(SEG, 42), TEAL_SOFT, sh=(0, 0, 0, 120), off=2)
    img.save(os.path.join(OUT, "text_close.png"))
    print("text_close")


lower_third("s1", "Every term,\nthe same chaos.")
lower_third("s2", "Clashing rooms.\nDouble-booked teachers.", hsize=58)
lower_third("s3", "Meet UTOS", "University Timetable Optimization System", hsize=92)
lower_third("s4a", "One click.\nConflict-free.")
lower_third("s4b", "Solve.  Lock.  Re-optimize.", hsize=58)
lower_third("s5", "Every role,\none source of truth.")
lower_third("admin", "Hours lost to conflicts.")
lower_third("solver", "Constraint-aware scheduling.", hsize=58)
lower_third("hall", "From chaos to clarity.")
closing()
print("DONE")
