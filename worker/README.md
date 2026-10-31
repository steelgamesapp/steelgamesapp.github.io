# Steam import proxy

Lets visitors import their Steam wishlist (and owned games) into SteelGames.

1. Create a free Cloudflare account, then Workers & Pages > Create > Worker.
2. Paste in `steam-proxy.js` and deploy. Copy the worker URL (like `https://steelgames-steam.<name>.workers.dev`).
3. Optional, for owned games: get a Steam Web API key at https://steamcommunity.com/dev/apikey and add it to the worker as a secret named `STEAM_API_KEY`.
4. In `assets/shop.js`, set `SG.STEAM_PROXY = 'https://your-worker-url'`. The "Import from Steam" box then appears on the wishlist and collection pages.

Wishlist import needs no key. Profiles and game details must be public on Steam.
