# Paper Trade v1 — Prospective Validation

Paper-only prospective validation for two frozen option strategies:

- **NoDip — 3W far expiry / NIFTY** — current/control four-leg CBR variant.
- **NoDip — 1W far expiry / NIFTY** — separate alternative maturity variant.
- **MC-RQ6-v1 / NIFTY + SENSEX** — frozen four-leg Monte-Carlo strategy based on the supplied MC3 reference.

This repository is **not a manuscript repository**. It is an operational research and paper-trading validation harness.

## GitHub Pages

This is a **project site**, so its URL is:

**https://vishnuvcr.github.io/Paper-Trade-v1/**

The root URL `https://vishnuvcr.github.io/` is the separate user/organization site location and is expected to return 404 until a repository named `vishnuvcr.github.io` exists. GitHub documents project sites as `<owner>.github.io/<repositoryname>`.

## Current status

| Phase | Branch | Status |
|---|---|---|
| 0. Bootstrap | main | DONE |
| 1. Foundation | phase-1-foundation | DONE |
| 2. Strategy engines | phase-2-strategies | DONE |
| 3. Paper-trading runtime + schedulers | phase-3-paper-trading | DONE |
| 4. GitHub Pages | phase-4-pages | DONE |
| 5. Validation controls | phase-5-validation | DONE |

The integrated implementation is on `main`. The Pages workflow now deploys on every push to `main`, on its schedule, and through a manual workflow button.

## Automatic schedule

- NoDip assessment: 09:35 IST on weekdays; the scheduled run evaluates both the 3W and 1W far-expiry variants independently.
- NoDip near-expiry close check: 15:25 IST on weekdays; each variant exits relative to its near expiry.
- MC-RQ6-v1 assessment: 09:30 IST on weekdays; only D3 is eligible.
- Open-position marks: 10:15, 12:15, 14:15, 15:15, 15:25 and 15:35 IST on weekdays.
- GitHub Pages deployment: every 15 minutes during the market window, on push, plus a manual button.
- Every workflow exposes workflow_dispatch/manual execution. The NoDip workflow lets you choose ALL, NODIP_3W, or NODIP_1W.

## Scientific controls

- No live broker orders.
- Point-in-time signal data only.
- Provider provenance and source hashes are recorded.
- Bid/ask-aware paper execution with 2-point adverse slippage per leg.
- Configurable brokerage and statutory/venue cost model.
- Configuration fingerprint locks after the first accepted prospective trade.
- Append-only signals, events, errors and run ledgers.
- Missing market data fail closed; synthetic prices are not permitted.
- Historical daily MC inputs are cached in the repository after retrieval.

## Data hierarchy

NIFTY live options use the public NSE option-chain path with indiaopt and direct NSE fallback. NoDip evaluates the nearest expiry plus either a 1-week or 3-week far expiry. SENSEX uses the official BSE option-chain path first, with an explicit third-party fallback. Historical underlying closes use cached Yahoo Finance chart data. Expiry comes from the live chain rather than weekday assumptions.

## Reference

MC-RQ6 conventions were checked against the supplied MC-OPTIONS-VERIFICATION-MC3 repository and Pages site.

## Key files

- research/RESEARCH_PLAN.md
- research/PROTOCOL.md
- docs/DATA_SOURCE_REGISTRY.md
- config/strategies.yml
- config/costs.yml
- src/papertrade/
- tests/
- .github/workflows/
- research/logs/STATUS_LOG.md
- research/logs/ERROR_LOG.md
- research/logs/CONVERSATION_LOG.md
