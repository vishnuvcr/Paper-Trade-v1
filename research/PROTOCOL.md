# Prospective Validation Protocol

The system is paper-only. It records what would have been traded using information available at the observation timestamp. It never submits broker orders.

## NoDip

Underlying: NIFTY. Signal time: 09:35 IST. Each scheduled scan evaluates two independent frozen variants.

### NoDip — 3W far expiry

Near expiry = nearest listed expiry on or after the observation date. Far expiry = first listed expiry on or after near expiry + 21 calendar days.

### NoDip — 1W far expiry

Near expiry = nearest listed expiry on or after the observation date. Far expiry = first listed expiry on or after near expiry + 7 calendar days.

For both variants, ATM is the listed near-expiry strike nearest the point-in-time NIFTY spot; lower strike wins ties. Near CE/PE = ATM CE/PE at the near expiry. Far CE = the immediately higher listed strike than ATM at the selected far expiry. Far PE = the immediately lower listed strike than ATM at the selected far expiry.

All four LTPs must be finite and strictly positive.

CBR = (Far-expiry CE / Near-expiry CE) / (Far-expiry PE / Near-expiry PE).

CBR > 1.20 means no trade. CBR <= 1.20 is eligible.

Legs: BUY Near PE; SELL Near CE; BUY Far-expiry CE; SELL Far-expiry PE.

BUY entry uses ask + 2 points when ask exists, otherwise LTP + 2. SELL uses bid - 2 points when bid exists, otherwise LTP - 2. Non-positive executable prices invalidate entry.

Both variants exit on the previous trading session at 15:20 IST before the **near expiry**. The selected far expiry is therefore a maturity choice for the far legs, not the holding period.

## MC-RQ6-v1

Underlyings: NIFTY and SENSEX. Signal target: 09:30 IST. Acceptance window: 09:25–09:40 IST.

Expiry is the nearest listed expiry. D3 is the first of the final three trading sessions before expiry, using exchange-specific trading holidays.

History: final 756 finite daily log returns strictly before D3. Monte Carlo: 5,000 paths, seed 756, three-session horizon, IID with-replacement sampling, geometric compounding.

Spot proxy: put-call-parity median from the target-expiry snapshot when within 2% of previous close; otherwise previous close.

Quantiles: P20/P35/P65/P80. Map to nearest unique listed strikes, absolute distance then lower-strike tie-break.

Portfolio: BUY 1 P35, SELL 2 P20, BUY 1 C65, SELL 2 C80. Gate: gross MC-EV > 0. Exit: expiry settlement after the derivatives close.

## Costs and firewall

Primary friction is 2 points adverse slippage per leg. Brokerage, STT, exchange charges, SEBI fee, stamp duty and GST are configurable research assumptions. After the first accepted prospective trade, the strategy configuration fingerprint is locked and configuration changes are rejected.

Manual runs are diagnostic unless explicitly enabled inside the accepted window. Only prospective_valid=true observations enter validation statistics.
