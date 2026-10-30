"""Builds /keys.html: key resellers (live stats from CheapShark) plus a software deals section."""
import layout

SITE = layout.SITE
TAG = "steelgames-20"


def az(q):
    return f"https://www.amazon.com/s?k={q.replace(' ', '+')}&i=software&tag={TAG}"


ICONS = {
    "win": '<svg width="52" height="52" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 5.5 11 4.4v7H3zM12 4.3 21 3v8.4h-9zM3 12.6h8v7l-8-1.1zM12 12.6h9V21l-9-1.3z"/></svg>',
    "doc": '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/></svg>',
    "shield": '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 4 6v6c0 4.5 3.2 7.6 8 9 4.8-1.4 8-4.5 8-9V6z"/><path d="m9 12 2.2 2.2L15.5 10"/></svg>',
    "brush": '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 3 9 12l3 3 9-9z"/><path d="M9 12c-3 0-4 2-4 4 0 2-1 3-2 4 3 1 8 0 9-5"/></svg>',
    "disk": '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M7 15h.01M11 15h6M3 11h18"/></svg>',
    "lock": '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3M12 15v2"/></svg>',
}

SOFTWARE = [
    ("Windows 11", "#66C0F4", "win", "Windows 11 Home and Pro", "The operating system most gaming PCs run. Buy a full retail license for a new build or an upgrade.", ["One-time purchase", "Digital or boxed"], "Windows 11 Pro"),
    ("Office", "#FF8A3D", "doc", "Microsoft 365 and Office", "Word, Excel and PowerPoint for school, work and household budgets. Compare yearly plans and one-time versions.", ["Subscription", "One-time option"], "Microsoft 365"),
    ("Security", "#5CE08A", "shield", "Antivirus and security", "Protection for every device in the house. Look for multi-device plans that cover PC, phone and tablet.", ["Subscription", "Multi-device"], "antivirus software"),
    ("Creative", "#FF6B8A", "brush", "Video, photo and music tools", "Editing and creating software for streamers, YouTubers and anyone cutting gameplay clips.", ["Creators", "Streaming"], "video editing software"),
    ("Backup", "#B388FF", "disk", "Backup and PC utilities", "Back up your game saves, clean up your drive and keep your build running smoothly.", ["Utilities", "Digital download"], "PC backup software"),
    ("Privacy", "#4DD0E1", "lock", "Password managers and VPN apps", "Keep your accounts safe, especially store logins that hold your whole game library.", ["Subscription", "Accounts"], "password manager"),
]

# (store name used by CheapShark or None, display name, color, trust key, description, homepage)
RESELLERS = [
    ("Fanatical", "Fanatical", "#FF8A3D", "auth", "Official Steam keys, big bundles and frequent flash sales. A favorite for single-game discounts.", "https://www.fanatical.com"),
    ("GreenManGaming", "Green Man Gaming", "#5CE08A", "auth", "Long-running authorized retailer selling Steam keys, with a loyalty program that gives money back.", "https://www.greenmangaming.com"),
    ("Humble Store", "Humble Store", "#FF5A5F", "auth", "Steam keys and DRM-free games, and a share of each sale supports charity.", "https://www.humblebundle.com/store"),
    ("Gamesplanet", "Gamesplanet", "#4DD0E1", "auth", "Publisher-authorized store with regional sites and a steady stream of deals on PC games.", "https://us.gamesplanet.com"),
    ("GamersGate", "GamersGate", "#FF7043", "auth", "One of the older digital stores, strong on strategy and simulation catalogs.", "https://www.gamersgate.com"),
    ("GameBillet", "GameBillet", "#FFD43B", "keys", "Key store with deep discounts on recent PC releases and big publisher catalogs.", "https://www.gamebillet.com"),
    ("Voidu", "Voidu", "#F06292", "keys", "Digital key store known for low prices on Steam and publisher launcher keys.", "https://www.voidu.com"),
    ("IndieGala", "IndieGala", "#FF5252", "keys", "Indie-focused store with bundles that pack many small games into one low price.", "https://www.indiegala.com"),
    ("WinGameStore", "WinGameStore", "#4FC3F7", "keys", "Key seller with aggressive pricing on older and mid-priced PC games.", "https://www.wingamestore.com"),
    (None, "CDKeys", "#B388FF", "keys", "Popular key retailer for PC games, gift cards and software. Compare prices on their site.", "https://www.cdkeys.com"),
    (None, "Kinguin", "#FF9A1A", "mkt", "A marketplace where many third-party sellers list keys. Prices can be very low, so check seller ratings first.", "https://www.kinguin.net"),
    (None, "Eneba", "#8E6BFF", "mkt", "A marketplace with keys from many sellers, plus gift cards and software. Check seller ratings and buyer protection.", "https://www.eneba.com"),
]
TRUST = {"auth": "Authorized retailer", "keys": "Key store", "mkt": "Marketplace"}


def js_data():
    import json
    return json.dumps([{"store": s, "name": n, "c": c, "trust": t, "desc": d, "url": u} for s, n, c, t, d, u in RESELLERS])


SCRIPT = r"""
<script>
(() => {
  const API = 'https://www.cheapshark.com/api/1.0';
  const R = __DATA__;
  const TRUST = { auth: 'Authorized retailer', keys: 'Key store', mkt: 'Marketplace' };
  const $ = (s) => document.querySelector(s);
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const money = (v) => '$' + (+v).toFixed(2);
  const art = (d) => d.steamAppID && d.steamAppID !== '0' ? 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + d.steamAppID + '/header.jpg' : d.thumb;
  const st = { stores: {}, ids: [], pick: '', low: new Map(), asked: new Set(), deals: new Map(), cards: {} };
  const rg = $('#rgrid'), grid = $('#grid'), chips = $('#rchips'), status = $('#status');

  const rcard = (r, s) => {
    const info = s ? s.info : null;
    const logo = r.logo ? '<img src="' + esc(r.logo) + '" alt="" width="36" height="36">' : '';
    const stats = info
      ? '<div class="stats"><div class="stat now"><small>Live deals</small><strong>' + info.n + (info.n >= 60 ? '+' : '') + '</strong></div><div class="stat hi"><small>Avg discount</small><strong>' + info.avg + '%</strong></div><div class="stat lo"><small>Top deal</small><strong>' + money(info.best.salePrice) + '</strong></div></div>'
      : '<div class="stats"><div class="stat"><small>Live deals</small><strong>Visit</strong></div><div class="stat"><small>Catalog</small><strong>Games+</strong></div><div class="stat"><small>Type</small><strong>' + (r.trust === 'mkt' ? 'Market' : 'Keys') + '</strong></div></div>';
    return '<article class="rcard" style="--c:' + r.c + '"><div class="art">' + (info ? '<img class="bg" src="' + esc(art(info.best)) + '" alt="" loading="lazy">' : '') +
      '<div class="badge">' + logo + '<h3>' + esc(r.name) + '</h3></div></div><div class="body"><span class="trust ' + r.trust + '">' + TRUST[r.trust] + '</span><p>' + esc(r.desc) + '</p>' +
      (info ? '<p class="fine">Best right now: <b style="color:#fff">' + esc(info.best.title) + '</b> at -' + Math.round(+info.best.savings) + '%</p>' : '') + stats +
      '<div class="acts">' + (s ? '<button type="button" data-pick="' + s.id + '">See their deals</button>' : '') + '<a class="primary" href="' + esc(r.url) + '" target="_blank" rel="noopener sponsored">Visit ' + esc(r.name) + '</a></div></div></article>';
  };
  const draw = () => { rg.innerHTML = R.map((r) => rcard(r, st.cards[r.name])).join(''); };

  const HEART = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.6-9.3-9A5.4 5.4 0 0 1 12 6.6 5.4 5.4 0 0 1 21.3 12C19 16.4 12 21 12 21z"/></svg>';
  const CARTI = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 12.2a1 1 0 0 0 1 .8h9.1a1 1 0 0 0 1-.8L21 7H6"/></svg>';
  const act = (d, store) => {
    const sid = d.steamAppID && d.steamAppID !== '0' ? d.steamAppID : '';
    const a = ' data-id="' + esc(d.gameID) + '" data-deal="' + esc(d.dealID) + '" data-title="' + esc(d.title) + '" data-thumb="' + esc(d.thumb) + '" data-steam="' + esc(sid) + '" data-store="' + esc(store) + '" data-price="' + esc(d.salePrice) + '" data-normal="' + esc(d.normalPrice) + '"';
    return '<div class="gact"><button type="button" data-wish' + a + ' aria-pressed="false">' + HEART + '<span class="lab">Wishlist</span></button><button type="button" data-cart' + a + ' aria-pressed="false">' + CARTI + '<span class="lab">Add to cart</span></button></div>';
  };
  const dcard = (d) => {
    const off = Math.round(+d.savings), store = st.stores[d.storeID] || 'Store', r = R.find((x) => x.store === store);
    const html = '<a class="gwide" style="--store:' + (r ? r.c : '#7B5CFF') + '" href="/deal/?id=' + encodeURIComponent(d.gameID) + '"><span class="pic"><img src="' + esc(art(d)) + '" alt="' + esc(d.title) + ' cover art" loading="lazy" onerror="this.onerror=null;this.src=\'' + esc(d.thumb) + '\'">' + (off > 0 ? '<span class="off">-' + off + '%</span>' : '') + '</span>' +
      '<span class="info"><span class="t">' + esc(d.title) + '</span><span class="sub"><b>' + esc(r ? r.name : store) + '</b>' + (r ? '<span class="tag">' + TRUST[r.trust] + '</span>' : '') + (+d.steamRatingPercent > 0 ? '<span>' + d.steamRatingPercent + '% positive</span>' : '') + '</span>' +
      '<span class="stats"><span class="stat now"><small>Now</small><strong>' + money(d.salePrice) + '</strong></span><span class="stat hi"><small>Highest</small><strong>' + money(Math.max(+d.normalPrice, +d.salePrice)) + '</strong></span>' +
      '<span class="stat lo pending" data-low="' + esc(d.gameID) + '"><small>Lowest ever</small><strong>...</strong></span></span></span></a>';
    return '<div class="gw">' + html + act(d, store) + '</div>';
  };
  const paintLow = () => document.querySelectorAll('[data-low]').forEach((el) => { const v = st.low.get(el.dataset.low); if (v === undefined) return; el.classList.remove('pending'); el.querySelector('strong').textContent = money(v); });
  const fillLow = async (rows) => {
    const need = rows.map((d) => d.gameID).filter((id) => !st.asked.has(id)); need.forEach((id) => st.asked.add(id));
    for (let i = 0; i < need.length; i += 25) {
      const ids = need.slice(i, i + 25);
      try { const j = await (await fetch(API + '/games?ids=' + ids.join(','))).json(); ids.forEach((id) => { if (j[id] && j[id].cheapestPriceEver) st.low.set(id, +j[id].cheapestPriceEver.price); }); } catch (e) { ids.forEach((id) => st.asked.delete(id)); }
      paintLow();
    }
  };
  const showDeals = () => {
    const rows = [...st.deals.values()].filter((d) => !st.pick || String(d.storeID) === st.pick).sort((a, b) => (+b.dealRating) - (+a.dealRating)).slice(0, 36);
    grid.innerHTML = rows.length ? rows.map(dcard).join('') : '<p class="empty">No live deals right now. Check back soon.</p>';
    status.textContent = rows.length ? 'Showing ' + rows.length + ' of the best key deals' + (st.pick ? ' at ' + st.stores[st.pick] : ' across all resellers') + '.' : '';
    fillLow(rows); paintLow();
  };
  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-pick]'); if (!b) return;
    st.pick = b.dataset.pick; syncChips(); showDeals(); $('#deals').scrollIntoView({ behavior: 'smooth' });
  });
  const syncChips = () => { chips.innerHTML = '<button type="button" data-pick="" aria-pressed="' + (!st.pick) + '" style="--c:#FFB020">All resellers</button>' + st.ids.map((id) => { const r = R.find((x) => x.store === st.stores[id]); return '<button type="button" data-pick="' + id + '" aria-pressed="' + (st.pick === id) + '" style="--c:' + (r ? r.c : '#7B5CFF') + '">' + esc(r ? r.name : st.stores[id]) + '</button>'; }).join(''); };

  draw();
  fetch(API + '/stores').then((r) => r.json()).then(async (all) => {
    all.filter((s) => s.isActive).forEach((s) => { st.stores[s.storeID] = s.storeName; });
    R.forEach((r) => { const s = all.find((x) => x.isActive && x.storeName === r.store); if (s) { r.id = s.storeID; r.logo = 'https://www.cheapshark.com' + s.images.logo; st.ids.push(s.storeID); } });
    const live = R.filter((r) => r.id);
    const results = await Promise.all(live.map((r) => fetch(API + '/deals?storeID=' + r.id + '&onSale=1&sortBy=Deal%20Rating&pageSize=60&steamRating=0').then((x) => x.json()).catch(() => [])));
    live.forEach((r, i) => {
      const d = (results[i] || []).filter((x) => +x.salePrice > 0); if (!d.length) return;
      d.forEach((x) => { if (!st.deals.has(x.dealID)) st.deals.set(x.dealID, x); });
      st.cards[r.name] = { id: r.id, info: { n: d.length, avg: Math.round(d.reduce((a, x) => a + (+x.savings), 0) / d.length), best: d[0] } };
    });
    // one card per game in the grid: keep the cheapest listing
    const byGame = new Map(); st.deals.forEach((d) => { const o = byGame.get(d.gameID); if (!o || +d.salePrice < +o.salePrice) byGame.set(d.gameID, d); });
    st.deals = new Map([...byGame.values()].map((d) => [d.dealID, d]));
    st.ids = st.ids.filter((id) => R.some((r) => r.id === id && st.cards[r.name]));
    draw(); syncChips(); showDeals();
  }).catch(() => { grid.innerHTML = '<p class="empty">Deals are loading slowly. Please try again in a moment.</p>'; });
})();
</script>
"""


def build():
    sw = "".join(
        f'<a class="scard" style="--c:{c}" href="{az(q)}" target="_blank" rel="noopener sponsored"><span class="ph">{ICONS[ic]}</span>'
        f'<h3>{t}</h3><p>{d}</p><span class="tags">{"".join(f"<span>{x}</span>" for x in tags)}</span><span class="go">Compare prices &rarr;</span></a>'
        for _, c, ic, t, d, tags, q in SOFTWARE)
    tips = "".join(f'<div class="tip"><b>{i}</b><p>{t}</p></div>' for i, t in enumerate([
        "Stick with authorized retailers when you can. They buy keys from publishers, so problems are rare.",
        "Marketplaces list many third-party sellers. Check the seller's rating and the store's buyer protection before you buy.",
        "Be careful when a price is far below every other store. A great price is fine, an impossible one is a warning sign.",
        "Check the region and platform. Some keys only work in certain countries or on certain launchers like Steam, EA or Ubisoft.",
        "Redeem your key soon after buying and keep the receipt in case you need support.",
        "For Windows and Office, buy a full retail license from a trusted seller and make sure it matches the version you want."], 1))
    return (layout.head("Game Key Resellers and Software Deals | SteelGames",
                        "Compare trusted game key resellers and see today's best key deals with current, highest and lowest prices. Plus deals on Windows, Office, security and creative software.",
                        f"{SITE}/keys.html")
            + layout.header("keys")
            + """<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Keys &amp; software</p>
<h1>Game key resellers and software deals</h1>
<p class="lede">Key stores often beat the official price. See who is running the best deals right now, how big their discounts are, and what to watch for before you buy.</p>
<div class="chips"><a href="#resellers">Resellers</a><a href="#deals">Best key deals</a><a href="#software">Software deals</a><a href="#safe">Buying safely</a></div>
</div></section>
<section class="block" id="resellers"><div class="wrap"><h2>Key resellers</h2>
<p class="fine">Live stats come from current store listings. Marketplaces and stores we can't read live link straight to their sites.</p>
<div class="rgrid" id="rgrid"></div></div></section>
<section class="block" id="deals"><div class="wrap"><h2>Best key deals right now</h2>
<div class="chips cats" id="rchips"></div>
<p class="status" id="status" aria-live="polite"></p>
<div class="wide-grid" id="grid" aria-live="polite"><div class="gwide sk"></div><div class="gwide sk"></div><div class="gwide sk"></div><div class="gwide sk"></div></div>
<p class="fine">Highest is the usual full price. Lowest ever is the lowest price recorded across the stores we track.</p></div></section>
<section class="block" id="software"><div class="wrap"><h2>Software deals</h2>
<p class="fine">Everyday software for your gaming PC. Tap a card to compare current prices.</p>
<div class="sgrid">""" + sw + """</div></div></section>
<section class="block" id="safe"><div class="wrap"><h2>Buying keys safely</h2><div class="tips">""" + tips + """</div></div></section>
</main>
""" + SCRIPT.replace("__DATA__", js_data()) + layout.footer())
