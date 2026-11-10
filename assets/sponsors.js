/* SteelGames sponsor slots.
   Fills any element that has data-sponsor-slot="home" or "gear" from /sponsors.json (see tools/SPONSORS.md to book one).
   - Every paid spot is labeled "Sponsored" and its link is rel="sponsored nofollow".
   - An empty slot shows a slim "Advertise here" line (only when the element has data-house) so prospects can see where it goes.
   - Views and clicks are counted as GoatCounter events (sponsor-view/<id>, sponsor-click/<id>) so sponsors get real numbers.
   - A sponsor only shows between its starts and ends dates (inclusive). If several are booked for one slot they take turns. */
(function () {
  var slots = document.querySelectorAll('[data-sponsor-slot]');
  if (!slots.length) return;

  var css = '.sgsp{display:block;margin:0 0 14px}' +
    '.sgsp-a{display:flex;align-items:center;gap:14px;padding:12px 14px;border-radius:10px;background:#150E38;border:1px solid #35288A;color:#fff;text-decoration:none}' +
    '.sgsp-a:hover{border-color:#B9AEFF;color:#fff}' +
    '.sgsp-img{width:132px;height:74px;object-fit:cover;border-radius:6px;flex:none;background:#0F0A24}' +
    '.sgsp-tx{display:flex;flex-direction:column;gap:2px;min-width:0;flex:1;font-size:13px;color:#C9C2EE;line-height:1.35}' +
    '.sgsp-tx strong{color:#fff;font-size:16px;line-height:1.25}' +
    '.sgsp-lab{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#FFB020}' +
    '.sgsp-cta{flex:none;padding:8px 14px;border-radius:8px;background:#FF7A1A;color:#1a0f00;font-weight:700;font-size:13px;white-space:nowrap}' +
    '.sgsp-house{border-style:dashed;background:transparent}.sgsp-house .sgsp-cta{background:transparent;color:#FF7A1A;border:1px solid #FF7A1A}' +
    '@media(max-width:560px){.sgsp-a{flex-wrap:wrap}.sgsp-img{width:100%;height:120px}.sgsp-cta{width:100%;text-align:center}}';
  var st = document.createElement('style');
  st.id = 'sgsp-css';
  st.appendChild(document.createTextNode(css));
  document.head.appendChild(st);

  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function safeUrl(u) { return /^https?:\/\//i.test(String(u || '')) ? String(u) : ''; }
  function endMs(s) {
    if (!s) return Infinity;
    var t = String(s).length <= 10 ? Date.parse(s + 'T23:59:59') : Date.parse(s);
    return isNaN(t) ? Infinity : t;
  }
  function startMs(s) {
    if (!s) return 0;
    var t = Date.parse(String(s).length <= 10 ? s + 'T00:00:00' : s);
    return isNaN(t) ? 0 : t;
  }
  function count(path, title, tries) {
    try {
      if (window.goatcounter && window.goatcounter.count) { window.goatcounter.count({ path: path, title: title, event: true }); return; }
    } catch (e) { return; }
    if ((tries || 0) < 6) setTimeout(function () { count(path, title, (tries || 0) + 1); }, 1000);
  }
  function once(key, fn) {
    try { if (sessionStorage.getItem(key)) return; sessionStorage.setItem(key, '1'); } catch (e) { /* private mode: count anyway */ }
    fn();
  }

  function live(list, slot) {
    var now = Date.now();
    return (Array.isArray(list) ? list : []).filter(function (x) {
      if (!x || !x.active || !safeUrl(x.url) || !x.title) return false;
      var where = x.slots || x.slot || ['home'];
      where = Array.isArray(where) ? where : [where];
      return where.indexOf(slot) > -1 && startMs(x.starts) <= now && now <= endMs(x.ends);
    });
  }

  function render(el, s) {
    var slot = el.getAttribute('data-sponsor-slot');
    var id = String(s.id || s.title).toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40);
    var img = safeUrl(s.image);
    el.innerHTML = '<aside class="sgsp" aria-label="Sponsored"><a class="sgsp-a" href="' + esc(safeUrl(s.url)) + '" target="_blank" rel="sponsored nofollow noopener">' +
      (img ? '<img class="sgsp-img" src="' + esc(img) + '" alt="" loading="lazy" width="132" height="74">' : '') +
      '<span class="sgsp-tx"><span class="sgsp-lab">Sponsored</span><strong>' + esc(s.title) + '</strong>' + (s.text ? '<span>' + esc(s.text) + '</span>' : '') + '</span>' +
      '<span class="sgsp-cta">' + esc(s.cta || 'Learn more') + '</span></a></aside>';
    once('sgsp-v-' + id + '-' + slot, function () { count('sponsor-view/' + id + '/' + slot, 'Sponsor view: ' + s.title); });
    el.querySelector('a').addEventListener('click', function () { count('sponsor-click/' + id + '/' + slot, 'Sponsor click: ' + s.title); });
  }

  function house(el) {
    var label = el.getAttribute('data-house-label') || 'Featured spot';
    var title = el.getAttribute('data-house-title') || 'Your game or gear could be here';
    var text = el.getAttribute('data-house-text') || 'Reach PC gamers who are ready to buy.';
    el.innerHTML = '<aside class="sgsp" aria-label="Advertise here"><a class="sgsp-a sgsp-house" href="/advertise.html">' +
      '<span class="sgsp-tx"><span class="sgsp-lab">' + esc(label) + '</span><strong>' + esc(title) + '</strong><span>' + esc(text) + '</span></span>' +
      '<span class="sgsp-cta">See rates</span></a></aside>';
  }

  var turn = Math.floor(Date.now() / 3600000);   // several booked sponsors take turns, one per hour
  fetch('/sponsors.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; }).then(function (list) {
    slots.forEach(function (el) {
      var slot = el.getAttribute('data-sponsor-slot');
      var now = live(list, slot);
      if (now.length) render(el, now[turn % now.length]);
      else if (el.hasAttribute('data-house')) house(el);
    });
  });
})();
