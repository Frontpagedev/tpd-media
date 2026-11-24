"""TPD: Musadik Malik in New Delhi — SCO forum. Usage: render23.py reel|x out.mp4 | render23.py reel|x stills t..."""
import os, sys, math, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from render2 import clamp, ease, seg, tw, wrap, LOGO_IM, fadeimg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "geo")); import mapdata

HERE = os.path.dirname(os.path.abspath(__file__)); FT = os.path.join(HERE, "footage/nq"); VO = os.path.join(HERE, "vo/nq")
SCR = "/tmp/claude-0/-home-claude/60efd90f-1914-5c23-b412-fb0172b38646/scratchpad/p24"
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
C_M = mk("meet0.mp4", "iw:ih:0:0"); C_SEN = mk("nq4.mp4", "960:660:60:360"); C_RANA = mk("rs3.mp4", "360:246:15:90"); C_NADRA = mk("nq1.mp4", "iw:ih:0:0"); C_QAT = mk("nq3.mp4", "iw:ih:0:0"); C_MANS = mk("nq2.mp4", "iw:ih:0:0"); C_MZ = mk("meet0.mp4", "500:282:348:120"); C_MZ2 = mk("meet0.mp4", "500:282:0:110")

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


NARR = list("abcdefg")
VOD = {k: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(VO, k + ".mp3")], capture_output=True, text=True).stdout) for k in NARR}
KK = "NEW PROVINCES"
def vid(c, t, off, cap="Video: @azammaalik on X"): return c.frame((off + t) % 25.5), cap
def s_a(im, t, D):
    if t < 7.5: v = C_SEN.frame(2 + t); cap = "Naqvi in the Senate (file) · Video: Express Tribune on X"
    else: v = C_RANA.frame(4 + t - 7.5); cap = "Rana Sanaullah on Capital Talk (file) · Video: Geo News"
    y = med(im, v, t, cap, reveal=False) + 26; d = ImageDraw.Draw(im)
    y = kick(d, y, "MOHSIN NAQVI · INTERIOR MINISTER · 22 NOV", SAF)
    f = HX(int(50 * S))
    for i, ln in enumerate(wrap(f, "“The day I respond, that minister won't be able to show his face.”", W - 80)): d.text((40, y + i * int(f.size * 1.15)), ln, font=f, fill=INK)
    y += 3 * int(f.size * 1.15) + 20
    para(d, y, t, "He named no one. Rana Sanaullah has criticised Naqvi publicly for two years.", 4.0, 30)
    chrome(im, "NAQVI VS SANAULLAH", "Express · Aaj · WE News · Express Tribune")
def s_b(im, t, D):
    v, cap = vid(C_M, t, 0); y = med(im, v, t, "Naqvi with Ch Shujaat Hussain · Video: @azammaalik on X") + 26; d = ImageDraw.Draw(im)
    y = kick(d, y, "SAME DAY: NAQVI MEETS THE CHAUDHRYS")
    for k, s_, s0 in [("SALIK HUSSAIN", "Accused Maryam Nawaz's Punjab government of corruption", 3.0), ("MARYAM'S REPLY", "Rs5 billion defamation notice", 8.5), ("THE LINK", "Naqvi and the Chaudhrys share family ties", 14.0)]:
        b = ease(seg(t, s0, s0 + .5)); d.text((40, y), k, font=TX(int(22 * S), "Bold"), fill=mix(b, GOLD))
        y = rise(d, 40, y + int(32 * S), s_, TX(int(32 * S), "Bold"), t, s0, INK) + 20
    chrome(im, KK, "Express Tribune · ARY · Minute Mirror")
def s_c(im, t, D):
    d = ImageDraw.Draw(im); v = C_SEN.frame(30 + t); v = v.resize((W, MH // 2), box=(0, MH // 4, W, MH * 3 // 4)); im.paste(v, (0, Y0)); caption(im.crop((0, 0, 1, 1)), "")
    y = kick(d, Y0 + MH // 2 + 20, "WHAT'S REALLY AT STAKE")
    y = big(d, y, t, "New provinces", .1, 72) + 16
    rows = [("NAQVI", "Floated a referendum on new provinces", ACC, .8), ("PML-N", "Ministers say a referendum “will happen”", ACC, 2.4), ("PPP", "Opposes new provinces in Sindh, and the referendum", RED, 4.6)]
    for k, s_, c, s0 in rows:
        b = ease(seg(t, s0, s0 + .5)); hh = int(120 * S)
        d.rounded_rectangle([40, y, W - 40, y + hh], radius=14, fill=mix(b, (24, 34, 48)), outline=mix(b, c), width=3)
        d.text((70, y + int(18 * S)), k, font=TX(int(24 * S), "Bold"), fill=mix(b, c))
        for j, ln in enumerate(wrap(TX(int(29 * S), "SemiBold"), s_, W - 150)[:2]): d.text((70, y + int(52 * S) + j * int(34 * S)), ln, font=TX(int(29 * S), "SemiBold"), fill=mix(b, INK))
        y += hh + 18
    chrome(im, KK, "Daily Pakistan · Al Jazeera · Daily Times")
def s_d(im, t, D):
    if t < 6: v = C_QAT.frame(12 + t); cap = "Naqvi receiving Qatar's interior minister (file) · Video: Interior Ministry"
    elif t < 12: v = C_MANS.frame(4 + t - 6); cap = "Naqvi at Mansoora (file) · Video: Interior Ministry"
    else: v = C_NADRA.frame(10 + t - 12); cap = "Naqvi at a NADRA centre, 22 Nov · Video: Interior Ministry"
    y = med(im, v, t, cap, reveal=t < 1) + 26; d = ImageDraw.Draw(im)
    y = big(d, y, t, "The man, or the plan?", .1, 64, GOLD) + 16
    for s_, s0 in [("Sources: not liked in the cabinet; seen as embarrassing the PM", 3.0), ("Sources: neither Bilawal nor Maryam is on his side", 8.0), ("Only political ally: the Chaudhry Shujaat family", 12.0)]:
        b = ease(seg(t, s0, s0 + .5)); f = TX(int(30 * S), "SemiBold"); ls = wrap(f, s_, W - 130)
        d.ellipse([46, y + 12, 62, y + 28], fill=mix(b, SAF))
        for j, ln in enumerate(ls): d.text((84, y + j * int(38 * S)), ln, font=f, fill=mix(b, INK))
        y += len(ls) * int(38 * S) + 16
    chrome(im, KK, "")
def s_e(im, t, D):
    d = ImageDraw.Draw(im); y = kick(d, Y0, "THE PLAN, SO FAR")
    f = HK(int(64 * S)); b = ease(seg(t, .2, .8)); d.text((40, y), "JULY", font=f, fill=mix(b, INK))
    lx = 40 + tw(f, "JULY") + 20; rx = W - 40 - tw(f, "NOV"); p = ease(seg(t, .6, 2.6))
    d.line([(lx, y + int(40 * S)), (lx + (rx - 20 - lx) * p, y + int(40 * S))], fill=GOLD, width=4)
    if p >= 1: d.text((rx, y), "NOV", font=f, fill=INK)
    y += int(110 * S)
    for k, s_, s0 in [("0", "parliamentary debates", 3.2), ("0", "amendment drafts in parliament", 5.2), ("?", "how many provinces", 12.0), ("?", "map or date", 14.5)]:
        b = ease(seg(t, s0, s0 + .5)); d.text((40, y), k, font=HK(int(72 * S)), fill=mix(b, RED if k == "0" else GOLD))
        d.text((160, y + int(22 * S)), s_, font=TX(int(34 * S), "Bold"), fill=mix(b, INK)); y += int(100 * S)
    para(d, y + 10, t, "Sources: not discussed in the federal cabinet either.", 8.0, 28)
    chrome(im, KK, "Al Jazeera · Arab News · Express Tribune")
def s_f(im, t, D):
    d = ImageDraw.Draw(im); y = kick(d, Y0, "THE REFERENDUM QUESTION")
    y = big(d, y, t, "Can a referendum create a province?", .1, 56) + 10
    b = ease(seg(t, 1.2, 1.8)); d.text((40, y), "NO.", font=HK(int(110 * S)), fill=mix(b, RED)); y += int(140 * S)
    for k, s0 in [("Two-thirds of the National Assembly", 4.0), ("Two-thirds of the Senate", 5.2), ("Two-thirds of the affected provincial assembly", 6.4)]:
        b = ease(seg(t, s0, s0 + .4)); d.text((40, y), "✓" if False else "•", font=HX(int(40 * S)), fill=mix(b, ACC)); d.text((84, y + 4), k, font=TX(int(32 * S), "Bold"), fill=mix(b, INK)); y += int(56 * S)
    para(d, y + 20, t, "A referendum can show public opinion, but only parliament and the provincial assembly can redraw a province's borders.", 8.5, 28)
    chrome(im, KK, "Constitution, Art. 239(4) · Arab News · Express Tribune")
def s_g(im, t, D):
    v = C_NADRA.frame(30 + t); v = Image.blend(v, Image.new("RGB", v.size, BG), .45); y = med(im, v, 9) + 30; d = ImageDraw.Draw(im)
    y = big(d, y, t, "Real reform, or a political manoeuvre?", .1, 58)
    c = ease(seg(t, 3.0, 3.6)); ly = y + int(50 * S); lg = LOGO_IM.resize((110, 110), Image.LANCZOS)
    im.paste(fadeimg(lg, c), (40, ly), fadeimg(lg, c)); d.text((170, ly + 34), "thepakistandaily.com", font=HX(40), fill=mix(c, INK))
P_ = .5
SCENES = [(k, VOD[k] + P_ + (2.2 if k == "g" else 0), f) for k, f in zip(NARR, [s_a, s_b, s_c, s_d, s_e, s_f, s_g])]
STARTS = np.cumsum([0] + [D for _, D, _ in SCENES]).tolist(); TR = .3
VO_AT = {k: STARTS[i] + .15 for i, k in enumerate(NARR)}
BITES = []
MUSIC = os.path.join(HERE, "audio/Stormfront.mp3")
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
        for s in map(float, sys.argv[3:]): at(s).save(os.path.join(HERE, f"v24{MODE}_{s:05.1f}.png"))
        sys.exit()
    out = sys.argv[2]; os.makedirs(SCR, exist_ok=True); parts = []
    for i in range(len(SCENES)):
        p = os.path.join(SCR, f"{MODE}_{i}_{SCENES[i][0]}.mp4"); render_scene(i, p); parts.append(p)
    lst = os.path.join(SCR, f"{MODE}_list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    silent = os.path.join(SCR, f"{MODE}_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    DUR = STARTS[-1]
    names = list(VO_AT.keys()); ins = ["-i", silent, "-i", os.path.join(HERE, "audio/Stormfront.mp3")]
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
