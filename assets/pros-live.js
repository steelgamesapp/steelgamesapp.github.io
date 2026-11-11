/* SteelGames Pro Setups: live RAM price ticker + chart, and the "Loadout Roulette" game.
   Reads /data/ram.json (refreshed every two hours by .github/workflows/pros-live.yml) and checks again every 5 minutes
   while the page is open, so the numbers move without a reload. No libraries: the chart is plain SVG. */
(() => {
  'use strict';
  const SERIES = [ // fixed order and color per memory type (validated for color-blind separation on the dark surface)
    { id: 'DDR5', name: 'DDR5 16Gb', color: '#E0650A' },
    { id: 'DDR4', name: 'DDR4 16Gb', color: '#1C9DB0' },
    { id: 'DDR4-8', name: 'DDR4 8Gb', color: '#9466E8' },
    { id: 'GDDR6', name: 'GDDR6 8Gb', color: '#A88A14' },
  ];
  const RANGES = [['1W', 7], ['1M', 30], ['3M', 91], ['All', 0]];
  const $ = (s, r = document) => r.querySelector(s);
  const money = (v, d = 2) => '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let data = null, on = new Set(['DDR5', 'DDR4']), range = 30;

  function ago(iso) {
    const m = Math.round((Date.now() - Date.parse(iso)) / 60000);
    if (!isFinite(m)) return '';
    if (m < 2) return 'just now';
    if (m < 60) return m + ' min ago';
    const h = Math.round(m / 60);
    return h < 48 ? h + ' hr ago' : Math.round(h / 24) + ' days ago';
  }

  /* ---------- ticker tape ---------- */
  function ticker() {
    const el = $('#ramTape');
    if (!el || !data) return;
    const cells = [];
    for (const s of SERIES) {
      const t = (data.today || {})[s.id];
      if (!t) continue;
      const up = t.chg > 0, flat = !t.chg;
      cells.push(`<span class="tk"><b>${esc(s.name)}</b> ${money(t.avg, 3)} <i class="${flat ? 'fl' : up ? 'up' : 'dn'}">${flat ? '■' : up ? '▲' : '▼'} ${Math.abs(t.chg).toFixed(2)}%</i></span>`);
    }
    for (const k of (data.kits || []).slice(0, 8)) {
      const h = (data.kits_history || {})[k.asin] || [];
      const prev = h.length > 1 ? h[h.length - 2][1] : null;
      const d = prev ? (k.price - prev) / prev * 100 : 0;
      cells.push(`<a class="tk" href="${esc(k.url)}" target="_blank" rel="sponsored nofollow noopener"><b>${esc(k.gen)} ${k.gb || ''}GB</b> ${esc(k.short.replace(/ (DDR[45]|RAM).*/i, ''))} ${money(k.price)}${d ? ` <i class="${d > 0 ? 'up' : 'dn'}">${d > 0 ? '▲' : '▼'} ${Math.abs(d).toFixed(1)}%</i>` : ''}</a>`);
    }
    const row = cells.join('<span class="sep" aria-hidden="true">•</span>');
    el.innerHTML = `<div class="tape-run">${row}<span class="sep" aria-hidden="true">•</span>${row}<span class="sep" aria-hidden="true">•</span></div>`;
    el.querySelector('.tape-run').style.animationDuration = Math.max(30, cells.length * 6) + 's';
  }

  /* ---------- headline numbers ---------- */
  function stats() {
    const box = $('#ramStats');
    if (!box || !data) return;
    box.innerHTML = SERIES.filter(s => (data.today || {})[s.id]).map(s => {
      const t = data.today[s.id], pts = (data.spot || {})[s.id] || [];
      const first = pts.find(p => Date.parse(p[0]) >= Date.now() - range * 864e5) || pts[0];
      const long = pts.length > 2 && Date.parse(pts[pts.length - 1][0]) - Date.parse(pts[0][0]) > 864e5;
      const ch = long && first ? (t.avg - first[1]) / first[1] * 100 : t.chg;
      const lab = long ? (range ? RANGES.find(r => r[1] === range)[0] : 'all time') : 'today';
      return `<div class="rstat"><span class="sw" style="background:${s.color}"></span><small>${esc(s.name)} chip</small>
        <strong>${money(t.avg, 2)}</strong><em class="${ch > 0 ? 'up' : ch < 0 ? 'dn' : 'fl'}">${ch > 0 ? '▲' : ch < 0 ? '▼' : '■'} ${Math.abs(ch || 0).toFixed(2)}% ${lab}</em>
        <span class="rng">Day range ${money(t.lo)} – ${money(t.hi)}</span></div>`;
    }).join('');
  }

  /* ---------- line chart ---------- */
  function chart() {
    const wrap = $('#ramChart');
    if (!wrap || !data) return;
    const W = wrap.clientWidth || 800, H = Math.max(220, Math.min(340, W * 0.42));
    const P = { l: 52, r: 16, t: 14, b: 30 };
    const since = range ? Date.now() - range * 864e5 : 0;
    const lines = SERIES.filter(s => on.has(s.id)).map(s => ({ ...s, pts: ((data.spot || {})[s.id] || []).map(p => [Date.parse(p[0]), p[1]]).filter(p => p[0] >= since) }))
      .filter(s => s.pts.length);
    const all = lines.flatMap(s => s.pts);
    if (!all.length) { wrap.innerHTML = '<p class="fine">Pick a memory type above to see its price line.</p>'; return; }
    let x0 = Math.min(...all.map(p => p[0])), x1 = Math.max(...all.map(p => p[0]));
    if (x1 - x0 < 864e5) { x0 -= 432e5; x1 += 432e5; }
    const sparse = Math.max(...all.map(p => p[0])) - Math.min(...all.map(p => p[0])) < 864e5;
    const today = data.today || {};
    if (sparse) for (const s of lines) { const t = today[s.id]; if (t && t.lo && t.hi) all.push([all[0][0], t.lo], [all[0][0], t.hi]); }
    let y0 = Math.min(...all.map(p => p[1])), y1 = Math.max(...all.map(p => p[1]));
    const pad = (y1 - y0) * 0.12 || y1 * 0.1 || 1; y0 = Math.max(0, y0 - pad); y1 += pad;
    const X = t => P.l + (t - x0) / (x1 - x0) * (W - P.l - P.r);
    const Y = v => P.t + (1 - (v - y0) / (y1 - y0)) * (H - P.t - P.b);
    const ticks = 4, grid = [];
    for (let i = 0; i <= ticks; i++) {
      const v = y0 + (y1 - y0) * i / ticks;
      grid.push(`<line x1="${P.l}" x2="${W - P.r}" y1="${Y(v)}" y2="${Y(v)}" class="g"/><text x="${P.l - 8}" y="${Y(v) + 4}" text-anchor="end">$${v.toFixed(v < 10 ? 1 : 0)}</text>`);
    }
    const xt = [];
    const span = x1 - x0, n = Math.min(6, Math.max(2, Math.floor(W / 130)));
    for (let i = 0; i <= n; i++) {
      const t = x0 + span * i / n, d = new Date(t);
      const lab = span < 3 * 864e5 ? d.toLocaleTimeString([], { hour: 'numeric' }) : d.toLocaleDateString([], { month: 'short', day: 'numeric' });
      xt.push(`<text x="${X(t)}" y="${H - 8}" text-anchor="${i === 0 ? 'start' : i === n ? 'end' : 'middle'}">${lab}</text>`);
    }
    const paths = lines.map(s => {
      const d = s.pts.map((p, i) => (i ? 'L' : 'M') + X(p[0]).toFixed(1) + ' ' + Y(p[1]).toFixed(1)).join('');
      const last = s.pts[s.pts.length - 1];
      const area = s.id === lines[0].id && s.pts.length > 1 ? `<path d="${d}L${X(last[0])} ${H - P.b}L${X(s.pts[0][0])} ${H - P.b}Z" fill="url(#rg-${s.id})" opacity=".55"/>` : '';
      const t = today[s.id], k = lines.indexOf(s), cx = X(last[0]) - (lines.length - 1) * 9 + k * 18;
      const candle = sparse && t && t.lo && t.hi ? `<line x1="${cx}" x2="${cx}" y1="${Y(t.hi)}" y2="${Y(t.lo)}" stroke="${s.color}" stroke-width="6" stroke-linecap="round" opacity=".45"/>` : '';
      if (sparse) return `${candle}<circle cx="${cx}" cy="${Y(last[1])}" r="6" fill="${s.color}" stroke="#1A1342" stroke-width="2" class="pulse"/>`;
      return `${area}<path d="${d}" fill="none" stroke="${s.color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
        <circle cx="${X(last[0])}" cy="${Y(last[1])}" r="5" fill="${s.color}" stroke="#1A1342" stroke-width="2" class="pulse"/>`;
    }).join('');
    const defs = lines.map(s => `<linearGradient id="rg-${s.id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${s.color}" stop-opacity=".35"/><stop offset="1" stop-color="${s.color}" stop-opacity="0"/></linearGradient>`).join('');
    wrap.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="DRAM spot price chart">
      <defs>${defs}</defs>${grid.join('')}${xt.join('')}${paths}
      <line class="xh" y1="${P.t}" y2="${H - P.b}" x1="-10" x2="-10"/><rect class="hit" x="${P.l}" y="${P.t}" width="${W - P.l - P.r}" height="${H - P.t - P.b}" fill="transparent"/></svg>
      <div class="tip" hidden></div>`;
    const svg = wrap.querySelector('svg'), tip = wrap.querySelector('.tip'), xh = svg.querySelector('.xh');
    const move = ev => {
      const r = svg.getBoundingClientRect(), mx = (ev.touches ? ev.touches[0].clientX : ev.clientX) - r.left;
      const t = x0 + (mx * W / r.width - P.l) / (W - P.l - P.r) * span;
      const rows = lines.map(s => { let b = s.pts[0]; for (const p of s.pts) if (Math.abs(p[0] - t) < Math.abs(b[0] - t)) b = p; return [s, b]; });
      const bt = rows[0][1][0];
      xh.setAttribute('x1', X(bt)); xh.setAttribute('x2', X(bt));
      tip.hidden = false;
      tip.innerHTML = `<b>${new Date(bt).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</b>` +
        rows.map(([s, p]) => `<span><i style="background:${s.color}"></i>${esc(s.name)} <strong>${money(p[1], 3)}</strong></span>`).join('');
      const left = X(bt) / W * r.width;
      tip.style.left = Math.min(Math.max(left - tip.offsetWidth / 2, 0), r.width - tip.offsetWidth) + 'px';
    };
    svg.addEventListener('pointermove', move);
    svg.addEventListener('touchmove', move, { passive: true });
    svg.addEventListener('pointerleave', () => { tip.hidden = true; xh.setAttribute('x1', -10); xh.setAttribute('x2', -10); });
    $('#ramNote').textContent = sparse ? "Bars show today's trading range (high to low) and the dot is the average. The line fills in as the tracker records a new price every two hours." : '';
  }

  function controls() {
    const box = $('#ramCtl');
    if (!box) return;
    box.innerHTML = SERIES.map(s => `<button type="button" data-s="${s.id}" aria-pressed="${on.has(s.id)}"><span class="sw" style="background:${s.color}"></span>${esc(s.name)}</button>`).join('') +
      '<span class="gap"></span>' + RANGES.map(([l, d]) => `<button type="button" data-r="${d}" aria-pressed="${d === range}">${l}</button>`).join('');
    box.onclick = e => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.s) { on.has(b.dataset.s) ? on.size > 1 && on.delete(b.dataset.s) : on.add(b.dataset.s); }
      if (b.dataset.r) range = +b.dataset.r;
      controls(); chart(); stats();
    };
  }

  function kits() {
    const box = $('#ramKits');
    if (!box || !data || !(data.kits || []).length) return;
    box.innerHTML = data.kits.slice(0, 6).map(k => `<a class="kit" href="${esc(k.url)}" target="_blank" rel="sponsored nofollow noopener">
      <img src="${esc(k.img)}" alt="" loading="lazy" width="64" height="64"><span><small>#${k.rank} best seller · ${esc(k.gen)} ${k.gb || ''}GB</small>${esc(k.short)}</span>
      <strong>${money(k.price)}${k.gb ? `<em>${money(k.price / k.gb)}/GB</em>` : ''}</strong></a>`).join('');
  }

  async function load() {
    try {
      const r = await fetch('/data/ram.json?t=' + Math.floor(Date.now() / 300000), { cache: 'no-store' });
      if (!r.ok) throw new Error(r.status);
      data = await r.json();
    } catch (e) { if (!data) { const n = $('#ramNote'); if (n) n.textContent = 'Live prices could not load right now. Try again in a minute.'; } return; }
    const u = $('#ramUpdated'); if (u) u.textContent = 'Spot prices updated ' + ago(data.spot_updated || data.updated);
    ticker(); stats(); chart(); kits();
  }

  /* ---------- Loadout Roulette: spin a random best-seller setup and compare it with a pro's ---------- */
  function roulette() {
    const box = $('#roulette'); if (!box) return;
    let items = [];
    try { items = JSON.parse($('#bestData').textContent).items || []; } catch (e) { return; }
    const slots = ['mouse', 'keyboard', 'headset'].map(k => items.filter(i => i.kind === k)).filter(a => a.length);
    const reels = box.querySelectorAll('.reel'), total = $('#rlTotal'), btn = $('#rlSpin');
    btn.onclick = () => {
      btn.disabled = true;
      const picks = slots.map(a => a[Math.floor(Math.random() * a.length)]);
      const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
      reels.forEach((r, i) => {
        const pool = slots[i] || [];
        let n = 0;
        const spin = setInterval(() => {
          const it = n++ < (reduce ? 0 : 8 + i * 5) ? pool[Math.floor(Math.random() * pool.length)] : picks[i];
          r.innerHTML = it ? `<img src="${esc(it.img)}" alt="" width="96" height="96"><b>${esc(it.short)}</b><span>${it.price ? money(it.price) : ''}</span>
            <a href="${esc(it.url)}" target="_blank" rel="sponsored nofollow noopener">See it on Amazon</a>` : '';
          r.classList.toggle('spinning', it !== picks[i]);
          if (it === picks[i]) {
            clearInterval(spin);
            if (i === reels.length - 1) {
              const sum = picks.reduce((a, p) => a + (p && p.price || 0), 0);
              total.innerHTML = `Your loadout: <strong>${money(sum)}</strong>. A full pro setup like shroud's runs over $700. ${sum < 150 ? 'Budget legend.' : sum < 250 ? 'Solid value.' : 'Big spender.'}`;
              btn.disabled = false; btn.textContent = 'Spin again';
              if (window.goatcounter && goatcounter.count) goatcounter.count({ path: 'pros-roulette-spin', event: true });
            }
          }
        }, 70);
      });
    };
  }

  function start() {
    controls(); load(); roulette();
    setInterval(() => { if (!document.hidden) load(); }, 300000);
    let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(chart, 150); });
  }
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', start) : start();
})();
