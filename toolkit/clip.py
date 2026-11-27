"""Simple clip maker for The Pakistan Daily (pakistan_connect_buzz style):
the best 1 to 2 minutes of a speech or event, logo, ONE headline strip, footage credit. Nothing else.

  python3 toolkit/clip.py --src in.mp4 --start 12.5 --dur 75 \
      --headline "Bilawal: *PTI is a political reality*" --credit "Video: @account on X" \
      --out 2026-11-28/bilawal-clip

Writes <out>-4x5.mp4 (1080x1350, cover appended as the last 0.6 s), <out>-cover-4x5.png and
<out>-story.png (1080x1920, card at 75% width, centred, clear of the top and bottom 250 px).
Words wrapped in *asterisks* take the accent colour. Prints the Buffer thumbnailOffset (ms).
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1350, 30
BG, INK, ACC, DIM = (8, 11, 17), (246, 247, 250), (0, 180, 112), (200, 206, 218)
INTER = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    for p in (INTER + name, os.path.join(HERE, "fonts", "Oswald.ttf")):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("FAILED: " + " ".join(cmd[:6]) + "...\n" + r.stderr[-1500:])
    return r.stdout


def probe(path):
    j = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", path]))
    s = j["streams"][0]; w, h = s["width"], s["height"]
    rot = abs(int(float((s.get("side_data_list") or [{}])[0].get("rotation", 0))))
    if rot in (90, 270): w, h = h, w
    audio = bool(run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", path]).strip())
    return w, h, float(j["format"]["duration"]), audio


def wrap_rich(d, text, f, maxw):
    """Wrap to lines of (word, highlighted) pairs."""
    words, hi = [], False
    for tok in text.split():
        start = tok.startswith("*"); end = tok.endswith("*") and len(tok) > 1
        if start: hi = True
        words.append((tok.strip("*"), hi))
        if end: hi = False
    lines, cur = [], []
    for w in words:
        trial = " ".join(x[0] for x in cur + [w])
        if cur and d.textlength(trial, font=f) > maxw:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur: lines.append(cur)
    return lines


def fit_headline(d, text, maxw, maxh, sizes=(74, 66, 58, 52, 46, 40)):
    for s in sizes:
        f = font("InterDisplay-Black.otf", s); lines = wrap_rich(d, text, f, maxw); lh = int(s * 1.14)
        if len(lines) * lh <= maxh and len(lines) <= 4:
            return f, lines, lh
    return f, lines[:4], lh


def draw_lines(d, x, y, lines, f, lh):
    sp = d.textlength(" ", font=f)
    for ln in lines:
        cx = x
        for word, hi in ln:
            d.text((cx, y), word, font=f, fill=ACC if hi else INK); cx += d.textlength(word, font=f) + sp
        y += lh
    return y


def overlay(headline, credit, py, ph):
    """Transparent chrome: logo bar, one headline strip under the panel, credit on the panel."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 132], fill=BG + (235,))
    logo = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA").resize((64, 64), Image.LANCZOS)
    im.paste(logo, (40, 34), logo)
    d.text((120, 46), "THE PAKISTAN DAILY", font=font("InterDisplay-ExtraBold.otf", 34), fill=INK)
    d.rectangle([0, py - 4, W, py - 1], fill=(0, 0, 0, 255)); d.rectangle([0, py + ph, W, py + ph + 3], fill=(0, 0, 0, 255))
    if credit:
        f = font("Inter-SemiBold.otf", 20); cw = int(d.textlength(credit, font=f)) + 26
        d.rectangle([W - cw, py + ph - 36, W, py + ph], fill=(0, 0, 0, 200)); d.text((W - cw + 13, py + ph - 30), credit, font=f, fill=(228, 226, 220))
    top = py + ph + 4
    d.rectangle([0, top, W, H], fill=BG + (242,))
    f, lines, lh = fit_headline(d, headline, W - 130, H - top - 70)
    block = len(lines) * lh; y = top + max(26, (H - top - block) // 2 - 8)
    d.rectangle([40, y + 8, 50, y + block - 4], fill=ACC)
    draw_lines(d, 74, y, lines, f, lh)
    return im


def story(cover):
    """1080x1920 Story: the 4:5 card at 75% width, centred, clear of the top and bottom 250 px."""
    st = cover.resize((1080, 1350)).resize((108, 192)).filter(ImageFilter.GaussianBlur(6)).resize((1080, 1920))
    st = Image.blend(st, Image.new("RGB", (1080, 1920), BG), .62)
    cw = 810; ch = int(cw * H / W); card = cover.resize((cw, ch), Image.LANCZOS)
    ImageDraw.Draw(st).rectangle([135 - 3, (1920 - ch) // 2 - 3, 135 + cw + 2, (1920 - ch) // 2 + ch + 2], fill=(0, 0, 0))
    st.paste(card, (135, (1920 - ch) // 2))
    return st


def main():
    a = argparse.ArgumentParser(); a.add_argument("--src", required=True); a.add_argument("--start", type=float, default=0)
    a.add_argument("--dur", type=float, default=90); a.add_argument("--headline", required=True); a.add_argument("--credit", default="")
    a.add_argument("--out", required=True); a.add_argument("--cover-at", type=float, default=None, help="seconds into the clip for the cover frame")
    o = a.parse_args()
    sw, sh, sdur, has_audio = probe(o.src)
    dur = max(1.0, min(o.dur, sdur - o.start))
    if dur > 125: sys.exit("Clip longer than 2 minutes: trim it.")
    ph = min(int(round(W * sh / sw / 2) * 2), 900)          # panel height: full width, capped for tall sources
    py = 132 + 8; os.makedirs(os.path.dirname(o.out) or ".", exist_ok=True)
    ov = overlay(o.headline, o.credit, py, ph); ovp = o.out + "-overlay.png"; ov.save(ovp)
    body, cov, mp4 = o.out + "-body.mp4", o.out + "-cover-4x5.png", o.out + "-4x5.mp4"
    fc = (f"[0:v]fps={FPS},split[a][b];"
          f"[a]scale=108:135:force_original_aspect_ratio=increase,crop=108:135,gblur=sigma=4,scale={W}:{H},eq=brightness=-0.22[bg];"
          f"[b]scale={W}:{ph}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{ph}[fg];"
          f"[bg][fg]overlay=0:{py}[v1];[v1][1:v]overlay=0:0,format=yuv420p[v]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{o.start}", "-t", f"{dur}", "-i", o.src, "-i", ovp]
    if not has_audio: cmd += ["-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
    cmd += ["-filter_complex", fc + ("" if not has_audio else ";[0:a]loudnorm=I=-15:TP=-1.5,aresample=48000[au]"),
            "-map", "[v]", "-map", "[au]" if has_audio else "2:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-shortest", body]
    run(cmd)
    at = o.cover_at if o.cover_at is not None else min(dur * .35, dur - .2)
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{at}", "-i", body, "-frames:v", "1", cov])
    cover = Image.open(cov).convert("RGB"); story(cover).save(o.out + "-story.png")
    tail = o.out + "-tail.mp4"                                  # cover as the last 0.6 s, so it can be the Reel cover
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", "0.6", "-i", cov, "-f", "lavfi", "-t", "0.6", "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-shortest", tail])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", body, "-i", tail, "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4])
    for p in (ovp, body, tail): os.remove(p)
    print(json.dumps({"video": mp4, "cover": cov, "story": o.out + "-story.png", "seconds": round(dur + .6, 1),
                      "thumbnailOffset_ms": int((dur + .3) * 1000), "mb": round(os.path.getsize(mp4) / 1e6, 1)}))


if __name__ == "__main__":
    main()
