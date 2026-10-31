"""Price history for SteelGames game pages.

Stores one small JSON file per game in data/history/. A point is added whenever the best price
changes, and "seen" records the last day we checked. New files are seeded with the lowest price
ever recorded by CheapShark, so every chart has a floor from day one and fills in daily after that.
Renders a dependency-free SVG step chart.
"""
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "data", "history")
W, H = 720, 280
PL, PR, PT, PB = 52, 16, 16, 34


def _load(gid):
    try:
        return json.load(open(os.path.join(DIR, f"{gid}.json")))
    except Exception:
        return {"points": [], "seen": None}


def update(gid, today_iso, price, low=0.0, low_ts=None):
    """Record today's best price. Returns the history dict."""
    h = _load(gid)
    pts = h["points"]
    if not pts and low and low_ts:
        d = datetime.fromtimestamp(int(low_ts), timezone.utc).strftime("%Y-%m-%d")
        if d < today_iso:
            pts.append([d, round(float(low), 2)])
    if not pts or round(pts[-1][1], 2) != round(float(price), 2):
        if pts and pts[-1][0] == today_iso:
            pts[-1][1] = round(float(price), 2)
        else:
            pts.append([today_iso, round(float(price), 2)])
    h["seen"] = today_iso
    os.makedirs(DIR, exist_ok=True)
    json.dump(h, open(os.path.join(DIR, f"{gid}.json"), "w"), separators=(",", ":"))
    return h


def _ts(d):
    return datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()


def _money(v):
    return "Free" if v == 0 else "$%.2f" % v


def render(h, regular=0.0, low=0.0):
    pts = [(p[0], float(p[1])) for p in h["points"]]
    if not pts:
        return ""
    end = h["seen"] or pts[-1][0]
    t0, t1 = _ts(pts[0][0]), max(_ts(end), _ts(pts[0][0]) + 86400)
    top = max([p[1] for p in pts] + [regular or 0, 1.0])
    top = (int(top / 4) + 1) * 4 if top > 8 else (int(top / 2) + 1) * 2
    iw, ih = W - PL - PR, H - PT - PB

    def X(t):
        return PL + (t - t0) / (t1 - t0) * iw

    def Y(v):
        return PT + ih - (v / top) * ih

    path = [f"M{X(_ts(pts[0][0])):.1f},{Y(pts[0][1]):.1f}"]
    for i in range(1, len(pts)):
        x = X(_ts(pts[i][0]))
        path.append(f"L{x:.1f},{Y(pts[i-1][1]):.1f} L{x:.1f},{Y(pts[i][1]):.1f}")
    path.append(f"L{X(t1):.1f},{Y(pts[-1][1]):.1f}")
    line = " ".join(path)
    area = line + f" L{X(t1):.1f},{Y(0):.1f} L{X(t0):.1f},{Y(0):.1f} Z"
    grid = ""
    for k in range(5):
        v = top * k / 4
        grid += (f'<line class="g" x1="{PL}" x2="{W-PR}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/>'
                 f'<text class="t" x="{PL-8}" y="{Y(v)+4:.1f}" text-anchor="end">${v:.0f}</text>')
    labels = [(t0, pts[0][0], "start"), (t1, end, "end")]
    if t1 - t0 > 86400 * 20:
        mid = (t0 + t1) / 2
        labels.insert(1, (mid, datetime.fromtimestamp(mid, timezone.utc).strftime("%Y-%m-%d"), "middle"))
    xl = "".join(f'<text class="t" x="{X(t):.1f}" y="{H-10}" text-anchor="{a}">{datetime.strptime(d, "%Y-%m-%d").strftime("%b %d, %Y").replace(" 0", " ")}</text>' for t, d, a in labels)
    reg = ""
    if regular and regular > 0:
        reg = (f'<line class="r" x1="{PL}" x2="{W-PR}" y1="{Y(regular):.1f}" y2="{Y(regular):.1f}"/>'
               f'<text class="t r2" x="{W-PR}" y="{Y(regular)-6:.1f}" text-anchor="end">Usual {_money(regular)}</text>')
    cur_d, cur_v = pts[-1][0], pts[-1][1]
    mn = min(pts, key=lambda p: p[1])
    marks = (f'<circle class="dl" cx="{X(_ts(mn[0])):.1f}" cy="{Y(mn[1]):.1f}" r="5"/>'
             f'<circle class="dc" cx="{X(t1):.1f}" cy="{Y(cur_v):.1f}" r="5"/>')
    desc = (f"Price history chart. Lowest recorded {_money(mn[1])} on {mn[0]}. Current best price {_money(cur_v)}. "
            f"Tracked from {pts[0][0]} to {end}.")
    since = datetime.strptime(pts[0][0], "%Y-%m-%d").strftime("%B %d, %Y").replace(" 0", " ")
    note = (f"Chart starts at the lowest price ever recorded and fills in every day from our own price checks. "
            f"Lowest on chart: <strong>{_money(mn[1])}</strong>. Earliest point: {since}.")
    return (f'<figure class="phist"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{desc}">'
            f'<title>{desc}</title>{grid}{reg}<path class="a" d="{area}"/><path class="l" d="{line}"/>{marks}{xl}</svg>'
            f'<figcaption class="fine"><span class="k dl"></span>Lowest <span class="k dc"></span>Current best price. {note}</figcaption></figure>')
