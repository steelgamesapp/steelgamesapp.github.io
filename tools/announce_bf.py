"""One-time Black Friday announcement to the SteelGames Discord (deal-bot webhook). Approved by Jon Nov 26, 2026."""
import json, os, urllib.request

hook = os.environ["DISCORD_WEBHOOK_URL"]
url = "https://steelgamesapp.com/black-friday/?utm_source=discord&utm_campaign=bf2026"
payload = {
    "username": "SteelGames Deals",
    "content": "🔥 **Black Friday is live on SteelGames** 🔥",
    "embeds": [{
        "title": "Black Friday & Cyber Monday gaming deals hub",
        "url": url,
        "color": 0xFF7A1A,
        "description": (
            "Live sale prices pulled straight from each store, refreshed every 3 hours until Cyber Monday:\n\n"
            "⌨️ **Gaming gear up to 60% off**: SOLAKAKA keyboards and mice, AutoFull gaming chairs and desk bundles\n"
            "🎮 **PC game keys 25%+ off**: big names like Hogwarts Legacy, Red Dead Redemption 2 and Borderlands 4\n"
            "🎁 **Gift cards under face value**: PlayStation, Xbox, Nintendo, Steam and Roblox, compared across stores\n"
            "🛒 Store-wide sales from Amazon, Redragon, GMKtec and more\n\n"
            "Prices change fast, so the store's checkout has the final price."),
        "footer": {"text": "Veteran-owned • steelgamesapp.com"},
    }],
}
req = urllib.request.Request(hook, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "User-Agent": "SteelGames"})
print("Discord:", urllib.request.urlopen(req, timeout=30).status)
