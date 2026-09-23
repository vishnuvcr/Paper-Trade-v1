# Data Source Registry

## Live option data

NSE public option-chain data are the primary NIFTY source. SENSEX uses the indiaopt open-source BSE adapter by default and records the provider as third-party. Provider failure is fail-closed.

## Historical underlying data

Yahoo Finance chart data are a secondary public source for daily NIFTY and SENSEX index closes. Retrieved data are cached with retrieval metadata and a content hash.

## Calendar

The NSE trading holiday feed is queried for futures/options dates and cached. A checked-in 2026 fallback is retained. BSE/SENSEX holiday handling is kept separate.

## Provider hierarchy

1. Exchange/public machine-readable source.
2. Attributable third-party adapter.
3. Explicit configured provider.
4. No synthetic fallback.

## Acceptance

An accepted signal requires target expiry, timestamp, point-in-time quote data, required strikes, provider metadata, source hash and configuration fingerprint.

Optional India VIX, global indices, USD/INR, gold and FII/DII summaries may be captured diagnostically and do not alter frozen signals.
