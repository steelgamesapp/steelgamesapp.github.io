"""Home page band that advertises the Desk Setup Builder with an auto-scrolling strip of finished setups.
Writes between <!-- setups-preview --> and <!-- /setups-preview --> in index.html.
Pictures come from data/setup_ideas.json (node tools/render_setups.js). Run: python3 tools/home_setups.py"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICK = ["neon-cyberpunk", "all-white-minimal", "veteran-ops-room", "cozy-wood-cabin", "sim-racing-rig",
        "gta-6-night-drive", "bubblegum-pink", "dual-screen-streamer", "handheld-cozy-corner", "desert-sunset",
        "console-tv-corner", "crimson-battlestation", "forest-green", "first-setup-budget"]
e = html.escape

CSS = """<style>
.sbp{margin-top:22px;display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:18px;align-items:center;padding:18px;border-radius:16px;background:linear-gradient(120deg,#1F1650 0%,#140F2A 70%);border:1px solid var(--line-strong);overflow:hidden}
.sbp-txt h2{margin:0;font-size:clamp(21px,2.4vw,27px);line-height:1.15}
.sbp-txt p{margin:8px 0 14px;color:var(--steel);font-size:15px}
.sbp-new{display:inline-block;margin-bottom:8px;background:#FF8A1A;color:#fff;font:700 11px/1 'Space Grotesk',sans-serif;letter-spacing:.6px;padding:5px 8px;border-radius:6px}
.sbp-btns{display:flex;flex-wrap:wrap;gap:8px}
.sbp-go{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:12px;background:linear-gradient(135deg,#FFC21A 0%,#FF8A1A 100%);color:#1A0E04;font-weight:700;text-decoration:none}
.sbp-alt{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:12px;border:1px solid var(--line-strong);color:#fff;font-weight:600;text-decoration:none}
.sbp-alt:hover{background:rgba(255,255,255,.06);color:#fff}
.sbp-view{position:relative;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
.sbp-track{display:flex;gap:12px;width:max-content;animation:sbp-run 70s linear infinite}
.sbp-view:hover .sbp-track,.sbp-view:focus-within .sbp-track{animation-play-state:paused}
@keyframes sbp-run{to{transform:translateX(calc(-50% - 6px))}}
.sbp-c{flex:none;width:230px;border-radius:12px;overflow:hidden;background:#140F2A;border:1px solid var(--line);color:#fff;text-decoration:none}
.sbp-c:hover{border-color:#B9AEFF;color:#fff}
.sbp-c img{display:block;width:100%;height:auto;aspect-ratio:5/3}
.sbp-c span{display:block;padding:7px 10px 9px;font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sbp-c small{display:block;color:var(--accent-soft,#B9AEFF);font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase}
@media (max-width:760px){.sbp{grid-template-columns:minmax(0,1fr);padding:14px}.sbp-c{width:190px}}
@media (prefers-reduced-motion:reduce){.sbp-track{animation:none}.sbp-view{overflow-x:auto;-webkit-mask-image:none;mask-image:none}.sbp-track [aria-hidden=true]{display:none}}
</style>"""


def build():
    ideas = {i["slug"]: i for i in json.load(open(os.path.join(ROOT, "data", "setup_ideas.json")))["setups"]}
    picks = [ideas[s] for s in PICK if s in ideas]

    def card(it, dup):
        extra = ' aria-hidden="true" tabindex="-1"' if dup else ''
        return (f'<a class="sbp-c" href="/setups/ideas/#{e(it["slug"])}"{extra}>'
                f'<img src="/assets/setups/draw/{e(it["slug"])}.svg" width="1200" height="720" loading="lazy" alt="{"" if dup else "Drawing of the " + e(it["name"]) + " setup"}">'
                f'<span><small>{e(it["look"])}</small>{e(it["name"])}</span></a>')
    track = "".join(card(i, False) for i in picks) + "".join(card(i, True) for i in picks)
    return f"""<!-- setups-preview -->
    {CSS}
    <section class="sbp" aria-labelledby="sbp-h">
      <div class="sbp-txt"><span class="sbp-new">NEW</span><h2 id="sbp-h">Build your dream gaming desk</h2>
        <p>Pick a desk, lights, screens and gear and watch it come together. Every piece links to Amazon, from budget to premium.</p>
        <div class="sbp-btns"><a class="sbp-go" href="/setups/">Open the Setup Builder</a><a class="sbp-alt" href="/setups/ideas/#ds-h">See {len(ideas)} setups</a></div></div>
      <div class="sbp-view"><div class="sbp-track">{track}</div></div>
    </section>
    <!-- /setups-preview -->"""


if __name__ == "__main__":
    p = os.path.join(ROOT, "index.html")
    page = open(p).read()
    block = build()
    if "<!-- setups-preview -->" in page:
        page = re.sub(r"<!-- setups-preview -->.*?<!-- /setups-preview -->", lambda m: block, page, flags=re.S)
    else:  # first run: right after the deals and gifts picture slider
        anchor = '<section class="pr" aria-labelledby="pr-h">'
        i = page.index(anchor)
        j = page.index("</section>", i) + len("</section>")
        page = page[:j] + "\n    " + block + page[j:]
    open(p, "w").write(page)
    print("home page setups preview updated")
