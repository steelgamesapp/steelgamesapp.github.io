"""Builds data/home_promos.json: the picture slider of Black Friday deals and holiday gifts on the home page.
Reads the finished gifts page (/gifts/index.html), so it always matches what the gift shop shows.
Run after tools/gifts_page.py:  python3 tools/home_promos.py"""
import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'gifts' / 'index.html'
OUT = ROOT / 'data' / 'home_promos.json'

# (section id on the gifts page, label shown on the slide, how many to take)
SECTIONS = [
    ('deals', 'Black Friday', 8),
    ('under-25', 'Gift under $25', 3),
    ('under-50', 'Gift under $50', 3),
    ('under-100', 'Gift under $100', 3),
    ('under-200', 'Gift under $200', 2),
    ('big-gifts', 'Big gift', 2),
    ('creator', 'For streamers', 2),
    ('console', 'For console players', 2),
]

ART = re.compile(r'<article class="item"([^>]*)>(.*?)</article>', re.S)
TODAY = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).date().isoformat()  # US Central


def text(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


def items(page, sec_id):
    start = page.find(f'id="{sec_id}-h"')
    if start < 0:
        return []
    end = page.find('<h2', start + 10)
    chunk = page[start:end if end > 0 else len(page)]
    out = []
    for attrs, body in ART.findall(chunk):
        until = re.search(r'data-until="([0-9-]+)"', attrs)
        if until and until.group(1) < TODAY:
            continue  # time-limited offer has ended
        img = re.search(r'<img src="([^"]+)"', body)
        if not img or img.group(1).endswith('.svg'):
            continue  # only real product photos
        href = re.search(r'<a class="buy" href="([^"]+)"', body) or re.search(r'href="([^"]+)"', body)
        title = re.search(r'<h4>(.*?)</h4>', body, re.S)
        price = re.search(r'<div class="price"><b>([^<]+)</b>', body)
        code = re.search(r'<span class="code-chip">(.*?)</span>', body, re.S)
        if not (href and title):
            continue
        out.append({
            'title': text(title.group(1)),
            'img': html.unescape(img.group(1)),
            'href': html.unescape(href.group(1)),
            'price': text(price.group(1)) if price else '',
            'note': text(code.group(1)) if code else '',
        })
    return out


def main():
    page = SRC.read_text(encoding='utf-8')
    seen, slides = set(), []
    for sec_id, label, n in SECTIONS:
        took = 0
        for it in items(page, sec_id):
            if took >= n:
                break
            if it['img'] in seen or it['title'] in seen:
                continue
            seen.update([it['img'], it['title']])
            it['tag'] = label
            it['kind'] = 'deal' if sec_id == 'deals' else 'gift'
            slides.append(it)
            took += 1
    OUT.write_text(json.dumps({'slides': slides}, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'Wrote {len(slides)} slides to {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
