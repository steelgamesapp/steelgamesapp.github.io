"""Kinguin key buttons on the /game/ pages.

Kinguin is SteelGames' approved key marketplace on Impact. This module:
  * finds, for each tracked game page, the matching Kinguin PC Steam key (exact title match, base product,
    region-free first, North America keys second; DLC, other editions, gifts, accounts and other regions
    are never matched),
  * keeps the matches and the last price seen in data/kinguin_keys.json,
  * draws a "Buy the Steam key on Kinguin" button (Impact tracking link) inside each game page's price box.

Run by .github/workflows/kinguin-keys.yml every 6 hours with the secrets IMPACT_ACCOUNT_SID and
IMPACT_AUTH_TOKEN (Kinguin blocks GitHub's servers, so everything comes from Kinguin's product feed on Impact).
build_seo.py calls block() when it rebuilds a game page, so the button survives the daily rebuilds.

A price is printed only when it came from the feed within the last FRESH_DAYS days; otherwise the button
shows without one. Nothing here ever raises into the page build.
Standard library only.
"""
import base64
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "kinguin_keys.json")
GAME_DIR = os.path.join(ROOT, "game")

TRACK = "https://kinguin.sjv.io/c/8059330/3827272/50048"  # same Impact link as the gift card page
PROP = "9076396"                                          # steelgamesapp.com media property on Impact
PROGRAM = 50048                                           # Kinguin on Impact
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

BUDGET = int(os.environ.get("KINGUIN_BUDGET", "260"))  # Impact searches per run
FRESH_DAYS = 3        # show a price only if seen this recently
REFRESH_DAYS = 1      # re-check a matched game's price after this many days
RESEARCH_DAYS = 7     # look again for a game Kinguin didn't have after this many days

START, END = "<!--kinguin-->", "<!--/kinguin-->"

# Kinguin names: "<title> PC Steam CD Key", "<title> Steam CD Key", optional region before "PC"/"Steam".
NAME_RE = re.compile(r"^(?P<title>.+?)(?:\s+(?P<region>GLOBAL|NA|US|North America))?(?:\s+PC)?\s+Steam\s+(?:CD\s+)?Key(?:\s+(?P<region2>GLOBAL))?$", re.I)
OK_REGIONS = {"": "global", "global": "global", "na": "na", "us": "na", "north america": "na"}


def norm(t):
    t = re.sub(r"['\u2018\u2019`]", "", str(t))
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = t.lower().replace("&", " and ")
    t = re.sub(r"[™®©]|\(tm\)|\(r\)", "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def parse_name(name):
    """(normalized title, region tag) for a plain PC Steam key name, else None."""
    m = NAME_RE.match(str(name).strip())
    if not m:
        return None
    region = (m.group("region") or m.group("region2") or "").lower()
    if region not in OK_REGIONS:
        return None
    title = m.group("title")
    # A region written inside the title part ("Foo EU") means a locked key.
    if re.search(r"\b(EU|EMEA|LATAM|RU|CIS|ROW|ASIA|UK|TR|IN|CN|BR|AR|ARG)\b$", title):
        return None
    return norm(title), OK_REGIONS[region]


def product_page(offer_url):
    """Kinguin product page (no language, currency or country) from an Impact offer link."""
    try:
        u = urllib.parse.parse_qs(urllib.parse.urlparse(offer_url).query).get("u", [""])[0]
        p = urllib.parse.urlparse(u)
        if p.hostname != "www.kinguin.net":
            return None
        m = re.search(r"/category/(\d+)/([a-z0-9-]+)", p.path)
        if not m:
            return None
        return m.group(1), m.group(2)
    except Exception:
        return None


def track(page, gid):
    return f"{TRACK}?subId1=site-game-{gid}&u={urllib.parse.quote(page, safe='')}&partnerpropertyid={PROP}"


_cache = {}


def load(cached=False):
    if cached and "data" in _cache:
        return _cache["data"]
    try:
        with open(DATA, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = {"games": {}, "misses": {}}
    _cache["data"] = d
    return d


# ---------- page side ----------

def _fresh(checked):
    try:
        return (date.today() - date.fromisoformat(checked)).days <= FRESH_DAYS
    except Exception:
        return False


def _short(d):
    try:
        return date.fromisoformat(d).strftime("%b %d").replace(" 0", " ")
    except Exception:
        return ""


def block(gid, data=None):
    """HTML for the game page's price box, or "" when Kinguin has no matching key."""
    try:
        g = (data or load(cached=True)).get("games", {}).get(str(gid))
        if not g or not g.get("sku") or not g.get("slug"):
            return ""
        e = html.escape
        page = f"https://www.kinguin.net/category/{g['sku']}/{g['slug']}"
        where = "Works worldwide on Steam." if g.get("region") == "global" else "North America key: for Steam accounts in the US and Canada."
        price = ""
        if g.get("usd") and _fresh(g.get("checked", "")):
            price = f" Sellers started at about <strong style=\"color:#fff\">${g['usd']:.2f}</strong> when we checked on {_short(g['checked'])}; prices change all day."
        return (f'{START}<div class="kgk" style="margin-top:12px;padding-top:12px;border-top:1px solid var(--line)">'
                f'<a class="btn btn-ghost" style="width:100%" rel="sponsored nofollow noopener" target="_blank" href="{e(track(page, gid))}">Buy the Steam key on Kinguin</a>'
                f'<p class="fine" style="margin-top:8px">{where}{price} Kinguin is a marketplace of third-party key sellers, so check the seller rating before you buy. '
                f'We earn a commission if you buy through this link.</p></div>{END}')
    except Exception as ex:
        print("kinguin block failed", gid, ex, file=sys.stderr)
        return ""


BUY_RE = re.compile(r'(<a class="btn" rel="sponsored noopener" href="https://www\.cheapshark\.com/redirect\?dealID=[^"]*">Buy at [^<]*</a>)')


def inject(page_html, gid, data=None):
    """Put (or refresh, or remove) the Kinguin block in an existing game page."""
    new = block(gid, data)
    if START in page_html and END in page_html:
        return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: new, page_html, count=1, flags=re.S)
    if not new:
        return page_html
    return BUY_RE.sub(lambda m: m.group(1) + "\n" + new, page_html, count=1)


def tracked_pages():
    """{game id: (slug, title)} for the game pages on disk."""
    try:
        with open(os.path.join(GAME_DIR, "tracked.json"), encoding="utf-8") as f:
            slugs = json.load(f)
    except Exception:
        return {}
    out = {}
    for gid, slug in slugs.items():
        p = os.path.join(GAME_DIR, slug, "index.html")
        try:
            m = re.search(r"<h1>(.*?)</h1>", open(p, encoding="utf-8").read(), re.S)
        except OSError:
            continue
        if m:
            out[str(gid)] = (slug, html.unescape(m.group(1)).strip())
    return out


def inject_all(data=None):
    data = data or load()
    n = 0
    for gid, (slug, _t) in tracked_pages().items():
        p = os.path.join(GAME_DIR, slug, "index.html")
        src = open(p, encoding="utf-8").read()
        out = inject(src, gid, data)
        if out != src and len(out) > 1000:
            open(p, "w", encoding="utf-8").write(out)
            n += 1
    print("game pages updated:", n)
    return n


# ---------- feed side ----------

def _get(url, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json"}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def usd_rates():
    """{currency: units per 1 USD}."""
    for url in ("https://api.frankfurter.app/latest?from=USD", "https://open.er-api.com/v6/latest/USD"):
        try:
            r = _get(url)["rates"]
            r["USD"] = 1.0
            return r
        except Exception as ex:
            print("rate source failed:", url, ex)
    return {"USD": 1.0}


class Impact:
    def __init__(self, sid, token):
        self.sid = sid
        self.hdr = {"Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()}
        self.calls = 0

    def search(self, keyword, pages=2):
        items = []
        for page in range(1, pages + 1):
            q = urllib.parse.urlencode({"Keyword": keyword, "PageSize": 100, "Page": page})
            url = f"https://api.impact.com/Mediapartners/{self.sid}/Catalogs/ItemSearch?{q}"
            for attempt in range(3):
                try:
                    self.calls += 1
                    data = _get(url, self.hdr)
                    break
                except urllib.error.HTTPError as ex:
                    if ex.code == 429:
                        raise
                    if ex.code >= 500 and attempt < 2:
                        time.sleep(5)
                        continue
                    raise
            got = data.get("Items") or []
            items += got
            if len(got) < 100:
                break
            time.sleep(0.4)
        return items


def _is_kinguin(it):
    blob = json.dumps(it).lower()
    return str(it.get("CampaignId") or it.get("ProgramId") or "") == str(PROGRAM) or "kinguin" in blob


def best_match(title, items, rates):
    """The Kinguin product for this title from feed items, with a fresh USD price if there is one."""
    want = norm(title)
    found = {}  # (sku) -> info
    cutoff = datetime.now(timezone.utc) - timedelta(days=FRESH_DAYS)
    for it in items:
        if not _is_kinguin(it):
            continue
        parsed = parse_name(it.get("Name", ""))
        if not parsed or parsed[0] != want:
            continue
        pp = product_page(it.get("Url") or "")
        if not pp:
            continue
        sku, slug = pp
        f = found.setdefault(sku, {"sku": sku, "slug": slug, "region": parsed[1], "name": it.get("Name", ""), "offers": []})
        if str(it.get("StockAvailability", "InStock")).lower() not in ("instock", "in stock", ""):
            continue
        try:
            price, cur = float(it.get("CurrentPrice")), str(it.get("Currency", "")).upper()
        except (TypeError, ValueError):
            continue
        upd = str(it.get("LastUpdated") or it.get("DateLastUpdated") or "")
        try:
            when = datetime.fromisoformat(upd.replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
        except ValueError:
            when = None
        if price > 0 and cur in rates and when and when >= cutoff:
            f["offers"].append((cur, round(price / float(rates[cur]), 2), when))
    if not found:
        return None
    # Region-free key first, then North America.
    pick = sorted(found.values(), key=lambda f: (f["region"] != "global", not f["offers"]))[0]
    usd = None
    if pick["offers"]:
        gbp = [o for o in pick["offers"] if o[0] == "GBP"]  # Kinguin's UK feed is the one kept current
        usd = (gbp or sorted(pick["offers"], key=lambda o: o[2], reverse=True))[0][1]
    return {"sku": pick["sku"], "slug": pick["slug"], "region": pick["region"], "name": pick["name"], "usd": usd}


def refresh(sid, token):
    data = load()
    games, misses = data.setdefault("games", {}), data.setdefault("misses", {})
    pages = tracked_pages()
    today = date.today()
    rates = usd_rates()

    def age(d):
        try:
            return (today - date.fromisoformat(d)).days
        except Exception:
            return 10 ** 6

    queue = [g for g in pages if g not in games and g not in misses]                                   # never looked
    queue += sorted((g for g in pages if g in games and age(games[g].get("checked", "")) >= REFRESH_DAYS),
                    key=lambda g: games[g].get("checked", ""))                                         # price refresh
    queue += sorted((g for g in pages if g in misses and age(misses[g]) >= RESEARCH_DAYS), key=lambda g: misses[g])
    print(f"{len(pages)} game pages, {len(games)} matched, {len(misses)} not on Kinguin, {len(queue)} to look up")
    api = Impact(sid, token)
    done = 0
    for gid in queue:
        if api.calls >= BUDGET:
            break
        title = pages[gid][1]
        kw = games[gid]["name"] if gid in games else f"{title} Steam CD Key"
        try:
            hit = best_match(title, api.search(kw), rates)
        except urllib.error.HTTPError as ex:
            print("Impact stopped us:", ex.code, "- saving progress")
            break
        except Exception as ex:
            print("search failed", gid, title, ex)
            continue
        iso = today.isoformat()
        if hit:
            games[gid] = {**hit, "title": title, "checked": iso}
            misses.pop(gid, None)
        else:
            games.pop(gid, None)
            misses[gid] = iso
        done += 1
        time.sleep(0.4)
    # Forget games whose page is gone.
    for d in (games, misses):
        for gid in [g for g in d if g not in pages]:
            d.pop(gid)
    data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    print(f"looked up {done} games with {api.calls} API calls; now {len(games)} matched, {len(misses)} not on Kinguin")
    return data


def main():
    sid, token = os.environ.get("IMPACT_ACCOUNT_SID"), os.environ.get("IMPACT_AUTH_TOKEN")
    if "--probe" in sys.argv:  # print what the feed returns for one title (for debugging matches)
        api = Impact(sid, token)
        kw = sys.argv[sys.argv.index("--probe") + 1]
        items = api.search(kw, pages=1)
        print(len(items), "items; first item keys:", sorted(items[0].keys()) if items else None)
        for it in items[:40]:
            print(it.get("CatalogId"), it.get("CampaignId"), it.get("Currency"), it.get("CurrentPrice"),
                  it.get("LastUpdated") or it.get("DateLastUpdated"), it.get("StockAvailability"), "|", it.get("Name"))
        print(best_match(kw.replace(" Steam CD Key", ""), items, usd_rates()))
        return
    if sid and token:
        data = refresh(sid, token)
    else:
        print("::warning::Impact keys not set; using the saved Kinguin matches")
        data = load()
    inject_all(data)


if __name__ == "__main__":
    main()
