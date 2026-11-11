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
SCHEMA = 2  # bump to make every cached game refresh once (v2 adds trailers and more screenshots)
BUDGET = 150  # games refreshed per build, so the daily run stays quick and polite
_used = 0
OFFLINE = False

GENRE_CAT = {"Action": "action", "Adventure": "adventure", "RPG": "rpg", "Strategy": "strategy", "Simulation": "sim",
             "Racing": "racing", "Sports": "sports"}
FEATURES = ["Single-player", "Multi-player", "Co-op", "Online Co-op", "LAN Co-op", "Shared/Split Screen Co-op",
            "Online PvP", "PvP", "MMO", "VR Supported", "VR Support", "VR Only", "Tracked Controller Support", "Steam Achievements", "Steam Cloud", "Remote Play on TV", "Steam Trading Cards", "Family Sharing"]
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


def _movies(raw):
    """Official trailers from the store page: HLS stream (plays in every modern browser through hls.js) plus the old mp4 as a backup."""
    out = []
    for mv in (raw or [])[:2]:
        hls = mv.get("hls_h264") or ""
        if not hls and not mv.get("id"):
            continue
        out.append({"id": mv.get("id"), "n": _strip(mv.get("name")), "t": mv.get("thumbnail"), "hls": hls,
                    "mp4": f"https://cdn.akamai.steamstatic.com/steam/apps/{mv.get('id')}/movie480.mp4" if mv.get("id") else ""})
    return out


def compact(d, deck):
    plat = d.get("platforms") or {}
    pcr = d.get("pc_requirements") or {}
    pcr = pcr if isinstance(pcr, dict) else {}
    cats = [c.get("description", "") for c in d.get("categories", []) or []]
    feats = [c for c in FEATURES if c in cats]
    return {
        "name": d.get("name"),
        "appid": d.get("steam_appid"),
        "desc": _strip(d.get("short_description")),
        "header": d.get("header_image"),
        "shots": [{"t": s.get("path_thumbnail"), "f": s.get("path_full")} for s in (d.get("screenshots") or [])[:12]],
        "movies": _movies(d.get("movies")),
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


_BLURBS = None


def blurb(appid):
    """Our own written summary for a game (data/blurbs.json), kept apart from Steam's cache so a refresh never wipes it."""
    global _BLURBS
    if _BLURBS is None:
        try:
            _BLURBS = json.load(open(os.path.join(ROOT, "data", "blurbs.json")))
        except Exception:
            _BLURBS = {}
    return _BLURBS.get(str(appid)) or ""


def load(appid):
    try:
        return json.load(open(_path(appid)))
    except Exception:
        return None


def _save(appid, d, fetched=None):
    os.makedirs(DIR, exist_ok=True)
    json.dump({"fetched": fetched or date.today().isoformat(), "v": SCHEMA, "d": d}, open(_path(appid), "w"), separators=(",", ":"))


def _with_blurb(c, appid):
    """Return the game's details with our own written summary merged in. The same file is what the live /deal/ page reads,
    so when blurbs.json changes the cached file is rewritten to match."""
    d = dict(c["d"])
    b = blurb(appid)
    if (d.get("blurb") or "") != b:
        d["blurb"] = b
        if not b:
            d.pop("blurb")
        if c.get("v") == SCHEMA:
            _save(appid, d, c.get("fetched"))
    return d


def get(appid):
    """Return compact metadata for a Steam app id (cached), or None."""
    global _used
    appid = str(appid or "")
    if not appid.isdigit() or appid == "0":
        return None
    c = load(appid)
    fresh = c and c.get("v") == SCHEMA and (date.today() - datetime.strptime(c["fetched"], "%Y-%m-%d").date()).days < TTL_DAYS
    if fresh or OFFLINE or _used >= BUDGET:
        return _with_blurb(c, appid) if c else None
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
        c = {"fetched": date.today().isoformat(), "v": SCHEMA, "d": d}
        _save(appid, d)
        time.sleep(1.2)
        return _with_blurb(c, appid)
    except Exception:
        return _with_blurb(c, appid) if c else None


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


def _ico(name):
    return ICONS[name]


ICONS["pc"] = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4" width="19" height="12.5" rx="2"/><path d="M8 20.5h8M12 16.5v4"/></svg>'
ICONS["handheld"] = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="1.5" y="6.5" width="21" height="11" rx="4"/><path d="M6.5 10.5v3M5 12h3"/><circle cx="16.5" cy="11" r=".9"/><circle cx="18.5" cy="13" r=".9"/></svg>'
ICONS["ctl"] = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 8h10a4 4 0 0 1 4 4v1a3 3 0 0 1-5.2 2L14 13h-4l-1.8 2A3 3 0 0 1 3 13v-1a4 4 0 0 1 4-4z"/></svg>'
ICONS["kbm"] = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="7" width="14" height="10" rx="2"/><path d="M5 10.5h1M8.5 10.5h1M12 10.5h1M5.5 14h7"/><rect x="18" y="5" width="4" height="7" rx="2"/></svg>'
ICONS["players"] = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17.5" cy="9" r="2.4"/><path d="M17 14.2c2.4.3 4.5 2.2 4.5 4.8"/></svg>'
ICONS["vr"] = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5h18a1 1 0 0 1 1 1V15a2 2 0 0 1-2 2h-3.5l-1.7-2.5h-4.6L8.5 17H5a2 2 0 0 1-2-2V9.5a1 1 0 0 1 0-1z"/></svg>'


def best_on(m):
    """What this game works best on, as (headline, [(icon, label, value, state)]). Drives the strip at the top of every game page.
    Mirrored in assets/gamedetails.js for the live /deal/ page, so change both together."""
    p = m.get("platforms") or {}
    feats = m.get("features") or []
    deck = m.get("deck", 0)
    plats = [n for k, n in (("windows", "Windows PC"), ("mac", "Mac"), ("linux", "Linux")) if p.get(k)] or ["Windows PC"]
    best = [plats[0]]
    if deck == 3:
        best.append("Steam Deck")
    elif deck == 2:
        best.append("Steam Deck (playable)")
    head = "Works best on " + " and ".join(best)
    tiles = [("pc", "Platform", " · ".join(plats), "good")]
    if deck == 3:
        tiles.append(("handheld", "Handheld", "Steam Deck Verified, so it should run well on handheld PCs like the Steam Deck and ROG Ally.", "good"))
    elif deck == 2:
        tiles.append(("handheld", "Handheld", "Steam Deck Playable. Works on handheld PCs, but may need small tweaks.", "ok"))
    elif deck == 1:
        tiles.append(("handheld", "Handheld", "Not supported on Steam Deck. Best on a desktop or laptop.", "bad"))
    else:
        tiles.append(("handheld", "Handheld", "Steam Deck rating not available yet.", ""))
    ctl = m.get("controller")
    if ctl == "full":
        tiles.append(("ctl", "Controls", "Full controller support. Plays well on a gamepad or keyboard and mouse.", "good"))
    elif ctl == "partial":
        tiles.append(("ctl", "Controls", "Partial controller support. Keyboard and mouse is the safer pick.", "ok"))
    else:
        tiles.append(("kbm", "Controls", "Made for keyboard and mouse.", ""))
    modes = [n for k, n in (("Single-player", "Single-player"), ("Co-op", "Co-op"), ("Online Co-op", "Online co-op"), ("Shared/Split Screen Co-op", "Split-screen co-op"),
                            ("Multi-player", "Multiplayer"), ("Online PvP", "Online PvP"), ("MMO", "MMO")) if k in feats]
    modes = list(dict.fromkeys(modes))[:3]
    vr = any(f in feats for f in ("VR Supported", "VR Support", "VR Only"))
    if vr:
        modes.append("VR")
    if modes:
        tiles.append(("vr" if "VR" in modes and len(modes) == 1 else "players", "Play style", " · ".join(modes), ""))
    return head, tiles


def strip_html(m=None):
    """The 'Works best on' strip shown right under the game title. Games without Steam details still get a platform tile."""
    head, tiles = best_on(m) if m else ("Works best on Windows PC", [("pc", "Platform", "Windows PC", "good")])
    t = "".join(f'<div class="wbt {_e(st)}"><span class="wbi">{ICONS[ic]}</span><span class="wbx"><small>{_e(lab)}</small>{_e(val)}</span></div>' for ic, lab, val, st in tiles)
    return f'<div class="wbstrip" role="group" aria-label="Works best on"><p class="wbhead">{_e(head)}</p><div class="wbtiles">{t}</div></div>'


def specs_table(m):
    mn, rc = dict(m.get("min") or []), dict(m.get("rec") or [])
    labels = list(dict.fromkeys(list(mn) + list(rc)))
    if not labels:
        return ""
    rows = "".join(f"<tr><th scope=\"row\">{_e(l)}</th><td>{_e(mn.get(l, '-'))}</td><td>{_e(rc.get(l, '-'))}</td></tr>" for l in labels)
    return (f'<h3 class="sub">PC requirements</h3><div class="scroll"><table class="specs"><thead><tr><th></th><th>Minimum</th><th>Recommended</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def about_html(m):
    """Our own written summary of the game (data/blurbs.json), when we have one."""
    b = (m.get("blurb") or "").strip()
    if not b:
        return ""
    paras = "".join(f"<p>{_e(x.strip())}</p>" for x in b.split("\n\n") if x.strip())
    return f'<section class="block about"><div class="wrap"><h2>About {_e(m.get("name") or "this game")}</h2><div class="prose">{paras}</div></div></section>'


PLAY = '<svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.9l10.5-6.5a1 1 0 0 0 0-1.8L9.5 4.6A1 1 0 0 0 8 5.5z"/></svg>'


def media_html(m):
    """Official trailer plus screenshots. Works as plain links with no JavaScript; assets/gamedetails.js adds the player and the viewer."""
    name = m.get("name") or "this game"
    shots = [s for s in m.get("shots", []) if s.get("t") and s.get("f")]
    movies = [v for v in (m.get("movies") or []) if v.get("hls") or v.get("mp4")]
    if not shots and not movies:
        return ""
    trailer = ""
    if movies:
        mv = movies[0]
        poster = (shots[0]["t"] if shots else mv.get("t")) or ""
        trailer = (f'<button type="button" class="trailer" data-hls="{_e(mv.get("hls"))}" data-mp4="{_e(mv.get("mp4"))}" data-poster="{_e(poster)}" aria-label="Play the {_e(name)} trailer">'
                   f'<img src="{_e(poster)}" alt="Trailer preview" loading="lazy" width="600" height="338"><span class="play">{PLAY}</span><span class="tcap">Watch the trailer</span></button>')
    cells = "".join(f'<a href="{_e(s["f"])}" target="_blank" rel="noopener" data-full="{_e(s["f"])}"><img src="{_e(s["t"])}" alt="Screenshot {i} of {_e(name)}" loading="lazy" width="300" height="169"></a>'
                    for i, s in enumerate(shots, 1))
    return (f'<section class="block" id="media"><div class="wrap"><h2>Trailer and screenshots</h2>'
            f'<div class="media" data-gallery data-name="{_e(name)}">{trailer}<div class="shots">{cells}</div></div>'
            f'<p class="fine">Trailer and screenshots are from the publisher. Tap a screenshot to enlarge it.</p></div></section>')


def details_html(m):
    """About, trailer, screenshots, details and specs for a game page. Returns (above_fold_desc, body_html)."""
    tags = ""
    for g in m.get("genres", []):
        cid = GENRE_CAT.get(g)
        tags += (f'<a class="tag" href="/games.html#cat={cid}">{_e(g)}</a>' if cid else f'<span class="tag">{_e(g)}</span>')
    for f in m.get("features", []):
        tags += f'<span class="tag feat">{_e(f)}</span>'
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
    body = about_html(m) + media_html(m)
    if tags:
        body += f'<section class="block"><div class="wrap"><h2>Categories</h2><div class="tags">{tags}</div></div></section>'
    if drows or m.get("min") or m.get("rec"):
        body += f'<section class="block"><div class="wrap"><h2>Details</h2>{tbl}{specs_table(m)}</div></section>'
    return m.get("desc") or "", body


def fallback_html():
    """Games without Steam details get no extra sections (the strip at the top still shows the platform)."""
    return ""
