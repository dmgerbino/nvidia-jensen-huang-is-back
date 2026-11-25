# Closing prices for the share card

`NVDA.csv` holds daily closes (`date,close`) for the 90 calendar days ending on the reinstatement date (Nov 23, 2026). `scripts/og.py` draws the card's price line from it. Until the Nov 23 close is added, the card's last point is the intraday price in `site.json` `latest_price` (from `finance.json`).

| Ticker | Source | Range | Read on |
|---|---|---|---|
| NVDA | Yahoo Finance historical prices, https://finance.yahoo.com/quote/NVDA/history/ | Aug 24 – Nov 20, 2026 | Nov 23, 2026 |
| NVDA | Nov 23 close $165.05, Motley Fool Stock Market Today (4:40 PM ET), https://www.fool.com/coverage/stock-market-today/2026/11/23/stock-market-today-nov-23-nvidia-surges-31-adding-nearly-usd1-trillion-in-market-value-as-jensen-huang-reclaims-ceo-role/ | Nov 23, 2026 | Nov 23, 2026 |
| NVDA | Nov 24 close $155.38, Motley Fool Stock Market Today and Yahoo Finance | Nov 24, 2026 | Nov 24, 2026 |
