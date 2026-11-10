"""Media kit page for SteelGames advertisers (/media-kit/).

Every number on it is counted from the site's own files each time the daily build runs, so it stays true as the site grows.
Traffic and audience figures are shown only if data/traffic.json exists (see tools/SPONSORS.md); until then the page says
they are sent on request instead of guessing. Keep the rates in step with advertise.html.
"""
import html
import json
import os
import layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = layout.SITE
MAIL = "steelgames.app@outlook.com"

PACKAGES = [
    ("Featured spot", "$49 / week", "Top of the home page deals, with art, a short pitch and a link. Labeled Sponsored. Views and clicks counted."),
    ("Sponsored mission video", "$149 / video", "A short \"mission briefing\" video about your game, posted on our TikTok, Reels, Shorts and Bluesky."),
    ("Discord shout-out", "$25 / post", "A pinned post in our Discord deals channel."),
    ("Gear guide placement", "$39 / month", "A featured slot in the gaming gear guide for headsets, chairs, controllers and PC parts. Labeled Sponsored."),
]
CHANNELS = [
    ("Website", SITE + "/"),
    ("YouTube Shorts", "https://www.youtube.com/channel/UCxnxfOz2r4jsk6TTFB1Ar-Q"),
    ("TikTok", "https://www.tiktok.com/@steelgamesapp"),
    ("Instagram", "https://www.instagram.com/steelgamesapp/"),
    ("Discord", "https://discord.gg/ekrRaejc6"),
    ("Chrome extension", "https://chromewebstore.google.com/detail/digihifdddmmflefajfemioefidnoaif"),
]
RULES = [
    "Every paid spot is labeled Sponsored.",
    "Games must be sold through an official or authorized store.",
    "No gambling, adult content or account selling.",
    "We never sell or share our users' personal data with advertisers.",
]


def _count_dirs(rel, need="index.html"):
    base = os.path.join(ROOT, rel)
    if not os.path.isdir(base):
        return 0
    return sum(1 for n in os.listdir(base) if os.path.isfile(os.path.join(base, n, need)))


def _count_files(rel, ext=".json"):
    base = os.path.join(ROOT, rel)
    return sum(1 for n in os.listdir(base) if n.endswith(ext)) if os.path.isdir(base) else 0


def facts():
    return [
        (f"{_count_dirs('game'):,}", "PC games with their own price page, refreshed daily"),
        (f"{_count_dirs('deals'):,}", "deal lists by price, genre and theme"),
        (f"{_count_dirs('guides'):,}", "buying guides for games and gear"),
        (f"{_count_dirs('pros'):,}", "pro gamer setups with the gear they use"),
    ]


def traffic_block():
    try:
        t = json.load(open(os.path.join(ROOT, "data", "traffic.json")))
        rows = "".join(f"<tr><th scope=\"row\">{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>" for k, v in t.get("rows", {}).items())
        if rows:
            return (f'<table class="mk-t"><tbody>{rows}</tbody></table>'
                    f'<p class="fine">Source: {html.escape(t.get("source", "site analytics"))}. Updated {html.escape(t.get("updated", ""))}.</p>')
    except Exception:
        pass
    return (f'<p>Traffic and audience numbers change every week, so we send the current figures with your proposal instead of printing old ones. '
            f'<a href="mailto:{MAIL}?subject=SteelGames%20traffic%20numbers">Ask for this month\'s numbers</a>.</p>')


def build():
    e = html.escape
    style = """<style>
.mk-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:18px 0}
.mk-s{padding:16px;border-radius:12px;background:#150E38;border:1px solid #35288A}
.mk-s b{display:block;font:700 30px/1.1 "Space Grotesk",Inter,sans-serif;color:#fff}
.mk-s span{font-size:14px;color:#C9C2EE}
.mk-t{width:100%;border-collapse:collapse;margin:12px 0}
.mk-t th,.mk-t td{text-align:left;padding:10px 12px;border-bottom:1px solid #35288A;vertical-align:top}
.mk-t th{color:#fff;font-weight:600;width:34%}
.mk-t td{color:#C9C2EE}
.mk-t td.pr{color:#FFB020;font-weight:700;white-space:nowrap}
.mk-l{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}
.mk-l a{padding:9px 14px;border-radius:999px;border:1px solid #35288A;background:#150E38;color:#fff;text-decoration:none}
.mk-l a:hover{border-color:#B9AEFF}
</style>"""
    stats = "".join(f'<div class="mk-s"><b>{e(n)}</b><span>{e(t)}</span></div>' for n, t in facts())
    pkgs = "".join(f'<tr><th scope="row">{e(n)}</th><td>{e(d)}</td><td class="pr">{e(p)}</td></tr>' for n, p, d in PACKAGES)
    chans = "".join(f'<a href="{e(u)}" rel="noopener">{e(n)}</a>' for n, u in CHANNELS)
    rules = "".join(f"<li>{e(r)}</li>" for r in RULES)
    title = "Media kit and advertising rates | SteelGames"
    desc = "SteelGames media kit: what the PC game deals site tracks, where it is promoted, and rates for sponsored spots, videos and gear placements."
    return (layout.head(title, desc, f"{SITE}/media-kit/", extra=style) + layout.header("") + f"""<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">For advertisers and brand partners</p>
<h1>SteelGames media kit</h1>
<p class="lede">SteelGames is a veteran-owned PC game deals site. People open it when they are about to buy a game or upgrade their setup. This page lists what the site tracks, where it is promoted and what a sponsored spot costs.</p>
<div class="chips"><a class="btn" href="mailto:{MAIL}?subject=Advertising%20on%20SteelGames">Email us to book</a><a href="/advertise.html">Ways to advertise</a></div>
</div></section>
<section class="block"><div class="wrap">
<h2>What the site tracks today</h2>
<div class="mk-g">{stats}</div>
<p class="fine">Counted from the live site when this page was built. Official stores and authorized key sellers are compared side by side, with a Wait-O-Meter that says whether to buy now or wait.</p>
</div></section>
<section class="block"><div class="wrap">
<h2>Rates</h2>
<table class="mk-t"><tbody>{pkgs}</tbody></table>
<p class="fine">Launch rates for a limited time. We reply with open dates and a simple invoice. We count views and clicks on every paid spot and send you the numbers when your run ends.</p>
</div></section>
<section class="block"><div class="wrap">
<h2>Traffic and audience</h2>
{traffic_block()}
</div></section>
<section class="block"><div class="wrap">
<h2>Where we are</h2>
<div class="mk-l">{chans}</div>
</div></section>
<section class="block"><div class="wrap">
<h2>Our rules</h2>
<ul>{rules}</ul>
<p class="fine">SteelGames is a product of Lonestar PPS, LLC, a veteran-owned company. Questions: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
</div></section>
</main>
""" + layout.footer())


if __name__ == "__main__":
    out = os.path.join(ROOT, "media-kit")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w").write(build())
    print("wrote media-kit/index.html")
