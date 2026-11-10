"""Popular games feed for SteelGames.

Why this exists: the daily build only tracked games that were on sale and cheap, so the games people search for
most (Elden Ring, Cyberpunk 2077, Baldur's Gate 3...) had no price page at all. This adds a few popular games a
day to the tracked list so each one gets its own /game/<slug>/ page with price history, even when it is not on
sale. People search "<game> price" all year, not only during a sale.

Sources, in order: tools/popular_curated.json (edit it freely: [steamAppID, "Title"]), then Steam's most-played chart.
Each Steam id is looked up once and remembered in tools/popular_map.json, so later runs cost nothing for it.
Skipped on purpose: free games (no purchase to link to), software, DLC, and adult-only titles (AdSense is on every page).
Standard library only. build_seo.py passes in its own rate-limited `get` so the price API budget stays shared.
"""
import json
import os
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_FILE = os.path.join(ROOT, "tools", "popular_map.json")
CURATED_FILE = os.path.join(ROOT, "tools", "popular_curated.json")
CHARTS = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
DETAILS = "https://store.steampowered.com/api/appdetails?appids=%s"
UA = {"User-Agent": "SteelGames-SEO-Builder (steelgames.app@outlook.com)"}
ADULT_ONLY = {3, 4}   # Steam content descriptors: adult-only sexual content, frequent nudity or sexual content
PER_RUN = 20          # new games added to the tracked list per build; the rest wait for the next run
MAX_LOOKUPS = 40      # new Steam ids resolved per build (each costs one price API call)


def _fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def candidates():
    """Steam app ids to consider, best first, no duplicates."""
    out, seen = [], set()
    for row in _load(CURATED_FILE, []):
        a = str(row[0])
        if a not in seen:
            seen.add(a)
            out.append(a)
    try:
        for r in _fetch(CHARTS)["response"]["ranks"]:
            a = str(r["appid"])
            if a not in seen:
                seen.add(a)
                out.append(a)
    except Exception as ex:
        print("steam chart unavailable:", ex)
    return out


def resolve(get, appid):
    """One Steam id -> {"id": price API game id, "title": ...} or {"skip": reason}. None means try again next run."""
    try:
        d = _fetch(DETAILS % appid).get(appid) or {}
    except Exception as ex:
        print("steam details failed", appid, ex)
        return None
    time.sleep(1.0)  # Steam's store API is touchy about bursts
    if not d.get("success") or not d.get("data"):
        return {"skip": "no steam store page"}
    x = d["data"]
    if x.get("type") != "game":
        return {"skip": "not a game", "title": x.get("name", "")}
    if x.get("is_free"):
        return {"skip": "free to play", "title": x.get("name", "")}
    if ADULT_ONLY & set((x.get("content_descriptors") or {}).get("ids") or []):
        return {"skip": "adult only", "title": x.get("name", "")}
    try:
        rows = get("/games", {"steamAppID": appid})
    except Exception as ex:
        if ex.__class__.__name__ == "RateLimited":
            raise
        print("price lookup failed", appid, ex)
        return None
    if not rows:
        return {"skip": "not on the price API", "title": x.get("name", "")}
    return {"id": str(rows[0]["gameID"]), "title": rows[0].get("external") or x.get("name", "")}


def next_seeds(get, tracked_ids, per_run=PER_RUN):
    """Price API game ids to add to today's build. Safe to call every run."""
    known = _load(MAP_FILE, {})
    tracked = {str(t) for t in tracked_ids}
    out, lookups = [], 0
    try:
        for appid in candidates():
            if len(out) >= per_run:
                break
            e = known.get(appid)
            if e is None:
                if lookups >= MAX_LOOKUPS:
                    break
                lookups += 1
                e = resolve(get, appid)
                if e is None:
                    continue
                known[appid] = e
            gid = e.get("id")
            if gid and gid not in tracked:
                out.append(gid)
                tracked.add(gid)
    finally:
        json.dump(known, open(MAP_FILE, "w"), indent=0, sort_keys=True)
    print(f"popular games: {len(out)} new to track, {lookups} looked up")
    return out


if __name__ == "__main__":
    # Manual check: python3 tools/popular.py   (resolves and remembers up to MAX_LOOKUPS games)
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_seo
    ids = _load(os.path.join(ROOT, "tools", "game_ids.json"), [])
    new = next_seeds(build_seo.get, ids, per_run=int(sys.argv[1]) if len(sys.argv) > 1 else PER_RUN)
    print(new)
