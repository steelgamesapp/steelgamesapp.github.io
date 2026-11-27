"""Builds steelgamesapp.com/s/ : "Gear from our videos", one numbered card per Short/TikTok.

Every video says "#N on steelgamesapp.com/s" and its pinned comment/caption repeats it, so a viewer lands on
exactly the product from the video they just watched. Data lives in data/videos.json (newest numbers shown first).

Amazon rules (Associates linking requirements): no Amazon prices or star ratings on this page, only a
"Check today's price on Amazon" button. Brand-store picks link through our brand affiliate links.

Run: python3 tools/videos_page.py
"""
import html
import json
import os

import gear_shop as gs
import layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "data", "videos.json")))
OUT = os.path.join(ROOT, "s", "index.html")
e = html.escape

TOPICS = {"mouse": "Mice", "fps": "Shooter settings", "pc": "PC and Windows", "console": "PS5 and Xbox", "monitor": "Monitors"}
PRIME = "https://www.amazon.com/amazonprime?tag=" + gs.TAG

BRAND_IMG = {(c["brand"], it["handle"]): it.get("img", "") for c in gs.DATA["brand_cats"] for it in c["items"]}


def pick_html(p, alt=False):
    if p.get("amazon"):
        url, img, btn = gs.amazon_url(p["amazon"]), gs.amazon_img(p["amazon"]), "Check today's price on Amazon"
        store = "Amazon"
    else:
        url = gs.brand_url(p["brand"], p["handle"])
        path = BRAND_IMG.get((p["brand"], p["handle"]), "")
        img = gs.shopify_img(path, 400) if path else ""
        btn, store = f"Shop at {p['brand']}", p["brand"]
    label = "Budget or brand-store pick" if alt else "Our pick"
    pic = f'<img src="{e(img)}" alt="{e(p["name"])}" loading="lazy" width="120" height="120">' if img else ""
    return (f'<div class="vp{" alt" if alt else ""}"><a class="vp-pic" href="{e(url)}" target="_blank" rel="sponsored nofollow noopener" '
            f'tabindex="-1" aria-hidden="true">{pic}</a><div class="vp-txt"><small>{label}</small><b>{e(p["name"])}</b>'
            f'<span>{e(p["why"])}</span><a class="vp-btn" href="{e(url)}" target="_blank" rel="sponsored nofollow noopener" '
            f'data-store="{e(store)}">{e(btn)} &rarr;</a></div></div>')


def card(v):
    picks = pick_html(v["pick"]) + (pick_html(v["alt"], True) if v.get("alt") else "")
    return (f'<article class="vc" id="{v["n"]}" data-topic="{e(v.get("topic", ""))}"><div class="vc-head"><span class="vc-n">#{v["n"]}</span>'
            f'<h2>{e(v["title"])}</h2></div><p class="vc-tip"><b>The tip:</b> {e(v["tip"])}</p>{picks}</article>')


CSS = """<style>
.s-hero{padding:28px 0 8px}.s-hero h1{margin:0 0 8px}
.s-find{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:14px 0 6px}
.s-find input{width:110px;padding:10px 12px;border-radius:10px;border:1px solid #3A2C7A;background:#140D33;color:#fff;font:600 18px Inter,system-ui,sans-serif}
.s-find button,.s-chip{padding:10px 14px;border-radius:10px;border:1px solid #3A2C7A;background:#261B5C;color:#fff;font:600 14px Inter,system-ui,sans-serif;cursor:pointer}
.s-chips{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 18px}.s-chip[aria-pressed="true"]{background:#FF7A1A;border-color:#FF7A1A;color:#140D33}
.s-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}
.vc{background:#140D33;border:1px solid #2C2160;border-radius:16px;padding:16px;scroll-margin-top:90px}
.vc:target{border-color:#FF7A1A;box-shadow:0 0 0 2px #FF7A1A55}
.vc-head{display:flex;gap:10px;align-items:flex-start}.vc-head h2{font-size:17px;line-height:1.3;margin:2px 0 0}
.vc-n{flex:none;background:#FF7A1A;color:#140D33;font:700 16px "Space Grotesk",Inter,sans-serif;border-radius:9px;padding:5px 9px}
.vc-tip{color:#CFC8F0;font-size:14px;margin:10px 0 12px}
.vp{display:flex;gap:12px;align-items:flex-start;border-top:1px solid #2C2160;padding-top:12px;margin-top:10px}
.vp-pic{flex:none;width:96px;height:96px;background:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.vp-pic img{max-width:92px;max-height:92px;object-fit:contain}
.vp-txt{display:flex;flex-direction:column;gap:3px;font-size:14px}.vp-txt small{color:#FF8A1A;font-weight:600;text-transform:uppercase;letter-spacing:.6px;font-size:11px}
.vp-txt span{color:#CFC8F0}.vp.alt .vp-txt small{color:#8FB4E3}
.vp-btn{margin-top:6px;align-self:flex-start;background:#FF7A1A;color:#140D33;font-weight:700;padding:9px 12px;border-radius:9px;text-decoration:none}
.vp.alt .vp-btn{background:#261B5C;color:#fff;border:1px solid #3A2C7A}
.s-prime{background:#1B1245;border:1px solid #3A2C7A;border-radius:14px;padding:14px 16px;margin:6px 0 20px;font-size:14px}
.s-prime a{color:#FF8A1A;font-weight:700}
</style>"""

JS = """<script>
(function(){
 var f=document.getElementById('sFind'),i=document.getElementById('sNum');
 f.addEventListener('submit',function(ev){ev.preventDefault();var n=(i.value||'').replace(/\\D/g,'');var el=n&&document.getElementById(n);
  if(el){location.hash=n;el.scrollIntoView({behavior:'smooth',block:'start'})}else{i.setCustomValidity('No video #'+n+' yet');i.reportValidity();i.setCustomValidity('')}});
 var chips=document.getElementById('sChips');chips.addEventListener('click',function(ev){var b=ev.target.closest('.s-chip');if(!b)return;
  chips.querySelectorAll('.s-chip').forEach(function(c){c.setAttribute('aria-pressed',c===b)});
  document.querySelectorAll('.vc').forEach(function(c){c.style.display=(b.dataset.t==='all'||c.dataset.topic===b.dataset.t)?'':'none'})});
 document.addEventListener('click',function(ev){var a=ev.target.closest('.vp-btn');if(!a||!window.goatcounter||!goatcounter.count)return;
  var c=a.closest('.vc');goatcounter.count({path:'s-click-'+(c?c.id:'x')+'-'+(a.dataset.store||'').toLowerCase(),event:true})});
})();
</script>"""


def build():
    vids = sorted(DATA["videos"], key=lambda v: -v["n"])
    topics = [t for t in TOPICS if any(v.get("topic") == t for v in vids)]
    chips = '<button class="s-chip" aria-pressed="true" data-t="all">All</button>' + "".join(
        f'<button class="s-chip" aria-pressed="false" data-t="{t}">{TOPICS[t]}</button>' for t in topics)
    body = f"""<main id="main"><div class="wrap">
<section class="s-hero">
<h1>Gear from our videos</h1>
<p class="lede">Every SteelGames Short and TikTok has a number. Find yours below to see the gear that goes with that tip.</p>
<form class="s-find" id="sFind" role="search" aria-label="Find a video by number"><label for="sNum">Video #</label><input id="sNum" inputmode="numeric" autocomplete="off" placeholder="12"><button type="submit">Show me</button></form>
</section>
<p class="s-prime"><b>Shopping before Christmas?</b> Get free fast delivery on Prime items with a <a href="{PRIME}" target="_blank" rel="sponsored nofollow noopener">free Amazon Prime trial</a>.</p>
<div class="s-chips" id="sChips" role="group" aria-label="Filter by topic">{chips}</div>
<div class="s-grid">
{"".join(card(v) for v in vids)}
</div>
<p class="fine" style="margin-top:24px">Amazon buttons show today's price and reviews on Amazon.com. Brand-store buttons go to the brand's own store. We earn a commission from these links at no extra cost to you.</p>
</div></main>
"""
    page = (layout.head("Gear from our videos | SteelGames", "Find the gaming gear from any SteelGames Short or TikTok by its number.",
                        layout.SITE + "/s/", CSS) + layout.header("gear") + body + JS + layout.footer())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(page)
    print(f"wrote {OUT}: {len(vids)} videos")


if __name__ == "__main__":
    build()
