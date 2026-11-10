#!/usr/bin/env python3
"""Nightly site-health check for SteelGames. Standard library only.

Run by .github/workflows/health.yml. Looks for the things that quietly cost money on a deals site:
  - stale prices (game pages the daily build failed to refresh)
  - broken internal links and images (missing files)
  - pages missing a title, description, canonical link or H1 (invisible to search)
  - sitemap entries with no page, and pages missing from the sitemap
  - Amazon links without our Associates tag, and affiliate links not marked rel="sponsored"
  - outside links and images that answer 404/410 or do not resolve (a rotating sample each night)
  - the live site itself: home page, sitemap and a sample of pages answering 200

Output: a Markdown report on stdout (also written to health_report.md), a JSON summary in health_report.json, and an
exit code of 0 either way (the workflow decides what to do). Nothing in the repo is changed.

Usage: python3 tools/health_check.py [--offline]      (--offline skips every network check, for tests)
"""
import concurrent.futures as cf
import datetime as dt
import html as htmllib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://steelgamesapp.com"
AMAZON_TAG = "steelgames-20"
STALE_DAYS = 2            # a game page not refreshed for this many days counts as stale
OUTSIDE_SAMPLE = 80       # bulk Steam/CheapShark links and images checked per night (rotates through all of them)
IMAGE_SAMPLE = 150        # (unused: kept for reference)
LIVE_SAMPLE = 40          # live pages fetched per night
UA = "Mozilla/5.0 (compatible; SteelGamesHealthCheck/1.0; +https://steelgamesapp.com)"
# Retailers that refuse bots. Their answers say nothing about whether a link works, so we do not test them.
SKIP_HOSTS = ("amazon.", "amzn.", "tiktok.com", "instagram.com", "facebook.com", "discord.gg", "discord.com",
              "chromewebstore.google.com", "youtube.com", "youtu.be", "fonts.googleapis.com", "fonts.gstatic.com",
              "gc.zgo.at", "googlesyndication.com", "twitter.com", "x.com")
AFFILIATE_HOSTS = ("sjv.io", "pxf.io", "awin1.com", "go.nordvpn.net", "go.nordpass.io", "redragonshop.com", "epomaker.com",
                   "lamzu.com", "cheapshark.com")

OFFLINE = "--offline" in sys.argv
TODAY = dt.datetime.now(dt.timezone.utc).date()
DAY = TODAY.toordinal()

problems = []   # (severity, area, message, detail_list)
notes = []      # plain facts for the report footer


def add(sev, area, msg, items=None):
    problems.append({"severity": sev, "area": area, "message": msg, "items": (items or [])[:15], "count": len(items or [])})


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def html_pages():
    """Every .html file in the site (skips media, node-style folders and Google's verification file)."""
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", ".github", "node_modules", "media", "worker", "extension", "tools")]
        for f in files:
            if f.endswith(".html") and not f.startswith("google"):
                out.append(os.path.join(base, f))
    return sorted(out)


def url_for(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if rel == "index.html":
        return SITE + "/"
    return SITE + "/" + (rel[:-len("index.html")] if rel.endswith("/index.html") else rel)


def exists_local(href):
    """Does an internal link ('/games.html', '/game/x/', '/assets/pages.css?v=2') point at something on disk?"""
    p = urllib.parse.urlsplit(href).path
    if not p.startswith("/"):
        return True
    p = urllib.parse.unquote(p).lstrip("/")
    full = os.path.join(ROOT, p)
    if p == "" or p.endswith("/"):
        return os.path.isfile(os.path.join(full, "index.html"))
    return os.path.isfile(full) or os.path.isfile(os.path.join(full, "index.html"))


# ---------- offline checks ----------

def check_pages():
    pages = html_pages()
    notes.append(f"{len(pages)} pages scanned")
    no_title, no_desc, no_canon, no_h1, bad_links, bad_imgs = [], [], [], [], {}, {}
    amazon_untagged, sponsor_rel, stale, undated = [], [], [], []
    outside_links, outside_imgs = {}, {}
    game_pages = 0
    for path in pages:
        s = read(path)
        u = url_for(path)
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        # Pages that are not meant to rank (private pages, app shell, embeds) are not held to the search basics.
        searchable = not re.search(r'<meta[^>]*name="robots"[^>]*noindex', s) and not (
            rel.startswith(("assets/", "app/", "social/")) or rel in ("embed.html",))
        if searchable:
            if "<title>" not in s or re.search(r"<title>\s*</title>", s):
                no_title.append(u)
            if not re.search(r'<meta name="description" content="[^"]{20,}', s):
                no_desc.append(u)
            if 'rel="canonical"' not in s:
                no_canon.append(u)
            if not re.search(r"<h1[ >]", s):
                no_h1.append(u)
        for m in re.finditer(r'<a\b[^>]*\bhref="([^"#]+)[^"]*"[^>]*>', s):
            tag, href = m.group(0), htmllib.unescape(m.group(1))
            if href.startswith("/") and not href.startswith("//"):
                if not exists_local(href):
                    bad_links.setdefault(href, []).append(u)
            elif href.startswith("http"):
                host = urllib.parse.urlsplit(href).netloc.lower()
                if "amazon." in host and "/dp/" in href or "amazon." in host and "/s?" in href:
                    if f"tag={AMAZON_TAG}" not in href:
                        amazon_untagged.append(f"{u} -> {href[:90]}")
                if any(h in host for h in AFFILIATE_HOSTS if h != "cheapshark.com") and "sponsored" not in tag:
                    sponsor_rel.append(f"{u} -> {host}")
                if not any(h in host for h in SKIP_HOSTS) and "steelgamesapp.com" not in host:
                    outside_links.setdefault(href, u)
        for m in re.finditer(r'<img\b[^>]*\bsrc="([^"]+)"', s):
            src = htmllib.unescape(m.group(1))
            if src.startswith("/") and not src.startswith("//"):
                if not exists_local(src):
                    bad_imgs.setdefault(src, []).append(u)
            elif src.startswith("http"):
                outside_imgs.setdefault(src, u)
        if "/game/" in path.replace(os.sep, "/") and path.endswith("index.html") and os.path.dirname(path) != os.path.join(ROOT, "game"):
            game_pages += 1
            m = re.search(r"Updated ([A-Z][a-z]+ \d{1,2}, \d{4})", s)
            if not m:
                undated.append(u)
            else:
                try:
                    d = dt.datetime.strptime(m.group(1), "%B %d, %Y").date()
                    if (TODAY - d).days > STALE_DAYS:
                        stale.append((u, (TODAY - d).days))
                except ValueError:
                    undated.append(u)
    if no_title: add("high", "SEO basics", "Pages with no title", no_title)
    if no_desc: add("medium", "SEO basics", "Pages with no (or a very short) meta description", no_desc)
    if no_canon: add("medium", "SEO basics", "Pages with no canonical link", no_canon)
    if no_h1: add("medium", "SEO basics", "Pages with no H1 heading", no_h1)
    if bad_links:
        add("high", "Links", "Internal links that point at a page that does not exist",
            [f"{h}  (on {v[0]}{' and %d more' % (len(v) - 1) if len(v) > 1 else ''})" for h, v in sorted(bad_links.items())])
    if bad_imgs:
        add("high", "Images", "Local images that are missing from the site",
            [f"{h}  (on {v[0]}{' and %d more' % (len(v) - 1) if len(v) > 1 else ''})" for h, v in sorted(bad_imgs.items())])
    if amazon_untagged:
        add("high", "Money links", f"Amazon links without our Associates tag ({AMAZON_TAG}). These earn nothing", amazon_untagged)
    if sponsor_rel:
        add("low", "Money links", 'Affiliate links not marked rel="sponsored" (search engines prefer it)', sponsor_rel)
    stale_pct = round(100 * len(stale) / game_pages, 1) if game_pages else 0.0
    if stale:
        worst = sorted(stale, key=lambda x: -x[1])
        add("high" if stale_pct >= 15 else "medium", "Prices",
            f"{len(stale)} of {game_pages} game pages ({stale_pct}%) have prices older than {STALE_DAYS} days",
            [f"{u}  ({d} days old)" for u, d in worst])
    if undated:
        add("low", "Prices", "Game pages with no 'Updated' date", undated)
    notes.append(f"{game_pages} game pages, {stale_pct}% stale")
    return {"game_pages": game_pages, "stale": len(stale), "stale_pct": stale_pct}, outside_links, outside_imgs


def check_sitemap():
    try:
        urls = re.findall(r"<loc>([^<]+)</loc>", read(os.path.join(ROOT, "sitemap.xml")))
    except OSError:
        add("high", "Sitemap", "sitemap.xml is missing")
        return []
    missing = []
    for u in urls:
        p = urllib.parse.urlsplit(u).path
        if not exists_local(p):
            missing.append(u)
    if missing:
        add("high", "Sitemap", "Sitemap lists pages that do not exist", missing)
    listed = {urllib.parse.urlsplit(u).path for u in urls}
    unlisted = []
    for sec in ("game", "deals", "guides", "pros"):
        base = os.path.join(ROOT, sec)
        if os.path.isdir(base):
            for name in sorted(os.listdir(base)):
                if os.path.isfile(os.path.join(base, name, "index.html")) and f"/{sec}/{name}/" not in listed:
                    unlisted.append(f"/{sec}/{name}/")
    if unlisted:
        add("medium", "Sitemap", "Pages on the site that the sitemap does not list (Google may never find them)", unlisted)
    notes.append(f"{len(urls)} sitemap entries")
    return urls


def check_data_files():
    for rel, minimum in (("sponsors.json", 0), ("data/key_deals.json", 1), ("data/gear.json", 1)):
        try:
            d = json.load(open(os.path.join(ROOT, rel)))
            if len(d) < minimum:
                add("medium", "Data", f"{rel} is empty")
        except Exception as ex:
            add("high", "Data", f"{rel} cannot be read: {ex}")


# ---------- network checks ----------

def probe(url, method="HEAD"):
    """Returns (status, note). status 0 = could not connect. Redirects are followed."""
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, ""
    except urllib.error.HTTPError as ex:
        if method == "HEAD" and ex.code in (403, 405, 501):
            return probe(url, "GET")
        return ex.code, ""
    except urllib.error.URLError as ex:
        return 0, str(ex.reason)[:80]
    except Exception as ex:
        return 0, str(ex)[:80]


def rotate(items, n):
    """A different slice each night so the whole list gets covered over a few days."""
    items = sorted(items)
    if len(items) <= n:
        return items
    start = (DAY * n) % len(items)
    return (items + items)[start:start + n]


BULK_HOSTS = ("steamstatic.com", "cheapshark.com")  # thousands of near-identical links: sample these, check everything else


def pick(urls):
    """Every affiliate, gear and retailer URL each night; only a rotating slice of the bulk Steam/CheapShark ones."""
    bulk_set = {u for u in urls if any(h in urllib.parse.urlsplit(u).netloc for h in BULK_HOSTS)}
    rest = sorted(u for u in urls if u not in bulk_set)
    return rest + rotate(list(bulk_set), OUTSIDE_SAMPLE)


def run_probes(urls, label):
    """Returns (dead, unreachable). dead = the site said 404/410 (certain). unreachable = no answer even on a second try
    (could be the site, could be bot-blocking, so it is reported with a lower priority)."""
    dead, unreachable = [], []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(zip(urls, ex.map(probe, urls)))
    retry = [u for u, (c, n) in results if c == 0 and "timed out" not in n.lower() and "Tunnel connection failed" not in n]
    again = dict(zip(retry, [probe(u) for u in retry]))
    for u, (code, note) in results:
        if u in again:
            code, note = again[u]
        if code in (404, 410):
            dead.append((u, code, note))
        elif code == 0 and u in again:
            unreachable.append((u, code, note))
    return dead, unreachable


def check_outside(outside_links, outside_imgs):
    links = pick(list(outside_links))
    imgs = pick(list(outside_imgs))
    dead_l, down_l = run_probes(links, "links")
    dead_i, down_i = run_probes(imgs, "images")
    if dead_l:
        add("high" if len(dead_l) > 5 else "medium", "Money links", "Outside links that are dead (the page is gone, 404/410)",
            [f"{u}  [{c}]  on {outside_links[u]}" for u, c, note in dead_l])
    if down_l:
        add("low", "Money links", "Outside links that did not answer twice in a row (site down, or it blocks bots; worth a manual click)",
            [f"{u}  [{note}]  on {outside_links[u]}" for u, c, note in down_l])
    if dead_i:
        add("medium", "Images", "Outside images that are gone (visitors see a broken picture)",
            [f"{u}  [{c}]  on {outside_imgs[u]}" for u, c, note in dead_i])
    if down_i:
        add("low", "Images", "Outside images that did not answer twice in a row", [f"{u}  [{note}]  on {outside_imgs[u]}" for u, c, note in down_i])
    notes.append(f"checked {len(links)} of {len(outside_links)} outside links and {len(imgs)} of {len(outside_imgs)} outside images tonight")


def check_live(urls):
    code, _ = probe(SITE + "/", "GET")
    if code != 200:
        add("high", "Live site", f"The home page answered {code or 'nothing'}", [SITE + "/"])
    pages = rotate([u for u in urls if u.rstrip("/") != SITE], LIVE_SAMPLE)
    dead = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for u, (c, note) in zip(pages, ex.map(lambda x: probe(x, "GET"), pages)):
            if c != 200:
                dead.append(f"{u}  [{c or note}]")
    if dead:
        add("high" if len(dead) > 3 else "medium", "Live site", "Sitemap pages that do not load on the live site", dead)
    notes.append(f"{len(pages)} live pages fetched")


# ---------- report ----------

def report(stats):
    order = {"high": 0, "medium": 1, "low": 2}
    problems.sort(key=lambda p: (order[p["severity"]], p["area"]))
    high = sum(1 for p in problems if p["severity"] == "high")
    lines = [f"# SteelGames site health: {TODAY.isoformat()}", ""]
    if not problems:
        lines.append("All clear. Nothing needs attention.")
    else:
        lines.append(f"**{len(problems)} issue types found, {high} high priority.**")
        icon = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}
        for p in problems:
            lines += ["", f"### [{icon[p['severity']]}] {p['area']}: {p['message']}" + (f" ({p['count']})" if p["count"] else "")]
            for it in p["items"]:
                lines.append(f"- {it}")
            if p["count"] > len(p["items"]):
                lines.append(f"- ...and {p['count'] - len(p['items'])} more")
    lines += ["", "---", "Checked: " + "; ".join(notes) + "."]
    text = "\n".join(lines) + "\n"
    open(os.path.join(ROOT, "health_report.md"), "w").write(text)
    json.dump({"date": TODAY.isoformat(), "problems": problems, "high": high, **stats}, open(os.path.join(ROOT, "health_report.json"), "w"), indent=1)
    return text


def main():
    stats, outside_links, outside_imgs = check_pages()
    urls = check_sitemap()
    check_data_files()
    if not OFFLINE:
        try:
            check_outside(outside_links, outside_imgs)
            check_live(urls)
        except Exception as ex:  # a network hiccup must never hide the offline findings
            notes.append(f"network checks stopped early: {ex}")
    print(report(stats))


if __name__ == "__main__":
    main()
