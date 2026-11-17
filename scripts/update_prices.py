#!/usr/bin/env python3
"""Refresh gift-card prices on gift-cards/index.html.

Kinguin blocks GitHub's servers, so prices come from Kinguin's product feed on
Impact (secrets IMPACT_ACCOUNT_SID and IMPACT_AUTH_TOKEN). Without those, a
recent snapshot in data/giftcard_prices.json is used; otherwise the page is left as is.
"""
import base64, datetime, json, os, re, sys, urllib.parse, urllib.request

PAGE = "gift-cards/index.html"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
BRANDS = {
    "psn": ("PlayStation Network Card US", "PlayStation Network"),
    "xbox": ("XBOX Live Prepaid Card US", "XBOX Live"),
}
FEED_CURRENCY = "GBP"  # Kinguin's UK feed on Impact is the one kept current
SNAPSHOT = "data/giftcard_prices.json"


def get(url, headers=None):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def to_usd(cur):
    for url in ("https://api.frankfurter.app/latest?from=%s&to=USD" % cur,
                "https://open.er-api.com/v6/latest/%s" % cur):
        try:
            return float(json.loads(get(url))["rates"]["USD"])
        except Exception as e:  # try next source
            print("rate source failed:", url, e)
    sys.exit("no exchange rate; leaving page unchanged")


def face_value(brand, name):
    """Face value in USD for a plain US PlayStation or Xbox card name, else None."""
    starts = {"psn": "PlayStation Network", "xbox": "XBOX Live"}[brand]
    name = name.strip()
    if not name.startswith(starts) or not name.endswith(" US"):
        return None  # skips other regions and bundles like "EA SPORTS FC 25 PlayStation Network Card"
    m = re.search(r'(?:\$|USD )(\d+)\b', name)
    return int(m.group(1)) if m else None


def impact_prices(sid, token):
    """Lowest Kinguin price per face value from the Impact product catalog, in FEED_CURRENCY."""
    auth = base64.b64encode(("%s:%s" % (sid, token)).encode()).decode()
    hdr = {"Authorization": "Basic " + auth, "Accept": "application/json"}
    prices = {b: {} for b in BRANDS}
    for brand, (keyword, _) in BRANDS.items():
        for page in range(1, 6):
            q = urllib.parse.urlencode({"Keyword": keyword, "PageSize": 100, "Page": page})
            data = json.loads(get("https://api.impact.com/Mediapartners/%s/Catalogs/ItemSearch?%s" % (sid, q), hdr))
            items = data.get("Items") or []
            if page == 1:
                print(brand, "items on page 1:", len(items))
            for it in items:
                if str(it.get("Currency", "")).upper() != FEED_CURRENCY:
                    continue
                if "kinguin" not in json.dumps(it).lower():
                    continue
                face = face_value(brand, str(it.get("Name", "")))
                try:
                    price = float(it.get("CurrentPrice"))
                except (TypeError, ValueError):
                    continue
                if face and price > 0 and (face not in prices[brand] or price < prices[brand][face]):
                    prices[brand][face] = price
            if len(items) < 100:
                break
    return prices


def snapshot_prices():
    """Prices saved in data/giftcard_prices.json, if checked within the last 2 days."""
    try:
        snap = json.load(open(SNAPSHOT, encoding="utf-8"))
        age = (datetime.date.today() - datetime.date.fromisoformat(snap["checked"])).days
    except Exception as e:
        print("no usable price snapshot:", e)
        return None
    if age > 2 or snap.get("currency") != FEED_CURRENCY:
        print("price snapshot is %d days old; not using it" % age)
        return None
    return {b: {int(k): float(v) for k, v in snap.get(b, {}).items()} for b in BRANDS}


def main():
    sid, token = os.environ.get("IMPACT_ACCOUNT_SID"), os.environ.get("IMPACT_AUTH_TOKEN")
    if sid and token:
        prices = impact_prices(sid, token)
    else:
        print("::warning::Impact keys not set; trying the saved price snapshot")
        prices = snapshot_prices()
    if not prices or not any(prices.values()):
        print("::warning::No current prices found; page left unchanged")
        return
    rate = to_usd(FEED_CURRENCY)
    print("rate", rate, {b: sorted(p) for b, p in prices.items()})
    with open(PAGE, encoding="utf-8") as f:
        src = f.read()
    changed = 0

    def fix(m):
        nonlocal changed
        block = m.group(0)
        k = re.search(r'subId1=site-giftcards-(psn|xbox)(\d+)&', block)
        if not k:
            return block
        brand, face = k.group(1), int(k.group(2))
        price = prices[brand].get(face)
        if price is None:
            print("no price found for", brand, face, "- left unchanged")
            return block
        usd = round(price * rate, 2)
        pct = (face - usd) / face * 100
        new = re.sub(r'(gc-price-from">)[^<]*', r'\g<1>From $%.2f' % usd, block)
        if pct >= 1:
            badge = '<span class="gc-badge">~%d%% off</span>' % round(pct)
            face_txt = "%.1f%% under face value on Kinguin" % pct
        elif pct >= -1:
            badge = ""
            face_txt = "About face value on Kinguin"
        else:
            badge = ""
            face_txt = "Above face value, so the console store may be cheaper"
        new = re.sub(r'<span class="gc-badge">[^<]*</span>', "", new)
        new = new.replace('</span><svg class="gc-thumb-icon"', badge + '<svg class="gc-thumb-icon"', 1) if badge else new
        new = re.sub(r'(gc-face">)[^<]*', r'\g<1>' + face_txt, new)
        if new != block:
            changed += 1
        return new

    out = re.sub(r'<a class="gc-card".*?</a>', fix, src, flags=re.S)
    if out != src:
        with open(PAGE, "w", encoding="utf-8") as f:
            f.write(out)
    print("cards changed:", changed)


if __name__ == "__main__":
    main()
