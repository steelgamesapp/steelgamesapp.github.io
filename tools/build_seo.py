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
     "faq": [("Are these Steam prices?", "Yes. Every row on this page is the Steam price. Other stores are compared on each game's page in the SteelGames app."),
             ("Can I find the lowest price ever?", "Open a game in the app to see its price history meter and the lowest price recorded.")]},
    {"slug": "highly-rated-pc-game-deals", "h1": "Highly rated PC games on sale", "q": {"steamRating": 90, "upperPrice": 20, "sortBy": "Deal Rating"},
     "desc": "PC games with 90% or higher Steam reviews that are on sale for $20 or less.",
     "intro": "Great reviews and a small price. Every game here has a Steam rating of 90 percent or higher and is on sale for $20 or less today.",
     "faq": [("Where do the ratings come from?", "They are Steam user review percentages reported by CheapShark."),
             ("Can the price change?", "Yes. Prices are refreshed daily and stores can change them at any time.")]},
    {"slug": "biggest-pc-game-discounts", "h1": "Biggest PC game discounts", "q": {"sortBy": "Savings", "upperPrice": 30},
     "desc": "The deepest PC game discounts right now, sorted by percent off.",
     "intro": "If you want the biggest percentage off, start here. These PC games have the deepest discounts today across the stores we track.",
     "faq": [("Is a big discount always a good deal?", "Not always. Compare the sale price with the game's lowest recorded price in the SteelGames app."),
             ("Do you include free games?", "Free giveaways are covered separately. This list focuses on paid games with deep discounts.")]},
    {"slug": "gog-game-deals", "h1": "GOG game deals today", "q": {"storeID": 7, "sortBy": "Deal Rating"},
     "desc": "The best GOG game deals today, DRM-free PC games ranked by deal rating.",
     "intro": "GOG sells DRM-free PC games, so you keep them without a launcher. These are today's strongest GOG discounts, ranked by deal rating.",
     "faq": [("What does DRM-free mean?", "You can install and play the game without an online check or a launcher."),
             ("Can I compare prices with other stores?", "Open any game in the SteelGames app to see every store's price side by side.")]},
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
             ("Which store has the lowest price?", "It changes daily. Open a game in the SteelGames app to compare every store.")]},
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
    for i, d in enumerate(deals, 1):
        store = stores.get(str(d.get("storeID")), "Store")
        sav = round(float(d.get("savings") or 0))
        rate = d.get("steamRatingPercent")
        rating = f"{rate}% ({e(d.get('steamRatingText') or '')})" if rate and rate != "0" else "-"
        link = f"{SITE}/app/#/game/{d.get('gameID')}"
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
:root{{--bg:#0C0E11;--surface:#15181D;--line:#262C35;--fg:#EDEFF2;--muted:#9BA4AF;--accent:#FF7A1A;color-scheme:dark}}
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
<a class="cta" href="{SITE}/app/">Open the SteelGames app for price history and alerts</a>
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
<style>:root{{color-scheme:dark}}body{{margin:0;background:#0C0E11;color:#EDEFF2;font:16px/1.6 Inter,system-ui,sans-serif;padding-block:24px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}main{{max-width:820px;margin:0 auto;display:flex;flex-direction:column;gap:16px}}a{{color:#FF7A1A}}h1{{font:700 34px/1.1 "Space Grotesk",system-ui,sans-serif;margin:0}}li{{margin-bottom:12px}}li span{{display:block;color:#9BA4AF;font-size:15px}}ul{{padding-left:20px;margin:0}}</style></head>
<body><main><nav><a href="/">SteelGames</a></nav><h1>PC game deals</h1>
<p style="color:#9BA4AF;margin:0">Fresh lists every day. Updated {today}.</p><ul>{lis}</ul></main></body></html>
"""


def main():
    today = datetime.now(timezone.utc).strftime("%B %d, %Y").replace(" 0", " ")
    sample = sys.argv[sys.argv.index("--sample") + 1] if "--sample" in sys.argv else None
    if sample:
        data = json.load(open(sample))
        stores, fetch = data["stores"], lambda q: data["deals"]
    else:
        stores = {s["storeID"]: s["storeName"] for s in get("/stores")}
        fetch = lambda q: get("/deals", {**q, "pageSize": 40, "onSale": 1})
    urls = [f"{SITE}/", f"{SITE}/app/", f"{SITE}/gear.html", f"{SITE}/advertise.html", f"{SITE}/deals/"]
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
    os.makedirs(os.path.join(ROOT, "deals"), exist_ok=True)
    open(os.path.join(ROOT, "deals", "index.html"), "w").write(hub_html(today))
    iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc><lastmod>{iso}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
