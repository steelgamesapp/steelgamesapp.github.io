"""Builds gift-cards/index.html: a price comparison of US gaming gift cards across our affiliate stores.

Data comes from data/giftcards.json (tools/giftcards.py, every 3 hours from the stores' Impact feeds).
Every Buy button is our tracked Impact link with subId1=site-giftcards-<card><face>-<store>, so Impact
reports show which card and store earn. Promo codes live in PROMOS (shown only until their end date).
Run: python3 tools/giftcards_page.py
"""
import html
import json
import os
from datetime import date, datetime, timezone

import layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "giftcards.json")
OUT = os.path.join(ROOT, "gift-cards", "index.html")
e = html.escape

OFFICIAL = {
    "psn": ("PlayStation Store", "https://store.playstation.com/"),
    "xbox": ("Microsoft Store", "https://www.xbox.com/en-US/microsoft-store"),
    "nintendo": ("Nintendo eShop", "https://www.nintendo.com/us/store/"),
    "steam": ("Steam", "https://store.steampowered.com/digitalgiftcards/"),
    "roblox": ("Roblox", "https://www.roblox.com/giftcards"),
}
BLURB = {
    "psn": "Adds money to a US PlayStation account: games, add-ons, PS Plus and in-game currency on PS4 and PS5.",
    "xbox": "Adds money to a US Xbox account: games, Game Pass, and currency like V-Bucks, COD Points and Minecoins.",
    "nintendo": "Adds money to a US Nintendo account for Switch and Switch 2 games and DLC.",
    "steam": "Adds money to a US Steam wallet for games, DLC and in-game items.",
    "roblox": "Robux and Roblox Premium. Check that the card works in your country before you buy.",
}
PROMOS = [
    {"store": "all", "until": "2026-12-01", "html": '<b>Black Friday and Cyber Monday:</b> gift cards under face value plus live gear and PC game deals. <a href="/black-friday/">See every deal</a>.'},
    {"store": "kinguin", "until": "2026-11-26", "html": 'Kinguin reader code <b class="gc-hl">STEEL4</b>: 4% off the Prepaid category, Nov 12 to Nov 26 (carts up to &euro;150, two uses per person).'},
]


def money(v):
    return f"${v:,.2f}"


def ago(ts):
    try:
        t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return ""
    m = int((datetime.now(timezone.utc) - t).total_seconds() // 60)
    return "just now" if m < 2 else f"{m} min ago" if m < 90 else f"{m // 60} hours ago" if m < 48 * 60 else f"{m // 1440} days ago"


def track(url, card, face, store):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}subId1=site-giftcards-{card}{face}-{store}"


def offer_row(o, face, card, best, stores):
    pct = (face - o["usd"]) / face * 100
    badge = ""
    if best:
        badge += '<span class="gk-best">Best deal</span>'
    if pct >= 1:
        badge += f'<span class="gk-off">-{round(pct)}%</span>'
    elif pct <= -1:
        badge += '<span class="gk-over">over face value</span>'
    st = stores.get(o["store"], {})
    price = ("&asymp; " if o.get("approx") else "") + money(o["usd"])
    note = f'Converted from {o["cur"]} {o["price"]:,.2f}' if o.get("approx") else "Feed price in USD"
    return (f'<div class="gk-row"><div class="gk-store"><b>{e(st.get("name", o["store"]))}</b><small>{e(st.get("kind", ""))}</small>'
            f'<span class="gk-pn">{e(o["name"])}</span><span class="gk-up">Checked {e(ago(o.get("checked", "")))}</span></div>'
            f'<div class="gk-price"><strong>{price}</strong><span title="{e(note)}">{badge}</span></div>'
            f'<a class="gk-buy" href="{e(track(o["url"], card, face, o["store"]))}" target="_blank" rel="sponsored nofollow noopener" '
            f'data-gk="{card}{face}-{o["store"]}">Buy &#8599;</a></div>')


def face_block(card, face, offers, stores):
    off_name, off_url = OFFICIAL[card]
    rows = "".join(offer_row(o, face, card, i == 0 and o["usd"] < face, stores) for i, o in enumerate(offers))
    best = offers[0]["usd"] if offers else None
    head = (f'<span class="gk-face">${face}</span>' +
            (f'<span class="gk-from">from <b>{("&asymp; " if offers[0].get("approx") else "") + money(best)}</b></span>' if best else
             '<span class="gk-from">No store has it in stock right now</span>'))
    official = (f'<div class="gk-row gk-official"><div class="gk-store"><b>{e(off_name)}</b><small>Official store</small>'
                f'<span class="gk-pn">Face value, no third-party seller</span></div><div class="gk-price"><strong>{money(face)}</strong></div>'
                f'<a class="gk-buy alt" href="{e(off_url)}" target="_blank" rel="noopener">Official &#8599;</a></div>')
    return f'<details class="gk-card" id="{card}-{face}"{" open" if face in (50, 100) else ""}><summary>{head}</summary>{rows}{official}</details>'


CSS = """<style>
.gk-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 8px}
.gk-tab{padding:10px 16px;border-radius:10px;border:1px solid #3A2C7A;background:#261B5C;color:#fff;font:600 15px Inter,system-ui,sans-serif;cursor:pointer}
.gk-tab[aria-selected="true"]{background:#FF7A1A;border-color:#FF7A1A;color:#140D33}
.gk-panel[hidden]{display:none}.gk-panel>p{color:#CFC8F0}
.gk-card{background:#140D33;border:1px solid #2C2160;border-radius:14px;margin:10px 0;overflow:hidden}
.gk-card summary{display:flex;align-items:center;gap:14px;padding:14px 16px;cursor:pointer;list-style:none}
.gk-card summary::-webkit-details-marker{display:none}
.gk-face{font:700 22px "Space Grotesk",Inter,sans-serif;background:#261B5C;border-radius:10px;padding:6px 12px}
.gk-from{color:#CFC8F0}.gk-from b{color:#7CF0A8;font-size:18px}
.gk-row{display:grid;grid-template-columns:1fr auto auto;gap:14px;align-items:center;padding:12px 16px;border-top:1px solid #2C2160}
.gk-store{display:flex;flex-direction:column;gap:2px;min-width:0}.gk-store small{color:#8FB4E3}
.gk-pn{color:#CFC8F0;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.gk-up{color:#8A82B5;font-size:12px}
.gk-price{text-align:right;display:flex;flex-direction:column;gap:4px;align-items:flex-end}.gk-price strong{font:700 20px "Space Grotesk",Inter,sans-serif}
.gk-best{background:#1C7CF0;color:#fff;font-size:12px;padding:2px 6px;border-radius:4px;margin-right:4px}
.gk-off{background:#E0303A;color:#fff;font-size:12px;padding:2px 6px;border-radius:4px}
.gk-over{color:#FFB0B0;font-size:12px}
.gk-buy{background:#5B4CF5;color:#fff;font-weight:700;padding:12px 18px;border-radius:8px;text-decoration:none;white-space:nowrap}
.gk-buy.alt{background:#261B5C;border:1px solid #3A2C7A}.gk-official{background:#0F0A24}
.gk-promo{background:#1B1245;border:1px solid #FF7A1A;border-radius:12px;padding:12px 16px;margin:12px 0}
.gc-hl{color:#FF8A1A}
@media (max-width:640px){.gk-row{grid-template-columns:1fr auto}.gk-buy{grid-column:1/-1;text-align:center}}
</style>"""

JS = """<script>
(function(){
 var tabs=document.querySelectorAll('.gk-tab');
 function show(id){tabs.forEach(function(t){t.setAttribute('aria-selected',t.dataset.p===id)});
  document.querySelectorAll('.gk-panel').forEach(function(p){p.hidden=p.id!=='p-'+id})}
 tabs.forEach(function(t){t.addEventListener('click',function(){show(t.dataset.p);history.replaceState(null,'','#'+t.dataset.p)})});
 var h=(location.hash||'').slice(1).split('-')[0];if(h&&document.getElementById('p-'+h))show(h);
 document.addEventListener('click',function(ev){var a=ev.target.closest('.gk-buy');if(!a||!a.dataset.gk||!window.goatcounter||!goatcounter.count)return;
  goatcounter.count({path:'giftcard-click-'+a.dataset.gk,event:true})});
})();
</script>"""


def build():
    d = json.load(open(DATA))
    stores = d.get("stores", {})
    today = date.today().isoformat()
    promos = "".join(f'<p class="gk-promo fine">{p["html"]}</p>' for p in PROMOS if p["until"] >= today)
    order = ["psn", "xbox", "nintendo", "steam", "roblox"]
    live = [c for c in order if any(d["cards"].get(c, {}).get("faces", {}).values())]
    tabs = "".join(f'<button class="gk-tab" role="tab" data-p="{c}" aria-selected="{str(i == 0).lower()}">{e(d["cards"][c]["name"])}</button>'
                   for i, c in enumerate(live))
    panels = ""
    for i, c in enumerate(live):
        faces = d["cards"][c]["faces"]
        blocks = "".join(face_block(c, int(f), offs, stores) for f, offs in faces.items() if offs)
        panels += (f'<section class="gk-panel" id="p-{c}" role="tabpanel"{"" if i == 0 else " hidden"}><h2>{e(d["cards"][c]["name"])} gift cards (US)</h2>'
                   f'<p>{e(BLURB[c])}</p>{blocks}</section>')
    body = f"""<main id="main"><div class="wrap">
<section class="hero">
<p class="crumbs"><a href="/">Home</a> / <a href="/gifts/">Gifts</a> / Gift cards</p>
<p class="eyebrow">Live gift card price comparison</p>
<h1>Cheapest gaming gift cards, compared live</h1>
<p class="lede">PlayStation, Xbox, Nintendo, Steam and Roblox cards for US accounts, compared across {len(stores)} stores and the official store. Prices refresh every few hours from each store's own product feed (last refresh {e(ago(d.get("updated", "")))}).</p>
{promos}
</section>
<div class="gk-tabs" role="tablist" aria-label="Gift card brand">{tabs}</div>
{panels}
<section class="block" id="tips">
<h2>Before you buy a gift card code</h2>
<ul class="gc-tips fine">
<li>Check the region. A US card only works on a US account.</li>
<li>Prices marked &asymp; were converted to dollars from the store's feed. Stores can add a payment or service fee at checkout, so compare the final total with the face value. If it's higher, buy from the official store instead.</li>
<li>Kinguin is a marketplace: pick a seller with lots of good ratings, and redeem the code as soon as it arrives.</li>
<li>Skip the add-ons at checkout unless you want them. They raise the price.</li>
</ul>
<p class="fine">We earn a commission when you buy through these links, at no extra cost to you. SteelGames isn't affiliated with Sony, Microsoft, Nintendo, Valve or Roblox.</p>
</section>
</div></main>
"""
    page = (layout.head("Cheapest PlayStation, Xbox, Nintendo, Steam and Roblox gift cards (US), compared live | SteelGames",
                        "Compare live prices for US PlayStation, Xbox, Nintendo eShop, Steam and Roblox gift cards across trusted stores.",
                        layout.SITE + "/gift-cards/", CSS) + layout.header("gifts") + body + JS + layout.footer())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(page)
    print(f"wrote {OUT}: {sum(len(o) for c in d['cards'].values() for o in c['faces'].values())} offers")


if __name__ == "__main__":
    build()
