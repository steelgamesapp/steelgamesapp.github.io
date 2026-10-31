"""Builds /wishlist.html and /cart.html (saved in the visitor's browser)."""
import layout

SITE = layout.SITE
HEART = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.6-9.3-9A5.4 5.4 0 0 1 12 6.6 5.4 5.4 0 0 1 21.3 12C19 16.4 12 21 12 21z"/></svg>'

COMMON = r"""
const $ = (s) => document.querySelector(s);
const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const money = SG.money;
const SC = { 'Steam': '#66C0F4', 'GreenManGaming': '#5CE08A', 'Fanatical': '#FF8A3D', 'GOG': '#B388FF', 'Epic Games Store': '#E8E8F0', 'Humble Store': '#FF5A5F', 'GameBillet': '#FFD43B', 'Gamesplanet': '#4DD0E1', 'GamersGate': '#FF7043', 'Voidu': '#F06292', 'IndieGala': '#FF5252', 'WinGameStore': '#4FC3F7' };
const buy = (deal, id) => deal ? 'https://www.cheapshark.com/redirect?dealID=' + encodeURIComponent(deal) : '/deal/?id=' + encodeURIComponent(id);
"""

SYNC_BOX = """<details class="syncbox" id="syncbox"><summary>Sync and backup</summary>
<p class="fine">Move your wishlist and collection to another phone or computer, or keep a backup. No account needed.</p>
<div class="chips"><button type="button" id="s-export">Download backup</button><label class="filebtn">Restore from backup<input type="file" id="s-file" accept="application/json,.json" hidden></label><button type="button" id="s-link">Copy sync link</button></div>
<p class="fine" id="s-msg" role="status" aria-live="polite"></p>
<div class="steamimp" id="steamimp" hidden><h3>Import from Steam</h3><p class="fine">Your Steam profile needs to be public. Type your profile name or 17-digit Steam ID.</p>
<div class="row"><input id="s-prof" type="text" placeholder="Steam profile name or ID" autocomplete="off"><button type="button" class="btn" id="s-wl">Import wishlist</button><button type="button" class="btn btn-ghost" id="s-own">Import owned games</button></div></div>
</details>
<script>document.addEventListener('DOMContentLoaded', () => {
const $ = (s) => document.querySelector(s), msg = (t) => { $('#s-msg').textContent = t; };
$('#s-export').addEventListener('click', () => { SG.download('steelgames-backup-' + new Date().toISOString().slice(0, 10) + '.json', JSON.stringify(SG.exportData(), null, 2)); msg('Backup downloaded.'); });
$('#s-file').addEventListener('change', async (e) => { const f = e.target.files[0]; if (!f) return; try { const r = SG.importData(JSON.parse(await f.text())); msg('Restored. You now have ' + r.wishlist + ' wishlisted and ' + r.collection + ' owned games.'); } catch (x) { msg(x.message || 'That file could not be read.'); } e.target.value = ''; });
$('#s-link').addEventListener('click', async () => { const u = SG.syncLink(); try { await navigator.clipboard.writeText(u); msg('Link copied. Open it on your other device to bring your lists over.'); } catch (x) { window.prompt('Copy this link:', u); } });
if (SG.STEAM_PROXY) { $('#steamimp').hidden = false;
  const run = async (kind) => { const p = $('#s-prof').value.trim(); if (!p) { msg('Enter your Steam profile name or ID first.'); return; } msg('Reading your Steam profile...');
    try { const found = await SG.steamImport(p, kind, (i, n) => msg('Matching games ' + i + ' of ' + n + '...')); const r = SG.addImported(found, kind); msg('Imported ' + found.length + ' games. You now have ' + r.wishlist + ' wishlisted and ' + r.collection + ' owned.'); } catch (x) { msg(x.message); } };
  $('#s-wl').addEventListener('click', () => run('wishlist')); $('#s-own').addEventListener('click', () => run('owned')); }
});</script>"""

WISH_JS = COMMON + r"""
const list = $('#list'), bar = $('#bar'); let live = {}, names = {};
const draw = () => {
  const w = SG.wishlist();
  if (!w.length) { list.innerHTML = '<div class="empty"><p style="font-size:18px;color:#fff;margin-bottom:6px">Your wishlist is empty</p><p>Tap the heart on any game and we will flag it here when the price drops.</p><p style="margin-top:14px"><a class="btn" href="/games.html">Browse games</a></p></div>'; bar.hidden = true; return; }
  bar.hidden = false;
  list.innerHTML = w.map((g) => {
    const p = live[g.id], now = p ? p.now : null, hit = p && ((g.target && now <= g.target) || (g.price != null && now <= g.price - 0.5));
    const isLow = p && p.low != null && now <= p.low;
    const img = SG.art({ steam: g.steam || (p && p.steam), thumb: g.thumb });
    const store = p ? (names[p.storeID] || 'Store') : '';
    const pills = (hit ? '<span class="pill hot">Price drop</span>' : '') + (isLow ? '<span class="pill good">Lowest ever</span>' : '') + (g.target && p && now <= g.target ? '<span class="pill good">Hit your target</span>' : '');
    return '<article class="lrow" style="--store:' + (SC[store] || '#7B5CFF') + '"><a class="pic" href="/deal/?id=' + encodeURIComponent(g.id) + '"><img src="' + esc(img) + '" alt="" loading="lazy" onerror="this.onerror=null;this.src=\'' + esc(g.thumb) + '\'"></a>' +
      '<div class="main"><h3>' + esc(g.title) + '</h3><div class="pills">' + pills + '</div>' +
      '<div class="stats"><div class="stat now"><small>Now' + (store ? ' at ' + esc(store) : '') + '</small><strong>' + (p ? money(now) : '...') + '</strong></div><div class="stat hi"><small>Highest</small><strong>' + (p && p.normal ? money(Math.max(p.normal, now)) : '...') + '</strong></div><div class="stat lo"><small>Lowest ever</small><strong>' + (p && p.low != null ? money(p.low) : '...') + '</strong></div></div>' +
      '<label class="target">Alert me at or below $<input type="number" min="0" step="0.01" inputmode="decimal" value="' + (g.target || '') + '" data-target="' + esc(g.id) + '" placeholder="' + (p ? Math.max(1, Math.floor(now * 0.8)) : '10') + '"></label></div>' +
      '<div class="side">' + (p ? '<button type="button" class="primary" data-addcart="' + esc(g.id) + '">' + (SG.inCart(g.id) ? 'In cart' : 'Add to cart') + '</button><a href="' + esc(buy(p.deal, g.id)) + '" target="_blank" rel="noopener sponsored">Buy now</a>' : '') + '<button type="button" class="danger" data-remove="' + esc(g.id) + '">Remove</button></div></article>';
  }).join('');
  const n = SG.hits(w, live).length;
  $('#hitcount').textContent = n ? n + (n === 1 ? ' game is' : ' games are') + ' cheaper right now.' : 'No price drops yet. We check every time you open SteelGames.';
};
const refresh = async () => {
  try { names = Object.fromEntries((await (await fetch(SG.API + '/stores')).json()).map((s) => [s.storeID, s.storeName])); } catch (e) {}
  live = await SG.checkPrices(); draw();
};
document.addEventListener('click', (e) => {
  const r = e.target.closest('[data-remove]'), a = e.target.closest('[data-addcart]');
  if (r) { const id = r.dataset.remove; const w = SG.wishlist().filter((x) => x.id !== id); SG.LS.set('watchlist', w); document.dispatchEvent(new CustomEvent('sg:change')); draw(); }
  if (a) { const g = SG.wishlist().find((x) => x.id === a.dataset.addcart), p = live[a.dataset.addcart]; if (g && p) { SG.addCart({ id: g.id, deal: p.deal, title: g.title, thumb: g.thumb, steam: g.steam || p.steam, store: names[p.storeID], price: p.now, normal: p.normal }); SG.toast('Added to your cart.', '/cart.html', 'View cart'); draw(); } }
});
document.addEventListener('change', (e) => { const t = e.target.closest('[data-target]'); if (t) { SG.setTarget(t.dataset.target, parseFloat(t.value)); SG.toast(t.value > 0 ? 'Alert set at $' + (+t.value).toFixed(2) + '.' : 'Alert removed.'); draw(); } });
const nb = $('#notify');
const syncNotify = () => { if (!('Notification' in window)) { nb.hidden = true; return; } nb.textContent = Notification.permission === 'granted' ? 'Browser alerts are on' : 'Turn on browser alerts'; nb.disabled = Notification.permission === 'granted' || Notification.permission === 'denied'; if (Notification.permission === 'denied') nb.textContent = 'Browser alerts are blocked'; };
nb.addEventListener('click', async () => { try { await Notification.requestPermission(); } catch (e) {} syncNotify(); });
syncNotify(); draw(); refresh();
"""

CART_JS = COMMON + r"""
const list = $('#list'), sum = $('#sum');
const draw = () => {
  const c = SG.cart();
  if (!c.length) { list.innerHTML = '<div class="empty"><p style="font-size:18px;color:#fff;margin-bottom:6px">Your cart is empty</p><p>Add games from any list and compare your total here.</p><p style="margin-top:14px"><a class="btn" href="/games.html">Browse games</a></p></div>'; sum.hidden = true; return; }
  sum.hidden = false;
  const groups = {}; c.forEach((x) => { (groups[x.store] = groups[x.store] || []).push(x); });
  list.innerHTML = Object.keys(groups).map((s) => {
    const items = groups[s], sub = items.reduce((a, x) => a + x.price, 0);
    return '<section class="rows" style="--store:' + (SC[s] || '#7B5CFF') + '"><h3 class="group-h"><i></i>' + esc(s) + '<span>' + items.length + (items.length === 1 ? ' game' : ' games') + ' · ' + money(sub) + '</span></h3>' + items.map((x) => {
      const off = x.normal > x.price ? Math.round((1 - x.price / x.normal) * 100) : 0;
      return '<article class="lrow"><a class="pic" href="/deal/?id=' + encodeURIComponent(x.id) + '"><img src="' + esc(SG.art(x)) + '" alt="" loading="lazy" onerror="this.onerror=null;this.src=\'' + esc(x.thumb) + '\'"></a>' +
        '<div class="main"><h3>' + esc(x.title) + '</h3><div class="pills">' + (off ? '<span class="pill hot">-' + off + '%</span>' : '') + '<span class="pill">' + esc(x.store) + '</span></div>' +
        '<div class="stats"><div class="stat now"><small>Price</small><strong>' + money(x.price) + '</strong></div><div class="stat hi"><small>Highest</small><strong>' + money(Math.max(x.normal, x.price)) + '</strong></div><div class="stat lo"><small>You save</small><strong>' + money(Math.max(0, x.normal - x.price)) + '</strong></div></div></div>' +
        '<div class="side"><a class="primary" href="' + esc(buy(x.deal, x.id)) + '" target="_blank" rel="noopener sponsored">Buy at ' + esc(x.store) + '</a><button type="button" data-wish2="' + esc(x.id) + '">Move to wishlist</button><button type="button" class="danger" data-rm="' + esc(x.id) + '">Remove</button></div></article>';
    }).join('') + '</section>';
  }).join('');
  const total = c.reduce((a, x) => a + x.price, 0), reg = c.reduce((a, x) => a + Math.max(x.normal, x.price), 0);
  $('#n').textContent = c.length; $('#reg').textContent = money(reg); $('#tot').textContent = money(total); $('#sav').textContent = money(Math.max(0, reg - total));
};
document.addEventListener('click', (e) => {
  const r = e.target.closest('[data-rm]'), m = e.target.closest('[data-wish2]');
  if (r) { SG.removeCart(r.dataset.rm); draw(); }
  if (m) { const x = SG.cart().find((i) => i.id === m.dataset.wish2); if (x) { if (!SG.inWish(x.id)) SG.toggleWish({ id: x.id, title: x.title, thumb: x.thumb, steam: x.steam, price: x.price }); SG.removeCart(x.id); SG.toast('Moved to your wishlist.', '/wishlist.html', 'View'); draw(); } }
});
$('#clear').addEventListener('click', () => { SG.LS.set('sg_cart', []); document.dispatchEvent(new CustomEvent('sg:change')); draw(); });
draw();
"""


def wishlist():
    return (layout.head("Your Wishlist | SteelGames", "Save games to your SteelGames wishlist and see when their price drops.", f"{SITE}/wishlist.html", '<meta name="robots" content="noindex,follow">\n')
            + layout.header()
            + """<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Saved on this device</p>
<h1>Your wishlist</h1>
<p class="lede">Save games you want and set a target price. We check prices each time you open SteelGames and flag every drop.</p>
<div class="chips"><a href="/wishlist.html" aria-current="page">Wishlist</a><a href="/collection.html">My collection</a></div>
</div></section>
<section class="block"><div class="wrap">
<div class="notice alertbar" id="bar"><span id="hitcount"></span><button type="button" class="btn btn-ghost" id="notify">Turn on browser alerts</button></div>
<div class="rows" id="list" aria-live="polite"></div>
<p class="fine">Your wishlist is saved in this browser and shared with the SteelGames app on this device. Alerts appear when you visit; browser alerts need permission.</p>
""" + SYNC_BOX + """</div></section>
</main>
<script>document.addEventListener('DOMContentLoaded', () => {""" + WISH_JS + """});</script>
""" + layout.footer())


def cart():
    return (layout.head("Your Cart | SteelGames", "Compare your total across stores and buy each game at the store with the best price.", f"{SITE}/cart.html", '<meta name="robots" content="noindex,follow">\n')
            + layout.header()
            + """<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Saved on this device</p>
<h1>Your cart</h1>
<p class="lede">Line up the games you plan to buy, see your total and what you save, then check out at each store.</p>
</div></section>
<section class="block"><div class="wrap"><div class="cols">
<div class="rows" id="list" aria-live="polite"></div>
<aside class="summary" id="sum" hidden>
<h2 style="font-size:20px">Order summary</h2>
<div class="line"><span>Games</span><span id="n">0</span></div>
<div class="line"><span>Usual price</span><span id="reg"></span></div>
<div class="line save"><span>You save</span><span id="sav"></span></div>
<div class="line"><span>Total</span><span class="total" id="tot"></span></div>
<p class="fine">Each game is bought on the store's own site, so you pay the store directly. SteelGames never takes payment. Prices can change at any time.</p>
<button type="button" class="btn btn-ghost" id="clear">Clear cart</button>
</aside>
</div></div></section>
</main>
<script>document.addEventListener('DOMContentLoaded', () => {""" + CART_JS + """});</script>
""" + layout.footer())


COLL_JS = COMMON + r"""
const list = $('#list');
const draw = () => {
  const c = SG.collection();
  $('#cn').textContent = c.length ? c.length + (c.length === 1 ? ' game' : ' games') : '';
  if (!c.length) { list.innerHTML = '<div class="empty"><p style="font-size:18px;color:#fff;margin-bottom:6px">Your collection is empty</p><p>Tap "I own this" on a game page to track what you already have. Owned games drop off your wishlist and cart.</p><p style="margin-top:14px"><a class="btn" href="/games.html">Browse games</a></p></div>'; return; }
  list.innerHTML = c.map((g) => '<article class="lrow"><a class="pic" href="/deal/?id=' + encodeURIComponent(g.id) + '"><img src="' + esc(SG.art(g)) + '" alt="" loading="lazy" onerror="this.onerror=null;this.src=\'' + esc(g.thumb) + '\'"></a>' +
    '<div class="main"><h3>' + esc(g.title) + '</h3><div class="pills"><span class="pill good">Owned</span>' + (g.added ? '<span class="pill">Added ' + esc(g.added) + '</span>' : '') + '</div></div>' +
    '<div class="side"><button type="button" class="danger" data-un="' + esc(g.id) + '">Remove</button></div></article>').join('');
};
document.addEventListener('click', (e) => { const r = e.target.closest('[data-un]'); if (r) { SG.LS.set('sg_owned', SG.collection().filter((x) => String(x.id) !== r.dataset.un)); document.dispatchEvent(new CustomEvent('sg:change')); draw(); } });
document.addEventListener('sg:change', draw);
draw();
"""


def collection():
    return (layout.head("Your Collection | SteelGames", "Track the PC games you already own so your wishlist and deal alerts only show what you still want.", f"{SITE}/collection.html", '<meta name="robots" content="noindex,follow">\n')
            + layout.header()
            + """<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Saved on this device</p>
<h1>My collection <span class="fine" id="cn"></span></h1>
<p class="lede">The games you already own. Mark a game as owned and it leaves your wishlist and cart, so alerts only cover what you still want.</p>
<div class="chips"><a href="/wishlist.html">Wishlist</a><a href="/collection.html" aria-current="page">My collection</a></div>
</div></section>
<section class="block"><div class="wrap">
<div class="rows" id="list" aria-live="polite"></div>
""" + SYNC_BOX + """</div></section>
</main>
<script>document.addEventListener('DOMContentLoaded', () => {""" + COLL_JS + """});</script>
""" + layout.footer())


def sync():
    return (layout.head("Import your lists | SteelGames", "Bring your SteelGames wishlist and collection to this device.", f"{SITE}/sync.html", '<meta name="robots" content="noindex,nofollow">\n')
            + layout.header()
            + """<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Sync</p>
<h1>Import your lists</h1>
<p class="lede" id="lede">Checking your link...</p>
<div class="chips" id="acts"></div>
</div></section>
</main>
<script>document.addEventListener('DOMContentLoaded', () => {
const d = SG.readSyncHash(), lede = document.getElementById('lede'), acts = document.getElementById('acts');
if (!d || (!(d.wishlist || []).length && !(d.collection || []).length)) { lede.textContent = 'This link has no lists in it. Copy a fresh sync link from your wishlist page on your other device.'; return; }
lede.textContent = 'This link has ' + (d.wishlist || []).length + ' wishlisted and ' + (d.collection || []).length + ' owned games. They will be merged with what you already have on this device.';
const b = document.createElement('button'); b.type = 'button'; b.className = 'btn'; b.textContent = 'Import now';
b.addEventListener('click', () => { try { const r = SG.importData(d); lede.textContent = 'Done. You now have ' + r.wishlist + ' wishlisted and ' + r.collection + ' owned games.'; acts.innerHTML = '<a href="/wishlist.html">Open wishlist</a><a href="/collection.html">Open collection</a>'; history.replaceState(null, '', location.pathname); } catch (x) { lede.textContent = x.message; } });
acts.appendChild(b);
});</script>
""" + layout.footer())
