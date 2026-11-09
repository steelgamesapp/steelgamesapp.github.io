"""Builds /international.html: shop gaming gear from your own country's Amazon store.

Every button on the page is written as a normal amazon.com search link. /assets/geo.js (loaded on every page) works out the
visitor's country and swaps each link for the same search on their local Amazon site, so the page also works with JavaScript off.
Product names and pictures below are the picks already shown in our buying guides."""
import html
import layout

SITE = layout.SITE
TAG = "steelgames-20"
E = html.escape


def az(q):
    return f"https://www.amazon.com/s?k={q.replace(' ', '+')}&tag={TAG}"


ARROW = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>')
REL = 'target="_blank" rel="sponsored nofollow noopener"'

# (icon file, title, search words, what to look for)
CATEGORIES = [
    ("mouse", "Gaming mouse", "gaming mouse", "Wired or wireless, pick one that fits your hand size and the way you grip a mouse."),
    ("keyboard", "Mechanical keyboard", "mechanical keyboard", "A compact 60% or 75% board saves desk space for mouse swings."),
    ("headset", "Gaming headset", "gaming headset", "Wired headsets cost less and never need charging; wireless ones free up your desk."),
    ("monitor", "Gaming monitor", "gaming monitor 144hz", "A 144 Hz or higher refresh rate makes motion look smoother than a standard 60 Hz screen."),
    ("controller", "PC game controller", "pc game controller", "Check that it works with Windows out of the box."),
    ("mic", "USB microphone", "usb microphone", "USB mics plug straight in, an easy upgrade for voice chat and streaming."),
    ("chair", "Gaming chair", "gaming chair", "Check the seat height range and weight limit against your own size."),
    ("pad", "Mouse pad", "gaming mouse pad large", "A large desk mat gives your mouse and keyboard one smooth surface."),
    ("storage", "SSD for game installs", "internal ssd 1tb nvme", "Move your biggest games to an SSD to cut load times."),
]

# (name, kind, picture). Names are searched on the visitor's local store, so a pick that is not sold there shows the closest match.
PICKS = [
    ("Logitech G305 Lightspeed Wireless Mouse", "Wireless mouse", "https://m.media-amazon.com/images/I/51sg9BLSMTL._AC_SL400_.jpg", "mouse"),
    ("ATTACK SHARK X3 Wireless Gaming Mouse", "Ultralight wireless mouse", "https://m.media-amazon.com/images/I/61bIadP0qML._AC_SL400_.jpg", "mouse"),
    ("Keychron C2 Pro Wired Mechanical Keyboard", "Full-size wired keyboard", "https://m.media-amazon.com/images/I/61BD0Q4JcyL._AC_SL400_.jpg", "keyboard"),
    ("RK ROYAL KLUDGE R65 Mechanical Keyboard", "Compact 60% keyboard", "https://m.media-amazon.com/images/I/61hOhuiqrTL._AC_SL400_.jpg", "keyboard"),
    ("HyperX Cloud Stinger 2 Gaming Headset", "Wired headset", "https://m.media-amazon.com/images/I/61gKp5mi0-L._AC_SL400_.jpg", "headset"),
    ("Logitech G435 Lightspeed Wireless Gaming Headset", "Wireless headset", "https://m.media-amazon.com/images/I/81bQEkMevBL._AC_SL400_.jpg", "headset"),
    ("MSI PRO MP243L 24-inch 144Hz Monitor", "24-inch 1080p, 144 Hz", "https://m.media-amazon.com/images/I/7105oWqjsjL._AC_SL400_.jpg", "monitor"),
    ("SANSUI 27-inch 1440p 180Hz IPS Monitor", "27-inch 1440p, 180 Hz", "https://m.media-amazon.com/images/I/71CfZv5EvpL._AC_SL400_.jpg", "monitor"),
    ("GameSir Nova Lite 2 Wireless PC Controller", "Wireless controller", "https://m.media-amazon.com/images/I/61yHqDf0SqL._AC_SL400_.jpg", "controller"),
    ("Logitech Blue Yeti USB Microphone", "USB microphone", "https://m.media-amazon.com/images/I/61KTMvS5JBL._AC_SL400_.jpg", "mic"),
    ("AKG Ara USB-C Condenser Microphone", "USB microphone", "https://m.media-amazon.com/images/I/61b9fd3RPnL._AC_SL400_.jpg", "mic"),
    ("Redragon S101 Keyboard and Mouse Combo", "Keyboard and mouse set", "https://m.media-amazon.com/images/I/81OG51gWHVL._AC_SL400_.jpg", "keyboard"),
]

CSS = """<style>
.geo-now{font-weight:600;color:#fff}
.geo-chips button{font-size:14px}
.geo-note{max-width:46em}
.faq h3{font-size:18px;margin-top:6px}
.faq p{color:var(--steel);max-width:46em}
</style>
"""

SCRIPT = """<script>
(function () {
  var chips = document.getElementById('geo-chips'), now = document.getElementById('geo-now');
  if (!chips) return;
  function draw() {
    var g = window.SGGeo; if (!g) return;
    var names = Object.keys(g.sites).sort(function (a, b) { return g.sites[a][1].localeCompare(g.sites[b][1]); });
    chips.textContent = '';
    names.forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = g.sites[c][1];
      b.setAttribute('aria-pressed', c === g.region() ? 'true' : 'false');
      b.addEventListener('click', function () { g.set(c); });
      chips.appendChild(b);
    });
    now.textContent = 'Your Amazon store: ' + g.shortHost(g.region()) + ' (' + g.sites[g.region()][1] + ')';
  }
  document.addEventListener('sg:geo', draw);
  draw();
})();
</script>
"""


def category_card(icon, title, q, tip):
    return (f'<article class="gcar"><a class="gimg icon" href="{E(az(q))}" {REL} tabindex="-1" aria-hidden="true">'
            f'<img src="/assets/gear-icons/{icon}.svg" alt="" loading="lazy" width="256" height="256"></a>'
            f'<div class="gb"><h3>{E(title)}</h3><p>{E(tip)}</p>'
            f'<a class="btn gbuy" href="{E(az(q))}" {REL} data-sg-name="{E(q)}">See prices on Amazon{ARROW}</a></div></article>')


def pick_card(name, kind, img, icon):
    fb = f"this.onerror=null;this.src='/assets/gear-icons/{icon}.svg';this.closest('.gimg').classList.add('icon')"
    return (f'<article class="gcar"><p class="gl">{E(kind)}</p>'
            f'<a class="gimg" href="{E(az(name))}" {REL} tabindex="-1" aria-hidden="true">'
            f'<img src="{E(img)}" alt="{E(name)}" loading="lazy" width="400" height="300" onerror="{E(fb)}"></a>'
            f'<div class="gb"><h3>{E(name)}</h3>'
            f'<a class="btn gbuy" href="{E(az(name))}" {REL}>See price on Amazon{ARROW}</a></div></article>')


def build():
    title = "Shop gaming gear from your country | SteelGames"
    desc = ("Amazon runs a separate store in every country. Pick yours and every SteelGames gear link sends you to your local Amazon "
            "with local prices and delivery.")
    out = [layout.head(title, desc, f"{SITE}/international.html", CSS), layout.header("gear"), "<main>\n"]
    out.append(
        '<section class="hero"><div class="wrap">\n'
        '<p class="crumbs"><a href="/">Home</a> / <a href="/gear.html">Gear</a> / Shop from your country</p>\n'
        '<h1>Shop gaming gear from your country</h1>\n'
        '<p class="lede">Amazon runs a separate store in each country. Pick yours below and every Amazon button on SteelGames '
        'will send you to your own store, with local prices, local currency and local delivery.</p>\n'
        '<p class="fine geo-note">We choose your country automatically and remember your pick in this browser only. '
        'You can change it here or from the selector at the bottom of any page.</p>\n'
        '</div></section>\n')
    out.append(
        '<section class="block" id="country"><div class="wrap">\n<h2>Pick your country</h2>\n'
        '<p class="geo-now" id="geo-now" aria-live="polite">Your Amazon store: Amazon.com (United States)</p>\n'
        '<div class="chips cats geo-chips" id="geo-chips"><noscript>Turn on JavaScript to switch countries. These links go to Amazon.com.</noscript></div>\n'
        '<p class="fine geo-note">Not on the list? Amazon has no store in every country. If yours is missing, the links go to Amazon.com, '
        'which ships many items abroad. Check the delivery estimate and import fees before you order.</p>\n'
        '</div></section>\n')
    out.append('<section class="block" id="categories"><div class="wrap">\n<h2>Shop by category</h2>\n'
               '<p class="lede">These open a search on your local Amazon, so you always land on gear that is sold in your country.</p>\n'
               '<div class="gear-grid">' + "".join(category_card(*c) for c in CATEGORIES) + '</div>\n</div></section>\n')
    out.append('<section class="block" id="picks"><div class="wrap">\n<h2>Our favorite picks</h2>\n'
               '<p class="lede">The gear from our buying guides. Each button searches for the product on your local Amazon. '
               'A few items are sold only in some countries; if one is missing, the search shows the closest match.</p>\n'
               '<div class="gear-grid">' + "".join(pick_card(*p) for p in PICKS) + '</div>\n'
               '<p class="fine">Prices on Amazon change often, and they are shown in your own currency. '
               'See the full lists in our <a href="/guides/">buying guides</a> and on the <a href="/gear.html">Gear page</a>.</p>\n'
               '</div></section>\n')
    out.append(
        '<section class="block faq" id="faq"><div class="wrap">\n<h2>Questions</h2>\n'
        '<h3>Why do the buttons open a search instead of one product?</h3>\n'
        '<p>The same product is often not sold in every country, or has a different listing there. A search on your local store '
        'always shows what you can actually buy and have delivered.</p>\n'
        '<h3>Do I pay more because of these links?</h3>\n'
        '<p>No. The price is whatever Amazon charges in your country. See the note at the bottom of the page about commissions.</p>\n'
        '<h3>Where does my country come from?</h3>\n'
        '<p>Your browser asks a free country lookup run by Cloudflare, and we keep the answer in your browser for a week. '
        'If that fails, we use your browser language. We do not store it on our servers. You can always change it above.</p>\n'
        '</div></section>\n')
    out.append("</main>\n" + SCRIPT)
    out.append(layout.footer())
    return "".join(out)


if __name__ == "__main__":
    print(build()[:400])
