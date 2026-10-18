# Strict slacks of the PR1673 capped phase-cell fusion outer in this package

Construction, proof and every formula are Vlado Vojdanovski's PR1673 (vendored verbatim under `vendor/pr1673`); the classical-matrix boundary
constant c = 3/10 is Chafik Boukhalfa's PR1699 specialisation of Francois Le Gall's published exponent (`CLASSICAL-BOUNDARY.md`). The following
constants are free in PR1673's own text and audits (each only has to be strictly positive) and are set as follows:

| constant | PR1673 | PR1699 | here | why free |
|---|---|---|---|---|
| b (complex saving) | 17-decimal truncation | endpoint (22 digits) - 1e-30 | certified endpoint (1e-300) - 1e-310 | must lie strictly inside the certified supplier endpoint |
| q gap (q = b - gap) | 1e-10 | 1e-30 | 1e-310 | q < a_eff < b strictly |
| backoff after truncation | 1e-11 | 1e-42 | 1e-322 | strict gap absorbs polylog factors |
| layout slack s0 | 1e-5 | 1e-30 | 1e-310 | positive layout slack (carried by the boundary row in pkg4) |
| r0 | 1e-6 | 1e-30 | 1e-310 | only eventual u = alpha^2 <= p^r0 |
| zeta | 1e-8 | 1e-32 | 1e-312 | r + zeta > 0 gives g a B = o(p) |
| stop exponent | 1e-9 | 1e-36 | 1e-316 | any t_stop > 0 with (1-t)b > a_eff, q < (1-t)b |
| decimal floor | 1e-18 | 1e-48 | 1e-346 | rounding grid only |

The exact enclosure of the native moment sum uses a 1e-340 grid (360 log terms, 100 exponential terms) so that moment(b) < 1 and
moment(endpoint + 1e-300) > 1 are certified (the supplier endpoint is certified to 1e-300 by finer-constant copies of the fine engines). kappa = 0.0016776417313433545642517275958639984231708545722735432722117400060454625429077941422798526440584702
(exact rational in `LEDGER.json`), above PR1699's exact kappa by 6.69e-25.


**Fine-prime package, 1e-300 endpoint refinement.** epsilon = 1 - DELTA_E with DELTA_E = 2e-310 (any DELTA_E > r0 = 1e-310 is admissible, outer/FINE-PADDING-COMPOSITION.md), beta = 1 - 3 DELTA_E; the formulas are unchanged, only these constants move.
