# Error / Limitation Log

2026-09-23 foundation: repository was initially empty; bootstrapped README before phase branching.

2026-09-23 CI: ledger syntax was corrected after compile failure.

2026-09-23 CI: D3 unit test expectation was corrected after test failure; implementation was retained.

2026-09-23: 2026 NSE holiday cache was expanded to the complete controlled list.

Limitations: GitHub Actions schedules are best effort; public option-chain providers can rate limit or change schema; SENSEX uses a third-party adapter; historical executable option quotes are not fabricated; brokerage and BSE transaction charges remain configurable research assumptions.

Corrections: NoDip uses adjacent far strikes, parity-based spot, no entry on same-day expiry, previous-session exit; MC SENSEX entry uses D3 gating; prospective configuration is fingerprint-locked.


## 2026-09-23 — Manual Runner #1

The master manual run failed because the SENSEX `indiaopt` BSE endpoint returned non-JSON/likely blocked HTML. This was a provider-data failure, not a strategy calculation failure. The master runtime was corrected to fail closed per underlying: log the provider error, record `DATA_UNAVAILABLE`, and continue evaluating the remaining strategies/underlyings rather than aborting the whole run. The manual workflow was also hardened with explicit write permissions, timeout and diagnostic `--manual` mode.
