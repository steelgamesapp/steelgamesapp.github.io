"""Shared page shell (head, header, footer) for generated SteelGames pages."""
import html

SITE = "https://steelgamesapp.com"
LOGO = ('<svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 2 28 9v14l-12 7L4 23V9z" fill="#1C2027" '
        'stroke="#C3CBD5" stroke-width="2" stroke-linejoin="round"/><path d="M20 11h-6a2.5 2.5 0 0 0 0 5h4a2.5 2.5 0 0 1 0 5h-6" '
        'fill="none" stroke="#FF7A1A" stroke-width="2.4" stroke-linecap="round"/></svg>')
STAR = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8FB4E3" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M12 2l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 15.4l-5.3 3 1.2-6L3.4 8.3l6-.7z"/></svg>')
HEART = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.6-9.3-9A5.4 5.4 0 0 1 12 6.6 5.4 5.4 0 0 1 21.3 12C19 16.4 12 21 12 21z"/></svg>'
CARTI = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 12.2a1 1 0 0 0 1 .8h9.1a1 1 0 0 0 1-.8L21 7H6"/></svg>'
NAV = [("games", "/games.html", "Games"), ("keys", "/keys.html", "Keys"), ("news", "/app/#/news", "News"), ("gear", "/gear.html", "Gear"),
       ("reviews", "/reviews.html", "Reviews"), ("community", "/community.html", "Community")]


def head(title, desc, canonical, extra=""):
    e = html.escape
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/assets/pages.css">
<meta name="google-adsense-account" content="ca-pub-3613204296597380">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3613204296597380" crossorigin="anonymous"></script>
<script data-goatcounter="https://steelgames.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script src="/assets/shop.js" defer></script>
{extra}</head>
<body>
"""


def header(active=""):
    cur = ' aria-current="page"'
    links = "".join('<a href="%s"%s>%s</a>' % (h, cur if k == active else "", n) for k, h, n in NAV)
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="SteelGames home">{LOGO}<span>STEELGAMES</span></a>
    <nav class="nav" aria-label="Site">{links}<a class="nav-cta" href="/app/#/account">Profile</a></nav>
  </div>
</header>
"""


def footer():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <span class="vet-badge">{STAR}Veteran-owned and operated</span>
    <div class="footer-links">
      <a href="/games.html">Games</a><a href="/keys.html">Key resellers</a><a href="/deals/">Deal lists</a><a href="/gear.html">Shop gear</a>
      <a href="/privacy.html">Privacy policy</a><a href="/terms.html">Terms of use</a><a href="/advertise.html">Advertise</a>
      <a href="mailto:steelgames.app@outlook.com">Contact us</a><span>© 2026 Lonestar PPS, LLC</span>
    </div>
    <p>As an Amazon Associate, SteelGames earns from qualifying purchases. SteelGames may also earn a commission from other stores linked on this site, at no extra cost to you. Prices can change at any time.</p>
    <p>SteelGames is a product of Lonestar PPS, LLC, a veteran-owned company. Not affiliated with Valve, Epic Games, Microsoft, Sony or Nintendo.</p>
  </div>
</footer>
</body>
</html>
"""


def img_for(d):
    """Best picture for a CheapShark deal: Steam capsule when we know the app id."""
    sid = str(d.get("steamAppID") or "")
    if sid and sid != "0":
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/capsule_184x69.jpg"
    return d.get("thumb") or ""
