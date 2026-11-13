"""Gift Cards and Game Currency page (/gift-cards/). DRAFT: noindex, not in the sitemap, not in the site menu.

Run `python3 tools/currency_page.py` to rebuild gift-cards/index.html.

- Cards link to Kinguin search results for US cards, through SteelGames' Kinguin tracking link on Impact
  (kinguin.sjv.io, same link as the STEEL4 banner). Eneba declined SteelGames on Nov 13, 2026, so Eneba is out.
- No prices are printed: Kinguin seller prices change all day. When checked on Nov 13, 2026, small US cards
  ($1 to $55) sold at or above face value and bigger cards ($100 to $250) sold a little below it, so the page
  says so and tells readers to compare with the face value before they buy.
- Steam Wallet and Fortnite V-Bucks resale prices were above face value when checked, so the page sends readers
  to buy those directly instead of listing them.
"""
import html
import os
from urllib.parse import quote

import layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "gift-cards")
URL = layout.SITE + "/gift-cards/"
KINGUIN_TRACK = "https://kinguin.sjv.io/c/8059330/3827272/50048"
KINGUIN_PROP = "9076396"
SEARCH = "https://www.kinguin.net/listing?phrase="

# (section id, title, intro, [(card title, what it covers, kinguin search phrase, sub id)])
SECTIONS = [
    ("playstation", "PlayStation Store", "Adds money to a US PlayStation account, for games, add-ons, PS Plus and in-game currency on PS4 and PS5.",
     [("PlayStation Store cards, US", "Every US card value on Kinguin, from $1 to $500.", "PlayStation Network Card USD US", "psn")]),
    ("xbox", "Xbox", "Adds money to a US Xbox account for games, Game Pass, and currency like V-Bucks, COD Points and Minecoins.",
     [("Xbox gift cards, US", "Every US card value on Kinguin, from $1 to $250.", "XBOX Live Prepaid Card US", "xbox"),
      ("Game Pass cards, US", "Prepaid Game Pass time for a US account.", "XBOX Game Pass Subscription Card US", "gamepass")]),
]

STEEL4 = ('<p class="fine gc-code" data-until="2026-11-26"><b>Kinguin reader code:</b> use <b class="gc-hl">STEEL4</b> for 4% off everything in '
          '<a href="{href}" target="_blank" rel="sponsored nofollow noopener">Kinguin\'s Prepaid category</a>, '
          'Nov 12 to Nov 26. Carts up to &euro;150, two uses per person.</p>')

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


def kinguin(page, sub):
    return f"{KINGUIN_TRACK}?subId1=site-giftcards-{sub}&u={quote(page, safe='')}&partnerpropertyid={KINGUIN_PROP}"


def card(title, covers, phrase, sub):
    href = kinguin(SEARCH + quote(phrase), sub)
    return (f'<a class="gc-card" href="{esc(href)}" target="_blank" rel="sponsored nofollow noopener">'
            f'<b>{esc(title)}</b><span class="gc-face">{esc(covers)} Compare the price with the face value before you buy.</span>'
            f'<span class="gc-go">See today\'s prices on Kinguin</span></a>')


def build():
    title = "Gift Cards and Game Currency for US Accounts | SteelGames"
    desc = "PlayStation and Xbox gift cards and memberships for US accounts, plus where to buy Steam Wallet and Fortnite V-Bucks for the best price."
    steel4 = STEEL4.format(href=esc(kinguin("https://www.kinguin.net/campaign/prepaids", "steel4")))
    out = [layout.head(title, desc, URL, extra='<meta name="robots" content="noindex, nofollow">\n' + CSS), layout.header("gifts")]
    out.append(f"""<main id="main">
<section class="hero"><div class="wrap">
  <p class="crumbs"><a href="/">Home</a> / <a href="/gifts/">Gifts</a> / Gift cards</p>
  <p class="eyebrow">Gift cards and game currency</p>
  <h1>Gift cards for US gaming accounts</h1>
  <p class="lede">Digital PlayStation and Xbox codes from sellers on Kinguin's marketplace, all for US accounts. Prices change all day. The bigger cards ($100 and up) usually sell a little under face value, while small cards often cost more than face value, so check before you check out.</p>
  {steel4}
</div></section>""")
    for sid, h2, intro, cards in SECTIONS:
        out.append(f"""<section class="block" id="{sid}"><div class="wrap">
  <h2>{esc(h2)}</h2>
  <p class="fine">{esc(intro)}</p>
  <div class="gc-grid">{''.join(card(*c) for c in cards)}</div>
</div></section>""")
    out.append("""<section class="block" id="direct"><div class="wrap">
  <h2>Steam Wallet and Fortnite V-Bucks</h2>
  <p class="fine">When we checked resale sites, Steam Wallet cards and V-Bucks cost more than buying them directly, so we don't list them. Add Steam Wallet funds in the Steam app or buy a card at a store near you, and buy V-Bucks inside Fortnite. If you buy V-Bucks on Xbox or PlayStation, an Xbox or PlayStation card above pays for them.</p>
</div></section>
<section class="block" id="tips"><div class="wrap">
  <h2>Before you buy a gift card code</h2>
  <ul class="gc-tips fine">
    <li>Check the region. A US card only works on a US account.</li>
    <li>Compare the price at checkout, fees included, with the face value. If it's higher, buy from the console's own store instead.</li>
    <li>Pick a seller with lots of good ratings, and redeem the code as soon as it arrives.</li>
    <li>Skip the add-ons at checkout unless you want them. They raise the price.</li>
  </ul>
  <p class="fine">We earn a commission if you buy through these links, at no extra cost to you. SteelGames isn't affiliated with Sony or Microsoft.</p>
</div></section>
</main>
""")
    out.append(layout.footer().replace("</body>", HIDE_ENDED + "\n</body>"))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write("".join(out))
    print("wrote gift-cards/index.html (Kinguin links)")


if __name__ == "__main__":
    build()
