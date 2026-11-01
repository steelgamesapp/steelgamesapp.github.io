"""'Best gear for this game' picks for every game page.

Rules, products and wording live in tools/gear_rules.json so the static game pages (built here) and the live
price page (/deal/, built in the browser from /data/gear.json) always recommend the same things.

How a game is matched: Steam details (genres, VR / PvP / co-op features, controller support, Steam Deck rating,
recommended graphics card) when we have them, plus keywords in the title. Each match is a play style
(VR, racing, competitive...), each play style lists gear slots, and every slot has a best-value pick and an
upgrade pick. Prices are never shown here: Amazon prices change constantly, so buttons say "See price".
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = json.load(open(os.path.join(ROOT, "tools", "gear_rules.json")))
ITEMS, SLOTS, PROFILES = RULES["items"], RULES["slots"], RULES["profiles"]
ORDER, MAX = RULES["order"], RULES["max_slots"]
KW = {p: re.compile(rx, re.I) for p, rx in RULES["keywords"].items()}

# Only one slot from each group appears on a page (one monitor, one headset...).
GROUPS = {"comp_monitor": "monitor", "big_monitor": "monitor", "detail_monitor": "monitor",
          "comp_headset": "headset", "chat_headset": "headset", "immersive_headset": "headset",
          "controller": "pad", "sports_pad": "pad", "fps_mouse": "mouse", "strat_mouse": "mouse",
          "comp_kb": "kb", "type_kb": "kb"}
STYLE_NAMES = {"vr": "VR", "flight": "Flight", "racing": "Racing", "competitive": "Competitive multiplayer",
               "sports": "Sports", "coop": "Co-op and multiplayer", "horror": "Horror", "shooter": "Shooter",
               "strategy": "Strategy", "rpg": "RPG", "action": "Action", "casual": "Relaxed and indie", "general": "All-round"}
GENRES = {"Racing": "racing", "Sports": "sports", "Strategy": "strategy", "RPG": "rpg", "Action": "action", "Casual": "casual"}
VR_FEATS = {"VR Support", "VR Supported", "VR Only", "Tracked Controller Support"}
PVP_FEATS = {"Online PvP", "PvP", "MMO"}
COOP_FEATS = {"Online Co-op", "Co-op", "LAN Co-op", "Shared/Split Screen Co-op", "Multi-player"}
# Recommended graphics cards that mean "this game wants a strong GPU".
HEAVY_GPU = re.compile(r"rtx\s?[2-5]0[5-9]0|rtx\s?[2-5]0[6-9]0|gtx\s?10[78]0|gtx\s?1660|rx\s?[5-9][6-9]00|rx\s?[67]\d00|arc\s?a7", re.I)


def styles(title, meta=None):
    """Play styles for a game, most important first."""
    found = set()
    m = meta or {}
    feats = set(m.get("features") or [])
    if feats & VR_FEATS:
        found.add("vr")
    if feats & PVP_FEATS:
        found.add("competitive")
    if feats & COOP_FEATS:
        found.add("coop")
    for g in m.get("genres") or []:
        if g in GENRES:
            found.add(GENRES[g])
    if "Indie" in (m.get("genres") or []) and not found:
        found.add("casual")
    for p, rx in KW.items():
        if rx.search(title or ""):
            found.add(p)
    # A shooter with online PvP is a competitive game; drop the weaker label.
    if "competitive" in found:
        found.discard("shooter")
    out = [p for p in ORDER if p in found]
    return out or ["general"]


def slots_for(title, meta=None):
    """Ordered gear slot ids for a game (at most MAX)."""
    m = meta or {}
    st = styles(title, m)
    picked, groups = [], set()

    def add(s, front=False):
        if s in picked or s not in SLOTS:
            return
        grp = GROUPS.get(s)
        if grp and grp in groups:
            return
        if grp:
            groups.add(grp)
        picked.insert(0, s) if front else picked.append(s)

    # Interleave the top two play styles so a "horror + co-op" game gets both kinds of gear.
    lists = [PROFILES[p] for p in st[:2]]
    for i in range(max(len(x) for x in lists)):
        for lst in lists:
            if i < len(lst):
                add(lst[i])
    multiplayer = bool({"competitive", "coop", "sports"} & set(st))
    if multiplayer:
        add("mic")
    if m.get("controller") == "full":
        add("controller")
    rec_gpu = " ".join(v for k, v in (m.get("rec") or []) if "graphic" in k.lower() or "video" in k.lower())
    if rec_gpu and HEAVY_GPU.search(rec_gpu):
        add("gpu")
    if m.get("deck") == 3:
        add("deck_storage")
    for s in PROFILES["general"]:  # fill thin pages with the all-round basics
        if len(picked) >= 4:
            break
        add(s)
    return picked[:MAX], st


def _e(t):
    return html.escape(str(t or ""))


ARROW = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>')


def _fallback(slot):
    """If a product photo won't load, show a drawing of that kind of gear instead of an empty box."""
    return (f"this.onerror=null;this.src='/assets/gear-icons/{slot['icon']}.svg';"
            "this.closest('.gimg').classList.add('icon')")


ICON_SVG = {
    "platform": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
    "controls": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 8h10a4 4 0 0 1 4 4v1a3 3 0 0 1-5.2 2L14 13h-4l-1.8 2A3 3 0 0 1 3 13v-1a4 4 0 0 1 4-4z"/></svg>',
    "display": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="13" rx="2"/><path d="M9 21h6"/></svg>',
    "audio": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 15v-3a8 8 0 0 1 16 0v3"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/></svg>',
}
BW = RULES["bestway"]


def _first(rows, st):
    for p, txt in rows:
        if p in st:
            return txt
    return dict(rows)["general"]


def best_way(st, meta=None):
    """[(kind, label, value)] for the 'Best way to play' panel."""
    m = meta or {}
    plat = []
    if "vr" in st:
        plat.append("PC VR headset")
    pl = m.get("platforms") or {}
    if pl.get("windows", True):
        plat.append("Windows PC")
    deck = m.get("deck")
    if deck == 3:
        plat.append("Steam Deck (Verified)")
    elif deck == 2:
        plat.append("Steam Deck (Playable)")
    if pl.get("mac"):
        plat.append("Mac")
    if pl.get("linux"):
        plat.append("Linux")
    controls = _first(BW["controls"], st)
    ctl = m.get("controller")
    if ctl == "full" and controls in ("Mouse and keyboard", "Mouse and keyboard or controller"):
        controls = "Mouse and keyboard, or a controller (fully supported)"
    elif ctl == "full" and controls.startswith("Controller or"):
        controls = "Controller (fully supported) or mouse and keyboard"
    elif not ctl and m and controls == "Controller":
        controls = "Mouse and keyboard (no official controller support)"
    return [("platform", "Works best on", " · ".join(plat)), ("controls", "Best controls", controls),
            ("display", "Best screen", _first(BW["display"], st)), ("audio", "Best sound", _first(BW["audio"], st))]


def best_way_html(st, meta=None):
    tiles = "".join(f'<div class="bw"><span class="bwi">{ICON_SVG[k]}</span><span><small>{_e(lab)}</small>{_e(val)}</span></div>'
                    for k, lab, val in best_way(st, meta))
    return f'<h3 class="sub">Best way to play</h3><div class="bestway">{tiles}</div>'


def card(slot_id, title):
    s = SLOTS[slot_id]
    v = ITEMS[s["value"]]
    up = ITEMS.get(s.get("up") or "")
    rel = 'target="_blank" rel="sponsored nofollow noopener"'
    upg = ""
    if up:
        upg = (f'<a class="gup" href="{_e(up["url"])}" {rel}><img src="{_e(up["img"])}" alt="" loading="lazy" width="56" height="56" '
               f'onerror="this.onerror=null;this.src=\'/assets/gear-icons/{s["icon"]}.svg\'"><span><small>Upgrade pick</small>{_e(up["name"])}</span></a>')
    return (f'<article class="gcar"><p class="gl">{_e(s["label"])}</p>'
            f'<a class="gimg" href="{_e(v["url"])}" {rel} tabindex="-1" aria-hidden="true"><img src="{_e(v["img"])}" alt="{_e(v["name"])}" '
            f'loading="lazy" width="400" height="300" onerror="{_fallback(s)}"></a>'
            f'<div class="gb"><span class="gtag">Best value</span><h3>{_e(v["name"])}</h3><p>{_e(s["why"].replace("{t}", title))}</p>'
            f'<a class="btn gbuy" href="{_e(v["url"])}" {rel}>See price on Amazon{ARROW}</a>{upg}</div></article>')


def section(title, meta=None):
    """The full 'Best gear for <game>' block for a static game page, wrapped in markers so it can be refreshed."""
    picks, st = slots_for(title, meta)
    chips = "".join(f'<span class="tag">{_e(STYLE_NAMES.get(p, p))}</span>' for p in st[:3])
    cards = "".join(card(s, title) for s in picks)
    return (f'<!--gear--><section class="block gear"><div class="wrap"><h2>Best gear for {_e(title)}</h2>'
            f'<p class="lede gear-lede">How this game plays best, and the gear to match: a best-value pick and an upgrade for each.</p>'
            f'<div class="tags">{chips}</div>{best_way_html(st, meta)}<h3 class="sub">Recommended gear</h3><div class="gear-grid">{cards}</div>'
            f'<p class="fine">Prices change often, so check the latest price on Amazon. SteelGames may earn a small commission on purchases.</p>'
            f'</div></section><!--/gear-->')


GEAR_RE = re.compile(r"<!--gear-->.*?<!--/gear-->", re.S)


def inject(page_html, title, meta=None):
    """Add or refresh the gear block in an existing game page (used for pages kept from an earlier build)."""
    block = section(title, meta)
    if GEAR_RE.search(page_html):
        return GEAR_RE.sub(lambda _: block, page_html, count=1)
    anchor = '<section class="block"><div class="wrap"><h2>Questions</h2>'
    if anchor in page_html:
        return page_html.replace(anchor, block + "\n" + anchor, 1)
    return page_html.replace("</main>", block + "\n</main>", 1)


def write_json(game_slots, path=None):
    """Rules plus each tracked game's picks, for the live /deal/ page."""
    path = path or os.path.join(ROOT, "data", "gear.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = {k: RULES[k] for k in ("items", "slots", "profiles", "keywords", "order", "max_slots", "bestway")}
    out["groups"], out["names"], out["games"], out["icons"] = GROUPS, STYLE_NAMES, game_slots, ICON_SVG
    json.dump(out, open(path, "w"), separators=(",", ":"))
