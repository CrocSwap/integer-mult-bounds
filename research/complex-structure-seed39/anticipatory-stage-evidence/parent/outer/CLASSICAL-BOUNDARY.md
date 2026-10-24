# Classical-matrix boundary (tau = 2.372864 here; PR1699 used 12/5)

PR1673 (Vlado Vojdanovski) charges the batched boundary algebra W^(tau-1) where tau is a fixed target exponent for W-square complex matrix
products; its stability lemma only requires omega_C < tau (it is stated there for the supplied omega_C <= 9/4 premise, tau = 19/8).
Chafik Boukhalfa (PR1699, `research/t74-signed554-phase-fusion/CLASSICAL-MATRIX-TRANSFER.md`) observed that Francois Le Gall's published
theorem omega < 2.3728639 (ISSAC 2014, arXiv 1401.7714, Table 1 and Section 6.3) already gives omega_C < 12/5, so the matrix branch needs no
unproven premise. This package adopts that specialisation: the boundary exponent is epsilon - xi + (tau-1)/2 = epsilon - xi + 7/10, the boundary
saving is 3/10 + xi - epsilon, and the ledger constant is c = (3 - tau)/2 = 3/10. The checks `matrix_exponent_above_published_bound`
(12/5 > 2.3728639) and `matrix_exponent_below_five_halves` are in the ledger; the exponent is an external published theorem and is not
re-proved here (neither in PR1699 nor in this package). The boundary row is far above the binding rows, so the final kappa is set by the
main transform = fused Gaussian balance with the sparse-union row carrying the layout slack, exactly as in PR1673's matrix corollary (this paragraph describes the PR1699 configuration; in this package the union row is relaxed by the new radix schedule and the boundary row binds, see the end of this file).

What changes here relative to PR1699 is purely numerical and uses the freedom already in PR1673's proof: every strict slack (r0, zeta, layout slack,
q gap, stop exponent, decimal floor, backoff) is only required to be positive; they are set to 1e-100 or below, and b is the certified complex
endpoint minus 1e-100 instead of a 22-digit truncation minus 1e-30. The native moment test of the supplier is re-enclosed on a 2^-572 grid
(directed-rounding integer fixed point, atanh/exponential term counts derived from the grid in check_ledger.py): moment(b) < 1 and moment(endpoint + 1e-90) > 1 are both proven by exact rational enclosures.
Resulting kappa exceeds PR1699's exact kappa 0.001677641731343354564251058287... by about 6.7e-25.


## Change in this package

The target exponent is tau = 2.372864 (just above Le Gall's published 2.3728639; PR1699's lemma only needs omega_C < tau), so c = (3 - tau)/2 = 0.313568. With the union row relaxed by the radix-distributed schedule (outer/UNION-SCHEDULE.md, new in this package) the boundary row binds: boundary saving c + xi - eps = kappa + slack, and kappa is set by the balance epsilon = (1 + q + q(c - s - r - zeta))/(1 + q)^2, xi = epsilon (1 + q) - c + s. The checks `matrix_exponent_above_published_bound` (tau - 2.3728639 = 1e-7 > 0) and `matrix_exponent_below_five_halves` are in the ledger.

## Superseded in this package

The square exponent tau = 2.372864 above is replaced by the rectangular-batching effective exponent tau_eff = 2.1567081 (k = 5, outer/RECT-BOUNDARY.md). Le Gall's bound is no longer used in the ledger.

## Superseded again in pkg7

The boundary exponent is now tau_eff = 2 + 1e-100 from structured solves (outer/STRUCTURED-BOUNDARY.md); the fallback is the k = 5 batching of outer/RECT-BOUNDARY.md.
