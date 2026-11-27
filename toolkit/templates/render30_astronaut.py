"""TPD 27 Nov: Pakistan's first astronaut aboard Tiangong (kit v3, from render29 template)."""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from tpdkit import *
from tpdkit import _topmask
SCR = "/tmp/claude-0/-home-claude/78d62065-14a4-5957-9119-43d9bdce8425/scratchpad/v30"
V = os.path.join(HERE, "footage/astronaut/pakinfrance.mp4")
PH = 820; CROP = "720:547:0:72"  # top of the portrait frame only, burned subtitles (y~860-1010) never enter
def mk(): return Src(V, CROP, ph=PH, sharpen=True)
S_OPEN, S_TRAIN, S_PART, S_END = mk(), mk(), mk(), mk()
CAP = "Pre-launch interview · Video: @PakinFrance on X"
PKG = (1, 122, 56)  # Pakistan green
KK = "TIANGONG"
B_OPEN = (V, 14.00, 22.95); B_TRAIN = (V, 4.6, 13.7); B_PART = (V, 26.64, 36.75); B_END = (V, 36.96, 43.64)
def bl(b): return b[2] - b[1]
SUBY = PY + PH + 26

# ---------- starfield / earth ----------
rnd = random.Random(30)
STARS = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice([1, 1, 1, 2, 2, 3]), rnd.uniform(0, 6.28), rnd.uniform(.3, 1)) for _ in range(330)]
_yy = np.linspace(0, 1, H)[:, None]
SKY = Image.fromarray(np.clip(np.stack([6 + 10 * _yy, 9 + 16 * _yy, 20 + 34 * _yy], -1).repeat(W, 1), 0, 255).astype(np.uint8), "RGB")
def make_earth(cy, r):
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32); dist = np.sqrt((xs - 540) ** 2 + (ys - cy) ** 2)
    inside = dist <= r; depth = np.clip((r - dist) / 260, 0, 1)
    col = np.zeros((H, W, 4), np.float32)
    col[..., 0] = 20 + 30 * (1 - depth); col[..., 1] = 70 + 60 * (1 - depth); col[..., 2] = 120 + 90 * (1 - depth)
    col[..., 3] = inside * 255
    glow = np.clip(1 - np.abs(dist - r) / 46, 0, 1) ** 2 * (dist > r)
    col[..., 0] = np.where(inside, col[..., 0], 90); col[..., 1] = np.where(inside, col[..., 1], 170); col[..., 2] = np.where(inside, col[..., 2], 255)
    col[..., 3] = np.maximum(col[..., 3], glow * 200)
    return Image.fromarray(col.astype(np.uint8), "RGBA")
EARTH = make_earth(2630, 1500); EARTH2 = make_earth(3400, 2200)
def stars(im, t, speed=6, dim=1.0):
    im.paste(SKY, (0, 0)); d = ImageDraw.Draw(im)
    for x, y, s, ph, b in STARS:
        x = int((x - t * speed * s) % W); y = int(y); a = dim * b * (.65 + .35 * math.sin(t * 2.2 + ph)); c = tuple(int(v * a) for v in (235, 240, 255))
        d.rectangle([x, y, x + s - 1, y + s - 1], fill=c) if s < 3 else d.ellipse([x - 1, y - 1, x + 2, y + 2], fill=c)
def earth(im, t, e=EARTH, rise_px=40, D=7):
    im.paste(e, (0, int(rise_px * (1 - t / D))), e)

# ---------- scenes ----------
def s_open(im, t, D):
    y = stage(im, S_OPEN, B_OPEN[1] + t, CAP, zoom=1 + .05 * t / D); d = ImageDraw.Draw(im)
    o = ease(seg(t, 3.6, 4.0)); f = HK(56); yy = PY + 36
    if o < 1:
        for i, ln in enumerate(["Pakistan's first astronaut", "is aboard China's space station"]):
            w_ = tw(f, ln); dx = -int((w_ + 120) * ease(seg(t, 3.6 + i * .06, 4.0 + i * .06)))
            d.rectangle([34 + dx, yy - 6, 34 + dx + w_ + 30, yy + 68], fill=PKG); d.text((49 + dx, yy), ln, font=f, fill=INK); yy += 80
    y = label(d, y + 26, "WING COMMANDER ZEESHAN ALI", GOLD, t + 1)
    subs(d, y, t, [(-1, 2.95, "“The real challenge, honestly speaking, was *mastering the Chinese language.*”"), (2.95, 5.4, "“All the switches, all the software…”"),
                   (5.4, 8.0, "“…all the programs, all the voice announcements…”"), (8.0, D + 1, "“…*everything is in Chinese.*”")], 58)
    srcline(d, "Dawn · Reuters · Arab News"); chrome(im, KK, ACC)
P0, P1, P2 = (230, 1162), (290, 880), (850, 905)
def bez(u): return tuple((1 - u) ** 2 * P0[k] + 2 * (1 - u) * u * P1[k] + u ** 2 * P2[k] for k in range(2))
def station(d, x, y, a):
    c = mix(a, (225, 230, 240)); p = mix(a, (60, 120, 210))
    d.rectangle([x - 26, y - 8, x + 26, y + 8], fill=c); d.rectangle([x - 6, y - 16, x + 6, y + 16], fill=c)
    for sx in (-1, 1): d.rectangle([x + sx * 34 - 12, y - 26, x + sx * 34 + 12, y + 26], fill=p, outline=c)
def s_journey(im, t, D):
    stars(im, t); earth(im, t, D=D); d = ImageDraw.Draw(im)
    y = label(d, 170, "THE JOURNEY · 25 NOVEMBER", GOLD, t)
    y = rise(d, 40, y, "First foreign astronaut on *Tiangong*", HK(74), t, .1, maxw=880, lh=84) + 34
    facts = [(1.0, "Lift-off 5:18am Pakistan time, Jiuquan, China"), (2.0, "Long March-2F rocket, Shenzhou-24")]
    for s0, s_ in facts:
        a = ease(seg(t, s0, s0 + .45)); dx = int(40 * (1 - a))
        d.ellipse([44 + dx, y + 14, 60 + dx, y + 30], fill=mix(a, ACC)); d.text((80 + dx, y), s_, font=TX(40, "Bold"), fill=mix(a, INK)); y += 72
    a = ease(seg(t, 3.0, 3.4)); m = int(round(218 * ease(seg(t, 3.0, 5.0))))
    if a > 0:
        d.text((40, y + 14), f"{m // 60} h {m % 60:02d} min", font=HK(96), fill=mix(a, GOLD)); d.text((44, y + 130), "from lift-off to docking", font=TX(36), fill=mix(a, SOFT))
    u = ease(seg(t, 1.0, 5.0)); pts = [bez(k / 80 * u) for k in range(81)]
    if u > 0:
        for k in range(0, 80, 2): d.line([pts[k], pts[k + 1]], fill=(150, 200, 255), width=4)
        x, yb = pts[-1]; d.ellipse([x - 9, yb - 9, x + 9, yb + 9], fill=GOLD)
    sa = ease(seg(t, .6, 1.2)); station(d, P2[0] + 10, P2[1] - 6 + int(4 * math.sin(t * 2)), sa)
    if u >= 1:
        k = ease(seg(t, 5.0, 5.4)); d.ellipse([P2[0] - 40 * k + 10, P2[1] - 46 * k, P2[0] + 40 * k + 10, P2[1] + 34 * k], outline=mix(1 - k * .7, GOLD), width=3)
    d.text((P0[0] - 60, P0[1] + 18), "JIUQUAN", font=TX(22, "Bold"), fill=SOFT); d.text((P2[0] - 70, P2[1] + 40), "TIANGONG", font=TX(22, "Bold"), fill=mix(sa, SOFT))
    srcline(d, "Dawn · Reuters · Arab News"); chrome(im, KK, ACC)
def s_train(im, t, D):
    y = stage(im, S_TRAIN, B_TRAIN[1] + t, CAP, zoom=1.05 - .05 * t / D); d = ImageDraw.Draw(im)
    y = label(d, y + 26, "ON HIS TRAINING", GOLD, t)
    subs(d, y, t, [(0, 3.0, "“Being a fighter pilot, *I've been going through the training*…”"), (3.0, 5.7, "“…like *centrifuge training*…”"),
                   (5.7, 7.1, "“…like *rescue and survival training*…”"), (7.1, D + 1, "“…like *emergency procedure training*.”")], 58)
    chrome(im, "TRAINING", GOLD)
WHO = [("40", "years old, a fighter pilot"), (None, "Wing Commander"), (None, "Payload specialist on Shenzhou-24, with China's Tang Hongbo and Wu Yi"),
       ("7 months", "of training in Beijing, with intensive Chinese classes")]
def s_who(im, t, D):
    stars(im, t, speed=3, dim=.7); earth(im, t, EARTH2, 0, D); d = ImageDraw.Draw(im)
    y = label(d, 170, "WHO IS HE", GOLD, t); y = rise(d, 40, y, "Muhammad *Zeeshan Ali*", HK(76), t, .1, maxw=900) + 30
    for i, (big, s_) in enumerate(WHO):
        a = back(seg(t, .8 + i * .9, 1.4 + i * .9)); al = ease(seg(t, .8 + i * .9, 1.2 + i * .9)); sd = 1 if i % 2 == 0 else -1; dx = int(sd * 700 * (1 - a))
        bx = 0
        tf = TX(38, "Bold") if big else HX(52); ls = wrap(tf, s_, W - 160 - (0 if not big else 0))
        hh = (84 if big else 0) + len(ls) * (48 if big else 62) + 46
        if al > 0:
            card(im, (40 + dx, y, W - 40 + dx, y + hh), al, outline=PKG if i % 2 == 0 else GOLD); d = ImageDraw.Draw(im)
            d.rectangle([40 + dx, y + 20, 48 + dx, y + hh - 20], fill=mix(al, GOLD if i % 2 else ACC, CARD)); yy = y + 22
            if big: d.text((76 + dx, yy - 6), big, font=HK(78), fill=mix(al, GOLD, CARD)); yy += 84
            for ln in ls: d.text((76 + dx, yy), ln, font=tf, fill=mix(al, INK if not big else SOFT, CARD)); yy += 48 if big else 62
        y += hh + 20
    srcline(d, "Dawn · Reuters · Arab News"); chrome(im, KK, ACC)
def ic_algae(d, x, y, a):
    for cx, cy, r in [(0, 0, 22), (26, -14, 14), (24, 20, 16), (-22, 22, 12), (-20, -20, 11)]:
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r], fill=mix(a, (40, 190, 110), CARD), outline=mix(a, (170, 240, 190), CARD), width=2)
def ic_seed(d, x, y, a):
    for cx, cy in [(-20, -14), (12, -20), (-6, 10), (24, 12), (-28, 22)]:
        d.ellipse([x + cx - 13, y + cy - 10, x + cx + 13, y + cy + 10], fill=mix(a, (230, 205, 150), CARD), outline=mix(a, (160, 130, 80), CARD), width=2)
def ic_mat(d, x, y, a):
    hx = [(x + 34 * math.cos(math.radians(60 * k)), y + 34 * math.sin(math.radians(60 * k))) for k in range(6)]
    d.polygon(hx, outline=mix(a, BLUE, CARD), width=5)
    d.line([(x - 10, y - 20), (x + 2, y - 2), (x - 6, y + 8), (x + 8, y + 24)], fill=mix(a, GOLD, CARD), width=4)
EXP = [(ic_algae, "Microalgae: a possible source of food and oxygen"), (ic_seed, "Quinoa seeds: what spaceflight does to them"), (ic_mat, "A material that repairs itself when damaged")]
def s_exp(im, t, D):
    stars(im, t, speed=-4, dim=.8); d = ImageDraw.Draw(im)
    y = label(d, 170, "WHAT PAKISTAN SENT UP", GOLD, t)
    a = ease(seg(t, .1, .5)); n = min(4, 1 + int(4 * seg(t, .2, 1.4)))
    d.text((40, y + int(18 * (1 - a))), f"{n} experiments", font=HK(100), fill=mix(a, INK)); y += 124
    y = rise(d, 40, y, "chosen from about *300 proposals*", TX(42, "Bold"), t, .9, col=SOFT) + 46
    for i, (ic, s_) in enumerate(EXP):
        s0 = 2.0 + i * 1.5; al = ease(seg(t, s0, s0 + .5)); dy = int(40 * (1 - al)); ls = wrap(TX(42, "Bold"), s_, W - 290); hh = max(150, 50 + len(ls) * 54)
        if al > 0:
            card(im, (40, y + dy, W - 40, y + dy + hh), al); d = ImageDraw.Draw(im)
            sc = .6 + .4 * back(seg(t, s0, s0 + .6)); r = int(62 * sc); cx, cy = 140, y + dy + hh // 2
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(al, (14, 20, 32), CARD)); ic(d, cx, cy, al)
            ty = y + dy + (hh - len(ls) * 54) // 2 - 4
            for j, ln in enumerate(ls): d.text((236, ty + j * 54), ln, font=TX(42, "Bold"), fill=mix(al, INK, CARD))
        y += hh + 24
    srcline(d, "Dawn · Reuters · Arab News · Geo"); chrome(im, "THE SCIENCE", GOLD)
def s_part(im, t, D):
    y = stage(im, S_PART, B_PART[1] + t, CAP, zoom=1 + .05 * t / D); d = ImageDraw.Draw(im)
    y = label(d, y + 26, "ON HIS CREWMATES", GOLD, t)
    subs(d, y, t, [(0, 3.3, "“I consider myself lucky enough to get *the best partners*…”"), (3.3, 6.4, "“…who not only understand me and *respect my opinion*…”"),
                   (6.4, D + 1, "“…and then collectively reach a common response to *any situation.*”")], 58)
    chrome(im, "THE CREW", ACC)
def s_next(im, t, D):
    stars(im, t, speed=8); earth(im, t, EARTH, 60, D); d = ImageDraw.Draw(im)
    y = label(d, 170, "WHAT HAPPENS NEXT", GOLD, t) + 130
    for i, (big, cap, col) in enumerate([("5 to 10 days", "expected stay on the station", GOLD), ("Shenzhou-23", "the spacecraft that brings him home", ACC)]):
        s0 = .3 + i * 1.6; a = ease(seg(t, s0, s0 + .5)); sc = back(seg(t, s0, s0 + .6))
        f = HK(int(116 * max(.3, sc))) if sc < 1 else HK(116)
        if a > 0:
            d.rectangle([40, y + 10, 40 + int(10 * a), y + 230], fill=col)
            d.text((76, y + int(20 * (1 - a))), big, font=HK(116), fill=mix(a, col)); d.text((80, y + 150), cap, font=TX(42, "Bold"), fill=mix(ease(seg(t, s0 + .3, s0 + .8)), INK))
        y += 300
    srcline(d, "Dawn · Reuters · TVB News"); chrome(im, KK, ACC)
TE = bl(B_END)
def end_card(im, t):
    stars(im, t + 20, speed=5); earth(im, t, EARTH2, 30, 3.5); d = ImageDraw.Draw(im)
    c = ease(seg(t, .15, .75)); lg = LOGO_IM.resize((150, 150), Image.LANCZOS); y = 470 + int(30 * (1 - c))
    im.paste(fadeimg(lg, c), ((W - 150) // 2, y), fadeimg(lg, c)); f = HX(58); s_ = "thepakistandaily.com"
    d.text(((W - tw(f, s_)) // 2, y + 190), s_, font=f, fill=mix(ease(seg(t, .4, 1.0)), INK, (10, 14, 28)))
def s_end(im, t, D):
    if t < TE + .3:
        y = stage(im, S_END, B_END[1] + min(t, TE - 1 / FPS), CAP, zoom=1 + .05 * t / TE); d = ImageDraw.Draw(im)
        y = label(d, y + 26, "ON PAKISTAN AND CHINA", GOLD, t)
        subs(d, y, t, [(0, 2.3, "“This cooperation and coordination and friendship…”"), (2.3, TE + 1, "“…*represents the friendship between Pakistan and China.*”")], 58)
        chrome(im, KK, ACC)
        if t > TE:
            e = BGI.copy(); end_card(e, t - TE); k = ease((t - TE) / .3); im.paste(Image.blend(im, e, k))
    else: end_card(im, t - TE)
SCENES = [("open", bl(B_OPEN), s_open), ("journey", 7.0, s_journey), ("train", bl(B_TRAIN), s_train), ("who", 7.0, s_who), ("exp", 8.5, s_exp),
          ("part", bl(B_PART), s_part), ("next", 6.0, s_next), ("end", TE + 3.5, s_end)]
SH = Show(SCENES)
def cover(path):
    import subprocess
    raw = os.path.join(SCR, "cover_src.png"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "3.0", "-i", V, "-frames:v", "1", "-vf", "crop=688:860:16:20,scale=1080:1350:flags=lanczos,unsharp=5:5:0.6", raw], check=True)
    im = Image.open(raw).convert("RGB"); 
    g = Image.fromarray(np.clip((np.clip((np.linspace(0, 1, H) - .45) / .4, 0, 1) ** 1.2 * 245), 0, 255).astype(np.uint8)[:, None].repeat(W, 1), "L"); im.paste(BGI, (0, 0), g)
    im.paste(BLACK, (0, 0), _topmask); d = ImageDraw.Draw(im)
    im.paste(LOGO_IM.resize((64, 64), Image.LANCZOS), (40, 44)); d.text((120, 56), "THE PAKISTAN DAILY", font=HX(34), fill=INK)
    f = HK(80); ls = wrap(f, "Pakistan's first astronaut is aboard China's space station", 900); y = H - 110 - len(ls) * 90 - 70
    d.rectangle([40, y - 30, 160, y - 22], fill=ACC)
    for ln in ls: d.text((40, y), ln, font=f, fill=INK); y += 90
    d.text((42, y + 14), "What Zeeshan Ali is doing up there", font=TX(42, "Bold"), fill=GOLD)
    fc = TX(22); c = "Video: @PakinFrance on X"; d.text((W - 40 - tw(fc, c), H - 44), c, font=fc, fill=SOFT)
    im.save(path)
if __name__ == "__main__":
    if sys.argv[1] == "stills": SH.stills(SCR, list(map(float, sys.argv[2:]))); sys.exit()
    if sys.argv[1] == "cover": cover(sys.argv[2]); sys.exit()
    bites = [B_OPEN + (SH.start("open"),), B_TRAIN + (SH.start("train"),), B_PART + (SH.start("part"),), B_END + (SH.start("end"),)]
    print({n: round(SH.start(n), 2) for n, _, _ in SCENES}, SH.DUR)
    SH.render(sys.argv[1], sys.argv[2], SCR, os.path.join(HERE, "audio/Nonstop.mp3"), bites, [], mvol=(.07, .28))
