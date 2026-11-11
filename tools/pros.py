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


PALETTE = [("DDR5", "DDR5 16Gb", "#E0650A"), ("DDR4", "DDR4 16Gb", "#1C9DB0"), ("DDR4-8", "DDR4 8Gb", "#9466E8"), ("GDDR6", "GDDR6 8Gb", "#A88A14")]
KIND_ICON = {"mouse": "mouse", "keyboard": "keyboard", "headset": "headset", "controller": "controller", "pad": "pad", "monitor": "monitor", "mic": "mic", "chair": "chair"}
LIVE_CSS = """<style>
.ram-tape{position:relative;overflow:hidden;background:#0A0619;border-bottom:1px solid var(--line-strong);font:600 14px/1 var(--display);white-space:nowrap}
.ram-tape::before{content:"LIVE RAM";position:absolute;left:0;top:0;bottom:0;z-index:2;display:flex;align-items:center;gap:6px;padding:0 12px 0 14px;background:linear-gradient(90deg,#0A0619 80%,transparent);color:#FF8A1A;letter-spacing:1.5px;font-size:12px}
.tape-run{display:inline-flex;align-items:center;gap:18px;padding:11px 0 11px 110px;animation:tape 60s linear infinite}
.ram-tape:hover .tape-run{animation-play-state:paused}
@keyframes tape{to{transform:translateX(-50%)}}
.tk{color:#fff;text-decoration:none}.tk b{color:var(--muted);font-weight:600;margin-right:4px}.tk i{font-style:normal;margin-left:4px}
.up{color:#7CF0A8}.dn{color:#FF8FA6}.fl{color:var(--muted)}.sep{color:var(--line-strong)}
.ram-board{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:20px;margin-top:6px}
.ram-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px 16px;margin-bottom:12px}
.ram-head h2{display:flex;align-items:center;gap:10px}
.live-dot{width:10px;height:10px;border-radius:50%;background:#FF4D4D;box-shadow:0 0 0 0 rgba(255,77,77,.7);animation:ping 1.6s infinite}
@keyframes ping{70%{box-shadow:0 0 0 10px rgba(255,77,77,0)}100%{box-shadow:0 0 0 0 rgba(255,77,77,0)}}
.ram-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:14px}
.rstat{display:grid;gap:2px;padding:12px 14px;border-radius:12px;background:var(--raised);position:relative}
.rstat .sw{position:absolute;left:0;top:12px;bottom:12px;width:4px;border-radius:0 4px 4px 0}
.rstat small{color:var(--muted);font-size:13px}.rstat strong{font:700 26px var(--display)}.rstat em{font-style:normal;font-weight:600;font-size:14px}.rstat .rng{font-size:12px;color:var(--muted)}
.ram-ctl{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}.ram-ctl .gap{flex:1}
.ram-ctl button{display:inline-flex;align-items:center;gap:6px;font:600 13px var(--body);color:#fff;background:transparent;border:1px solid var(--line-strong);border-radius:999px;padding:7px 12px;cursor:pointer;min-height:36px}
.ram-ctl button[aria-pressed="true"]{background:var(--chip);border-color:transparent}
.ram-ctl .sw,.tip i{display:inline-block;width:10px;height:10px;border-radius:3px}
.ram-chart{position:relative;min-height:220px}.ram-chart svg{display:block;width:100%;height:auto;touch-action:pan-y}
.ram-chart text{fill:var(--muted);font:12px var(--body)}.ram-chart .g{stroke:rgba(201,194,238,.12)}.ram-chart .xh{stroke:rgba(255,255,255,.4);stroke-dasharray:3 3}
.ram-chart .pulse{animation:pl 1.6s ease-in-out infinite}@keyframes pl{50%{opacity:.45}}
.tip{position:absolute;top:0;pointer-events:none;background:#0A0619;border:1px solid var(--line-strong);border-radius:10px;padding:8px 10px;font-size:13px;display:grid;gap:3px;min-width:170px;box-shadow:0 8px 24px rgba(0,0,0,.5)}
.tip[hidden]{display:none}.tip span{display:flex;align-items:center;gap:6px}.tip strong{margin-left:auto}
.ram-kits{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;margin-top:16px}
.kit{display:flex;align-items:center;gap:12px;padding:10px;border-radius:12px;background:var(--raised);color:#fff;text-decoration:none;min-width:0}
.kit:hover{outline:1px solid var(--chip)}.kit img{width:56px;height:56px;object-fit:contain;background:#fff;border-radius:8px;flex:none}
.kit span{flex:1;min-width:0;font-size:14px;line-height:1.3;overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical}.kit small{display:block;color:var(--muted);font-size:12px}
.kit strong{font:700 16px var(--display);text-align:right}.kit em{display:block;font:500 12px var(--body);color:var(--muted);font-style:normal}
.best-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
.bs{position:relative;display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden;color:#fff;text-decoration:none;transition:transform .15s ease,border-color .15s ease}
.bs:hover{transform:translateY(-3px) rotate(-.4deg);border-color:#FF8A1A;color:#fff}
.bs .pic{background:#fff;aspect-ratio:1;display:grid;place-items:center;padding:14px}.bs .pic img{max-width:100%;max-height:100%;object-fit:contain}
.bs .rk{position:absolute;top:10px;left:10px;font:700 15px var(--display);background:#0A0619;color:#FFB020;border:2px solid #FFB020;border-radius:10px;padding:2px 8px}
.bs .rk.r1{background:#FFB020;color:#1F1000}.bs .pa{position:absolute;top:10px;right:10px;font:700 11px var(--body);letter-spacing:.5px;text-transform:uppercase;background:var(--chip);border-radius:999px;padding:4px 8px}
.bs .bi{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}.bs h3{font-size:15px;line-height:1.3}
.bs .meta{display:flex;justify-content:space-between;align-items:baseline;margin-top:auto;font-size:13px;color:var(--muted)}.bs .meta b{font:700 19px var(--display);color:#fff}
.roulette{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:14px 0}
.reel{display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;min-height:230px;padding:14px;border-radius:16px;background:var(--surface);border:2px dashed var(--line-strong);font-size:14px}
.reel img{width:96px;height:96px;object-fit:contain;background:#fff;border-radius:12px}.reel b{font-family:var(--display);line-height:1.25}.reel a{font-size:13px;margin-top:auto}
.reel.spinning{filter:blur(1.5px);border-color:#FF8A1A}.reel .q{margin:auto;font:700 46px var(--display);color:var(--line-strong)}
#rlTotal{min-height:1.6em}
@media (max-width:640px){.ram-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.rstat strong{font-size:22px}.ram-board{padding:14px}.roulette{grid-template-columns:minmax(0,1fr)}.reel{min-height:0}.ram-ctl .gap{flex-basis:100%;height:0}}
@media (prefers-reduced-motion:reduce){.tape-run,.live-dot,.ram-chart .pulse{animation:none}.bs{transition:none}}
</style>
"""


def _load(name, default):
    try:
        return json.load(open(os.path.join(ROOT, "data", name)))
    except Exception:
        return default


def ram_section(ram):
    stats = ""
    for sym, label, color in PALETTE:  # server-rendered so the numbers show even before the script runs
        t = (ram.get("today") or {}).get(sym)
        if t:
            cls = "up" if (t.get("chg") or 0) > 0 else "dn" if (t.get("chg") or 0) < 0 else "fl"
            arrow = {"up": "▲", "dn": "▼", "fl": "■"}[cls]
            stats += (f'<div class="rstat"><span class="sw" style="background:{color}"></span><small>{_e(label)} chip</small>'
                      f'<strong>${t["avg"]:,.2f}</strong><em class="{cls}">{arrow} {abs(t.get("chg") or 0):.2f}% today</em>'
                      f'<span class="rng">Day range ${t.get("lo") or 0:,.2f} – ${t.get("hi") or 0:,.2f}</span></div>')
    return f"""<section class="block"><div class="wrap"><div class="ram-board" id="ram">
<div class="ram-head"><h2><span class="live-dot" aria-hidden="true"></span>RAM price tracker</h2><span class="fine" id="ramUpdated" aria-live="polite"></span></div>
<p class="fine" style="margin:0 0 12px">Memory prices have exploded as AI data centers buy up chips. This tracks the wholesale spot price of one memory chip (what RAM makers pay), plus what the best-selling RAM kits cost on Amazon right now.</p>
<div class="ram-stats" id="ramStats">{stats}</div>
<div class="ram-ctl" id="ramCtl" role="group" aria-label="Chart options"></div>
<div class="ram-chart" id="ramChart"></div>
<p class="fine" id="ramNote"></p>
<h3 style="margin-top:14px">Best-selling RAM kits on Amazon</h3>
<div class="ram-kits" id="ramKits"></div>
<p class="fine">Spot prices: <a href="https://www.dramexchange.com/" rel="nofollow noopener" target="_blank">DRAMeXchange</a> session average, USD per chip. Kit prices: Amazon Best Sellers in Computer Memory. Checked every two hours.</p>
</div></div></section>
"""


def best_section(best):
    pro_asins = set()
    for v in ITEMS.values():  # gear our pro pages already recommend as budget or step-up picks
        m = __import__("re").search(r"/dp/([A-Z0-9]{10})", v.get("url", ""))
        if m:
            pro_asins.add(m.group(1))
    cards = ""
    for i in best.get("items", [])[:20]:
        icon = KIND_ICON.get(i.get("kind"), "mouse")
        rating = f'★ {i["stars"]:.1f}' + (f' · {i["ratings"]:,}' if i.get("ratings") else "") if i.get("stars") else ""
        price = f'<b>${i["price"]:,.2f}</b>' if i.get("price") else "<b>See price</b>"
        cards += (f'<a class="bs" href="{_e(i["url"])}" {REL}><span class="rk{" r1" if i["rank"] == best["items"][0]["rank"] else ""}">#{i["rank"]}</span>'
                  + ('<span class="pa">Pro pick</span>' if i["asin"] in pro_asins else "")
                  + f'<span class="pic"><img src="{_e(i["img"])}" alt="{_e(i["short"])}" loading="lazy" width="200" height="200" '
                  f'onerror="this.onerror=null;this.src=\'/assets/gear-icons/{icon}.svg\'"></span>'
                  f'<span class="bi"><h3>{_e(i["short"])}</h3><span class="meta">{price}<span>{rating}</span></span></span></a>')
    slim = {"items": [{k: i.get(k) for k in ("short", "img", "price", "url", "kind")} for i in best.get("items", [])]}
    return cards, json.dumps(slim).replace("<", "\\u003c")


def hub(cat):
    ram, best = _load("ram.json", {}), _load("bestsellers.json", {"items": []})
    cards = ""
    for p in PROS:
        top = " · ".join(n for k, n in p["gear"][:3])
        cards += (f'<a class="hub-card pro-card" href="/pros/{p["slug"]}/"><span class="pro-av" aria-hidden="true">{_e(initials(p["name"]))}</span>'
                  f'<h3>{_e(p["name"])}</h3><p>{_e(p["known"])}</p><p class="pro-top">{_e(top)}</p><span class="go">See the full setup &rarr;</span></a>')
    best_cards, best_json = best_section(best)
    best_html = ""
    if best_cards:
        best_html = f"""<section class="block"><div class="wrap">
<h2>What gamers are actually buying</h2>
<p class="fine">Amazon's top-selling PC gaming gear right now, refreshed every two hours. Gift cards and game codes left out. <span class="pa-key">"Pro pick"</span> means it is one of the cheaper picks on our pro setup pages.</p>
<div class="best-grid">{best_cards}</div></div></section>
<section class="block"><div class="wrap">
<h2>Loadout Roulette</h2>
<p class="fine">Can a random best-seller setup beat a pro's? Spin for a mouse, keyboard and headset from Amazon's top sellers.</p>
<div class="roulette" id="roulette"><div class="reel"><span class="q">?</span>Mouse</div><div class="reel"><span class="q">?</span>Keyboard</div><div class="reel"><span class="q">?</span>Headset</div></div>
<p id="rlTotal" aria-live="polite"></p><button type="button" class="btn" id="rlSpin">Spin my loadout</button>
<script type="application/json" id="bestData">{best_json}</script>
</div></section>
"""
    tape = '<div class="ram-tape" id="ramTape" aria-label="Live RAM prices"><div class="tape-run"><span class="tk">Loading live RAM prices…</span></div></div>\n'
    return (layout.head(f"Pro gaming setups: what top streamers use ({CHECKED}) | SteelGames",
                        "The mice, keyboards, headsets and monitors the biggest US-based gamers use, Amazon's best-selling gaming gear right now, and a live RAM price tracker.",
                        f"{SITE}/pros/", LIVE_CSS + '<script src="/assets/pros-live.js?v=1" defer></script>\n') + layout.header("pros") + tape + f"""<main>
{ram_section(ram) if ram.get("today") else ""}<section class="hero"><div class="wrap">
<p class="eyebrow">Pro setups &middot; checked {CHECKED}</p>
<h1>What the pros play on</h1>
<p class="lede">The exact gear the biggest US-based streamers and pros use, where to buy it, and a cheaper pick for every piece.</p>
<div class="chips"><a href="#best">Amazon best sellers</a><a href="#roulette">Loadout Roulette</a><a href="#ram">RAM prices</a><a href="/gear.html">All gaming gear</a></div>
</div></section>
<section class="block"><div class="wrap"><div class="hub-grid">{cards}</div>
<p class="fine">Setups come from public pro-settings databases, credited on each page. SteelGames is not affiliated with or endorsed by these players.</p></div></section>
<div id="best"></div>{best_html}</main>
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
