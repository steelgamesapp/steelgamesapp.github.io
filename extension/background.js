// Looks up prices from CheapShark and answers the content script.
const API = 'https://www.cheapshark.com/api/1.0';

async function stores() {
  const { sgStores } = await chrome.storage.local.get('sgStores');
  if (sgStores && Date.now() - sgStores.at < 7 * 864e5) return sgStores.map;
  const list = await (await fetch(API + '/stores')).json();
  const map = Object.fromEntries(list.map((s) => [s.storeID, s.storeName]));
  await chrome.storage.local.set({ sgStores: { at: Date.now(), map } });
  return map;
}

async function lookup(appid) {
  const key = 'sg_' + appid;
  const cached = (await chrome.storage.local.get(key))[key];
  if (cached && Date.now() - cached.at < 3 * 36e5) return cached.data;
  const found = await (await fetch(API + '/games?steamAppID=' + encodeURIComponent(appid))).json();
  if (!found.length) return { notFound: true };
  const id = found[0].gameID;
  const g = await (await fetch(API + '/games?id=' + id)).json();
  const names = await stores();
  const deals = (g.deals || []).slice().sort((a, b) => +a.price - +b.price);
  if (!deals.length) return { notFound: true };
  const data = {
    id, title: g.info && g.info.title,
    best: +deals[0].price, regular: +deals[0].retailPrice, store: names[deals[0].storeID] || 'a store', dealID: deals[0].dealID,
    low: g.cheapestPriceEver ? +g.cheapestPriceEver.price : null,
    lowDate: g.cheapestPriceEver ? g.cheapestPriceEver.date : null,
    stores: deals.length,
  };
  await chrome.storage.local.set({ [key]: { at: Date.now(), data } });
  return data;
}

chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (msg && msg.type === 'price') {
    lookup(msg.appid).then(reply).catch(() => reply({ error: true }));
    return true;
  }
});
