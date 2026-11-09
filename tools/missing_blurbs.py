"""List tracked game pages that have no written About text yet (data/blurbs.json), with the facts needed to write one.

Run: python3 tools/missing_blurbs.py > missing.json
Write a 90-120 word, two-paragraph description in our own words for each, add it to data/blurbs.json keyed by
Steam app id, and the next build (or tools/build_seo.py's details step) puts it on the page."""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    blurbs = json.load(open(os.path.join(ROOT, "data", "blurbs.json")))
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "game", "*", "index.html"))):
        page = open(f, encoding="utf-8").read()
        m = re.search(r'data-steam="(\d+)"', page)
        if not m or m.group(1) == "0" or m.group(1) in blurbs:
            continue
        sid = m.group(1)
        title = re.search(r"<h1>(.*?)</h1>", page, re.S)
        meta = {}
        try:
            meta = json.load(open(os.path.join(ROOT, "data", "meta", sid + ".json")))["d"]
        except Exception:
            pass
        out.append({"appid": sid, "title": title.group(1).strip() if title else "", "genres": meta.get("genres", []),
                    "features": meta.get("features", [])[:8], "developer": meta.get("dev", []), "released": meta.get("released", ""),
                    "store_summary": meta.get("desc", "")})
    json.dump(out, sys.stdout, indent=1)
    print(f"\n{len(out)} game pages need a description", file=sys.stderr)


if __name__ == "__main__":
    main()
