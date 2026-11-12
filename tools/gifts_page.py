"""Holiday gift shop page (/gifts/) built from the product cards on gear.html.

Every card, link, photo and price comes straight from gear.html, so the gift shop never shows a product, link or price
that the Gear page does not. Run `python3 tools/gifts_page.py` after gear.html changes (the daily SEO workflow runs it too).

Sections:
- Black Friday deals: the "deals" group of gear.html as it stands.
- Shop by budget: every card that shows a price (brand-store prices and JLab list prices), sorted by price.
- Shop by kind of gamer: the Amazon picks and brand stores (no prices, because Amazon prices change constantly).
- Gift a game and gift guides: links to our deal lists and buying guides.
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEAR = os.path.join(ROOT, "gear.html")
OUT_DIR = os.path.join(ROOT, "gifts")
URL = "https://steelgamesapp.com/gifts/"
BLACK_FRIDAY = "Black Friday is Friday, Nov 27 and Cyber Monday is Monday, Nov 30, 2026"

BUDGETS = [("under-25", "Stocking stuffers under $25", 0, 25),
           ("under-50", "Gifts from $25 to $50", 25, 50),
           ("under-100", "Gifts from $50 to $100", 50, 100),
           ("under-200", "Gifts from $100 to $200", 100, 200),
           ("big-gifts", "Big gifts, $200 and up", 200, 10 ** 9)]

# (section id, title, intro, [(gear group id, category title or None for all)])
KINDS = [
    ("pc-gamer", "For every PC gamer", "Keyboards, mice and headsets: the gear a PC gamer touches every day.",
     [("pc-parts", "Keyboards"), ("pc-parts", "Mice"), ("streaming", "Headsets")]),
    ("desk", "Desk setup upgrades", "Chairs, monitors, lighting, mousepads and desk gadgets that make a gaming corner nicer.",
     [("desk-setup", None)]),
    ("creator", "For streamers and creators", "Microphones, webcams, lights, stream decks, capture cards and speakers.",
     [("streaming", "Stream decks"), ("streaming", "Microphones"), ("streaming", "Lights and mic arms"), ("streaming", "Webcams"),
      ("streaming", "Speakers"), ("streaming", "Capture cards")]),
    ("console", "For console players", "Controllers, charging docks, cables, storage, cases and racing wheels.",
     [("console", None)]),
    ("builder", "For the PC builder", "Graphics cards, processors, memory, storage, cases, cooling and networking for an upgrade.",
     [("pc-parts", "Graphics cards"), ("pc-parts", "Processors"), ("pc-parts", "Memory"), ("pc-parts", "Storage"),
      ("pc-parts", "PC cases"), ("pc-parts", "Cooling and power"), ("pc-parts", "Networking")]),
    ("vr", "VR and handheld", "Headsets for PC VR.", [("portable-vr", None)]),
    ("stores", "Shop a whole brand store", "Let them pick: these go to each brand's own store.", [("brand-stores", None)]),
]

JUMP = {"pc-gamer": "PC gamers", "desk": "Desk setup", "creator": "Streamers", "console": "Console players",
        "builder": "PC builders", "vr": "VR", "stores": "Brand stores"}
GAME_LINKS = [("/deals/free-pc-games-right-now/", "Free PC games right now"), ("/deals/pc-games-under-5/", "PC games under $5"),
              ("/deals/pc-games-under-10/", "PC games under $10"), ("/deals/pc-games-under-15/", "PC games under $15"),
              ("/guides/best-co-op-pc-games-under-10-dollars/", "Best co-op PC games under $10"),
              ("/guides/best-pc-games-under-10-dollars-worth-buying/", "Best PC games under $10 worth buying"),
              ("/games.html", "Every game we track, with the lowest price")]
GUIDE_LINKS = [("/guides/best-gifts-for-pc-gamers-under-100/", "Best gifts for PC gamers under $100"),
               ("/guides/best-gaming-gifts-under-50/", "Best gaming gifts under $50"),
               ("/guides/best-gaming-headset-under-100/", "Best gaming headset under $100"),
               ("/guides/best-budget-gaming-desk-setup/", "Build a budget PC gaming desk setup"),
               ("/guides/best-usb-microphone-for-streaming-under-100/", "Best USB microphone for streaming"),
               ("/guides/black-friday-2026-pc-game-deals-guide/", "Black Friday 2026 PC game deals guide")]


# Offers marked data-until="YYYY-MM-DD" (copied from gear.html) hide themselves after that day, US Central time.
HIDE_ENDED = '<script>document.querySelectorAll("[data-until]").forEach(function(e){if(Date.now()>Date.parse(e.dataset.until+"T23:59:59-06:00"))e.remove()});</script>'


def esc(t):
    return html.escape(str(t), quote=True)


def parse(gear):
    """All product cards with their group, category, price and searchable text."""
    marks = [(m.start(), "group", m.group(1)) for m in re.finditer(r'<section class="group" id="([^"]+)"', gear)]
    marks += [(m.start(), "cat", html.unescape(m.group(1)).strip()) for m in re.finditer(r'<div class="cat">\s*<h3[^>]*>(.*?)</h3>', gear, re.S)]
    marks.sort()
    cards = []
    for m in re.finditer(r'<article class="item[^"]*"[^>]*>.*?</article>', gear, re.S):
        group = cat = None
        for pos, kind, val in marks:
            if pos > m.start():
                break
            if kind == "group":
                group, cat = val, None
            else:
                cat = val
        body = m.group(0)
        name = html.unescape(re.sub(r"<[^>]+>", "", (re.search(r"<h4>(.*?)</h4>", body, re.S) or [None, ""])[1])).strip()
        pm = re.search(r'<div class="price">.*?\$([\d,]+(?:\.\d+)?)', body, re.S)
        price = float(pm.group(1).replace(",", "")) if pm else None
        cards.append(dict(html=body, group=group, cat=cat, name=name, price=price))
    return cards


def grid(cards):
    return '<div class="items">\n' + "\n".join(c["html"] for c in cards) + "\n</div>"


def section(sid, title, intro, inner, extra_class=""):
    return f"""
  <section class="group{extra_class}" id="{sid}" aria-labelledby="{sid}-h">
    <div class="wrap">
      <div class="group-head">
        <h2 id="{sid}-h">{esc(title)}</h2>
        <p>{intro}</p>
      </div>
      {inner}
    </div>
  </section>"""


def main():
    gear = open(GEAR, encoding="utf-8").read()
    cards = parse(gear)
    head_end = gear.index("<body")
    head = gear[:head_end]
    header = re.search(r'<header class="site-header">.*?</header>', gear, re.S).group(0)
    # Only the footer itself: the Gear page's own filter script after it targets elements this page does not have.
    footer = gear[gear.index("<footer"):gear.index("</footer>") + len("</footer>")] + "\n" + HIDE_ENDED + "\n</body>\n</html>\n"
    helper = re.search(r"<script>function sgFix.*?</script>", gear, re.S).group(0)
    asof = re.search(r"listed on ([A-Z][a-z]{2} \d{1,2}, \d{4})", gear)
    asof = asof.group(1) if asof else "the date shown on our Gear page"

    # ---- head: new title, description, canonical, social tags
    title = "Gaming gifts for Black Friday and Christmas 2026 | SteelGames"
    count_all = len([c for c in cards])
    desc = (f"{count_all} gaming gift ideas for PC and console gamers, sorted by budget and by the kind of gamer: "
            "stocking stuffers under $25, gifts under $50 and $100, big gifts, Black Friday deals and games to gift.")
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", head, count=1, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + esc(desc) + m.group(2), head, count=1)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + URL + m.group(2), head, count=1)
    for prop, val in (("og:title", title), ("og:description", desc), ("og:url", URL)):
        head = re.sub(r'(<meta property="%s" content=")[^"]*(")' % prop, lambda m, v=val: m.group(1) + esc(v) + m.group(2), head)
    head = re.sub(r'(<meta name="twitter:(?:title|description)" content=")[^"]*(")', lambda m: m.group(1) + esc(desc if "description" in m.group(0) else title) + m.group(2), head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", head, flags=re.S)
    extra_css = """<style>
.gift-dates{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.gift-dates span{background:var(--surface);border:1px solid var(--line-strong);border-radius:12px;padding:8px 12px;font-size:15px;color:var(--steel)}
.gift-dates b{color:#fff}
.gift-search{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:8px}
.gift-search input{flex:1 1 260px;min-height:46px;padding:0 14px;border-radius:12px;border:1px solid var(--line-strong);background:var(--surface);color:#fff;font:inherit;font-size:16px}
.gift-search p{color:var(--muted);font-size:14px}
.link-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.link-list a{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;font-weight:600;text-decoration:none;color:#fff}
.link-list a:hover{border-color:var(--accent);color:#fff}
.group.is-empty{display:none}
</style>
"""
    head = head.replace("</head>", extra_css + "</head>")

    # ---- header: the Gifts tab is the current page
    header = header.replace(' aria-current="page"', "")
    header = re.sub(r'(<a href="/gifts/")>', r'\1 aria-current="page">', header, count=1)

    # ---- sections
    out_sections, jump, total = [], [], 0
    deals = [c for c in cards if c["group"] == "deals"]
    if deals:
        out_sections.append(section("deals", "Black Friday deals now",
                                    esc(BLACK_FRIDAY) + ". These sales are run by the stores, can change at any time and some end sooner, so check the final price at checkout.",
                                    '<div class="cat">' + grid(deals) + "</div>"))
        jump.append(("deals", "Black Friday deals"))
        total += len(deals)

    priced = sorted([c for c in cards if c["price"] is not None and c["group"] != "deals"], key=lambda c: (c["price"], c["name"]))
    for sid, title, lo, hi in BUDGETS:
        sel = [c for c in priced if lo <= c["price"] < hi]
        if not sel:
            continue
        intro = (f"Brand-store prices as each store listed them on {esc(asof)}, and JLab list prices (JLab buttons go to Amazon, where the price can differ). "
                 "Prices can change, so check the final price at checkout.")
        out_sections.append(section(sid, title, intro, '<div class="cat">' + grid(sel) + "</div>"))
        jump.append((sid, title.replace("Gifts from ", "").replace("Stocking stuffers under", "Under")))
        total += len(sel)

    used = {id(c) for c in deals} | {id(c) for c in priced}
    for sid, title, intro, picks in KINDS:
        cats_html, n = [], 0
        for group, cat in picks:
            sel = [c for c in cards if id(c) not in used and c["group"] == group and (cat is None or c["cat"] == cat)]
            if not sel:
                continue
            for c in sel:
                used.add(id(c))
            n += len(sel)
            label = cat or ""
            cats_html.append('<div class="cat">' + (f"<h3>{esc(label)}</h3>" if label else "") + grid(sel) + "</div>")
        if not n:
            continue
        intro += " Amazon buttons show today's price and reviews."
        out_sections.append(section(sid, title, esc(intro), "\n".join(cats_html)))
        jump.append((sid, JUMP.get(sid, title)))
        total += n

    left = [c for c in cards if id(c) not in used]
    if left:
        out_sections.append(section("more", "More gift ideas", "Everything else from our Gear page.", '<div class="cat">' + grid(left) + "</div>"))
        jump.append(("more", "More ideas"))
        total += len(left)

    links = lambda items: '<div class="link-list">' + "".join(f'<a href="{h}">{esc(t)}</a>' for h, t in items) + "</div>"
    out_sections.append(section("games", "Gift a game", "Our live deal lists show today's lowest prices on official stores and trusted sellers.", links(GAME_LINKS), " info"))
    out_sections.append(section("guides", "Gift guides", "Short buying guides with our top picks and why we chose them.", links(GUIDE_LINKS), " info"))
    jump += [("games", "Gift a game"), ("guides", "Gift guides")]

    jump_html = "\n".join(f'      <a href="#{sid}">{esc(label)}</a>' for sid, label in jump)
    star = re.search(r'<span class="vet-badge"[^>]*>.*?</span>', gear, re.S).group(0)
    body = f"""<body><a class="skip" href="#main" onclick="var m=document.querySelector('main');if(m){{m.setAttribute('tabindex','-1');m.focus();m.scrollIntoView();}}return false;">Skip to content</a>
{header}

<main>
  <section class="intro">
    <div class="wrap">
      {star}
      <h1>Gaming gifts for Black Friday and Christmas 2026</h1>
      <p class="lede">{total} gift ideas for PC and console gamers, sorted by budget and by the kind of gamer you are shopping for. Brand-store prices were checked on {esc(asof)}; Amazon buttons show today's price and reviews.</p>
      <div class="gift-dates"><span><b>Black Friday:</b> Fri, Nov 27</span><span><b>Cyber Monday:</b> Mon, Nov 30</span><span><b>Christmas:</b> Fri, Dec 25. Check each store's holiday shipping dates before you order.</span></div>
      <p class="notice"><strong>How we make money:</strong> As an Amazon Associate and a partner of the brands featured here, SteelGames earns from qualifying purchases. Every product button on this page is an affiliate link, and it costs you nothing extra. These are picks we chose, and we have not tested them ourselves.</p>
      <div class="gift-search"><input type="search" id="gift-q" placeholder="Search gifts, like keyboard, chair or controller" aria-label="Search gifts"><p id="gift-count" aria-live="polite"></p></div>
    </div>
  </section>

  <nav class="jump" aria-label="Gift sections">
    <div class="wrap">
{jump_html}
    </div>
  </nav>
{''.join(out_sections)}

  <section class="cta">
    <div class="wrap">
      <h2>Not sure what they want?</h2>
      <p>Our Gear page has every pick with filters, and the Discord is a good place to ask what other gamers would want.</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn" href="/gear.html">See all gear</a><a class="btn" href="https://discord.gg/ekrRaejc6">Join the Discord</a></div>
    </div>
  </section>
  <p class="shop-empty wrap" id="gift-empty" hidden>No gift matches that search. Try a shorter word, like "mouse" or "chair".</p>
</main>
{helper}
<script>
(function(){{var q=document.getElementById('gift-q'),c=document.getElementById('gift-count'),em=document.getElementById('gift-empty');
var items=[].slice.call(document.querySelectorAll('main .item'));var groups=[].slice.call(document.querySelectorAll('main section.group:not(.info)'));
function run(){{var v=(q.value||'').trim().toLowerCase(),n=0;items.forEach(function(i){{var ok=!v||i.textContent.toLowerCase().indexOf(v)>-1;i.hidden=!ok;if(ok)n++;}});
groups.forEach(function(g){{var any=g.querySelector('.item:not([hidden])');g.classList.toggle('is-empty',!any);}});
[].slice.call(document.querySelectorAll('main .cat')).forEach(function(ct){{ct.hidden=!ct.querySelector('.item:not([hidden])')&&!!ct.querySelector('.item');}});
c.textContent=v?(n+(n===1?' gift matches':' gifts match')):(items.length+' gift ideas');em.hidden=n>0;}}
q.addEventListener('input',run);run();}})();
</script>
"""
    page = head + body + footer
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "index.html")
    open(path, "w", encoding="utf-8").write(page)
    print(f"wrote {path}: {total} gift cards, {len(page):,} bytes")


if __name__ == "__main__":
    main()
