"""Gift card price comparison: live prices from our affiliate stores, read from their Impact product feeds.

Stores (all approved partners on Impact, so every Buy button is our tracked link and pays us a commission):
  Kinguin (program 50048, marketplace), Gameseal (25825), Loaded (18216).
Cards: US PlayStation, Xbox, Nintendo eShop, Steam Wallet and Roblox, at the usual face values.

Run by .github/workflows/giftcards.yml every 3 hours with the secrets IMPACT_ACCOUNT_SID and IMPACT_AUTH_TOKEN.
Writes data/giftcards.json, then tools/giftcards_page.py builds gift-cards/index.html from it.
A store's price is only shown when it came from the feed within STALE_DAYS; a failed run keeps the last file.
Standard library only. Usage: python3 tools/giftcards.py [--probe "search words"]
"""
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "giftcards.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
STALE_DAYS = 3

# Which feed currency to trust per store (Kinguin keeps only its UK/GBP feed current; the others have a USD feed).
STORES = {
    "kinguin": {"name": "Kinguin", "program": "50048", "host": "kinguin.sjv.io", "cur": ["GBP"], "kind": "Marketplace (third-party sellers)"},
    "gameseal": {"name": "Gameseal", "program": "25825", "host": "impact.gameseal.com", "cur": ["USD", "GBP"], "kind": "Key store"},
    "loaded": {"name": "Loaded", "program": "18216", "host": "go.loaded.com", "cur": ["USD"], "kind": "Key store (formerly CDKeys)"},
}

CARDS = {
    "psn": {"name": "PlayStation Store", "faces": [10, 20, 25, 50, 75, 100],
            "words": ["PlayStation Network Card US", "PlayStation Store Gift Card USD", "PSN Card USD US"],
            "match": r"playstation|\bpsn\b", "global_ok": False},
    "xbox": {"name": "Xbox", "faces": [10, 15, 20, 25, 50, 100],
             "words": ["XBOX Live Prepaid Card US", "Xbox Gift Card USD US"],
             "match": r"\bxbox\b", "global_ok": False, "skip": r"game ?pass|ultimate|core|live gold"},
    "nintendo": {"name": "Nintendo eShop", "faces": [10, 20, 35, 50, 70, 99],
                 "words": ["Nintendo eShop Card USD US", "Nintendo eShop Gift Card USD"],
                 "match": r"nintendo|eshop", "global_ok": False, "na_ok": True},
    "steam": {"name": "Steam Wallet", "faces": [5, 10, 20, 50, 100],
              "words": ["Steam Wallet Gift Card USD US", "Steam Gift Card USD"],
              "match": r"\bsteam\b", "global_ok": False},
    "roblox": {"name": "Roblox", "faces": [10, 25, 50],
               "words": ["Roblox Gift Card USD", "Roblox Card USD"],
               "match": r"\broblox\b", "global_ok": True},
}

# Any of these region tokens in a product name means it is not a card for a US account.
OTHER_REGIONS = {"CA", "CAN", "CANADA", "UK", "GB", "GBP", "EU", "EUR", "EUROPE", "AU", "AUD", "AUSTRALIA", "NZ", "HK", "SG",
                 "SGD", "GY", "MX", "MEXICO", "BR", "BRAZIL", "IN", "INDIA", "JP", "JAPAN", "KR", "TR", "TRY", "TURKEY", "UAE",
                 "AE", "SA", "KSA", "LEBANON", "PL", "PLN", "DE", "FR", "IT", "ES", "NL", "SE", "NO", "DK", "ZA", "ARG", "AR",
                 "CL", "CO", "PE", "PH", "MY", "TH", "ID", "VN", "TW", "KZ", "UA", "RU", "CZ", "HU", "RO", "CH", "AT", "BE",
                 "PT", "IE", "IL", "QA", "KW", "OM", "BH", "EG", "NG"}
US_TOKENS = {"US", "USA", "UNITED STATES", "AMERICA"}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json"}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def usd_rates():
    """{currency: units per 1 USD}."""
    for url in ("https://api.frankfurter.app/latest?from=USD", "https://open.er-api.com/v6/latest/USD"):
        try:
            r = get(url)["rates"]
            r["USD"] = 1.0
            return r
        except Exception as ex:
            print("rate source failed:", url, ex)
    return None


class Impact:
    def __init__(self, sid, token):
        self.sid = sid
        self.hdr = {"Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()}

    def search(self, keyword, pages=3):
        items = []
        for page in range(1, pages + 1):
            q = urllib.parse.urlencode({"Keyword": keyword, "PageSize": 100, "Page": page})
            url = f"https://api.impact.com/Mediapartners/{self.sid}/Catalogs/ItemSearch?{q}"
            data = None
            for attempt in range(3):
                try:
                    data = get(url, self.hdr)
                    break
                except urllib.error.HTTPError as ex:
                    if ex.code >= 500 and attempt < 2:
                        time.sleep(5)
                        continue
                    raise
            got = (data or {}).get("Items") or []
            items += got
            if len(got) < 100:
                break
            time.sleep(0.5)
        return items


def store_of(it):
    blob = (str(it.get("CampaignId") or it.get("ProgramId") or "") + " " + str(it.get("Url") or "")).lower()
    for sid, s in STORES.items():
        if s["program"] in blob.split() or s["host"] in blob:
            return sid
    return None


def tokens(name):
    up = name.upper().replace("(", " ").replace(")", " ").replace("-", " ").replace(",", " ")
    return set(up.split()), up


def face_of(name):
    """Face value in USD from a product name, or None if the card isn't a USD card."""
    n = name.upper()
    m = re.search(r"\$\s?(\d{1,3})\b|\bUSD\s?(\d{1,3})\b|\b(\d{1,3})\s?(?:USD|\$)", n)
    if not m:
        return None
    return int(next(g for g in m.groups() if g))


def fits(card, name):
    c = CARDS[card]
    low = name.lower()
    if not re.search(c["match"], low) or (c.get("skip") and re.search(c["skip"], low)):
        return None
    if re.search(r"\bdlc\b|bundle|subscription|membership|account\b|\bgift\s+\(", low):
        return None
    toks, up = tokens(name)
    if toks & OTHER_REGIONS:
        return None
    if "GLOBAL" in toks and not c["global_ok"]:
        return None
    if "NORTH AMERICA" in up and not c.get("na_ok"):
        return None
    f = face_of(name)
    return f if f in c["faces"] else None


def collect(api, rates):
    found = {}  # (card, face, store) -> offer
    for card, c in CARDS.items():
        for words in c["words"]:
            try:
                items = api.search(words)
            except Exception as ex:
                print("search failed:", words, ex, file=sys.stderr)
                continue
            for it in items:
                sid = store_of(it)
                if not sid:
                    continue
                name = str(it.get("Name") or "")
                face = fits(card, name)
                if not face:
                    continue
                if str(it.get("StockAvailability", "InStock")).replace(" ", "").lower() not in ("instock", ""):
                    continue
                try:
                    price, cur = float(it.get("CurrentPrice")), str(it.get("Currency") or "").upper()
                except (TypeError, ValueError):
                    continue
                if price <= 0 or cur not in STORES[sid]["cur"] or cur not in rates:
                    continue
                usd = round(price / float(rates[cur]), 2)
                # Guard against mismatched products: a real offer is between 60% and 140% of face value.
                if not (0.6 * face <= usd <= 1.4 * face):
                    continue
                url = str(it.get("Url") or "")
                if STORES[sid]["host"] not in url:
                    continue
                key = (card, face, sid)
                rank = STORES[sid]["cur"].index(cur)
                old = found.get(key)
                if old and (old["_rank"], old["usd"]) <= (rank, usd):
                    continue
                found[key] = {"store": sid, "usd": usd, "approx": cur != "USD", "cur": cur, "price": price,
                              "name": name, "url": url, "_rank": rank}
            time.sleep(0.3)
    return found


def build(found, old):
    stamp = now()
    cards = {}
    for card, c in CARDS.items():
        faces = {}
        for face in c["faces"]:
            offers = []
            for sid in STORES:
                o = found.get((card, face, sid))
                if o:
                    o = {k: v for k, v in o.items() if not k.startswith("_")}
                    o["checked"] = stamp
                else:
                    # keep the last good price for a store for up to STALE_DAYS
                    prev = next((p for p in old.get("cards", {}).get(card, {}).get("faces", {}).get(str(face), [])
                                 if p.get("store") == sid), None)
                    if prev and age_days(prev.get("checked")) <= STALE_DAYS:
                        o = prev
                if o:
                    offers.append(o)
            offers.sort(key=lambda o: o["usd"])
            faces[str(face)] = offers
        cards[card] = {"name": c["name"], "faces": faces}
    return {"updated": stamp, "stores": {k: {"name": v["name"], "kind": v["kind"]} for k, v in STORES.items()}, "cards": cards}


def age_days(ts):
    try:
        t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 86400
    except Exception:
        return 999


def main():
    sid, token = os.environ.get("IMPACT_ACCOUNT_SID"), os.environ.get("IMPACT_AUTH_TOKEN")
    if not sid or not token:
        print("Impact keys not set; nothing to do.")
        return 0
    api = Impact(sid, token)
    if len(sys.argv) > 2 and sys.argv[1] == "--probe":
        items = api.search(sys.argv[2], pages=1)
        print("fields:", sorted(items[0].keys()) if items else "none")
        for it in items[:40]:
            print(store_of(it), "|", it.get("CampaignId"), "|", it.get("Name"), "|", it.get("CurrentPrice"), it.get("Currency"),
                  "|", fits("psn", str(it.get("Name"))) or fits("xbox", str(it.get("Name"))))
        return 0
    rates = usd_rates()
    if not rates:
        print("No exchange rates; keeping the last prices.", file=sys.stderr)
        return 0
    try:
        old = json.load(open(OUT))
    except Exception:
        old = {}
    found = collect(api, rates)
    print("offers found:", len(found))
    if len(found) < 5:
        print("Too few offers; keeping the last prices.", file=sys.stderr)
        return 0
    data = build(found, old)
    json.dump(data, open(OUT, "w"), indent=1)
    for card, c in data["cards"].items():
        print(card, {f: [(o["store"], o["usd"]) for o in offs] for f, offs in c["faces"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
