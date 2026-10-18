# Endpoint recertification and slack specialization (proof note)

Same construction as PR1839, with two changes of finite constants.

**Supplier endpoint.** Let H be the unchanged global paid profile and W = 66,304, m = 73.
- Let `B` be the native endpoint in `overlay/new/SPEC.json`, `expected.complex_lower`, on the 1e-300 grid.
- The package's assembler (`code/assemble.py`, unchanged) first certifies the inherited 1e-24 bracket with the retained engines.
- It then calls the finer engines. These must give moment(B) < 1, i.e. the upper enclosure is below 1 in both `fine_mercator` and `fine_moment`. They must also give moment(B + 1e-300) > 1, i.e. the lower enclosure is above 1 in both.
- The conservative side repeats this with the 10^-16 · 32m^2 rank-one fallback share.

The finer engines are the same algorithms with larger constants:
- Mercator: an even number of alternating terms, which keeps the partial sum below the log (PR1519), and the tail bounded by the next term.
- Exponential: a Taylor series with a geometric tail bound.
- Outward rounding to DYAD 2^1100 or to a 1e-330 grid.
- The independent oracle check bounds every log enclosure they use with a 900-term atanh series and requires each to be tight.

Hence B lies below the moment root, and B + 1e-300 above it, with the same rigour as the 1e-90 certificate.

**Slacks.** Write h = 10^-310. Then:
- b = B − h, q = b − h, a = (q + b)/2;
- r0 = slack = h, zeta = 10^-312, stop = 10^-316;
- delta = 2h, epsilon = 1 − delta, beta = 1 − 3·delta.

The checks:
- The strict source-axis gap is delta − r0 = h > 0.
- The membership gap is 1 − beta − 2·delta = delta > 0.
- The Gaussian row exceeds main by delta(1 − 2q) > 0.
- The boundary saving is epsilon·q + slack.
- The effective-router gap is a − q = h/2 > 0, and stop·b < h/2.
- kappa = floor(epsilon·q·10^346)/10^346 − 10^-322 lies strictly below every cost saving.

All 59 inequalities, including the strict comparison with PR1839's exact rational, are checked as exact rationals in `outer/check_ledger.py`. The separate `outer/independent_check.py` re-derives the balance without importing the ledger.

Every slack is a fixed positive constant. The eventual polynomial/polylog absorption and source-prime existence arguments of PR1786/PR1673 therefore apply verbatim, with an unspecified larger cutoff. No uniformity as h → 0 and no equality at epsilon = 1 or at the supplier endpoint is claimed.
