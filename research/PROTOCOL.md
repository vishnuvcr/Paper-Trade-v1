# Prospective Validation Protocol

The system is paper-only. It records what would have been traded using information available at the observation timestamp. It never submits broker orders.

## NoDip

Underlying: NIFTY. Signal time: 09:35 IST. Contract: nearest listed expiry.

ATM is the listed strike nearest point-in-time spot; lower strike wins ties. Near CE/PE = ATM CE/PE. Far CE = immediately higher listed CE strike. Far PE = immediately lower listed PE strike.

All four LTPs must be finite and strictly positive.

CBR = (Far CE / Near CE) / (Far PE / Near PE).

CBR > 1.20 means no trade. CBR <= 1.20 is eligible.

Legs: BUY Near PE; SELL Near CE; BUY Far CE; SELL Far PE.

BUY entry uses ask + 2 points when ask exists, otherwise LTP + 2. SELL uses bid - 2 points when bid exists, otherwise LTP - 2. Non-positive executable prices invalidate entry.

Exit is the previous trading session at 15:20 IST before expiry.

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
