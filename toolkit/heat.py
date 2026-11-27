"""Engagement checker for The Pakistan Daily's social manager. Reads X numbers through api.fxtwitter.com.

  python3 toolkit/heat.py score <x-url-or-id> [...]   rank other people's posts (what is already travelling)
  python3 toolkit/heat.py own                         refresh our own posts in social/scoreboard.json (last 4 days)
  python3 toolkit/heat.py top [days]                  our best and worst posts, for the lessons file

score = likes + 2*reposts + 2*replies + 2*quotes; heat = score per hour since posting. Views are shown as well.
Instagram numbers for our own posts come from Buffer (list_posts includeMetrics) and are written by the run itself.
"""
import json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = os.path.join(ROOT, "social", "scoreboard.json")
UA = {"User-Agent": "TPDNewsVideo/1.0"}


def fetch(ref):
    m = re.search(r"(\d{10,})\s*$", ref.split("?")[0].rstrip("/"))
    if not m: return None
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.fxtwitter.com/i/status/{m.group(1)}", headers=UA), timeout=20) as r:
            t = json.load(r).get("tweet") or {}
    except Exception as e:
        return {"id": m.group(1), "error": str(e)[:80]}
    if not t: return {"id": m.group(1), "error": "not found"}
    n = lambda k: int(t.get(k) or 0)
    age = max((time.time() - (t.get("created_timestamp") or time.time())) / 3600, .25)
    score = n("likes") + 2 * n("retweets") + 2 * n("replies") + 2 * n("quotes")
    au = t.get("author") or {}
    media = (t.get("media") or {}).get("videos") or []
    return {"id": m.group(1), "url": t.get("url"), "account": au.get("screen_name"), "followers": au.get("followers"),
            "views": n("views"), "likes": n("likes"), "reposts": n("retweets"), "replies": n("replies"), "quotes": n("quotes"),
            "age_h": round(age, 1), "score": score, "heat": round(score / age, 1),
            "video_s": round(media[0].get("duration") or 0) if media else 0, "text": (t.get("text") or "")[:140].replace("\n", " ")}


def load():
    return json.load(open(BOARD)) if os.path.exists(BOARD) else []


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "score":
        rows = [r for r in (fetch(x) for x in sys.argv[2:]) if r]
        rows.sort(key=lambda r: -r.get("heat", -1))
        for r in rows: print(json.dumps(r, ensure_ascii=False))
    elif cmd == "own":
        board, now, n = load(), time.time(), 0
        for p in board:
            if not p.get("x_url") or now - p.get("posted_ts", now) > 4 * 86400: continue
            r = fetch(p["x_url"])
            if r and "error" not in r:
                p["x"] = {k: r[k] for k in ("views", "likes", "reposts", "replies", "quotes", "score")}; p["x_checked_h"] = r["age_h"]; n += 1
        json.dump(board, open(BOARD, "w"), indent=1, ensure_ascii=False)
        print(f"refreshed {n} of {len(board)} posts")
    elif cmd == "top":
        days = float(sys.argv[2]) if len(sys.argv) > 2 else 7
        rows = [p for p in load() if time.time() - p.get("posted_ts", 0) < days * 86400]
        total = lambda p: (p.get("x") or {}).get("score", 0) + (p.get("ig") or {}).get("score", 0)
        rows.sort(key=lambda p: -total(p))
        for p in rows:
            print(f"{total(p):>6}  {p.get('date')} {p.get('format'):<9} x:{(p.get('x') or {}).get('views', '-')}v/{(p.get('x') or {}).get('score', '-')}  "
                  f"ig:{(p.get('ig') or {}).get('views', '-')}v/{(p.get('ig') or {}).get('score', '-')}  {p.get('story', '')[:60]}  [{p.get('hook', '')[:40]}]")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
