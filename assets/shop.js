/* SteelGames wishlist + cart. Saved in this browser (shares the app's "watchlist"), with sale alerts when you visit. */
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
  const SEARCH_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';
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
    const a0 = document.createElement('a'); a0.className = 'nav-ico nav-search'; a0.href = '/games.html'; a0.setAttribute('aria-label', 'Search games'); a0.setAttribute('aria-expanded', 'false'); a0.innerHTML = SEARCH_ICON;
    a0.addEventListener('click', (e) => { e.preventDefault(); SG.openSearch(); });
    if (cta) { n.insertBefore(a0, cta); n.insertBefore(a1, cta); n.insertBefore(a2, cta); } else { n.appendChild(a0); n.appendChild(a1); n.appendChild(a2); }
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
    document.querySelectorAll('[data-own]').forEach((b) => {
      const on = SG.inOwned(b.dataset.id); b.setAttribute('aria-pressed', on);
      const lab = b.querySelector('.lab'); if (lab) lab.textContent = on ? 'Owned' : 'I own this';
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

  /* ---------- collection (games you own) ---------- */
  SG.collection = () => LS.get('sg_owned', []);
  SG.inOwned = (id) => SG.collection().some((x) => String(x.id) === String(id));
  SG.toggleOwned = (it) => {
    let c = SG.collection(); const on = c.some((x) => String(x.id) === String(it.id));
    if (on) c = c.filter((x) => String(x.id) !== String(it.id));
    else {
      c.unshift({ id: String(it.id), title: it.title, thumb: it.thumb || '', steam: it.steam || '', added: new Date().toISOString().slice(0, 10) });
      LS.set('watchlist', SG.wishlist().filter((x) => String(x.id) !== String(it.id)));
      LS.set('sg_cart', SG.cart().filter((x) => String(x.id) !== String(it.id)));
    }
    LS.set('sg_owned', c.slice(0, 1000)); emit(); return !on;
  };

  /* ---------- sync and backup (no account needed) ---------- */
  const uniq = (arr) => { const seen = new Set(); return arr.filter((x) => x && x.id != null && !seen.has(String(x.id)) && seen.add(String(x.id))); };
  const clean = (x, keys) => { const o = { id: String(x.id) }; keys.forEach((k) => { if (x[k] != null && x[k] !== '') o[k] = x[k]; }); o.title = String(x.title || 'Game').slice(0, 160); return o; };
  SG.exportData = () => ({ app: 'SteelGames', v: 1, exported: new Date().toISOString(), wishlist: SG.wishlist(), collection: SG.collection() });
  SG.importData = (d) => {
    if (!d || typeof d !== 'object') throw new Error('Not a SteelGames backup.');
    const w = Array.isArray(d.wishlist) ? d.wishlist : [], c = Array.isArray(d.collection) ? d.collection : [];
    if (!w.length && !c.length) throw new Error('That backup has no games in it.');
    const owned = uniq(c.map((x) => clean(x, ['thumb', 'steam', 'added'])).concat(SG.collection()));
    const ownedIds = new Set(owned.map((x) => x.id));
    const local = SG.wishlist(), localById = Object.fromEntries(local.map((x) => [x.id, x]));
    const wish = uniq(local.concat(w.map((x) => Object.assign(clean(x, ['thumb', 'steam', 'price', 'target']), localById[String(x.id)] || {})))).filter((x) => !ownedIds.has(x.id));
    LS.set('sg_owned', owned.slice(0, 1000)); LS.set('watchlist', wish.slice(0, 100)); emit();
    return { wishlist: wish.length, collection: owned.length };
  };
  const b64 = (s) => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const unb64 = (s) => decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/'))));
  SG.syncLink = () => {
    const d = { wishlist: SG.wishlist().map((x) => clean(x, ['steam', 'price', 'target'])), collection: SG.collection().map((x) => clean(x, ['steam', 'added'])) };
    return location.origin + '/sync.html#d=' + b64(JSON.stringify(d));
  };
  SG.readSyncHash = () => { const m = /[#&]d=([^&]+)/.exec(location.hash); if (!m) return null; try { return JSON.parse(unb64(m[1])); } catch (e) { return null; } };
  SG.download = (name, text) => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); };

  /* Steam import. Needs the small proxy in /worker (Steam blocks direct browser calls). Leave empty until it is deployed. */
  SG.STEAM_PROXY = 'https://steelgames-steam.steelgames.workers.dev';
  SG.STEAM_OWNED = false; /* set true after adding a STEAM_API_KEY secret to the Worker */
  SG.steamImport = async (profile, kind, onStep) => {
    if (!SG.STEAM_PROXY) throw new Error('Steam import is not switched on yet.');
    const r = await fetch(SG.STEAM_PROXY + '?kind=' + encodeURIComponent(kind) + '&profile=' + encodeURIComponent(profile));
    const j = await r.json(); if (!r.ok || j.error) throw new Error(j.error || 'Steam did not answer.');
    const apps = (j.appids || []).slice(0, kind === 'wishlist' ? 100 : 400), found = [];
    for (let i = 0; i < apps.length; i++) {
      if (onStep) onStep(i + 1, apps.length);
      try {
        const g = (await (await fetch(SG.API + '/games?steamAppID=' + apps[i])).json())[0];
        if (g) found.push({ id: String(g.gameID), title: g.external, thumb: g.thumb || '', steam: String(apps[i]), price: g.cheapest != null ? +g.cheapest : null });
      } catch (e) { /* skip this one */ }
      await new Promise((ok) => setTimeout(ok, 120));
    }
    return found;
  };
  SG.addImported = (found, kind) => {
    if (kind === 'owned') return SG.importData({ collection: found });
    return SG.importData({ wishlist: found });
  };

  document.addEventListener('click', (e) => {
    const o = e.target.closest('[data-own]'); if (!o) return;
    e.preventDefault(); const on = SG.toggleOwned(itemOf(o));
    SG.toast(on ? 'Added to your collection.' : 'Removed from your collection.', on ? '/collection.html' : '', 'View');
  });

  /* ---------- site-wide game search ---------- */
  const sstyle = document.createElement('style');
  sstyle.textContent = '.sg-search{position:relative;background:rgba(28,16,80,.98);border-bottom:1px solid #4A37A8;z-index:60}.sg-search[hidden]{display:none}.sg-search .box{max-width:1080px;margin:0 auto;padding:12px 16px;position:relative}' +
    '.sg-search input{width:100%;min-height:48px;padding:0 16px;border-radius:12px;border:1px solid #4A37A8;background:#120A2B;color:#fff;font:17px Inter,system-ui,sans-serif}.sg-search input:focus-visible{outline:2px solid #FFB020;outline-offset:2px}' +
    '.sg-res{list-style:none;margin:8px 0 0;padding:0;border-radius:12px;background:#1E1450;border:1px solid #3B2B8A;overflow:hidden;max-height:min(60vh,440px);overflow-y:auto}.sg-res:empty{display:none}' +
    '.sg-res li a,.sg-res li.msg{display:flex;align-items:center;gap:12px;padding:10px 12px;color:#fff;text-decoration:none;font:600 15px Inter,system-ui,sans-serif}.sg-res li.msg{color:#BDB4EA;font-weight:500}' +
    '.sg-res li a:hover,.sg-res li a[aria-selected="true"]{background:#2A1C6B}.sg-res img{width:92px;height:43px;object-fit:cover;border-radius:6px;background:#0E0820;flex:none}.sg-res .t{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.sg-res .p{color:#FFCB5C;font-weight:700;white-space:nowrap}' +
    '@media (max-width:480px){.sg-res img{width:64px;height:30px}}';
  document.head.appendChild(sstyle);
  let sbar, sinput, slist, stoken = 0, stimer, sactive = -1, tracked = null;
  const loadTracked = () => { if (tracked) return; tracked = {}; fetch('/game/tracked.json').then((r) => r.json()).then((j) => { tracked = j || {}; }).catch(() => {}); };
  const sbuild = () => {
    if (sbar) return;
    const header = document.querySelector('.site-header'); if (!header) return;
    sbar = document.createElement('div'); sbar.className = 'sg-search'; sbar.hidden = true; sbar.setAttribute('role', 'search');
    sbar.innerHTML = '<div class="box"><input type="search" id="sg-q" placeholder="Search any game, like Elden Ring" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="sg-res" aria-label="Search games"><ul class="sg-res" id="sg-res" role="listbox" aria-live="polite"></ul></div>';
    header.insertAdjacentElement('afterend', sbar);
    sinput = sbar.querySelector('input'); slist = sbar.querySelector('ul');
    sinput.addEventListener('input', () => { clearTimeout(stimer); stimer = setTimeout(sfind, 250); });
    sinput.addEventListener('keydown', (e) => {
      const items = [...slist.querySelectorAll('a')];
      if (e.key === 'Escape') { SG.closeSearch(); return; }
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { if (!items.length) return; e.preventDefault(); sactive = (sactive + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length; items.forEach((a, i) => a.setAttribute('aria-selected', i === sactive)); items[sactive].scrollIntoView({ block: 'nearest' }); }
      if (e.key === 'Enter') { const a = items[sactive >= 0 ? sactive : 0]; if (a) { e.preventDefault(); location.href = a.href; } }
    });
    document.addEventListener('click', (e) => { if (sbar && !sbar.hidden && !e.target.closest('.sg-search') && !e.target.closest('.nav-search')) SG.closeSearch(); });
  };
  const sfind = async () => {
    const q = sinput.value.trim(), tok = ++stoken; sactive = -1;
    if (q.length < 2) { slist.innerHTML = ''; sinput.setAttribute('aria-expanded', 'false'); return; }
    slist.innerHTML = '<li class="msg">Searching...</li>';
    try {
      const list = await (await fetch(API + '/games?limit=8&title=' + encodeURIComponent(q))).json();
      if (tok !== stoken) return;
      const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
      slist.innerHTML = list.length ? list.map((g) => {
        const art = SG.art({ steam: g.steamAppID, thumb: g.thumb });
        return '<li role="presentation"><a role="option" aria-selected="false" href="' + (tracked && tracked[g.gameID] ? '/game/' + tracked[g.gameID] + '/' : '/deal/?id=' + encodeURIComponent(g.gameID)) + '"><img src="' + esc(art) + '" alt="" loading="lazy" onerror="this.onerror=null;this.src=\'' + esc(g.thumb) + '\'"><span class="t">' + esc(g.external) + '</span><span class="p">from ' + money(g.cheapest) + '</span></a></li>';
      }).join('') : '<li class="msg">No games found for "' + esc(q) + '". Try fewer words.</li>';
      sinput.setAttribute('aria-expanded', list.length ? 'true' : 'false');
    } catch (e) { if (tok === stoken) slist.innerHTML = '<li class="msg">Search is busy right now. Try again in a moment.</li>'; }
  };
  SG.openSearch = () => { sbuild(); if (!sbar) { location.href = '/games.html'; return; } loadTracked(); sbar.hidden = false; document.querySelectorAll('.nav-search').forEach((a) => a.setAttribute('aria-expanded', 'true')); sinput.focus(); sinput.select(); };
  SG.closeSearch = () => { if (!sbar) return; sbar.hidden = true; document.querySelectorAll('.nav-search').forEach((a) => a.setAttribute('aria-expanded', 'false')); };
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey && !/^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || '')) && !e.target.isContentEditable) { e.preventDefault(); SG.openSearch(); }
  });

  const start = () => { nav(); sync(); setTimeout(alertCheck, 1500); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
