#!/usr/bin/env python3
"""Daily deal bot: posts today's top PC game deals to Bluesky, Telegram and Discord, each linking to SteelGames.

Run once a day by .github/workflows/deal-bot.yml. Standard library only.
Each channel turns on by itself once its secrets are added in GitHub (Settings > Secrets and variables > Actions):
  Bluesky:  BLUESKY_HANDLE (e.g. steelgames.bsky.social) and BLUESKY_APP_PASSWORD (Bluesky > Settings > App passwords)
  Telegram: TELEGRAM_BOT_TOKEN (from @BotFather) and TELEGRAM_CHAT_ID (e.g. @steelgamesdeals, bot added as channel admin)
  Discord:  DISCORD_WEBHOOK_URL (channel > Edit > Integrations > Webhooks)
A channel with no secrets is skipped. The same game is not posted again for 7 days (data/posted.json).

Usage: python3 tools/deal_bot.py [--dry-run] [--sample deals.json]
"""
import html
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://steelgamesapp.com"
API = "https://www.cheapshark.com/api/1.0"
POSTED = os.path.join(ROOT, "data", "posted.json")
PER_DAY = 3
REPOST_DAYS = 7
UTM = "utm_source={src}&utm_medium=social&utm_campaign=daily_deals"
# Daily posts only send people to the platform's own store. Key stores, marketplaces and other resellers are
# left out on purpose, and so is any store not listed here. Names match CheapShark's /stores storeName values.
OFFICIAL_STORES = {"Steam", "GOG", "Epic Games Store", "Humble Store", "Origin", "Uplay", "Blizzard Shop"}


def http(url, data=None, headers=None, method=None, tries=3):
    h = {"User-Agent": "SteelGames-Deal-Bot"}
    h.update(headers or {})
    body = None
    if data is not None:
        if isinstance(data, (bytes, bytearray)):
            body = bytes(data)
        else:
            body = json.dumps(data).encode()
            h.setdefault("Content-Type", "application/json")
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers=h, method=method)
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                ctype = r.headers.get("Content-Type", "")
                return json.loads(raw) if "json" in ctype and raw else raw
        except urllib.error.HTTPError as ex:
            if ex.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"{ex.code} from {url.split('?')[0]}: {ex.read()[:300]!r}")


def load_json(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def game_url(gid, src):
    tracked = load_json(os.path.join(ROOT, "game", "tracked.json"), {})
    base = f"{SITE}/game/{tracked[gid]}/" if gid in tracked else f"{SITE}/deal/?id={gid}"
    return base + ("&" if "?" in base else "?") + UTM.format(src=src)


def pick(deals, posted, today):
    """Best few deals not posted in the last week, one per game, real discounts only."""
    cutoff = (today - timedelta(days=REPOST_DAYS)).isoformat()
    seen, out = set(), []
    for d in deals:
        gid = str(d.get("gameID"))
        if gid in seen or posted.get(gid, "") >= cutoff:
            continue
        if float(d.get("savings") or 0) < 30 or float(d.get("salePrice") or 0) <= 0:
            continue
        seen.add(gid)
        out.append(d)
        if len(out) == PER_DAY:
            break
    return out


def official_only(deals, stores):
    """Keep only deals sold by an official store (see OFFICIAL_STORES)."""
    return [d for d in deals if stores.get(str(d.get("storeID")), "") in OFFICIAL_STORES]


def facts(d, stores):
    price, normal = float(d["salePrice"]), float(d["normalPrice"])
    off = round(float(d.get("savings") or 0))
    store = stores.get(str(d.get("storeID")), "an official store")
    rating = d.get("steamRatingPercent")
    sid = str(d.get("steamAppID") or "")
    img = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg" if sid and sid != "0" else (d.get("thumb") or "")
    return {"title": d.get("title", "Game"), "price": f"${price:.2f}", "normal": f"${normal:.2f}", "off": off, "store": store,
            "rating": f"{rating}% positive on Steam" if rating and rating != "0" else "", "img": img, "gid": str(d.get("gameID"))}


# ---------- channels ----------
def post_discord(items, dry):
    hook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not hook:
        return "skipped (no DISCORD_WEBHOOK_URL)"
    embeds = [{"title": f"{f['title']}: {f['price']} (-{f['off']}%)", "url": game_url(f["gid"], "discord"),
               "description": f"Was {f['normal']} at {f['store']}." + (f" {f['rating']}." if f["rating"] else "") + " Compare every store and see the price history.",
               "color": 0xFF7A1A, **({"image": {"url": f["img"]}} if f["img"] else {})} for f in items]
    payload = {"username": "SteelGames Deals", "content": "🎯 **Today's top PC game deals**", "embeds": embeds}
    if dry:
        return "dry run: " + json.dumps(payload)[:300]
    http(hook, payload)
    return "posted"


def post_telegram(items, dry):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        return "skipped (no TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID)"
    e = html.escape
    for f in items:
        cap = (f"🎯 <b>{e(f['title'])}</b>\n{e(f['price'])} <s>{e(f['normal'])}</s> (-{f['off']}%) at {e(f['store'])}\n"
               + (f"{e(f['rating'])}\n" if f["rating"] else "") + f"\n<a href=\"{e(game_url(f['gid'], 'telegram'))}\">Compare every store on SteelGames</a>")
        if dry:
            continue
        api = f"https://api.telegram.org/bot{tok}/"
        if f["img"]:
            http(api + "sendPhoto", {"chat_id": chat, "photo": f["img"], "caption": cap, "parse_mode": "HTML"})
        else:
            http(api + "sendMessage", {"chat_id": chat, "text": cap, "parse_mode": "HTML"})
        time.sleep(2)
    return "dry run" if dry else "posted"


def post_bluesky(items, dry):
    handle, pw = os.environ.get("BLUESKY_HANDLE"), os.environ.get("BLUESKY_APP_PASSWORD")
    if not (handle and pw):
        return "skipped (no BLUESKY_HANDLE / BLUESKY_APP_PASSWORD)"
    pds = "https://bsky.social/xrpc/"
    if dry:
        return "dry run"
    s = http(pds + "com.atproto.server.createSession", {"identifier": handle, "password": pw})
    auth = {"Authorization": "Bearer " + s["accessJwt"]}
    for f in items:
        url = game_url(f["gid"], "bluesky")
        text = f"🎯 {f['title']}: {f['price']} (was {f['normal']}, -{f['off']}%) at {f['store']}.\n\nPrice history + every store: steelgamesapp.com\n#PCGaming #GameDeals"
        text = text[:290]
        embed = {"$type": "app.bsky.embed.external", "external": {"uri": url, "title": f"{f['title']}: {f['price']} on SteelGames",
                                                                     "description": f"-{f['off']}% at {f['store']}. Compare every official store and see the lowest price ever."}}
        if f["img"]:
            try:
                img = urllib.request.urlopen(urllib.request.Request(f["img"], headers={"User-Agent": "SteelGames-Deal-Bot"}), timeout=20).read()
                blob = http(pds + "com.atproto.repo.uploadBlob", img, {**auth, "Content-Type": "image/jpeg"})
                embed["external"]["thumb"] = blob["blob"]
            except Exception as ex:
                print("bluesky thumb skipped:", ex, file=sys.stderr)
        # Make the site name a clickable link (Bluesky needs byte offsets).
        b = text.encode()
        start = b.find(b"steelgamesapp.com")
        facets = [{"index": {"byteStart": start, "byteEnd": start + len("steelgamesapp.com")},
                   "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}]}] if start >= 0 else []
        rec = {"$type": "app.bsky.feed.post", "text": text, "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
               "facets": facets, "embed": embed, "langs": ["en"]}
        http(pds + "com.atproto.repo.createRecord", {"repo": s["did"], "collection": "app.bsky.feed.post", "record": rec}, auth)
        time.sleep(2)
    return "posted"


def main():
    dry = "--dry-run" in sys.argv
    today = datetime.now(timezone.utc).date()
    if "--sample" in sys.argv:
        data = json.load(open(sys.argv[sys.argv.index("--sample") + 1]))
        stores, deals = data["stores"], data["deals"]
    else:
        stores = {s["storeID"]: s["storeName"] for s in http(API + "/stores")}
        deals = http(API + "/deals?" + urllib.parse.urlencode({"sortBy": "Deal Rating", "onSale": 1, "pageSize": 60, "steamRating": 80, "upperPrice": 40}))
    posted = load_json(POSTED, {})
    chosen = pick(official_only(deals, stores), posted, today)
    if not chosen:
        print("No new deals worth posting today.")
        return
    items = [facts(d, stores) for d in chosen]
    print("Today's picks:", ", ".join(f"{f['title']} {f['price']}" for f in items))
    any_ok = False
    for name, fn in (("Bluesky", post_bluesky), ("Telegram", post_telegram), ("Discord", post_discord)):
        try:
            res = fn(items, dry)
            any_ok = any_ok or res == "posted"
            print(f"{name}: {res}")
        except Exception as ex:
            print(f"::warning title={name} post failed::{ex}")
    if any_ok:
        for f in items:
            posted[f["gid"]] = today.isoformat()
        cutoff = (today - timedelta(days=30)).isoformat()
        posted = {k: v for k, v in posted.items() if v >= cutoff}
        os.makedirs(os.path.dirname(POSTED), exist_ok=True)
        json.dump(posted, open(POSTED, "w"), indent=0, sort_keys=True)


if __name__ == "__main__":
    main()
