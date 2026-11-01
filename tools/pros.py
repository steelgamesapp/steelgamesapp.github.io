"""Pro Setups: what the biggest US-based gamers actually use, with where to buy it and a cheaper pick for each piece.

Builds /pros/ (hub) and /pros/<slug>/ (one page per player). Gear comes from public setup databases, listed per
player with the date it was checked; players change gear often, so update PROS when a source changes.
Every item links to Amazon with the steelgames-20 tag. Items we already stock link straight to the product with its
photo; the rest use a tagged Amazon search (still earns commission) and a drawing of that gear type.
No player photos are used anywhere: players are shown by initials only.
"""
import html
import json
import os
import urllib.parse

import layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = layout.SITE
RULES = json.load(open(os.path.join(ROOT, "tools", "gear_rules.json")))
ITEMS = RULES["items"]
TAG = "steelgames-20"
CHECKED = "November 2026"

KIND = {  # label, icon, budget pick, step-up pick (keys in gear_rules.json items)
    "mouse": ("Mouse", "mouse", "g305", "superlight2"),
    "keyboard": ("Keyboard", "keyboard", "aulaf75", "huntsman"),
    "headset": ("Headset", "headset", "blackshark", "cloud3"),
    "monitor": ("Monitor", "monitor", "sansui", "lg27gr75q"),
    "mousepad": ("Mousepad", "pad", "qck", None),
    "mic": ("Microphone", "mic", "am8", "quadcast"),
    "controller": ("Controller", "controller", "8bitdo2", "dsedge"),
    "chair": ("Chair", "chair", "gtplayer", "tc100"),
}
# Pro items we already sell with a confirmed product link and photo.
EXACT = {"Logitech G840 XL Mousepad": "Logitech G840 XL Mousepad", "SteelSeries Apex Pro TKL": "SteelSeries Apex Pro TKL Gen 3"}


def _catalog_by_name():
    out = {}
    for v in ITEMS.values():
        out[v["name"]] = v
    try:  # the wider gear catalog from the Gear page
        for o in json.load(open(os.path.join(ROOT, "tools", "gear_catalog_all.json"))):
            out.setdefault(o["name"], o)
    except Exception:
        pass
    return out


PROS = [
    {"slug": "shroud", "name": "shroud", "real": "Michael Grzesiek", "known": "Variety FPS streamer, former CS:GO pro",
     "games": "VALORANT, CS2, PUBG, variety shooters",
     "source": ("Hotspawn, May 2026", "https://www.hotspawn.com/?p=177032"),
     "gear": [("mouse", "Logitech G Pro X2 SUPERSTRIKE"), ("keyboard", "Logitech PRO X TKL"), ("headset", "Logitech PRO X 2 Wireless"),
              ("monitor", "ASUS ROG Swift OLED PG27AQDM"), ("mousepad", "Logitech G840 XL Mousepad")]},
    {"slug": "ninja", "name": "Ninja", "real": "Tyler Blevins", "known": "The face of Fortnite streaming",
     "games": "Fortnite, VALORANT",
     "source": ("setup.gg", "https://www.setup.gg/ninja-valorant-setup-2/"),
     "gear": [("mouse", "Finalmouse UltralightX"), ("keyboard", "SteelSeries Apex Pro TKL"), ("headset", "beyerdynamic DT 1990 PRO"),
              ("monitor", "Alienware AW2518H"), ("mousepad", "HyperX Fury S Pro XL"), ("mic", "Shure MV7X")]},
    {"slug": "tarik", "name": "tarik", "real": "Tarik Celik", "known": "CS major champion turned VALORANT streamer",
     "games": "VALORANT, CS2",
     "source": ("CSDB", "https://csdb.gg/players/tarik"),
     "gear": [("mouse", "Finalmouse UltralightX Large"), ("keyboard", "Wooting 60HE+"), ("headset", "beyerdynamic DT 770 PRO"),
              ("monitor", "ZOWIE XL2566K"), ("mousepad", "ZOWIE G-SR-SE Gris")]},
    {"slug": "iitztimmy", "name": "iiTzTimmy", "real": "Timothy An", "known": "Top Apex Legends streamer and pro",
     "games": "Apex Legends, VALORANT",
     "source": ("setup.gg", "https://www.setup.gg/player/iitztimmy/"),
     "gear": [("mouse", "ASUS ROG Harpe Ace Extreme"), ("keyboard", "ASUS ROG Azoth"), ("headset", "Logitech G Pro X Headset Shroud Edition"),
              ("monitor", "ASUS ROG Swift OLED PG27AQDM"), ("mousepad", "Artisan Ninja FX Zero Soft"), ("mic", "Shure SM7B"),
              ("chair", "Herman Miller Embody")]},
    {"slug": "summit1g", "name": "summit1g", "real": "Jaryd Lazar", "known": "Variety streamer with deep CS roots",
     "games": "CS2, Escape from Tarkov, variety",
     "source": ("setup.gg", "https://www.setup.gg/player/summit1g/"),
     "gear": [("mouse", "ZOWIE EC1-DW"), ("keyboard", "DrunkDeer A75"), ("headset", "Audio-Technica ATH-AD700X"),
              ("monitor", "Samsung Odyssey G7 32-inch"), ("mousepad", "Kurosun Samurai")]},
    {"slug": "nickmercs", "name": "NICKMERCS", "real": "Nick Kolcheff", "known": "The biggest controller player on PC",
     "games": "Call of Duty, Fortnite, Apex Legends",
     "source": ("SetupGamers, July 2026", "https://www.setupgamers.com/?p=4903"),
     "gear": [("controller", "SCUF Infinity 4PS PRO"), ("headset", "ASTRO A40 TR with MixAmp Pro"), ("monitor", "Alienware AW2521HF"),
              ("mic", "Shure SM7B")]},
]


def _e(t):
    return html.escape(str(t or ""))


def amazon_search(q):
    return "https://www.amazon.com/s?" + urllib.parse.urlencode({"k": q, "tag": TAG})


REL = 'target="_blank" rel="sponsored nofollow noopener"'
ARROW = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>')


def initials(name):
    return name.strip()[:1].upper()


def item_card(kind, name, cat):
    lab, icon, budget, step = KIND[kind]
    exact = cat.get(EXACT.get(name, name))
    url = exact["url"] if exact else amazon_search(name)
    img = exact["img"] if exact and exact.get("img") else f"/assets/gear-icons/{icon}.svg"
    fb = f"this.onerror=null;this.src='/assets/gear-icons/{icon}.svg';this.closest('.gimg').classList.add('icon')"
    alts = ""
    for tag, key in (("Budget pick", budget), ("Step up", step)):
        a = ITEMS.get(key or "")
        if a and a["name"] != (exact or {}).get("name"):
            alts += (f'<a class="gup" href="{_e(a["url"])}" {REL}><img src="{_e(a["img"])}" alt="" loading="lazy" width="56" height="56" '
                     f'onerror="this.onerror=null;this.src=\'/assets/gear-icons/{icon}.svg\'"><span><small>{tag}</small>{_e(a["name"])}</span></a>')
    return (f'<article class="gcar"><p class="gl">{_e(lab)}</p>'
            f'<a class="gimg{"" if exact else " icon"}" href="{_e(url)}" {REL} tabindex="-1" aria-hidden="true"><img src="{_e(img)}" alt="{_e(name)}" loading="lazy" width="400" height="300" onerror="{fb}"></a>'
            f'<div class="gb"><span class="gtag pro">Pro pick</span><h3>{_e(name)}</h3>'
            f'<a class="btn gbuy" href="{_e(url)}" {REL}>Shop on Amazon{ARROW}</a>'
            + (f'<p class="alt-h">Same job for less</p>{alts}' if alts else "") + '</div></article>')


def pro_page(p, cat):
    title = f"{p['name']} setup: the gear {p['name']} uses ({CHECKED}) | SteelGames"
    desc = f"The mouse, keyboard, headset and monitor {p['name']} uses, where to buy each one, and cheaper picks that do the same job."
    url = f"{SITE}/pros/{p['slug']}/"
    cards = "".join(item_card(k, n, cat) for k, n in p["gear"])
    faq = [(f"What mouse does {p['name']} use?", next((n for k, n in p["gear"] if k == "mouse"), "A controller: " + next((n for k, n in p["gear"] if k == "controller"), "see the list above"))),
           (f"What monitor does {p['name']} use?", next((n for k, n in p["gear"] if k == "monitor"), "Not listed")),
           (f"Is this list current?", f"It matches {p['source'][0]}, checked {CHECKED}. Players change gear often, so check back.")]
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "ItemList", "name": f"{p['name']} setup",
         "itemListElement": [{"@type": "ListItem", "position": i, "name": n} for i, (k, n) in enumerate(p["gear"], 1)]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]).replace("<", "\\u003c")
    others = "".join(f'<a href="/pros/{o["slug"]}/">{_e(o["name"])}</a>' for o in PROS if o is not p)
    faq_html = "".join(f"<details><summary>{_e(q)}</summary><p>{_e(a)}</p></details>" for q, a in faq)
    return (layout.head(title, desc, url, f'<script type="application/ld+json">{ld}</script>\n') + layout.header("pros") + f"""<main>
<section class="hero"><div class="wrap">
<p class="crumbs"><a href="/">Home</a> / <a href="/pros/">Pro setups</a></p>
<div class="pro-id"><span class="pro-av" aria-hidden="true">{_e(initials(p['name']))}</span><div>
<p class="eyebrow">Pro setup &middot; checked {CHECKED}</p>
<h1>{_e(p['name'])}'s setup</h1>
<p class="lede">{_e(p['known'])}. Plays {_e(p['games'])}. Here is the gear {_e(p['name'])} uses, plus cheaper picks that do the same job.</p>
</div></div>
</div></section>
<section class="block gear"><div class="wrap">
<div class="gear-grid">{cards}</div>
<p class="fine">Gear list from <a href="{_e(p['source'][1])}" rel="nofollow noopener" target="_blank">{_e(p['source'][0])}</a>. SteelGames is not affiliated with or endorsed by {_e(p['name'])}. Pros change gear often. SteelGames may earn a commission on purchases.</p>
</div></section>
<section class="block"><div class="wrap"><h2>Questions</h2><div class="faq">{faq_html}</div></div></section>
<section class="block"><div class="wrap"><h2>More pro setups</h2><div class="more-lists">{others}</div></div></section>
</main>
""" + layout.footer())


def hub(cat):
    cards = ""
    for p in PROS:
        top = " · ".join(n for k, n in p["gear"][:3])
        cards += (f'<a class="hub-card pro-card" href="/pros/{p["slug"]}/"><span class="pro-av" aria-hidden="true">{_e(initials(p["name"]))}</span>'
                  f'<h3>{_e(p["name"])}</h3><p>{_e(p["known"])}</p><p class="pro-top">{_e(top)}</p><span class="go">See the full setup &rarr;</span></a>')
    return (layout.head(f"Pro gaming setups: what top streamers use ({CHECKED}) | SteelGames",
                        "The mice, keyboards, headsets and monitors the biggest US-based gamers use, with where to buy each and cheaper picks.",
                        f"{SITE}/pros/") + layout.header("pros") + f"""<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Pro setups &middot; checked {CHECKED}</p>
<h1>What the pros play on</h1>
<p class="lede">The exact gear the biggest US-based streamers and pros use, where to buy it, and a cheaper pick for every piece.</p>
<div class="chips"><a href="/gear.html">All gaming gear</a><a href="/games.html">Game deals</a></div>
</div></section>
<section class="block"><div class="wrap"><div class="hub-grid">{cards}</div>
<p class="fine">Setups come from public pro-settings databases, credited on each page. SteelGames is not affiliated with or endorsed by these players.</p></div></section>
</main>
""" + layout.footer())


def build_all():
    """Write /pros/ and every player page. Returns their URLs for the sitemap."""
    cat = _catalog_by_name()
    base = os.path.join(ROOT, "pros")
    os.makedirs(base, exist_ok=True)
    open(os.path.join(base, "index.html"), "w").write(hub(cat))
    urls = [f"{SITE}/pros/"]
    for p in PROS:
        d = os.path.join(base, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(pro_page(p, cat))
        urls.append(f"{SITE}/pros/{p['slug']}/")
    return urls


if __name__ == "__main__":
    print("\n".join(build_all()))
