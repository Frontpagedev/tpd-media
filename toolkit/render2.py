import os
"""TPD square news short — editorial style (cream, serif, brand red), cold open on the key fact."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1080; FPS = 30; DUR = 45.0
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
CREAM = (247, 243, 236); INK = (24, 22, 20); GREY = (110, 104, 98); LINE = (226, 219, 208)
RED = (173, 0, 2); RED2 = (140, 0, 2); PALE = (236, 229, 218)

def serif(size, bold=True, italic=False):
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-%sVariable.ttf" % ("Italic-" if italic else ""), size)
    try: f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception: pass
    return f
def sans(size, w="SemiBold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", size)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def seg(t, a, b): return clamp((t - a) / (b - a))
def tw(f, s): b = f.getbbox(s); return b[2] - b[0]
def wrap(f, s, mw):
    out, cur = [], ""
    for wd in s.split():
        c = (cur + " " + wd).strip()
        if tw(f, c) <= mw: cur = c
        else: out.append(cur); cur = wd
    return out + ([cur] if cur else [])
def fadeimg(im, a):
    im = im.convert("RGBA")
    if a < 1: im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    return im

LOGO_IM = Image.open(LOGO).convert("RGB")

# ---------- flags ----------
def star(d, cx, cy, R, fill, rot=-90):
    d.polygon([(cx + (R if i % 2 == 0 else R * .4) * math.cos(math.radians(rot + i * 36)),
                cy + (R if i % 2 == 0 else R * .4) * math.sin(math.radians(rot + i * 36))) for i in range(10)], fill=fill)
def flag(k, w, h):
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im); WH = (255, 255, 255)
    if k == "PK":
        d.rectangle([0, 0, w, h], fill=(1, 65, 28)); d.rectangle([0, 0, w // 4, h], fill=WH)
        cx, cy, r = w * .625, h * .5, h * .3; d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=WH)
        r2 = r * .85; d.ellipse([cx+r*.28-r2, cy-r*.22-r2, cx+r*.28+r2, cy-r*.22+r2], fill=(1, 65, 28))
        star(d, cx + r*.55, cy - r*.42, h*.085, WH, -45)
    elif k == "TR":
        d.rectangle([0, 0, w, h], fill=(227, 10, 23)); cx, cy, r = w*.36, h*.5, h*.25
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=WH); r2 = r*.8
        d.ellipse([cx+r*.25-r2, cy-r2, cx+r*.25+r2, cy+r2], fill=(227, 10, 23)); star(d, cx+r*.95, cy, h*.125, WH, 180)
    elif k == "SA":
        d.rectangle([0, 0, w, h], fill=(0, 108, 53))
        for i in range(7):
            x0 = w * (.2 + i * .087); d.rounded_rectangle([x0, h*.27, x0+w*.06, h*.47], radius=2, fill=WH)
        d.rectangle([w*.22, h*.66, w*.76, h*.69], fill=WH)
    elif k == "IR":
        d.rectangle([0, 0, w, h/3], fill=(35, 159, 64)); d.rectangle([0, h/3, w, 2*h/3], fill=WH)
        d.rectangle([0, 2*h/3, w, h], fill=(218, 0, 0))
    return im

# ---------- portraits: real photo if photos/<KEY>.jpg exists, else typographic card ----------
PEOPLE = {
    "PK": dict(name="Asim Munir", pre="Field Marshal", role="Chief of Defence Forces and Chief of Army Staff", country="Pakistan", ini="AM", col=(1, 65, 28)),
    "SA": dict(name="Khalid bin Salman", pre="Prince", role="Minister of Defence", country="Saudi Arabia", ini="KbS", col=(0, 98, 50)),
    "TR": dict(name="İbrahim Kalın", pre="", role="Head of the National Intelligence Organisation (MİT)", country="Türkiye", ini="İK", col=(175, 12, 24)),
}
def portrait(k, w, h):
    p = os.path.join(HERE, "photos", k + ".jpg")
    if os.path.exists(p):
        im = Image.open(p).convert("RGB"); s = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        x = (im.width - w) // 2; y = max(0, int((im.height - h) * 0.25))
        return im.crop((x, y, x + w, y + h))
    c = np.array(PEOPLE[k]["col"], float)
    yy, xx = np.mgrid[0:h, 0:w]
    g = (0.75 + 0.25 * (1 - yy / h))[..., None]
    arr = np.clip(c * g + 18 * np.sin(xx / 7.0)[..., None] * 0, 0, 255).astype(np.uint8)
    im = Image.fromarray(arr); lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(-h, w, 26): d.line([(i, 0), (i + h, h)], fill=(255, 255, 255, 14), width=2)
    f = serif(int(h * 0.36)); s = PEOPLE[k]["ini"]
    d.text(((w - tw(f, s)) / 2, h * 0.24), s, font=f, fill=(255, 255, 255, 235))
    im = im.convert("RGBA"); im.alpha_composite(lay)
    fl = flag(k, int(w * .22), int(w * .22 * 2 / 3)); im.paste(fl, (int(w * .06), int(h - w * .06 - fl.height)))
    return im.convert("RGB")
PORT = {k: portrait(k, 600, 600) for k in PEOPLE}
PORT_BIG = {k: portrait(k, 1080, 640) for k in PEOPLE}

# ---------- chrome ----------
SOURCES = "Sources: IRNA · ISNA · The Express Tribune / Anadolu"
def chrome(im, t, show_logo=True):
    d = ImageDraw.Draw(im)
    if show_logo:
        im.paste(LOGO_IM.resize((64, 64), Image.LANCZOS), (48, 40))
        d.text((128, 46), "The Pakistan Daily", font=serif(30), fill=INK)
        d.rectangle([128, 88, 128 + 190, 91], fill=RED)
    d.text((W - 48 - tw(sans(20), "WORLD · IRAN"), 54), "WORLD · IRAN", font=sans(20), fill=RED)
    d.text((48, H - 52), SOURCES, font=sans(16, "Medium"), fill=GREY)
    d.rectangle([0, H - 12, W * t / DUR, H], fill=RED)

def highlight_text(d, x, y, lines, f, hl_words, lh, reveal):
    """Draws serif lines word by word; words in hl_words get a red box with white text."""
    i = 0
    for li, ln in enumerate(lines):
        cx = x
        for wd in ln.split():
            a = ease(seg(reveal, i * 0.06, i * 0.06 + 0.25)); i += 1
            ww = tw(f, wd)
            if a > 0:
                yy = y + li * lh + 14 * (1 - a)
                key = wd.strip(",.").lower()
                col = INK
                if key in hl_words:
                    d.rectangle([cx - 8, y + li * lh + 4, cx + ww + 8, y + li * lh + lh - 6], fill=RED)
                    col = (255, 255, 255)
                c = tuple(int(CREAM[j] + (col[j] - CREAM[j]) * a) for j in range(3)) if key not in hl_words else col
                d.text((cx, yy), wd, font=f, fill=c)
            cx += ww + tw(f, " ")

# ---------- scenes ----------
def s_cold(im, t, D):
    # FIRST FRAME = the fact, fully legible at t=0
    d = ImageDraw.Draw(im)
    keys = ["PK", "SA", "TR"]; sz = 300; gap = 24; x0 = (W - 3 * sz - 2 * gap) // 2
    for i, k in enumerate(keys):
        z = 1 + 0.05 * t / D; s = int(sz * z)
        p = PORT[k].resize((s, s), Image.LANCZOS).crop(((s - sz) // 2, (s - sz) // 2, (s - sz) // 2 + sz, (s - sz) // 2 + sz))
        im.paste(p, (x0 + i * (sz + gap), 150))
        d.text((x0 + i * (sz + gap), 150 + sz + 12), PEOPLE[k]["country"].upper(), font=sans(19), fill=RED)
    f = serif(54)
    txt = "Pakistan's army chief, Saudi Arabia's defence minister and Turkey's spy chief are heading to Tehran"
    lines = wrap(f, txt, W - 120)
    highlight_text(d, 60, 530, lines, f, {"tehran"}, 74, t * 1.6 + 2.0)  # already revealed at t=0
    a = ease(seg(t, 1.2, 1.8))
    d.text((60, 530 + len(lines) * 74 + 22), "For a joint meeting, Iran's top security body says",
           font=serif(30, False, True), fill=tuple(int(CREAM[j] + (GREY[j] - CREAM[j]) * a) for j in range(3)))

def s_person(k, idx):
    P = PEOPLE[k]
    def draw(im, t, D):
        d = ImageDraw.Draw(im)
        z = 1 + 0.06 * t / D; ph = PORT_BIG[k]
        s = ph.resize((int(1080 * z), int(640 * z)), Image.LANCZOS)
        ox = int((s.width - 1080) * (0.5 + 0.3 * (t / D - .5))); oy = (s.height - 640) // 2
        im.paste(s.crop((ox, oy, ox + 1080, oy + 640)), (0, 120))
        a = ease(seg(t, 0.15, 0.7))
        y0 = 120 + 640 + 30
        d.rectangle([60, y0, 60 + 6, y0 + 200], fill=RED)
        lab = f"0{idx} / 03 · {P['country'].upper()}"
        d.text((86, y0 - 2), lab, font=sans(20), fill=RED)
        if P["pre"]: d.text((86 + 40 * (1 - a), y0 + 32), P["pre"], font=serif(28, False, True), fill=GREY)
        d.text((86 + 60 * (1 - a), y0 + 66), P["name"], font=serif(64), fill=INK)
        b = ease(seg(t, 0.5, 1.0))
        for i, ln in enumerate(wrap(sans(26, "Regular"), P["role"], 860)):
            d.text((88, y0 + 152 + i * 34), ln, font=sans(26, "Regular"),
                   fill=tuple(int(CREAM[j] + (INK[j] - CREAM[j]) * b) for j in range(3)))
    return draw

LON0, LON1, LAT0, LAT1 = 26, 78, 18, 44
def proj(lat, lon): return (80 + (lon - LON0) / (LON1 - LON0) * 920, 250 + (LAT1 - lat) / (LAT1 - LAT0) * 600)
CITY = {"Tehran": (35.69, 51.39), "Islamabad": (33.68, 73.05), "Riyadh": (24.71, 46.68), "Ankara": (39.93, 32.86)}
def s_map(im, t, D):
    d = ImageDraw.Draw(im, "RGBA")
    d.text((60, 140), "Three capitals, one table", font=serif(52), fill=INK)
    d.text((60, 206), "Senior security officials converge on Tehran", font=serif(28, False, True), fill=GREY)
    for lat in np.arange(LAT0, LAT1 + .1, 1.3):
        for lon in np.arange(LON0, LON1 + .1, 1.3):
            x, y = proj(lat, lon); d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=LINE)
    tx, ty = proj(*CITY["Tehran"])
    for i, (c, k, who) in enumerate([("Ankara", "TR", "Kalın"), ("Riyadh", "SA", "Khalid bin Salman"), ("Islamabad", "PK", "Munir")]):
        sx, sy = proj(*CITY[c]); p = ease(seg(t, .4 + i * .7, 2.0 + i * .7))
        mx, my = (sx + tx) / 2, min(sy, ty) - 120
        pts = [((1-u)**2*sx + 2*(1-u)*u*mx + u*u*tx, (1-u)**2*sy + 2*(1-u)*u*my + u*u*ty) for u in np.linspace(0, p, 50)]
        ca = ease(seg(t, .2 + i * .7, .7 + i * .7))
        if ca > 0:
            d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=INK + (int(255 * ca),))
            im.paste(fadeimg(flag(k, 48, 32), ca), (int(sx - 24), int(sy + 18)), fadeimg(flag(k, 48, 32), ca))
            f = sans(24, "Bold"); d.text((sx - tw(f, c.upper()) / 2, sy + 58), c.upper(), font=f, fill=INK + (int(255 * ca),))
            f2 = serif(22, False, True); d.text((sx - tw(f2, who) / 2, sy + 88), who, font=f2, fill=GREY + (int(255 * ca),))
        if p > 0: d.line(pts, fill=RED + (255,), width=5)
    for kk in range(2):
        ph = (t * .7 + kk / 2) % 1; r = 12 + ph * 60
        d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=RED + (int(170 * (1 - ph)),), width=3)
    d.ellipse([tx - 14, ty - 14, tx + 14, ty + 14], fill=RED)
    d.text((tx - 70, ty + 26), "TEHRAN", font=serif(40), fill=RED)
    d.text((W - 60 - tw(sans(16, "Medium"), "Schematic, not to scale"), 870), "Schematic, not to scale", font=sans(16, "Medium"), fill=GREY)

def s_quote(im, t, D):
    d = ImageDraw.Draw(im)
    d.text((60, 160), "WHAT TEHRAN SAYS", font=sans(22), fill=RED)
    a = ease(seg(t, 0, .6)); d.rectangle([60, 220, 66, 220 + int(430 * a)], fill=RED)
    f = serif(50, False, True)
    lines = ["The visit is part of a push", "to implement", "“endogenous security”", "in West Asia"]
    for i, ln in enumerate(lines):
        b = ease(seg(t, .3 + i * .35, .9 + i * .35))
        hl = i == 2
        ff = serif(62) if hl else f
        col = RED if hl else INK
        c = tuple(int(CREAM[j] + (col[j] - CREAM[j]) * b) for j in range(3))
        d.text((100 + 30 * (1 - b), 250 + i * 86), ln, font=ff, fill=c)
    b = ease(seg(t, 2.0, 2.6))
    c = tuple(int(CREAM[j] + (INK[j] - CREAM[j]) * b) for j in range(3))
    d.text((100, 640), "Announced by Ali Bagheri", font=sans(28, "Bold"), fill=c)
    d.text((100, 680), "Deputy Secretary, Iran's Supreme National Security Council", font=sans(24, "Regular"), fill=c)
    b = ease(seg(t, 3.0, 3.6)); c = tuple(int(CREAM[j] + (GREY[j] - CREAM[j]) * b) for j in range(3))
    for i, ln in enumerate(wrap(serif(28, False, True), "The phrase is Tehran's term for security arranged by the region's own states.", 900)):
        d.text((100, 770 + i * 40), ln, font=serif(28, False, True), fill=c)

STATS = [("3", "regional powers sending top security officials"),
         ("1", "joint meeting, which Munir flagged in recent Tehran talks"),
         ("27 Oct", "Israel votes, with tensions over Iran running high")]
def s_stats(im, t, D):
    d = ImageDraw.Draw(im)
    d.text((60, 150), "Why it matters now", font=serif(52), fill=INK)
    for i, (n, lab) in enumerate(STATS):
        a = ease(seg(t, .4 + i * .9, 1.0 + i * .9)); y = 290 + i * 190
        if a <= 0: continue
        col = RED if i != 1 else INK
        d.rectangle([60, y, 66, y + int(140 * a)], fill=col)
        num = n
        if n.isdigit(): num = str(int(round(int(n) * a))) if a < 1 else n
        c = tuple(int(CREAM[j] + (col[j] - CREAM[j]) * a) for j in range(3))
        d.text((96, y + 10), num, font=serif(96), fill=c)
        f = sans(28, "Regular"); x = 96 + max(tw(serif(96), n), 120) + 40
        ci = tuple(int(CREAM[j] + (INK[j] - CREAM[j]) * a) for j in range(3))
        for k, ln in enumerate(wrap(f, lab, W - x - 60)):
            d.text((x, y + 40 + k * 38), ln, font=f, fill=ci)

def s_end(im, t, D):
    a = ease(seg(t, 0, .6))
    d = ImageDraw.Draw(im)
    top = int(H * (1 - a))
    d.rectangle([0, top, W, H], fill=RED)
    if a < .99: return
    b = ease(seg(t, .5, 1.2)); WHc = lambda v: tuple(int(RED[j] + (v[j] - RED[j]) * b) for j in range(3))
    f = serif(54)
    for i, ln in enumerate(["Three regional powers,", "one meeting,", "hosted by Tehran"]):
        d.text(((W - tw(f, ln)) / 2, 230 + i * 72), ln, font=f, fill=WHc((255, 255, 255)))
    d.rectangle([W / 2 - 60, 470, W / 2 + 60, 474], fill=WHc((255, 255, 255)))
    c = ease(seg(t, 1.0, 1.7))
    lg = LOGO_IM.resize((300, 300), Image.LANCZOS)
    im.paste(fadeimg(lg, c), ((W - 300) // 2, 540), fadeimg(lg, c))
    f2 = sans(28, "SemiBold"); s = "thepakistandaily.com"
    d.text(((W - tw(f2, s)) / 2, 870), s, font=f2, fill=tuple(int(RED[j] + (255 - RED[j]) * c) for j in range(3)))
    d.text(((W - tw(sans(16, "Medium"), SOURCES)) / 2, H - 52), SOURCES, font=sans(16, "Medium"), fill=(240, 200, 200))

SCENES = [(0, 7, s_cold), (7, 11.5, s_person("PK", 1)), (11.5, 16, s_person("SA", 2)), (16, 20.5, s_person("TR", 3)),
          (20.5, 28.5, s_map), (28.5, 35, s_quote), (35, 40.5, s_stats), (40.5, 45, s_end)]

def frame(t):
    for a, b, fn in SCENES:
        if a <= t < b:
            im = Image.new("RGB", (W, H), CREAM)
            fn(im, t - a, b - a)
            if fn is not s_end: chrome(im, t)
            out = im
            if a > 0 and t - a < 0.25:  # quick wipe-in from previous scene feel
                k = (t - a) / 0.25
                bg = Image.new("RGB", (W, H), CREAM); chrome(bg, t)
                out = Image.blend(bg, im, ease(k))
            return out
    return Image.new("RGB", (W, H), CREAM)

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in map(float, sys.argv[2:]): frame(s).save(os.path.join(HERE, f"v2_{s:05.1f}.png"))
        sys.exit()
    out, audio = sys.argv[1], sys.argv[2]
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait(); print("done")
