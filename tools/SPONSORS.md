# Booking a sponsor on SteelGames

Sponsored spots are controlled by one file: `sponsors.json` in the main folder of the site. When a sponsor pays, add one entry to it. When the run is over the spot disappears by itself on the `ends` date. There is nothing to rebuild.

## Where spots appear

| `slots` value | Where it shows | Matches on the Advertise page |
| --- | --- | --- |
| `home` | Top of the home page deals (and the Featured spot in the app) | Featured spot, $49 / week |
| `gear` | Top of the Gear guide page | Gear guide placement, $39 / month |

The Discord shout-out and the mission video are done by hand and are not in this file.

## One entry

```json
{
  "id": "acme-launch",
  "active": true,
  "slots": ["home"],
  "starts": "2026-11-20",
  "ends": "2026-11-27",
  "title": "Acme Quest is 30% off this week",
  "text": "A co-op adventure for 1 to 4 players.",
  "image": "https://example.com/acme-banner.jpg",
  "url": "https://example.com/acme-quest?ref=steelgames",
  "cta": "See the game"
}
```

`sponsors.json` holds a list of these inside square brackets, with a comma between entries. An empty list `[]` means nothing is booked, and the site shows a small "Advertise here" line instead.

Rules the page follows on its own:
- Shown only from `starts` through the whole of `ends`. Leave `starts` out to begin right away.
- `image` is optional. Use a banner at least 264 x 148 pixels.
- Every paid spot is labeled "Sponsored" and its link is marked as paid.
- If two sponsors book the same slot for the same dates, they take turns, one per hour.
- Only `http` and `https` links work.

## Results for the sponsor

Every view and click is counted in GoatCounter (steelgames.goatcounter.com) as an event named `sponsor-view/<id>/<slot>` or `sponsor-click/<id>/<slot>`. When a run ends, search for the `id` there and send the sponsor the two totals.

## Putting real traffic numbers on the media kit

The media kit page (`/media-kit/`) prints traffic only if `data/traffic.json` exists. Use this shape and update it monthly from GoatCounter:

```json
{
  "updated": "November 2026",
  "source": "GoatCounter",
  "rows": {
    "Visitors last 30 days": "12,400",
    "Page views last 30 days": "31,000"
  }
}
```

Only put numbers there that you can show on screen if a sponsor asks.
