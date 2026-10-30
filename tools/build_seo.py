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


def page_html(p, deals, stores, today):
    e = html.escape
    url = f"{SITE}/deals/{p['slug']}/"
    rows = []
    items = []
    best = {}
    for d in deals:
        gid = str(d.get("gameID"))
        if gid not in best or float(d.get("salePrice") or 0) < float(best[gid].get("salePrice") or 0):
            best[gid] = d
    deals = [best[g] for g in dict.fromkeys(str(d.get("gameID")) for d in deals)]
    for i, d in enumerate(deals, 1):
        store = stores.get(str(d.get("storeID")), "Store")
        sav = round(float(d.get("savings") or 0))
        rate = d.get("steamRatingPercent")
        rating = f"{rate}% ({e(d.get('steamRatingText') or '')})" if rate and rate != "0" else "-"
        link = f"{SITE}/deal/?id={d.get('gameID')}"
        rows.append(
            f"<tr><td><a href=\"{e(link)}\">{e(d.get('title',''))}</a></td><td>{money(d.get('salePrice'))}</td>"
            f"<td class=\"was\">{money(d.get('normalPrice'))}</td><td>{sav}% off</td><td>{rating}</td><td>{e(store)}</td></tr>")
        items.append({"@type": "ListItem", "position": i, "url": link, "name": d.get("title", "")})
    table = ("<div class=\"scroll\"><table><thead><tr><th>Game</th><th>Price</th><th>Usual</th><th>Discount</th><th>Reviews</th><th>Store</th></tr></thead><tbody>"
             + "".join(rows) + "</tbody></table></div>") if rows else "<p>No deals match right now. Check back tomorrow.</p>"
    faq_html = "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in p["faq"])
    others = "".join(f"<li><a href=\"/deals/{o['slug']}/\">{e(o['h1'])}</a></li>" for o in PAGES if o["slug"] != p["slug"])
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
<meta name="google-adsense-account" content="ca-pub-3613204296597380">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3613204296597380" crossorigin="anonymous"></script>
<script data-goatcounter="https://steelgames.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script type="application/ld+json">{ld}</script>
<style>
:root{{--bg:#140B33;--surface:#1E1450;--line:#3B2B8A;--fg:#FFFFFF;--muted:#BDB4EA;--accent:#FFB020;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;padding-block:24px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:900px;margin:0 auto;display:flex;flex-direction:column;gap:18px}}
a{{color:var(--accent)}}
nav a{{font-weight:600;text-decoration:none}}
h1{{font:700 34px/1.1 "Space Grotesk",system-ui,sans-serif;margin:0;text-wrap:balance}}
h2,h3{{margin:0}}
h3{{font-size:17px;margin-top:6px}}
p{{margin:0;color:var(--muted);max-width:68ch}}
.scroll{{overflow-x:auto;border:1px solid var(--line);border-radius:8px}}
table{{border-collapse:collapse;width:100%;min-width:640px;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);font-size:15px}}
th{{background:var(--surface);color:var(--muted);font-weight:500;font-size:13px;text-transform:uppercase;letter-spacing:.06em}}
td.was{{color:var(--muted);text-decoration:line-through}}
.cta{{display:inline-block;background:var(--accent);color:#1A0E04;padding:10px 16px;border-radius:6px;font-weight:600;text-decoration:none;align-self:flex-start}}
footer p{{font-size:13px}}
ul{{margin:0;padding-left:20px;color:var(--muted)}}
</style>
</head>
<body>
<main>
<nav><a href="/">SteelGames</a> / <a href="/deals/">Deals</a></nav>
<h1>{e(p['h1'])}</h1>
<p>{e(p['intro'])}</p>
<p>Updated {today}. Prices come from official stores and key sellers and can change at any time.</p>
{table}
<section><h2>Questions</h2>{faq_html}</section>
<section><h2>More deal lists</h2><ul>{others}</ul></section>
<footer><p>SteelGames is a product of Lonestar PPS, LLC, a veteran-owned company. As an Amazon Associate, SteelGames earns from qualifying purchases.</p></footer>
</main>
</body>
</html>
"""


def hub_html(today):
    e = html.escape
    lis = "".join(f"<li><a href=\"/deals/{p['slug']}/\">{e(p['h1'])}</a> <span>{e(p['desc'])}</span></li>" for p in PAGES)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>PC Game Deals | SteelGames</title>
<meta name="description" content="Daily PC game deal lists from SteelGames: games under $5, under $10, best Steam deals, highly rated sales and free games.">
<link rel="canonical" href="{SITE}/deals/">
<script data-goatcounter="https://steelgames.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<meta name="google-adsense-account" content="ca-pub-3613204296597380">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3613204296597380" crossorigin="anonymous"></script>
<style>:root{{color-scheme:dark}}body{{margin:0;background:#140B33;color:#FFFFFF;font:16px/1.6 Inter,system-ui,sans-serif;padding-block:24px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}main{{max-width:820px;margin:0 auto;display:flex;flex-direction:column;gap:16px}}a{{color:#FF7A1A}}h1{{font:700 34px/1.1 "Space Grotesk",system-ui,sans-serif;margin:0}}li{{margin-bottom:12px}}li span{{display:block;color:#9BA4AF;font-size:15px}}ul{{padding-left:20px;margin:0}}</style></head>
<body><main><nav><a href="/">SteelGames</a></nav><h1>PC game deals</h1>
<p style="color:#9BA4AF;margin:0">Fresh lists every day. Updated {today}.</p><ul>{lis}</ul></main></body></html>
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
    rows = "".join(f"<tr><td>{e(stores[str(d['storeID'])])}</td><td>{money(d['price'])}</td><td class=\"was\">{money(d['retailPrice'])}</td><td><a rel=\"sponsored noopener\" href=\"https://www.cheapshark.com/redirect?dealID={e(str(d.get('dealID','')))}\">Buy</a></td></tr>" for d in deals)
    faq = [(f"What is the lowest price ever for {title}?", f"The lowest recorded price is {money(low)}{(' in ' + when) if when else ''}." if low > 0 else "We don't have a recorded lowest price for this game yet."),
           (f"Is {title} on sale right now?", f"The best current price we found is {money(cur)} at {stores[str(best['storeID'])]}, against a usual price of {money(reg)}."),
           (f"Should I buy {title} now or wait?", f"{label}. {detail}")]
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "Product", "name": title, "image": info.get("thumb") or "",
         "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": "%.2f" % cur, "highPrice": "%.2f" % float(deals[-1]["price"]), "offerCount": len(deals)}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]).replace("<", "\\u003c")
    desc = f"{title} price today: {money(cur)} at {stores[str(best['storeID'])]}. {label}. Compare official store prices and see the lowest price ever."
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)} price history and best price today | SteelGames</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)} price today | SteelGames"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">
<meta name="google-adsense-account" content="ca-pub-3613204296597380">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3613204296597380" crossorigin="anonymous"></script>
<script data-goatcounter="https://steelgames.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script type="application/ld+json">{ld}</script>
<style>:root{{--bg:#140B33;--surface:#1E1450;--line:#3B2B8A;--fg:#FFFFFF;--muted:#BDB4EA;--accent:#FFB020;color-scheme:dark}}*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;padding:24px 16px 56px}}
main{{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:18px}}a{{color:var(--accent)}}nav a{{font-weight:600;text-decoration:none}}
h1{{font:700 32px/1.1 "Space Grotesk",system-ui,sans-serif;margin:0;text-wrap:balance}}h2,h3{{margin:0}}h3{{font-size:17px;margin-top:6px}}p{{margin:0;color:var(--muted)}}
.big{{font:700 40px/1 "Space Grotesk",system-ui,sans-serif;color:var(--fg)}}.big s{{font-size:20px;color:var(--muted);font-weight:400;margin-left:10px}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px;display:flex;flex-direction:column;gap:6px}}
table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line)}}th{{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.06em}}td.was{{color:var(--muted);text-decoration:line-through}}
.cta{{display:inline-block;background:var(--accent);color:#1A0E04;padding:12px 18px;border-radius:8px;font-weight:700;text-decoration:none;align-self:flex-start}}footer p{{font-size:13px}}</style></head>
<body><main>
<nav><a href="/">SteelGames</a> / <a href="/game/">Games</a></nav>
<h1>{e(title)} price history and best price today</h1>
<div class="big">{money(cur)}<s>{money(reg)}</s></div>
<p>Best current price: {e(stores[str(best['storeID'])])}. Updated {today}.</p>
<div class="card"><strong>{e(label)}</strong><p>{e(detail)}</p></div>
<table><thead><tr><th>Store</th><th>Price</th><th>Usual</th><th></th></tr></thead><tbody>{rows}</tbody></table>
{"<p>Lowest price ever: <strong style=\"color:var(--fg)\">" + money(low) + "</strong>" + (" (" + when + ")" if when else "") + "</p>" if low > 0 else ""}
<a class="cta" rel="sponsored noopener" href="https://www.cheapshark.com/redirect?dealID={e(str(best.get('dealID','')))}">Buy at {e(stores[str(best['storeID'])])} for {money(cur)}</a>
<section><h2>Questions</h2>{"".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq)}</section>
<footer><p>SteelGames is a product of Lonestar PPS, LLC, a veteran-owned company. Prices can change at any time. As an Amazon Associate, SteelGames earns from qualifying purchases.</p></footer>
</main></body></html>
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
    lis = "".join(f"<li><a href=\"/game/{s}/\">{html.escape(t)}</a></li>" for s, t in sorted(entries, key=lambda x: x[1].lower()))
    os.makedirs(base, exist_ok=True)
    open(os.path.join(base, "index.html"), "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PC game prices and price history | SteelGames</title>
<meta name="description" content="Current best prices and lowest-ever prices for popular PC games from official stores.">
<link rel="canonical" href="{SITE}/game/">
<script data-goatcounter="https://steelgames.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<style>:root{{color-scheme:dark}}body{{margin:0;background:#140B33;color:#FFFFFF;font:16px/1.6 Inter,system-ui,sans-serif;padding:24px 16px 56px}}main{{max-width:760px;margin:0 auto}}a{{color:#FFB020}}h1{{font:700 32px/1.1 system-ui}}li{{margin:4px 0}}</style></head>
<body><main><nav><a href="/">SteelGames</a></nav><h1>PC game prices and price history</h1><p style="color:#9BA4AF">Updated {today}.</p><ul>{lis}</ul></main></body></html>
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
    urls = [f"{SITE}/", f"{SITE}/get-app/", f"{SITE}/gear.html", f"{SITE}/reviews.html", f"{SITE}/community.html", f"{SITE}/advertise.html", f"{SITE}/deals/"]
    for p in PAGES:
        try:
            deals = fetch(p["q"])
        except Exception as ex:
            print("fetch failed for", p["slug"], ex, file=sys.stderr)
            continue
        d = os.path.join(ROOT, "deals", p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(page_html(p, deals, stores, today))
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
