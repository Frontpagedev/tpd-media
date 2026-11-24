"""TPD: Musadik Malik in New Delhi — SCO forum. Usage: render23.py reel|x out.mp4 | render23.py reel|x stills t..."""
import os, sys, math, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from render2 import clamp, ease, seg, tw, wrap, LOGO_IM, fadeimg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "geo")); import mapdata

HERE = os.path.dirname(os.path.abspath(__file__)); FT = os.path.join(HERE, "footage/mm"); VO = os.path.join(HERE, "vo/mm")
SCR = "/tmp/claude-0/-home-claude/60efd90f-1914-5c23-b412-fb0172b38646/scratchpad/p23"
FPS = 30
BG = (10, 14, 20); BG2 = (20, 30, 44); INK = (244, 246, 250); SOFT = (176, 186, 204); DIM = (92, 104, 128)
ACC = (0, 170, 110); GOLD = (232, 190, 96); SAF = (255, 153, 51); RED = (225, 60, 60); CYAN = (80, 190, 230)
ID = "/usr/share/fonts/opentype/inter/"
_f = {}
def F(n, s):
    k = (n, s)
    if k not in _f: _f[k] = ImageFont.truetype(ID + n, s)
    return _f[k]
HK = lambda s: F("InterDisplay-Black.otf", s); HX = lambda s: F("InterDisplay-ExtraBold.otf", s)
TX = lambda s, w="Medium": F(f"Inter-{w}.otf", s)
LORA = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)
def mix(a, c, bg=BG): return tuple(int(bg[j] + (c[j] - bg[j]) * clamp(a)) for j in range(3))

MODE = sys.argv[1] if len(sys.argv) > 1 else "reel"; R = MODE == "reel"
if R: W, H = 1080, 1920; TOP = 196; Y0 = 290; Y1 = 1610; SRC = 1640
else: W, H = 1080, 1350; TOP = 24; Y0 = 100; Y1 = 1280; SRC = 1305
CH = Y1 - Y0; S = 1.22 if R else .9

_g = np.linspace(0, 1, H)[:, None, None]
BGIMG = Image.fromarray((np.array(BG) * (1 - _g) + np.array(BG2) * _g).repeat(W, 1).astype(np.uint8))
rng = np.random.default_rng(23); PART = rng.random((110, 4))
def background(t):
    im = BGIMG.copy(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, sp, sz in PART:
        px = (x * W + t * (6 + sp * 16)) % W; py = (y * H + math.sin(t * .4 + x * 9) * 30) % H; r = 1.5 + sz * 3.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=(170, 190, 210, int(8 + sp * 18)))
    im.paste(lay, (0, 0), lay); return im

def fp(n): return os.path.join(FT, n)
IMG = {k: Image.open(fp(v)).convert("RGB") for k, v in {"open": "ph_3685_0.jpg", "taj": "ph_0964_2.jpg", "iran": "ph_6069_0.jpg", "aze": "ph_2142_0.jpg", "aud": "ph_3685_1.jpg"}.items()}
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
            vf = f"crop={self.crop},fps={FPS}"
            self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{idx / FPS:.3f}", "-i", self.path, "-vf", vf,
                                       "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); self.next = idx
        b = self.p.stdout.read(self.w * self.h * 3); self.next += 1
        return Image.frombytes("RGB", (self.w, self.h), b) if len(b) == self.w * self.h * 3 else Image.new("RGB", (self.w, self.h), BG)

MH = int(CH * (.56 if R else .50))
def mk(name, crop): return Clip(fp(name), crop + f",scale={W}:{MH}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{MH}", W, MH)
C_GHALIB = mk("ghalib.mp4", "iw:ih:0:0"); C_MEDIA = mk("media720.mp4", "720:600:0:60"); C_ARRIVE = mk("arrive.mp4", "1100:620:0:100")
C_HOMAGE = mk("homage.mp4", "iw:ih:0:0"); C_MOH = mk("mohenjo.mp4", "iw:ih:0:0"); C_QILA = mk("qila.mp4", "iw:ih:0:0")
C_PANAH = mk("panah.mp4", "iw:ih:0:0"); C_AANA = mk("aana.mp4", "iw:ih:0:0"); C_MODI = mk("modi.mp4", "iw:ih:0:0"); C_CHAT = mk("chat.mp4", "iw:ih:0:0")

def chrome(im, kicker, src):
    d = ImageDraw.Draw(im)
    im.paste(LOGO_IM.resize((50, 50), Image.LANCZOS), (40, TOP))
    d.text((104, TOP + 7), "THE PAKISTAN DAILY", font=HX(28), fill=INK)
    if kicker:
        f = TX(22, "Bold"); kw = tw(f, kicker) + 30
        d.rounded_rectangle([W - 40 - kw, TOP + 6, W - 40, TOP + 46], radius=8, fill=ACC); d.text((W - 40 - kw + 15, TOP + 13), kicker, font=f, fill=BG)
    if src: d.text((40, SRC), "SOURCES: " + src, font=TX(18, "SemiBold"), fill=DIM)
def rise(d, x, y, text, font, t, start=0, col=INK, maxw=None, lh=None):
    ls = wrap(font, text, maxw or W - 80); lh = lh or int(font.size * 1.18)
    for i, ln in enumerate(ls):
        a = ease(seg(t, start + i * .1, start + i * .1 + .5))
        if a > 0: d.text((x, y + i * lh + int(16 * (1 - a))), ln, font=font, fill=mix(a, col))
    return y + len(ls) * lh
def caption(img, text):
    d = ImageDraw.Draw(img); f = TX(18); w_ = tw(f, text) + 26
    d.rectangle([img.width - w_, img.height - 32, img.width, img.height], fill=(0, 0, 0)); d.text((img.width - w_ + 13, img.height - 27), text, font=f, fill=(225, 220, 214))
def med(im, ph, t, cap=None, y=None, reveal=True):
    y = Y0 if y is None else y
    if cap: caption(ph, cap)
    a = ease(clamp(t / .4)) if reveal else 1; hh = max(1, int(ph.height * a)); im.paste(ph.crop((0, 0, ph.width, hh)), (0, y)); return y + ph.height
def kick(d, y, s, col=ACC): d.text((40, y), s, font=TX(26, "Bold"), fill=col); return y + 44
def big(d, y, t, s, st=.2, size=52, col=INK): return rise(d, 40, y, s, HX(int(size * S)), t, st, col)
def para(d, y, t, s, st=.8, size=31, col=SOFT): return rise(d, 40, y, s, TX(int(size * S), "SemiBold"), t, st, col)
def subs(d, y, t, items, size=46, col=INK):
    for a0, a1, s in items:
        if a0 <= t < a1:
            f = HX(int(size * S))
            for i, ln in enumerate(wrap(f, s, W - 80)): d.text((40, y + i * int(f.size * 1.15)), ln, font=f, fill=col)
def photo(key, t, D, focus=(.5, .5), z0=1.0, z1=1.08, h=None): return cover(key, W, h or MH, z0 + (z1 - z0) * clamp(t / max(D, .1)), focus)
def bite(im, t, clip, t0, cap, label, items, kk, src="", col=ACC):
    v = clip.frame(t0 + t); y = med(im, v, t, cap, reveal=False) + 26; d = ImageDraw.Draw(im)
    y = kick(d, y, label, col); subs(d, y, t, items); chrome(im, kk, src)

# ---------------- audio pieces ----------------
NARR = ["intro", "climate", "floods", "proposals", "media", "india", "pak", "sco", "summit", "end"]
VOD = {k: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(VO, k + ".mp3")], capture_output=True, text=True).stdout) for k in NARR}
B_GHALIB = (fp("ghalib.mp4"), 0.0, 17.7)
B_AANA = (fp("aana.mp4"), 11.2, 15.4)
B_MODI = (fp("modi.mp4"), 0.0, 4.9)
BX = json.load(open(os.path.join(HERE, "r23_bites.json"))) if os.path.exists(os.path.join(HERE, "r23_bites.json")) else {}
B_ENEMY = tuple(BX.get("enemy", [fp("qila.mp4"), 10.0, 16.0])); B_MONS = tuple(BX.get("mons", [fp("mohenjo.mp4"), 10.0, 16.0]))

KK = "MALIK IN DELHI"
# ---------------- scenes ----------------
def s_open(im, t, D):
    v = C_MEDIA.frame(40 + t); y = med(im, v, t, "Video via X", reveal=False) + 28; d = ImageDraw.Draw(im)
    y = kick(d, y, "NEW DELHI · 20–22 NOVEMBER 2026")
    f = HX(int(58 * S))
    for i, ln in enumerate(wrap(f, "Pakistan's first minister in India since the May 2025 war", W - 80)): d.text((40, y + i * int(f.size * 1.14)), ln, font=f, fill=INK)
    chrome(im, KK, "")

def s_ghalib(im, t, D):
    bite(im, t, C_GHALIB, B_GHALIB[1], "SCO forum, Purana Qila · Video: Sidhant Sibal on X", "DR MUSADIK MALIK · FEDERAL MINISTER",
         [(0, 5.6, "“It felt strange — a few kos from Ghalib's grave —”"), (5.6, 11.3, "“…to sit here and speak to you in English.”"),
          (11.3, 18, "“So I decided to speak to you today in Urdu, the voice of my heart.”")], KK)

def s_intro(im, t, D):
    d = ImageDraw.Draw(im)
    if t < 6.2: v = C_ARRIVE.frame(2 + t); cap = "Arriving at Purana Qila · Video: Senator Musadik Office"
    elif t < 11.6: v = photo("open", t - 6.2, 5.4, (.3, .5), 1.05, 1.16); cap = "Malik at the opening; Modi inaugurated the forum · Photo: Musadik Malik Office"
    else: v = C_HOMAGE.frame(20 + t - 11.6); cap = "Video: Sidhant Sibal on X"
    y = med(im, v, t, cap, reveal=t < 1) + 26
    y = kick(d, y, "THE VISIT")
    y = big(d, y, t, "First SCO Civilisational Dialogue Forum", .2, 50) + 12
    for i, (s, s0) in enumerate([("Purana Qila, New Delhi · on India's invitation", 2.0), ("First Pakistani federal minister in India since Bilawal Bhutto in 2023", 7.0), ("Received by Pakistan's Chargé d'Affaires Saad Warraich", 12.0)]):
        b = ease(seg(t, s0, s0 + .5)); f = TX(int(29 * S), "SemiBold"); ls = wrap(f, s, W - 130)
        d.ellipse([46, y + 12, 62, y + 28], fill=mix(b, ACC))
        for j, ln in enumerate(ls): d.text((84, y + j * int(38 * S)), ln, font=f, fill=mix(b, INK))
        y += len(ls) * int(38 * S) + 16
    chrome(im, KK, "Dawn · Arab News · Outlook · The Nation")

def s_climate(im, t, D):
    v = C_QILA.frame(30 + t); y = med(im, v, t, "Video: Senator Musadik Office") + 26; d = ImageDraw.Draw(im)
    y = kick(d, y, "THE SPEECH · 21 NOVEMBER")
    f = LORA(int(60 * S)); q = "“The enemy of civilisation is not another civilisation. It is climate change.”"
    for i, ln in enumerate(wrap(f, q, W - 80)):
        n = int(len(ln) * clamp((t - .5 - i * .55) / .6))
        if n > 0: d.text((40, y + i * int(f.size * 1.2)), ln[:n], font=f, fill=INK)
    chrome(im, KK, "Dawn · Musadik Malik Office")

def s_enemy(im, t, D):
    bite(im, t, C_ENEMY, B_ENEMY[1], "Video: Senator Musadik Office", "MALIK AT THE FORUM", BX.get("enemy_subs", []), KK)

def counter(d, x, y, t, s0, val, suf, lab, col):
    b = ease(seg(t, s0, s0 + 1.4)); n = int(val * b)
    d.text((x, y), f"{n:,}{suf}", font=HK(int(84 * S)), fill=mix(min(1, b * 3), col))
    d.text((x, y + int(100 * S)), lab, font=TX(int(26 * S), "SemiBold"), fill=mix(min(1, b * 3), SOFT))
def s_floods(im, t, D):
    v = C_MOH.frame(40 + t); y = med(im, v, t, "Video: Senator Musadik Office", reveal=t < 1) + 26; d = ImageDraw.Draw(im)
    y = kick(d, y, "PAKISTAN'S 2022 FLOODS", CYAN)
    counter(d, 40, y, t, .4, 1700, "+", "people killed", INK); counter(d, W // 2 + 20, y, t, 2.4, 33, "%", "of Pakistan under water", CYAN)
    y += int(160 * S)
    para(d, y, t, "Malik: the ruins of Mohenjo-daro sheltered people fleeing the water.", 5.2, 31, INK)
    chrome(im, KK, "Dawn · UN OCHA · Malik's speech")

PROPS = ["A network of SCO cultural institutions", "A shared digital heritage repository", "A climate-resilient heritage framework"]
def s_proposals(im, t, D):
    d = ImageDraw.Draw(im); y = kick(d, Y0, "MALIK'S THREE PROPOSALS"); y += 10
    for i, s in enumerate(PROPS):
        b = ease(seg(t, .5 + i * 1.1, 1.0 + i * 1.1)); yy = y + i * int(150 * S); hh = int(124 * S)
        d.rounded_rectangle([40 + int(60 * (1 - b)), yy, W - 40, yy + hh], radius=16, fill=mix(b, (24, 36, 52)), outline=mix(b, ACC), width=3)
        d.text((70, yy + int(22 * S)), str(i + 1), font=HK(int(66 * S)), fill=mix(b, ACC))
        for j, ln in enumerate(wrap(TX(int(31 * S), "Bold"), s, W - 230)[:2]): d.text((170, yy + int(26 * S) + j * int(40 * S)), ln, font=TX(int(31 * S), "Bold"), fill=mix(b, INK))
    y += 3 * int(150 * S) + 20
    b = ease(seg(t, 4.2, 4.8)); d.text((40, y), "AND AN INVITATION", font=TX(int(24 * S), "Bold"), fill=mix(b, GOLD))
    big(d, y + int(44 * S), t, "Come to Mohenjo-daro and Harappa", 4.4, 50, INK)
    chrome(im, KK, "Dawn · Musadik Malik Office")

def s_mons(im, t, D):
    bite(im, t, C_MOH, B_MONS[1], "Video: Senator Musadik Office", "MALIK, INVITING DELEGATES TO PAKISTAN", BX.get("mons_subs", []), KK)

def s_media(im, t, D):
    v = C_MEDIA.frame(120 + t); y = med(im, v, t, "Speaking to Indian media · Video via X") + 26; d = ImageDraw.Draw(im)
    y = kick(d, y, "ASKED ABOUT TERRORISM", SAF)
    y = big(d, y, t, "“I do not wish to present a narrative of mere victimhood… thousands of our people have been martyred.”", .4, 40) + 14
    para(d, y, t, "He called for a transparent regional mechanism, based on evidence.", 6.5, 30)
    chrome(im, KK, "Express Tribune · IANS")

def s_aana(im, t, D):
    bite(im, t, C_AANA, B_AANA[1], "Video: WION via Sidhant Sibal on X", "TO AN INDIAN REPORTER",
         [(0, 4.3, "“I hope you won't complain again — and the coming and going continues.”")], KK)

def s_modi(im, t, D):
    bite(im, t, C_MODI, B_MODI[1], "Video: WION via Sidhant Sibal on X", "ON MODI'S SPEECH", BX.get("modi_subs", [(0, 5, "“PM Modi's speech was good.”")]), KK)

def clipping(d, x, y, w, outlet, head, tag, b, col):
    if b <= 0: return y
    f = HX(int(36 * S)); ls = wrap(f, head, w - 60); hh = int(70 * S) + len(ls) * int(44 * S) + 20
    yy = y + int(30 * (1 - b))
    d.rounded_rectangle([x, yy, x + w, yy + hh], radius=14, fill=mix(b, (236, 234, 228)))
    d.rectangle([x, yy, x + 10, yy + hh], fill=mix(b, col))
    d.text((x + 30, yy + 18), outlet, font=TX(int(22 * S), "Bold"), fill=mix(b, (90, 90, 90), (236, 234, 228)))
    if tag:
        ft = TX(int(18 * S), "Bold"); tw_ = tw(ft, tag) + 20
        d.rounded_rectangle([x + w - 24 - tw_, yy + 16, x + w - 24, yy + 16 + int(28 * S)], radius=6, fill=mix(b, col)); d.text((x + w - 14 - tw_, yy + 19), tag, font=ft, fill=(255, 255, 255))
    for j, ln in enumerate(ls): d.text((x + 30, yy + int(56 * S) + j * int(44 * S)), ln, font=f, fill=mix(b, (20, 20, 24), (236, 234, 228)))
    return y + hh + 20

def s_india(im, t, D):
    v = C_CHAT.frame(1 + t * .9); y = med(im, v.filter(ImageFilter.GaussianBlur(0)), t, "Malik and Indian culture minister Gajendra Singh Shekhawat · Video via X", y=Y0, reveal=t < 1)
    y = int(Y0 + MH * (.72 if R else .55)); d = ImageDraw.Draw(im)
    if not R: y = Y0 + MH + 20
    y = kick(d, y + (0 if not R else 0), "HOW INDIA REACTED", SAF) if not R else y
    items = [("OUTLOOK · THE WEEK", "Congress' Tewari and Khurshid: “What has changed since Pahalgam?”", "OPPOSITION", 1.8),
             ("IANS", "Pakistan minister sidesteps questions on terrorism", "NEWS AGENCY", 6.8),
             ("INDIA'S STANDING POSITION", "Indus Waters Treaty remains in abeyance", "MEA", 11.0)]
    for o, h, tg, s0 in items: y = clipping(d, 40, y, W - 80, o, h, tg, ease(seg(t, s0, s0 + .5)), SAF)
    chrome(im, "INDIA REACTS", "Outlook · The Week · Dainik Jagran · IANS · MEA")

def s_pak(im, t, D):
    d = ImageDraw.Draw(im); keys = [("taj", "With Tajikistan's culture minister", (.5, .4)), ("iran", "With Iran's Imanipour", (.45, .4)), ("aze", "With Azerbaijan's Adil Karimli", (.5, .4))]
    if t < 8.0: v = C_PANAH.frame(60 + t); cap = "Video: Senator Musadik Office"
    else:
        k = min(2, int((t - 8.0) / 2.5)); kk, c, fo = keys[k]; tt = t - 8.0 - k * 2.5; v = photo(kk, tt, 2.5, fo, 1.0, 1.1); cap = c + " · Photo: Musadik Malik Office"
    y = med(im, v, t, cap, reveal=t < 1); y = int(Y0 + MH * (.72 if R else .55)) if R else Y0 + MH + 20
    items = [("EXPRESS TRIBUNE · OPINION", "Musadik takes Delhi by storm", "COLUMN", .8), ("EXPRESS TRIBUNE", "Minister schools Indian media over ‘terror mantra’", "NEWS", 4.0),
             ("GEO NEWS", "Musadik urges collective efforts for regional peace", "TV", 7.5)]
    for o, h, tg, s0 in items: y = clipping(d, 40, y, W - 80, o, h, tg, ease(seg(t, s0, s0 + .5)), ACC)
    chrome(im, "PAKISTAN REACTS", "Express Tribune · Geo News · Dawn")

SCO = ["China", "Russia", "India", "Pakistan", "Iran", "Kazakhstan", "Kyrgyzstan", "Tajikistan", "Uzbekistan", "Belarus"]
CTX = ["Afghanistan", "Mongolia", "Turkmenistan", "Ukraine", "Poland", "Turkey", "Saudi Arabia", "Myanmar", "Nepal", "Bangladesh", "Iraq", "Azerbaijan", "Georgia", "Armenia",
       "Finland", "Latvia", "Lithuania", "Estonia", "Romania", "Moldova", "Syria", "Oman", "United Arab Emirates", "Yemen", "Thailand", "Vietnam", "Laos", "North Korea", "South Korea", "Japan", "Bhutan", "Sri Lanka", "Kuwait", "Jordan", "Germany", "Norway", "Sweden", "Slovakia", "Hungary"]
GEO = mapdata.topo_countries(set(SCO + CTX))
LON0, LON1, LAT0, LAT1 = 22, 140, 4, 72
def mp(lon, lat, box):
    x0, y0, w, h = box
    if lon < 0: lon += 360
    lon = min(lon, 180); k = math.cos(math.radians(38))
    sx = min(w / ((LON1 - LON0) * k), h / (LAT1 - LAT0)); cx = (LON0 + LON1) / 2; cy = (LAT0 + LAT1) / 2
    return x0 + w / 2 + (lon - cx) * k * sx, y0 + h / 2 - (lat - cy) * sx
def s_sco(im, t, D):
    d = ImageDraw.Draw(im); y = kick(d, Y0, "THE SHANGHAI COOPERATION ORGANISATION")
    y = big(d, y, t, "10 members. Pakistan holds the chair.", .1, 48) + 10
    box = (0, y, W, int(CH * (.62 if R else .50))); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    order = {n: i for i, n in enumerate(["Pakistan", "China", "Russia", "India", "Iran", "Kazakhstan", "Kyrgyzstan", "Tajikistan", "Uzbekistan", "Belarus"])}
    for n, rings in GEO.items():
        if n in SCO:
            b = ease(seg(t, .8 + order[n] * .35, 1.3 + order[n] * .35)); c = (ACC if n == "Pakistan" else (60, 110, 160))
            fill = tuple(int(42 + (c[j] - 42) * b) for j in range(3)) + (255,)
        else: fill = (36, 44, 58, 255)
        for r in rings:
            pts = [mp(lo, la, box) for lo, la in r]
            if len(pts) > 2: ld.polygon(pts, fill=fill, outline=(14, 18, 26, 255))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([0, box[1], W, box[1] + box[3]], fill=255)
    from PIL import ImageChops; im.paste(lay, (0, 0), ImageChops.multiply(lay.getchannel(3), m))
    px, py = mp(69.3, 30.4, box); p = ease(seg(t, 5.2, 6.0))
    if p > 0:
        r = 18 + 30 * ((t * .8) % 1); d.ellipse([px - r, py - r, px + r, py + r], outline=GOLD, width=3)
        f = TX(int(24 * S), "Bold"); lw = tw(f, "CHAIR SINCE 1 SEPT 2026") + 28; d.rounded_rectangle([px - lw + 40, py + 40, px + 40, py + 40 + int(40 * S)], radius=8, fill=mix(p, GOLD)); d.text((px - lw + 54, py + 46), "CHAIR SINCE 1 SEPT 2026", font=f, fill=BG)
    yy = box[1] + box[3] + 20
    para(d, yy, t, "Pakistan took over the Council of Heads of State chair from Kyrgyzstan after the Bishkek summit.", 6.4, 29, INK)
    chrome(im, "THE SCO", "SCO · Foreign Office · Arab News · Dawn")

def s_summit(im, t, D):
    d = ImageDraw.Draw(im); y = kick(d, Y0, "NEXT SCO SUMMIT", GOLD)
    f = HK(int(118 * S)); s = "ISLAMABAD"; b = ease(seg(t, .2, 1.0))
    d.text((40 + int(40 * (1 - b)), y), s, font=f, fill=mix(b, INK)); y += int(130 * S)
    b2 = ease(seg(t, .9, 1.6)); d.text((40, y), "AUGUST 2027", font=HK(int(78 * S)), fill=mix(b2, GOLD)); y += int(110 * S)
    d.line([(40, y), (40 + (W - 80) * ease(seg(t, 1.4, 2.4)), y)], fill=GOLD, width=3); y += 28
    y = para(d, y, t, "Theme: “Turning Vision into Action: Connectivity, Innovation and Shared Prosperity”", 2.2, 29, SOFT) + 26
    rows = [("INVITATIONS", "Foreign Office: all heads of state, India's included, will be invited", 4.5), ("LAST TIME", "Indian FM Jaishankar came to Islamabad for SCO heads of government, October 2024", 8.0)]
    for k, s_, s0 in rows:
        b = ease(seg(t, s0, s0 + .5)); d.text((40, y), k, font=TX(int(22 * S), "Bold"), fill=mix(b, ACC))
        y = rise(d, 40, y + int(34 * S), s_, TX(int(31 * S), "SemiBold"), t, s0, INK) + 22
    chrome(im, "ISLAMABAD 2027", "Foreign Office · Express Tribune · Arab News · Outlook")

def s_end(im, t, D):
    v = C_GHALIB.frame(60 + t); v = Image.blend(v, Image.new("RGB", v.size, BG), .45); y = med(im, v, 9) + 30; d = ImageDraw.Draw(im)
    y = big(d, y, t, "Will Modi come to Islamabad?", .1, 60, INK)
    c = ease(seg(t, 2.6, 3.2)); ly = y + int(60 * S)
    lg = LOGO_IM.resize((110, 110), Image.LANCZOS); im.paste(fadeimg(lg, c), (40, ly), fadeimg(lg, c))
    d.text((170, ly + 34), "thepakistandaily.com", font=HX(40), fill=mix(c, INK))

P_ = .6
def bl(b): return b[2] - b[1]
SCENES = [("open", 3.4, s_open), ("ghalib", bl(B_GHALIB), s_ghalib), ("intro", VOD["intro"] + P_, s_intro), ("climate", VOD["climate"] + P_, s_climate)]
if "enemy" in BX: SCENES.append(("enemy", bl(B_ENEMY), s_enemy))
SCENES += [("floods", VOD["floods"] + P_, s_floods), ("proposals", max(VOD["proposals"] + P_, 8.5), s_proposals)]
if "mons" in BX: SCENES.append(("mons", bl(B_MONS), s_mons))
SCENES += [("media", VOD["media"] + P_, s_media), ("aana", bl(B_AANA), s_aana), ("india", VOD["india"] + P_, s_india),
           ("pak", VOD["pak"] + P_, s_pak), ("sco", VOD["sco"] + P_, s_sco), ("summit", VOD["summit"] + P_, s_summit), ("end", VOD["end"] + 2.4, s_end)]
STARTS = np.cumsum([0] + [D for _, D, _ in SCENES]).tolist(); TR = .3
_ix = {n: i for i, (n, _, _) in enumerate(SCENES)}
VO_AT = {k: STARTS[_ix[k]] + .2 for k in NARR}
BITES = [(b[0], b[1], b[2], STARTS[_ix[n]]) for n, b in [("ghalib", B_GHALIB), ("enemy", B_ENEMY), ("mons", B_MONS), ("aana", B_AANA), ("modi", B_MODI)] if n in _ix]
MUSIC = os.path.join(HERE, "audio/Impact_Andante.mp3")
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
        for s in map(float, sys.argv[3:]): at(s).save(os.path.join(HERE, f"v23{MODE}_{s:05.1f}.png"))
        sys.exit()
    out = sys.argv[2]; os.makedirs(SCR, exist_ok=True); parts = []
    for i in range(len(SCENES)):
        p = os.path.join(SCR, f"{MODE}_{i}_{SCENES[i][0]}.mp4"); render_scene(i, p); parts.append(p)
    lst = os.path.join(SCR, f"{MODE}_list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    silent = os.path.join(SCR, f"{MODE}_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    DUR = STARTS[-1]
    names = list(VO_AT.keys()); ins = ["-i", silent, "-i", os.path.join(HERE, "audio/Impact_Andante.mp3")]
    for p_, *_ in BITES: ins += ["-i", p_]
    for n in names: ins += ["-i", os.path.join(VO, n + ".mp3")]
    duck = "+".join(f"between(t,{at:.2f},{at + (b1 - b0):.2f})" for _, b0, b1, at in BITES)
    fc = [f"[1:a]atrim=0:{DUR},volume='if({duck or 0},0.06,0.15)':eval=frame,afade=t=in:st=0:d=1,afade=t=out:st={DUR - 3}:d=3[m]"]
    for i, (p_, b0, b1, at) in enumerate(BITES):
        fc.append(f"[{2 + i}:a]atrim={b0}:{b1},asetpts=PTS-STARTPTS,dynaudnorm,volume=1.2,afade=t=in:d=0.12,afade=t=out:st={b1 - b0 - .25:.2f}:d=0.25,adelay={int(at * 1000)}:all=1[b{i}]")
    nb = len(BITES)
    for i, n in enumerate(names): fc.append(f"[{2 + nb + i}:a]volume=1.0,adelay={int(VO_AT[n] * 1000)}:all=1[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(len(names))) + "".join(f"[b{i}]" for i in range(nb)) + f"[m]amix=inputs={len(names) + nb + 1}:duration=longest:normalize=0,atrim=0:{DUR},loudnorm=I=-15:TP=-1.5[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", ";".join(fc),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-t", f"{DUR}",
                    "-movflags", "+faststart", out], check=True)
    print("done", DUR)
