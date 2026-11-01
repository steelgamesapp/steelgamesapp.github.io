/* "Best gear for this game" on the live price page (/deal/).
   Same rules and products as the static game pages: both read tools/gear_rules.json (published as /data/gear.json).
   Games we already track use their Steam-based picks; any other game is matched by keywords in its title. */
(function () {
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>';
  let rulesP = null;
  const rules = () => (rulesP = rulesP || fetch('/data/gear.json').then((r) => r.json()));

  function styles(R, title) {
    let found = R.order.filter((p) => R.keywords[p] && new RegExp(R.keywords[p], 'i').test(title || ''));
    if (found.includes('competitive')) found = found.filter((p) => p !== 'shooter');
    return found.length ? found : ['general'];
  }

  function slotsFor(R, title) {
    const st = styles(R, title), picked = [], groups = new Set();
    const add = (s) => {
      if (picked.includes(s) || !R.slots[s]) return;
      const g = R.groups[s];
      if (g && groups.has(g)) return;
      if (g) groups.add(g);
      picked.push(s);
    };
    const lists = st.slice(0, 2).map((p) => R.profiles[p]);
    const n = Math.max(...lists.map((l) => l.length));
    for (let i = 0; i < n; i++) lists.forEach((l) => { if (i < l.length) add(l[i]); });
    if (st.some((p) => ['competitive', 'coop', 'sports'].includes(p))) add('mic');
    for (const s of R.profiles.general) { if (picked.length >= 4) break; add(s); }
    return [picked.slice(0, R.max_slots), st];
  }

  function card(R, id, title) {
    const s = R.slots[id], v = R.items[s.value], up = s.up ? R.items[s.up] : null;
    const rel = 'target="_blank" rel="sponsored nofollow noopener"';
    const upg = up ? '<a class="gup" href="' + esc(up.url) + '" ' + rel + '><img src="' + esc(up.img) + '" alt="" loading="lazy" width="56" height="56" onerror="this.style.visibility=\'hidden\'"><span><small>Upgrade pick</small>' + esc(up.name) + '</span></a>' : '';
    return '<article class="gcar"><p class="gl">' + esc(s.label) + '</p>' +
      '<a class="gimg" href="' + esc(v.url) + '" ' + rel + ' tabindex="-1" aria-hidden="true"><img src="' + esc(v.img) + '" alt="' + esc(v.name) + '" loading="lazy" width="400" height="300" onerror="this.closest(\'.gimg\').classList.add(\'empty\')"></a>' +
      '<div class="gb"><span class="gtag">Best value</span><h3>' + esc(v.name) + '</h3><p>' + esc(s.why.split('{t}').join(title)) + '</p>' +
      '<a class="btn gbuy" href="' + esc(v.url) + '" ' + rel + '>See price on Amazon' + ARROW + '</a>' + upg + '</div></article>';
  }

  window.SGGear = {
    async render(mount, gid, title) {
      try {
        const R = await rules();
        let [picks, st] = slotsFor(R, title);
        if (R.games && R.games[gid] && R.games[gid].length) picks = R.games[gid];
        const chips = st.slice(0, 3).map((p) => '<span class="tag">' + esc(R.names[p] || p) + '</span>').join('');
        mount.innerHTML = '<section class="block gear"><div class="wrap"><h2>Best gear for ' + esc(title) + '</h2>' +
          '<p class="lede gear-lede">Picked for how this game plays, with a best-value choice and an upgrade for each.</p>' +
          '<div class="tags">' + chips + '</div><div class="gear-grid">' + picks.map((s) => card(R, s, title)).join('') + '</div>' +
          '<p class="fine">Prices change often, so check the latest price on Amazon. SteelGames may earn a small commission on purchases.</p></div></section>';
      } catch (e) { /* gear is a bonus; the price page works without it */ }
    },
  };
})();
