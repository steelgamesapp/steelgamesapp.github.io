/* SteelGames: send every visitor to their own country's Amazon store.

   What this does
   - Works out the visitor's country (Cloudflare's free country lookup, remembered for a week, with the browser language
     as a backup), lets them change it, and remembers a manual choice in this browser.
   - Rewrites each Amazon link on the page. A product link becomes a search for that product's name on the visitor's local
     store, because a fixed product page often does not exist in another country.
   - US visitors see the original links, untouched.

   TAGS: put our Amazon Associates tracking ID for a country here once we have joined that country's program.
   A blank tag means the link still works for the shopper but earns us nothing. Never put the US tag on another
   country's store: Amazon does not accept it there. */
(() => {
  'use strict';
  if (window.SGGeo) return;

  const TAGS = {
    US: 'steelgames-20',
    CA: '', MX: '', BR: '',
    GB: '', IE: '', DE: '', FR: '', IT: '', ES: '', NL: '', SE: '', PL: '', BE: '',
    TR: '', AE: '', SA: '', EG: '',
    IN: '', JP: '', AU: '', SG: '',
  };

  /* country code: [Amazon site, country name] */
  const SITES = {
    US: ['www.amazon.com', 'United States'],
    CA: ['www.amazon.ca', 'Canada'],
    MX: ['www.amazon.com.mx', 'Mexico'],
    BR: ['www.amazon.com.br', 'Brazil'],
    GB: ['www.amazon.co.uk', 'United Kingdom'],
    IE: ['www.amazon.ie', 'Ireland'],
    DE: ['www.amazon.de', 'Germany'],
    FR: ['www.amazon.fr', 'France'],
    IT: ['www.amazon.it', 'Italy'],
    ES: ['www.amazon.es', 'Spain'],
    NL: ['www.amazon.nl', 'Netherlands'],
    SE: ['www.amazon.se', 'Sweden'],
    PL: ['www.amazon.pl', 'Poland'],
    BE: ['www.amazon.com.be', 'Belgium'],
    TR: ['www.amazon.com.tr', 'Turkey'],
    AE: ['www.amazon.ae', 'United Arab Emirates'],
    SA: ['www.amazon.sa', 'Saudi Arabia'],
    EG: ['www.amazon.eg', 'Egypt'],
    IN: ['www.amazon.in', 'India'],
    JP: ['www.amazon.co.jp', 'Japan'],
    AU: ['www.amazon.com.au', 'Australia'],
    SG: ['www.amazon.sg', 'Singapore'],
  };

  /* Countries with no store of their own go to the nearest store that ships there. Anywhere else falls back to Amazon.com. */
  const NEAREST = {
    AT: 'DE', CH: 'DE', LI: 'DE', DK: 'DE', FI: 'DE', CZ: 'DE', SK: 'DE', HU: 'DE', RO: 'DE', BG: 'DE', GR: 'DE', HR: 'DE',
    SI: 'DE', EE: 'DE', LV: 'DE', LT: 'DE', CY: 'DE', MT: 'DE', LU: 'FR', PT: 'ES', NZ: 'AU',
  };

  /* Backup guess from the browser's timezone, used only if the country lookup fails and the language has no region. */
  const TZ = {
    'Europe/London': 'GB', 'Europe/Dublin': 'IE', 'Europe/Berlin': 'DE', 'Europe/Paris': 'FR', 'Europe/Madrid': 'ES',
    'Europe/Rome': 'IT', 'Europe/Amsterdam': 'NL', 'Europe/Stockholm': 'SE', 'Europe/Warsaw': 'PL', 'Europe/Brussels': 'BE',
    'Europe/Istanbul': 'TR', 'Asia/Dubai': 'AE', 'Asia/Riyadh': 'SA', 'Africa/Cairo': 'EG', 'Asia/Kolkata': 'IN',
    'Asia/Calcutta': 'IN', 'Asia/Tokyo': 'JP', 'Asia/Singapore': 'SG', 'America/Mexico_City': 'MX', 'America/Sao_Paulo': 'BR',
    'America/Toronto': 'CA', 'America/Vancouver': 'CA', 'America/Edmonton': 'CA', 'America/Winnipeg': 'CA', 'America/Halifax': 'CA',
    'Australia/Sydney': 'AU', 'Australia/Melbourne': 'AU', 'Australia/Brisbane': 'AU', 'Australia/Perth': 'AU', 'Australia/Adelaide': 'AU',
    'Pacific/Auckland': 'NZ',
  };

  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } },
  };
  const SS = {
    get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* storage blocked */ } },
  };
  const shortHost = (c) => 'Amazon' + SITES[c][0].replace(/^www\.amazon/, '');       /* Amazon.co.uk */
  const countryName = (cc) => {
    if (SITES[cc]) return SITES[cc][1];
    try { return new Intl.DisplayNames(['en'], { type: 'region' }).of(cc) || cc; } catch (e) { return cc; }
  };
  const resolve = (cc) => {
    cc = String(cc || '').toUpperCase();
    if (cc === 'UK') cc = 'GB';
    if (SITES[cc]) return cc;
    return NEAREST[cc] || 'US';
  };
  const mapped = (cc) => { cc = String(cc || '').toUpperCase(); return !!(SITES[cc] || NEAREST[cc] || cc === 'UK'); };

  let region = 'US', detected = '', manual = false, found = 0;
  const saved = LS.get('sg_region');
  if (saved && SITES[saved]) { region = saved; manual = true; }
  try {
    const c = JSON.parse(LS.get('sg_cc') || 'null');
    if (c && c.c && Date.now() - c.t < 7 * 864e5) detected = c.c;
  } catch (e) { /* ignore */ }
  if (!manual && detected) region = resolve(detected);

  const emit = () => { try { document.dispatchEvent(new CustomEvent('sg:geo', { detail: { region, detected, manual } })); } catch (e) { /* old browser */ } };

  /* ---------- country lookup ---------- */
  const lookup = () => new Promise((done) => {
    let over = false;
    const fin = (cc) => { if (!over) { over = true; done(cc); } };
    const t = setTimeout(() => fin(''), 3500);
    try {
      fetch('https://www.cloudflare.com/cdn-cgi/trace', { cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer' })
        .then((r) => r.text())
        .then((x) => { clearTimeout(t); const m = /^loc=([A-Z0-9]{2})$/m.exec(x); fin(m ? m[1] : ''); })
        .catch(() => { clearTimeout(t); fin(''); });
    } catch (e) { clearTimeout(t); fin(''); }
  });
  const guess = () => {
    try {
      const langs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ''];
      for (const l of langs) { const m = /[-_]([A-Za-z]{2})$/.exec(l); if (m) return m[1].toUpperCase(); }
      return TZ[Intl.DateTimeFormat().resolvedOptions().timeZone] || '';
    } catch (e) { return ''; }
  };

  /* ---------- link rewriting ---------- */
  const AMZ = /^(www\.)?amazon\.com$/i;
  const clean = (s) => String(s || '').replace(/\s+/g, ' ').trim();
  const GENERIC = /^(see|view|check|shop|buy|get|compare|find|search|visit)\b/i;

  const nameFor = (a) => {
    const given = clean(a.dataset.sgName);
    if (given) return given;
    const img = a.querySelector('img[alt]');
    if (img && clean(img.alt)) return clean(img.alt);
    const c = a.cloneNode(true);
    c.querySelectorAll('small,svg,img').forEach((x) => x.remove());
    const own = clean(c.textContent);
    if (own.length > 3 && !GENERIC.test(own) && !/amazon/i.test(own)) return own;
    const box = a.closest('article, tr, li, .scard');
    if (box) {
      if (box.tagName === 'TR') { const td = box.querySelectorAll('td')[1]; if (td) return clean(td.textContent); }
      const h = box.querySelector('h4, h3, h2');
      if (h) return clean(h.textContent);
    }
    return '';
  };

  const relabel = (a, code) => {
    [...a.childNodes].filter((n) => n.nodeType === 3 && /Amazon/.test(n._sgT !== undefined ? n._sgT : n.nodeValue)).forEach((n) => {
      if (n._sgT === undefined) n._sgT = n.nodeValue;
      n.nodeValue = code === 'US' ? n._sgT : n._sgT.replace(/Amazon(?!\.)/, shortHost(code));
    });
  };

  const urlFor = (code, q, asin) => {
    const host = SITES[code][0], tag = TAGS[code] || '';
    const t = tag ? 'tag=' + encodeURIComponent(tag) : '';
    if (q) return 'https://' + host + '/s?k=' + encodeURIComponent(q).replace(/%20/g, '+') + (t ? '&' + t : '');
    if (asin) return 'https://' + host + '/dp/' + asin + (t ? '?' + t : '');
    return 'https://' + host + '/' + (t ? '?' + t : '');
  };

  const apply = () => {
    document.querySelectorAll('a[href*="amazon.com"], a[data-sg-orig]').forEach((a) => {
      if (a.dataset.sgGeo === region) return;
      const orig = a.dataset.sgOrig || a.getAttribute('href');
      let u;
      try { u = new URL(orig, location.href); } catch (e) { return; }
      if (!AMZ.test(u.hostname)) return;
      a.dataset.sgOrig = orig;
      if (region === 'US') {
        a.setAttribute('href', orig);
      } else {
        const m = /\/dp\/([A-Za-z0-9]{10})/.exec(u.pathname);
        const q = u.searchParams.get('k') || nameFor(a);
        a.setAttribute('href', urlFor(region, q, m ? m[1].toUpperCase() : ''));
      }
      relabel(a, region);
      a.dataset.sgGeo = region;
    });
    found = document.querySelectorAll('a[data-sg-geo]').length;
  };

  /* ---------- picker UI: a slim bar for visitors outside the US, and a selector in the footer ---------- */
  const css = document.createElement('style');
  css.textContent =
    '.sg-geo-bar{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;justify-content:center;padding:10px 44px 10px 16px;position:relative;' +
    'background:#261B5C;border-bottom:1px solid #4A37A8;color:#fff;font:600 14px/1.45 Inter,system-ui,sans-serif;text-align:center}' +
    '.sg-geo-bar[hidden]{display:none}.sg-geo-bar a{color:#FFB020}.sg-geo-bar label{display:inline-flex;align-items:center;gap:8px}' +
    '.sg-geo-x{position:absolute;right:8px;top:50%;transform:translateY(-50%);width:32px;height:32px;border:0;border-radius:8px;background:transparent;color:#fff;font:700 20px/1 sans-serif;cursor:pointer}' +
    '.sg-geo-x:hover{background:#35288A}' +
    '.sg-geo-sel{background:#1A1342;color:#fff;border:1px solid #4A37A8;border-radius:8px;padding:6px 10px;font:600 14px Inter,system-ui,sans-serif;max-width:78vw}' +
    '.sg-geo-foot{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin:14px 0;font:600 14px Inter,system-ui,sans-serif;color:#DAD4F7}' +
    '.sg-geo-foot label{display:inline-flex;align-items:center;gap:8px}';
  document.head.appendChild(css);

  const mkSelect = () => {
    const s = document.createElement('select');
    s.className = 'sg-geo-sel';
    s.setAttribute('aria-label', 'Choose your country for Amazon links');
    Object.keys(SITES).sort((x, y) => SITES[x][1].localeCompare(SITES[y][1])).forEach((c) => {
      const o = document.createElement('option');
      o.value = c; o.textContent = SITES[c][1] + ' (' + shortHost(c) + ')';
      s.appendChild(o);
    });
    s.value = region;
    s.addEventListener('change', () => api.set(s.value));
    return s;
  };

  let bar = null, barMsg = null;
  const ui = () => {
    document.querySelectorAll('.sg-geo-sel').forEach((s) => { s.value = region; });
    const dismissed = SS.get('sg_geo_x') === '1';
    const fallback = !manual && detected && detected !== 'US' && !mapped(detected);
    const show = found > 0 && !dismissed && !/^\/international/.test(location.pathname) && (region !== 'US' || fallback);
    if (show && !bar) {
      const header = document.querySelector('.site-header') || document.querySelector('header');
      if (!header) return;
      bar = document.createElement('div');
      bar.className = 'sg-geo-bar';
      bar.setAttribute('role', 'region');
      bar.setAttribute('aria-label', 'Amazon store for your country');
      barMsg = document.createElement('span');
      const lab = document.createElement('label');
      lab.appendChild(document.createTextNode('Change country '));
      lab.appendChild(mkSelect());
      const more = document.createElement('a');
      more.href = '/international.html'; more.textContent = 'Shop from your country';
      const x = document.createElement('button');
      x.type = 'button'; x.className = 'sg-geo-x'; x.setAttribute('aria-label', 'Dismiss'); x.textContent = '×';
      x.addEventListener('click', () => { SS.set('sg_geo_x', '1'); bar.hidden = true; });
      bar.append(barMsg, lab, more, x);
      header.insertAdjacentElement('afterend', bar);
    }
    if (bar) {
      bar.hidden = !show;
      if (region !== 'US') {
        barMsg.textContent = 'Amazon links on this page go to ' + shortHost(region) + ' for shoppers in ' + SITES[region][1] + '.';
      } else if (fallback) {
        barMsg.textContent = 'Amazon has no store in ' + countryName(String(detected).toUpperCase()) +
          ', so these links go to Amazon.com, which ships many items abroad. Check delivery before you order.';
      }
    }
  };

  const footer = () => {
    const w = document.querySelector('.site-footer .wrap');
    if (!w || w.querySelector('.sg-geo-foot')) return;
    const d = document.createElement('div');
    d.className = 'sg-geo-foot';
    const lab = document.createElement('label');
    lab.appendChild(document.createTextNode('Shopping from '));
    lab.appendChild(mkSelect());
    const a = document.createElement('a');
    a.href = '/international.html'; a.textContent = 'Shop gear from your country';
    d.append(lab, a);
    const p = w.querySelector('p');
    if (p) w.insertBefore(d, p); else w.appendChild(d);
  };

  /* ---------- public API (the "shop from your country" page uses it) ---------- */
  const api = window.SGGeo = {
    sites: SITES,
    region: () => region,
    detected: () => detected,
    shortHost,
    url: (q, code) => urlFor(SITES[code || region] ? (code || region) : 'US', q, ''),
    set(code) {
      if (!SITES[code]) return;
      region = code; manual = true;
      LS.set('sg_region', code);
      apply(); ui(); emit();
    },
  };

  let queued = false;
  const queue = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; apply(); ui(); }); };

  const start = () => {
    apply(); footer(); ui(); emit();
    new MutationObserver(queue).observe(document.documentElement, { childList: true, subtree: true });
    if (!manual && !detected) {
      lookup().then((cc) => {
        if (cc) LS.set('sg_cc', JSON.stringify({ c: cc, t: Date.now() }));
        detected = cc || guess();
        if (!manual) region = resolve(detected);
        apply(); ui(); emit();
      });
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
