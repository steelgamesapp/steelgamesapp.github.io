"""Shop sections for gear.html: JLab, brand-partner products, extra Amazon picks, search and filters.

Data lives in tools/gear_shop.json. Run `python3 tools/gear_shop.py` and the new sections are inserted into
gear.html between <!--shop:...--> markers, so running it again refreshes them instead of duplicating them.

Links:
- Amazon items: https://www.amazon.com/dp/<ASIN>?tag=<tag>, photo from Amazon's own Associates image link.
- Brand items: the brand's product page wrapped in that brand's affiliate link (a ref parameter, an Impact
  deep link with ?u=, or an Awin deep link with &ued=).
- JLab items go to Amazon until jlab.direct_template is filled in with the JLab tracking link, then to jlab.com.
Prices are only shown for brand stores and JLab list prices, never for Amazon, because Amazon prices change constantly.
"""
import html
import json
import os
import re
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "gear.html")
DATA = json.load(open(os.path.join(ROOT, "tools", "gear_shop.json"), encoding="utf-8"))
TAG = DATA["amazon_tag"]
CDN = DATA["shopify_cdn"]
ASOF = DATA["asof"]

REL = 'target="_blank" rel="sponsored nofollow noopener"'
ARROW = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>')
# If a photo ever fails to load, show a drawing of that kind of gear instead of an empty box.
ICON_RULES = [("quest", "vr"), ("vr headset", "vr"), ("keyboard", "keyboard"), ("mouse", "mouse"), ("headset", "headset"), ("headphone", "headset"), ("earbud", "headset"),
              ("buds", "headset"), ("speaker", "speaker"), ("monitor", "monitor"), ("oled", "monitor"), ("case", "case"),
              ("cooler", "power"), ("power supply", "power"), ("rm850", "power"), ("router", "network"), ("switch", "network"),
              ("ethernet", "network"), ("cable", "network"), ("key light", "light"), ("light", "light"), ("mic", "mic"),
              ("vr", "vr"), ("chair", "chair"), ("desk", "chair"), ("dock", "plug"), ("charger", "plug"),
              ("nano", "plug"), ("pc", "gpu"), ("gaming", "controller")]


def icon_for(name):
    low = (name or "").lower()
    for key, icon in ICON_RULES:
        if key in low:
            return icon
    return "controller"


def esc(t):
    return html.escape(str(t if t is not None else ""), quote=True)


def money(v):
    return "${:,.2f}".format(float(v))


# ---------------------------------------------------------------- links and photos
def amazon_url(asin):
    return f"https://www.amazon.com/dp/{asin}?tag={TAG}"


def amazon_img(asin):
    """Amazon's product photo by ASIN (500px). Checked one by one: ASINs with no photo return a 1px gif."""
    return f"https://m.media-amazon.com/images/P/{asin}.01._SCLZZZZZZZ_.jpg"


def amazon_alt(asin):
    """Second try if the first photo fails: the same Amazon photo service on its older image host.
    (The Associates widget host ws-na.amazon-adsystem.com no longer exists, so it must not be used.)"""
    return f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg"


def brand_url(brand, handle):
    b = DATA["brands"][brand]
    page = b["product_url"].replace("{handle}", handle)
    link = b["link"]
    if link["type"] == "append":
        return page + ("&" if "?" in page else "?") + link["param"]
    if link["type"] == "impact":
        return link["base"] + "?u=" + quote(page, safe="")
    if link["type"] == "awin":
        return link["base"] + "&ued=" + quote(page, safe="")
    raise ValueError(link)


def shopify_img(path, width=520):
    return f"{CDN}{path}?width={width}"


# ---------------------------------------------------------------- card markup
def chips_html(chips, top=False):
    s = "".join(f'<span class="chip p-{c}">{esc(l)}</span>' for c, l in chips)
    if top:
        s += '<span class="chip p-top">★ Top rated</span>'
    return f'<div class="item-top"><span class="chips">{s}</span></div>'


def photo_attrs(name, alt_img=None):
    """Lazy-loaded photo that falls back to a second photo, then to a drawing of that kind of gear (see sgFix)."""
    alt = f' data-alt="{esc(alt_img)}"' if alt_img else ""
    return (f'loading="lazy" decoding="async" width="400" height="300" data-icon="{icon_for(name)}"{alt} '
            'onerror="sgFix(this)" onload="sgChk(this)"')


def card(url, img, name, blurb, chips, label, top=False, price=None, price_note="", src="amazon", brand=None, price_from=False, alt_img=None):
    attrs = f' data-src="{src}"' + (f' data-brand="{esc(brand)}"' if brand else "")
    price_html = ""
    if price:
        lead = "<span>From</span>" if price_from else ""
        price_html = f'\n          <div class="price">{lead}<b>{money(price)}</b><span>{esc(price_note)}</span></div>'
    return (f'        <article class="item"{attrs}>\n'
            f'          <a class="thumb" href="{esc(url)}" {REL} tabindex="-1" aria-hidden="true"><img src="{esc(img)}" alt="{esc(name)}" '
            f'{photo_attrs(name, alt_img)}></a>\n'
            f'          {chips_html(chips, top)}\n'
            f'          <h4>{esc(name)}</h4>\n'
            f'          <p>{esc(blurb)}</p>{price_html}\n'
            f'          <a class="buy" href="{esc(url)}" {REL}>{esc(label)}{ARROW}</a>\n'
            f'        </article>')


def amazon_card(it, brand=None, price=None, price_note=""):
    return card(amazon_url(it["asin"]), amazon_img(it["asin"]), it["name"], it["blurb"], it["chips"],
                "See price on Amazon", top=it.get("top", False), price=price, price_note=price_note, src="amazon", brand=brand,
                alt_img=amazon_alt(it["asin"]))


def jlab_img(it):
    """JLab's own product photo from its store, falling back to the Amazon image if no photo is listed."""
    return shopify_img(it["img"]) if it.get("img") else amazon_img(it["asin"])


def jlab_card(it):
    tpl = DATA["jlab"].get("direct_template", "").strip()
    if tpl:
        page = DATA["jlab"]["product_url"].replace("{handle}", it["handle"])
        url = tpl.replace("{url}", quote(page, safe=""))
        return card(url, jlab_img(it), it["name"], it["blurb"], it["chips"], "Shop at JLab",
                    top=it.get("top", False), price=it["price"], price_note="at JLab", src="brand", brand="JLab")
    return card(amazon_url(it["asin"]), jlab_img(it), it["name"], it["blurb"], it["chips"], "See price on Amazon",
                top=it.get("top", False), price=it["price"], price_note="JLab list price", src="amazon", brand="JLab")


def brand_card(brand, it):
    return card(brand_url(brand, it["handle"]), shopify_img(it["img"]), it["name"], it["blurb"], it["chips"],
                f"Shop at {brand}", price=it["price"], price_note=f"at {brand}", src="brand", brand=brand, price_from=bool(it.get("from")))


def cat_html(title, items_html):
    return (f'      <div class="cat">\n        <h3>{esc(title)}</h3>\n        <div class="items">\n{items_html}\n        </div>\n      </div>')


def group_html(gid, title, intro, cats):
    return (f'<!--shop:{gid}-->\n  <section class="group" id="{gid}" aria-labelledby="{gid}-h">\n    <div class="wrap">\n'
            f'      <div class="group-head">\n        <h2 id="{gid}-h">{esc(title)}</h2>\n        <p>{esc(intro)}</p>\n      </div>\n'
            + "\n".join(cats) + f'\n    </div>\n  </section>\n<!--/shop:{gid}-->')


# ---------------------------------------------------------------- html surgery
def strip_markers(h):
    h = re.sub(r"\n?[ \t]*<!--shop:([\w:.\- ]+)-->.*?<!--/shop:\1-->[ \t]*\n?", "\n", h, flags=re.S)
    h = re.sub(r'<a class="thumb[^"]*" data-shop="1"[^>]*>.*?</a>\n\s*', "", h, flags=re.S)
    return h


def section_span(h, gid):
    m = re.search(r'<section class="group" id="%s"' % re.escape(gid), h)
    if not m:
        raise SystemExit(f"group {gid} not found")
    end = h.index("</section>", m.start()) + len("</section>")
    return m.start(), end


def matching_div_end(h, start):
    """Index just after the </div> that closes the <div ...> opening at `start`."""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", h[start:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return start + m.end()
    raise SystemExit("unbalanced div")


def cat_span(h, gid, title):
    s, e = section_span(h, gid)
    m = re.search(r'<div class="cat">\s*<h3>%s</h3>' % re.escape(title), h[s:e])
    if not m:
        raise SystemExit(f"category {title!r} not found in {gid}")
    a = s + m.start()
    return a, matching_div_end(h, a)


def insert_after_section(h, gid, block):
    _, e = section_span(h, gid)
    return h[:e] + "\n\n" + block + h[e:]


def insert_before_section(h, gid, block):
    s, _ = section_span(h, gid)
    return h[:s] + block + "\n\n  " + h[s:]


# ---------------------------------------------------------------- page-level pieces
CSS = """
/* shop additions: price line, search and filters */
.item[hidden], .cat[hidden], .group[hidden] { display: none; }
.price { display: flex; align-items: baseline; flex-wrap: wrap; gap: 2px 8px; }
.price b { font-family: var(--display); font-size: 22px; font-weight: 700; letter-spacing: -0.2px; }
.price span { font-size: 13px; color: var(--muted); }
/* keep the whole product photo inside the 4:3 picture box instead of letting a square photo spill out and get cut off */
.thumb { grid-template: minmax(0, 1fr) / minmax(0, 1fr); }
.thumb img { max-width: 100%; max-height: 100%; }
.thumb.icon { background: #1E1450; }
.thumb.icon img { padding: 0; object-fit: cover; }
.shopbar .wrap { padding-block: 22px 0; display: flex; flex-wrap: wrap; gap: 12px 16px; align-items: center; }
.sq { flex: 1 1 320px; display: flex; align-items: center; gap: 10px; padding: 0 14px; min-height: 48px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line-strong); color: var(--steel); }
.sq:focus-within { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(255,176,32,.35); }
.sq input { flex: 1; min-width: 0; background: none; border: 0; color: var(--fg); font: inherit; font-size: 16px; outline: 0; padding: 12px 0; }
.sq input::placeholder { color: var(--muted); }
.fchips { display: flex; gap: 8px; flex-wrap: wrap; }
.fchip { font: inherit; font-size: 14px; font-weight: 600; padding: 0 14px; min-height: 42px; border-radius: 999px; border: 1px solid var(--line-strong); background: var(--surface); color: var(--steel); cursor: pointer; }
.fchip:hover { color: var(--fg); background: var(--raised); }
.fchip[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
.fchip:focus-visible, .sq input:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.scount { margin: 0; flex-basis: 100%; font-size: 14px; color: var(--muted); }
.shop-empty { margin: 0; padding: 40px 0; text-align: center; color: var(--steel); }
"""

JS = """
(function () {
  var q = document.getElementById('shop-q'); if (!q) return;
  var items = [].slice.call(document.querySelectorAll('.item'));
  var chips = [].slice.call(document.querySelectorAll('.fchip'));
  var count = document.getElementById('shop-count'), empty = document.getElementById('shop-empty'), mode = 'all';
  items.forEach(function (el) {
    if (!el.dataset.src) { var a = el.querySelector('a.buy'); el.dataset.src = a && /amazon\\.com/.test(a.href) ? 'amazon' : 'brand'; }
    el.dataset.t = el.textContent.toLowerCase().replace(/\\s+/g, ' ');
  });
  function run() {
    var words = q.value.trim().toLowerCase().split(/\\s+/).filter(Boolean), shown = 0;
    items.forEach(function (el) {
      var ok = mode === 'all' || (mode === 'jlab' ? el.dataset.brand === 'JLab' : el.dataset.src === mode);
      for (var i = 0; ok && i < words.length; i++) if (el.dataset.t.indexOf(words[i]) < 0) ok = false;
      el.hidden = !ok; if (ok) shown++;
    });
    [].forEach.call(document.querySelectorAll('.cat'), function (c) { c.hidden = !c.querySelector('.item:not([hidden])'); });
    [].forEach.call(document.querySelectorAll('.group'), function (g) { g.hidden = !g.querySelector('.item:not([hidden])'); });
    var filtering = mode !== 'all' || words.length > 0;
    count.textContent = filtering ? shown + (shown === 1 ? ' product' : ' products') + ' shown' : '';
    empty.hidden = shown > 0;
  }
  q.addEventListener('input', run);
  chips.forEach(function (b) { b.addEventListener('click', function () {
    mode = b.dataset.mode; chips.forEach(function (c) { c.setAttribute('aria-pressed', c === b ? 'true' : 'false'); }); run();
  }); });
})();
"""

SEARCH_ICON = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>')

SGFIX = "function sgFix(i){var a=i.getAttribute('data-alt');if(a&&!i.dataset.t){i.dataset.t=1;i.src=a;return}i.onerror=i.onload=null;i.src='/assets/gear-icons/'+i.dataset.icon+'.svg';i.closest('.thumb').classList.add('icon')}function sgChk(i){if(i.naturalWidth<40)sgFix(i)}"

BAR = f"""<!--shop:bar-->
  <script>{SGFIX}</script>
  <section class="shopbar" aria-label="Search the gear guide">
    <div class="wrap">
      <label class="sq">{SEARCH_ICON}<input id="shop-q" type="search" placeholder="Search gear, like headset or JLab" autocomplete="off" aria-label="Search gear"></label>
      <div class="fchips" role="group" aria-label="Filter products">
        <button type="button" class="fchip" data-mode="all" aria-pressed="true">All</button>
        <button type="button" class="fchip" data-mode="jlab" aria-pressed="false">JLab</button>
        <button type="button" class="fchip" data-mode="brand" aria-pressed="false">Brand stores</button>
        <button type="button" class="fchip" data-mode="amazon" aria-pressed="false">Amazon picks</button>
      </div>
      <p class="scount" id="shop-count" aria-live="polite"></p>
    </div>
  </section>
<!--/shop:bar-->"""

EMPTY = '<!--shop:empty--><p class="shop-empty wrap" id="shop-empty" hidden>No gear matches that search. Try a shorter word, like "mouse" or "chair".</p><!--/shop:empty-->'

NAV = [("deals", "Black Friday deals"), ("jlab", "JLab"), ("brand-shop", "Brand picks"), ("brand-stores", "Brand stores"),
       ("pc-parts", "PC parts"), ("desk-setup", "Desk setup"), ("streaming", "Streaming and audio"),
       ("console", "Console accessories"), ("portable-vr", "VR and handheld")]


def build(h):
    h = strip_markers(h)

    # --- JLab group (after deals) and brand picks group (after JLab)
    jl_cats = [cat_html(c["title"], "\n".join(jlab_card(i) for i in c["items"])) for c in DATA["jlab_cats"]]
    jl = group_html("jlab", "JLab Audio and gaming gear",
                    "JLab makes headsets, keyboards, mice, headphones and speakers at everyday prices. These are the pieces we would "
                    f"look at first. Prices shown are JLab's own list prices as of {ASOF}; check the store for today's price.", jl_cats)
    h = insert_after_section(h, "deals", jl)

    br_cats = [cat_html(c["title"], "\n".join(brand_card(c["brand"], i) for i in c["items"])) for c in DATA["brand_cats"]]
    br = group_html("brand-shop", "Brand picks you can shop now",
                    "Products from the brands we partner with, linked straight to each brand's own store. "
                    f"Prices are what each store listed on {ASOF} and can change, so check the final price at checkout.", br_cats)
    h = insert_after_section(h, "jlab", br)

    # --- new categories inside existing groups (kept in order), and appended cards
    for c in DATA["amazon_new_cats"]:
        block = f'<!--shop:cat:{c["group"]}:{c["title"]}-->\n' + cat_html(c["title"], "\n".join(amazon_card(i) for i in c["items"])) + \
                f'\n<!--/shop:cat:{c["group"]}:{c["title"]}-->'
        _, end = cat_span(h, c["group"], c["after"])
        h = h[:end] + "\n" + block + h[end:]
    for a in DATA["amazon_appends"]:
        s, e = cat_span(h, a["group"], a["cat"])
        items_open = h.index('<div class="items">', s)
        close = matching_div_end(h, items_open) - len("</div>")
        key = f'append:{a["group"]}:{a["cat"]}'
        block = f'<!--shop:{key}-->\n' + "\n".join(amazon_card(i) for i in a["items"]) + f'\n<!--/shop:{key}-->\n        '
        h = h[:close] + block + h[close:]

    # --- new groups (VR and handheld)
    for g in DATA["new_groups"]:
        cats = [cat_html(c["title"], "\n".join(amazon_card(i) for i in c["items"])) for c in g["cats"]]
        h = insert_after_section(h, g["after"], group_html(g["id"], g["title"], g["intro"], cats))

    # --- pictures for cards that had none
    for title, t in DATA["thumbs"].items():
        m = re.search(r'<article class="item">(?:(?!</article>).)*?<h4>%s</h4>.*?</article>' % re.escape(html.escape(title, quote=False)), h, re.S)
        if not m:
            m = re.search(r'<article class="item">(?:(?!</article>).)*?<h4>%s</h4>.*?</article>' % re.escape(title), h, re.S)
        if not m or "<img" in m.group(0):
            continue
        href = re.search(r'class="buy" href="([^"]+)"', m.group(0)).group(1)
        if "icon" in t:
            thumb = (f'<a class="thumb icon" data-shop="1" href="{href}" {REL} tabindex="-1" aria-hidden="true"><img src="/assets/gear-icons/{t["icon"]}.svg" '
                     f'alt="{esc(t["alt"])}" loading="lazy" decoding="async" width="400" height="300"></a>\n          ')
        else:
            thumb = (f'<a class="thumb" data-shop="1" href="{href}" {REL} tabindex="-1" aria-hidden="true"><img src="{esc(shopify_img(t["img"]))}" '
                     f'alt="{esc(t["alt"])}" {photo_attrs(t["alt"] + " " + title)}></a>\n          ')
        card_html = m.group(0).replace('<article class="item">\n          ', '<article class="item">\n          ' + thumb, 1)
        h = h[:m.start()] + card_html + h[m.end():]

    # --- search bar, nav, css, js
    nav = ('<nav class="jump" aria-label="Gear groups">\n    <div class="wrap">\n' +
           "\n".join(f'      <a href="#{i}">{esc(t)}</a>' for i, t in NAV) + '\n    </div>\n  </nav>')
    h = re.sub(r'<nav class="jump".*?</nav>', lambda _: nav + "\n\n  " + BAR, h, count=1, flags=re.S)
    h = h.replace("</main>", EMPTY + "\n</main>", 1)
    h = re.sub(r"\n/\* shop additions.*?(?=\n</style>)", "", h, flags=re.S)
    h = h.replace("</style>", CSS.rstrip("\n") + "\n</style>", 1)
    h = re.sub(r"<script>\n\(function \(\) \{\n  var q = document.getElementById\('shop-q'\).*?</script>\n", "", h, flags=re.S)
    h = h.replace("</body>", "<script>" + JS + "</script>\n</body>", 1)

    # --- intro copy
    deals_s, deals_e = section_span(h, "deals")
    total = len(re.findall(r'<article class="item"', h)) - len(re.findall(r'<article class="item"', h[deals_s:deals_e]))
    lede = (f'{total} products for PC parts, desk setups, streaming, audio and console accessories: JLab, the brands we partner with, '
            'and our top Amazon picks. Items marked ★ Top rated had 4.4 stars or better from at least 1,500 Amazon buyers when we picked them. '
            'Tap any button to see today\'s price and reviews before you buy.')
    h = re.sub(r'(<h1>Gear for your whole setup</h1>\s*<p class="lede">).*?(</p>)', lambda m: m.group(1) + lede + m.group(2), h, count=1, flags=re.S)
    h = re.sub(r'<strong>How we make money:</strong>.*?</p>',
               "<strong>How we make money:</strong> As an Amazon Associate and a partner of the brands featured here, SteelGames earns from qualifying purchases. "
               "Every button on this page is an affiliate link, and it costs you nothing extra. These are picks we chose. The only paid placement is the box marked Sponsored, if there is one.</p>",
               h, count=1, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")',
               r"\1SteelGames gear guide: JLab audio and gaming gear, brand-partner picks and top Amazon finds for PC parts, desk setups, streaming and console accessories, with every commission link clearly labeled.\2",
               h, count=1)
    h = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", h)  # keep re-runs from piling up blank lines
    return h, total


ICONS = {
    "vpn": '<path d="M32 8 12 16v14c0 12 8.5 21 20 26 11.5-5 20-14 20-26V16z"/><path d="m23 32 6 6 12-13"/>',
    "password": '<rect x="14" y="28" width="36" height="26" rx="4"/><path d="M22 28v-7a10 10 0 0 1 20 0v7"/><circle cx="32" cy="41" r="3"/><path d="M32 44v5"/>',
    "case": '<rect x="18" y="8" width="28" height="48" rx="3"/><path d="M24 16h16M24 22h16"/><circle cx="32" cy="42" r="6"/>',
    "power": '<path d="M36 8 20 34h12l-4 22 16-26H32z"/>',
    "network": '<path d="M10 28a30 30 0 0 1 44 0M17 36a20 20 0 0 1 30 0M24 44a10 10 0 0 1 16 0"/><circle cx="32" cy="52" r="2"/>',
    "plug": '<path d="M24 8v12M40 8v12M18 20h28v10a14 14 0 0 1-28 0zM32 44v12"/>',
    "keys": '<circle cx="22" cy="32" r="10"/><circle cx="22" cy="32" r="3"/><path d="M32 32h24M48 32v8M56 32v6"/>',
}


def write_icons():
    d = os.path.join(ROOT, "assets", "gear-icons")
    os.makedirs(d, exist_ok=True)
    for name, body in ICONS.items():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="256" height="256" fill="none" stroke="#FF7A1A" '
               'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="0" y="0" width="64" height="64" fill="#1E1450" '
               f'stroke="none"/>{body}</svg>')
        open(os.path.join(d, name + ".svg"), "w").write(svg)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else PAGE
    src = open(PAGE, encoding="utf-8").read()
    new, total = build(src)
    write_icons()
    open(out, "w", encoding="utf-8").write(new)
    print(f"wrote {out}: {total} products on the page, {len(new):,} bytes")
