# Error / Limitation Log

2026-09-23 foundation: repository was initially empty; bootstrapped README before phase branching.

2026-09-23 CI: ledger syntax was corrected after compile failure.

2026-09-23 CI: D3 unit test expectation was corrected after test failure; implementation was retained.

2026-09-23: 2026 NSE holiday cache was expanded to the complete controlled list.

Limitations: GitHub Actions schedules are best effort; public option-chain providers can rate limit or change schema; SENSEX uses a third-party adapter; historical executable option quotes are not fabricated; brokerage and BSE transaction charges remain configurable research assumptions.

Corrections: NoDip uses adjacent far strikes, parity-based spot, no entry on same-day expiry, previous-session exit; MC SENSEX entry uses D3 gating; prospective configuration is fingerprint-locked.


## 2026-09-23 — Manual Runner #1

The master manual run failed because the SENSEX `indiaopt` BSE endpoint returned non-JSON/likely blocked HTML. This was a provider-data failure, not a strategy calculation failure. The master runtime was corrected to fail closed per underlying: log the provider error, record `DATA_UNAVAILABLE`, and continue evaluating the remaining strategies/underlyings rather than aborting the whole run. The manual workflow was also hardened with explicit write permissions, timeout and diagnostic `--manual` mode.


## 2026-09-23 — SENSEX provider correction

The first SENSEX implementation relied solely on indiaopt BSEClient with scrip `999920`, which failed on a live GitHub Actions run because BSE returned non-JSON content. Research of current public integrations found the BSE official API path `DerivOptionChain_IV/w` with the SENSEX scrip code `1` and the expiry endpoint `ddlExpiry_IV/w`. The runtime was corrected to use this official BSE API first, with indiaopt retained only as a fallback; no synthetic or stale quote is used.


## 2026-09-23 — Successful provider recovery

Master Paper Runner #3 completed successfully after the BSE provider correction. The latest SENSEX signal recorded `BSE_OFFICIAL_DERIVOPTIONCHAIN_IV` with `official=true`, expiry `24 Sep 2026`, and no new SENSEX provider error. The earlier two `999920` indiaopt failures remain as historical audit records.


## 2026-09-23 — Scheduler reliability review

GitHub Actions schedules are correctly configured with `Asia/Kolkata`, but GitHub documents that scheduled runs can be delayed under platform load and sufficiently high load can drop queued runs. Therefore exact wall-clock execution cannot be guaranteed by GitHub Actions alone. To reduce operational risk without changing the frozen NoDip signal definition, the workflows were hardened with pip caching, explicit timeouts, and MC-RQ6 redundant attempts at 09:30/09:35/09:40 within its already registered 09:25–09:40 acceptance window. NoDip remains fail-closed outside its 09:35 signal minute rather than silently turning a delayed run into a different signal.
