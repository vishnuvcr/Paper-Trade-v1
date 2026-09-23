# Error / Limitation Log

## 2026-09-23 — Foundation

The target repository was initially empty; root content lookup returned 404 because no commit existed. Resolved by bootstrapping README before phase branching.

## Design limitations

- GitHub Actions schedules are best-effort; actual observation timestamps are retained.
- Public option-chain providers can rate-limit or change schema; provider failure is logged and fails closed.
- SENSEX live data use a third-party integration and are labelled accordingly.
- Historical executable option bid/ask archives are not fabricated; the prospective layer uses current quotes only.
- Paytm Money brokerage is configurable because public pricing can vary by account/date.
- BSE holiday-feed automation is not treated as authoritative unless a machine-readable BSE calendar is available; the current D3 control uses the checked-in Indian market holiday baseline and live expiry.

## Corrections made during implementation

1. NoDip far strikes were frozen as adjacent listed strikes rather than arbitrary distance assumptions.
2. NoDip spot is derived from target-expiry put-call parity against previous close, not from strike medians.
3. NoDip does not open a position when the selected expiry is the current session.
4. NoDip near-expiry closing uses the previous trading session, not the MC D3 date.
5. MC SENSEX scans are guarded by the same explicit D3 calendar test before entry.
6. Configuration fingerprint is stored after the first prospective trade and checked before later runs.
