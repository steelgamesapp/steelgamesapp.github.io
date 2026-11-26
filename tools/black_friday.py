"""SteelGames Black Friday / Cyber Monday deals hub: /black-friday/.

Live sale prices come from our partner brands' own Impact product feeds (USD feeds only, discount of 10%+
versus the brand's own list price), so every Buy button is our tracked link:
  gear   - SOLAKAKA, AutoFull, Edifier, Twinkly, Satechi, UPERFECT, Lemorele (whichever have sale items)
  games  - Loaded (PC game keys, USD feed, 25%+ off)
  cards  - the best gift card prices from data/giftcards.json (tools/giftcards.py)
Plus hand-picked store-wide sales (Amazon, Redragon, GMKtec, Kinguin, Gameseal, Loaded) in STORE_SALES.
No Amazon prices are shown (Associates rules). After Dec 1 the page switches to "holiday deals" wording.

Run by .github/workflows/giftcards.yml after the gift card refresh (every 3 hours).
Usage: python3 tools/black_friday.py            (feeds, needs IMPACT_ACCOUNT_SID / IMPACT_AUTH_TOKEN)
       python3 tools/black_friday.py --page-only (rebuild the page from data/black_friday.json)
"""
import html
import json
import os
import re
import sys
import time
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout  # noqa: E402
from giftcards import Impact, now, age_days  # noqa: E402

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "black_friday.json")
CARDS = os.path.join(ROOT, "data", "giftcards.json")
OUT = os.path.join(ROOT, "black-friday", "index.html")
e = html.escape

GEAR_BRANDS = {  # CampaignName contains -> display name, what to keep (regex on product name; None = all)
    "solakaka": ("SOLAKAKA", None),
    "autofull": ("AutoFull", None),
    "edifier": ("Edifier", None),
    "twinkly": ("Twinkly", None),
    "uperfect": ("UPERFECT", None),
    "satechi": ("Satechi", r"keyboard|monitor stand|ssd|mouse|controller"),
    "lemorele": ("Lemorele", r"hub|dock|kvm|adapter|switch|charger"),
}
GEAR_QUERIES = ["gaming keyboard", "gaming mouse", "mechanical keyboard", "gaming headset", "gaming speakers", "speakers",
                "gaming monitor", "portable monitor", "gaming chair", "gaming desk", "led lights gaming", "light bar",
                "usb-c hub", "charger", "earbuds", "headphones", "controller"]
GAME_QUERIES = ["Call of Duty PC", "Battlefield 6 PC", "EA SPORTS FC 26 PC", "Arc Raiders PC", "Elden Ring PC", "Cyberpunk 2077 PC",
                "Red Dead Redemption 2 PC", "Hogwarts Legacy PC", "Baldur's Gate 3 PC", "Monster Hunter Wilds PC", "Helldivers 2 PC",
                "Borderlands 4 PC", "Assassin's Creed PC", "Resident Evil PC", "Final Fantasy PC", "Forza Horizon PC",
                "The Sims 4 PC", "Diablo IV PC", "Minecraft PC", "Black Myth Wukong PC", "Silent Hill PC", "Doom PC"]
CAT = [("keyboard", "Keyboards"), ("mouse", "Mice"), ("chair|desk", "Chairs and desks"), ("monitor", "Monitors"),
       ("speaker|headset|headphone|earbud|audio", "Audio"), ("light|lamp|strip|bar", "Lights"), ("", "Accessories")]

STORE_SALES = [
    {"name": "Amazon Black Friday", "what": "Amazon's full Black Friday and Cyber Monday deals page.",
     "url": "https://www.amazon.com/blackfriday?tag=steelgames-20", "btn": "See deals on Amazon"},
    {"name": "Redragon BFCM sale", "what": "Redragon's Black Friday and Cyber Monday page: keyboards, mice, headsets.",
     "url": "https://redragonshop.com/pages/black-friday-cyber-monday?aff=7360", "btn": "Shop Redragon"},
    {"name": "GMKtec mini PCs", "what": "GMKtec's Black Friday mini PC sale (their store says 30-day price protection).",
     "url": "https://www.awin1.com/cread.php?awinmid=45751&awinaffid=3137720", "btn": "Shop GMKtec"},
    {"name": "UPERFECT portable monitors", "what": "UPERFECT's Black Friday sale on portable and gaming monitors.",
     "url": "https://uperfect.sjv.io/1GBBGg", "btn": "Shop UPERFECT"},
    {"name": "Loaded game keys", "what": "PC game keys and gift cards (Loaded is the store formerly called CDKeys).",
     "url": "https://go.loaded.com/4a7vz9", "btn": "Shop Loaded"},
    {"name": "Kinguin marketplace", "what": "Game keys and gift cards from marketplace sellers. Check seller ratings.",
     "url": "https://kinguin.sjv.io/c/8059330/3827272/50048?subId1=site-bf-hub&partnerpropertyid=9076396", "btn": "Shop Kinguin"},
    {"name": "Free Amazon Prime trial", "what": "Free fast delivery on Prime items, handy for Christmas shopping.",
     "url": "https://www.amazon.com/amazonprime?tag=steelgames-20", "btn": "Start a free trial"},
]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def base_name(n):
    """Product name without colour or variant ("Keyboard - White", "[Combo Off]")."""
    n = re.sub(r"\[[^\]]*\]", "", n)
    return re.split(r"\s+-\s+", n)[0].strip()


def track(url, sub):
    return url + ("&" if "?" in url else "?") + "subId1=site-bf-" + sub


def gear_deals(api):
    best = {}
    for q in GEAR_QUERIES:
        try:
            items = api.search(q, pages=2)
        except Exception as ex:
            print("search failed", q, ex, file=sys.stderr)
            continue
        for it in items:
            camp = str(it.get("CampaignName") or "").lower()
            key = next((k for k in GEAR_BRANDS if k in camp), None)
            if not key or str(it.get("Currency") or "").upper() != "USD":
                continue
            name = str(it.get("Name") or "")
            brand, keep = GEAR_BRANDS[key]
            if keep and not re.search(keep, name, re.I):
                continue
            if re.search(r"canada|\bUK\b|\bEU\b|australia|refurbished|open box", name, re.I):
                continue
            cur, orig = num(it.get("CurrentPrice")), num(it.get("OriginalPrice"))
            if not (orig > cur > 0) or (orig - cur) / orig < 0.10:
                continue
            if str(it.get("StockAvailability", "InStock")).replace(" ", "").lower() not in ("instock", ""):
                continue
            b = base_name(name)
            k = (brand, b.lower())
            if k in best and best[k]["price"] <= cur:
                continue
            img = it.get("ImageUrl") or ""
            best[k] = {"brand": brand, "name": b, "price": cur, "was": orig, "off": round((orig - cur) / orig * 100),
                       "url": str(it.get("Url") or ""), "img": img if str(img).startswith("https://") else ""}
        time.sleep(0.3)
    out = sorted(best.values(), key=lambda d: -d["off"])
    per = {}
    keep = []
    for d in out:  # at most 10 per brand so one brand can't fill the page
        per[d["brand"]] = per.get(d["brand"], 0) + 1
        if per[d["brand"]] <= (4 if d["brand"] in ("Satechi", "Lemorele") else 10):
            keep.append(d)
    return keep


def game_deals(api):
    best = {}
    for q in GAME_QUERIES:
        try:
            items = api.search(q, pages=1)
        except Exception as ex:
            print("search failed", q, ex, file=sys.stderr)
            continue
        for it in items:
            if "loaded" not in str(it.get("CampaignName") or "").lower() or str(it.get("Currency") or "").upper() != "USD":
                continue
            name = str(it.get("Name") or "")
            if not re.search(r"\bPC\b", name) or re.search(r"gift card|wallet|points|currency|coins", name, re.I):
                continue
            cur, orig = num(it.get("CurrentPrice")), num(it.get("OriginalPrice"))
            if not (orig > cur > 0) or (orig - cur) / orig < 0.25 or orig < 9:
                continue
            k = name.lower()
            if k in best and best[k]["price"] <= cur:
                continue
            img = it.get("ImageUrl") or ""
            best[k] = {"name": name, "price": cur, "was": orig, "off": round((orig - cur) / orig * 100),
                       "url": str(it.get("Url") or ""), "img": img if str(img).startswith("https://") else ""}
        time.sleep(0.3)
    return sorted(best.values(), key=lambda d: (-d["was"], -d["off"]))[:24]


def card_deals():
    try:
        d = json.load(open(CARDS))
    except Exception:
        return []
    out = []
    for cid, c in d.get("cards", {}).items():
        for face, offers in c.get("faces", {}).items():
            if offers and offers[0]["usd"] < int(face) * 0.97:
                o = offers[0]
                out.append({"card": c["name"], "face": int(face), "store": d["stores"].get(o["store"], {}).get("name", o["store"]),
                            "usd": o["usd"], "approx": o.get("approx"), "off": round((int(face) - o["usd"]) / int(face) * 100),
                            "url": o["url"] + ("&" if "?" in o["url"] else "?") + f"subId1=site-bf-card-{cid}{face}-{o['store']}"})
    return sorted(out, key=lambda x: -x["off"])[:8]


def money(v):
    return f"${v:,.2f}"


def cat_of(name):
    low = name.lower()
    return next(label for pat, label in CAT if not pat or re.search(pat, low))


def tile(d, sub, label=""):
    img = f'<img src="{e(d["img"])}" alt="" loading="lazy" width="160" height="160">' if d.get("img") else ""
    return (f'<a class="bf-tile" href="{e(track(d["url"], sub))}" target="_blank" rel="sponsored nofollow noopener" data-bf="{e(sub)}">'
            f'<span class="bf-off">-{d["off"]}%</span><span class="bf-pic">{img}</span>'
            f'<span class="bf-brand">{e(label)}</span><span class="bf-name">{e(d["name"])}</span>'
            f'<span class="bf-price"><b>{money(d["price"])}</b><s>{money(d["was"])}</s></span><span class="bf-go">Get the deal &#8599;</span></a>')


CSS = """<style>
.bf-hero{padding:26px 0 6px}.bf-hero h1{margin:0 0 8px}
.bf-count{display:inline-flex;gap:10px;align-items:center;background:#1B1245;border:1px solid #FF7A1A;border-radius:12px;padding:10px 14px;font-weight:700;margin:8px 0}
.bf-count b{color:#FF8A1A;font-size:20px}
.bf-jump{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.bf-jump a{padding:9px 13px;border-radius:10px;background:#261B5C;border:1px solid #3A2C7A;color:#fff;text-decoration:none;font-weight:600}
.bf-sec{margin:28px 0}.bf-sec>p{color:#CFC8F0}
.bf-chips{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 14px}.bf-chip{padding:8px 12px;border-radius:10px;border:1px solid #3A2C7A;background:#261B5C;color:#fff;font:600 14px Inter,system-ui,sans-serif;cursor:pointer}
.bf-chip[aria-pressed="true"]{background:#FF7A1A;border-color:#FF7A1A;color:#140D33}
.bf-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(200px,1fr))}
.bf-tile{position:relative;display:flex;flex-direction:column;gap:6px;background:#140D33;border:1px solid #2C2160;border-radius:14px;padding:12px;color:#fff;text-decoration:none}
.bf-tile:hover{border-color:#FF7A1A}
.bf-off{position:absolute;top:10px;left:10px;background:#E0303A;color:#fff;font-weight:700;font-size:13px;padding:3px 7px;border-radius:6px}
.bf-pic{height:150px;background:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.bf-pic img{max-width:95%;max-height:145px;object-fit:contain}
.bf-brand{color:#8FB4E3;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.bf-name{font-weight:600;font-size:14px;line-height:1.3}
.bf-price b{font:700 20px "Space Grotesk",Inter,sans-serif;color:#7CF0A8;margin-right:8px}.bf-price s{color:#8A82B5}
.bf-go{margin-top:auto;color:#FF8A1A;font-weight:700;font-size:14px}
.bf-store{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.bf-st{background:#140D33;border:1px solid #2C2160;border-radius:14px;padding:14px;display:flex;flex-direction:column;gap:6px}
.bf-st a{align-self:flex-start;margin-top:6px;background:#5B4CF5;color:#fff;font-weight:700;padding:10px 14px;border-radius:9px;text-decoration:none}
.bf-cards{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.bf-card{display:flex;justify-content:space-between;align-items:center;background:#140D33;border:1px solid #2C2160;border-radius:12px;padding:12px 14px;color:#fff;text-decoration:none}
.bf-card b{color:#7CF0A8}
</style>"""

JS = """<script>
(function(){
 var end=new Date('%END%T23:59:59-06:00'),el=document.getElementById('bfLeft');
 function tick(){var s=Math.max(0,(end-Date.now())/1000|0),d=s/86400|0,h=s%86400/3600|0,m=s%3600/60|0;
  if(el)el.textContent=d+'d '+h+'h '+m+'m'}tick();setInterval(tick,30000);
 var chips=document.getElementById('bfChips');if(chips)chips.addEventListener('click',function(ev){var b=ev.target.closest('.bf-chip');if(!b)return;
  chips.querySelectorAll('.bf-chip').forEach(function(c){c.setAttribute('aria-pressed',c===b)});
  document.querySelectorAll('#bfGear .bf-tile').forEach(function(t){t.style.display=(b.dataset.c==='all'||t.dataset.c===b.dataset.c)?'':'none'})});
 document.addEventListener('click',function(ev){var a=ev.target.closest('[data-bf]');if(!a||!window.goatcounter||!goatcounter.count)return;
  goatcounter.count({path:'bf-click-'+a.dataset.bf,event:true})});
})();
</script>"""


def page(d):
    today = date.today()
    bf_on = today <= date(2026, 12, 1)
    end = "2026-11-30" if today <= date(2026, 11, 30) else "2026-12-01" if bf_on else "2026-12-24"
    title = "Black Friday and Cyber Monday gaming deals 2026" if bf_on else "Holiday gaming deals 2026"
    count_label = ("Cyber Monday ends in" if today <= date(2026, 11, 30) else "Last sales end in") if bf_on else "Christmas Eve in"
    gear = d.get("gear", [])
    for g in gear:
        g["cat"] = cat_of(g["name"])
    cats = [label for _, label in CAT if any(g["cat"] == label for g in gear)]
    chips = '<button class="bf-chip" aria-pressed="true" data-c="all">All</button>' + "".join(
        f'<button class="bf-chip" aria-pressed="false" data-c="{e(c)}">{e(c)}</button>' for c in cats)
    gear_html = "".join(tile(g, f"gear-{re.sub(r'[^a-z0-9]+', '-', g['brand'].lower())}", g["brand"]).replace(
        'class="bf-tile"', f'class="bf-tile" data-c="{e(g["cat"])}"', 1) for g in gear)
    games_html = "".join(tile(g, "game-loaded", "Loaded · PC key") for g in d.get("games", []))
    cards = d.get("cards", [])
    cards_html = "".join(f'<a class="bf-card" href="{e(c["url"])}" target="_blank" rel="sponsored nofollow noopener" data-bf="card">'
                         f'<span>{e(c["card"])} ${c["face"]}<br><small>{e(c["store"])}</small></span>'
                         f'<span><b>{"&asymp; " if c.get("approx") else ""}{money(c["usd"])}</b> <small>-{c["off"]}%</small></span></a>' for c in cards)
    stores = "".join(f'<div class="bf-st"><b>{e(s["name"])}</b><span class="fine">{e(s["what"])}</span>'
                     f'<a href="{e(s["url"])}" target="_blank" rel="sponsored nofollow noopener" data-bf="store">{e(s["btn"])} &#8599;</a></div>'
                     for s in STORE_SALES)
    upd = d.get("updated", "")
    body = f"""<main id="main"><div class="wrap">
<section class="bf-hero">
<p class="crumbs"><a href="/">Home</a> / <a href="/gifts/">Gifts</a> / {e(title)}</p>
<h1>{e(title)}</h1>
<p class="lede">Real sale prices on gaming gear, PC games and gift cards, pulled live from each store's own product feed and checked every few hours. Every deal shows the store's own list price next to the sale price.</p>
<span class="bf-count">{e(count_label)} <b id="bfLeft"></b></span>
<nav class="bf-jump" aria-label="Jump to"><a href="#gear">Gear deals ({len(gear)})</a><a href="#games">PC game deals ({len(d.get("games", []))})</a><a href="#cards">Gift cards</a><a href="#stores">Store-wide sales</a><a href="/s/">Gear from our videos</a></nav>
</section>
<section class="bf-sec" id="gear"><h2>Gaming gear on sale</h2>
<p>Keyboards, mice, chairs, monitors, audio and lights from brands we work with, sorted by the biggest discount.</p>
<div class="bf-chips" id="bfChips" role="group" aria-label="Filter gear">{chips}</div>
<div class="bf-grid" id="bfGear">{gear_html or '<p class="fine">Gear deals are loading. Check back in a few hours.</p>'}</div></section>
<section class="bf-sec" id="games"><h2>PC game keys on sale</h2>
<p>Steam and PC keys from Loaded (formerly CDKeys), at least 25% off. Check the platform and region before you buy.</p>
<div class="bf-grid">{games_html or '<p class="fine">Game deals are loading. Check back in a few hours.</p>'}</div></section>
<section class="bf-sec" id="cards"><h2>Gift cards under face value</h2>
<p>US PlayStation, Xbox, Nintendo, Steam and Roblox cards selling below face value right now. <a href="/gift-cards/">Compare every store</a>.</p>
<div class="bf-cards">{cards_html or '<p class="fine">No cards are under face value right now. <a href="/gift-cards/">See all prices</a>.</p>'}</div></section>
<section class="bf-sec" id="stores"><h2>Store-wide sales</h2><div class="bf-store">{stores}</div></section>
<p class="fine">Prices last checked {e(upd[:16].replace('T', ' '))} UTC and can change at any time; the store's checkout shows the final price. Amazon links show Amazon's live prices on Amazon. We earn a commission when you buy through these links, at no extra cost to you.</p>
</div></main>
"""
    desc = "Live Black Friday and Cyber Monday 2026 deals on gaming keyboards, mice, chairs, monitors, PC game keys and gift cards."
    return (layout.head(f"{title} | SteelGames", desc, layout.SITE + "/black-friday/", CSS) + layout.header("gifts") + body
            + JS.replace("%END%", end) + layout.footer())


def main():
    if "--page-only" not in sys.argv:
        sid, token = os.environ.get("IMPACT_ACCOUNT_SID"), os.environ.get("IMPACT_AUTH_TOKEN")
        try:
            old = json.load(open(DATA))
        except Exception:
            old = {}
        if sid and token:
            api = Impact(sid, token)
            gear, games = gear_deals(api), game_deals(api)
            print("gear deals:", len(gear), "game deals:", len(games))
            data = {"updated": now(), "gear": gear if len(gear) >= 4 else old.get("gear", []),
                    "games": games if len(games) >= 3 else old.get("games", [])}
        else:
            data = old or {"updated": now(), "gear": [], "games": []}
        data["cards"] = card_deals()
        if age_days(data.get("updated")) > 3:
            data["gear"], data["games"] = [], []
        json.dump(data, open(DATA, "w"), indent=1)
    d = json.load(open(DATA))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(page(d))
    print("wrote", OUT, len(d.get("gear", [])), "gear,", len(d.get("games", [])), "games,", len(d.get("cards", [])), "cards")


if __name__ == "__main__":
    main()
