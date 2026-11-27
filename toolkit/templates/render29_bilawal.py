"""TPD 27 Nov: Bilawal: PTI a political reality (v2 on kit v3, with Friday updates)."""
import os, sys
from PIL import Image, ImageDraw
from tpdkit import *
FT = os.path.join(HERE, "footage/bb"); SCR = "/tmp/claude-0/-home-claude-tpd-media/f6fb36f0-8f45-50d0-a64f-ba15b1fcce9c/scratchpad/v29"
fp = lambda n: os.path.join(FT, n + ".mp4")
GEO = fp("2126034942257947119"); TRUST = fp("2126000193539891280"); HARD = fp("2126018574674206975"); TARAR = fp("2126036256434081883"); SYS = fp("2126012732399063181"); PROV = fp("2126015506318774632"); ELEC = fp("2126004885338640504")
SQ = "1500:1056:0:110"
S_GEO = Src(GEO, "560:394:330:40", sharpen=True); S_GEO2 = Src(GEO, "560:394:330:40", sharpen=True); S_TR = Src(TRUST, SQ); S_HD = Src(HARD, SQ); S_SYS = Src(SYS, SQ, ph=640)
S_TAR = Src(TARAR, "270:190:940:118", sharpen=True); S_PROV = Src(PROV, SQ); S_ELEC = Src(ELEC, SQ); S_END = Src(TRUST, SQ)
KK = "BILAWAL'S RESET"
B_OPEN = (GEO, 203.2, 212.0); B_TRUST = (TRUST, 60.2, 76.0); B_HARD = (HARD, 43.2, 56.1); B_FAZL = (GEO, 154.0, 160.9); B_T1 = (TARAR, 18.7, 25.2); B_T2 = (TARAR, 180.2, 184.3)
def bl(b): return b[2] - b[1]
def s_open(im, t, D):
    y = stage(im, S_GEO, B_OPEN[1] + t, "Multan Press Club, 26 Nov · Video: Geo News", zoom=1 + .06 * t / D); d = ImageDraw.Draw(im)
    a = ease(seg(t, 0, .35)); o = ease(seg(t, 3.4, 3.9)); f = HK(70); yy = PY + 40
    if o < 1:
        for ln in ["Bilawal: give PTI", "its seats back"]:
            w_ = tw(f, ln); d.rectangle([34, yy - 4, 34 + (w_ + 28) * a, yy + 82], fill=PPP); d.text((48, yy), ln, font=f, fill=mix(a, INK, PPP)); yy += 94
    y = label(d, y + 34, "BILAWAL BHUTTO-ZARDARI, PPP CHAIRMAN", GOLD, t)
    subs(d, y, t, [(0, 3.9, "“If PTI can't get *PTI's own seats*…”"), (3.9, 9.5, "“…how can they go to *me, the PML-N or the JUI?*”")], 68)
    srcline(d, "Geo News · Dawn · Daily Times"); chrome(im, "MULTAN · 26 NOV", PPP)
def s_reality(im, t, D):
    y = stage(im, S_SYS, 10 + t * .9, "Video: PPP Media Cell", zoom=1.0 + .05 * t / D); d = ImageDraw.Draw(im)
    y = label(d, y + 30, "THE LINE EVERYONE IS QUOTING", GOLD, t)
    y = rise(d, 40, y, "“Khan sahib is a convict, he is in jail, but *PTI is a political reality.*”", LORA(64), t, .2, lh=78)
    srcline(d, "Dawn · Daily Times · The Nation"); chrome(im, KK, PPP)
def s_trust(im, t, D):
    y = stage(im, S_TR, B_TRUST[1] + t, "Video: PPP Media Cell"); d = ImageDraw.Draw(im)
    y = label(d, y + 34, "ON WHAT THE GOVERNMENT SHOULD OFFER PTI", ACC, t)
    subs(d, y, t, [(0, 4.8, "“…a system *you don't trust*:”"), (4.8, 12.9, "“*parliament*, the *Election Commission*, the *courts*, accountability…”"), (12.9, 17, "“…how do we *restore that trust?*”")], 64)
    srcline(d, "PPP Media Cell · Dawn"); chrome(im, "TRUST DEFICIT", ACC)
ASKS = [("1", "Return PTI's reserved seats", "a “low-hanging fruit” to rebuild trust"), ("2", "Bring the opposition back in", "to committees and electoral reform"), ("3", "Decide everything in Parliament", "not outside it")]
def s_asks(im, t, D):
    backdrop(im, S_PROV, 5 + t, vgrad(H, .68, .93)); d = ImageDraw.Draw(im)
    y = label(d, 170, "WHAT BILAWAL IS ASKING FOR", GOLD, t); y = rise(d, 40, y, "Three steps to a “reset”", HK(84), t, .05) + 40
    for i, (n, h, b) in enumerate(ASKS):
        a = ease(seg(t, .9 + i * 1.3, 1.4 + i * 1.3)); dx = int(70 * (1 - a)); card(im, (40 + dx, y, W - 40 + dx, y + 250), a, outline=PPP); d = ImageDraw.Draw(im)
        d.text((74 + dx, y + 40), n, font=HK(140), fill=mix(a, PPP, CARD)); d.text((210 + dx, y + 54), h, font=TX(46, "Bold"), fill=mix(a, INK, CARD))
        for j, ln in enumerate(wrap(TX(35), b, W - 310)): d.text((210 + dx, y + 124 + j * 44), ln, font=TX(35), fill=mix(a, SOFT, CARD))
        y += 276
    srcline(d, "Dawn · Daily Times · The Nation"); chrome(im, KK, PPP)
def s_hard(im, t, D):
    y = stage(im, S_HD, B_HARD[1] + t, "Video: PPP Media Cell", zoom=1.06 - .06 * t / D); d = ImageDraw.Draw(im)
    y = label(d, y + 34, "ON THE BACKLASH TO HIS LAST PRESSER", RED, t)
    subs(d, y, t, [(0, 4.7, "“It's said today that Pakistan is a *hard state*.”"), (4.7, 9.4, "“For Pakistan to be a hard state, it should have *thick skin*.”"), (9.4, 13.5, "“You can't have a hard state with *thin skin*.”")], 66)
    srcline(d, "PPP Media Cell · Geo News · Dawn"); chrome(im, "IN ENGLISH", GOLD)
def s_fazl(im, t, D):
    y = stage(im, S_GEO2, B_FAZL[1] + t, "Video: Geo News"); d = ImageDraw.Draw(im)
    y = label(d, y + 34, "UPDATE · ON MAULANA FAZLUR REHMAN", RED, t)
    subs(d, y, t, [(0, bl(B_FAZL), "“Maulana's *house arrest*… I condemn it. It is beyond understanding.”")], 60)
    if t >= bl(B_FAZL): rise(d, 40, y, "Hours later, Fazl told supporters in Lahore he had been *arrested*. Police deny it.", HX(54), t, bl(B_FAZL), lh=64)
    srcline(d, "Geo News · The Nation · Nukta"); chrome(im, "LATEST", RED)
T1 = bl(B_T1)
def s_tarar(im, t, D):
    st = B_T1[1] + t if t < T1 else B_T2[1] + (t - T1)
    y = stage(im, S_TAR, st, "Geo News, 26 Nov · Video: Geo News"); d = ImageDraw.Draw(im)
    y = label(d, y + 34, "THE REPLY: ATTAULLAH TARAR, INFO MINISTER", GRN2, t)
    subs(d, y, t, [(0, 3.2, "“Bilawal sahib is getting *a bit angry* these days.”"), (3.2, T1, "“And he is *our ally*. He has our respect.”"), (T1, D + 1, "“Why so much *fear of public opinion?*”")], 64)
    srcline(d, "Geo News"); chrome(im, "PML-N REPLIES", GRN2)
PTS = [(PPP, "The PPP keeps the PML-N-led government in power, yet sides with PTI on its seats", 1.0), (GOLD, "It rejects a referendum on new provinces and defends Fazl", 2.8),
       (GRN2, "Tarar says the disagreement does not mean the alliance is over", 4.6)]
def s_why(im, t, D):
    backdrop(im, S_ELEC, 20 + t, vgrad(H, .68, .93)); d = ImageDraw.Draw(im)
    y = label(d, 170, "WHY IT MATTERS", GOLD, t); y = rise(d, 40, y, "An ally pushing, *not leaving*", HK(84), t, .05, lh=94) + 44
    for i, (c, s_, s0) in enumerate(PTS):
        a = ease(seg(t, s0, s0 + .5)); ls = wrap(TX(44, "Bold"), s_, W - 150); hh = 60 + len(ls) * 56
        card(im, (40, y, W - 40, y + hh), a); d = ImageDraw.Draw(im); d.rectangle([40, y + 18, 48, y + hh - 18], fill=mix(a, c, CARD))
        for j, ln in enumerate(ls): d.text((76, y + 28 + j * 56), ln, font=TX(44, "Bold"), fill=mix(a, INK, CARD))
        y += hh + 24
    srcline(d, "Dawn · The Nation · Geo News"); chrome(im, "ANALYSIS", GOLD)
def s_end(im, t, D):
    backdrop(im, S_END, 10 + t, vgrad(H, .45, .9)); d = ImageDraw.Draw(im)
    y = rise(d, 40, 470, "Repositioning, or *just bargaining?*", HK(104), t, .1, lh=114); endcard(im, d, y + 60, t, 1.0)
SCENES = [("open", bl(B_OPEN), s_open), ("reality", 7.0, s_reality), ("trust", bl(B_TRUST), s_trust), ("asks", 8.0, s_asks), ("hard", bl(B_HARD), s_hard),
          ("fazl", bl(B_FAZL) + 5.0, s_fazl), ("tarar", bl(B_T1) + bl(B_T2), s_tarar), ("why", 9.0, s_why), ("end", 5.0, s_end)]
SH = Show(SCENES)
if __name__ == "__main__":
    if sys.argv[1] == "stills": SH.stills(SCR, list(map(float, sys.argv[2:]))); sys.exit()
    bites = [B_OPEN + (SH.start("open"),), B_TRUST + (SH.start("trust"),), B_HARD + (SH.start("hard"),), B_FAZL + (SH.start("fazl"),), B_T1 + (SH.start("tarar"),), B_T2 + (SH.start("tarar") + T1,)]
    amb = [(SYS, 10.0, 16.8, SH.start("reality")), (PROV, 5.0, 12.8, SH.start("asks")), (ELEC, 20.0, 28.8, SH.start("why")), (TRUST, 10.0, 14.8, SH.start("end"))]
    SH.render(sys.argv[1], sys.argv[2], SCR, os.path.join(HERE, "audio/Undaunted.mp3"), bites, amb)
