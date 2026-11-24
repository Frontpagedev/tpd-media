"""TPD explainer: Smog in Lahore — levels, causes, debate. Usage: render12.py reel|x out.mp4 | render12.py reel|x stills t..."""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from render2 import clamp, ease, seg, tw, wrap, LOGO_IM, fadeimg

HERE = os.path.dirname(os.path.abspath(__file__)); PH = FT = os.path.join(HERE, "footage/msl")
SCR = "/tmp/claude-0/-home-claude/60efd90f-1914-5c23-b412-fb0172b38646/scratchpad/p22"
FPS = 30
BG = (10, 14, 18); BG2 = (24, 34, 30); INK = (244, 246, 250); SOFT = (176, 186, 204); DIM = (92, 104, 128)
ORANGE = (255, 150, 40); RED = (220, 40, 40); PURPLE = (143, 63, 151); MAROON = (126, 0, 35); GREEN = (0, 200, 120); YEL = (250, 210, 40)
AQI_BANDS = [(0, 50, (0, 200, 90), "Good"), (51, 100, (250, 210, 40), "Moderate"), (101, 150, (255, 140, 60), "Unhealthy for sensitive groups"),
             (151, 200, (220, 40, 40), "Unhealthy"), (201, 300, (143, 63, 151), "Very unhealthy"), (301, 500, (126, 0, 35), "Hazardous")]
ID = "/usr/share/fonts/opentype/inter/"
_f = {}
def F(n, s):
    k = (n, s)
    if k not in _f: _f[k] = ImageFont.truetype(ID + n, s)
    return _f[k]
HK = lambda s: F("InterDisplay-Black.otf", s); HX = lambda s: F("InterDisplay-ExtraBold.otf", s); HB = lambda s: F("InterDisplay-Bold.otf", s)
TX = lambda s, w="Medium": F(f"Inter-{w}.otf", s)
def mix(a, c, bg=BG): return tuple(int(bg[j] + (c[j] - bg[j]) * clamp(a)) for j in range(3))

MODE = sys.argv[1] if len(sys.argv) > 1 else "reel"; R = MODE == "reel"
if R: W, H = 1080, 1920; TOP = 196; Y0 = 290; Y1 = 1610; SRC = 1640
else: W, H = 1080, 1350; TOP = 24; Y0 = 100; Y1 = 1280; SRC = 1305
CH = Y1 - Y0; S = 1.36 if R else .9; V = 1.3 if R else 1.0   # type scale

# hazy background: vertical gradient + drifting particles
_g = np.linspace(0, 1, H)[:, None, None]
BGIMG = Image.fromarray((np.array(BG) * (1 - _g) + np.array(BG2) * _g).repeat(W, 1).astype(np.uint8))
rng = np.random.default_rng(12); PART = rng.random((140, 4))
def background(t):
    im = BGIMG.copy(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, sp, sz in PART:
        px = (x * W + t * (6 + sp * 18)) % W; py = (y * H + math.sin(t * .4 + x * 9) * 30) % H; r = 1.5 + sz * 4
        d.ellipse([px - r, py - r, px + r, py + r], fill=(170, 190, 180, int(8 + sp * 20)))
    im.paste(lay, (0, 0), lay); return im

def P(n): return Image.open(os.path.join(PH, n)).convert("RGB")
IMG = {}
def cover(key, w, h, z=1.0, focus=(.5, .5)):
    im = IMG[key]; s = max(w / im.width, h / im.height) * z; cw, ch = w / s, h / s
    x0 = clamp(focus[0] * im.width - cw / 2, 0, im.width - cw); y0 = clamp(focus[1] * im.height - ch / 2, 0, im.height - ch)
    return im.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))

class Clip:
    def __init__(self, path, crop, w, h): self.path, self.crop, self.w, self.h, self.p, self.next = path, crop, w, h, None, None
    def frame(self, st):
        idx = round(st * FPS)
        if self.p is None or self.next != idx:
            if self.p: self.p.kill()
            vf = f"crop={self.crop},scale={self.w}:{self.h}:flags=lanczos,fps={FPS}"
            self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{idx / FPS:.3f}", "-i", self.path, "-vf", vf,
                                       "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); self.next = idx
        b = self.p.stdout.read(self.w * self.h * 3); self.next += 1
        return Image.frombytes("RGB", (self.w, self.h), b) if len(b) == self.w * self.h * 3 else Image.new("RGB", (self.w, self.h), BG)
VH = 720 if R else 500


def chrome(im, kicker, src):
    d = ImageDraw.Draw(im)
    im.paste(LOGO_IM.resize((50, 50), Image.LANCZOS), (40, TOP))
    d.text((104, TOP + 7), "THE PAKISTAN DAILY", font=HX(28), fill=INK)
    if kicker:
        f = TX(22, "Bold"); kw = tw(f, kicker) + 30
        d.rounded_rectangle([W - 40 - kw, TOP + 6, W - 40, TOP + 46], radius=8, fill=ORANGE); d.text((W - 40 - kw + 15, TOP + 13), kicker, font=f, fill=BG)
    if src: d.text((40, SRC), "SOURCES: " + src, font=TX(18, "SemiBold"), fill=DIM)

def rise(d, x, y, text, font, t, start=0, col=INK, maxw=None, lh=None):
    ls = wrap(font, text, maxw or W - 80); lh = lh or int(font.size * 1.18)
    for i, ln in enumerate(ls):
        a = ease(seg(t, start + i * .1, start + i * .1 + .5))
        if a > 0: d.text((x, y + i * lh + int(16 * (1 - a))), ln, font=font, fill=mix(a, col))
    return y + len(ls) * lh

def aqi_color(v):
    for lo, hi, c, _ in AQI_BANDS:
        if v <= hi: return c
    return MAROON

def caption(img, text):
    d = ImageDraw.Draw(img); f = TX(18); w_ = tw(f, text) + 26
    d.rectangle([img.width - w_, img.height - 32, img.width, img.height], fill=(0, 0, 0)); d.text((img.width - w_ + 13, img.height - 27), text, font=f, fill=(225, 220, 214))

# ---------------- scenes ----------------
sys.path.insert(0, os.path.join(HERE, "geo")); import mapdata
AMB = ORANGE; CYAN = (80, 200, 230); RED = (230, 70, 70); GREENP = (40, 160, 90)
MH = int(CH * (.56 if R else .50))
FOOT = os.path.join(FT, "main.mp4")
CL = Clip(FOOT, f"1024:576:0:0,scale={W}:{MH}:force_original_aspect_ratio=increase,crop={W}:{MH}", W, MH)
PROVS = mapdata.provinces(); NB = mapdata.topo_countries({"Afghanistan", "Iran", "India", "China", "Tajikistan", "Oman", "Nepal", "Turkmenistan"})

def med(im, ph, t, cap=None, y=None, reveal=True):
    y = Y0 if y is None else y
    if cap: caption(ph, cap)
    a = ease(clamp(t / .4)) if reveal else 1; hh = max(1, int(ph.height * a)); im.paste(ph.crop((0, 0, ph.width, hh)), (0, y)); return y + ph.height
def kick(d, y, s, col=AMB): d.text((40, y), s, font=TX(26, "Bold"), fill=col); return y + 44
def big(d, y, t, s, st=.2, size=54, col=INK): return rise(d, 40, y, s, HX(int(size * S)), t, st, col)
def para(d, y, t, s, st=.8, size=32, col=SOFT): return rise(d, 40, y, s, TX(int(size * S), "SemiBold"), t, st, col)
CAP = "Footage: ISPR"

def s_open(im, t, D):
    v = CL.frame(0.2 + t); y = med(im, v, t, CAP, reveal=False) + 30; d = ImageDraw.Draw(im)
    y = kick(d, y, "18 NOVEMBER 2026 · ARMY ROCKET FORCE COMMAND")
    f = HX(int(60 * S))
    for i, ln in enumerate(wrap(f, "Pakistan test-fires the Fatah-3 supersonic cruise missile", W - 80)): d.text((40, y + i * int(f.size * 1.14)), ln, font=f, fill=INK)
    chrome(im, "DEFENCE", "ISPR")

def s_flight(im, t, D):
    v = CL.frame(3.6 + min(t, 5.2)); y = med(im, v, t, CAP, reveal=False) + 30; d = ImageDraw.Draw(im)
    y = kick(d, y, "WHAT THE MILITARY SAYS")
    y = big(d, y, t, "“Can engage long-range targets with high precision and lethality at supersonic speeds”", .3, 46)
    para(d, y + 12, t, "ISPR", 2.0, 28)
    chrome(im, "DEFENCE", "ISPR")

SPEC = [("TYPE", "Supersonic, likely ramjet-powered", "ANALYSTS"), ("LAUNCHER", "Road-mobile truck launcher", "OBSERVED"),
        ("SPEED", "Est. Mach 2.2–4", "ESTIMATE"), ("RANGE", "Est. 290–450 km", "ESTIMATE"), ("DESIGN", "Resembles China's HD-1", "ANALYSTS")]
def s_spec(im, t, D):
    d = ImageDraw.Draw(im); y = big(d, Y0, t, "Fatah-3, decoded", 0, 60) + 10
    y = para(d, y, t, "Pakistan has not released range or speed. These are analyst estimates.", .4, 28) + int(26 * S)
    for i, (k, v, tg) in enumerate(SPEC):
        b = ease(seg(t, 1.2 + i * .9, 1.7 + i * .9)); yy = y + i * int(120 * S * (1.15 if R else 1))
        d.text((40, yy), k, font=TX(int(22 * S), "Bold"), fill=mix(b, SOFT))
        c = CYAN if tg == "OBSERVED" else AMB; f = TX(int(20 * S), "Bold"); w = tw(f, tg) + 20
        d.rounded_rectangle([W - 40 - w, yy - 2, W - 40, yy + int(30 * S)], radius=6, outline=mix(b, c), width=2); d.text((W - 30 - w, yy + 2), tg, font=f, fill=mix(b, c))
        d.text((40, yy + int(34 * S)), v, font=HX(int(40 * S)), fill=mix(b, INK))
        d.line([(40, yy + int(96 * S)), (W - 40, yy + int(96 * S))], fill=mix(b, (50, 60, 60)), width=2)
    chrome(im, "THE MISSILE", "Quwa · The Defense Post · Army Recognition")

def s_race(im, t, D):
    d = ImageDraw.Draw(im); y = big(d, Y0, t, "Why speed matters", 0, 60) + 6
    y = para(d, y, t, "Time to cover 300 km", .3, 32) + int(50 * S)
    lanes = [("SUBSONIC CRUISE MISSILE", "Mach 0.8", 18.2, SOFT), ("SUPERSONIC, MACH 2.8", "", 5.2, AMB)]
    x0, x1 = 60, W - 60; T = 7.0
    for i, (lab, sub, mins, c) in enumerate(lanes):
        yy = y + i * int(250 * S * (1.1 if R else .95)); d.text((40, yy), lab, font=TX(int(26 * S), "Bold"), fill=c)
        ly = yy + int(90 * S); d.line([(x0, ly), (x1, ly)], fill=(60, 70, 70), width=4)
        for k in range(7): xx = x0 + (x1 - x0) * k / 6; d.line([(xx, ly - 8), (xx, ly + 8)], fill=(80, 90, 90), width=2)
        p = clamp((t - .8) / (T * mins / 18.2)); xm = x0 + (x1 - x0) * ease(p) if i else x0 + (x1 - x0) * p
        d.line([(x0, ly), (xm, ly)], fill=c, width=8)
        d.polygon([(xm + 26, ly), (xm - 10, ly - 12), (xm - 4, ly), (xm - 10, ly + 12)], fill=c)
        clock = mins * clamp((t - .8) / (T * mins / 18.2)); s = f"{clock:4.1f} min"; f = HK(int(54 * S))
        d.text((W - 40 - tw(f, s), yy + int(130 * S)), s, font=f, fill=INK if p < 1 else c)
    para(d, y + 2 * int(250 * S * (1.1 if R else .95)) + 10, t, "Less time for air defences to detect, track and intercept.", 8.0, 34, INK)
    chrome(im, "THE PHYSICS", "Illustrative · Mach 1 ≈ 1,235 km/h at sea level")

FAM = [("Fatah-1", 140, "guided rocket", SOFT, False), ("Fatah-2", 400, "guided rocket", CYAN, False), ("Fatah-3", 450, "supersonic cruise, est.", AMB, True), ("Fatah-4", 750, "subsonic cruise", (190, 120, 255), False)]
LP = (71.0, 30.2)
def s_rings(im, t, D):
    mh = int(CH * (.60 if R else .55)); lon0, lat0, span = 74.0, 29.0, 22.0 if R else 25.0; cl = math.cos(math.radians(lat0)); sc = W / span
    def P(lo, la): return (W / 2 + (lo - lon0) * cl * sc, mh / 2 - (la - lat0) * sc)
    lay = Image.new("RGB", (W, mh), (12, 18, 22)); d = ImageDraw.Draw(lay, "RGBA")
    for n, polys in NB.items():
        for poly in polys:
            pts = [P(*q) for q in poly]
            if len(pts) > 2: d.polygon(pts, fill=(30, 36, 40), outline=(60, 66, 70))
    for n, polys in PROVS.items():
        for poly in polys:
            pts = [P(*q) for q in poly]
            if len(pts) > 2: d.polygon(pts, fill=(34, 74, 52), outline=(70, 120, 90))
    cx, cy = P(*LP)
    for i, (n, km, kind, c, est) in enumerate(FAM):
        a = ease(seg(t, .8 + i * 1.5, 1.9 + i * 1.5))
        if a <= 0: continue
        r = km / 111.0 * sc * a; col = c + (int(255 * min(1, a)),)
        if est:
            for k in range(0, 360, 8): d.arc([cx - r, cy - r * 1.0, cx + r, cy + r], k, k + 5, fill=col, width=5)
            r2 = 290 / 111.0 * sc * a
            for k in range(0, 360, 8): d.arc([cx - r2, cy - r2, cx + r2, cy + r2], k, k + 5, fill=c + (150,), width=3)
        else: d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=4)
        f = TX(int(22 * S), "Bold"); lab = f"{n} \u00b7 " + (str(km) if not est else "290\u2013450") + " km"; ang = math.radians([-60, -20, 25, -45][i])
        lx, ly_ = cx + r * math.cos(ang), cy + r * math.sin(ang); d.rectangle([lx + 4, ly_ - 14, lx + 12 + tw(f, lab), ly_ + 16], fill=(12, 18, 22, 200)); d.text((lx + 8, ly_ - 12), lab, font=f, fill=col)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=INK)
    im.paste(lay, (0, Y0)); d = ImageDraw.Draw(im)
    d.text((40, Y0 + mh - 32), "Illustrative ranges from a point in central Pakistan · Map: Natural Earth", font=TX(18), fill=DIM)
    y = Y0 + mh + 26; y = kick(d, y, "THE FATAH FAMILY")
    big(d, y, t, "Fatah-3 fills the gap: faster than Fatah-4, longer reach than Fatah-1", 6.6, 42)
    chrome(im, "THE ARSENAL", "Dawn · Arab News · Quwa · The Defense Post")

def s_brahmos(im, t, D):
    d = ImageDraw.Draw(im); y = big(d, Y0, t, "The obvious comparison: BrahMos", 0, 54) + int(30 * S)
    cols = [("BRAHMOS", "India · in service since the mid-2000s", "Mach 2.8", "290–450 km", CYAN), ("FATAH-3", "Pakistan · tested Nov 2026", "Est. Mach 2.2–4", "Est. 290–450 km", AMB)]
    cw = (W - 100) // 2
    for i, (n, sub, sp, rg, c) in enumerate(cols):
        b = ease(seg(t, .6 + i * 1.0, 1.1 + i * 1.0)); x = 40 + i * (cw + 20); hh = int(420 * S)
        d.rounded_rectangle([x, y, x + cw, y + hh], radius=18, fill=mix(b, (24, 30, 34)), outline=mix(b, c), width=3)
        d.text((x + 24, y + 22), n, font=HX(int(40 * S)), fill=mix(b, c))
        for j, ln in enumerate(wrap(TX(int(22 * S), "SemiBold"), sub, cw - 48)): d.text((x + 24, y + int(78 * S) + j * int(28 * S)), ln, font=TX(int(22 * S), "SemiBold"), fill=mix(b, SOFT))
        d.text((x + 24, y + int(160 * S)), "SPEED", font=TX(int(20 * S), "Bold"), fill=mix(b, SOFT)); d.text((x + 24, y + int(186 * S)), sp, font=HX(int(36 * S)), fill=mix(b, INK))
        d.text((x + 24, y + int(270 * S)), "RANGE", font=TX(int(20 * S), "Bold"), fill=mix(b, SOFT)); d.text((x + 24, y + int(296 * S)), rg, font=HX(int(36 * S)), fill=mix(b, INK))
    para(d, y + int(450 * S), t, "India says it fired BrahMos at Pakistani targets in May 2025. If estimates hold, Fatah-3 puts Pakistan in the same speed class.", 3.2, 30, INK)
    chrome(im, "THE RIVALRY", "BrahMos Aerospace · Business Today · Defence Security Asia")

def s_impact(im, t, D):
    v = CL.frame(9.0 + t) if t < 3.8 else CL.frame(12.9 + min(t - 3.8, 3.0)); y = med(im, v, t, CAP, reveal=False) + 30; d = ImageDraw.Draw(im)
    y = kick(d, y, "THE TEST")
    big(d, y, t, "ISPR footage shows the missile striking its target marker", .3, 48)
    chrome(im, "THE TEST", "ISPR")

TL = [("MAY 2025", "Four-day conflict with India"), ("AUG 2025", "Army Rocket Force Command created"), ("SEP 2025", "Fatah-4 cruise missile tested, 750 km"),
      ("MAY 2026", "Fatah-3 unveiled"), ("NOV 2026", "Fatah-3 test-fired")]
def s_why(im, t, D):
    d = ImageDraw.Draw(im); y = big(d, Y0, t, "Why now?", 0, 64) + int(30 * S)
    for i, (dt, s) in enumerate(TL):
        b = ease(seg(t, .6 + i * .9, 1.1 + i * .9)); yy = y + i * int(108 * S * (1.1 if R else .95)); c = AMB if i == len(TL) - 1 else INK
        d.ellipse([52, yy + 12, 76, yy + 36], fill=mix(b, AMB))
        if i < len(TL) - 1: d.line([(64, yy + 40), (64, yy + int(108 * S * (1.1 if R else .95)) + 8)], fill=mix(b, (60, 70, 70)), width=3)
        d.text((100, yy + 4), dt, font=HX(int(30 * S)), fill=mix(b, AMB)); d.text((100, yy + int(44 * S)), s, font=TX(int(30 * S), "SemiBold"), fill=mix(b, c))
    yy = y + len(TL) * int(108 * S * (1.1 if R else .95)) + 10
    para(d, yy, t, "The Rocket Force is built for conventional, non-nuclear precision strikes: deterrence below the nuclear threshold.", 5.6, 30, INK)
    chrome(im, "THE CONTEXT", "Dawn · Arab News · Quwa · ISPR")

def s_end(im, t, D):
    v = CL.frame(16.0 + t) if t < 4.0 else CL.frame(21.0 + min(t - 4.0, 1.3)); y = med(im, v, t, CAP, reveal=False) + 30; d = ImageDraw.Draw(im)
    big(d, y, t, "In South Asia's missile race, speed is the new deterrent.", .3, 50)
    c = ease(seg(t, 2.6, 3.2)); ly = y + int(170 * S)
    lg = LOGO_IM.resize((100, 100), Image.LANCZOS); im.paste(fadeimg(lg, c), (40, ly), fadeimg(lg, c))
    d.text((160, ly + 30), "thepakistandaily.com", font=HX(38), fill=mix(c, INK))


UNK = ["Official range and speed", "Accuracy in combat conditions", "When it enters service", "How many will be built"]
def s_unknown(im, t, D):
    d = ImageDraw.Draw(im); y = big(d, Y0, t, "What we still don't know", 0, 60) + int(30 * S)
    for i, s_ in enumerate(UNK):
        b = ease(seg(t, .6 + i * .9, 1.1 + i * .9)); yy = y + i * int(110 * S * (1.1 if R else .95))
        d.text((40, yy), "?", font=HK(int(56 * S)), fill=mix(b, AMB)); d.text((40 + int(70 * S), yy + int(10 * S)), s_, font=HX(int(40 * S)), fill=mix(b, INK))
    para(d, y + 4 * int(110 * S * (1.1 if R else .95)) + 10, t, "A successful test is a milestone, not proof of operational readiness, analysts note.", 4.6, 30, SOFT)
    chrome(im, "THE CAVEATS", "Army Recognition \u00b7 Quwa")

SCENES = [("open", 3.5, s_open), ("flight", 6.0, s_flight), ("spec", 9.0, s_spec), ("race", 12.0, s_race), ("rings", 12.0, s_rings),
          ("brahmos", 11.0, s_brahmos), ("impact", 6.8, s_impact), ("unknown", 8.0, s_unknown), ("why", 12.0, s_why), ("end", 7.0, s_end)]
STARTS = np.cumsum([0] + [D for _, D, _ in SCENES]).tolist(); TR = .35
def scene_frame(i, tl):
    n, D, fn = SCENES[i]; im = background(STARTS[i] + tl); fn(im, tl, D); return im
def frame_in_scene(i, tl):
    im = scene_frame(i, tl)
    if i > 0 and tl < TR:  # haze dissolve: blur-through transition
        prev = scene_frame(i - 1, SCENES[i - 1][1] - 1e-3); k = ease(tl / TR)
        rad = 14 * math.sin(math.pi * k); out = Image.blend(prev, im, k)
        return out.filter(ImageFilter.GaussianBlur(rad)) if rad > .5 else out
    return im
def at(t):
    for i in range(len(SCENES)):
        if t < STARTS[i + 1]: return frame_in_scene(i, t - STARTS[i])
    return frame_in_scene(len(SCENES) - 1, SCENES[-1][1] - 1e-3)

ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS)]
def render_scene(i, path):
    n, D, fn = SCENES[i]; tmp = path[:-4] + ".part.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + ENC + [tmp], stdin=subprocess.PIPE)
    for k in range(int(round(D * FPS))): pr.stdin.write(frame_in_scene(i, k / FPS).tobytes())
    pr.stdin.close()
    if pr.wait() == 0: os.replace(tmp, path)
    else: raise SystemExit(f"scene {n} failed")

if __name__ == "__main__":
    if sys.argv[2] == "stills":
        for s in map(float, sys.argv[3:]): at(s).save(os.path.join(HERE, f"v22{MODE}_{s:05.1f}.png"))
        sys.exit()
    out = sys.argv[2]; os.makedirs(SCR, exist_ok=True); parts = []
    for i in range(len(SCENES)):
        p = os.path.join(SCR, f"{MODE}_{i}_{SCENES[i][0]}.mp4"); render_scene(i, p); parts.append(p)
    lst = os.path.join(SCR, f"{MODE}_list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    silent = os.path.join(SCR, f"{MODE}_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    DUR = STARTS[-1]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(HERE, "audio/Industrial_Cinematic.mp3"), "-filter_complex",
                    f"[1:a]atrim=0:{DUR},afade=t=in:st=0:d=0.3,afade=t=out:st={DUR - 3}:d=3,loudnorm=I=-15:TP=-1.5[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-t", f"{DUR}",
                    "-movflags", "+faststart", out], check=True)
    print("done", DUR)
