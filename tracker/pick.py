"""Pick voice + format for the next Shorts from shorts_log.csv.

Score = views_7d (or 2x views_48h when 7d isn't in yet), boosted by avg_view_pct when known.
Thompson-style sampling on log-views: proven winners get most slots, but every voice/format
still gets tried, and anything with < 3 measured Shorts keeps an exploration bonus.
Usage: python3 pick.py [n]   -> prints n (voice, format) suggestions plus the current leaderboard.
"""
import csv, math, random, sys, os
from collections import defaultdict

VOICES = ["am_michael", "am_fenrir", "am_onyx", "am_adam", "bm_george"]
FORMATS = ["scam-spotting", "free-fix", "money-tip", "info"]   # roundup/promo dropped: 4-8x fewer views
rows = list(csv.DictReader(open(os.path.join(os.path.dirname(__file__), "shorts_log.csv"))))

def score(r):
    v7, v2 = r.get("views_7d"), r.get("views_48h")
    v = float(v7) if v7 else (2 * float(v2) if v2 else None)
    if v is None: return None
    pct = float(r["avg_view_pct"]) / 100 if r.get("avg_view_pct") else 0.6
    return math.log1p(v) * (0.7 + 0.5 * pct)

def stats(key, options):
    out = {}
    for o in options:
        s = [x for x in (score(r) for r in rows if r[key] == o) if x is not None]
        n = len(s); mu = sum(s) / n if n else 4.0
        out[o] = (mu, n)
    return out

def draw(st):
    return max(st, key=lambda o: random.gauss(st[o][0], 1.2 / math.sqrt(st[o][1] + 1)) + (0.6 if st[o][1] < 3 else 0))

vs, fs = stats("voice", VOICES), stats("format", FORMATS)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
print("Voices :", {k: (round(m, 2), c) for k, (m, c) in sorted(vs.items(), key=lambda x: -x[1][0])})
print("Formats:", {k: (round(m, 2), c) for k, (m, c) in sorted(fs.items(), key=lambda x: -x[1][0])})
for _ in range(n):
    print("next ->", draw(vs), "+", draw(fs))
