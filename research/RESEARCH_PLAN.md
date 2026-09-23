# Paper Trade v1 — Research & Prospective Validation Plan

## Scope

Build a paper-only prospective validation system for two frozen option strategies:

1. NoDip: NIFTY four-leg option-chain strategy based on the supplied CBR rule.
2. NoDip — 3W far expiry: the current/control NoDip maturity configuration.
3. NoDip — 1W far expiry: the added alternative NoDip maturity configuration.
4. MC-RQ6-v1: the frozen BATMAN Monte-Carlo four-leg strategy recovered from the supplied MC3 reference repository.

A manuscript is explicitly out of scope.

## Research questions

- RQ1: Can the NoDip flowchart be converted into a deterministic, point-in-time executable specification without post-hoc discretionary choices?
- RQ2: Does MC-RQ6-v1 reproduce the supplied MC3 control specification in a prospectively executable environment?
- RQ3: What are prospective trade frequency, gate rate, execution availability and net paper P&L under the frozen rules and documented frictions?
- RQ4: How sensitive are observations to bid/ask availability, adverse slippage, statutory/venue costs and lot-size chronology?
- RQ5: Are observations reproducible from stored source snapshots and configuration fingerprints?
- RQ6: How do the frozen NoDip far-expiry variants (3-week versus 1-week maturity selection) differ in signal availability, executable entry and prospective net P&L while holding the entry gate and near-expiry holding rule constant?

## Phase plan

| Phase | Branch | Deliverables | Exit criterion |
|---|---|---|---|
| 0 | main | Repository bootstrap and governance | Baseline repository exists |
| 1 | phase-1-foundation | Protocol, configs, source registry, logs, cached calendar | Specifications are internally consistent |
| 2 | phase-2-strategies | NoDip and MC engines, deterministic tests | Strategy tests pass; no look-ahead |
| 3 | phase-3-paper-trading | Ledger, live adapters, costs, schedulers | Scheduled/manual runs are executable |
| 4 | phase-4-pages | Static dashboard and raw-data views | Pages build reproducibly |
| 5 | phase-5-validation | Integration, smoke tests, prospective lock | End-to-end controls pass |

## Scientific controls

- Freeze strategy parameters before the first accepted prospective trade.
- Never use future quotes, expiry settlement, or future underlying closes in a signal.
- Store timestamps, provider metadata, source hashes and configuration fingerprints.
- Keep scans, non-trades and errors in append-only ledgers.
- Separate gross gate economics from executable entry economics.
- Report gross and net paper P&L separately.
- Model brokerage, STT, venue/SEBI/stamp/GST costs as configurable research assumptions.
- No synthetic live prices.
- Manual diagnostics cannot silently become prospective evidence.
- One open position per strategy/instrument/expiry/signature.
- No optimisation using prospective observations.

## Reporting

The operational site will report descriptive prospective metrics:

- valid scans and trade count;
- gate rate;
- executable-entry rate;
- mean and median net P&L;
- cumulative P&L;
- profitable-trade proportion;
- sequential drawdown;
- worst trade;
- cost contribution;
- live mark-to-market;
- provider failure rate.

Inferential analyses are deferred until a pre-registered prospective sample is available.

## Explicit exclusions

No manuscript, publication package or automatic parameter search will be generated.
