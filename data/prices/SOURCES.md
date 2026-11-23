# Closing prices for the share card

`NVDA.csv` holds daily closes (`date,close`) for the 90 calendar days ending on the reinstatement date (Nov 23, 2026). `scripts/og.py` draws the card's price line from it. Until the Nov 23 close is added, the card's last point is the intraday price in `site.json` `latest_price` (from `finance.json`).

| Ticker | Source | Range | Read on |
|---|---|---|---|
| NVDA | Yahoo Finance historical prices, https://finance.yahoo.com/quote/NVDA/history/ | Aug 24 – Nov 20, 2026 | Nov 23, 2026 |
