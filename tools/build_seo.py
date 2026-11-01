#!/usr/bin/env python3
"""Builds static SEO deal pages under /deals/ from the CheapShark API.

Run daily by .github/workflows/seo.yml. Standard library only.
Usage: python3 tools/build_seo.py [--sample path.json]   (--sample skips the network, for tests)
"""
import html, json, os, sys, urllib.parse, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout
import games_page
import keys_page
import military_page
import history
import waitometer
import medals
import steam_meta
import shop_pages
import deal_page
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


def get(path, params=None, tries=5):
    """GET from the price API, backing off and retrying when it rate-limits (HTTP 429) or hiccups (5xx)."""
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"User-Agent": "SteelGames-SEO-Builder"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as ex:
            if ex.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            try:
                wait = float(ex.headers.get("Retry-After") or 0)
            except Exception:
                wait = 0
            wait = max(wait, 5 * (2 ** attempt))  # 5, 10, 20, 40 s
            print(f"rate limited on {path} ({ex.code}), waiting {wait:.0f}s", file=sys.stderr)
            time.sleep(min(wait, 90))


def money(v):
    try:
        return "$%.2f" % float(v)
    except Exception:
        return "-"


STORE_COLORS = {"Steam": "#66C0F4", "GreenManGaming": "#5CE08A", "Fanatical": "#FF8A3D", "GOG": "#B388FF", "Epic Games Store": "#E8E8F0",
                "Humble Store": "#FF5A5F", "GameBillet": "#FFD43B", "Gamesplanet": "#4DD0E1", "GamersGate": "#FF7043", "Voidu": "#F06292",
                "Direct2Drive": "#9CCC65", "IndieGala": "#FF5252", "WinGameStore": "#4FC3F7", "2Game": "#FFB74D", "Games Republic": "#A1887F"}


FAILED = []  # steps that failed; surfaced as an Actions warning
OFFLINE = False  # set by --sample so tests never touch the network


def fetch_lows(gids):
    """Lowest price on record per game id, batched 25 at a time. Missing ids simply get no medal."""
    out = {}
    if OFFLINE:
        return out
    gids = list(gids)
    for i in range(0, len(gids), 25):
        try:
            data = get("/games", {"ids": ",".join(gids[i:i + 25])})
            for gid, g in data.items():
                out[str(gid)] = float((g.get("cheapestPriceEver") or {}).get("price") or 0)
        except Exception as ex:
            print("lows failed", ex, file=sys.stderr)
        time.sleep(0.3)
    return out


def page_html(p, deals, stores, today):
    e = html.escape
    url = f"{SITE}/deals/{p['slug']}/"
    best = {}
    for d in deals:
        gid = str(d.get("gameID"))
        if gid not in best or float(d.get("salePrice") or 0) < float(best[gid].get("salePrice") or 0):
            best[gid] = d
    deals = [best[g] for g in dict.fromkeys(str(d.get("gameID")) for d in deals)]
    rows, items = [], []
    lows = fetch_lows(str(d.get("gameID")) for d in deals)
    _today = datetime.now(timezone.utc).date()
    for i, d in enumerate(deals, 1):
        store = stores.get(str(d.get("storeID")), "Store")
        sav = round(float(d.get("savings") or 0))
        rate = d.get("steamRatingPercent")
        rating = f" · {rate}% positive ({e(d.get('steamRatingText') or '')})" if rate and rate != "0" else ""
        link = f"{SITE}/deal/?id={d.get('gameID')}"
        price = float(d.get("salePrice") or 0)
        price_txt = "Free" if price == 0 else money(price)
        was = f'<span class="was">{money(d.get("normalPrice"))}</span>' if sav > 0 else ""
        off = f'<span class="off">-{sav}%</span>' if sav > 0 else ""
        col = STORE_COLORS.get(store, "#7B5CFF")
        _mk, _ = medals.rank(price, lows.get(str(d.get("gameID")), 0), history._load(str(d.get("gameID"))), _today)
        mchip = medals.chip(_mk) if _mk else ""
        _h = (f'<button type="button" class="heart" data-wish data-id="{e(str(d.get("gameID")))}" data-title="{e(d.get("title", ""))}" data-thumb="{e(d.get("thumb") or "")}"'
              f' data-steam="{e(str(d.get("steamAppID") or "") if str(d.get("steamAppID") or "") != "0" else "")}" data-price="{price:.2f}" aria-pressed="false">{layout.HEART}</button>')
        rows.append(
            f'<div class="drow-w"><a class="drow" style="--store:{col}" href="{e(link)}"><span class="n">{i}</span>'
            f'<img src="{e(layout.img_for(d))}" alt="" loading="lazy" width="184" height="69">'
            f'<span class="txt"><span class="t">{e(d.get("title", ""))}</span><span class="m"><b>{e(store)}</b>{rating}{mchip}</span></span>'
            f'<span class="pr"><span><span class="price">{price_txt}</span>{was}</span>{off}</span></a>{_h}</div>')
        items.append({"@type": "ListItem", "position": i, "url": link, "name": d.get("title", "")})
    listing = ('<div class="deal-list">' + "".join(rows) + "</div>") if rows else '<p class="empty">No deals match right now. Check back tomorrow.</p>'
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    others = "".join(f"<a href=\"/deals/{o['slug']}/\">{e(o['h1'])}</a>" for o in PAGES if o["slug"] != p["slug"] and not o["slug"].startswith("deals-"))
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "ItemList", "name": p["h1"], "itemListElement": items},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
    ]).replace("<", "\\u003c")
    return (layout.head(f"{p['h1']} - {today} | SteelGames", p["desc"], url, f'<script type="application/ld+json">{ld}</script>\n')
        + layout.header()
        + f"""<main>
<section class="hero"><div class="wrap">
<p class="crumbs"><a href="/">Home</a> / <a href="/deals/">Deals</a></p>
<p class="eyebrow">Updated {today}</p>
<h1>{e(p['h1'])}</h1>
<p class="lede">{e(p['intro'])}</p>
<div class="chips"><a href="/games.html">Browse all games</a><a href="/deals/">All deal lists</a></div>
</div></section>
<section class="block"><div class="wrap">
{listing}
<p class="fine">Prices come from official stores and key sellers and can change at any time. Tap a game to compare every store.</p>
</div></section>
<section class="block"><div class="wrap"><h2>Questions</h2><div class="faq">{faq_html}</div></div></section>
<section class="block"><div class="wrap"><h2>More deal lists</h2><div class="more-lists">{others}</div></div></section>
</main>
""" + layout.footer())


def hub_html(today):
    e = html.escape
    def card(p):
        return (f"<a class=\"hub-card\" href=\"/deals/{p['slug']}/\"><h3>{e(p['h1'])}</h3><p>{e(p['desc'])}</p>"
                f"<span class=\"go\">View list &rarr;</span></a>")
    main_cards = "".join(card(p) for p in PAGES if not p["slug"].startswith("deals-"))
    theme_cards = "".join(card(p) for p in PAGES if p["slug"].startswith("deals-"))
    return (layout.head("PC Game Deals | SteelGames", "Daily PC game deal lists from SteelGames: games under $5, under $10, best Steam deals, highly rated sales and free games.", f"{SITE}/deals/")
        + layout.header()
        + f"""<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Fresh every day &middot; Updated {today}</p>
<h1>PC game deal lists</h1>
<p class="lede">Hand-picked ways to find a great price: by budget, by store and by what you like to play. Every list is rebuilt each day from live store prices.</p>
<div class="chips"><a href="/games.html">Browse all games</a><a href="/gear.html">Gaming gear</a></div>
</div></section>
<section class="block"><div class="wrap"><h2>Best deal lists</h2><div class="hub-grid">{main_cards}</div></div></section>
<section class="block"><div class="wrap"><h2>Deals by type of game</h2><div class="hub-grid">{theme_cards}</div></div></section>
</main>
""" + layout.footer())


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


MEDALS = {}


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
    _h = history.update(gid, datetime.now(timezone.utc).strftime("%Y-%m-%d"), cur, low, ts)
    chart = history.render(_h, reg, low)
    _medal, _mdetail = medals.rank(cur, low, _h, datetime.now(timezone.utc).date())
    MEDALS[gid] = _medal
    medal_html = medals.badge(_medal, _mdetail) if _medal else ""
    _wom = waitometer.assess(cur, reg, low, datetime.now(timezone.utc).date(), _h, stores[str(best['storeID'])])
    label, detail = _wom['label'], waitometer.faq_text(_wom)
    slug = f"{slugify(title)}-{gid}"
    url = f"{SITE}/game/{slug}/"
    rows = "".join(f"<tr><td>{e(stores[str(d['storeID'])])}</td><td>{money(d['price'])}</td><td class=\"was\">{money(d['retailPrice'])}</td><td><a class=\"go\" rel=\"sponsored noopener\" href=\"https://www.cheapshark.com/redirect?dealID={e(str(d.get('dealID','')))}\">Buy</a></td></tr>" for d in deals)
    _m = steam_meta.get(str(info.get("steamAppID") or ""))
    _desc, meta_html = steam_meta.details_html(_m) if _m else ("", steam_meta.fallback_html())
    faq = [(f"What is the lowest price ever for {title}?", f"The lowest recorded price is {money(low)}{(' in ' + when) if when else ''}." if low > 0 else "We don't have a recorded lowest price for this game yet."),
           (f"Is {title} on sale right now?", f"The best current price we found is {money(cur)} at {stores[str(best['storeID'])]}, against a usual price of {money(reg)}."),
           (f"Should I buy {title} now or wait?", f"{label}. {detail}")]
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "Product", "name": title, "image": info.get("thumb") or "", **({"description": _desc} if _desc else {}),
         "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": "%.2f" % cur, "highPrice": "%.2f" % float(deals[-1]["price"]), "offerCount": len(deals)}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]).replace("<", "\\u003c")
    desc = f"{title} price today: {money(cur)} at {stores[str(best['storeID'])]}. {label}. Compare official store prices and see the lowest price ever."
    sid = str(info.get("steamAppID") or "")
    cover = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg" if sid and sid != "0" else (info.get("thumb") or "")
    if _m:
        cover = _m.get("header") or cover
    lede_html = f'<p class="lede">{e(_desc)}</p>' if _desc else ""
    vclass = "v-good" if label in ("Buy now", "Good deal") else ("v-wait" if label.startswith("Wait") else "")
    low_line = (f'<p class="fine">Lowest price ever: <strong style="color:#fff">{money(low)}</strong>' + (f" ({when})" if when else "") + "</p>") if low > 0 else ""
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    _da = (f' data-id="{e(str(gid))}" data-deal="{e(str(best.get("dealID", "")))}" data-title="{e(title)}" data-thumb="{e(info.get("thumb") or "")}" data-steam="{e(sid if sid != "0" else "")}"'
           f' data-store="{e(stores[str(best["storeID"])])}" data-price="{cur:.2f}" data-normal="{reg:.2f}" aria-pressed="false"')
    shop_btns = (f'<button type="button" data-wish{_da}>{layout.HEART}<span class="lab">Wishlist</span></button>'
                 f'<button type="button" data-cart{_da}>{layout.CARTI}<span class="lab">Add to cart</span></button>'
                 f'<button type="button" data-own{_da}>{layout.CHECKI}<span class="lab">I own this</span></button>')
    page = (layout.head(f"{title} price history and best price today | SteelGames", desc, url, f'<script type="application/ld+json">{ld}</script>\n')
        + layout.header("games")
        + f"""<main>
<section class="hero"><div class="wrap">
<p class="crumbs"><a href="/">Home</a> / <a href="/games.html">Games</a></p>
<p class="eyebrow">Price check &middot; Updated {today}</p>
<h1>{e(title)}</h1>
{lede_html}
</div></section>
<section class="block"><div class="wrap">
<div class="gp">
<img class="cover" src="{e(cover)}" alt="{e(title)} cover art" width="460" height="215" onerror="this.onerror=null;this.src='{e(info.get("thumb") or "")}'">
<div class="pricebox">
<div class="big">{money(cur)}<s>{money(reg)}</s></div>
<p class="fine">Best current price at {e(stores[str(best['storeID'])])}</p>
{medal_html}
{waitometer.widget(_wom)}
<div class="gact" style="border:0;background:none;padding:0">{shop_btns}</div>
<a class="btn" rel="sponsored noopener" href="https://www.cheapshark.com/redirect?dealID={e(str(best.get('dealID','')))}">Buy at {e(stores[str(best['storeID'])])} for {money(cur)}</a>
{low_line}
{military_page.best_for_game_html()}
</div></div>
<h2>Price history</h2>
{chart}
<h2>Compare stores</h2>
<table class="stores"><thead><tr><th>Store</th><th>Price</th><th>Usual</th><th></th></tr></thead><tbody>{rows}</tbody></table>
</div></section>
{meta_html}
<section class="block"><div class="wrap"><h2>Questions</h2><div class="faq">{faq_html}</div></div></section>
</main>
""" + layout.footer())
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
    tracked_slugs = {}
    base = os.path.join(ROOT, "game")
    # Yesterday's slugs and grid cards, so a game that fails to fetch today keeps its page instead of vanishing.
    try:
        old_slugs = json.load(open(os.path.join(base, "tracked.json")))
    except Exception:
        old_slugs = {}
    old_cards = {}
    try:
        for m in re.finditer(r'<a class="gcard" href="/game/([^/]+)/">.*?<span class="t">(.*?)</span>.*?</a>', open(os.path.join(base, "index.html")).read(), re.S):
            old_cards[m.group(1)] = (html.unescape(m.group(2)), m.group(0))
    except Exception:
        pass
    for gid in ids:
        try:
            g = fetch_game(gid)
            slug, page = game_page(gid, g, stores, today)
        except Exception as ex:
            print("game failed", gid, ex, file=sys.stderr)
            FAILED.append(f"game {gid}")
            slug, page = None, None
            old = old_slugs.get(gid)
            if old and old in old_cards and os.path.exists(os.path.join(base, old, "index.html")):
                keep.append(gid)
                tracked_slugs[gid] = old
                entries.append((old, old_cards[old][0], None, None, old_cards[old][1]))
                urls.append(f"{SITE}/game/{old}/")
        if not page:
            continue
        d = os.path.join(base, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(page)
        keep.append(gid)
        tracked_slugs[gid] = slug
        _info = g.get("info") or {}
        _sid = str(_info.get("steamAppID") or "")
        _img = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{_sid}/header.jpg" if _sid and _sid != "0" else (_info.get("thumb") or "")
        _low = min((float(d["price"]) for d in g.get("deals", []) if str(d.get("storeID")) in stores), default=0)
        entries.append((slug, _info.get("title", "Game"), _img, money(_low), MEDALS.get(gid)))
        urls.append(f"{SITE}/game/{slug}/")
        time.sleep(0.25)
    json.dump(keep, open(GAME_IDS_FILE, "w"))
    os.makedirs(base, exist_ok=True)
    json.dump({gid: slug for gid, slug in tracked_slugs.items() if gid in keep}, open(os.path.join(base, "tracked.json"), "w"), separators=(",", ":"))
    # Remove pages for games that are no longer tracked.
    live = {x[0] for x in entries}
    if os.path.isdir(base):
        for name in os.listdir(base):
            if name not in live and os.path.isdir(os.path.join(base, name)):
                import shutil
                shutil.rmtree(os.path.join(base, name))
    cards = "".join(
        md if im is None else  # reused card from yesterday (fetch failed today)
        f'<a class="gcard" href="/game/{s}/"><span class="pic"><img src="{html.escape(im)}" alt="" loading="lazy" width="460" height="215"></span>'
        f'<span class="info"><span class="t">{html.escape(t)}</span><span class="row"><span class="price">{pr}</span>{medals.chip(md) if md else ""}</span></span></a>'
        for s, t, im, pr, md in sorted(entries, key=lambda x: x[1].lower()))
    os.makedirs(base, exist_ok=True)
    open(os.path.join(base, "index.html"), "w").write(
        layout.head("PC game prices and price history | SteelGames", "Current best prices and lowest-ever prices for popular PC games from official stores.", f"{SITE}/game/")
        + layout.header("games")
        + f"""<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Updated {today}</p>
<h1>PC game prices and price history</h1>
<p class="lede">Check today's best price and the lowest price ever for popular PC games.</p>
<div class="chips"><a href="/games.html">Search all games</a></div>
</div></section>
<section class="block"><div class="wrap"><div class="game-grid">{cards}</div></div></section>
</main>
""" + layout.footer())
    return [f"{SITE}/game/"] + urls


def main():
    today = datetime.now(timezone.utc).strftime("%B %d, %Y").replace(" 0", " ")
    sample = sys.argv[sys.argv.index("--sample") + 1] if "--sample" in sys.argv else None
    global OFFLINE
    OFFLINE = bool(sample)
    steam_meta.OFFLINE = OFFLINE
    if sample:
        data = json.load(open(sample))
        stores, fetch = data["stores"], lambda q: data["deals"]
    else:
        stores = {s["storeID"]: s["storeName"] for s in get("/stores")}
        fetch = lambda q: get("/deals", {**q, "pageSize": 40, "onSale": 1})
    urls = [f"{SITE}/", f"{SITE}/games.html", f"{SITE}/keys.html", f"{SITE}/get-app/", f"{SITE}/gear.html", f"{SITE}/reviews.html", f"{SITE}/community.html", f"{SITE}/military.html", f"{SITE}/advertise.html", f"{SITE}/deals/"]
    for p in PAGES:
        try:
            deals = fetch(p["q"])
        except Exception as ex:
            print("fetch failed for", p["slug"], ex, file=sys.stderr)
            FAILED.append(p["slug"])
            # Keep yesterday's page (and its sitemap entry) rather than dropping it.
            if os.path.exists(os.path.join(ROOT, "deals", p["slug"], "index.html")):
                urls.append(f"{SITE}/deals/{p['slug']}/")
            continue
        d = os.path.join(ROOT, "deals", p["slug"])
        if not deals and os.path.exists(os.path.join(d, "index.html")):
            print("no deals returned for", p["slug"], "- keeping yesterday's page", file=sys.stderr)
            urls.append(f"{SITE}/deals/{p['slug']}/")
            continue
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(page_html(p, deals, stores, today))
        urls.append(f"{SITE}/deals/{p['slug']}/")
        print("built", p["slug"], len(deals))
        if not sample:
            time.sleep(1.0)
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
        FAILED.append("games")
        # Keep existing game pages in the sitemap so a bad day doesn't de-index them.
        gbase = os.path.join(ROOT, "game")
        if os.path.isdir(gbase):
            urls.append(f"{SITE}/game/")
            urls += [f"{SITE}/game/{n}/" for n in sorted(os.listdir(gbase)) if os.path.isdir(os.path.join(gbase, n))]
    open(os.path.join(ROOT, "games.html"), "w").write(games_page.build())
    open(os.path.join(ROOT, "keys.html"), "w").write(keys_page.build())
    os.makedirs(os.path.join(ROOT, "deal"), exist_ok=True)
    open(os.path.join(ROOT, "deal", "index.html"), "w").write(deal_page.build())
    open(os.path.join(ROOT, "wishlist.html"), "w").write(shop_pages.wishlist())
    open(os.path.join(ROOT, "cart.html"), "w").write(shop_pages.cart())
    open(os.path.join(ROOT, "collection.html"), "w").write(shop_pages.collection())
    open(os.path.join(ROOT, "sync.html"), "w").write(shop_pages.sync())
    open(os.path.join(ROOT, "military.html"), "w").write(military_page.build())
    os.makedirs(os.path.join(ROOT, "deals"), exist_ok=True)
    open(os.path.join(ROOT, "deals", "index.html"), "w").write(hub_html(today))
    iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc><lastmod>{iso}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    if FAILED:
        # Shows as a yellow warning on the Actions run instead of a silent green check.
        print(f"::warning title=Partial build::{len(FAILED)} step(s) failed: {', '.join(FAILED[:15])}")


if __name__ == "__main__":
    main()
