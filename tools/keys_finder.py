"""Key finder for /keys.html: search any game across the key stores and compare their prices.

Affiliate links: paste each approved program's tracking template into tools/affiliates.json.
Templates apply to the key marketplaces only (Kinguin, Eneba, CDKeys). Stores that CheapShark tracks
always use the CheapShark redirect, because that is the condition for its free price data.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def affiliates():
    """Only accept https templates that contain {url}; ignore comments and blanks."""
    try:
        with open(os.path.join(HERE, "affiliates.json")) as f:
            raw = json.load(f)
    except Exception:
        return {}
    return {k: v.strip() for k, v in raw.items()
            if not k.startswith("_") and isinstance(v, str) and v.strip().startswith("https://") and "{url}" in v}


SECTION = """<section class="block" id="find"><div class="wrap"><h2>Find any game key</h2>
<p class="fine">Search the key stores we track and compare their prices side by side. Prices come from live store listings. SteelGames may earn a commission when you buy through our links.</p>
<form class="kform" id="kform" role="search" autocomplete="off">
<label class="sr" for="kq">Game title</label>
<input id="kq" name="q" type="search" placeholder="Try Hades, Baldur's Gate 3 or Stardew Valley" enterkeyhint="search" maxlength="80">
<button class="btn" type="submit">Search keys</button>
</form>
<div class="chips" id="ksug" aria-label="Popular searches"><button type="button" data-q="Hades">Hades</button><button type="button" data-q="Cyberpunk 2077">Cyberpunk 2077</button><button type="button" data-q="Baldur's Gate 3">Baldur's Gate 3</button><button type="button" data-q="Stardew Valley">Stardew Valley</button><button type="button" data-q="Hogwarts Legacy">Hogwarts Legacy</button><button type="button" data-q="Elden Ring">Elden Ring</button></div>
<div class="kbar"><p class="status" id="kstat" aria-live="polite"></p>
<label class="ksort" for="ksort">Sort <select id="ksort"><option value="match">Best match</option><option value="price">Lowest price</option><option value="off">Biggest discount</option></select></label></div>
<div class="kgrid" id="kres"></div>
<div class="nmore"><button class="btn btn-ghost" id="kmore" type="button" hidden>Show more games</button></div>
<div id="kmkt"></div>
<noscript><p class="fine">The key finder needs JavaScript. You can still browse the resellers below.</p></noscript>
</div></section>
"""

STYLE = """<style>
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.kform{display:flex;gap:10px;flex-wrap:wrap}
.kform input{flex:1 1 260px;min-width:0;min-height:52px;padding:0 16px;border-radius:12px;border:1px solid var(--line-strong);background:var(--surface);color:#fff;font:500 16px var(--body)}
.kform input::placeholder{color:var(--muted)}
.kbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.ksort{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--muted)}
.ksort select{min-height:44px;border-radius:10px;border:1px solid var(--line-strong);background:var(--surface);color:#fff;padding:0 12px;font:600 14px var(--body)}
.kgrid{display:grid;grid-template-columns:minmax(0,1fr);gap:16px}
.kres{display:grid;grid-template-columns:200px minmax(0,1fr);gap:16px;padding:14px;border-radius:16px;background:var(--surface);border:1px solid var(--line);min-width:0}
@media (max-width:520px){.kres{grid-template-columns:minmax(0,1fr)}}
.kpic{position:relative;display:block;border-radius:10px;overflow:hidden;aspect-ratio:460/215;background:#0A0619;align-self:start}
.kpic img{width:100%;height:100%;object-fit:cover;display:block}
.kpic .off{position:absolute;top:6px;right:6px;padding:2px 8px;border-radius:7px;font:700 12px var(--display);background:var(--off-bg);color:var(--off-fg)}
.kbody{display:flex;flex-direction:column;gap:8px;min-width:0}
.kt{font:700 18px/1.25 var(--display);color:#fff;text-decoration:none}
.kt:hover{color:var(--accent-soft)}
.koff{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.koff li{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:10px;align-items:center;padding:8px 10px;border-radius:10px;background:var(--bg);border:1px solid var(--line);border-left:3px solid var(--c,#7B5CFF)}
@media (max-width:520px){.koff li{grid-template-columns:minmax(0,1fr) auto}.koff li .kbuy{grid-column:1/-1}}
.kn b{display:block;font-size:14px;color:#fff}
.kn small{color:var(--muted);font-size:12px}
.kp{display:flex;align-items:baseline;gap:6px;font-variant-numeric:tabular-nums}
.kp strong{font:700 18px var(--display);color:#fff}
.kp s{font-size:12px;color:var(--muted)}
.kp em{font:700 10px var(--body);letter-spacing:.06em;text-transform:uppercase;color:var(--good);font-style:normal}
.kbuy{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 16px;border-radius:10px;background:var(--grad-cta);color:var(--accent-ink);font:700 14px var(--body);text-decoration:none}
.kbuy:hover{filter:brightness(1.08);color:var(--accent-ink)}
.kall{font-size:14px}
.koff li.knone{display:block;padding:10px 12px;border-radius:10px;background:var(--bg);border:1px dashed var(--line-strong);font-size:14px;color:var(--muted)}
.knone b{color:#fff}
.kmks{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:13px;color:var(--muted)}
.kmks a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--line-strong);background:var(--bg);color:#fff;text-decoration:none;font:600 13px var(--body)}
.kmks a:hover{background:var(--raised)}
.kmkt{padding:16px;border-radius:16px;border:1px dashed var(--line-strong);display:flex;flex-direction:column;gap:10px}
.kmkt h3{font-size:18px}
</style>
"""

SCRIPT = r"""<script>
(() => {
  const API = 'https://www.cheapshark.com/api/1.0';
  const R = __DATA__;
  const AFF = __AFF__;
  const TRUST = { auth: 'Authorized retailer', keys: 'Key store', mkt: 'Marketplace' };
  const MARKETS = [
    { name: 'Kinguin', url: (q) => 'https://www.kinguin.net/listing?phrase=' + encodeURIComponent(q) },
    { name: 'Eneba', url: (q) => 'https://www.eneba.com/store/all?text=' + encodeURIComponent(q) },
    { name: 'CDKeys', url: (q) => 'https://www.cdkeys.com/catalogsearch/result/?q=' + encodeURIComponent(q) }
  ];
  const $ = (s) => document.querySelector(s);
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const money = (v) => '$' + (+v).toFixed(2);
  const form = $('#kform'), input = $('#kq'), out = $('#kres'), stat = $('#kstat'), sortSel = $('#ksort'), more = $('#kmore'), mkt = $('#kmkt');
  if (!form) return;
  const state = { q: '', games: [], shown: 12, seq: 0 };
  let storeMap = null;

  const loadStores = () => storeMap ? Promise.resolve(storeMap) : fetch(API + '/stores').then((r) => r.json()).then((all) => {
    const m = {};
    R.forEach((r) => { const s = all.find((x) => x.isActive && x.storeName === r.store); if (s) m[s.storeID] = r; });
    storeMap = m; return m;
  });
  const art = (d) => d.steamAppID && d.steamAppID !== '0' ? 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + d.steamAppID + '/header.jpg' : d.thumb;
  const finite = (v) => isFinite(v) ? v : Infinity;
  // Stores CheapShark tracks always open through its redirect: that is the condition for its free price data.
  const buyUrl = (d) => 'https://www.cheapshark.com/redirect?dealID=' + encodeURIComponent(d.dealID);
  const mktUrl = (m, q) => AFF[m.name] ? AFF[m.name].replace('{url}', encodeURIComponent(m.url(q))) : m.url(q);

  // Every game that matches the search, with the key store deals that exist for it right now (often none).
  const merge = (games, deals, q, map) => {
    const g = new Map(), ql = q.toLowerCase();
    games.forEach((x) => g.set(x.gameID, { id: x.gameID, title: x.external, art: art(x), thumb: x.thumb, low: +x.cheapest, offers: [] }));
    deals.forEach((d) => {
      const r = map[d.storeID]; if (!r || !(+d.salePrice > 0)) return;
      let x = g.get(d.gameID);
      if (!x) { x = { id: d.gameID, title: d.title, art: art(d), thumb: d.thumb, low: NaN, offers: [] }; g.set(d.gameID, x); }
      x.offers.push({ d, r });
    });
    const list = [...g.values()];
    list.forEach((x) => {
      x.offers.sort((a, b) => +a.d.salePrice - +b.d.salePrice);
      x.best = x.offers[0] || null;
      x.off = x.offers.length ? Math.max(...x.offers.map((o) => Math.round(+o.d.savings))) : 0;
      x.min = x.best ? +x.best.d.salePrice : finite(x.low);
      const t = x.title.toLowerCase();
      x.rel = t === ql ? 0 : t.indexOf(ql) === 0 ? 1 : t.indexOf(ql) > -1 ? 2 : 3;
    });
    return list;
  };
  const ORDER = {
    match: (a, b) => a.rel - b.rel || (b.offers.length > 0) - (a.offers.length > 0) || a.title.length - b.title.length || a.title.localeCompare(b.title),
    price: (a, b) => a.min - b.min,
    off: (a, b) => b.off - a.off || a.rel - b.rel
  };

  const card = (x) => {
    const href = '/deal/?id=' + encodeURIComponent(x.id);
    const rows = x.offers.slice(0, 4).map((o, i) => {
      const d = o.d, r = o.r, off = Math.round(+d.savings);
      return '<li style="--c:' + esc(r.c) + '"><span class="kn"><b>' + esc(r.name) + '</b><small>' + esc(TRUST[r.trust] || '') + '</small></span>' +
        '<span class="kp">' + (i === 0 && x.offers.length > 1 ? '<em>Lowest</em>' : '') + '<strong>' + money(d.salePrice) + '</strong>' + (off > 0 ? '<s>' + money(d.normalPrice) + '</s>' : '') + '</span>' +
        '<a class="kbuy" data-store="' + esc(r.name) + '" href="' + esc(buyUrl(d, r)) + '" target="_blank" rel="sponsored noopener" aria-label="Buy ' + esc(x.title) + ' at ' + esc(r.name) + '">Buy</a></li>';
    }).join('');
    const none = x.offers.length ? '' : '<li class="knone">No key store we track has a deal on this right now.' + (isFinite(x.low) ? ' Lowest price we track at any store: <b>' + money(x.low) + '</b>.' : '') + '</li>';
    const mk = '<div class="kmks"><span>Look for keys at</span>' + MARKETS.map((m) => '<a class="kmk" data-store="' + esc(m.name) + '" href="' + esc(mktUrl(m, x.title)) + '" target="_blank" rel="sponsored noopener" aria-label="Search ' + esc(x.title) + ' keys on ' + esc(m.name) + '">' + esc(m.name) + '</a>').join('') + '</div>';
    return '<article class="kres"><a class="kpic" href="' + href + '" tabindex="-1" aria-hidden="true"><img src="' + esc(x.art) + '" alt="" loading="lazy" onerror="this.onerror=null;this.src=\'' + esc(x.thumb) + '\'">' + (x.off > 0 ? '<span class="off">-' + x.off + '%</span>' : '') + '</a>' +
      '<div class="kbody"><a class="kt" href="' + href + '">' + esc(x.title) + '</a><ul class="koff">' + rows + none + '</ul>' + mk + '<a class="kall" href="' + href + '">All prices and price history</a></div></article>';
  };

  const marketsHtml = (q) => '<div class="kmkt"><h3>Try the marketplaces</h3><p class="fine">Nothing matched in our price feed. These links open a search for &ldquo;' + esc(q) + '&rdquo; on each site.</p><div class="chips">' +
    MARKETS.map((m) => '<a class="kbuy-link" data-store="' + esc(m.name) + '" href="' + esc(mktUrl(m, q)) + '" target="_blank" rel="sponsored noopener">Search ' + esc(m.name) + '</a>').join('') + '</div></div>';

  const paint = () => {
    const list = state.games.slice().sort(ORDER[sortSel.value] || ORDER.match);
    const show = list.slice(0, state.shown);
    out.innerHTML = show.length ? show.map(card).join('') : '<p class="empty" style="grid-column:1/-1">No games found for &ldquo;' + esc(state.q) + '&rdquo;. Try fewer words.</p>';
    mkt.innerHTML = list.length ? '<p class="fine">Marketplaces such as Kinguin, Eneba and CDKeys list keys from third-party sellers. Check the seller rating and buyer protection before you buy.</p>' : marketsHtml(state.q);
    stat.textContent = list.length ? 'Showing ' + show.length + ' of ' + list.length + ' games for “' + state.q + '”.' : '';
    more.hidden = list.length <= show.length;
    out.removeAttribute('aria-busy');
  };

  const run = async (raw) => {
    const q = (raw || '').trim(), my = ++state.seq; state.q = q;
    if (q.length < 2) { out.innerHTML = ''; stat.textContent = ''; mkt.innerHTML = ''; more.hidden = true; return; }
    stat.textContent = 'Searching…'; out.setAttribute('aria-busy', 'true'); mkt.innerHTML = '';
    try {
      const map = await loadStores(), e = encodeURIComponent(q);
      const [gm, dl] = await Promise.allSettled([
        fetch(API + '/games?title=' + e + '&limit=24').then((r) => r.json()),
        fetch(API + '/deals?title=' + e + '&storeID=' + Object.keys(map).join(',') + '&pageSize=60').then((r) => r.json())
      ]);
      if (my !== state.seq) return;
      if (gm.status === 'rejected' && dl.status === 'rejected') throw new Error('offline');
      const ok = (s) => s.status === 'fulfilled' && Array.isArray(s.value) ? s.value : [];
      state.games = merge(ok(gm), ok(dl), q, map); state.shown = 12; paint();
    } catch (e) {
      if (my !== state.seq) return;
      out.innerHTML = '<p class="empty" style="grid-column:1/-1">Search is not available right now. Please try again in a moment.</p>'; stat.textContent = ''; out.removeAttribute('aria-busy');
    }
  };
  const remember = (q) => { try { const u = new URL(location.href); if (q) u.searchParams.set('q', q); else u.searchParams.delete('q'); u.hash = 'find'; history.replaceState(null, '', u); } catch (e) {} };
  const count = (path, title) => { try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path, title, event: true }); } catch (e) {} };

  form.addEventListener('submit', (e) => { e.preventDefault(); remember(input.value.trim()); count('keys-search', 'Key search'); run(input.value); });
  let t = 0;
  input.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => run(input.value), 450); });
  sortSel.addEventListener('change', () => { if (state.games.length) paint(); });
  more.addEventListener('click', () => { state.shown += 12; paint(); });
  $('#ksug').addEventListener('click', (e) => { const b = e.target.closest('[data-q]'); if (!b) return; input.value = b.dataset.q; remember(b.dataset.q); count('keys-search', 'Key search'); run(b.dataset.q); });
  document.addEventListener('click', (e) => { const a = e.target.closest('.kbuy,.kbuy-link,.kmk'); if (a && a.dataset.store) count('keys-buy-' + a.dataset.store.toLowerCase().replace(/[^a-z0-9]+/g, '-'), 'Key buy click: ' + a.dataset.store); });

  const start = new URLSearchParams(location.search).get('q');
  if (start) { input.value = start; run(start); }
})();
</script>
"""


def tail(resellers_json):
    aff = json.dumps(affiliates()).replace("</", "<\\/")
    return STYLE + SCRIPT.replace("__DATA__", resellers_json).replace("__AFF__", aff)
