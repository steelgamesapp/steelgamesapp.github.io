#!/usr/bin/env python3
"""Refresh gift-card prices on gift-cards/index.html from Kinguin listing data."""
import json, re, sys, urllib.parse, urllib.request

PAGE = "gift-cards/index.html"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
BRANDS = {
    "psn": ("PlayStation Network Card USD US", "PlayStation Network Card"),
    "xbox": ("XBOX Live Prepaid Card USD US", "XBOX Live"),
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def eur_to_usd():
    for url, path in (("https://api.frankfurter.app/latest?from=EUR&to=USD", ("rates", "USD")),
                      ("https://open.er-api.com/v6/latest/EUR", ("rates", "USD"))):
        try:
            d = json.loads(get(url))
            return float(d[path[0]][path[1]])
        except Exception as e:  # try next source
            print("rate source failed:", url, e)
    sys.exit("no exchange rate; leaving page unchanged")


def listing(brand):
    phrase, prefix = BRANDS[brand]
    html = get("https://www.kinguin.net/listing?phrase=" + urllib.parse.quote(phrase))
    best = {}  # face value (int USD) -> lowest price in EUR cents
    for m in re.finditer(r'"name":"([^"]{5,100})","id":"[0-9a-f]{24}"', html):
        name = m.group(1)
        if not name.startswith(prefix) or not name.rstrip().endswith("US"):
            continue
        seg = html[m.start():m.start() + 6000]
        p = re.search(r'"calculated":(\d+)', seg)
        v = re.search(r'"prepaidAttributes":\{"unitType":"USD","value":"(\d+)"', seg)
        if not p or not v:
            continue
        face, cents = int(v.group(1)), int(p.group(1))
        if face not in best or cents < best[face]:
            best[face] = cents
    return best


def main():
    rate = eur_to_usd()
    prices = {b: listing(b) for b in BRANDS}
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
        cents = prices[brand].get(face)
        if cents is None:
            print("no price found for", brand, face, "- left unchanged")
            return block
        usd = round(cents / 100 * rate, 2)
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
