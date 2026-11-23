#!/usr/bin/env python3
"""Build and update the "NVIDIA: Jensen Huang is back" page (GitHub Pages, branch main, folder /).

One page, refreshed through the day. Each update:

    python3 scripts/publish.py update --src /mnt/project-files/jensen-reactions \\
        --label "1 PM refresh" --note "What changed, one or two sentences." \\
        --next "4 PM ET refresh, after the close"

copies the latest report, infographic and data files from --src, takes the price and
"as of" time from finance.json for the card, appends an entry to updates.json, re-renders the share
card (og.png) and rebuilds index.html. Then commit and push main.

    python3 scripts/publish.py build      # rebuild index.html and og.png from what is in the repo

Needs Python 3, plus cairosvg and the Inter font for the share card.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://dmgerbino.github.io/nvidia-jensen-huang-is-back/"
SITE_NAME = "Jensen Huang is back"
ET = dt.timezone(dt.timedelta(hours=-5), "ET")
OG_MARK = ("<!-- pub:og -->", "<!-- /pub:og -->")

# Files copied from the research folder on every update: (source, destination).
COPY = [
    ("report.html", "report.html"),
    ("infographic/nvda-huang-return.png", "media/nvda-huang-return.png"),
    ("infographic/nvda-huang-return.svg", "media/nvda-huang-return.svg"),
    ("reactions.json", "data/reactions.json"),
    ("NVDA-huang-return-data.json", "data/NVDA-huang-return-data.json"),
    ("finance.json", "data/finance.json"),
    ("price_points.json", "data/price_points.json"),
]


def jload(name):
    return json.load(open(os.path.join(ROOT, name), encoding="utf-8"))


def jsave(name, obj):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def et_label(ts):
    """'2026-11-23T12:33:22-05:00' -> '12:33 PM ET, Nov 23'."""
    t = dt.datetime.fromisoformat(ts).astimezone(ET)
    return t.strftime("%-I:%M %p ET, %b %-d")


def og_tags(site):
    c = site["card"]
    e = lambda x: html.escape(x, quote=True)
    v = re.sub(r"\D", "", site.get("updated_at") or site["first_published"])[:12]
    img = f"{SITE_URL}og.png?v={v}"
    alt = f'{c["name"]} share card: 90-day price line to the reinstatement, net income and EPS'
    tags = [
        ("property", "og:type", "article"), ("property", "og:site_name", SITE_NAME),
        ("property", "og:title", site["title"]), ("property", "og:description", site["description"]),
        ("property", "og:url", SITE_URL), ("property", "og:image", img),
        ("property", "og:image:width", "1200"), ("property", "og:image:height", "630"),
        ("property", "og:image:alt", alt),
        ("name", "twitter:card", "summary_large_image"), ("name", "twitter:title", site["title"]),
        ("name", "twitter:description", site["description"]), ("name", "twitter:image", img),
        ("name", "twitter:image:alt", alt),
    ]
    return (OG_MARK[0] + "\n" + f'<meta name="description" content="{e(site["description"])}">\n'
            + f'<link rel="canonical" href="{SITE_URL}">\n'
            + "\n".join(f'<meta {k}="{n}" content="{e(v)}">' for k, n, v in tags) + "\n" + OG_MARK[1])


PUB_CSS = """<style>
.pub{max-width:960px;margin:0 auto;padding:0 16px;font-family:var(--sans,'IBM Plex Sans',system-ui,sans-serif)}
header .pub-stamp,header .pub-media{font-family:var(--sans,'IBM Plex Sans',system-ui,sans-serif)}
header .pub-media a{color:var(--accent,#2A6DB0)}
.pub-stamp{margin:16px 0;padding:12px 16px;border:1px solid var(--border,#DDE1E6);border-radius:8px;background:var(--surface,transparent);font-size:.9375rem;line-height:1.5;color:var(--text,inherit)}
.pub-stamp b{font-weight:600}
.pub a{color:var(--accent,#2A6DB0)}
.pub-media{margin:24px 0}
.pub-media img{display:block;width:100%;max-width:520px;height:auto;border-radius:10px;border:1px solid var(--border,#DDE1E6)}
.pub-dl{font-size:.875rem;color:var(--muted,#5A626C);line-height:1.8}
.pub-log{margin:32px 0 48px}
.pub-log ol{list-style:none;padding:0;margin:0}
.pub-log li{padding:12px 0;border-top:1px solid var(--border,#DDE1E6);line-height:1.5}
.pub-log time{display:block;font-size:.875rem;font-weight:600;color:var(--muted,#5A626C)}
</style>"""


def build_page():
    site = jload("site.json")
    log = jload("updates.json")
    src = open(os.path.join(ROOT, "report.html"), encoding="utf-8").read()
    if not re.match(r"\s*<!doctype", src, re.I):
        src = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
               '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>\n'
               + src + "\n</body></html>\n")
    h = re.search(r"</head>", src, re.I)
    src = src[:h.start()] + og_tags(site) + "\n" + PUB_CSS + "\n" + src[h.start():]

    last = log[-1]
    nxt = site.get("next_update")
    stamp = (f'<div class="pub-stamp"><b>Last updated {html.escape(et_label(last["at"]))}</b> '
             f'({html.escape(last["label"])}). '
             + (f'Next: {html.escape(nxt)}. ' if nxt else "")
             + '<a href="#updates">What changed</a></div>')
    media = ('<section class="pub-media" aria-label="Infographic"><h2 class="sec">Infographic</h2>'
             '<a href="media/nvda-huang-return.png"><img src="media/nvda-huang-return.png" '
             'alt="NVIDIA reinstates Jensen Huang: stock move, analyst targets and reaction sentiment" loading="lazy"></a>'
             '<p class="pub-dl">Downloads: <a href="media/nvda-huang-return.svg" download>Infographic (SVG)</a>'
             ' · <a href="data/reactions.json" download>All quotes (reactions.json)</a>'
             ' · <a href="data/NVDA-huang-return-data.json" download>Snapshot (JSON)</a>'
             ' · <a href="data/finance.json" download>Market data (JSON)</a></p></section>')
    m = re.search(r"</header>", src, re.I)
    src = src[:m.start()] + stamp + media + "\n" + src[m.start():]

    items = "".join(f'<li><time datetime="{html.escape(u["at"])}">{html.escape(et_label(u["at"]))} · '
                    f'{html.escape(u["label"])}</time>{html.escape(u["note"])}</li>' for u in reversed(log))
    block = (f'<div class="pub"><section class="pub-log" id="updates"><h2 class="sec">Update log</h2>'
             f'<ol>{items}</ol><p class="pub-dl">This page is refreshed through the story. '
             f'Earlier versions are in the <a href="https://github.com/dmgerbino/nvidia-jensen-huang-is-back/commits/main">'
             f'commit history</a>.</p></section></div>')
    i = src.rfind("</main>")
    src = src[:i + len("</main>")] + "\n" + block + src[i + len("</main>"):]
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(src)

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import og
    og.card_png(site)


def cmd_update(a):
    for s, d in COPY:
        sp = os.path.join(a.src, s)
        if not os.path.exists(sp):
            sys.exit(f"Missing {sp}")
        os.makedirs(os.path.dirname(os.path.join(ROOT, d)) or ROOT, exist_ok=True)
        shutil.copyfile(sp, os.path.join(ROOT, d))
    fin = json.load(open(os.path.join(a.src, "finance.json"), encoding="utf-8"))
    site = jload("site.json")
    at = a.at or dt.datetime.now(ET).isoformat(timespec="seconds")
    site["updated_at"] = at
    site["updated_label"] = et_label(at)
    p = fin["price"]
    site["latest_price"] = {"date": fin["as_of"][:10], "price": p["last"], "as_of": fin["as_of"]}
    if a.next is not None:
        site["next_update"] = a.next or None
    jsave("site.json", site)
    log = jload("updates.json") if os.path.exists(os.path.join(ROOT, "updates.json")) else []
    log = [u for u in log if u["label"] != a.label] + [{"at": at, "label": a.label, "note": a.note}]
    jsave("updates.json", log)
    build_page()
    for root, _, files in os.walk(ROOT):
        if ".git" in root:
            continue
        for f in files:
            if os.path.getsize(os.path.join(root, f)) > 50 * 1024 * 1024:
                sys.exit(f"{f} is over 50 MB")
    print("Built index.html and og.png for", a.label)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update")
    u.add_argument("--src", required=True)
    u.add_argument("--label", required=True)
    u.add_argument("--note", required=True)
    u.add_argument("--at", help="ISO time of the update; defaults to now")
    u.add_argument("--next", help='Next scheduled update, e.g. "4 PM ET refresh"; "" clears it')
    sub.add_parser("build")
    a = ap.parse_args()
    cmd_update(a) if a.cmd == "update" else build_page()


if __name__ == "__main__":
    main()
