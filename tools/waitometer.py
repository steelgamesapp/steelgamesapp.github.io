"""Wait-O-Meter: should you buy this game now or wait?

Score runs 0 (buy now) to 100 (wait). It blends three things we can actually see:
how far today's price sits above the lowest price ever recorded, how soon the next big sale is,
and (once enough daily snapshots exist) how often the price has dipped below today's price.
Renders a small SVG gauge and a few plain-English reasons.
"""
import html
import json
import math
import os
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [(20, "Buy now", "buy"), (45, "Fine to buy", "ok"), (70, "Lean wait", "lean"), (101, "Wait", "wait")]
COLORS = {"buy": "#5CE08A", "ok": "#B6E35C", "lean": "#FFB020", "wait": "#FF6B8A"}


def _money(v):
    return "Free" if v == 0 else "$%.2f" % v


def _events():
    try:
        return json.load(open(os.path.join(HERE, "sale_events.json")))["events"]
    except Exception:
        return []


def next_event(today, store=""):
    """Return (event, days_until, running_now) for the soonest event that has not ended."""
    best = None
    for ev in _events():
        if store == "Steam" and not ev["name"].startswith("Steam"):
            continue  # Steam has no Black Friday sale, so judge Steam prices by Steam events
        s = datetime.strptime(ev["start"], "%Y-%m-%d").date()
        e = datetime.strptime(ev["end"], "%Y-%m-%d").date()
        if e < today:
            continue
        days = (s - today).days
        if best is None or s < best[3]:
            best = (ev, max(days, 0), s <= today <= e, s)
    return best[:3] if best else (None, None, False)


def _history_note(hist, cur, today):
    """Return (dips, days_tracked) when we have enough real snapshots, else None."""
    pts = (hist or {}).get("points") or []
    if len(pts) < 3:
        return None
    first = datetime.strptime(pts[0][0], "%Y-%m-%d").date()
    span = (today - first).days
    if span < 30:
        return None
    dips = sum(1 for _, p in pts[:-1] if float(p) < cur * 0.95)
    return dips, span


def assess(cur, reg, low, today=None, hist=None, store=""):
    today = today or date.today()
    if cur == 0:
        return {"score": 0, "label": "Buy now", "key": "buy", "reasons": ["It is free right now. Grab it."], "save": 0.0}
    reasons = []
    at_floor = low > 0 and cur <= low * 1.05
    if low > 0:
        over = cur / low - 1
        score = min(70.0, over * 70)
        if cur <= low:
            reasons.append("Matches the lowest price we have on record (%s)." % _money(low))
        elif at_floor:
            reasons.append("Within 5%% of its lowest price on record (%s)." % _money(low))
        else:
            reasons.append("%s is %d%% above its lowest price on record (%s)." % (_money(cur), round(over * 100), _money(low)))
    else:
        score = 35.0
        reasons.append("We do not have a lowest price on record for this game yet.")
    if reg > 0 and cur >= reg * 0.98:
        score = max(score, 55.0)
        reasons.append("It is not on sale right now.")
    ev, days, running = next_event(today, store)
    if ev and not at_floor:
        if running:
            reasons.append("%s is on now." % ev["name"])
        elif days <= 60:
            score += 25 * (1 - days / 60)
            reasons.append("Next big sale: %s, in %d day%s." % (ev["name"], days, "" if days == 1 else "s"))
        else:
            reasons.append("Next big sale: %s, in %d days." % (ev["name"], days))
    elif ev and at_floor:
        reasons.append("A sale is unlikely to beat this price by much.")
    hn = _history_note(hist, cur, today)
    if hn and not at_floor:
        dips, span = hn
        if dips:
            score += 10
            reasons.append("In the %d days we have tracked it, it dipped below today's price %d time%s." % (span, dips, "" if dips == 1 else "s"))
        else:
            score -= 5
            reasons.append("In the %d days we have tracked it, it has not been cheaper than today." % span)
    score = int(max(0, min(100, round(score))))
    label, key = next((l, k) for lim, l, k in BANDS if score < lim)
    save = round(max(0.0, cur - low), 2) if low > 0 else 0.0
    return {"score": score, "label": label, "key": key, "reasons": reasons[:4], "save": save}


def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def gauge(score, label, key):
    cx, cy, r, w = 120, 112, 90, 16
    arcs = ""
    segs = [(0, 20, "buy"), (20, 45, "ok"), (45, 70, "lean"), (70, 100, "wait")]
    for a, b, k in segs:
        x1, y1 = _pt(cx, cy, r, 180 - a * 1.8)
        x2, y2 = _pt(cx, cy, r, 180 - b * 1.8)
        arcs += f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}" fill="none" stroke="{COLORS[k]}" stroke-width="{w}" stroke-linecap="butt" opacity=".9"/>'
    nx, ny = _pt(cx, cy, r - 24, 180 - score * 1.8)
    needle = (f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
              f'<circle cx="{cx}" cy="{cy}" r="8" fill="#fff"/><circle cx="{cx}" cy="{cy}" r="3" fill="#0F0A24"/>')
    d = f"Wait-O-Meter: {label}. Score {score} out of 100, where 0 is buy now and 100 is wait."
    return (f'<svg class="wom-g" viewBox="0 0 240 132" role="img" aria-label="{html.escape(d)}"><title>{html.escape(d)}</title>{arcs}{needle}'
            f'<text x="14" y="130" class="wom-e">BUY NOW</text><text x="226" y="130" text-anchor="end" class="wom-e">WAIT</text></svg>')


def widget(a):
    e = html.escape
    lis = "".join(f"<li>{e(r)}</li>" for r in a["reasons"])
    save = f'<p class="wom-save">Waiting could save up to <strong>{_money(a["save"])}</strong>, if it returns to its lowest price.</p>' if a["save"] >= 0.5 and a["key"] in ("lean", "wait", "ok") else ""
    return (f'<div class="wom wom-{a["key"]}"><div class="wom-top"><span class="wom-title">WAIT-O-METER</span></div>'
            f'{gauge(a["score"], a["label"], a["key"])}<div class="wom-label">{e(a["label"])}</div><ul class="wom-why">{lis}</ul>{save}'
            f'<p class="fine">A guide from price history and sale dates, not a promise.</p></div>')


def faq_text(a):
    return f'{a["label"]}. ' + " ".join(a["reasons"][:3])
