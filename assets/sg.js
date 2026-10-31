/* SteelGames shared script: header, wishlist, cart, game cards. No build step, no dependencies. */
(function () {
'use strict';
const CS = 'https://www.cheapshark.com/api/1.0/';
const AMAZON_TAG = 'steelgames-20';
const STORE_COLORS = { 1: '#66C0F4', 2: '#D4B8FF', 3: '#2D9B4B', 7: '#C026D3', 11: '#E0531E', 13: '#4F8EF7', 15: '#FF7A1A',
21: '#0E9F8E', 23: '#D99A00', 25: '#9BA4AF', 27: '#5B3FD9', 28: '#7FD6FF', 30: '#FF4D8D', 35: '#FFB020' };
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const money = (v) => (v == null || isNaN(v)) ? '' : (Number(v) === 0 ? 'Free' : '$' + Number(v).toFixed(2));
const store = {
get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } window.dispatchEvent(new Event('sg:change')); }
};
// ---- CheapShark helpers ----
const cache = new Map();
async function api(path, params) {
const url = CS + path + (params ? '?' + new URLSearchParams(params) : '');
if (cache.has(url)) return cache.get(url);
const p = fetch(url).then((r) => { if (!r.ok) throw new Error('api ' + r.status); return r.json(); });
cache.set(url, p);
p.catch(() => cache.delete(url));
return p;
}
let storeNamesP;
function storeNames() {
if (!storeNamesP) storeNamesP = api('stores').then((l) => Object.fromEntries(l.filter((s) => s.isActive).map((s) => [s.storeID, s.storeName]))).catch(() => ({ 1: 'Steam', 25: 'Epic Games Store', 3: 'GreenManGaming', 7: 'GOG', 11: 'Humble Store', 15: 'Fanatical' }));
return storeNamesP;
}
// One row per game: the cheapest listing.
function dedupe(deals) {
const best = new Map();
deals.forEach((d) => { const b = best.get(d.gameID); if (!b || +d.salePrice < +b.salePrice) best.set(d.gameID, d); });
return [...best.values()];
}
async function lowestEver(ids) {
const out = {};
for (let i = 0; i < ids.length; i += 25) {
try {
const data = await api('games', { ids: ids.slice(i, i + 25).join(',') });
Object.entries(data).forEach(([id, g]) => { out[id] = { low: g.cheapestEver ? +g.cheapestEver.price : null, deals: g.deals || [] }; });
} catch (e) { /* keep going without lowest prices */ }
}
return out;
}
const artUrl = (d) => d.steamAppID ? 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + d.steamAppID + '/header.jpg' : d.thumb;
// ---- wishlist and cart ----
const wishlist = () => store.get('watchlist', []);
const cart = () => store.get('sg_cart', []);
const inWish = (id) => wishlist().some((x) => String(x.id) === String(id));
const inCart = (id) => cart().some((x) => String(x.id) === String(id));
function toggleWish(d) {
let w = wishlist();
if (inWish(d.gameID)) w = w.filter((x) => String(x.id) !== String(d.gameID));
else w.unshift({ id: String(d.gameID), title: d.title, thumb: d.thumb || artUrl(d), art: artUrl(d), price: +d.salePrice });
store.set('watchlist', w.slice(0, 50));
}
function toggleCart(d) {
let c = cart();
if (inCart(d.gameID)) c = c.filter((x) => String(x.id) !== String(d.gameID));
else c.push({ id: String(d.gameID), title: d.title, thumb: d.thumb || artUrl(d), art: artUrl(d), price: +d.salePrice, normal: +d.normalPrice, storeID: String(d.storeID), dealID: d.dealID });
store.set('sg_cart', c.slice(0, 100));
}
// ---- game cards ----
const registry = {};
function card(d, info) {
registry[d.gameID] = d;
const off = Math.round(+d.savings || 0);
const free = +d.salePrice === 0;
const low = info && info.low != null ? Math.min(info.low, +d.salePrice) : null;
const high = Math.max(+d.normalPrice || 0, +d.salePrice);
const color = STORE_COLORS[d.storeID] || '#7B5CFF';
const w = inWish(d.gameID), c = inCart(d.gameID);
return '<article class="gcard" style="--store:' + color + '" data-gid="' + esc(d.gameID) + '">'
+ (free ? '<span class="badge free">FREE</span>' : off > 0 ? '<span class="badge">-' + off + '%</span>' : '')
+ '<a class="art" href="/deal/?id=' + encodeURIComponent(d.gameID) + '"><img src="' + esc(artUrl(d)) + '" data-fallback="' + esc(d.thumb || '') + '" alt="' + esc(d.title) + ' cover art" loading="lazy"></a>'
+ '<div class="body"><h3><a href="/deal/?id=' + encodeURIComponent(d.gameID) + '">' + esc(d.title) + '</a></h3>'
+ '<div class="prices"><div class="now"><span>Now</span><b>' + money(d.salePrice) + '</b></div><div><span>Highest</span><b>' + (high ? money(high) : '-') + '</b></div><div class="low"><span>Lowest</span><b>' + (low != null ? money(low) : '-') + '</b></div></div>'
+ '<div class="store-line">Best at <b data-store="' + esc(d.storeID) + '"></b>' + (d.steamRatingPercent && d.steamRatingPercent !== '0' ? ' · ' + esc(d.steamRatingPercent) + '% positive' : '') + '</div>'
+ '<div class="actions"><button class="btn heart" data-act="wish" data-gid="' + esc(d.gameID) + '" aria-pressed="' + w + '" aria-label="' + (w ? 'Remove from wishlist' : 'Add to wishlist') + '">' + (w ? '♥' : '♡') + '</button>'
+ '<button class="btn btn-primary grow" data-act="cart" data-gid="' + esc(d.gameID) + '">' + (c ? 'In cart ✓' : 'Add to cart') + '</button></div></div></article>';
}
async function fillStoreNames(root) {
const names = await storeNames();
(root || document).querySelectorAll('[data-store]').forEach((el) => { el.textContent = names[el.dataset.store] || 'Store'; });
}
// Renders deals into a container and fills in the lowest-ever prices afterwards.
async function render(el, deals, append) {
const uniq = dedupe(deals);
const html = uniq.map((d) => card(d)).join('');
if (append) el.insertAdjacentHTML('beforeend', html); else el.innerHTML = html;
fillStoreNames(el);
const info = await lowestEver(uniq.map((d) => d.gameID));
uniq.forEach((d) => {
const node = el.querySelector('[data-gid="' + CSS.escape(String(d.gameID)) + '"].gcard');
if (node && info[d.gameID]) { const n = document.createElement('div'); n.innerHTML = card(d, info[d.gameID]); node.replaceWith(n.firstChild); }
});
fillStoreNames(el);
return uniq.length;
}
function refreshButtons() {
document.querySelectorAll('[data-act="wish"]').forEach((b) => { const on = inWish(b.dataset.gid); b.setAttribute('aria-pressed', on); b.textContent = on ? '♥' : '♡'; b.setAttribute('aria-label', on ? 'Remove from wishlist' : 'Add to wishlist'); });
document.querySelectorAll('[data-act="cart"]').forEach((b) => { b.textContent = inCart(b.dataset.gid) ? 'In cart ✓' : 'Add to cart'; });
const set = (id, n) => { const el = document.getElementById(id); if (el) { el.textContent = n; el.classList.toggle('on', n > 0); } };
set('sg-wcount', wishlist().length); set('sg-ccount', cart().length);
}
document.addEventListener('click', (e) => {
const b = e.target.closest('[data-act]'); if (!b) return;
const d = registry[b.dataset.gid]; if (!d) return;
if (b.dataset.act === 'wish') toggleWish(d); else if (b.dataset.act === 'cart') toggleCart(d);
});
document.addEventListener('error', (e) => {
const t = e.target;
if (t && t.tagName === 'IMG' && t.dataset.fallback && t.src !== t.dataset.fallback) t.src = t.dataset.fallback;
}, true);
(window.SG_DEALS || []).forEach((d) => { registry[d.gameID] = d; });
window.addEventListener('sg:change', refreshButtons);
window.addEventListener('storage', refreshButtons);
// ---- header and footer ----
function chrome() {
const here = location.pathname;
const cur = (p) => (here === p || here === p.replace('.html', '')) ? ' aria-current="page"' : '';
const h = document.getElementById('sg-header');
if (h) h.outerHTML = '<header class="sg-header"><div class="wrap"><a class="sg-brand" href="/" aria-label="SteelGames home"><svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 2 28 9v14l-12 7L4 23V9z" fill="#1C2027" stroke="#C3CBD5" stroke-width="2" stroke-linejoin="round"/><path d="M20 11h-6a2.5 2.5 0 0 0 0 5h4a2.5 2.5 0 0 1 0 5h-6" fill="none" stroke="#FF7A1A" stroke-width="2.4" stroke-linecap="round"/></svg>STEELGAMES</a>'
+ '<nav class="sg-nav" aria-label="Site"><a href="/deals/"' + (here.indexOf('/deals') === 0 ? ' aria-current="page"' : '') + '>Deals</a><a href="/games.html"' + cur('/games.html') + '>Games</a><a href="/keys.html"' + cur('/keys.html') + '>Keys &amp; Software</a><a href="/gear.html">Gear</a>'
+ '<a href="/wishlist.html"' + cur('/wishlist.html') + '>♥ Wishlist <span class="count" id="sg-wcount"></span></a><a href="/cart.html"' + cur('/cart.html') + '>Cart <span class="count" id="sg-ccount"></span></a></nav></div></header>';
const f = document.getElementById('sg-footer');
if (f) f.outerHTML = '<footer class="sg-footer"><div class="wrap"><p>SteelGames is a product of Lonestar PPS, LLC, a veteran-owned company.</p><p>Prices come from official stores and key sellers and can change at any time. SteelGames may earn a commission when you buy through our links. As an Amazon Associate, SteelGames earns from qualifying purchases.</p><p><a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a> · <a href="/advertise.html">Advertise</a></p></div></footer>';
refreshButtons();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', chrome); else chrome();
window.SG = { toggleWish, toggleCart, registry, CS, AMAZON_TAG, STORE_COLORS, esc, money, store, api, storeNames, dedupe, lowestEver, artUrl, wishlist, cart, inWish, inCart, card, render, fillStoreNames, refreshButtons };
})();
