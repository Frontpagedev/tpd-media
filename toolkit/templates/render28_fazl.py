"""TPD 27 Nov: Fazl: arrested or not? Usage: render28_fazl.py out.mp4 cover.png | render28_fazl.py stills t..."""
import os, sys, math
from PIL import Image, ImageDraw
from tpdkit import *
FT = os.path.join(HERE, "footage/fz"); SCR = "/tmp/claude-0/-home-claude-tpd-media/f6fb36f0-8f45-50d0-a64f-ba15b1fcce9c/scratchpad/v28"
SP = os.path.join(FT, "tpd_suspend.mp4"); ST = os.path.join(FT, "tpd_arrest.mp4"); MSG = os.path.join(FT, "msg.mp4"); PW = os.path.join(FT, "2126233565721743517.mp4"); QT = os.path.join(FT, "2126233176058265811.mp4")
S_SP = Src(SP, sharpen=True); S_SP2 = Src(SP, sharpen=True); S_SP3 = Src(SP, sharpen=True); S_SP4 = Src(SP, sharpen=True, ph=640); S_SP5 = Src(SP, sharpen=True)
S_ST = Src(ST, "848:476:0:0", sharpen=True); S_MSG = Src(MSG); S_PW = Src(PW, "1280:660:0:0"); S_PW2 = Src(PW, "1280:660:0:0", ph=640)
KK = "FAZL: ARRESTED?"
B_OPEN = (SP, 104.6, 118.6); B_ST = (ST, 131.1, 142.5); B_JAIL = (SP, 62.0, 74.9)
def bl(b): return b[2] - b[1]

def s_open(im, t, D):
    y = stage(im, S_SP, B_OPEN[1] + t, "Multan Road, Lahore, Thursday night · Video: JUI-F", zoom=1.0 + .05 * t / D); d = ImageDraw.Draw(im)
    # stamp
    a = back(seg(t, .15, .55)); o = ease(seg(t, 3.6, 4.1))
    if a > 0 and o < 1:
        f = HK(int(150 * (1.6 - .6 * min(a, 1)))); s = "ARRESTED?"; w_ = tw(f, s); x = (W - w_) // 2; yy = PY + 380 - f.size // 2
        lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); ld.rectangle([x - 26, 30, x + w_ + 26, 30 + f.size + 34], fill=RED + (int(235 * (1 - o)),)); ld.text((x, 34), s, font=f, fill=(255, 255, 255, int(255 * (1 - o))))
        lay = lay.rotate(-3, resample=Image.BICUBIC); im.paste(lay, (0, yy - 40), lay)
    y = label(d, y + 34, "MAULANA FAZLUR REHMAN, JUI-F CHIEF", GOLD, t)
    subs(d, y, t, [(0, 3.2, "“Just now, the *IG* came to me…”"), (3.2, 5.9, "“…the *CCPO* came.”"), (5.9, 8.4, "“They have *arrested me*.”"),
                   (8.4, 11.7, "“I am in *their custody*. Wherever they take me, they take me.”"), (11.7, 15, "“So do not worry.”")], 68)
    srcline(d, "JUI-F · Nukta · Arab News"); chrome(im, "LAHORE · THURSDAY MIDNIGHT", RED)
def s_vs(im, t, D):
    backdrop(im, S_SP2, 196 + t); d = ImageDraw.Draw(im)
    y = label(d, 170, "TWO VERSIONS OF ONE NIGHT", GOLD, t); rise(d, 40, y, "Was he arrested?", HK(92), t, .05)
    for i, (tag, col, head, body, who, s0) in enumerate([
            ("JUI-F SAYS", RED, "Yes.", "Officers got into his car and took him away. He is under house arrest.", "Party statement", .7),
            ("POLICE SAY", BLUE, "No.", "He was not arrested. He went home with his convoy.", "DIG Operations Faisal Kamran", 2.3)]):
        a = ease(seg(t, s0, s0 + .5)); y0 = 420 + i * 440; dx = int((1 - a) * (-90 if i == 0 else 90))
        card(im, (40 + dx, y0, W - 40 + dx, y0 + 410), a, outline=col); d = ImageDraw.Draw(im)
        f = TX(24, "Bold"); kw = tw(f, tag) + 28; d.rounded_rectangle([70 + dx, y0 + 28, 70 + dx + kw, y0 + 70], radius=8, fill=mix(a, col, CARD)); d.text((84 + dx, y0 + 36), tag, font=f, fill=mix(a, BG, CARD))
        d.text((70 + dx, y0 + 96), head, font=HK(120), fill=mix(a, col, CARD))
        yy = y0 + 196
        for ln in wrap(TX(36, "Bold"), body, W - 440): pass
        yy = y0 + 240
        for ln in wrap(TX(40, "Bold"), body, W - 140): d.text((70 + dx, yy), ln, font=TX(40, "Bold"), fill=mix(a, INK, CARD)); yy += 52
        f2 = TX(26); d.text((W - 70 + dx - tw(f2, who), y0 + 36), who, font=f2, fill=mix(a, SOFT, CARD))
    srcline(d, "Geo News · The News · Nukta · JUI-F"); chrome(im, KK, RED)
TL = [("2:00 PM", "Leaves his home in Park View for the Sargodha rally", ACC, .5), ("AFTERNOON", "Multan Road blocked. Convoy stuck near Thokar Niaz Baig", GOLD, 2.0),
      ("~10 HOURS", "Talks with the CCPO and DIG. He refuses to turn back, JUI-F says", GOLD, 3.6), ("MIDNIGHT", "Tells the crowd he has been arrested", RED, 5.2)]
def s_time(im, t, D):
    backdrop(im, S_PW, 53 + t * .8, vgrad(H, .72, .93)); d = ImageDraw.Draw(im)
    y = label(d, 170, "THURSDAY IN LAHORE", GOLD, t); y = rise(d, 40, y, "He never reached Sargodha", HK(74), t, .05) + 40
    # route schematic
    x0, x1, xb = 110, W - 110, 520; p = ease(seg(t, .5, 2.6)); d.line([(x0, y + 30), (x1, y + 30)], fill=(70, 80, 100), width=6)
    for xx in range(xb + 20, x1, 28): d.line([(xx, y + 30), (xx + 12, y + 30)], fill=BG, width=8)
    xc = x0 + (xb - x0) * p; d.line([(x0, y + 30), (xc, y + 30)], fill=ACC, width=8)
    d.ellipse([x0 - 14, y + 16, x0 + 14, y + 44], fill=ACC); d.text((x0 - 50, y + 60), "Park View", font=TX(28, "Bold"), fill=INK)
    b = ease(seg(t, 2.4, 2.8)); d.rectangle([xb - 8, y - 14 - 10 * b, xb + 8, y + 74 + 10 * b], fill=mix(b, RED, (70, 80, 100))); d.text((xb - 110, y + 100), "Thokar Niaz Baig", font=TX(28, "Bold"), fill=mix(b, RED))
    d.ellipse([x1 - 14, y + 16, x1 + 14, y + 44], outline=(120, 130, 150), width=4); d.text((x1 - 90, y + 60), "Sargodha", font=TX(28, "Bold"), fill=DIM)
    pr = 13 + 3 * math.sin(t * 6); d.ellipse([xc - pr, y + 30 - pr, xc + pr, y + 30 + pr], fill=INK)
    y += 200
    for i, (tm, s_, col, s0) in enumerate(TL):
        a = ease(seg(t, s0, s0 + .45)); yy = y + i * 172
        d.text((40, yy + 4), tm, font=HX(38), fill=mix(a, col, (14, 18, 26)))
        for j, ln in enumerate(wrap(TX(40, "Bold"), s_, W - 370)): d.text((330 + int(30 * (1 - a)), yy + j * 52), ln, font=TX(40, "Bold"), fill=mix(a, INK, (14, 18, 26)))
    srcline(d, "JUI-F statement · Nukta · Express · The Nation"); chrome(im, KK, RED)
def s_state(im, t, D):
    y = stage(im, S_ST, B_ST[1] + t, "Video: JUI-F statement"); d = ImageDraw.Draw(im)
    y = label(d, y + 34, "JUI-F, AFTER THE STANDOFF", RED, t)
    subs(d, y, t, [(0, 5.4, "“The latest: Maulana sahib has been put under *house arrest* in Lahore.”"), (5.4, 9.3, "“His house has been sealed. *Police* have been deployed.”"), (9.3, 12, "“Meetings have been *banned*.”")], 62)
    srcline(d, "JUI-F · Arab News"); chrome(im, "THE PARTY'S VERSION", RED)
ROWS = [("JUI-F", RED, "Under house arrest, in police custody at a residence in Lahore", .8), ("POLICE", BLUE, "At his residence. Not arrested, not under house arrest", 2.4),
        ("GOVT SOURCES", ACC, "At his sister's home in Park View, not under arrest, they tell The Pakistan Daily", 4.0)]
def s_where(im, t, D):
    backdrop(im, S_MSG, 30 + t, vgrad(H, .62, .92)); d = ImageDraw.Draw(im)
    y = label(d, 170, "FRIDAY", GOLD, t); y = rise(d, 40, y, "So where is he now?", HK(88), t, .05) + 36
    for i, (tag, col, s_, s0) in enumerate(ROWS):
        a = ease(seg(t, s0, s0 + .5)); ls = wrap(TX(42, "Bold"), s_, W - 150); hh = 100 + len(ls) * 54
        card(im, (40, y, W - 40, y + hh), a); d = ImageDraw.Draw(im); d.rectangle([40, y + 18, 48, y + hh - 18], fill=mix(a, col, CARD))
        d.text((76, y + 22), tag, font=TX(27, "Bold"), fill=mix(a, col, CARD))
        for j, ln in enumerate(ls): d.text((76, y + 66 + j * 54), ln, font=TX(42, "Bold"), fill=mix(a, INK, CARD))
        y += hh + 22
    a = ease(seg(t, 5.6, 6.2)); rise(d, 40, y + 16, "All three agree on one thing: *he is in a house in Lahore.*", TX(38, "Bold"), t, 5.6, INK, lh=50, bg=(14, 18, 26))
    srcline(d, "JUI-F · Geo News · The News · govt sources"); chrome(im, KK, RED)
CTX = [("25 NOV", "Sargodha bars Fazl and eight JUI-F leaders for 30 days", .5), ("26 NOV", "JUI-F blocks highways and motorways nationwide", 2.4),
       ("COURT", "Police tell the Lahore High Court he is neither arrested nor wanted", 4.3)]
def s_ctx(im, t, D):
    y = stage(im, S_PW2, 43.6 + t, "Peshawar, 26 Nov · Video: Geo News"); d = ImageDraw.Draw(im)
    y = label(d, y + 30, "HOW IT GOT HERE", GOLD, t) + 4
    for i, (tm, s_, s0) in enumerate(CTX):
        a = ease(seg(t, s0, s0 + .45)); d.text((40, y + 2), tm, font=HX(34), fill=mix(a, ACC, (14, 18, 26)))
        ls = wrap(TX(37, "Bold"), s_, W - 260)
        for j, ln in enumerate(ls): d.text((215 + int(26 * (1 - a)), y + j * 47), ln, font=TX(37, "Bold"), fill=mix(a, INK, (14, 18, 26)))
        y += len(ls) * 47 + 26
    srcline(d, "Dawn · Nukta · Arab News · The Nation"); chrome(im, "BACKSTORY", GOLD)
def s_jail(im, t, D):
    y = stage(im, S_SP3, B_JAIL[1] + t, "Video: JUI-F", zoom=1.05 - .05 * t / D); d = ImageDraw.Draw(im)
    y = label(d, y + 34, "FAZL TO THE GOVERNMENT", GOLD, t)
    subs(d, y, t, [(0, 3.0, "“Arrests *cannot block* our path.”"), (3.0, 8.4, "“Why take the trouble of arresting us?”"), (8.4, 13.5, "“We will come to your *jail gates* and offer ourselves.”")], 66)
    srcline(d, "JUI-F · Nukta"); chrome(im, KK, RED)
NOW = [("JUI-F protests after Friday prayers, nationwide", ACC, .6), ("Peshawar police book 16 JUI-F leaders and workers over the motorway blockade", GOLD, 2.4),
       ("Bilawal condemns the “house arrest” and says he will try to meet Fazl", PPP, 4.2)]
def s_now(im, t, D):
    y = stage(im, S_SP4, 238 + t, "Video: JUI-F"); d = ImageDraw.Draw(im)
    y = label(d, y + 30, "TODAY", RED, t) + 4
    for i, (s_, col, s0) in enumerate(NOW):
        a = ease(seg(t, s0, s0 + .45)); ls = wrap(TX(38, "Bold"), s_, W - 130); d.rectangle([40, y + 6, 48, y + len(ls) * 48 - 6], fill=mix(a, col, (14, 18, 26)))
        for j, ln in enumerate(ls): d.text((72 + int(26 * (1 - a)), y + j * 48), ln, font=TX(38, "Bold"), fill=mix(a, INK, (14, 18, 26)))
        y += len(ls) * 48 + 26
    srcline(d, "Arab News · Ummat · Geo News · The Nation"); chrome(im, "WHAT'S NEXT", ACC)
def s_end(im, t, D):
    backdrop(im, S_SP5, 2 + t, vgrad(H, .45, .9)); d = ImageDraw.Draw(im)
    y = rise(d, 40, 470, "Arrested, or just *not allowed to leave?*", HK(104), t, .1, lh=114)
    endcard(im, d, y + 60, t, 1.0)
SCENES = [("open", bl(B_OPEN), s_open), ("vs", 8.0, s_vs), ("time", 9.5, s_time), ("state", bl(B_ST), s_state), ("where", 9.0, s_where),
          ("ctx", 8.8, s_ctx), ("jail", bl(B_JAIL), s_jail), ("now", 8.5, s_now), ("end", 5.0, s_end)]
SH = Show(SCENES)
if __name__ == "__main__":
    if sys.argv[1] == "stills": SH.stills(SCR, list(map(float, sys.argv[2:]))); sys.exit()
    bites = [B_OPEN + (SH.start("open"),), B_ST + (SH.start("state"),), B_JAIL + (SH.start("jail"),)]
    amb = [(SP, 39.0, 47.0, SH.start("vs")), (SP, 150.0, 159.5, SH.start("time")), (SP, 226.0, 235.0, SH.start("where")), (PW, 43.6, 52.4, SH.start("ctx")), (SP, 238.0, 246.5, SH.start("now")), (SP, 2.0, 7.0, SH.start("end"))]
    SH.render(sys.argv[1], sys.argv[2], SCR, os.path.join(HERE, "audio/Stormfront.mp3"), bites, amb)
