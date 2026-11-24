"""TPD carousel maker (4:5, 1080x1350).
Usage: python3 carousel.py slides.json OUTPREFIX
slides.json: [{"img": "photo.jpg", "fy": 0.4, "kick": "KICKER", "head": "Headline", "body": "One or two lines",
               "credit": "Photo: X", "quote": false, "contain": false}, ...]   (last slide gets the URL line)
"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render2 import LOGO_IM, wrap, tw

ID = "/usr/share/fonts/opentype/inter/"
HK = lambda s: ImageFont.truetype(ID + "InterDisplay-Black.otf", s)
HX = lambda s: ImageFont.truetype(ID + "InterDisplay-ExtraBold.otf", s)
TX = lambda s, w="SemiBold": ImageFont.truetype(ID + f"Inter-{w}.otf", s)
W, H = 1080, 1350; M = 70; PH = 820
BG = (10, 14, 22); INK = (245, 246, 250); SOFT = (180, 190, 206); GRN = (0, 170, 100); GOLD = (236, 192, 96)


def grad(h, up):
    g = Image.new("L", (1, h))
    for i in range(h): g.putpixel((0, i), int(255 * ((h - 1 - i) if up else i) / (h - 1)))
    return g.resize((W, h))


def cover(f, w, h, fy=.4, contain=False):
    im = Image.open(f).convert("RGB")
    if contain:
        c = Image.new("RGB", (w, h), BG); im.thumbnail((w - 160, h - 160)); c.paste(im, ((w - im.width) // 2, (h - im.height) // 2 + 30)); return c
    s = max(w / im.width, h / im.height); nw, nh = int(im.width * s + 1), int(im.height * s + 1); im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2; y = int(max(0, min(nh - h, fy * nh - h / 2))); return im.crop((x, y, x + w, y + h))


def slide(n, N, s, out):
    c = Image.new("RGB", (W, H), BG); c.paste(cover(s["img"], W, PH, s.get("fy", .4), s.get("contain", False)), (0, 0))
    c.paste(Image.new("RGB", (W, 160), BG), (0, PH - 160), grad(160, False))
    c.paste(Image.new("RGB", (W, 170), (0, 0, 0)), (0, 0), grad(170, True).point(lambda v: int(v * .75)))
    d = ImageDraw.Draw(c)
    c.paste(LOGO_IM.resize((54, 54), Image.LANCZOS), (M, M - 10)); d.text((M + 68, M - 2), "THE PAKISTAN DAILY", font=HX(28), fill=INK)
    d.text((W - M - tw(TX(24, "Bold"), f"{n}/{N}"), M + 2), f"{n}/{N}", font=TX(24, "Bold"), fill=INK)
    cr = s.get("credit", "")
    if cr:
        fc = TX(17); cw = tw(fc, cr) + 22; d.rectangle([W - cw, PH - 190, W, PH - 162], fill=(0, 0, 0)); d.text((W - cw + 11, PH - 186), cr, font=fc, fill=(220, 220, 220))
    y = PH - 60; d.text((M, y), s.get("kick", ""), font=TX(26, "Bold"), fill=GRN); y += 48
    q = s.get("quote", False); f = HX(54) if q else HK(58)
    for ln in wrap(f, s["head"], W - 2 * M): d.text((M, y), ln, font=f, fill=GOLD if q else INK); y += int(f.size * 1.12)
    y += 16
    for ln in wrap(TX(31), s.get("body", ""), W - 2 * M): d.text((M, y), ln, font=TX(31), fill=SOFT); y += 43
    if n == N: d.text((M, H - M - 30), "thepakistandaily.com", font=HX(32), fill=INK)
    if y > H - 40: print(f"WARNING slide {n}: text overflows ({y}px)")
    c.save(out)


if __name__ == "__main__":
    slides = json.load(open(sys.argv[1])); pre = sys.argv[2]
    for i, s in enumerate(slides): slide(i + 1, len(slides), s, f"{pre}_{i + 1}.png")
    print("ok", len(slides))
