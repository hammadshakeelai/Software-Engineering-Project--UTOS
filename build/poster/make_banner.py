"""Render the UTOS GitHub README hero banner with PIL (no browser needed).
Outputs banner.png at 2x (2560x1280) for crisp retina display.
"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2                      # supersample / retina scale
W, H = 1280 * S, 640 * S

# ---- fonts -------------------------------------------------------------
FD = r"C:\Windows\Fonts"
def font(name, px):
    return ImageFont.truetype(os.path.join(FD, name), px * S)
F_EYE   = font("segoeuib.ttf", 13)
F_TITLE = font("segoeuib.ttf", 104)
F_SUB   = font("seguisb.ttf", 25)
F_PUR   = font("segoeui.ttf", 16)
F_PILL  = font("seguisb.ttf", 13)
F_ROLE  = font("seguisb.ttf", 12)
F_TECH  = font("segoeuib.ttf", 12)
F_BY    = font("segoeui.ttf", 13)
F_BYB   = font("seguisb.ttf", 13)
F_URL   = font("segoeui.ttf", 11)
F_BADGE = font("segoeuib.ttf", 13)
F_BADGS = font("seguisb.ttf", 9)

INK  = (232, 241, 240)
SUB  = (159, 182, 179)
MINT = (127, 240, 221)

# ---- background gradient (numpy) --------------------------------------
def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u = (xx / W); v = (yy / H)
# diagonal base navy gradient
t = (u * .55 + v * .45)
c0 = np.array([10, 22, 34]); c1 = np.array([12, 33, 40]); c2 = np.array([10, 28, 34])
base = (c0[None,None,:]*(1-t)[...,None] + c1[None,None,:]*t[...,None])
# blend toward c2 in lower band
base = base*(1-v[...,None]*.25) + c2[None,None,:]*(v[...,None]*.25)

def radial(cx, cy, rad, col, strength):
    d = np.sqrt((xx-cx*W)**2 + (yy-cy*H)**2) / (rad*S)
    g = np.clip(1 - d, 0, 1) ** 1.6
    return g[...,None] * np.array(col)[None,None,:] * strength

glow = (radial(.88, .18, 470, [22,184,166], .55)
        + radial(.06, .96, 360, [15,110,102], .75)
        + radial(.80, 1.05, 200, [22,184,166], .45))
arr = np.clip(base + glow, 0, 255).astype(np.uint8)
img = Image.fromarray(arr, "RGB").convert("RGBA")

# faint grid texture
tex = Image.new("RGBA", (W, H), (0,0,0,0))
td = ImageDraw.Draw(tex)
step = 42 * S
for x in range(0, W, step):
    td.line([(x,0),(x,H)], fill=(255,255,255,10), width=1)
for y in range(0, H, step):
    td.line([(0,y),(W,y)], fill=(255,255,255,10), width=1)
img = Image.alpha_composite(img, tex)
d = ImageDraw.Draw(img)

# ---- helpers ----------------------------------------------------------
def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r*S, fill=fill, outline=outline, width=width*S)

def text(draw, xy, s, fnt, fill, ls=0):
    if ls:
        x, y = xy
        for ch in s:
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += draw.textlength(ch, font=fnt) + ls*S
        return x
    draw.text(xy, s, font=fnt, fill=fill)
    return xy[0] + draw.textlength(s, font=fnt)

def tw(draw, s, fnt): return draw.textlength(s, font=fnt)

# ---- gradient title ---------------------------------------------------
def gradient_text(s, fnt, grad_cols):
    bb = d.textbbox((0,0), s, font=fnt)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    pad = 10*S
    mask = Image.new("L", (w+pad*2, h+pad*2), 0)
    ImageDraw.Draw(mask).text((pad-bb[0], pad-bb[1]), s, font=fnt, fill=255)
    grad = Image.new("RGB", mask.size)
    ga = np.zeros((mask.size[1], mask.size[0], 3), np.uint8)
    n = len(grad_cols)-1
    for ix in range(mask.size[0]):
        tt = ix/(mask.size[0]-1); seg = min(int(tt*n), n-1); lt = tt*n-seg
        ga[:,ix,:] = lerp(grad_cols[seg], grad_cols[seg+1], lt)
    grad = Image.fromarray(ga, "RGB")
    return grad, mask

LX = 64 * S
y = 54 * S
text(d, (LX, y), "SOFTWARE ENGINEERING  ·  COURSE PROJECT", F_EYE, MINT, ls=3)
y += 30 * S
grad, mask = gradient_text("UTOS", F_TITLE, [(255,255,255),(127,240,221),(22,184,166)])
img.paste(grad, (LX-10*S, y-6*S), mask)
y += 104 * S - 8*S
text(d, (LX, y), "University Timetable Optimization System", F_SUB, (223,243,240))
y += 25*S + 14*S

# purpose (wrapped manually)
pur_lines = [
 ("A web app that turns teachers, courses, rooms & sections into", SUB),
 ("conflict-free weekly timetables", (207,238,233)),
 ("through a constraint-based solver — with role-based access,", SUB),
 ("locking, re-optimization, versioning & live reports.", SUB),
]
# render line2 bold-ish inline:
text(d, (LX, y), "A web app that turns teachers, courses, rooms & sections", F_PUR, SUB); y += 23*S
x2 = LX
x2 = text(d, (x2, y), "into ", F_PUR, SUB)
x2 = text(d, (x2, y), "conflict-free weekly timetables", F_PUR, (207,238,233))
text(d, (x2, y), " through a constraint-based", F_PUR, SUB); y += 23*S
text(d, (LX, y), "solver — with role access, locking, re-optimize, versioning & reports.", F_PUR, SUB)
y += 23*S + 20*S

# ---- pills ------------------------------------------------------------
pills = ["Constraint solver","Lock & re-optimize","Versioning & diff",
         "Change requests","Reports & audit log"]
px, py = LX, y
maxx = LX + 540*S
for p in pills:
    wpx = tw(d, p, F_PILL) + 16*S + 14*S   # square + paddings
    if px + wpx > maxx:
        px = LX; py += 38*S
    rrect(d, [px, py, px+wpx, py+30*S], 15, fill=(22,184,166,33), outline=(22,184,166,90), width=1)
    d.rectangle([px+13*S, py+12*S, px+13*S+6*S, py+18*S], fill=MINT)
    text(d, (px+27*S, py+7*S), p, F_PILL, (214,239,235))
    px += wpx + 9*S
y = py + 30*S + 20*S

# ---- roles ------------------------------------------------------------
roles = [("Administrator",(22,184,166)),("Coordinator",(63,169,245)),
         ("Teacher",(245,166,35)),("Student",(176,110,245)),("Facility Mgr",(245,94,122))]
rx = LX
for name, col in roles:
    wpx = tw(d, name, F_ROLE) + 14*S + 12*S
    rrect(d, [rx, y, rx+wpx, y+28*S], 9, fill=(255,255,255,12), outline=(255,255,255,26), width=1)
    d.ellipse([rx+9*S, y+10*S, rx+17*S, y+18*S], fill=col)
    text(d, (rx+22*S, y+6*S), name, F_ROLE, (191,230,224))
    rx += wpx + 8*S
y += 28*S

# ---- footer: tech chips + author -------------------------------------
fy = 540*S
tx = LX
for tname in ["Python","stdlib HTTP","SQLite","Vanilla JS"]:
    wpx = tw(d, tname, F_TECH) + 22*S
    # gradient-ish chip: solid mint->teal vertical approximated by flat teal
    rrect(d, [tx, fy, tx+wpx, fy+26*S], 7, fill=(28,200,180,255))
    text(d, (tx+11*S, fy+6*S), tname, F_TECH, (10,28,34))
    tx += wpx + 7*S
# author line
ay = fy + 40*S
ax = text(d, (LX, ay), "Muhammad Hammad Shakeel", F_BYB, (234,251,248))
text(d, (ax, ay), "  ·  Team Hakari Bankai   |   utos.onrender.com", F_BY, SUB)

# ---- right: browser frame with screenshot ----------------------------
shot = Image.open(os.path.join(HERE, "crop_timetable.png")).convert("RGB")
FW = 560 * S                              # frame width
chrome_h = 34 * S
sw = FW
sh = int(shot.height * sw / shot.width)
sh = min(sh, 470*S)                        # cap height
shot_r = shot.resize((sw, int(shot.width and sw*shot.height/shot.width)))
shot_r = shot_r.crop((0,0,sw,sh))
FHt = chrome_h + sh
frame = Image.new("RGBA", (FW, FHt), (0,0,0,0))
fd = ImageDraw.Draw(frame)
# rounded white card
rrect(fd, [0,0,FW,FHt], 14, fill=(255,255,255,255))
# chrome bar
chrome = Image.new("RGBA",(FW,chrome_h),(15,36,48,255))
cd = ImageDraw.Draw(chrome)
for i,col in enumerate([(255,95,87),(254,188,46),(40,200,64)]):
    cd.ellipse([14*S+i*18*S, 11*S, 14*S+i*18*S+11*S, 22*S], fill=col)
cd.rounded_rectangle([78*S, 8*S, 230*S, 26*S], radius=11*S, fill=(10,26,32,255))
cd.text((92*S, 11*S), "utos.onrender.com", font=F_URL, fill=(143,179,174))
frame.paste(chrome, (0,0))
frame.paste(shot_r, (0, chrome_h))
# re-apply rounded mask to clip corners
mask = Image.new("L", (FW, FHt), 0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,FW,FHt], radius=14*S, fill=255)
frame.putalpha(mask)
# rotate
rot = frame.rotate(2.2, expand=True, resample=Image.BICUBIC)
# shadow
sh_img = Image.new("RGBA", rot.size, (0,0,0,0))
ImageDraw.Draw(sh_img).rounded_rectangle([0,0,rot.size[0],rot.size[1]], radius=20*S, fill=(0,0,0,150))
sh_img = sh_img.filter(ImageFilter.GaussianBlur(22*S))
fx, fy2 = 700*S, 92*S
img.alpha_composite(sh_img, (fx-10*S, fy2+18*S))
img.alpha_composite(rot, (fx, fy2))

# ---- badge ------------------------------------------------------------
badge = Image.new("RGBA",(150*S,52*S),(0,0,0,0))
bd = ImageDraw.Draw(badge)
ga = np.zeros((52*S,150*S,3),np.uint8)
for ix in range(150*S):
    ga[:,ix,:] = lerp((22,184,166),(15,110,102), ix/(150*S-1))
bgrad = Image.fromarray(ga,"RGB").convert("RGBA")
bmask = Image.new("L",(150*S,52*S),0)
ImageDraw.Draw(bmask).rounded_rectangle([0,0,150*S,52*S],radius=12*S,fill=255)
badge.paste(bgrad,(0,0),bmask)
bd = ImageDraw.Draw(badge)
t1 = "CONFLICT-FREE"; w1 = bd.textlength(t1,font=F_BADGE)
bd.text(((150*S-w1)/2, 9*S), t1, font=F_BADGE, fill=(255,255,255))
t2 = "SCORE ~92 / 100"; w2 = bd.textlength(t2,font=F_BADGS)
bd.text(((150*S-w2)/2, 30*S), t2, font=F_BADGS, fill=(225,245,242))
badge = badge.rotate(2.2, expand=True, resample=Image.BICUBIC)
img.alpha_composite(badge, (1080*S, 60*S))

# ---- save -------------------------------------------------------------
out = os.path.join(HERE, "banner.png")
img.convert("RGB").save(out, quality=95)
print("saved", out, img.size)
