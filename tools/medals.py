"""Gold, silver and bronze deal medals.

Gold  : today's price matches the lowest price on record (works from day one, CheapShark gives us that).
Silver: 2nd-lowest price level we have recorded. Bronze: 3rd-lowest.
Those true ranks need 30+ days of our own snapshots and 3+ distinct price levels. Until then silver and bronze
fall back to closeness to the lowest price on record (within 15% / 35%), and the badge text says so, so a medal
never claims more than the data shows.
"""
import html
from datetime import datetime

TOL = 0.03  # prices within 3% count as the same level
SPAN_DAYS = 30
INFO = {
    "gold": ("Gold deal", "#FFD24A", "#B8860B"),
    "silver": ("Silver deal", "#DDE3EA", "#8A94A3"),
    "bronze": ("Bronze deal", "#E39B5A", "#8C4F1E"),
}


def _levels(prices):
    out = []
    for p in sorted(prices):
        if not out or p > out[-1] * (1 + TOL) + 0.005:
            out.append(p)
    return out


def rank(cur, low, hist, today):
    """Return (medal_key or None, detail text)."""
    pts = [(d, float(p)) for d, p in ((hist or {}).get("points") or [])]
    prices = [p for _, p in pts] + [float(cur)]
    if low and low > 0:
        prices.append(float(low))
    floor = min(prices)
    if not (low and low > 0) and len(pts) < 2:
        return None, ""  # nothing to compare against yet, so no medal
    if cur <= floor + 0.005:
        if cur == 0:
            return "gold", "Free right now."
        return "gold", "Real deal: it matches the lowest price on record (%s)." % ("$%.2f" % floor)
    first = datetime.strptime((hist or {}).get("start") or pts[0][0], "%Y-%m-%d").date() if pts else today  # when we began tracking
    levels = _levels(prices)
    if (today - first).days < SPAN_DAYS or len(levels) < 3:
        # Not enough history of our own yet: judge by how close today's price is to the lowest on record.
        if floor <= 0:
            return None, ""
        gap = cur / floor - 1
        if gap <= 0.15:
            return "silver", "Within 15%% of its lowest price on record (%s)." % ("$%.2f" % floor)
        if gap <= 0.35:
            return "bronze", "Within 35%% of its lowest price on record (%s)." % ("$%.2f" % floor)
        return None, ""
    n = 1 + sum(1 for lv in levels if lv < cur / (1 + TOL) - 0.005)
    since = first.strftime("%B %Y")
    if n == 2:
        return "silver", "Second-lowest price we have recorded since %s." % since
    if n == 3:
        return "bronze", "Third-lowest price we have recorded since %s." % since
    return None, ""


def icon(key, size=44):
    _, hi, lo = INFO[key]
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 48 48" aria-hidden="true"><path d="M15 3h8l3 12h-8z" fill="#E4465A"/>'
            f'<path d="M33 3h-8l-3 12h8z" fill="#2D6CDF"/><circle cx="24" cy="30" r="14" fill="{hi}" stroke="{lo}" stroke-width="2.5"/>'
            f'<circle cx="24" cy="30" r="9.5" fill="none" stroke="{lo}" stroke-width="1.5" opacity=".7"/>'
            f'<path d="M24 23.5l2 4.2 4.6.5-3.4 3.1 1 4.5-4.2-2.4-4.2 2.4 1-4.5-3.4-3.1 4.6-.5z" fill="{lo}"/></svg>')


def badge(key, detail):
    name = INFO[key][0]
    return (f'<div class="medal medal-{key}" role="group" aria-label="{html.escape(name)}">{icon(key)}'
            f'<div><strong>{html.escape(name)}</strong><span>{html.escape(detail)}</span></div></div>')


def chip(key):
    """Small label for grid cards."""
    return f'<span class="mchip mchip-{key}">{icon(key, 16)}{html.escape(INFO[key][0].split()[0])}</span>'
