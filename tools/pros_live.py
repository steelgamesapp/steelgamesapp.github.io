"""Live data for the Pro Setups hub: the RAM price ticker and Amazon's best-selling gaming gear.

Writes two files the /pros/ page reads:
  data/ram.json          DRAM spot prices (DRAMeXchange, USD per chip) and Amazon's best-selling RAM kits, with history
  data/bestsellers.json  Amazon's best-selling PC gaming accessories right now (digital codes and gift cards removed)

Run by .github/workflows/pros-live.yml every two hours. If a source fails, the last good data is kept, so the page never
goes blank. History is capped so the files stay small.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAM = os.path.join(ROOT, "data", "ram.json")
BEST = os.path.join(ROOT, "data", "bestsellers.json")
TAG = "steelgames-20"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

# DRAMeXchange row name -> our short ticker symbol and label
SPOT = {
    "DDR5 16Gb (2Gx8) 4800/5600": ("DDR5", "DDR5 16Gb chip"),
    "DDR4 16Gb (2Gx8) 3200": ("DDR4", "DDR4 16Gb chip"),
    "DDR4 8Gb (1Gx8) 3200": ("DDR4-8", "DDR4 8Gb chip"),
    "GDDR6  8Gb": ("GDDR6", "GDDR6 8Gb (graphics card memory)"),
}
MAX_POINTS = 2000          # about 5 months at 12 points a day
SKIP = re.compile(r"gift card|robux|membership|game pass|online game code|digital code|\bcode\]|luna|subscription|v-bucks|points", re.I)


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        except Exception as ex:
            print("fetch failed", url, ex, file=sys.stderr)
            time.sleep(4 * (i + 1))
    return ""


def load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def num(s):
    try:
        return float(re.sub(r"[^\d.\-]", "", s))
    except ValueError:
        return None


# ---------- DRAMeXchange spot prices ----------

def parse_spot(page):
    out = {}
    for m in re.finditer(r'chip\.gif">\s*([^<]+?)\s*</a>\s*</td>((?:\s*<td[^>]*>.*?</td>){6})', page, re.S):
        name = re.sub(r"\s+", " ", m.group(1)).strip()
        key = next((k for k in SPOT if re.sub(r"\s+", " ", k) == name), None)
        if not key:
            continue
        cells = [re.sub(r"<[^>]+>|\s+", " ", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(2), re.S)]
        hi, lo, avg, chg = num(cells[0]), num(cells[1]), num(cells[4]), num(cells[5])
        if avg:
            out[SPOT[key][0]] = {"avg": avg, "hi": hi, "lo": lo, "chg": chg}
    stamp = re.search(r"Last Update:\s*([A-Za-z]{3})\.(\d{1,2})\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*\(GMT\+8\)", page)
    when = None
    if stamp:
        mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(stamp.group(1)) + 1
        local = dt.datetime(int(stamp.group(3)), mon, int(stamp.group(2)), int(stamp.group(4)), int(stamp.group(5)))
        when = (local - dt.timedelta(hours=8)).isoformat() + "Z"
    return out, when


def backfill(ram):
    """First run only: fill past months from public Wayback Machine snapshots of the DRAMeXchange home page."""
    if len(ram["spot"].get("DDR5", [])) >= 20:
        return
    cdx = get("https://web.archive.org/cdx/search/cdx?url=dramexchange.com/&output=json&fl=timestamp&filter=statuscode:200"
              "&collapse=timestamp:8&from=" + (dt.date.today() - dt.timedelta(days=150)).strftime("%Y%m%d"), tries=2)
    try:
        stamps = [r[0] for r in json.loads(cdx)[1:]]
    except Exception:
        return
    stamps = stamps[::max(1, len(stamps) // 60)]  # about 60 days spread over the window
    for ts in stamps:
        page = get(f"https://web.archive.org/web/{ts}id_/https://www.dramexchange.com/", tries=1)
        rows, when = parse_spot(page)
        when = when or dt.datetime.strptime(ts, "%Y%m%d%H%M%S").isoformat() + "Z"
        for sym, r in rows.items():
            ram["spot"].setdefault(sym, []).append([when, r["avg"]])
        time.sleep(1.5)
    for sym in ram["spot"]:
        ram["spot"][sym] = sorted({p[0]: p for p in ram["spot"][sym]}.values())


def update_spot(ram):
    rows, when = parse_spot(get("https://www.dramexchange.com/"))
    if not rows:
        print("no DRAM spot rows found, keeping old data", file=sys.stderr)
        return
    when = when or now_iso()
    ram["today"] = rows
    ram["spot_updated"] = when
    ram["labels"] = {v[0]: v[1] for v in SPOT.values()}
    for sym, r in rows.items():
        series = ram["spot"].setdefault(sym, [])
        if series and series[-1][0] == when:
            series[-1] = [when, r["avg"]]
        else:
            series.append([when, r["avg"]])
        ram["spot"][sym] = sorted({p[0]: p for p in series}.values())[-MAX_POINTS:]


# ---------- Amazon best sellers ----------

def parse_bestsellers(page):
    items = []
    blocks = re.split(r'(?=<span class="zg-bdg-text">#\d+</span>)', page)
    for b in blocks[1:]:
        rank = re.match(r'<span class="zg-bdg-text">#(\d+)</span>', b)
        asin = re.search(r"/dp/(B0[A-Z0-9]{8}|[0-9]{9}[0-9X])", b)
        img = re.search(r'<img alt="([^"]+)" src="([^"]+)"', b)
        price = re.search(r"\$([\d,]+\.\d\d)", b)
        stars = re.search(r"([\d.]+) out of 5 stars", b)
        reviews = re.search(r'aria-label="[\d.]+ out of 5 stars, ([\d,]+) ratings', b)
        if not (rank and asin and img):
            continue
        name = html.unescape(img.group(1)).strip()
        items.append({
            "rank": int(rank.group(1)), "asin": asin.group(1), "name": name,
            "short": short_name(name),
            "img": re.sub(r"\._[^.]+_\.", "._AC_SL400_.", img.group(2)),
            "price": num(price.group(1)) if price else None,
            "stars": float(stars.group(1)) if stars else None,
            "ratings": int(reviews.group(1).replace(",", "")) if reviews else None,
            "url": f"https://www.amazon.com/dp/{asin.group(1)}?tag={TAG}",
        })
    return items


def short_name(n):
    parts = [x.strip() for x in n.split(" | ")]
    head = re.split(r"\s[–-]\s|, | \(|: ", parts[0])[0]
    if len(head) < 34 and len(parts) > 1:  # "XBOX Wireless Gaming Controller | Elite Series 2 Core" keeps its model name
        head += " " + re.split(r", | \(", parts[1])[0]
    if len(head) > 60:
        head = head[:60].rsplit(" ", 1)[0]
    return head.rstrip(" -,|/")


def kind_of(n):
    n = n.lower()
    for k, words in (("mouse", ["mouse"]), ("keyboard", ["keyboard"]), ("headset", ["headset", "headphone", "earbud"]),
                     ("controller", ["controller", "gamepad"]), ("pad", ["mouse pad", "mousepad", "desk mat"]),
                     ("monitor", ["monitor"]), ("mic", ["microphone"]), ("chair", ["chair"])):
        if any(w in n for w in words):
            return "pad" if k == "mouse" and ("mouse pad" in n or "mousepad" in n) else k
    return "gear"


def update_bestsellers():
    old = load(BEST, {"items": []})
    lists = [("https://www.amazon.com/Best-Sellers-Video-Games-PC-Accessories/zgbs/videogames/229575", "PC gaming"),
             ("https://www.amazon.com/gp/bestsellers/videogames/14210751/", "PC gaming")]
    items, seen = [], set()
    for url, src in lists:
        for it in parse_bestsellers(get(url)):
            if it["asin"] in seen or SKIP.search(it["name"]):
                continue
            seen.add(it["asin"])
            it["kind"] = kind_of(it["name"])
            items.append(it)
        if len(items) >= 20:
            break
    if len(items) < 6:
        print("bestseller list too short, keeping old data", file=sys.stderr)
        return old
    data = {"updated": now_iso(), "source": "Amazon Best Sellers: PC Games & Accessories", "items": items[:24]}
    json.dump(data, open(BEST, "w"), indent=0)
    return data


def update_ram_kits(ram):
    items = [i for i in parse_bestsellers(get("https://www.amazon.com/Best-Sellers-Computers-Accessories-Computer-Memory/zgbs/pc/172500"))
             if i["price"] and re.search(r"ddr[45]", i["name"], re.I) and not re.search(r"laptop|sodimm|so-dimm|notebook", i["name"], re.I)]
    if not items:
        print("no RAM kits found, keeping old data", file=sys.stderr)
        return
    t = now_iso()
    for i in items:
        gen = re.search(r"ddr[45]", i["name"], re.I).group(0).upper()
        cap = re.search(r"(\d{1,3})\s?GB", i["name"], re.I)
        i["gen"], i["gb"] = gen, int(cap.group(1)) if cap else None
        hist = ram["kits_history"].setdefault(i["asin"], [])
        if not hist or hist[-1][1] != i["price"] or hist[-1][0][:10] != t[:10]:
            hist.append([t, i["price"]])
        ram["kits_history"][i["asin"]] = hist[-400:]
    ram["kits"] = items[:12]
    ram["kits_updated"] = t
    # An average $/GB index across the best-selling desktop kits, one per generation, recorded each run.
    for gen in ("DDR5", "DDR4"):
        per = [i["price"] / i["gb"] for i in items if i["gen"] == gen and i["gb"]]
        if per:
            s = ram["retail"].setdefault(gen, [])
            s.append([t, round(sum(per) / len(per), 3)])
            ram["retail"][gen] = s[-MAX_POINTS:]


def main():
    ram = load(RAM, {})
    for k, v in (("spot", {}), ("kits_history", {}), ("retail", {}), ("kits", [])):
        ram.setdefault(k, v)
    update_spot(ram)
    backfill(ram)  # only does anything while the history is still short
    update_ram_kits(ram)
    ram["updated"] = now_iso()
    json.dump(ram, open(RAM, "w"), separators=(",", ":"))
    best = update_bestsellers()
    print("RAM symbols:", {k: len(v) for k, v in ram["spot"].items()}, "kits:", len(ram["kits"]), "bestsellers:", len(best["items"]))


if __name__ == "__main__":
    main()
