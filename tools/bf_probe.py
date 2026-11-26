"""One-off probe: which joined Impact brands have discounted gaming gear in their feeds (prints only)."""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from giftcards import Impact  # noqa: E402

api = Impact(os.environ["IMPACT_ACCOUNT_SID"], os.environ["IMPACT_AUTH_TOKEN"])
seen = collections.Counter()
first = True
for kw in ["gaming keyboard", "gaming mouse", "gaming headset", "gaming monitor", "portable monitor", "gaming chair",
           "mini pc", "speakers", "earbuds", "usb-c hub", "charger", "headphones", "gaming desk", "game key steam"]:
    items = api.search(kw, pages=1)
    if first and items:
        print("FIELDS", sorted(items[0].keys()))
        first = False
    for it in items:
        camp = f'{it.get("CampaignId")}|{it.get("CampaignName")}'
        seen[camp] += 1
        try:
            cur, orig = float(it.get("CurrentPrice") or 0), float(it.get("OriginalPrice") or 0)
        except ValueError:
            continue
        if orig > cur > 0 and (orig - cur) / orig >= 0.1:
            print("DEAL", kw, "|", camp, "|", it.get("Name", "")[:70], "|", cur, orig, it.get("Currency"), "|", str(it.get("Url"))[:60])
print("CAMPAIGNS", seen.most_common(40))
