// SteelGames Steam import proxy (Cloudflare Worker).
// Steam blocks direct calls from a web page, so the site asks this tiny worker instead.
// It returns only a list of Steam app ids: {"appids":[220, 400, ...]}. Nothing is stored.
//
// Deploy: see worker/README.md. Optional secret STEAM_API_KEY enables "owned games" import.

const ORIGINS = ['https://steelgamesapp.com', 'https://www.steelgamesapp.com'];

function cors(origin) {
  return {
    'Access-Control-Allow-Origin': ORIGINS.includes(origin) ? origin : ORIGINS[0],
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=300',
    'Vary': 'Origin',
  };
}

const json = (obj, status, origin) => new Response(JSON.stringify(obj), { status, headers: cors(origin) });

async function resolveSteamId(profile) {
  const p = profile.trim().replace(/^https?:\/\/steamcommunity\.com\/(id|profiles)\//i, '').replace(/\/+$/, '');
  if (/^\d{17}$/.test(p)) return p;
  if (!/^[A-Za-z0-9_-]{2,64}$/.test(p)) return null;
  const r = await fetch('https://steamcommunity.com/id/' + encodeURIComponent(p) + '/?xml=1');
  const t = await r.text();
  const m = /<steamID64>(\d{17})<\/steamID64>/.exec(t);
  return m ? m[1] : null;
}

export default {
  async fetch(req, env) {
    const origin = req.headers.get('Origin') || '';
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(origin) });
    const u = new URL(req.url);
    const kind = u.searchParams.get('kind'), profile = u.searchParams.get('profile') || '';
    if (!['wishlist', 'owned'].includes(kind) || !profile) return json({ error: 'Missing profile.' }, 400, origin);

    const id = await resolveSteamId(profile);
    if (!id) return json({ error: 'Steam profile not found. Check the name or ID.' }, 404, origin);

    try {
      if (kind === 'wishlist') {
        const r = await fetch('https://api.steampowered.com/IWishlistService/GetWishlist/v1/?steamid=' + id);
        if (!r.ok) return json({ error: 'Steam did not return a wishlist. Make sure the profile and game details are public.' }, 502, origin);
        const j = await r.json();
        const items = (j.response && j.response.items) || [];
        return json({ appids: items.map((i) => i.appid) }, 200, origin);
      }
      if (!env.STEAM_API_KEY) return json({ error: 'Owned-games import is not switched on yet.' }, 501, origin);
      const r = await fetch('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key=' + env.STEAM_API_KEY + '&steamid=' + id + '&include_appinfo=0');
      if (!r.ok) return json({ error: 'Steam did not return your games.' }, 502, origin);
      const j = await r.json();
      const games = (j.response && j.response.games) || [];
      if (!games.length) return json({ error: 'No games found. Set Game details to public in your Steam privacy settings.' }, 404, origin);
      return json({ appids: games.map((g) => g.appid) }, 200, origin);
    } catch (e) {
      return json({ error: 'Steam is not answering right now. Try again in a minute.' }, 502, origin);
    }
  },
};
