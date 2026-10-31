"""Veteran and first responder discounts page for SteelGames (static content, no live data)."""
import html
import layout

SITE = layout.SITE
CHECKED = "October 31, 2026"

# Each entry only states what a brand page or public source reported. Amounts can change.
# who: "mil" = military/veterans, "fr" = first responders (police, fire, EMS).
BRANDS = [
    {"name": "Razer", "cat": "Peripherals & PCs", "c": "#5CE08A", "url": "https://www.razer.com/campaigns/heroes", "who": ["mil", "fr"],
     "desc": "The Razer Heroes Program covers active duty, retirees, veterans, military spouses and family, plus active police, firefighters and EMTs (and medical providers). US only. Reported at 15% off peripherals and accessories and 5% off desktops and laptops, verified through ID.me. Codes are single-use, last one month and exclude refurbished items.",
     "tags": ["15% peripherals", "5% PCs", "ID.me"]},
    {"name": "Dell", "cat": "PCs", "c": "#66C0F4", "url": "https://www.dell.com/en-us/lp/govx", "who": ["mil", "fr"],
     "desc": "Dell's Heroes program covers military, veterans and retirees, police, firefighters, EMTs, search and rescue, and healthcare workers in the US. Dell advertises up to 10% extra off eligible products on Dell.com, limited to two products per order and two orders a year. Verification runs through SheerID.",
     "tags": ["Up to 10%", "SheerID", "2 orders/yr"]},
    {"name": "ORIGIN PC", "cat": "Gaming PCs", "c": "#B388FF", "url": "https://www.originpc.com", "who": ["mil", "fr"],
     "desc": "Custom-built gaming desktops and laptops. ORIGIN PC announced a 2.5% ID.me discount in 2022 for military, government workers, nurses, first responders, teachers and students. Confirm it is still active before you order.",
     "tags": ["2.5% (2022)", "ID.me"]},
    {"name": "Glorious", "cat": "Peripherals", "c": "#FFB020", "url": "https://www.gloriousgaming.com", "who": ["mil"],
     "desc": "Mice, keyboards and desk gear from a Dallas-based brand. Its Heroes Discount Program gave 10% off to verified active-duty military and veterans through ID.me (announced May 2024).",
     "tags": ["10% reported", "ID.me"]},
    {"name": "Corsair", "cat": "PC parts", "c": "#FFD76A", "url": "https://www.corsair.com", "who": ["mil"],
     "desc": "Cases, coolers, memory and peripherals for builders. Corsair offers a military discount through ID.me verification. Past offers have been around 5% off qualifying purchases.",
     "tags": ["ID.me", "~5% past offers"]},
    {"name": "Lenovo", "cat": "PCs", "c": "#FF6B8A", "url": "https://www.lenovo.com", "who": ["mil"],
     "desc": "Laptops and desktops for US military, reservists, veterans and their immediate families. Lenovo also ships to APO, FPO and DPO addresses.",
     "tags": ["Families eligible", "APO/FPO shipping"]},
    {"name": "Xotic PC", "cat": "Gaming PCs", "c": "#4DD0E1", "url": "https://www.xoticpc.com", "who": ["mil"],
     "desc": "Custom gaming laptops and desktops. Listed by the Kansas Office of Veterans Services (verified February 2026) as offering special pricing for veterans. Ask them for the current amount.",
     "tags": ["Special veteran pricing"]},
    {"name": "Vertagear", "cat": "Chairs", "c": "#FF8A3D", "url": "https://www.vertagear.com", "who": ["mil"],
     "desc": "Gaming chairs and accessories. The Military Appreciation Program is reported at 20% off. You fill out a form with your name, email and a copy of your DD-214.",
     "tags": ["20% reported", "DD-214 form"]},
    {"name": "Chairs4Gaming", "cat": "Chairs & desks", "c": "#5CE08A", "url": "https://www.chairs4gaming.com", "who": ["mil"],
     "desc": "Gaming chairs, desks and accessories. Reported at 15% off after a quick verification, which gives you a one-time code. It does not apply to Black Friday, Cyber Monday or holiday sales.",
     "tags": ["15% reported", "Not valid Black Friday"]},
    {"name": "Skullcandy", "cat": "Audio", "c": "#66C0F4", "url": "https://www.skullcandy.com", "who": ["mil"],
     "desc": "Headsets and earbuds. Skullcandy offers military discounts and cash back on gaming audio when you verify with ID.me.",
     "tags": ["ID.me", "Cash back"]},
    {"name": "GameStop", "cat": "Games & collectibles", "c": "#FF6B8A", "url": "https://www.gamestop.com/military-discount", "who": ["mil"],
     "desc": "Limited. GameStop gives active military 10% off toys, collectibles and pre-owned items in store only. New games, new accessories, consoles and PC hardware are excluded.",
     "tags": ["10% in store", "Many exclusions"]},
]

STAR = ('<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M12 2l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 15.4l-5.3 3 1.2-6L3.4 8.3l6-.7z"/></svg>')

TIPS = [
    "Verification usually runs through ID.me, SheerID or GovX. Set up an ID.me account once and several of these brands accept it.",
    "Some brands ask for a DD-214 instead. Keep a clean copy on hand so you can upload it.",
    "Codes often can't be combined with other offers, and many are blocked on Black Friday and Cyber Monday. Compare the sale price against your code price.",
    "Terms change often. Check the brand's program page before you check out, and send us a note if something is out of date.",
]

FILTER_JS = """<script>
(function(){var chips=document.querySelectorAll('#who button');var cards=document.querySelectorAll('.scard[data-who]');
function show(w){cards.forEach(function(c){c.hidden=!(w==='all'||c.dataset.who.split(' ').indexOf(w)>-1);});
chips.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.w===w?'true':'false');});}
chips.forEach(function(b){b.addEventListener('click',function(){show(b.dataset.w);});});show('all');})();
</script>
"""


def card(b):
    e = html.escape
    tags = "".join(f"<span>{e(t)}</span>" for t in b["tags"])
    return (f'<a class="scard" data-who="{" ".join(b["who"])}" style="--c:{b["c"]}" href="{e(b["url"])}" target="_blank" rel="noopener noreferrer">'
            f'<span class="ph">{STAR}</span><h3>{e(b["name"])}</h3><p>{e(b["desc"])}</p>'
            f'<span class="tags"><span>{e(b["cat"])}</span>{tags}</span><span class="go">See the program &rarr;</span></a>')


def best_for_game_html():
    """Compact callout used on game pages."""
    return ('<div class="vetbox"><strong>Veteran, military or first responder?</strong> '
            'Razer, Dell and ORIGIN PC take extra off for those who serve. '
            '<a href="/military.html">See every discount &rarr;</a></div>')


def build():
    title = "Veteran and First Responder Gaming Discounts | SteelGames"
    desc = ("Military, veteran and first responder discounts on gaming PCs, peripherals, chairs and audio gear. "
            "See which brands honor those who serve, what they offer and how to verify. Veteran-owned.")
    url = f"{SITE}/military.html"
    tips = "".join(f'<div class="tip"><b>{i}</b><p>{html.escape(t)}</p></div>' for i, t in enumerate(TIPS, 1))
    mail = "mailto:steelgames.app@outlook.com?subject=Discount%20tip"
    return (layout.head(title, desc, url)
            + layout.header("military")
            + f"""<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Veteran-owned &middot; For those who serve</p>
<h1>Veteran and first responder gaming discounts</h1>
<p class="lede">Brands that give service members, veterans, police, firefighters and EMTs a better price on gaming PCs, peripherals, chairs and audio. SteelGames is veteran-owned, so this list is personal. Last checked {CHECKED}.</p>
<div class="chips" id="who" role="group" aria-label="Filter by who qualifies"><button type="button" data-w="all" aria-pressed="true">All</button><button type="button" data-w="mil" aria-pressed="false">Military &amp; veterans</button><button type="button" data-w="fr" aria-pressed="false">First responders</button></div>
</div></section>
<section class="block" id="brands"><div class="wrap"><h2>Brands that honor service</h2>
<p class="fine">Amounts are as last reported by each brand or a public source. Programs change, so confirm the current offer on the brand's page before you buy.</p>
<div class="sgrid">{"".join(card(b) for b in BRANDS)}</div></div></section>
<section class="block" id="verify"><div class="wrap"><h2>How to claim these discounts</h2>
<div class="tips">{tips}</div>
<div class="chips"><a href="https://www.id.me" target="_blank" rel="noopener noreferrer">ID.me</a><a href="https://www.govx.com" target="_blank" rel="noopener noreferrer">GovX</a></div></div></section>
<section class="block" id="tip"><div class="wrap"><h2>Know a brand we missed?</h2>
<p class="lede">Tell us about a military, veteran or first responder discount and we will check it and add it. Brands can also reach us about listing a program.</p>
<div class="chips"><a href="{mail}">Send a discount tip</a><a href="/advertise.html">Brands: get listed</a></div></div></section>
</main>
{FILTER_JS}"""
            + layout.footer())


if __name__ == "__main__":
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    open(os.path.join(root, "military.html"), "w").write(build())
