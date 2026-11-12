/* SteelGames site-wide "LIVE RAM" scrolling price strip.
   Shown under the site header on every page. Reads /data/ram.json (refreshed every two hours by
   .github/workflows/pros-live.yml) and re-checks every 5 minutes while the page is open.
   The Pro setups page already has its own strip (#ramTape), so this script does nothing there. */
(() => {
  'use strict';
  if (window.__sgRamTicker) return;
  window.__sgRamTicker = true;

  const SERIES = [
    { id: 'DDR5', name: 'DDR5 16Gb' },
    { id: 'DDR4', name: 'DDR4 16Gb' },
    { id: 'DDR4-8', name: 'DDR4 8Gb' },
    { id: 'GDDR6', name: 'GDDR6 8Gb' },
  ];
  const money = (v, d = 2) => '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function css() {
    const st = document.createElement('style');
    st.textContent =
      '.sg-rt{position:relative;overflow:hidden;background:#0A0619;border-bottom:1px solid #3A2C7A;font:600 14px/1 "Space Grotesk",Inter,system-ui,sans-serif;white-space:nowrap}' +
      '.sg-rt-lab{position:absolute;left:0;top:0;bottom:0;z-index:2;display:flex;align-items:center;padding:0 14px;background:#0A0619;box-shadow:12px 0 12px #0A0619;color:#FF8A1A;letter-spacing:1.5px;font-size:12px;text-decoration:none}' +
      '.sg-rt-run{display:inline-flex;align-items:center;gap:18px;padding:11px 0 11px 110px;animation:sgrt 60s linear infinite}' +
      '.sg-rt:hover .sg-rt-run{animation-play-state:paused}' +
      '@keyframes sgrt{to{transform:translateX(-50%)}}' +
      '.sg-rt .tk{color:#fff;text-decoration:none}.sg-rt .tk b{color:#B9B1E0;font-weight:600;margin-right:4px}.sg-rt .tk i{font-style:normal;margin-left:4px}' +
      '.sg-rt .up{color:#7CF0A8}.sg-rt .dn{color:#FF8FA6}.sg-rt .fl{color:#B9B1E0}.sg-rt .sep{color:#3A2C7A}' +
      '@media (prefers-reduced-motion:reduce){.sg-rt-run{animation:none}}';
    document.head.appendChild(st);
  }

  function build(data) {
    const cells = [];
    for (const s of SERIES) {
      const t = (data.today || {})[s.id];
      if (!t) continue;
      const up = t.chg > 0, flat = !t.chg;
      cells.push(`<a class="tk" href="/pros/#ram"><b>${esc(s.name)}</b> ${money(t.avg, 3)} <i class="${flat ? 'fl' : up ? 'up' : 'dn'}">${flat ? '■' : up ? '▲' : '▼'} ${Math.abs(t.chg).toFixed(2)}%</i></a>`);
    }
    for (const k of (data.kits || []).slice(0, 8)) {
      const h = (data.kits_history || {})[k.asin] || [];
      const prev = h.length > 1 ? h[h.length - 2][1] : null;
      const d = prev ? (k.price - prev) / prev * 100 : 0;
      cells.push(`<a class="tk" href="${esc(k.url)}" target="_blank" rel="sponsored nofollow noopener"><b>${esc(k.gen)} ${k.gb || ''}GB</b> ${esc(String(k.short || '').replace(/ (DDR[45]|RAM).*/i, ''))} ${money(k.price)}${d ? ` <i class="${d > 0 ? 'up' : 'dn'}">${d > 0 ? '▲' : '▼'} ${Math.abs(d).toFixed(1)}%</i>` : ''}</a>`);
    }
    return cells;
  }

  let el;
  async function load() {
    try {
      const r = await fetch('/data/ram.json', { cache: 'no-cache' });
      if (!r.ok) return;
      const cells = build(await r.json());
      if (!cells.length) return;
      if (!el) {
        el = document.createElement('div');
        el.className = 'sg-rt';
        el.setAttribute('aria-label', 'Live RAM prices');
        const header = document.querySelector('header.site-header') || document.querySelector('header');
        if (header && header.parentNode) header.parentNode.insertBefore(el, header.nextSibling);
        else document.body.insertBefore(el, document.body.firstChild);
      }
      const sep = '<span class="sep" aria-hidden="true">•</span>';
      const row = cells.join(sep);
      el.innerHTML = `<a class="sg-rt-lab" href="/pros/#ram">LIVE RAM</a><div class="sg-rt-run">${row}${sep}${row}${sep}</div>`;
      el.querySelector('.sg-rt-run').style.animationDuration = Math.max(30, cells.length * 6) + 's';
    } catch (e) { /* offline or blocked: leave the page as it is */ }
  }

  function start() {
    if (document.getElementById('ramTape')) return; // Pro setups page has its own strip
    css();
    load();
    setInterval(load, 5 * 60 * 1000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
