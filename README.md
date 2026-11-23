# NVIDIA: Jensen Huang is back

One page tracking the reaction to NVIDIA's Nov 23, 2026 reinstatement of Jensen Huang as President, CEO and director: every verified quote, sentiment charts, NVDA price targets, peers, fundamentals and technicals.

Live site: https://dmgerbino.github.io/nvidia-jensen-huang-is-back/ (GitHub Pages, branch `main`, folder `/`).

## Layout

- `index.html` is the published page: the report plus a "Last updated" stamp, the infographic, downloads and an update log. Generated; don't edit by hand.
- `report.html` is the report as built by the research pipeline (source).
- `site.json` holds the page title and description, the share card figures, `next_update` and the latest price.
- `updates.json` is the update log shown on the page, oldest first.
- `og.png` is the 1200x630 share card (Open Graph and Twitter), drawn by `scripts/og.py` in the Bank Earnings Reports design. The `?v=` on `og:image` changes with each update, so social sites fetch the new card.
- `media/` holds the infographic (PNG, SVG).
- `data/` holds the machine-readable files: `reactions.json` (all quotes), `NVDA-huang-return-data.json` (snapshot for infographic-to-video-v2), `finance.json`, `price_points.json`, and `prices/NVDA.csv` (daily closes for the card; sources in `prices/SOURCES.md`).

## Updating

After each refresh of the research folder:

```
python3 scripts/publish.py update --src /mnt/project-files/jensen-reactions \
  --label "4 PM refresh" --note "What changed, in a sentence or two." \
  --next "7 PM ET refresh"
git add -A && git commit -m "4 PM refresh" && git push origin main
```

Add each new daily close to `data/prices/NVDA.csv` first. Rendering the card needs `cairosvg` and the Inter font.
