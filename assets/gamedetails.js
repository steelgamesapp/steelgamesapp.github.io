/* Game details for SteelGames pages.
   1) Everywhere: the trailer player and the screenshot viewer (progressive: the pages work as plain links without JavaScript).
   2) On the live /deal/ page: SGDetails.mount() adds the "Works best on" strip, About, trailer, screenshots and details from
      /data/meta/<steam id>.json (written by the daily build) or, for games not tracked yet, from the Steam proxy worker.
   The static /game/ pages are rendered by tools/steam_meta.py with the same markup. Keep the two in step. */
(function () {
  if (window.SGDetails) return;
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const ICONS = {"pc": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><rect x=\"2.5\" y=\"4\" width=\"19\" height=\"12.5\" rx=\"2\"/><path d=\"M8 20.5h8M12 16.5v4\"/></svg>", "handheld": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><rect x=\"1.5\" y=\"6.5\" width=\"21\" height=\"11\" rx=\"4\"/><path d=\"M6.5 10.5v3M5 12h3\"/><circle cx=\"16.5\" cy=\"11\" r=\".9\"/><circle cx=\"18.5\" cy=\"13\" r=\".9\"/></svg>", "ctl": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M7 8h10a4 4 0 0 1 4 4v1a3 3 0 0 1-5.2 2L14 13h-4l-1.8 2A3 3 0 0 1 3 13v-1a4 4 0 0 1 4-4z\"/></svg>", "kbm": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><rect x=\"2\" y=\"7\" width=\"14\" height=\"10\" rx=\"2\"/><path d=\"M5 10.5h1M8.5 10.5h1M12 10.5h1M5.5 14h7\"/><rect x=\"18\" y=\"5\" width=\"4\" height=\"7\" rx=\"2\"/></svg>", "players": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><circle cx=\"9\" cy=\"8\" r=\"3.2\"/><path d=\"M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6\"/><circle cx=\"17.5\" cy=\"9\" r=\"2.4\"/><path d=\"M17 14.2c2.4.3 4.5 2.2 4.5 4.8\"/></svg>", "vr": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M3 8.5h18a1 1 0 0 1 1 1V15a2 2 0 0 1-2 2h-3.5l-1.7-2.5h-4.6L8.5 17H5a2 2 0 0 1-2-2V9.5a1 1 0 0 1 0-1z\"/></svg>"};
  const PLAY = "<svg width=\"30\" height=\"30\" viewBox=\"0 0 24 24\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M8 5.5v13a1 1 0 0 0 1.5.9l10.5-6.5a1 1 0 0 0 0-1.8L9.5 4.6A1 1 0 0 0 8 5.5z\"/></svg>";

  /* ---------- trailer player ---------- */
  let hlsP = null;
  const loadHls = () => (hlsP = hlsP || new Promise((res, rej) => {
    if (window.Hls) return res(window.Hls);
    const s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.5.17/hls.min.js';
    s.onload = () => res(window.Hls); s.onerror = rej; document.head.appendChild(s);
  }));
  async function playTrailer(btn) {
    const wrap = document.createElement('div');
    wrap.className = 'trailer playing';
    const v = document.createElement('video');
    v.controls = true; v.autoplay = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.preload = 'auto';
    if (btn.dataset.poster) v.poster = btn.dataset.poster;
    wrap.appendChild(v); btn.replaceWith(wrap);
    const hls = btn.dataset.hls, mp4 = btn.dataset.mp4;
    let fell = false;
    const fallback = () => { if (fell || !mp4) return; fell = true; v.src = mp4; v.play().catch(() => {}); };
    if (hls && v.canPlayType('application/vnd.apple.mpegurl')) { v.src = hls; v.addEventListener('error', fallback, { once: true }); }
    else if (hls) {
      try {
        const Hls = await loadHls();
        if (Hls && Hls.isSupported()) {
          const h = new Hls(); h.loadSource(hls); h.attachMedia(v);
          h.on(Hls.Events.ERROR, (e, d) => { if (d && d.fatal) { h.destroy(); fallback(); } });
        } else fallback();
      } catch (e) { fallback(); }
    } else fallback();
    v.play().catch(() => {});
  }

  /* ---------- screenshot viewer ---------- */
  function lightbox(list, i, name) {
    let n = i;
    const box = document.createElement('div');
    box.className = 'lb'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Screenshots of ' + name);
    box.innerHTML = '<img alt=""><button type="button" class="lb-x" aria-label="Close">&times;</button>' +
      (list.length > 1 ? '<button type="button" class="lb-p" aria-label="Previous screenshot">&lsaquo;</button><button type="button" class="lb-n" aria-label="Next screenshot">&rsaquo;</button>' : '') + '<div class="lb-c"></div>';
    const img = box.querySelector('img'), cap = box.querySelector('.lb-c');
    const show = (k) => { n = (k + list.length) % list.length; img.src = list[n]; img.alt = 'Screenshot ' + (n + 1) + ' of ' + name; cap.textContent = (n + 1) + ' of ' + list.length; };
    const close = () => { document.removeEventListener('keydown', key); box.remove(); document.body.style.overflow = ''; };
    const key = (e) => { if (e.key === 'Escape') close(); else if (e.key === 'ArrowRight') show(n + 1); else if (e.key === 'ArrowLeft') show(n - 1); };
    box.addEventListener('click', (e) => {
      if (e.target.closest('.lb-x') || e.target === box) close();
      else if (e.target.closest('.lb-p')) show(n - 1);
      else if (e.target.closest('.lb-n') || e.target === img) show(n + 1);
    });
    document.addEventListener('keydown', key);
    document.body.style.overflow = 'hidden'; document.body.appendChild(box); show(i);
    box.querySelector('.lb-x').focus();
  }

  document.addEventListener('click', (e) => {
    const t = e.target.closest('button.trailer');
    if (t) { e.preventDefault(); playTrailer(t); return; }
    const a = e.target.closest('[data-gallery] a[data-full]');
    if (a) {
      e.preventDefault();
      const g = a.closest('[data-gallery]'), links = [...g.querySelectorAll('a[data-full]')];
      lightbox(links.map((x) => x.dataset.full), links.indexOf(a), g.dataset.name || 'this game');
    }
  });

  /* ---------- the live /deal/ page ---------- */
  const GENRE_CAT = { Action: 'action', Adventure: 'adventure', RPG: 'rpg', Strategy: 'strategy', Simulation: 'sim', Racing: 'racing', Sports: 'sports' };

  function bestOn(m) {
    const p = m.platforms || {}, feats = m.features || [], deck = m.deck || 0;
    let plats = [['windows', 'Windows PC'], ['mac', 'Mac'], ['linux', 'Linux']].filter((x) => p[x[0]]).map((x) => x[1]);
    if (!plats.length) plats = ['Windows PC'];
    const best = [plats[0]];
    if (deck === 3) best.push('Steam Deck'); else if (deck === 2) best.push('Steam Deck (playable)');
    const tiles = [['pc', 'Platform', plats.join(' · '), 'good']];
    if (deck === 3) tiles.push(['handheld', 'Handheld', 'Steam Deck Verified, so it should run well on handheld PCs like the Steam Deck and ROG Ally.', 'good']);
    else if (deck === 2) tiles.push(['handheld', 'Handheld', 'Steam Deck Playable. Works on handheld PCs, but may need small tweaks.', 'ok']);
    else if (deck === 1) tiles.push(['handheld', 'Handheld', 'Not supported on Steam Deck. Best on a desktop or laptop.', 'bad']);
    else tiles.push(['handheld', 'Handheld', 'Steam Deck rating not available yet.', '']);
    if (m.controller === 'full') tiles.push(['ctl', 'Controls', 'Full controller support. Plays well on a gamepad or keyboard and mouse.', 'good']);
    else if (m.controller === 'partial') tiles.push(['ctl', 'Controls', 'Partial controller support. Keyboard and mouse is the safer pick.', 'ok']);
    else tiles.push(['kbm', 'Controls', 'Made for keyboard and mouse.', '']);
    const names = [['Single-player', 'Single-player'], ['Co-op', 'Co-op'], ['Online Co-op', 'Online co-op'], ['Shared/Split Screen Co-op', 'Split-screen co-op'], ['Multi-player', 'Multiplayer'], ['Online PvP', 'Online PvP'], ['MMO', 'MMO']];
    let modes = [...new Set(names.filter((n) => feats.includes(n[0])).map((n) => n[1]))].slice(0, 3);
    if (['VR Supported', 'VR Support', 'VR Only'].some((f) => feats.includes(f))) modes.push('VR');
    if (modes.length) tiles.push([modes.length === 1 && modes[0] === 'VR' ? 'vr' : 'players', 'Play style', modes.join(' · '), '']);
    return ['Works best on ' + best.join(' and '), tiles];
  }

  function strip(m) {
    const [head, tiles] = m ? bestOn(m) : ['Works best on Windows PC', [['pc', 'Platform', 'Windows PC', 'good']]];
    return '<div class="wbstrip" role="group" aria-label="Works best on"><p class="wbhead">' + esc(head) + '</p><div class="wbtiles">' +
      tiles.map((t) => '<div class="wbt ' + esc(t[3]) + '"><span class="wbi">' + ICONS[t[0]] + '</span><span class="wbx"><small>' + esc(t[1]) + '</small>' + esc(t[2]) + '</span></div>').join('') + '</div></div>';
  }

  function about(m) {
    const b = (m.blurb || '').trim();
    if (!b) return '';
    return '<section class="block about"><div class="wrap"><h2>About ' + esc(m.name || 'this game') + '</h2><div class="prose">' +
      b.split(/\n\n/).filter((x) => x.trim()).map((x) => '<p>' + esc(x.trim()) + '</p>').join('') + '</div></div></section>';
  }

  function media(m) {
    const name = m.name || 'this game';
    const shots = (m.shots || []).filter((s) => s.t && s.f), movies = (m.movies || []).filter((v) => v.hls || v.mp4);
    if (!shots.length && !movies.length) return '';
    let trailer = '';
    if (movies.length) {
      const mv = movies[0], poster = (shots[0] && shots[0].t) || mv.t || '';
      trailer = '<button type="button" class="trailer" data-hls="' + esc(mv.hls) + '" data-mp4="' + esc(mv.mp4) + '" data-poster="' + esc(poster) + '" aria-label="Play the ' + esc(name) + ' trailer"><img src="' + esc(poster) + '" alt="" loading="lazy" width="600" height="338"><span class="play">' + PLAY + '</span><span class="tcap">Watch the trailer</span></button>';
    }
    const cells = shots.map((s, i) => '<a href="' + esc(s.f) + '" target="_blank" rel="noopener" data-full="' + esc(s.f) + '"><img src="' + esc(s.t) + '" alt="Screenshot ' + (i + 1) + ' of ' + esc(name) + '" loading="lazy" width="300" height="169"></a>').join('');
    return '<section class="block" id="media"><div class="wrap"><h2>Trailer and screenshots</h2><div class="media" data-gallery data-name="' + esc(name) + '">' + trailer + '<div class="shots">' + cells + '</div></div>' +
      '<p class="fine">Trailer and screenshots are from the publisher. Tap a screenshot to enlarge it.</p></div></section>';
  }

  function specs(m) {
    const mn = Object.fromEntries(m.min || []), rc = Object.fromEntries(m.rec || []);
    const labels = [...new Set(Object.keys(mn).concat(Object.keys(rc)))];
    if (!labels.length) return '';
    return '<h3 class="sub">PC requirements</h3><div class="scroll"><table class="specs"><thead><tr><th></th><th>Minimum</th><th>Recommended</th></tr></thead><tbody>' +
      labels.map((l) => '<tr><th scope="row">' + esc(l) + '</th><td>' + esc(mn[l] || '-') + '</td><td>' + esc(rc[l] || '-') + '</td></tr>').join('') + '</tbody></table></div>';
  }

  function details(m) {
    let tags = (m.genres || []).map((g) => GENRE_CAT[g] ? '<a class="tag" href="/games.html#cat=' + GENRE_CAT[g] + '">' + esc(g) + '</a>' : '<span class="tag">' + esc(g) + '</span>').join('') +
      (m.features || []).map((f) => '<span class="tag feat">' + esc(f) + '</span>').join('');
    const rows = [];
    if ((m.dev || []).length) rows.push(['Developer', m.dev.join(', ')]);
    if ((m.pub || []).length) rows.push(['Publisher', m.pub.join(', ')]);
    if (m.released) rows.push(['Released', m.released]);
    if (m.meta) rows.push(['Metacritic', m.meta + ' / 100']);
    if ((m.langs || []).length) rows.push(['Languages', m.langs.length + ': ' + m.langs.slice(0, 6).join(', ') + (m.langs.length > 6 ? ' and more' : '')]);
    const drows = rows.map((r) => '<tr><th scope="row">' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>').join('');
    let out = '';
    if (tags) out += '<section class="block"><div class="wrap"><h2>Categories</h2><div class="tags">' + tags + '</div></div></section>';
    if (drows || (m.min || []).length || (m.rec || []).length) out += '<section class="block"><div class="wrap"><h2>Details</h2>' + (drows ? '<table class="specs det"><tbody>' + drows + '</tbody></table>' : '') + specs(m) + '</div></section>';
    return out;
  }

  async function load(sid) {
    if (!/^\d+$/.test(sid || '') || sid === '0') return null;
    try {
      const r = await fetch('/data/meta/' + sid + '.json');
      if (r.ok) { const j = await r.json(); if (j && j.d) return j.d; }
    } catch (e) { /* fall through to the proxy */ }
    const P = window.SG && window.SG.STEAM_PROXY;
    if (P) {
      try {
        const r = await fetch(P + '?kind=app&id=' + encodeURIComponent(sid));
        if (r.ok) { const j = await r.json(); if (j && j.d) return j.d; }
      } catch (e) { /* the page works without details */ }
    }
    return null;
  }

  window.SGDetails = {
    strip, bestOn,
    /* Fills #wbstrip (and #glede) near the title and #gdetails below the prices. Safe to call for any game. */
    async mount(sid) {
      const s = document.getElementById('wbstrip'), l = document.getElementById('glede'), d = document.getElementById('gdetails');
      const m = await load(sid);
      if (s) s.innerHTML = strip(m);
      if (!m) return;
      if (l && m.desc) { l.textContent = m.desc; l.hidden = false; }
      if (d) d.innerHTML = about(m) + media(m) + details(m);
    },
  };
})();
