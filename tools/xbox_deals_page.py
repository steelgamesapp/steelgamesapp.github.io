"""Xbox Deals page (/xbox-deals/). DRAFT: noindex, not in the sitemap, not in the site menu.
Run `python3 tools/xbox_deals_page.py` to rebuild xbox-deals/index.html from data/xbox_deals.json.
- Deals come from a hand-checked snapshot of Xbox.com's US weekly deals list (data/xbox_deals.json).
  Each deal card shows the price we saw and the date we saw it, and links to the game's Xbox.com page.
- When the Microsoft affiliate template is pasted into tools/affiliates.json (key "Microsoft", with {url}
  where the page address goes), every Xbox.com link becomes a tracked link on the next run.
- The deal grid removes itself in the visitor's browser 7 days after the snapshot date, so a stale
  week never shows; the rest of the page stays.
"""
import datetime, html, json, os
from urllib.parse import quote

import layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "xbox-deals")
URL = layout.SITE + "/xbox-deals/"
STORE = "https://www.xbox.com/en-US/games/store/"
ALL_DEALS = "https://www.xbox.com/en-US/games/browse/DynamicChannel.GameDeals"
GP_DEALS = "https://www.xbox.com/en-US/xbox-game-pass/deals"

CSS = """<style>
.xd-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-top:14px}
.xd-card{display:flex;flex-direction:column;gap:6px;padding:14px;border:1px solid var(--line-strong);border-radius:12px;background:var(--raised);color:inherit;text-decoration:none}
.xd-card:hover{border-color:var(--accent)}
.xd-off{align-self:flex-start;font-weight:700;font-size:.8rem;padding:2px 8px;border-radius:999px;background:var(--accent);color:#fff}
.xd-name{font-weight:600;line-height:1.3}
.xd-plat{font-size:.8rem;color:var(--muted)}
.xd-price{display:flex;gap:8px;align-items:baseline}
.xd-price s{color:var(--muted);font-size:.9rem}
.xd-price b{font-size:1.15rem}
.xd-go{margin-top:auto;font-size:.85rem;color:var(--accent)}
.xd-links{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.xd-btn{display:inline-block;padding:10px 14px;border:1px solid var(--line-strong);border-radius:10px;color:inherit;text-decoration:none}
.xd-btn:hover{border-color:var(--accent)}
.xd-tips{margin:10px 0 0 18px}
</style>"""

HIDE_STALE = ('<script>document.querySelectorAll("[data-until]").forEach(function(e){'
              'if(new Date()>new Date(e.getAttribute("data-until")+"T23:59:59")){var n=document.getElementById("xd-stale");'
              'if(n)n.hidden=false;e.remove()}});</script>')


def esc(t):
    return html.escape(str(t), quote=True)


def ms_template():
    """The Microsoft tracking template from affiliates.json, or None until the program approves us."""
    try:
        with open(os.path.join(ROOT, "tools", "affiliates.json")) as f:
            v = json.load(f).get("Microsoft", "")
    except (OSError, ValueError):
        return None
    v = (v or "").strip()
    return v if v.startswith("https://") and "{url}" in v else None


def link(page, tpl):
    return tpl.replace("{url}", quote(page, safe="")) if tpl else page


def load():
    with open(os.path.join(ROOT, "data", "xbox_deals.json"), encoding="utf-8") as f:
        d = json.load(f)
    checked = datetime.date.fromisoformat(d["checked"])
    deals = sorted(d["deals"], key=lambda x: (-x["off"], x["now"]))
    return checked, deals


def card(x, tpl):
    plat = "Xbox and PC" if x.get("pc") else "Xbox"
    return (f'<a class="xd-card" href="{esc(link(STORE + x["path"], tpl))}" target="_blank" rel="sponsored nofollow noopener">'
            f'<span class="xd-off">{x["off"]}% off</span>'
            f'<span class="xd-name">{esc(x["name"])}</span>'
            f'<span class="xd-plat">{plat}</span>'
            f'<span class="xd-price"><s>${x["was"]:.2f}</s><b>${x["now"]:.2f}</b></span>'
            f'<span class="xd-go">See it on Xbox.com</span></a>')


def build():
    tpl = ms_template()
    checked, deals = load()
    until = (checked + datetime.timedelta(days=7)).isoformat()
    seen = f"{checked:%B} {checked.day}, {checked.year}"
    under10 = sum(1 for x in deals if x["now"] < 10)
    title = "Xbox Game Deals This Week | SteelGames"
    desc = f"This week's Xbox digital game sales, sorted by biggest discount: {len(deals)} games, {under10} under $10."
    out = [layout.head(title, desc, URL, extra='<meta name="robots" content="noindex, nofollow">\n' + CSS), layout.header("deals")]
    out.append(f"""<main id="main">
<section class="hero"><div class="wrap">
  <p class="crumbs"><a href="/">Home</a> / Xbox deals</p>
  <p class="eyebrow">Xbox Store sales</p>
  <h1>Xbox game deals this week</h1>
  <p class="lede">Every digital game on sale in the US Xbox Store this week, sorted by the biggest discount. Prices are what Xbox.com showed on {esc(seen)}. Sales end without warning, so check the price on Xbox.com before you buy.</p>
</div></section>
<section class="block" id="deals"><div class="wrap">
  <h2>On sale now: {len(deals)} games, {under10} under $10</h2>
  <p class="fine" id="xd-stale" hidden>This week's list has ended. We post the new one each week, and Xbox.com has every game on sale right now.</p>
  <div class="xd-grid" data-until="{until}">{''.join(card(x, tpl) for x in deals)}</div>
  <div class="xd-links">
    <a class="xd-btn" href="{esc(link(ALL_DEALS, tpl))}" target="_blank" rel="sponsored nofollow noopener">Every Xbox game on sale</a>
    <a class="xd-btn" href="{esc(link(GP_DEALS, tpl))}" target="_blank" rel="sponsored nofollow noopener">Extra deals for Game Pass members</a>
  </div>
</div></section>
<section class="block" id="tips"><div class="wrap">
  <h2>Getting the most from an Xbox sale</h2>
  <ul class="xd-tips fine">
    <li>Game Pass members often get an extra discount on top of the sale price, and some games on sale are already in Game Pass.</li>
    <li>"Xbox and PC" games come with Xbox Play Anywhere on many titles, so one purchase can cover both. Check the game's page to be sure.</li>
    <li>A discounted Xbox gift card stretches a sale further. See our <a href="/gift-cards/">gift card page</a>.</li>
    <li>Upgrades and premium editions are only worth it if you'll use the extra content.</li>
  </ul>
  <p class="fine">We may earn a commission if you buy through these links, at no extra cost to you. SteelGames isn't affiliated with Microsoft or Xbox.</p>
</div></section>
</main>
""")
    out.append(layout.footer().replace("</body>", HIDE_STALE + "\n</body>"))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write("".join(out))
    print(f"wrote xbox-deals/index.html with {len(deals)} deals, list hides after {until}",
          "(tracked Microsoft links)" if tpl else "(plain Xbox.com links until the template is set)")


if __name__ == "__main__":
    build()
