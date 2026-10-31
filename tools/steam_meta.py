"""Game details from the Steam store (genres, features, platforms, Steam Deck status, specs, screenshots).

Fetched at build time (never in the visitor's browser, Steam blocks that), cached per game in data/meta/
for 14 days, and rendered into game pages. Standard library only. If Steam does not answer, a game simply
keeps whatever details it already had cached, or none, and its page still renders.
"""
import html
import json
import os
import re
import time
import urllib.request
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "data", "meta")
TTL_DAYS = 14
BUDGET = 80  # games refreshed per build, so the daily run stays quick and polite
_used = 0
OFFLINE = False

GENRE_CAT = {"Action": "action", "Adventure": "adventure", "RPG": "rpg", "Strategy": "strategy", "Simulation": "sim",
             "Racing": "racing", "Sports": "sports"}
FEATURES = ["Single-player", "Multi-player", "Co-op", "Online Co-op", "LAN Co-op", "Shared/Split Screen Co-op",
            "Online PvP", "Steam Achievements", "Steam Cloud", "Remote Play on TV", "Steam Trading Cards", "Family Sharing"]
DECK = {3: ("Verified", "good", "Steam Deck Verified: made to run well on the handheld."),
        2: ("Playable", "ok", "Steam Deck Playable: works, but may need small tweaks."),
        1: ("Unsupported", "bad", "Not supported on Steam Deck."),
        0: ("Not rated", "", "Steam Deck rating not available yet.")}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SteelGames-SEO-Builder"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def _strip(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip()


def _reqs(raw):
    """Turn Steam's requirement HTML into [(label, value)] pairs."""
    if not isinstance(raw, str):
        return []
    out = []
    for lab, val in re.findall(r"<strong>\s*([^<:]+?)\s*\**:?\s*</strong>\s*([^<]*)", raw):
        lab, val = _strip(lab), _strip(val)
        if val and lab.lower() not in ("minimum", "recommended"):
            out.append((lab, val))
    return out[:7]


def compact(d, deck):
    plat = d.get("platforms") or {}
    pcr = d.get("pc_requirements") or {}
    pcr = pcr if isinstance(pcr, dict) else {}
    cats = [c.get("description", "") for c in d.get("categories", []) or []]
    feats = [c for c in FEATURES if c in cats]
    return {
        "name": d.get("name"),
        "desc": _strip(d.get("short_description")),
        "header": d.get("header_image"),
        "shots": [{"t": s.get("path_thumbnail"), "f": s.get("path_full")} for s in (d.get("screenshots") or [])[:6]],
        "genres": [g.get("description") for g in d.get("genres", []) or [] if g.get("description")],
        "features": feats,
        "platforms": {"windows": bool(plat.get("windows")), "mac": bool(plat.get("mac")), "linux": bool(plat.get("linux"))},
        "controller": d.get("controller_support"),
        "dev": d.get("developers") or [], "pub": d.get("publishers") or [],
        "released": (d.get("release_date") or {}).get("date"),
        "meta": (d.get("metacritic") or {}).get("score"),
        "langs": [_strip(x).replace("*", "").strip() for x in re.split(r",", re.sub(r"<br\s*/?>.*", "", d.get("supported_languages") or "")) if _strip(x)][:40],
        "min": _reqs(pcr.get("minimum")), "rec": _reqs(pcr.get("recommended")),
        "deck": deck,
    }


def _path(appid):
    return os.path.join(DIR, f"{appid}.json")


def load(appid):
    try:
        return json.load(open(_path(appid)))
    except Exception:
        return None


def get(appid):
    """Return compact metadata for a Steam app id (cached), or None."""
    global _used
    appid = str(appid or "")
    if not appid.isdigit() or appid == "0":
        return None
    c = load(appid)
    fresh = c and (date.today() - datetime.strptime(c["fetched"], "%Y-%m-%d").date()).days < TTL_DAYS
    if fresh or OFFLINE or _used >= BUDGET:
        return c["d"] if c else None
    _used += 1
    try:
        j = _get(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=english")
        node = j.get(appid) or {}
        if not node.get("success"):
            raise ValueError("no data")
        deck = 0
        try:
            r = _get(f"https://store.steampowered.com/saleaction/ajaxgetdeckappcompatibilityreport?nAppID={appid}")
            deck = int((r.get("results") or {}).get("resolved_category") or 0)
        except Exception:
            deck = (c or {}).get("d", {}).get("deck", 0)
        d = compact(node["data"], deck)
        os.makedirs(DIR, exist_ok=True)
        json.dump({"fetched": date.today().isoformat(), "d": d}, open(_path(appid), "w"), separators=(",", ":"))
        time.sleep(1.2)
        return d
    except Exception:
        return c["d"] if c else None


# ---------- rendering ----------
ICONS = {
    "windows": '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 5.5 11 4.4v7H3zM12 4.3 21 3v8.4h-9zM3 12.6h8v7l-8-1.1zM12 12.6h9V21l-9-1.3z"/></svg>',
    "mac": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
    "linux": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3c-2 0-3 2-3 5 0 2-2 3-2 6 0 3 2 6 5 6s5-3 5-6c0-3-2-4-2-6 0-3-1-5-3-5z"/></svg>',
    "deck": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="7" width="20" height="10" rx="4"/><circle cx="7" cy="12" r="1.2"/><circle cx="17" cy="12" r="1.2"/></svg>',
    "pad": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 8h10a4 4 0 0 1 4 4v1a3 3 0 0 1-5.2 2L14 13h-4l-1.8 2A3 3 0 0 1 3 13v-1a4 4 0 0 1 4-4z"/></svg>',
}


def _e(t):
    return html.escape(str(t if t is not None else ""))


def works_best_on(m):
    """The 'Works best on' block."""
    p = m["platforms"]
    chips = ""
    for k, lab in (("windows", "Windows"), ("mac", "macOS"), ("linux", "Linux")):
        chips += f'<span class="wb {"on" if p.get(k) else "off"}">{ICONS[k]}{lab}</span>'
    dlab, dcls, dtxt = DECK.get(m.get("deck", 0), DECK[0])
    chips += f'<span class="wb deck {dcls}" title="{_e(dtxt)}">{ICONS["deck"]}Steam Deck: {dlab}</span>'
    ctl = {"full": "Full controller support", "partial": "Partial controller support"}.get(m.get("controller") or "")
    if ctl:
        chips += f'<span class="wb on">{ICONS["pad"]}{ctl}</span>'
    best = []
    if p.get("windows"):
        best.append("Windows PC")
    if m.get("deck") == 3:
        best.append("Steam Deck")
    elif m.get("deck") == 2:
        best.append("Steam Deck (playable)")
    if p.get("mac") and not p.get("windows"):
        best.append("Mac")
    if p.get("linux") and not p.get("windows"):
        best.append("Linux")
    head = ("Works best on " + " and ".join(best)) if best else "Platform details"
    return f'<section class="block"><div class="wrap"><h2>{_e(head)}</h2><div class="wbrow">{chips}</div></div></section>'


def specs_table(m):
    mn, rc = dict(m.get("min") or []), dict(m.get("rec") or [])
    labels = list(dict.fromkeys(list(mn) + list(rc)))
    if not labels:
        return ""
    rows = "".join(f"<tr><th scope=\"row\">{_e(l)}</th><td>{_e(mn.get(l, '-'))}</td><td>{_e(rc.get(l, '-'))}</td></tr>" for l in labels)
    return (f'<h3 class="sub">PC requirements</h3><div class="scroll"><table class="specs"><thead><tr><th></th><th>Minimum</th><th>Recommended</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def details_html(m):
    """Description, tags, screenshots, details and specs for a game page. Returns (above_fold_desc, body_html)."""
    tags = ""
    for g in m.get("genres", []):
        cid = GENRE_CAT.get(g)
        tags += (f'<a class="tag" href="/games.html#cat={cid}">{_e(g)}</a>' if cid else f'<span class="tag">{_e(g)}</span>')
    for f in m.get("features", []):
        tags += f'<span class="tag feat">{_e(f)}</span>'
    shots = "".join(f'<a href="{_e(s["f"])}" target="_blank" rel="noopener"><img src="{_e(s["t"])}" alt="Screenshot {i} of {_e(m.get("name"))}" loading="lazy" width="300" height="169"></a>'
                    for i, s in enumerate(m.get("shots", []), 1) if s.get("t") and s.get("f"))
    rows = []
    if m.get("dev"):
        rows.append(("Developer", ", ".join(m["dev"])))
    if m.get("pub"):
        rows.append(("Publisher", ", ".join(m["pub"])))
    if m.get("released"):
        rows.append(("Released", m["released"]))
    if m.get("meta"):
        rows.append(("Metacritic", f'{m["meta"]} / 100'))
    if m.get("langs"):
        rows.append(("Languages", f'{len(m["langs"])}: ' + ", ".join(m["langs"][:6]) + (" and more" if len(m["langs"]) > 6 else "")))
    drows = "".join(f"<tr><th scope=\"row\">{_e(k)}</th><td>{_e(v)}</td></tr>" for k, v in rows)
    tbl = ('<table class="specs det"><tbody>' + drows + "</tbody></table>") if drows else ""
    body = ""
    if tags:
        body += f'<section class="block"><div class="wrap"><h2>Categories</h2><div class="tags">{tags}</div></div></section>'
    if shots:
        body += f'<section class="block"><div class="wrap"><h2>Screenshots</h2><div class="shots">{shots}</div></div></section>'
    if drows or m.get("min") or m.get("rec"):
        body += f'<section class="block"><div class="wrap"><h2>Details</h2>{tbl}{specs_table(m)}</div></section>'
    return m.get("desc") or "", works_best_on(m) + body


def fallback_html():
    """Games without Steam details still get a platform line."""
    return ('<section class="block"><div class="wrap"><h2>Works best on</h2><div class="wbrow">'
            f'<span class="wb on">{ICONS["windows"]}Windows PC</span></div></div></section>')
