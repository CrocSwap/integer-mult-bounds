# Post-publication AI-agent technical review

Reviewed scientific commit: `f36782865dfe81abaa40254e8f41b8ccb3c54556`.
Proof clarification: `6cf4477f77c60edb8982fbc342a659206b5afceb`.
Review completed on 2026-10-09 UTC by a separate OpenAI AI agent after PR #124 was published.

The review supports the conditional saving
`kappa = 5519166047173/50000000000000000 = 0.00011038332094346`
under the retained analytic, recovery, prime, whole-residual, complete-row/copy,
and fixed-tape interfaces. It found no blocking mathematical gap or required
numerical correction in this construction. This is AI-agent technical review,
not human peer review, formal verification, or an official endorsement.

## Scope checked

- Birth-cut cancellation with correlated arbitrary dirty values and earlier source signals.
- All 2,106 pairs' liveness, nonaliasing, added residuals, and true reverse source chronology.
- Complete forward/inverse C operators and preserved spectators.
- Exact expanded readout coefficients, including 55/42, and the conservative charge G=3113921927424.
- Active-stack odd-denominator grid, boundary conversions, and row stock 15561 with degree 32000.
- Three strict moments, all 47 inequalities, and all seven final margins.

The exact published entrypoint was rerun in an isolated cloud mirror with four
hash-verified passive base inputs. It passed in 28.18 seconds with 380.1 MiB peak
memory; all 20 published files and the base inputs remained unchanged. No upstream
program was executed in that replay. The package's `run_checks.py` is the
reproduction entrypoint.

## Clarification applied

The concavity argument improves the unnormalized feasibility slack. The
normalized moment decreases at already feasible exponents; it need not decrease
at arbitrary infeasible exponents. The corrected proof makes this qualification
explicit. Its SHA256 is
`46b815acd08735170ae4060d1236df9ccfe2f44e1966ddb594a3a39a14980ebc`.
The numerical certificate and construction are unchanged.

This review does not establish an unconditional multiplication theorem, practical
speedup, global optimum, or successful upstream CI. The inherited general
interfaces remain explicit assumptions, and CI status is reported separately.
