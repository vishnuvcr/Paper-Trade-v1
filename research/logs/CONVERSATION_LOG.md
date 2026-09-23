# Conversation / Decision Log

## 2026-09-23

User requested a separate NoDip strategy option with two far-expiry selections:
- current 3-week far expiry;
- new 1-week far expiry.

Implementation decision:
- preserve the 3-week variant as the control (NODIP_3W);
- add an independent 1-week variant (NODIP_1W);
- near expiry remains the nearest listed expiry;
- far expiry is the first listed expiry on/after near expiry + 21 calendar days for 3W, or +7 calendar days for 1W;
- near CE/PE remain ATM at near expiry;
- far CE is the immediately higher listed strike than ATM at the selected far expiry;
- far PE is the immediately lower listed strike than ATM at the selected far expiry;
- the CBR gate remains unchanged;
- both variants exit on the previous trading session before the near expiry.

No prospective trade parameters are tuned from observations; the two variants are separate pre-specified research arms.
