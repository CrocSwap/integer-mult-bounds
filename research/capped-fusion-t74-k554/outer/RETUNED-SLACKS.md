# Strict slacks of the PR1673 capped phase-cell fusion outer in this package

Construction, proof and every formula are Vlado Vojdanovski's PR1673 (vendored verbatim under `vendor/pr1673`); the classical-matrix boundary
constant c = 3/10 is Chafik Boukhalfa's PR1699 specialisation of Francois Le Gall's published exponent (`CLASSICAL-BOUNDARY.md`). The following
constants are free in PR1673's own text and audits (each only has to be strictly positive) and are set as follows:

| constant | PR1673 | PR1699 | here | why free |
|---|---|---|---|---|
| b (complex saving) | 17-decimal truncation | endpoint (22 digits) - 1e-30 | certified endpoint - 1e-64 | must lie strictly inside the certified supplier endpoint |
| q gap (q = b - gap) | 1e-10 | 1e-30 | 1e-64 | q < a_eff < b strictly |
| backoff after truncation | 1e-11 | 1e-42 | 1e-76 | strict gap absorbs polylog factors |
| layout slack s0 | 1e-5 | 1e-30 | 1e-64 | positive layout slack (carried by the boundary row in pkg4) |
| r0 | 1e-6 | 1e-30 | 1e-64 | only eventual u = alpha^2 <= p^r0 |
| zeta | 1e-8 | 1e-32 | 1e-66 | r + zeta > 0 gives g a B = o(p) |
| stop exponent | 1e-9 | 1e-36 | 1e-70 | any t_stop > 0 with (1-t)b > a_eff, q < (1-t)b |
| decimal floor | 1e-18 | 1e-48 | 1e-100 | rounding grid only |

The exact enclosure of the native moment sum uses a 1e-110 grid (130 log terms, 45 exponential terms) so that moment(b) < 1 and
moment(endpoint + 1e-64) > 1 are certified at this scale. kappa = 0.0016776417313433545642517275958639984231708545722735432722117400060454625429077941422798526440584702
(exact rational in `LEDGER.json`), above PR1699's exact kappa by 6.69e-25.
