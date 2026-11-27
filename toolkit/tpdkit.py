"""TPD video kit v3 (27 Nov): framed-panel layout over a blurred live background, synced subtitles, progress bar.
A scene file builds clips with mk(), defines scene functions fn(im, t, D) and calls render()."""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from render2 import clamp, ease, seg, tw, wrap, LOGO_IM, fadeimg
FPS = 30; W, H = 1080, 1350; PY = 150
BG = (8, 11, 17); INK = (246, 247, 250); SOFT = (188, 197, 212); DIM = (120, 130, 150); CARD = (22, 29, 43)
ACC = (0, 180, 112); GOLD = (238, 194, 96); RED = (230, 66, 66); BLUE = (70, 150, 235); GRN2 = (30, 150, 80); PPP = (205, 42, 52)
ID = "/usr/share/fonts/opentype/inter/"; _f = {}
def F(n, s):
    if (n, s) not in _f: _f[(n, s)] = ImageFont.truetype(ID + n, s)
    return _f[(n, s)]
HK = lambda s: F("InterDisplay-Black.otf", s); HX = lambda s: F("InterDisplay-ExtraBold.otf", s); TX = lambda s, w="SemiBold": F(f"Inter-{w}.otf", s)
def LORA(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)
def mix(a, c, bg=BG): return tuple(int(bg[j] + (c[j] - bg[j]) * clamp(a)) for j in range(3))
def back(x): x = clamp(x); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def vgrad(h, a0, a1, p=1.0): return Image.fromarray(np.clip((a0 + (a1 - a0) * np.linspace(0, 1, h) ** p) * 255, 0, 255).astype(np.uint8)[:, None].repeat(W, 1), "L")
SHADE = vgrad(H, .50, .90, .8); TOPG = vgrad(190, .75, 0)
BLACK = Image.new("RGB", (W, H), (0, 0, 0)); BGI = Image.new("RGB", (W, H), BG)

class Clip:
    def __init__(self, path, vf, w, h): self.path, self.vf, self.w, self.h, self.p, self.next = path, vf, w, h, None, None
    def frame(self, st):
        idx = max(0, round(st * FPS))
        if self.p is None or self.next != idx:
            if self.p: self.p.kill()
            self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{idx / FPS:.3f}", "-i", self.path, "-vf", self.vf + f",fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); self.next = idx
        n = self.w * self.h * 3; b = self.p.stdout.read(n); self.next += 1
        return Image.frombytes("RGB", (self.w, self.h), b) if len(b) == n else Image.new("RGB", (self.w, self.h), BG)
class Src:
    """One source shot: a sharp panel stream plus a tiny stream that becomes the blurred full-frame background."""
    def __init__(self, path, crop="iw:ih:0:0", ph=760, sharpen=False):
        self.ph = ph; sh = ",unsharp=5:5:0.7" if sharpen else ""
        self.panel = Clip(path, f"crop={crop},scale={W}:{ph}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{ph}{sh}", W, ph)
        self.bg = Clip(path, f"crop={crop},scale=108:135:force_original_aspect_ratio=increase,crop=108:135,gblur=sigma=3", 108, 135)
def backdrop(im, src, st, dark=SHADE):
    im.paste(src.bg.frame(st).resize((W, H), Image.BICUBIC), (0, 0)); im.paste(BGI, (0, 0), dark)
def panel(im, src, st, cap=None, y=PY, zoom=1.0):
    fr = src.panel.frame(st)
    if zoom > 1.001:
        zw, zh = int(W * zoom), int(src.ph * zoom); fr = fr.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - src.ph) // 2, (zw - W) // 2 + W, (zh - src.ph) // 2 + src.ph))
    im.paste(fr, (0, y)); d = ImageDraw.Draw(im)
    d.rectangle([0, y - 4, W, y - 1], fill=(0, 0, 0)); d.rectangle([0, y + src.ph, W, y + src.ph + 3], fill=(0, 0, 0))
    if cap:
        f = TX(19); w_ = tw(f, cap) + 26; d.rectangle([W - w_, y + src.ph - 34, W, y + src.ph], fill=(0, 0, 0)); d.text((W - w_ + 13, y + src.ph - 29), cap, font=f, fill=(228, 226, 220))
    return y + src.ph
def stage(im, src, st, cap=None, zoom=1.0):
    backdrop(im, src, st); return panel(im, src, st, cap, zoom=zoom)
def chrome(im, kicker=None, col=ACC):
    im.paste(BLACK, (0, 0), _topmask); d = ImageDraw.Draw(im)
    im.paste(LOGO_IM.resize((56, 56), Image.LANCZOS), (40, 46)); d.text((110, 56), "THE PAKISTAN DAILY", font=HX(30), fill=INK)
    if kicker:
        f = TX(22, "Bold"); kw = tw(f, kicker) + 30; d.rounded_rectangle([W - 40 - kw, 52, W - 40, 96], radius=9, fill=col); d.text((W - 40 - kw + 15, 61), kicker, font=f, fill=BG)
_topmask = Image.new("L", (W, H), 0); _topmask.paste(TOPG, (0, 0))
def label(d, y, s, col=ACC, t=9):
    a = ease(seg(t, 0, .3)); f = TX(25, "Bold"); d.rectangle([40, y + 4, 46, y + 30], fill=col); d.text((60 - int(14 * (1 - a)), y), s, font=f, fill=mix(a, col)); return y + 50
def draw_rich(d, x, y, line, font, col, hi, a=1.0, bg=BG):
    """Draw one line; words wrapped in *asterisks* take the highlight colour."""
    for i, part in enumerate(line.split("*")):
        if not part: continue
        d.text((x, y), part, font=font, fill=mix(a, hi if i % 2 else col, bg)); x += d.textlength(part, font=font)
def wrap_rich(font, s, mw):
    out, cur, on = [], "", False
    for wd in s.split():
        plain = lambda z: z.replace("*", "")
        c = (cur + " " + wd).strip()
        if tw(font, plain(c)) <= mw: cur = c
        else:
            if cur.count("*") % 2: cur += "*"; wd = "*" + wd
            out.append(cur); cur = wd
    return out + ([cur] if cur else [])
def subs(d, y, t, items, size=62, col=INK, hi=GOLD):
    for a0, a1, s in items:
        if a0 <= t < a1:
            f = HX(size); k = ease(seg(t, a0, a0 + .22))
            for i, ln in enumerate(wrap_rich(f, s, W - 80)): draw_rich(d, 40, y + i * int(size * 1.14) + int(14 * (1 - k)), ln, f, col, hi, k)
def rise(d, x, y, text, font, t, start=0, col=INK, maxw=None, lh=None, hi=GOLD, bg=BG):
    ls = wrap_rich(font, text, maxw or W - 2 * x); lh = lh or int(font.size * 1.16)
    for i, ln in enumerate(ls):
        a = ease(seg(t, start + i * .09, start + i * .09 + .45))
        if a > 0: draw_rich(d, x, y + i * lh + int(18 * (1 - a)), ln, font, col, hi, a, bg)
    return y + len(ls) * lh
def card(im, box, a, fill=CARD, outline=None, r=20):
    """Translucent rounded card that fades in."""
    x0, y0, x1, y1 = box; lay = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, x1 - x0 - 1, y1 - y0 - 1], radius=r, fill=fill + (int(232 * clamp(a)),), outline=(outline + (int(255 * clamp(a)),)) if outline else None, width=3)
    im.paste(lay, (x0, y0), lay)
def srcline(d, s): d.text((40, H - 58), "SOURCES: " + s, font=TX(19, "SemiBold"), fill=DIM)
def endcard(im, d, y, t, start=1.0):
    c = ease(seg(t, start, start + .6)); lg = LOGO_IM.resize((116, 116), Image.LANCZOS)
    im.paste(fadeimg(lg, c), (40, y), fadeimg(lg, c)); d.text((178, y + 34), "thepakistandaily.com", font=HX(46), fill=mix(c, INK))

ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS)]
class Show:
    def __init__(self, scenes, tr=.28):
        self.S = scenes; self.ST = np.cumsum([0] + [D for _, D, _ in scenes]).tolist(); self.TR = tr; self.DUR = self.ST[-1]; self._prev = {}
    def start(self, name): return self.ST[[n for n, _, _ in self.S].index(name)]
    def raw(self, i, tl):
        im = BGI.copy(); self.S[i][2](im, tl, self.S[i][1]); return im
    def frame(self, i, tl):
        im = self.raw(i, tl)
        if i > 0 and tl < self.TR:
            if i not in self._prev: self._prev[i] = self.raw(i - 1, self.S[i - 1][1] - 1 / FPS)
            k = ease(tl / self.TR); im = Image.blend(self._prev[i], im, k); r = 9 * math.sin(math.pi * k)
            if r > .6: im = im.filter(ImageFilter.GaussianBlur(r))
        g = (self.ST[i] + tl) / self.DUR; d = ImageDraw.Draw(im); d.rectangle([0, H - 8, W, H], fill=(30, 36, 48)); d.rectangle([0, H - 8, int(W * g), H], fill=ACC)
        return im
    def at(self, t):
        for i in range(len(self.S)):
            if t < self.ST[i + 1]: return self.frame(i, t - self.ST[i])
        return self.frame(len(self.S) - 1, self.S[-1][1] - 1 / FPS)
    def _scene(self, i, path):
        pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + ENC + [path], stdin=subprocess.PIPE)
        for k in range(int(round(self.S[i][1] * FPS))): pr.stdin.write(self.frame(i, k / FPS).tobytes())
        pr.stdin.close(); assert pr.wait() == 0
    def render(self, out, cover_png, scr, music, bites, ambient=(), mvol=(.07, .17)):
        """bites/ambient: [(path, t0, t1, at)]; bites duck the music, ambient sits low under graphics."""
        import multiprocessing as mp
        os.makedirs(scr, exist_ok=True); parts = [os.path.join(scr, f"p{i}.mp4") for i in range(len(self.S))]
        with mp.Pool(4) as pool: pool.starmap(self._scene, list(enumerate(parts)))
        cp = os.path.join(scr, "cover.mp4"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", cover_png, "-t", "0.6", "-vf", f"scale={W}:{H},fps={FPS}"] + ENC + [cp], check=True)
        lst = os.path.join(scr, "list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts + [cp]))
        silent = os.path.join(scr, "silent.mp4"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
        DUR = self.DUR + .6; allb = list(bites) + list(ambient); ins = ["-i", silent, "-i", music]
        for p_, *_ in allb: ins += ["-i", p_]
        duck = "+".join(f"between(t,{a:.2f},{a + (b1 - b0):.2f})" for _, b0, b1, a in bites) or "0"
        fc = [f"[1:a]atrim=0:{DUR},volume='if({duck},{mvol[0]},{mvol[1]})':eval=frame,afade=t=out:st={DUR - 2.5}:d=2.5[m]"]
        for i, (p_, b0, b1, a) in enumerate(allb):
            vol = 1.3 if i < len(bites) else 0.32
            fc.append(f"[{2 + i}:a]atrim={b0}:{b1},asetpts=PTS-STARTPTS,aresample=44100,dynaudnorm,volume={vol},afade=t=in:d=0.08,afade=t=out:st={b1 - b0 - .2:.2f}:d=0.2,adelay={int(a * 1000)}:all=1[b{i}]")
        fc.append("".join(f"[b{i}]" for i in range(len(allb))) + f"[m]amix=inputs={len(allb) + 1}:duration=longest:normalize=0,atrim=0:{DUR},loudnorm=I=-15:TP=-1.5[a]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-t", f"{DUR}", "-movflags", "+faststart", out], check=True)
        print("done", round(DUR, 1), "cover frame at ms", int((self.DUR + .3) * 1000))
    def stills(self, scr, ts, name="st"):
        os.makedirs(scr, exist_ok=True); fs = []
        for s in ts: p = os.path.join(scr, f"{name}_{s:05.1f}.png"); self.at(s).save(p); fs.append(p)
        n = len(fs); cols = min(6, n); rows = (n + cols - 1) // cols; c = Image.new("RGB", (432 * cols, 540 * rows))
        for i, f in enumerate(fs): c.paste(Image.open(f).resize((432, 540), Image.LANCZOS), ((i % cols) * 432, (i // cols) * 540))
        c.save(os.path.join(scr, name + "_sheet.jpg"), quality=88)
