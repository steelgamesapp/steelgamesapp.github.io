# SteelGames Price Check (browser extension)

Shows the best price, the lowest price ever, and a link to veteran and first responder discounts on Steam store pages.

## Try it now (Chrome, Edge, Brave)
1. Open `chrome://extensions` and turn on Developer mode.
2. Click "Load unpacked" and pick this `extension` folder.
3. Open any Steam game page.

## Publish
- Chrome Web Store: one-time $5 developer fee, zip this folder and upload it.
- Edge Add-ons: free, same zip.
- Firefox: free at addons.mozilla.org. Firefox needs `"background": {"scripts": ["background.js"]}` in place of `service_worker`.

Prices come from the CheapShark API. Nothing is collected from the person browsing.
