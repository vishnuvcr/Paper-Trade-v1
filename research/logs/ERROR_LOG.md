# Error / Limitation Log

## 2026-09-23 — Repository inspection

- The new repository was initially empty. GitHub Contents API returned 404 because no commit existed.
- Resolution: bootstrap README on main before creating phase branches.

## Persistent limitations

- GitHub Actions schedules are best-effort and can be delayed; actual timestamps are stored.
- Public option-chain endpoints can be rate-limited or change schema.
- Third-party BSE data are not exchange-authoritative.
- Historical executable option bid/ask archives may require licensed data; no historical quotes are fabricated.
- Paytm Money pricing can vary by account/time; the configured number is a research assumption.
