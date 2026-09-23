# Conversation / Decision Log

## 2026-09-23 — User request

Create a new paper-trading GitHub Pages project in vishnuvcr/Paper-Trade-v1 for:
- the supplied NoDip NIFTY CBR strategy;
- the supplied MC-RQ6-v1 four-leg Monte-Carlo strategy;
- prospective validation;
- automatic public data retrieval;
- one master manual workflow;
- scheduled assessment and entry workflows;
- scientific auditability;
- MC-OPTIONS-VERIFICATION-MC3 as reference;
- no manuscript output.

## Design decisions

- Paper-only; no live broker orders.
- MC-RQ6-v1 remains frozen to the MC3 control.
- NoDip is deterministic from the supplied diagram; operational definitions are frozen before first prospective trade.
- Source snapshots, timestamps, config fingerprints and append-only ledgers are mandatory.
- Prospective results are not used for tuning.
