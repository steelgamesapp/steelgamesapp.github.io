#!/usr/bin/env python3
"""Builds static SEO deal pages under /deals/ from the CheapShark API.

Run daily by .github/workflows/seo.yml. Standard library only.
Usage: python3 tools/build_seo.py [--sample path.json]   (--sample skips the network, for tests)
"""
import html, json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

SITE = "https://steelgamesapp.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://www.cheapshark.com/api/1.0"

PAGES = [
    {"slug": "pc-games-under-5", "h1": "PC games under $5", "q": {"upperPrice": 5, "lowerPrice": 0.01, "sortBy": "Deal Rating"},
     "desc": "The best PC game deals under $5 right now, sorted by deal rating, from official stores and key sellers.",
     "intro": "Cheap does not have to mean junk. These PC games are priced under $5 today, ranked by how good the deal is compared with each game's usual price and its player reviews.",
     "faq": [("How often is this list updated?", "The list is rebuilt every day from live store prices."),
             ("Is the price the same at every store?", "No. Each row shows the store with the current price, so you can compare before you buy.")]},
    {"slug": "pc-games-under-10", "h1": "PC games under $10", "q": {"upperPrice": 10, "lowerPrice": 0.01, "sortBy": "Deal Rating"},
     "desc": "Top PC game deals under $10 today, ranked by savings and reviews.",
     "intro": "Ten dollars still buys a lot of PC gaming. This list ranks today's under-$10 deals by discount depth and review score, so the strongest values come first.",
     "faq": [("What does deal rating mean?", "It is a score from CheapShark that weighs the discount against the game's price history and popularity."),
             ("Do sales end quickly?", "Many store sales last a few days to two weeks. Check the store page for the end date.")]},
    {"slug": "best-steam-deals-today", "h1": "Best Steam deals today", "q": {"storeID": 1, "sortBy": "Deal Rating"},
     "desc": "The best Steam game deals today, ranked by deal rating with review scores.",
     "intro": "These are the strongest Steam discounts running today, ranked by deal rating. Each row shows the sale price, the usual price and the Steam review score.",
     "faq": [("Are these Steam prices?", "Yes. Every row on this page is the Steam price. Open a game to compare its price at other stores."),
             ("Can I find the lowest price ever?", "Open a game to see the lowest price recorded and the price at every store.")]},
    {"slug": "highly-rated-pc-game-deals", "h1": "Highly rated PC games on sale", "q": {"steamRating": 90, "upperPrice": 20, "sortBy": "Deal Rating"},
     "desc": "PC games with 90% or higher Steam reviews that are on sale for $20 or less.",
     "intro": "Great reviews and a small price. Every game here has a Steam rating of 90 percent or higher and is on sale for $20 or less today.",
     "faq": [("Where do the ratings come from?", "They are Steam user review percentages reported by CheapShark."),
             ("Can the price change?", "Yes. Prices are refreshed daily and stores can change them at any time.")]},
    {"slug": "biggest-pc-game-discounts", "h1": "Biggest PC game discounts", "q": {"sortBy": "Savings", "upperPrice": 30},
     "desc": "The deepest PC game discounts right now, sorted by percent off.",
     "intro": "If you want the biggest percentage off, start here. These PC games have the deepest discounts today across the stores we track.",
     "faq": [("Is a big discount always a good deal?", "Not always. Open a game to compare the sale price with its lowest recorded price."),
             ("Do you include free games?", "Free giveaways are covered separately. This list focuses on paid games with deep discounts.")]},
    {"slug": "gog-game-deals", "h1": "GOG game deals today", "q": {"storeID": 7, "sortBy": "Deal Rating"},
     "desc": "The best GOG game deals today, DRM-free PC games ranked by deal rating.",
     "intro": "GOG sells DRM-free PC games, so you keep them without a launcher. These are today's strongest GOG discounts, ranked by deal rating.",
     "faq": [("What does DRM-free mean?", "You can install and play the game without an online check or a launcher."),
             ("Can I compare prices with other stores?", "Open any game to see every store's price side by side.")]},
    {"slug": "epic-games-store-deals", "h1": "Epic Games Store deals today", "q": {"storeID": 25, "sortBy": "Deal Rating"},
     "desc": "Today's best Epic Games Store discounts on PC games, ranked by deal rating.",
     "intro": "These are the strongest Epic Games Store discounts today. Each row shows the sale price, the regular price and the Steam review score when one exists.",
     "faq": [("Do Epic prices change often?", "Yes. Epic runs frequent sales, and this list is rebuilt every day."),
             ("Does Epic give away free games?", "Often. The free games list on this site shows anything priced at $0.00 right now.")]},
    {"slug": "humble-store-deals", "h1": "Humble Store deals today", "q": {"storeID": 11, "sortBy": "Deal Rating"},
     "desc": "Today's best Humble Store PC game deals, ranked by deal rating.",
     "intro": "The Humble Store sells Steam keys and DRM-free games, and part of each sale supports charity. These are today's best Humble Store deals by deal rating.",
     "faq": [("Are Humble games Steam keys?", "Many are. The store page for each game says how it is delivered."),
             ("How are deals ranked?", "By CheapShark's deal rating, which weighs discount depth against price history.")]},
    {"slug": "green-man-gaming-deals", "h1": "Green Man Gaming deals today", "q": {"storeID": 3, "sortBy": "Deal Rating"},
     "desc": "Today's best Green Man Gaming PC game deals, ranked by deal rating.",
     "intro": "Green Man Gaming is an official reseller of PC game keys. These are the best discounts there today, ranked by deal rating.",
     "faq": [("Is Green Man Gaming legit?", "Yes. It is an authorized digital retailer for many publishers."),
             ("Which store has the lowest price?", "It changes daily. Open a game to compare every store.")]},
    {"slug": "fanatical-deals", "h1": "Fanatical deals today", "q": {"storeID": 15, "sortBy": "Deal Rating"},
     "desc": "Today's best Fanatical PC game deals, ranked by deal rating.",
     "intro": "Fanatical sells official PC game keys and bundles. These are the strongest single-game discounts there today, ranked by deal rating.",
     "faq": [("Does Fanatical sell bundles?", "Yes. This list shows single-game deals. Bundles are on the Fanatical site."),
             ("Are the keys official?", "Fanatical sells keys from publishers and authorized distributors.")]},
    {"slug": "pc-games-under-15", "h1": "PC games under $15", "q": {"upperPrice": 15, "lowerPrice": 0.01, "sortBy": "Deal Rating"},
     "desc": "The best PC game deals under $15 today, ranked by deal rating.",
     "intro": "Fifteen dollars covers most great indie games and many older AAA releases. These are today's best deals under $15.",
     "faq": [("How is this different from the under $10 list?", "It includes games priced from $10 to $15, so you see more recent and larger titles."),
             ("How often does it update?", "Every day.")]},
    {"slug": "top-metacritic-pc-game-deals", "h1": "Top-reviewed PC games on sale", "q": {"metacritic": 85, "upperPrice": 30, "sortBy": "Deal Rating"},
     "desc": "PC games with a Metacritic score of 85 or higher, on sale for $30 or less.",
     "intro": "Critics and players agree on these. Every game here has a Metacritic score of 85 or higher and is on sale for $30 or less today.",
     "faq": [("What is Metacritic?", "A site that averages professional reviews into one score out of 100."),
             ("Are critic scores the same as player scores?", "Not always. The Reviews column shows the Steam player score where one exists.")]},
    {"slug": "free-pc-games-right-now", "h1": "Free PC games right now", "q": {"upperPrice": 0, "sortBy": "Deal Rating"},
     "desc": "PC games that are free to claim or keep right now.",
     "intro": "Stores sometimes give games away for a limited time. Anything listed here shows a current price of $0.00. Claim it before the offer ends.",
     "faq": [("Is it really free?", "A price of $0.00 means the store lists the game at no cost right now. Some need a store account."),
             ("Why is the list sometimes short?", "Giveaways are rare and change often. Check back tomorrow.")]},
]


# Keyword pages: one per popular game theme, built from a CheapShark title search.
_THEMES = [("zombie", "Zombie games"), ("horror", "Horror games"), ("farming", "Farming games"), ("racing", "Racing games"),
           ("city", "City builder games"), ("survival", "Survival games"), ("space", "Space games"), ("puzzle", "Puzzle games"),
           ("tower defense", "Tower defense games"), ("roguelike", "Roguelike games"), ("football", "Football and soccer games"),
           ("war", "War and military games"), ("simulator", "Simulator games"), ("dungeon", "Dungeon crawler games"),
           ("lego", "LEGO games"), ("star wars", "Star Wars games"), ("resident evil", "Resident Evil games"), ("civilization", "Civilization games")]
for _kw, _name in _THEMES:
    PAGES.append({"slug": "deals-" + _kw.replace(" ", "-"), "h1": _name + " on sale", "q": {"title": _kw, "upperPrice": 40, "sortBy": "Deal Rating"},
        "desc": f"{_name} on sale for PC today, ranked by deal rating with review scores.",
        "intro": f"Current PC deals for {_name.lower()}, ranked by how good the discount is against each game's usual price. Prices come from official stores and authorized key sellers and refresh daily.",
        "faq": [("How is this list picked?", f"It searches current store listings for \"{_kw}\" and ranks results by deal rating."),
                ("Can I see price history?", "Open any game to see its lowest recorded price and every store's price.")]})


def get(path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"User-Agent": "SteelGames-SEO-Builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def money(v):
    try:
        return "$%.2f" % float(v)
    except Exception:
        return "-"


STORE_COLORS = {"1": "#66C0F4", "2": "#D4B8FF", "3": "#2D9B4B", "7": "#C026D3", "11": "#E0531E", "13": "#4F8EF7", "15": "#FF7A1A",
                "21": "#0E9F8E", "23": "#D99A00", "25": "#9BA4AF", "27": "#5B3FD9", "28": "#7FD6FF", "30": "#FF4D8D", "35": "#FFB020"}

HEAD_COMMON = """<meta name="google-adsense-account" content="ca-pub-3613204296597380">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3613204296597380" crossorigin="anonymous"></script>
<script data-goatcounter="https://steelgames.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/assets/sg.css">
<script defer src="/assets/sg.js"></script>"""


def art_url(d):
    sid = d.get("steamAppID")
    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg" if sid else (d.get("thumb") or "")


def deal_json(deals):
    """Deal objects the shared script registers so the heart and cart buttons work on static pages."""
    keep = ("gameID", "title", "salePrice", "normalPrice", "storeID", "dealID", "thumb", "steamAppID")
    return json.dumps([{k: d.get(k) for k in keep} for d in deals]).replace("<", "\\u003c")


def card_html(d, stores, low=None):
    e = html.escape
    sale, normal = float(d.get("salePrice") or 0), float(d.get("normalPrice") or 0)
    off = round(float(d.get("savings") or 0))
    high = max(sale, normal)
    lowest = min(float(low), sale) if low else None
    gid = e(str(d.get("gameID")))
    color = STORE_COLORS.get(str(d.get("storeID")), "#7B5CFF")
    badge = '<span class="badge free">FREE</span>' if sale == 0 else (f'<span class="badge">-{off}%</span>' if off > 0 else "")
    rate = d.get("steamRatingPercent")
    rating = f" &middot; {e(str(rate))}% positive" if rate and rate != "0" else ""
    link = f"/deal/?id={gid}"
    return (f'<article class="gcard" style="--store:{color}" data-gid="{gid}">{badge}'
            f'<a class="art" href="{link}"><img src="{e(art_url(d))}" data-fallback="{e(d.get("thumb") or "")}" alt="{e(d.get("title", ""))} cover art" loading="lazy"></a>'
            f'<div class="body"><h3><a href="{link}">{e(d.get("title", ""))}</a></h3>'
            f'<div class="prices"><div class="now"><span>Now</span><b>{money(sale) if sale else "Free"}</b></div><div><span>Highest</span><b>{money(high) if high else "-"}</b></div>'
            f'<div class="low"><span>Lowest</span><b>{money(lowest) if lowest is not None else "-"}</b></div></div>'
            f'<div class="store-line">Best at <b>{e(stores.get(str(d.get("storeID")), "Store"))}</b>{rating}</div>'
            f'<div class="actions"><button class="btn heart" data-act="wish" data-gid="{gid}" aria-pressed="false" aria-label="Add to wishlist">&#9825;</button>'
            f'<button class="btn btn-primary grow" data-act="cart" data-gid="{gid}">Add to cart</button></div></div></article>')


def page_html(p, deals, stores, today, lows=None):
    lows = lows or {}
    e = html.escape
    url = f"{SITE}/deals/{p['slug']}/"
    best = {}
    for d in deals:
        gid = str(d.get("gameID"))
        if gid not in best or float(d.get("salePrice") or 0) < float(best[gid].get("salePrice") or 0):
            best[gid] = d
    deals = [best[g] for g in dict.fromkeys(str(d.get("gameID")) for d in deals)]
    items = [{"@type": "ListItem", "position": i, "url": f"{SITE}/deal/?id={d.get('gameID')}", "name": d.get("title", "")} for i, d in enumerate(deals, 1)]
    cards = "".join(card_html(d, stores, lows.get(str(d.get("gameID")))) for d in deals)
    grid = f'<div class="grid">{cards}</div>' if cards else '<div class="empty">No deals match right now. Check back tomorrow.</div>'
    faq_html = "".join(f"<h3>{e(q)}</h3><p class=\"muted\">{e(a)}</p>" for q, a in p["faq"])
    others = "".join(f"<a class=\"chip\" href=\"/deals/{o['slug']}/\" style=\"text-decoration:none;display:inline-flex;align-items:center\">{e(o['h1'])}</a>" for o in PAGES if o["slug"] != p["slug"])
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "ItemList", "name": p["h1"], "itemListElement": items},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
    ]).replace("<", "\\u003c")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(p['h1'])} - {today} | SteelGames</title>
<meta name="description" content="{e(p['desc'])}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(p['h1'])} | SteelGames">
<meta property="og:description" content="{e(p['desc'])}">
<meta property="og:url" content="{url}">
{HEAD_COMMON}
<script type="application/ld+json">{ld}</script>
<script>window.SG_DEALS={deal_json(deals)};</script>
</head>
<body>
<div id="sg-header"></div>
<main class="wrap">
<section class="hero"><h1>{e(p['h1'])}</h1><p>{e(p['intro'])}</p><p class="muted">Updated {today}. Prices come from official stores and key sellers and can change at any time.</p></section>
{grid}
<section><h2>Questions</h2>{faq_html}</section>
<section><h2>More deal lists</h2><div class="chips" style="margin-top:10px">{others}</div></section>
</main>
<div id="sg-footer"></div>
</body>
</html>
"""


def hub_html(today):
    e = html.escape
    cards = "".join(f"<a class=\"shop\" style=\"text-decoration:none\" href=\"/deals/{p['slug']}/\"><h3 style=\"color:#fff\">{e(p['h1'])}</h3><p>{e(p['desc'])}</p></a>" for p in PAGES)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>PC Game Deals | SteelGames</title>
<meta name="description" content="Daily PC game deal lists from SteelGames: games under $5, under $10, best Steam deals, highly rated sales and free games.">
<link rel="canonical" href="{SITE}/deals/">
{HEAD_COMMON}
</head>
<body>
<div id="sg-header"></div>
<main class="wrap"><section class="hero"><h1>PC game deals</h1><p>Fresh lists every day. Updated {today}.</p></section>
<div class="shops">{cards}</div></main>
<div id="sg-footer"></div>
</body></html>
"""


# ---------- Per-game price pages ----------
import re, time
GAME_CAP = 400          # most games tracked at once; the list grows a little every day
GAME_IDS_FILE = os.path.join(ROOT, "tools", "game_ids.json")


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "game").lower()).strip("-")[:60] or "game"


def verdict(cur, reg, low):
    off = round((reg - cur) / reg * 100) if reg > 0 else 0
    if low <= 0:
        return ("Good deal" if off >= 50 else "Consider waiting"), f"{off}% off right now. We don't have its full price history yet."
    if cur <= low * 1.05:
        return "Buy now", "This is the lowest price it has been." if cur <= low else "Within 5% of its lowest price ever (%s)." % money(low)
    if off >= 40 and cur <= low * 1.35:
        return "Good deal", f"{off}% off. It has been {money(low)} before, so waiting could save {money(cur - low)}."
    return "Wait for a better price", f"It has been as low as {money(low)}. Track it and check back."


def game_page(gid, g, stores, today):
    e = html.escape
    info = g.get("info") or {}
    title = info.get("title") or "Game"
    deals = sorted([d for d in g.get("deals", []) if str(d.get("storeID")) in stores], key=lambda d: float(d["price"]))
    if not deals:
        return None, None
    best = deals[0]
    cur, reg = float(best["price"]), float(best["retailPrice"])
    low = float((g.get("cheapestPriceEver") or {}).get("price") or 0)
    ts = (g.get("cheapestPriceEver") or {}).get("date")
    when = datetime.fromtimestamp(int(ts), timezone.utc).strftime("%B %Y") if ts else ""
    label, detail = verdict(cur, reg, low)
    slug = f"{slugify(title)}-{gid}"
    url = f"{SITE}/game/{slug}/"
    sid = info.get("steamAppID")
    art = art_url({"steamAppID": sid, "thumb": info.get("thumb")})
    off = round((reg - cur) / reg * 100) if reg > 0 else 0
    lowest = min(low, cur) if low > 0 else None
    rows = "".join(f"<tr><td>{e(stores[str(d['storeID'])])}</td><td>{money(d['price'])}</td><td class=\"was\">{money(d['retailPrice'])}</td><td><a rel=\"sponsored noopener\" href=\"https://www.cheapshark.com/redirect?dealID={e(str(d.get('dealID','')))}\">Buy</a></td></tr>" for d in deals)
    faq = [(f"What is the lowest price ever for {title}?", f"The lowest recorded price is {money(low)}{(' in ' + when) if when else ''}." if low > 0 else "We don't have a recorded lowest price for this game yet."),
           (f"Is {title} on sale right now?", f"The best current price we found is {money(cur)} at {stores[str(best['storeID'])]}, against a usual price of {money(reg)}."),
           (f"Should I buy {title} now or wait?", f"{label}. {detail}")]
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "Product", "name": title, "image": art or "",
         "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": "%.2f" % cur, "highPrice": "%.2f" % float(deals[-1]["price"]), "offerCount": len(deals)}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]).replace("<", "\\u003c")
    desc = f"{title} price today: {money(cur)} at {stores[str(best['storeID'])]}. {label}. Compare official store prices and see the lowest price ever."
    reg_deal = {"gameID": str(gid), "title": title, "salePrice": best["price"], "normalPrice": best["retailPrice"], "storeID": best["storeID"],
                "dealID": best.get("dealID"), "thumb": info.get("thumb"), "steamAppID": sid}
    gid_e = e(str(gid))
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)} price history and best price today | SteelGames</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)} price today | SteelGames"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">
{"<meta property=\"og:image\" content=\"" + e(art) + "\">" if art else ""}
{HEAD_COMMON}
<script type="application/ld+json">{ld}</script>
<script>window.SG_DEALS={deal_json([reg_deal])};</script>
<style>.top{{display:grid;grid-template-columns:minmax(0,420px) 1fr;gap:20px;align-items:start}}.top img{{width:100%;border-radius:12px;border:1px solid var(--line-strong);display:block}}.verdict{{background:var(--surface);border:1px solid var(--line-strong);border-left:5px solid var(--accent);border-radius:12px;padding:14px 16px}}.verdict b{{font-size:19px}}@media(max-width:700px){{.top{{grid-template-columns:1fr}}}}</style>
</head>
<body>
<div id="sg-header"></div>
<main class="wrap">
<nav class="muted"><a href="/game/">Games</a> / {e(title)}</nav>
<div class="top">
{"<img src=\"" + e(art) + "\" data-fallback=\"" + e(info.get('thumb') or '') + "\" alt=\"" + e(title) + " cover art\">" if art else ""}
<div style="display:flex;flex-direction:column;gap:12px">
<h1>{e(title)} price history and best price today</h1>
<div class="prices" style="max-width:420px"><div class="now"><span>Now</span><b>{money(cur)}</b></div><div><span>Highest</span><b>{money(max(reg, cur))}</b></div><div class="low"><span>Lowest ever</span><b>{money(lowest) if lowest is not None else "-"}</b></div></div>
<p class="muted">{off}% off at {e(stores[str(best['storeID'])])}. Updated {today}.</p>
<div class="verdict"><b>{e(label)}</b><p class="muted">{e(detail)}</p></div>
<div class="actions"><button class="btn heart" data-act="wish" data-gid="{gid_e}" aria-pressed="false" aria-label="Add to wishlist">&#9825;</button><button class="btn grow" data-act="cart" data-gid="{gid_e}">Add to cart</button>
<a class="btn btn-primary grow" rel="sponsored noopener" href="https://www.cheapshark.com/redirect?dealID={e(str(best.get('dealID','')))}">Buy at {e(stores[str(best['storeID'])])} for {money(cur)}</a></div>
</div></div>
<div class="scroll"><table><thead><tr><th>Store</th><th>Price</th><th>Usual</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>
<section><h2>Questions</h2>{"".join(f"<h3>{e(q)}</h3><p class=\"muted\">{e(a)}</p>" for q, a in faq)}</section>
</main>
<div id="sg-footer"></div>
</body></html>
"""
    return slug, page


def build_games(stores, today, seeds, fetch_game):
    """Keep a growing list of game ids, rebuild every game page, return (urls, index entries)."""
    ids = []
    try:
        ids = json.load(open(GAME_IDS_FILE))
    except Exception:
        pass
    for gid in seeds:
        if gid not in ids:
            ids.append(gid)
    ids = ids[-GAME_CAP:]
    entries, urls, keep = [], [], []
    base = os.path.join(ROOT, "game")
    for gid in ids:
        try:
            g = fetch_game(gid)
            slug, page = game_page(gid, g, stores, today)
        except Exception as ex:
            print("game failed", gid, ex, file=sys.stderr)
            slug, page = None, None
        if not page:
            continue
        d = os.path.join(base, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(page)
        keep.append(gid)
        entries.append((slug, (g.get("info") or {}).get("title", "Game")))
        urls.append(f"{SITE}/game/{slug}/")
        time.sleep(0.25)
    json.dump(keep, open(GAME_IDS_FILE, "w"))
    # Remove pages for games that are no longer tracked.
    live = {s for s, _ in entries}
    if os.path.isdir(base):
        for name in os.listdir(base):
            if name not in live and os.path.isdir(os.path.join(base, name)):
                import shutil
                shutil.rmtree(os.path.join(base, name))
    cards = "".join(f"<a class=\"chip\" style=\"text-decoration:none;display:inline-flex;align-items:center\" href=\"/game/{s}/\">{html.escape(t)}</a>" for s, t in sorted(entries, key=lambda x: x[1].lower()))
    os.makedirs(base, exist_ok=True)
    open(os.path.join(base, "index.html"), "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>PC game prices and price history | SteelGames</title>
<meta name="description" content="Current best prices and lowest-ever prices for popular PC games from official stores.">
<link rel="canonical" href="{SITE}/game/">
{HEAD_COMMON}
</head>
<body>
<div id="sg-header"></div>
<main class="wrap"><section class="hero"><h1>PC game prices and price history</h1><p>Updated {today}. Looking for more? Browse by category on the <a href="/games.html">Games page</a>.</p></section>
<div class="chips">{cards}</div></main>
<div id="sg-footer"></div>
</body></html>
""")
    return [f"{SITE}/game/"] + urls


def main():
    today = datetime.now(timezone.utc).strftime("%B %d, %Y").replace(" 0", " ")
    sample = sys.argv[sys.argv.index("--sample") + 1] if "--sample" in sys.argv else None
    if sample:
        data = json.load(open(sample))
        stores, fetch = data["stores"], lambda q: data["deals"]
    else:
        stores = {s["storeID"]: s["storeName"] for s in get("/stores")}
        fetch = lambda q: get("/deals", {**q, "pageSize": 40, "onSale": 1})
    urls = [f"{SITE}/", f"{SITE}/get-app/", f"{SITE}/games.html", f"{SITE}/keys.html", f"{SITE}/gear.html", f"{SITE}/reviews.html", f"{SITE}/community.html", f"{SITE}/advertise.html", f"{SITE}/deals/"]
    fetched = {}
    for p in PAGES:
        try:
            fetched[p["slug"]] = fetch(p["q"])
        except Exception as ex:
            print("fetch failed for", p["slug"], ex, file=sys.stderr)
    lows = {}
    if not sample:   # lowest price ever per game, 25 games per request
        ids = list(dict.fromkeys(str(d.get("gameID")) for ds in fetched.values() for d in ds))
        for i in range(0, len(ids), 25):
            try:
                for gid, g in get("/games", {"ids": ",".join(ids[i:i + 25])}).items():
                    lows[gid] = (g.get("cheapestEver") or {}).get("price")
            except Exception as ex:
                print("lowest-price batch failed", ex, file=sys.stderr)
            time.sleep(0.3)
    for p in PAGES:
        if p["slug"] not in fetched:
            continue
        deals = fetched[p["slug"]]
        d = os.path.join(ROOT, "deals", p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(page_html(p, deals, stores, today, lows))
        urls.append(f"{SITE}/deals/{p['slug']}/")
        print("built", p["slug"], len(deals))
    # Per-game pages: seed with today's top deals, then rebuild every tracked game.
    try:
        if sample:
            seeds = ["1"]; fg = lambda gid: data["game"]
        else:
            seeds = []
            for pg in range(6):
                for d in get("/deals", {"sortBy": "Deal Rating", "onSale": 1, "pageSize": 60, "pageNumber": pg, "AAA": 0, "steamRating": 70}):
                    if str(d.get("storeID")) in stores and str(d["gameID"]) not in seeds:
                        seeds.append(str(d["gameID"]))
                time.sleep(0.5)
            fg = lambda gid: get("/games", {"id": gid})
        urls += build_games(stores, today, seeds, fg)
    except Exception as ex:
        print("games step failed", ex, file=sys.stderr)
    os.makedirs(os.path.join(ROOT, "deals"), exist_ok=True)
    open(os.path.join(ROOT, "deals", "index.html"), "w").write(hub_html(today))
    iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc><lastmod>{iso}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
