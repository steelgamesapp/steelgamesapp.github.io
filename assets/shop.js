hello
world/* SteelGames wishlist + cart. Saved in this browser (shares the app's "watchlist"), with sale alerts when you visit. */
(() => {
  if (window.SG) return;
  const API = 'https://www.cheapshark.com/api/1.0';
  const LS = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage blocked */ } },
  };
  const money = (v) => (v == null || isNaN(v)) ? '' : (+v === 0 ? 'Free' : '$' + (+v).toFixed(2));
  const SG = window.SG = { API, LS, money };

  SG.wishlist = () => LS.get('watchlist', []);
  SG.cart = () => LS.get('sg_cart', []);
  const emit = () => { document.dispatchEvent(new CustomEvent('sg:change')); };
  SG.inWish = (id) => SG.wishlist().some((w) => String(w.id) === String(id));
  SG.inCart = (id) => SG.cart().some((c) => String(c.id) === String(id));
  SG.toggleWish = (it) => {
    let w = SG.wishlist(); const on = w.some((x) => String(x.id) === String(it.id));
    if (on) w = w.filter((x) => String(x.id) !== String(it.id));
    else w.unshift({ id: String(it.id), title: it.title, thumb: it.thumb || '', steam: it.steam || '', price: it.price != null && it.price !== '' ? +it.price : null });
    LS.set('watchlist', w.slice(0, 100)); emit(); return !on;
  };
  SG.setTarget = (id, v) => { const w = SG.wishlist(); const it = w.find((x) => String(x.id) === String(id)); if (!it) return; if (v > 0) it.target = v; else delete it.target; delete it.alerted; LS.set('watchlist', w); emit(); };
  SG.addCart = (it) => {
    const c = SG.cart(); if (c.some((x) => String(x.id) === String(it.id))) return false;
    c.push({ id: String(it.id), deal: it.deal || '', title: it.title, thumb: it.thumb || '', steam: it.steam || '', store: it.store || 'Store', price: +it.price || 0, normal: +it.normal || +it.price || 0 });
    LS.set('sg_cart', c.slice(0, 100)); emit(); return true;
  };
  SG.removeCart = (id) => { LS.set('sg_cart', SG.cart().filter((x) => String(x.id) !== String(id))); emit(); };
  SG.art = (it) => (it.steam && it.steam !== '0') ? 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + it.steam + '/header.jpg' : it.thumb;

  /* ---------- styles for the header icons and toast ---------- */
  const css = document.createElement('style');
  css.textContent = '.nav a.nav-ico{display:inline-flex;align-items:center;gap:6px;position:relative}.nav a.nav-ico svg{display:block}.nav-ico .cnt{min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:#FF2E93;color:#fff;font:700 11px/18px Inter,system-ui,sans-serif;text-align:center}.nav-ico .cnt[hidden]{display:none}' +
    '.sg-toast{position:fixed;left:50%;bottom:22px;transform:translate(-50%,20px);opacity:0;z-index:99;max-width:min(92vw,460px);padding:12px 18px;border-radius:12px;background:#2A1C6B;border:1px solid #4A37A8;color:#fff;font:600 15px Inter,system-ui,sans-serif;box-shadow:0 10px 30px rgba(0,0,0,.45);transition:opacity .2s,transform .2s;display:flex;gap:12px;align-items:center}.sg-toast.on{opacity:1;transform:translate(-50%,0)}.sg-toast a{color:#FFCB5C;white-space:nowrap}@media (prefers-reduced-motion:reduce){.sg-toast{transition:none}}';
  document.head.appendChild(css);
  let tt, toastEl;
  SG.toast = (msg, href, label) => {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'sg-toast'; toastEl.setAttribute('role', 'status'); document.body.appendChild(toastEl); }
    toastEl.innerHTML = '<span></span>' + (href ? '<a href="' + href + '">' + label + '</a>' : '');
    toastEl.firstChild.textContent = msg; toastEl.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => toastEl.classList.remove('on'), 4200);
  };

  /* ---------- header icons ---------- */
  const HEART = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.6-9.3-9A5.4 5.4 0 0 1 12 6.6 5.4 5.4 0 0 1 21.3 12C19 16.4 12 21 12 21z"/></svg>';
  const CART = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 12.2a1 1 0 0 0 1 .8h9.1a1 1 0 0 0 1-.8L21 7H6"/></svg>';
  const counts = () => {
    const w = SG.wishlist().length, c = SG.cart().length;
    document.querySelectorAll('[data-count="wish"]').forEach((e) => { e.textContent = w; e.hidden = !w; });
    document.querySelectorAll('[data-count="cart"]').forEach((e) => { e.textContent = c; e.hidden = !c; });
  };
  const nav = () => {
    const n = document.querySelector('.nav'); if (!n || n.querySelector('.nav-ico')) return;
    const cta = n.querySelector('.nav-cta');
    const mk = (href, icon, label, key) => { const a = document.createElement('a'); a.className = 'nav-ico'; a.href = href; a.setAttribute('aria-label', label); a.innerHTML = icon + '<span class="cnt" data-count="' + key + '" hidden>0</span>'; return a; };
    const a1 = mk('/wishlist.html', HEART, 'Wishlist', 'wish'), a2 = mk('/cart.html', CART, 'Cart', 'cart');
    if (cta) { n.insertBefore(a1, cta); n.insertBefore(a2, cta); } else { n.appendChild(a1); n.appendChild(a2); }
    if (location.pathname.startsWith('/wishlist')) a1.setAttribute('aria-current', 'page');
    if (location.pathname.startsWith('/cart')) a2.setAttribute('aria-current', 'page');
    counts();
  };

  /* ---------- buttons on cards: data-wish / data-cart ---------- */
  const itemOf = (b) => ({ id: b.dataset.id, deal: b.dataset.deal, title: b.dataset.title, thumb: b.dataset.thumb, steam: b.dataset.steam, store: b.dataset.store, price: b.dataset.price, normal: b.dataset.normal });
  const sync = () => {
    document.querySelectorAll('[data-wish]').forEach((b) => {
      const on = SG.inWish(b.dataset.id); b.setAttribute('aria-pressed', on);
      const lab = b.querySelector('.lab'); if (lab) lab.textContent = on ? 'Wishlisted' : 'Wishlist';
      b.setAttribute('aria-label', (on ? 'Remove from wishlist: ' : 'Add to wishlist: ') + (b.dataset.title || ''));
    });
    document.querySelectorAll('[data-cart]').forEach((b) => {
      const on = SG.inCart(b.dataset.id); b.setAttribute('aria-pressed', on);
      const lab = b.querySelector('.lab'); if (lab) lab.textContent = on ? 'In cart' : 'Add to cart';
    });
    counts();
  };
  document.addEventListener('click', (e) => {
    const w = e.target.closest('[data-wish]'), c = e.target.closest('[data-cart]');
    if (w) { e.preventDefault(); const on = SG.toggleWish(itemOf(w)); SG.toast(on ? 'Added to your wishlist. We flag it when the price drops.' : 'Removed from your wishlist.', on ? '/wishlist.html' : '', 'View'); }
    else if (c) {
      e.preventDefault(); if (SG.inCart(c.dataset.id)) { location.href = '/cart.html'; return; }
      SG.addCart(itemOf(c)); SG.toast('Added to your cart.', '/cart.html', 'View cart');
    }
  });
  document.addEventListener('sg:change', sync);
  let mo; new MutationObserver(() => { clearTimeout(mo); mo = setTimeout(sync, 60); }).observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener('storage', sync);

  /* ---------- live price check for the wishlist ---------- */
  SG.checkPrices = async () => {
    const w = SG.wishlist(); const out = {};
    for (let i = 0; i < w.length; i += 25) {
      const ids = w.slice(i, i + 25).map((g) => encodeURIComponent(g.id)).join(',');
      try {
        const j = await (await fetch(API + '/games?ids=' + ids)).json();
        Object.keys(j).forEach((id) => {
          const deals = (j[id].deals || []).slice().sort((a, b) => +a.price - +b.price); if (!deals.length) return;
          out[id] = { now: +deals[0].price, normal: +deals[0].retailPrice, deal: deals[0].dealID, storeID: deals[0].storeID, low: j[id].cheapestPriceEver ? +j[id].cheapestPriceEver.price : null, steam: j[id].info && j[id].info.steamAppID, title: j[id].info && j[id].info.title };
        });
      } catch (e) { /* API busy: try again next visit */ }
    }
    return out;
  };
  SG.hits = (w, live) => w.filter((g) => { const p = live[g.id]; if (!p) return false; const hit = (g.target && p.now <= g.target) || (g.price != null && p.now <= g.price - 0.5); return hit; });
  const alertCheck = async () => {
    const w = SG.wishlist(); if (!w.length || location.pathname.startsWith('/wishlist')) return;
    const last = LS.get('sg_lastcheck', 0); if (Date.now() - last < 30 * 60 * 1000) return;
    LS.set('sg_lastcheck', Date.now());
    const live = await SG.checkPrices(); const fresh = SG.hits(w, live).filter((g) => g.alerted == null || live[g.id].now < g.alerted);
    if (!fresh.length) return;
    const all = SG.wishlist(); fresh.forEach((g) => { const it = all.find((x) => x.id === g.id); if (it) it.alerted = live[g.id].now; }); LS.set('watchlist', all);
    const msg = fresh.length === 1 ? fresh[0].title + ' is cheaper now: ' + money(live[fresh[0].id].now) : fresh.length + ' games on your wishlist are cheaper now';
    SG.toast(msg, '/wishlist.html', 'See deals');
    try { if ('Notification' in window && Notification.permission === 'granted') new Notification('Price drop on SteelGames', { body: msg, icon: '/app/icons/icon-192.png' }); } catch (e) { /* not supported */ }
  };

  const start = () => { nav(); sync(); setTimeout(alertCheck, 1500); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
