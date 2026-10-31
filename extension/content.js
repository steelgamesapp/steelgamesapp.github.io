// Adds a SteelGames price box to Steam store pages.
(() => {
  const m = /\/app\/(\d+)/.exec(location.pathname);
  if (!m || document.getElementById('sg-box')) return;
  const SITE = 'https://steelgamesapp.com';
  const money = (v) => (+v === 0 ? 'Free' : '$' + (+v).toFixed(2));
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const link = (href, text) => { const a = el('a', 'sg-link', text); a.href = href; a.target = '_blank'; a.rel = 'noopener'; return a; };

  chrome.runtime.sendMessage({ type: 'price', appid: m[1] }, (d) => {
    if (chrome.runtime.lastError || !d || d.error || d.notFound) return;
    const box = el('div', 'sg-box'); box.id = 'sg-box';
    const head = el('div', 'sg-head'); head.append(el('span', 'sg-brand', 'STEELGAMES'), el('span', 'sg-sub', 'Price check'));
    const price = el('div', 'sg-price', money(d.best));
    if (d.regular > d.best) price.append(el('s', '', money(d.regular)));
    const where = el('div', 'sg-where', 'Best price at ' + d.store + (d.stores > 1 ? ' of ' + d.stores + ' stores' : ''));
    box.append(head, price, where);
    if (d.low != null) {
      const atLow = d.best <= d.low;
      box.append(el('div', 'sg-low' + (atLow ? ' sg-good' : ''), atLow ? 'This is the lowest price we have recorded.' : 'Lowest ever: ' + money(d.low)));
    }
    const row = el('div', 'sg-row');
    row.append(link(SITE + '/deal/?id=' + d.id, 'Compare stores and history'));
    row.append(link(SITE + '/military.html', 'Veteran and first responder discounts'));
    box.append(row);
    const target = document.querySelector('.game_area_purchase_game') || document.querySelector('#game_highlights') || document.body;
    target.parentNode.insertBefore(box, target);
  });
})();
