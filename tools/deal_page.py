"""Builds /deal/index.html: the price comparison page every deal card links to."""
import layout

SITE = layout.SITE

SCRIPT = r"""
<script>
document.addEventListener('DOMContentLoaded', async () => {
  const API = 'https://www.cheapshark.com/api/1.0';
  const out = document.getElementById('out');
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const $ = (v) => (+v === 0 ? 'Free' : '$' + (+v).toFixed(2));
  const id = new URLSearchParams(location.search).get('id');
  const fail = (m) => { out.innerHTML = '<div class="wrap" style="padding-block:48px"><h1 style="font-size:32px">' + m + '</h1><p class="lede" style="margin-top:10px"><a href="/games.html">Browse all games</a></p></div>'; };
  if (!id || !/^\d+$/.test(id)) return fail('Game not found');
  try {
    const [stores, g] = await Promise.all([fetch(API + '/stores').then((r) => r.json()), fetch(API + '/games?id=' + id).then((r) => r.json())]);
    const names = Object.fromEntries(stores.filter((s) => s.isActive).map((s) => [s.storeID, s.storeName]));
    const deals = (g.deals || []).filter((d) => names[d.storeID]).sort((a, b) => +a.price - +b.price);
    if (!g.info || !deals.length) throw new Error('none');
    const title = g.info.title, best = deals[0], sid = g.info.steamAppID && g.info.steamAppID !== '0' ? g.info.steamAppID : '';
    document.title = title + ': compare prices | SteelGames';
    const cover = sid ? 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + sid + '/header.jpg' : g.info.thumb;
    const off = Math.round((1 - +best.price / Math.max(+best.retailPrice, +best.price || 1)) * 100);
    const lowObj = g.cheapestPriceEver && g.cheapestPriceEver.price !== undefined ? g.cheapestPriceEver : null;
    const low = lowObj ? +lowObj.price : null;
    const lowWhen = lowObj && lowObj.date ? new Date(lowObj.date * 1000).toLocaleString('en-US', { month: 'long', year: 'numeric' }) : '';
    const link = (d) => 'https://www.cheapshark.com/redirect?dealID=' + encodeURIComponent(d.dealID);
    const hi = Math.max(...deals.map((d) => +d.retailPrice), +best.price);
    const verdict = low == null ? ['', 'We do not have price history for this game yet.'] : (+best.price <= low * 1.05 ? ['v-good', 'Buy now: this is at or near the lowest price it has ever been.'] : (+best.price <= low * 1.35 ? ['', 'Fair price. It has been as low as ' + $(low) + ', so waiting could save a little.'] : ['v-wait', 'Wait if you can: it has been as low as ' + $(low) + '.']));
    const da = ' data-id="' + esc(id) + '" data-deal="' + esc(best.dealID) + '" data-title="' + esc(title) + '" data-thumb="' + esc(g.info.thumb) + '" data-steam="' + esc(sid) + '" data-store="' + esc(names[best.storeID]) + '" data-price="' + esc(best.price) + '" data-normal="' + esc(best.retailPrice) + '" aria-pressed="false"';
    const rows = deals.map((d) => '<tr><td>' + esc(names[d.storeID]) + '</td><td>' + $(d.price) + '</td><td class="was">' + $(d.retailPrice) + '</td><td><a class="go" href="' + esc(link(d)) + '" target="_blank" rel="noopener sponsored">Buy</a></td></tr>').join('');
    out.innerHTML = '<section class="hero"><div class="wrap"><p class="crumbs"><a href="/">Home</a> / <a href="/games.html">Games</a></p><p class="eyebrow">Compare prices</p><h1>' + esc(title) + '</h1></div></section>' +
      '<section class="block"><div class="wrap"><div class="gp"><img class="cover" src="' + esc(cover) + '" alt="' + esc(title) + ' cover art" width="460" height="215" onerror="this.onerror=null;this.src=\'' + esc(g.info.thumb) + '\'">' +
      '<div class="pricebox"><div class="big">' + $(best.price) + '<s>' + $(best.retailPrice) + '</s></div><p class="fine">Lowest price today at ' + esc(names[best.storeID]) + (off > 0 ? ' · ' + off + '% off' : '') + '</p>' +
      '<div class="stats"><div class="stat now"><small>Now</small><strong>' + $(best.price) + '</strong></div><div class="stat hi"><small>Highest</small><strong>' + $(hi) + '</strong></div><div class="stat lo"><small>Lowest ever</small><strong>' + (low == null ? 'n/a' : $(low)) + '</strong></div></div>' +
      '<div class="verdict ' + verdict[0] + '"><strong>' + (verdict[0] === 'v-good' ? 'Good time to buy' : verdict[0] === 'v-wait' ? 'Consider waiting' : 'Price check') + '</strong><p>' + verdict[1] + (lowWhen && low != null ? ' (Lowest was ' + lowWhen + '.)' : '') + '</p></div>' +
      '<div class="gact" style="border:0;background:none;padding:0"><button type="button" data-wish' + da + '>' + HEART + '<span class="lab">Wishlist</span></button><button type="button" data-cart' + da + '>' + CARTI + '<span class="lab">Add to cart</span></button></div>' +
      '<a class="btn" href="' + esc(link(best)) + '" target="_blank" rel="noopener sponsored">Buy at ' + esc(names[best.storeID]) + ' for ' + $(best.price) + '</a></div></div>' +
      '<h2>Compare stores</h2><table class="stores"><thead><tr><th>Store</th><th>Price</th><th>Usual</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div></section>';
  } catch (e) { fail('Prices unavailable right now'); }
});
</script>
"""


def build():
    return (layout.head("Game prices | SteelGames", "Compare a game's price across official stores and authorized sellers.", f"{SITE}/deal/", '<meta name="robots" content="noindex,follow">\n')
            + layout.header("games")
            + '<main><div id="out"><section class="hero"><div class="wrap"><h1>Loading prices...</h1></div></section></div></main>\n'
            + "<script>const HEART = " + repr(layout.HEART) + ", CARTI = " + repr(layout.CARTI) + ";</script>"
            + SCRIPT + layout.footer())
