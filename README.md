# Paper Trade v1 — Prospective Validation

Paper-only prospective validation for two frozen NIFTY option strategies:

- **NoDip** — option-chain compression-bias rule based on the CBR gate shown in the supplied flowchart.
- **MC-RQ6-v1** — the frozen Monte-Carlo four-leg strategy referenced by the supplied MC3 page and specification.

This repository is intentionally **not** a manuscript repository. It is an operational research/validation harness with reproducible data capture, append-only ledgers, GitHub Actions schedules, tests, and a GitHub Pages dashboard.

## Current status

| Phase | Branch | Status |
|---|---|---|
| 0. Bootstrap / governance | main | DONE |
| 1. Foundation + protocol | phase-1-foundation | PLANNED |
| 2. Strategy engines | phase-2-strategies | PLANNED |
| 3. Prospective execution + schedulers | phase-3-paper-trading | PLANNED |
| 4. Pages dashboard | phase-4-pages | PLANNED |
| 5. Integrated validation | phase-5-validation | PLANNED |

## Scientific controls

- No live broker orders.
- Point-in-time signal information only.
- Source snapshots and checksums are retained.
- Bid/ask-aware simulated execution with explicit slippage.
- Paytm Money-aligned configurable cost model; account-specific brokerage can be overridden.
- Prospective configuration fingerprint is locked after the first accepted prospective trade.
- Errors and workflow outcomes are append-only and visible.
- Strategy parameters are not optimised on prospective observations.
- Manual runs are auditable and can be marked diagnostic-only.
- Scheduled workflows use Asia/Kolkata timezone and record the actual observation timestamp.

## Reference

The MC-RQ6 operational conventions are informed by the public MC-OPTIONS-VERIFICATION-MC3 repository and Pages site supplied for this project.

## Project files

- research/RESEARCH_PLAN.md
- research/PROTOCOL.md
- docs/DATA_SOURCE_REGISTRY.md
- research/logs/STATUS_LOG.md
- research/logs/ERROR_LOG.md
- research/logs/CONVERSATION_LOG.md