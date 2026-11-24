"""TPD: Musadik Malik in New Delhi — SCO forum. Usage: render23.py reel|x out.mp4 | render23.py reel|x stills t..."""
import os, sys, math, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from render2 import clamp, ease, seg, tw, wrap, LOGO_IM, fadeimg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "geo")); import mapdata

HERE = os.path.dirname(os.path.abspath(__file__)); FT = os.path.join(HERE, "footage/fz"); VO = os.path.join(HERE, "vo/nq")
SCR = "/tmp/claude-0/-home-claude/60efd90f-1914-5c23-b412-fb0172b38646/scratchpad/p25"
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
            vf = f"crop={self.crop},fps={FPS}"
            self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{idx / FPS:.3f}", "-i", self.path, "-vf", vf,
                                       "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); self.next = idx
        b = self.p.stdout.read(self.w * self.h * 3); self.next += 1
        return Image.frombytes("RGB", (self.w, self.h), b) if len(b) == self.w * self.h * 3 else Image.new("RGB", (self.w, self.h), BG)

MH = int(CH * (.56 if R else .50))
def mk(name, crop): return Clip(fp(name), crop + f",scale={W}:{MH}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{MH}", W, MH)
C_TODAY = mk("today.mp4", "iw:ih:0:0"); C_SIEGE = mk("siege.mp4", "320:220:0:180"); C_UDD = mk("udd.mp4", "iw:ih:0:0")
C_POW = mk("power.mp4", "iw:ih:0:0"); C_POWZ = mk("power.mp4", "640:360:420:120"); C_NA1 = mk("na1.mp4", "1080:660:0:640"); C_NA2 = mk("na2.mp4", "1080:660:0:640")
NQ = os.path.join(HERE, "footage/nq")
def mk2(p, crop): return Clip(os.path.join(NQ, p), crop + f",scale={W}:{MH}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{MH}", W, MH)
C_RANA = mk2("rs3.mp4", "360:246:15:90"); C_SEN = mk2("nq4.mp4", "960:660:60:360")

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


KK = "FAZL UNDER SIEGE"
B_TODAY = (fp("today.mp4"), 51.0, 71.4); B_UDD = (fp("udd.mp4"), 0.0, 9.4); B_POW = (fp("power.mp4"), 0.0, 19.2)
def s_open(im, t, D):
    if 8.0 <= t < 14.0: v = C_SIEGE.frame(t - 8.0); cap = "Outside Fazl's residence, 24 Nov · Video: Sabir Shakir on X"
    else: v = C_TODAY.frame(B_TODAY[1] + t); cap = "Fazl's video message, 24 Nov · Video: @MoulanaOfficial"
    y = med(im, v, t, cap, reveal=False) + 24; d = ImageDraw.Draw(im)
    y = kick(d, y, "LAHORE · 24 NOVEMBER", RED)
    subs(d, y, t, [(0, 4.4, "“I regret to say that right now…”"), (4.4, 8.2, "“…I am under a state siege.”"),
                   (8.2, 14.0, "“The whole city of Lahore is filled with state barriers.”"), (14.0, 21, "“All roads are closed. Checkpoints everywhere.”")], 50)
    chrome(im, KK, "")
def counter(d, x, y, t, s0, val, suf, lab, col, pre=""):
    b = ease(seg(t, s0, s0 + 1.3)); n = int(val * b)
    d.text((x, y), f"{pre}{n:,}{suf}", font=HK(int(80 * S)), fill=mix(min(1, b * 3), col))
    for j, ln in enumerate(wrap(TX(int(25 * S), "SemiBold"), lab, W // 2 - 70)): d.text((x, y + int(96 * S) + j * int(32 * S)), ln, font=TX(int(25 * S), "SemiBold"), fill=mix(min(1, b * 3), SOFT))
def s_facts(im, t, D):
    v = C_SIEGE.frame(14 + t * .8) if t < 4.5 else C_TODAY.frame(200 + t); y = med(im, v, t, "Video: Sabir Shakir on X · @MoulanaOfficial", reveal=t < 1) + 24; d = ImageDraw.Draw(im)
    y = kick(d, y, "WHAT HAPPENED")
    counter(d, 40, y, t, .3, 3000, "", "police outside his house, a petition in the Lahore High Court claims", RED, "~")
    counter(d, W // 2 + 20, y, t, 1.6, 144, "", "Section 144 in Lahore, 24 to 26 Nov: no gatherings of 5 or more", GOLD, "§")
    y += int(200 * S)
    para(d, y, t, "He was due to address an all-parties lawyers' seminar at the Lahore High Court Bar. He couldn't get there.", 3.6, 29, INK)
    chrome(im, KK, "Dawn · @MoulanaOfficial")
EVENTS = [("MID-OCT", "Fazl attacks governor's rule in KP", .4), ("OCT 28", "In the NA: “If I weren't with you, you'd be blown away”", 1.8),
          ("LAST WEEK", "His security withdrawn in Islamabad and DI Khan, JUI-F says", 3.2), ("MON 23 NOV", "JUI-F workers arrested in several cities, party says", 4.6), ("TUE 24 NOV", "House cordoned in Lahore", 6.0)]
def s_time(im, t, D):
    d = ImageDraw.Draw(im); y = kick(d, Y0, "HOW WE GOT HERE"); y += 10
    x0 = 70; gap = int((CH - 160) / len(EVENTS)); p = ease(seg(t, .2, 6.6))
    d.line([(x0, y + 14), (x0, y + 14 + (len(EVENTS) - 1) * gap * p)], fill=(60, 72, 92), width=4)
    for i, (dt, s_, s0) in enumerate(EVENTS):
        b = ease(seg(t, s0, s0 + .5)); yy = y + i * gap; last = i == len(EVENTS) - 1
        c = RED if last else ACC; r = 14 if not last else 14 + 6 * abs(math.sin(t * 3))
        d.ellipse([x0 - r, yy + 14 - r, x0 + r, yy + 14 + r], fill=mix(b, c))
        d.text((x0 + 40, yy - 4), dt, font=TX(int(24 * S), "Bold"), fill=mix(b, c))
        for j, ln in enumerate(wrap(TX(int(31 * S), "Bold"), s_, W - x0 - 90)[:2]): d.text((x0 + 40 + int(30 * (1 - b)), yy + int(34 * S) + j * int(40 * S)), ln, font=TX(int(31 * S), "Bold"), fill=mix(b, INK))
    chrome(im, KK, "Dawn · National Assembly")
def s_udd(im, t, D):
    bite(im, t, C_UDD, B_UDD[1], "National Assembly, 28 Oct · Video: Exact Press Intl on X", "FAZL TO THE STATE, ON TERRORISM",
         [(0, 2.4, "“And you taunt me?”"), (2.4, 6.3, "“If I weren't with you on this front…”"), (6.3, 10, "“…you would have been blown away. Not even seen.”")], KK, col=RED)
def s_pow(im, t, D):
    c = C_POW if t < 9.5 else C_POWZ
    bite(im, t, c, B_POW[1], "21 Nov · Video: Sabir Shakir on X", "FAZL, ON WHO REALLY HOLDS POWER",
         [(0, 9.5, "“All the blame is put on politicians…”"), (9.5, 20, "“…but they ride a horse whose reins are never in their hands.”")], KK, col=GOLD)
def s_rana(im, t, D):
    if t < 5: v = C_RANA.frame(20 + t); cap = "Rana Sanaullah (file) · Video: Geo News"
    else: v = C_SEN.frame(10 + t); cap = "Mohsin Naqvi (file) · Video: Express Tribune on X"
    y = med(im, v, t, cap, reveal=t < 1) + 24; d = ImageDraw.Draw(im)
    y = kick(d, y, "MEANWHILE, LAST NIGHT", SAF)
    y = big(d, y, t, "Rana Sanaullah hits back at Mohsin Naqvi", .2, 48) + 12
    for s_, s0 in [("“Threats won't silence me.”", 2.0), ("Calls Naqvi's handling of new provinces a “total failure”", 4.5)]:
        b = ease(seg(t, s0, s0 + .5)); f = TX(int(30 * S), "Bold"); ls = wrap(f, s_, W - 130)
        d.ellipse([46, y + 12, 62, y + 28], fill=mix(b, SAF))
        for j, ln in enumerate(ls): d.text((84, y + j * int(38 * S)), ln, font=f, fill=mix(b, INK))
        y += len(ls) * int(38 * S) + 14
    chrome(im, "PRESSURE", "Samaa · Express Tribune · Geo · Dawn")
CORN = [("PML-N", "Rana Sanaullah vs Mohsin Naqvi", (0, 140, 70)), ("PPP", "Opposes new provinces and a referendum", (200, 40, 50)),
        ("JUI-F", "Fazl says he is under “state siege”", (40, 120, 200)), ("PTI", "Its KP government replaced by governor's rule", (230, 60, 60))]
def s_corners(im, t, D):
    d = ImageDraw.Draw(im); y = kick(d, Y0, "ANALYSIS", GOLD)
    y = big(d, y, t, "Pressure from every corner", .1, 54) + 20
    cx, cy = W // 2, y + int(CH * .32); R_ = int(min(W, CH) * .30)
    b0 = ease(seg(t, .3, .9)); rr = 120 + 6 * math.sin(t * 4)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=mix(b0, (36, 44, 58)), outline=mix(b0, GOLD), width=4)
    for j, ln in enumerate(["THE", "ESTABLISHMENT"]): f = TX(int(22 * S), "Bold"); d.text((cx - tw(f, ln) // 2, cy - 30 + j * int(32 * S)), ln, font=f, fill=mix(b0, INK))
    pos = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for i, ((nm, s_, c), (px_, py_)) in enumerate(zip(CORN, pos)):
        b = ease(seg(t, 1.0 + i * 1.2, 1.6 + i * 1.2)); bx = cx + px_ * (W // 2 - 250) ; by = cy + py_ * int(R_ * .95)
        ex = cx + px_ * int(rr * .8); ey = cy + py_ * int(rr * .8)
        d.line([(bx, by), (bx + (ex - bx) * b, by + (ey - by) * b)], fill=mix(b, c), width=6)
        w_, h_ = 420, int(150 * S); x1 = bx - w_ // 2; y1 = by - h_ // 2
        d.rounded_rectangle([x1, y1, x1 + w_, y1 + h_], radius=14, fill=mix(b, (24, 32, 46)), outline=mix(b, c), width=3)
        d.text((x1 + 18, y1 + 12), nm, font=HK(int(36 * S)), fill=mix(b, c))
        for j, ln in enumerate(wrap(TX(int(23 * S), "SemiBold"), s_, w_ - 36)[:3]): d.text((x1 + 18, y1 + int(58 * S) + j * int(29 * S)), ln, font=TX(int(23 * S), "SemiBold"), fill=mix(b, INK))
    para(d, cy + R_ + int(110 * S), t, "Is Pakistan's entire political order realigning?", 6.2, 34, GOLD)
    chrome(im, "ANALYSIS", "Dawn · Geo · Express Tribune · Samaa")
def s_end(im, t, D):
    v = C_NA1.frame(26 + t); v = Image.blend(v, Image.new("RGB", v.size, BG), .45); y = med(im, v, 9, "Video: Hamariweb on X") + 30; d = ImageDraw.Draw(im)
    y = big(d, y, t, "Sargodha next: JUI-F rally on 26 November", .1, 50, INK)
    c = ease(seg(t, 2.4, 3.0)); ly = y + int(50 * S); lg = LOGO_IM.resize((110, 110), Image.LANCZOS)
    im.paste(fadeimg(lg, c), (40, ly), fadeimg(lg, c)); d.text((170, ly + 34), "thepakistandaily.com", font=HX(40), fill=mix(c, INK))
def bl(b): return b[2] - b[1]
SCENES = [("open", bl(B_TODAY), s_open), ("facts", 9.0, s_facts), ("time", 9.0, s_time), ("udd", bl(B_UDD), s_udd), ("pow", bl(B_POW), s_pow),
          ("rana", 8.5, s_rana), ("corners", 10.5, s_corners), ("end", 6.0, s_end)]
STARTS = np.cumsum([0] + [D for _, D, _ in SCENES]).tolist(); TR = .3
_ix = {n: i for i, (n, _, _) in enumerate(SCENES)}
NARR = []; VO_AT = {}
BITES = [(b[0], b[1], b[2], STARTS[_ix[n]]) for n, b in [("open", B_TODAY), ("udd", B_UDD), ("pow", B_POW)]]
MUSIC = os.path.join(HERE, "audio/DarkTimes.mp3")
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
        for s in map(float, sys.argv[3:]): at(s).save(os.path.join(HERE, f"v25{MODE}_{s:05.1f}.png"))
        sys.exit()
    out = sys.argv[2]; os.makedirs(SCR, exist_ok=True); parts = []
    for i in range(len(SCENES)):
        p = os.path.join(SCR, f"{MODE}_{i}_{SCENES[i][0]}.mp4"); render_scene(i, p); parts.append(p)
    lst = os.path.join(SCR, f"{MODE}_list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    silent = os.path.join(SCR, f"{MODE}_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    DUR = STARTS[-1]
    names = list(VO_AT.keys()); ins = ["-i", silent, "-i", os.path.join(HERE, "audio/DarkTimes.mp3")]
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
