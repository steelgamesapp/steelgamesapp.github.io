"""Daily key-deals feed for /keys.html ("Today's key deals").

Called from keys_page.build() every time the site is rebuilt (3 times a day by .github/workflows/seo.yml).
  * Pulls current sales from the key stores through the CheapShark API.
  * Picks about a dozen well-reviewed games: one card per game at its cheapest key store, a few per store,
    skipping games shown in the last few days so the list feels fresh each day.
  * Keeps the same games for the whole UTC day (prices are refreshed on each rebuild, a game that is no
    longer on sale is swapped for a new one).
  * Saves data/key_deals.json (today's picks plus the last week) so a failed API call never empties the page.

This module never raises: on any problem build() returns the last saved picks, or an empty string.
Standard library only.
"""
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.environ.get("KEY_DEALS_FILE") or os.path.join(ROOT, "data", "key_deals.json")
API = "https://www.cheapshark.com/api/1.0"
UA = "SteelGames-Build/1.0 (steelgames.app@outlook.com)"

PICKS = 12            # cards shown
PER_STORE = 3         # at most this many cards from one store
MIN_OFF = 35          # percent off
MIN_RATING = 75       # Steam positive percent
MIN_REVIEWS = 150     # Steam review count, filters out unknown games
MAX_PRICE = 60.0
SKIP_DAYS = 3         # do not repeat a game shown in the last N days if there are enough others
KEEP_DAYS = 7
SKIP_TITLE = re.compile(r"soundtrack|\bost\b|artbook|art book|wallpaper|\bdemo\b|\bdlc\b|season pass|expansion pass|upgrade|supporter|\bbeta\b|dedicated server", re.I)

_state = {"limited": False}


def _get(path, params=None, tries=2):
    """GET JSON from CheapShark. Gives up fast on rate limits; the caller falls back to saved picks."""
    if _state["limited"]:
        raise RuntimeError("price API rate limited")
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as ex:
            if ex.code == 429:
                _state["limited"] = True
                raise
            if ex.code not in (500, 502, 503, 504) or attempt == tries - 1:
                raise
            time.sleep(3)
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == tries - 1:
                raise
            time.sleep(3)


def _load():
    try:
        with open(DATA) as f:
            d = json.load(f)
        if isinstance(d, dict) and isinstance(d.get("days"), list):
            return d
    except Exception:
        pass
    return {"days": []}


def _save(d):
    try:
        os.makedirs(os.path.dirname(DATA), exist_ok=True)
        with open(DATA, "w") as f:
            json.dump(d, f, indent=1)
            f.write("\n")
    except Exception as ex:
        print("key_deals: could not save", ex)


def _f(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _pick_row(x, store_name):
    return {
        "gameID": str(x["gameID"]), "dealID": x["dealID"], "title": x["title"],
        "store": store_name, "sale": round(_f(x["salePrice"]), 2), "normal": round(_f(x["normalPrice"]), 2),
        "off": int(round(_f(x["savings"]))), "rating": int(_f(x.get("steamRatingPercent"))),
        "reviews": int(_f(x.get("steamRatingCount"))), "steam": str(x.get("steamAppID") or "0"),
        "thumb": x.get("thumb") or "", "score": round(_f(x.get("dealRating")), 1), "low": None,
    }


def fetch_candidates(resellers):
    """{gameID: best listing} across the key stores, only deals that pass the quality bar."""
    stores = _get("/stores")
    want = {}
    for r in resellers:
        name = r[0]
        if not name:
            continue
        s = next((x for x in stores if x.get("isActive") in (1, "1", True) and x["storeName"] == name), None)
        if s:
            want[str(s["storeID"])] = r[1]  # CheapShark store id -> display name
    best = {}
    for sid, shown in want.items():
        try:
            rows = _get("/deals", {"storeID": sid, "onSale": 1, "sortBy": "Deal Rating", "pageSize": 40,
                                   "steamRating": MIN_RATING, "upperPrice": MAX_PRICE})
        except Exception as ex:
            print("key_deals: store", shown, "failed:", ex)
            if _state["limited"]:
                break
            continue
        for x in rows:
            price, off = _f(x["salePrice"]), _f(x["savings"])
            if price <= 0 or off < MIN_OFF or _f(x.get("steamRatingPercent")) < MIN_RATING:
                continue
            if _f(x.get("steamRatingCount")) < MIN_REVIEWS or SKIP_TITLE.search(x["title"]):
                continue
            row = _pick_row(x, shown)
            cur = best.get(row["gameID"])
            if cur is None or row["sale"] < cur["sale"]:
                best[row["gameID"]] = row
        time.sleep(0.4)
    return best


def add_lowest(rows):
    """Lowest price ever recorded (CheapShark's cheapestPriceEver), used for the 'Matches its lowest price' flag."""
    ids = [r["gameID"] for r in rows]
    for i in range(0, len(ids), 25):
        chunk = ids[i:i + 25]
        try:
            info = _get("/games", {"ids": ",".join(chunk)})
        except Exception as ex:
            print("key_deals: lowest-price lookup failed:", ex)
            return
        for r in rows:
            g = info.get(r["gameID"]) if isinstance(info, dict) else None
            if g and g.get("cheapestPriceEver"):
                r["low"] = round(_f(g["cheapestPriceEver"]["price"]), 2)


def choose(cands, recent, keep=()):
    """Pick PICKS games: keep today's earlier picks that are still on sale, fill the rest by deal rating."""
    chosen, per = [], {}
    for gid in keep:
        if gid in cands and len(chosen) < PICKS:
            c = cands[gid]
            chosen.append(c)
            per[c["store"]] = per.get(c["store"], 0) + 1
    ranked = sorted((c for c in cands.values() if c["gameID"] not in {x["gameID"] for x in chosen}),
                    key=lambda c: (c["score"], c["off"], c["reviews"]), reverse=True)
    fresh = [c for c in ranked if c["gameID"] not in recent]
    stale = [c for c in ranked if c["gameID"] in recent]
    for pool in (fresh, stale):
        for c in pool:
            if len(chosen) >= PICKS:
                break
            if per.get(c["store"], 0) >= PER_STORE:
                continue
            chosen.append(c)
            per[c["store"]] = per.get(c["store"], 0) + 1
    return chosen


def refresh(resellers, now=None):
    """Update data/key_deals.json for today and return it. Falls back to the saved file on any failure."""
    now = now or datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    data = _load()
    days = [d for d in data["days"] if d.get("date")]
    try:
        cands = fetch_candidates(resellers)
        if len(cands) < 4:
            raise RuntimeError(f"only {len(cands)} qualifying deals, keeping saved picks")
        todays = next((d for d in days if d["date"] == today), None)
        older = [d for d in days if d["date"] != today]
        recent = {p["gameID"] for d in older[:SKIP_DAYS] for p in d["picks"]}
        keep = [p["gameID"] for p in todays["picks"]] if todays else []
        chosen = choose(cands, recent, keep)
        add_lowest(chosen)
        for c in chosen:  # carry over a known lowest price if the lookup failed this run
            if c["low"] is None and todays:
                old = next((p for p in todays["picks"] if p["gameID"] == c["gameID"]), None)
                c["low"] = old.get("low") if old else None
        entry = {"date": today, "updated": now.strftime("%Y-%m-%d %H:%M UTC"), "picks": chosen}
        days = [entry] + older
        days.sort(key=lambda d: d["date"], reverse=True)
        data = {"days": days[:KEEP_DAYS]}
        _save(data)
        print(f"key_deals: {len(chosen)} picks for {today} from {len(cands)} candidates")
    except Exception as ex:
        print("key_deals: using saved picks:", ex)
    return data


# ---------------------------------------------------------------- rendering

CSS = """<style>
.kd-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap}
.kd-head p{margin:0}
.kd-date{display:inline-flex;align-items:center;gap:8px;font:700 12px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--off-fg);background:var(--off-bg);border:1px solid rgba(124,240,168,.35);padding:5px 12px;border-radius:999px}
.kd-date::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--good);box-shadow:0 0 0 3px rgba(92,224,138,.25)}
.kd-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
@media (max-width:980px){.kd-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:620px){.kd-grid{grid-template-columns:minmax(0,1fr)}}
.kd-card{--c:#7B5CFF;display:flex;flex-direction:column;border-radius:16px;overflow:hidden;background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--c);min-width:0;transition:transform .15s ease,border-color .15s ease}
.kd-card:hover{transform:translateY(-3px);border-color:var(--c)}
.kd-pic{position:relative;display:block;aspect-ratio:460/215;background:#0A0619}
.kd-pic img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.kd-off{position:absolute;top:10px;left:10px;padding:4px 10px;border-radius:8px;font:700 15px var(--display);background:var(--off-bg);color:var(--off-fg);border:1px solid rgba(124,240,168,.35);box-shadow:0 2px 8px rgba(0,0,0,.45)}
.kd-low{position:absolute;bottom:8px;right:8px;padding:3px 9px;border-radius:999px;font:700 11px var(--body);letter-spacing:.04em;text-transform:uppercase;background:rgba(255,176,32,.95);color:var(--accent-ink)}
.kd-body{display:flex;flex-direction:column;gap:10px;padding:14px 16px 16px;flex:1;min-width:0}
.kd-title{font:600 18px/1.3 var(--display);color:#fff;text-decoration:none;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.kd-title:hover{color:var(--accent-soft)}
.kd-sub{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:12px;color:var(--muted)}
.kd-sub b{color:var(--c);font-weight:700}
.kd-price{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-top:auto;font-variant-numeric:tabular-nums}
.kd-price strong{font:700 28px var(--display);color:#fff}
.kd-price s{font-size:14px;color:var(--muted)}
.kd-price span{font-size:12px;color:var(--muted)}
.kd-acts{display:flex;flex-direction:column;gap:8px}
.kd-acts .kbuy{width:100%}
.kd-acts .kd-cmp{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 14px;border-radius:10px;border:1px solid var(--line-strong);background:var(--bg);color:#fff;font:600 14px var(--body);text-decoration:none}
.kd-acts .kd-cmp:hover{background:var(--raised);color:#fff}
.kd-old{border:1px solid var(--line);border-radius:14px;background:var(--surface)}
.kd-old summary{cursor:pointer;padding:14px 18px;font:600 16px var(--display);list-style:none;display:flex;justify-content:space-between;align-items:center;gap:10px}
.kd-old summary::-webkit-details-marker{display:none}
.kd-old summary::after{content:"+";font-size:22px;color:var(--accent-soft)}
.kd-old[open] summary::after{content:"\\2212"}
.kd-day{padding:0 18px 16px}
.kd-day h3{font:700 12px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:14px 0 8px}
.kd-day ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 18px}
@media (max-width:700px){.kd-day ul{grid-template-columns:minmax(0,1fr)}}
.kd-day li{display:flex;justify-content:space-between;gap:10px;font-size:14px;border-bottom:1px solid var(--line);padding:6px 0;min-width:0}
.kd-day li a{color:#fff;text-decoration:none;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.kd-day li a:hover{color:var(--accent-soft)}
.kd-day li span{color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
@media (prefers-reduced-motion:reduce){.kd-card{transition:none}}
</style>
"""


def _e(s):
    return html.escape(str(s), quote=True)


def _money(v):
    return f"${float(v):,.2f}"


def _pretty(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%b %d").replace(" 0", " ")
    except ValueError:
        return date_str


def _updated(day):
    """'Nov 8, 21:19 UTC' from the saved '2026-11-08 21:19 UTC' stamp."""
    raw = day.get("updated", "")
    try:
        d = datetime.strptime(raw.replace(" UTC", ""), "%Y-%m-%d %H:%M")
        return d.strftime("%b %d, %H:%M UTC").replace(" 0", " ")
    except ValueError:
        return raw


def _buy_url(p, aff):
    """CheapShark redirect to the exact deal. CheapShark requires its redirect for every store it
    tracks (that is the condition for its free price data), so these links are never swapped for a
    store search or a store's own affiliate link."""
    return "https://www.cheapshark.com/redirect?dealID=" + urllib.parse.quote(p["dealID"], safe="%")


def _art(p):
    if p["steam"] and p["steam"] != "0":
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{p['steam']}/header.jpg"
    return p["thumb"]


def _card(p, meta, aff, first):
    color, trust = meta.get(p["store"], ("#7B5CFF", ""))
    low = p.get("low")
    at_low = low is not None and p["sale"] <= low + 0.005
    img = _art(p)
    thumb = _e(p["thumb"])
    fallback = f" onerror=\"this.onerror=null;this.src='{thumb}'\"" if p["thumb"] and p["thumb"] != img else ""
    eager = "" if first else ' loading="lazy"'
    rating = f"<span>{p['rating']}% positive</span>" if p["rating"] else ""
    tag = f'<span class="tag">{_e(trust)}</span>' if trust else ""
    was = f"<s>{_money(p['normal'])}</s>" if p["normal"] > p["sale"] else ""
    lowline = ""
    if low is not None and not at_low:
        lowline = f"<span>Lowest ever {_money(low)}</span>"
    return (
        f'<article class="kd-card" style="--c:{_e(color)}">'
        f'<a class="kd-pic" href="/deal/?id={_e(p["gameID"])}" tabindex="-1" aria-hidden="true">'
        f'<img src="{_e(img)}" alt="" width="460" height="215" decoding="async"{eager}{fallback}>'
        f'<span class="kd-off">-{p["off"]}%</span>' + ('<span class="kd-low">Lowest price ever</span>' if at_low else "") + "</a>"
        f'<div class="kd-body"><a class="kd-title" href="/deal/?id={_e(p["gameID"])}">{_e(p["title"])}</a>'
        f'<div class="kd-sub"><b>{_e(p["store"])}</b>{tag}{rating}</div>'
        f'<div class="kd-price"><strong>{_money(p["sale"])}</strong>{was}{lowline}</div>'
        f'<div class="kd-acts"><a class="kbuy" data-store="{_e(p["store"])}" href="{_e(_buy_url(p, aff))}" target="_blank" rel="sponsored nofollow noopener">Buy at {_e(p["store"])}</a>'
        f'<a class="kd-cmp" href="/deal/?id={_e(p["gameID"])}">Compare prices</a></div></div></article>')


def render(data, resellers, aff=None):
    days = data.get("days") or []
    if not days or not days[0].get("picks"):
        return ""
    aff = aff or {}
    meta = {r[1]: (r[2], {"auth": "Authorized retailer", "keys": "Key store", "mkt": "Marketplace"}.get(r[3], "")) for r in resellers}
    today = days[0]
    cards = "".join(_card(p, meta, aff, i < 3) for i, p in enumerate(today["picks"]))
    older = ""
    for d in days[1:4]:
        items = "".join(
            f'<li><a href="/deal/?id={_e(p["gameID"])}">{_e(p["title"])}</a><span>{_money(p["sale"])} at {_e(p["store"])}</span></li>'
            for p in d["picks"][:8])
        older += f'<h3>{_e(_pretty(d["date"]))}</h3><ul>{items}</ul>'
    arch = (f'<details class="kd-old"><summary>Earlier this week</summary><div class="kd-day">{older}'
            '<p class="fine">Prices shown are what they were when we posted them. Open a game to see today\'s price at every store.</p></div></details>') if older else ""
    when = _pretty(today["date"])
    upd = _e(_updated(today))
    return (CSS + f'<section class="block" id="today"><div class="wrap">'
            f'<div class="kd-head"><div><h2>Today\'s key deals</h2>'
            f'<p class="fine">Fresh picks every day from the key stores: well-reviewed games at a real discount, one price per game at the cheapest store we track.</p></div>'
            f'<span class="kd-date">Posted {_e(when)}</span></div>'
            f'<div class="kd-grid">{cards}</div>'
            f'<p class="fine">Prices checked {upd} and can change at any time, so confirm the final price at checkout. Keys are digital: check the platform and region on the store page before you buy.</p>'
            f'{arch}</div></section>\n')


def section(resellers, aff=None):
    """HTML for the keys page. Never raises."""
    try:
        data = refresh(resellers)
        return render(data, resellers, aff)
    except Exception as ex:
        print("key_deals: section skipped:", ex)
        return ""


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    import keys_page
    out = section(keys_page.RESELLERS)
    print(len(out), "bytes of HTML")
