"""Adds the site-wide LIVE RAM scrolling strip (/assets/ram-ticker.js) to every page that has the
SteelGames site header. Safe to run again and again: pages that already load it are skipped.
Run by .github/workflows/ram-ticker.yml after each site update, so regenerated pages keep the strip."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAG = '<script src="/assets/ram-ticker.js" defer></script>'
changed = 0
for p in ROOT.rglob('*.html'):
    if any(part.startswith('.') for part in p.relative_to(ROOT).parts) or p.relative_to(ROOT).parts[0] == 'assets':
        continue
    t = p.read_text(encoding='utf-8', errors='ignore')
    if '/assets/ram-ticker.js' in t or 'site-header' not in t or '</head>' not in t:
        continue
    p.write_text(t.replace('</head>', TAG + '\n</head>', 1), encoding='utf-8')
    changed += 1
print(f'Added the RAM ticker to {changed} page(s).')
