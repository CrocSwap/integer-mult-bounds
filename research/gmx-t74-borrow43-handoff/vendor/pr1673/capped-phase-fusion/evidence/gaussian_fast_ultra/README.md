# Gaussian inverse research package

Current conclusions, superseding the earlier open-upper remarks in LOWER-FACTOR.md:

1. **Fixed-width periodic norm theorem:** BILATERAL-LDU.md proves `||N^-1|| <= c^-4 exp(a/2)/(1-exp(-a rho theta))^2` for every fixed a>=1; at a=1 this is `<16 theta^-2`. The independent exact negative-origin controls are BILATERAL-CONTROLS.json.
2. **Complete one-dimensional data application:** LOWER-FACTOR.md supplies the lower factor with logarithmic guard overhead. UPPER-DATA-ALGORITHM.md supplies the upper factor and a direct periodic implementation with `O(s p polylog p)` data cost, shared per-axis coefficient preprocessing, and **Cp internal precision**. This is stated in the target `s>>poly(p)` regime. Exact controls are LOWER-CONTROLS.json, UPPER-DATA-CONTROLS.json, and CYCLIC-SCAN-CONTROLS.json.
3. **Length-preserving upper merge:** UPPER-LIFTING.md proves the Newton merge and bounded exact shear algebra. UPPER-MERGE-CONTROLS.json checks its degree indexing and factorization.
4. **Still open:** a realization of the normalized Hankel/Toeplitz steps with only logarithmic internal guard bits, and a bounded-depth width-preserving tensor circuit. Neither the analytic norm theorem nor the one-dimensional time bound establishes those, and no improved final multiplication exponent is claimed.

Replay all finite controls with Python 3:

```
python3 work/gaussian_fast_ultra/check_lower.py
python3 work/gaussian_fast_ultra/check_upper_merge.py
python3 work/gaussian_fast_ultra/check_bilateral.py
python3 work/gaussian_fast_ultra/check_upper_data.py
python3 work/gaussian_fast_ultra/check_cyclic_scan.py
```

The package uses no third-party source result beyond the elementary Newton polynomial identities stated and proved by their constructions. It retains the parent Gaussian notation and does not modify the frozen upstream manuscript.

Focused phase-fusion audit added later:

- `LOG-A-PHASE-SCHUR-AUDIT.md`: verifies strict row dominance at a=Theta(log p), polynomial Schur bounds, actual rounded Toeplitz interiors, and dyadic interior subdivision with only a logarithmic increase in boundary count. `LOG-A-SCHUR-CONTROLS.json` and `DYADIC-INTERIOR-CONTROLS.json` contain independent exact checks.
- `FORWARD-SMALL-A-AUDIT.md`: handles the distinct broad forward Gaussian S via b=pi/(alpha^2 rho^2), gives polynomial finite-block/completed-matrix inverse bounds, the exact target-grid chirp factorization, and the SPD Toeplitz circuit guard estimate. `FORWARD-CELL-CONTROLS.json` checks the coordinate and matrix identities.

These are interface components for the parent's focused partial-fusion proposal. They do not independently certify its full tensor schedule or final exponent.

- `CAPPED-GAUGE-AUDIT.md` independently validates capped dyadic interiors and exact reanchoring of the already-rounded narrow matrix, with local log range O(aB) rather than O(ad). It also validates the broad O(B/alpha^2) gauge and whole-boundary-group solve order. `CAPPED-GAUGE-CONTROLS.json` contains 27,216 partition checks and exact narrow/broad gauge controls. The capped final exponent ledger remains a separate assembly artifact.
