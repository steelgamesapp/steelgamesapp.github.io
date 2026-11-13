"""Gift Cards and Game Currency page (/gift-cards/). DRAFT: noindex, not in the sitemap, not in the site menu.

Run `python3 tools/currency_page.py` to rebuild gift-cards/index.html.

- Cards link to Eneba's US product pages. When the Eneba tracking template is pasted into tools/affiliates.json
  (key "Eneba", with {url} where the page address goes), every Eneba link becomes a tracked link on the next run.
- No prices are printed: resale prices change hourly and some cards sell above face value, so each card tells the
  reader to compare Eneba's price with the face value before buying.
- Steam and Fortnite V-Bucks were above face value on Eneba when checked (Nov 13, 2026), so the page sends readers
  to buy those directly instead of listing them.
"""
import html
import json
import os
from urllib.parse import quote

import layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "gift-cards")
URL = layout.SITE + "/gift-cards/"
ENEBA = "https://www.eneba.com/"

# (section id, title, intro, [(card name, face value in USD, eneba product slug, works with)])
SECTIONS = [
    ("playstation", "PlayStation Store", "Adds money to a US PlayStation account, for games, add-ons, PS Plus and in-game currency on PS4 and PS5.",
     [("PlayStation Store $10", 10, "psn-playstation-network-card-10-usd-usa-psn-key-united-states"),
      ("PlayStation Store $40", 40, "psn-playstation-network-card-40-usd-usa-psn-key-united-states"),
      ("PlayStation Store $50", 50, "psn-playstation-network-card-50-usd-usa-psn-key-united-states")]),
    ("xbox", "Xbox", "Adds money to an Xbox account for games, Game Pass, and currency like V-Bucks, COD Points and Minecoins.",
     [("Xbox $50", 50, "xbox-xbox-live-50-usd-xbox-live-key-north-america")]),
]

KINGUIN_STEEL4 = ('<p class="fine gc-code" data-until="2026-11-26"><b>Kinguin reader code:</b> use <b class="gc-hl">STEEL4</b> for 4% off everything in '
                  '<a href="https://kinguin.sjv.io/c/8059330/3827272/50048?subId1=site-giftcards-steel4&amp;u=https%3A%2F%2Fwww.kinguin.net%2Fcampaign%2Fprepaids&amp;partnerpropertyid=9076396" '
                  'target="_blank" rel="sponsored nofollow noopener">Kinguin\'s Prepaid category</a>, Nov 12 to Nov 26. Carts up to &euro;150, two uses per person.</p>')

CSS = """<style>
.gc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.gc-card{display:flex;flex-direction:column;gap:8px;padding:16px;border-radius:14px;background:var(--surface);border:1px solid var(--line-strong);color:#fff;text-decoration:none}
.gc-card:hover{background:var(--raised)}
.gc-card b{font:700 18px var(--display)}
.gc-card .gc-face{color:var(--muted);font-size:14px}
.gc-card .gc-go{margin-top:auto;font-weight:700;color:var(--accent)}
.gc-code{border:1px dashed var(--accent);border-radius:10px;padding:10px 14px;color:#fff}
.gc-hl{color:var(--accent);letter-spacing:1px}
.gc-tips li{margin:6px 0}
</style>
"""

HIDE_ENDED = '<script>document.querySelectorAll("[data-until]").forEach(function(e){if(Date.now()>Date.parse(e.dataset.until+"T23:59:59-06:00"))e.remove()});</script>'


def esc(t):
    return html.escape(str(t), quote=True)


def eneba_template():
    """The Eneba tracking template from affiliates.json, or None until the program approves us."""
    try:
        with open(os.path.join(ROOT, "tools", "affiliates.json")) as f:
            v = json.load(f).get("Eneba", "")
    except (OSError, ValueError):
        return None
    v = (v or "").strip()
    return v if v.startswith("https://") and "{url}" in v else None


def link(slug, tpl):
    page = ENEBA + slug
    return tpl.replace("{url}", quote(page, safe="")) if tpl else page


def card(name, face, slug, tpl):
    return (f'<a class="gc-card" href="{esc(link(slug, tpl))}" target="_blank" rel="sponsored nofollow noopener">'
            f'<b>{esc(name)}</b><span class="gc-face">US account. Face value ${face}. Compare Eneba\'s price with ${face} before you buy.</span>'
            f'<span class="gc-go">See today\'s price on Eneba</span></a>')


def build():
    tpl = eneba_template()
    title = "Gift Cards and Game Currency for US Accounts | SteelGames"
    desc = "PlayStation and Xbox gift cards for US accounts, plus where to buy Steam Wallet and Fortnite V-Bucks for the best price."
    out = [layout.head(title, desc, URL, extra='<meta name="robots" content="noindex, nofollow">\n' + CSS), layout.header("gifts")]
    out.append(f"""<main id="main">
<section class="hero"><div class="wrap">
  <p class="crumbs"><a href="/">Home</a> / <a href="/gifts/">Gifts</a> / Gift cards</p>
  <p class="eyebrow">Gift cards and game currency</p>
  <h1>Gift cards for US gaming accounts</h1>
  <p class="lede">Digital codes for PlayStation and Xbox, sold by sellers on Eneba's marketplace. Every card here works on a US account. Resale prices change all day and are sometimes above face value, so check the price against the face value before you check out.</p>
  {KINGUIN_STEEL4}
</div></section>""")
    for sid, h2, intro, cards in SECTIONS:
        out.append(f"""<section class="block" id="{sid}"><div class="wrap">
  <h2>{esc(h2)}</h2>
  <p class="fine">{esc(intro)}</p>
  <div class="gc-grid">{''.join(card(n, f, s, tpl) for n, f, s in cards)}</div>
</div></section>""")
    out.append("""<section class="block" id="direct"><div class="wrap">
  <h2>Steam Wallet and Fortnite V-Bucks</h2>
  <p class="fine">When we checked resale sites, Steam Wallet cards and V-Bucks cost more than buying them directly, so we don't list them. Add Steam Wallet funds in the Steam app or buy a card at a store near you, and buy V-Bucks inside Fortnite. If you buy V-Bucks on Xbox or PlayStation, an Xbox or PlayStation Store card above pays for them.</p>
</div></section>
<section class="block" id="tips"><div class="wrap">
  <h2>Before you buy a gift card code</h2>
  <ul class="gc-tips fine">
    <li>Check the region. A US card only works on a US account.</li>
    <li>Compare the price with the face value. If it's higher, buy from the console's own store instead.</li>
    <li>Pick a seller with lots of good ratings, and redeem the code as soon as it arrives.</li>
    <li>Skip the add-ons at checkout unless you want them. They raise the price.</li>
  </ul>
  <p class="fine">We earn a commission if you buy through these links, at no extra cost to you. SteelGames isn't affiliated with Sony, Microsoft, Valve or Epic Games.</p>
</div></section>
</main>
""")
    out.append(layout.footer().replace("</body>", HIDE_ENDED + "\n</body>"))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write("".join(out))
    print("wrote gift-cards/index.html", "(tracked Eneba links)" if tpl else "(plain Eneba links until the template is set)")


if __name__ == "__main__":
    build()
