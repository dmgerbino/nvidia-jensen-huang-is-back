#!/usr/bin/env python3
"""Open Graph share card (1200 x 630 PNG) for the "NVIDIA: Jensen Huang is back" page.

Same design as the Bank Earnings Reports cards (approved by David on Nov 14, 2026),
with an event subtitle and a time-stamped "Updated" line for intraday refreshes.

Needs cairosvg (python3 -m pip install cairosvg) and the Inter font installed.
scripts/publish.py calls it; you can also run it directly:

    python3 scripts/og.py                 # re-render og.png from site.json

Inputs:
  site.json                 card figures ("card"), first_published, updated_label,
                            latest_price (an intraday point added after the last close)
  data/prices/<TICKER>.csv  daily closes, header "date,close"; the card uses the
                            90 calendar days ending on card.event_date
Output: og.png at the repo root.

Design approved by David on Nov 14, 2026 (mockups in project storage,
og-image-mockups/). Keep layout changes in step with that approval.
"""
import csv
import datetime as dt
import json
import os
import sys
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRICES = os.path.join(ROOT, "data", "prices")
W, H = 1200, 630
PAD = 64
# X (Twitter) lays the site domain over the bottom of a summary_large_image card,
# so the bottom SAFE_BOTTOM px stay plain background: no text, no chart.
SAFE_BOTTOM = 96
CONTENT_BOTTOM = H - SAFE_BOTTOM
# Bump when the card layout changes, so the ?v= on og:image changes and social
# sites fetch the new image instead of their cached copy.
CARD_VERSION = "2"
WINDOW_DAYS = 90

# Site dark tokens (index.html), pure black per the branding guide.
BG = "#000000"
FG = "#F0EDEA"
MUTED = "#A39F99"
RULE = "#25292E"
ACCENT = "#5B9BD5"
UP = "#46C28E"
DOWN = "#F26B6B"
FONT = "Inter"
SITE = "dmgerbino.github.io/nvidia-jensen-huang-is-back"
SITE_NAME = "Jensen Huang is back"


def text(x, y, s, size, fill=FG, weight=400, anchor="start", ls=0):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size:g}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}">{escape(s)}</text>')


def svg_doc(body):
    check_safe_band(body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{BG}"/>'
            f'{body}</svg>')


def check_safe_band(body):
    """Refuse any text baseline or chart point inside the bottom band X covers."""
    import re
    limit = CONTENT_BOTTOM - 12  # leave room for descenders
    ys = [float(y) for y in re.findall(r'<text[^>]* y="([\d.]+)"', body)]
    ys += [float(y) for y in re.findall(r'\by[12]?="([\d.]+)"', body)]
    ys += [float(y) for y in re.findall(r'[ML]\s*[\d.]+,([\d.]+)', body)]
    ys += [float(c) + float(r) for c, r in re.findall(r'cy="([\d.]+)" r="([\d.]+)"', body)]
    bad = [y for y in ys if y > limit]
    if bad:
        raise ValueError(f"Card content at y={max(bad):.0f} enters the bottom {SAFE_BOTTOM}px kept clear for X.")


def fmt_date(d):
    if isinstance(d, str):
        d = dt.date.fromisoformat(d)
    return d.strftime("%b %-d, %Y")


def render(svg, png_path):
    try:
        import cairosvg
    except ImportError:
        sys.exit("Rendering share cards needs cairosvg: python3 -m pip install cairosvg")
    cairosvg.svg2png(bytestring=svg.encode(), write_to=png_path,
                     output_width=W, output_height=H)
    return png_path


# ----------------------------------------------------------------- bank card
def load_closes(path, end, days=WINDOW_DAYS):
    if not os.path.exists(path):
        sys.exit(f"No closing prices at {path}. Add a CSV with header date,close "
                 f"covering the {days} days to the release date.")
    start = end - dt.timedelta(days=days)
    pts = []
    for r in csv.DictReader(open(path)):
        d = dt.date.fromisoformat(r["date"].strip())
        if start <= d <= end:
            pts.append((d, float(r["close"])))
    pts.sort()
    if len(pts) < 20:
        sys.exit(f"{path} has only {len(pts)} closes between {start} and {end}; need the full window.")
    if (end - pts[-1][0]).days > 4:
        sys.exit(f"{path} ends {pts[-1][0]}, more than a few days before the release ({end}).")
    return pts


def sparkline(pts, x0, y0, w, h):
    vals = [v for _, v in pts]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    n = len(pts)
    xy = [(x0 + w * i / (n - 1), y0 + h - h * (v - lo) / span) for i, v in enumerate(vals)]
    first, last = vals[0], vals[-1]
    chg = (last / first - 1) * 100
    col = UP if chg >= 0 else DOWN
    base_y = y0 + h - h * (first - lo) / span
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    area = path + f" L{xy[-1][0]:.1f},{y0+h} L{xy[0][0]:.1f},{y0+h} Z"
    ex, ey = xy[-1]
    s = [
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{col}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>',
        f'<line x1="{x0}" y1="{base_y:.1f}" x2="{x0+w}" y2="{base_y:.1f}" stroke="{MUTED}" '
        f'stroke-width="2" stroke-dasharray="2 8" stroke-linecap="round" opacity="0.7"/>',
        f'<path d="{area}" fill="url(#g)"/>',
        f'<path d="{path}" fill="none" stroke="{col}" stroke-width="4" '
        f'stroke-linejoin="round" stroke-linecap="round"/>',
        f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="16" fill="{col}" opacity="0.25"/>',
        f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="9" fill="{col}" stroke="{BG}" stroke-width="3"/>',
    ]
    return "".join(s), chg, col


def fit(s, size, max_w, em=0.55):
    """Shrink a font size so a line of roughly `em` width per character fits max_w."""
    return min(size, max_w / (em * max(len(s), 1)))


def bank_card(c, updated=None):
    """c: name, exchange, ticker, quarter, released (date), published (date), closes,
    net_income, net_income_note, [net_income_label], [eps, eps_note, eps_label]."""
    b = []
    b.append(text(PAD, 84, c["name"], round(fit(c["name"], 56, W - 2 * PAD), 1), weight=700, ls=-1))
    b.append(f'<text x="{PAD}" y="130" font-family="{FONT}" font-size="32">'
             f'<tspan fill="{ACCENT}" font-weight="600">{escape(c["exchange"])}: {escape(c["ticker"])}</tspan>'
             f'<tspan fill="{MUTED}" font-size="30"> · '
             + (escape(c["subtitle"]) if c.get("subtitle") else
                f'{escape(c["quarter"])} results, released {escape(fmt_date(c["released"]))}')
             + '</tspan></text>')

    # Sparkline, with its change label on the right.
    sx0, sy0, sw, sh = PAD, 162, W - 2 * PAD - 210, 182
    spark, chg, col = sparkline(c["closes"], sx0, sy0, sw, sh)
    b.append(spark)
    arrow = "▲" if chg >= 0 else "▼"
    b.append(text(W - PAD, sy0 + sh / 2 + 6, f'{arrow} {chg:+.1f}%'.replace("-", "−"), 44, col, 700, "end"))
    b.append(text(W - PAD, sy0 + sh / 2 + 46, "90 days to", 26, MUTED, 400, "end"))
    b.append(text(W - PAD, sy0 + sh / 2 + 78, c.get("window_label") or "release", 26, MUTED, 400, "end"))

    # Numbers: net income always, EPS vs consensus only when one exists.
    ny = 396
    b.append(text(PAD, ny, c.get("net_income_label") or "Net income", 28, MUTED, 500))
    b.append(text(PAD, ny + 62, c["net_income"], 64, FG, 700, ls=-1))
    b.append(text(PAD, ny + 100, c["net_income_note"], 28, MUTED))
    if c.get("eps"):
        ex = PAD + 420
        b.append(text(ex, ny, c.get("eps_label") or "Adjusted EPS", 28, MUTED, 500))
        b.append(text(ex, ny + 62, c["eps"], 64, FG, 700, ls=-1))
        b.append(text(ex, ny + 100, c.get("eps_note", ""), 28, MUTED))

    # Footer: dates and site.
    fy = ny + 100  # level with the net income note line
    if updated:
        b.append(text(W - PAD, fy - 34, f"Updated {updated}", 28, FG, 600, "end"))
        b.append(text(W - PAD, fy, f'First published {fmt_date(c["published"])}', 24, MUTED, 400, "end"))
    else:
        b.append(text(W - PAD, fy, f'Published {fmt_date(c["published"])}', 28, FG, 600, "end"))
    b.append(text(W - PAD, ny, SITE_NAME, 26, ACCENT, 600, "end"))
    b.append(text(W - PAD, ny + 34, "by @dmgerbino", 26, MUTED, 400, "end"))
    return svg_doc("".join(b))


# ---------------------------------------------------------------- site glue
def card_png(site):
    """site: the parsed site.json. Renders og.png at the repo root."""
    c = site["card"]
    event = dt.date.fromisoformat(c["event_date"])
    closes = load_closes(os.path.join(ROOT, "data", "prices", f'{c["ticker"]}.csv'), event)
    lp = site.get("latest_price")
    if lp and dt.date.fromisoformat(lp["date"]) > closes[-1][0]:
        closes.append((dt.date.fromisoformat(lp["date"]), float(lp["price"])))
    card = dict(c, released=event, published=site["first_published"], closes=closes)
    up = site.get("updated_label")
    return render(bank_card(card, updated=up), os.path.join(ROOT, "og.png"))


if __name__ == "__main__":
    print(card_png(json.load(open(os.path.join(ROOT, "site.json")))))
