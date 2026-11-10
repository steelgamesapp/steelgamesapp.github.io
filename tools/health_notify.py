#!/usr/bin/env python3
"""Turns tools/health_check.py's report into one GitHub issue, and heals the one problem a script can fix.

- High or medium problems  -> open (or update) ONE issue titled "Site health: needs attention". GitHub emails you when it opens.
- A new high-priority problem on an already-open issue -> one short comment, so you get another email.
- Everything fine again    -> comment "all clear" and close the issue.
- Low-only findings        -> no issue; they stay in the Actions run summary.
- 15% or more game pages with old prices -> start the page build again (once; skipped if a build is already running).

Needs GITHUB_TOKEN and GITHUB_REPOSITORY (the workflow provides both). DRY_RUN=1 prints what it would do.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TITLE = "Site health: needs attention"
DRY = os.environ.get("DRY_RUN") == "1"
REPO = os.environ.get("GITHUB_REPOSITORY", "steelgamesapp/steelgamesapp.github.io")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(method, path, body=None):
    if DRY and method != "GET":
        print(f"[dry run] {method} {path} {json.dumps(body)[:200] if body else ''}")
        return {}
    req = urllib.request.Request("https://api.github.com" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "SteelGames-health"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def main():
    report = open(os.path.join(ROOT, "health_report.md")).read()
    data = json.load(open(os.path.join(ROOT, "health_report.json")))
    actionable = [p for p in data["problems"] if p["severity"] in ("high", "medium")]
    high = data.get("high", 0)
    try:
        open_issues = api("GET", f"/repos/{REPO}/issues?state=open&per_page=100")
    except urllib.error.HTTPError as ex:
        print(f"Cannot read issues ({ex.code}); are Issues enabled on the repository? Report stays in the run summary.")
        open_issues = None
    existing = next((i for i in (open_issues or []) if i["title"] == TITLE and "pull_request" not in i), None)

    if open_issues is not None:
        if actionable:
            body = f"<!-- high:{high} -->\n" + report[:60000]
            if existing:
                before = int((re.search(r"<!-- high:(\d+) -->", existing.get("body") or "") or [0, 0])[1])
                api("PATCH", f"/repos/{REPO}/issues/{existing['number']}", {"body": body})
                if high > before:
                    api("POST", f"/repos/{REPO}/issues/{existing['number']}/comments",
                        {"body": f"New high-priority problem tonight ({high} high now, {before} before). Details are in the issue text above."})
            else:
                api("POST", f"/repos/{REPO}/issues", {"title": TITLE, "body": body})
        elif existing:
            api("POST", f"/repos/{REPO}/issues/{existing['number']}/comments", {"body": f"All clear as of {data['date']}. Closing."})
            api("PATCH", f"/repos/{REPO}/issues/{existing['number']}", {"state": "closed"})

    if data.get("stale_pct", 0) >= 15:
        busy = False
        for st in ("in_progress", "queued"):
            try:
                busy = busy or bool(api("GET", f"/repos/{REPO}/actions/workflows/seo.yml/runs?status={st}&per_page=1").get("workflow_runs"))
            except urllib.error.HTTPError:
                pass
        if busy:
            print("Many pages are stale, but a page build is already running.")
        else:
            print(f"{data['stale_pct']}% of game pages are stale: starting the page build.")
            api("POST", f"/repos/{REPO}/actions/workflows/seo.yml/dispatches", {"ref": "main"})


if __name__ == "__main__":
    main()
