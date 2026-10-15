# Strict slacks of the PR1673 capped phase-cell fusion outer in this package

Construction, proof and every formula are Vlado Vojdanovski's PR1673 (vendored verbatim under `vendor/pr1673`); the classical-matrix boundary
constant c = 3/10 is Chafik Boukhalfa's PR1699 specialisation of Francois Le Gall's published exponent (`CLASSICAL-BOUNDARY.md`). The following
constants are free in PR1673's own text and audits (each only has to be strictly positive) and are set as follows:

| constant | PR1673 | PR1699 | here | why free |
|---|---|---|---|---|
| b (complex saving) | 17-decimal truncation | endpoint (22 digits) - 1e-30 | certified endpoint - 1e-3080 | must lie strictly inside the certified supplier endpoint |
| q gap (q = b - gap) | 1e-10 | 1e-30 | 1e-3080 | q < a_eff < b strictly |
| backoff after truncation | 1e-11 | 1e-42 | 1e-3022 | strict gap absorbs polylog factors |
| layout slack s0 | 1e-5 | 1e-30 | 1e-3080 | positive layout slack (carried by the boundary row in pkg4) |
| r0 | 1e-6 | 1e-30 | 1e-3080 | only eventual u = alpha^2 <= p^r0 |
| zeta | 1e-8 | 1e-32 | 1e-3082 | r + zeta > 0 gives g a B = o(p) |
| stop exponent | 1e-9 | 1e-36 | 1e-3086 | any t_stop > 0 with (1-t)b > a_eff, q < (1-t)b |
| decimal floor | 1e-18 | 1e-48 | 1e-3046 | rounding grid only |

The exact enclosure of the native moment sum uses a 2^-10413 grid (directed-rounding integer fixed point, atanh/exponential term counts derived from the grid in check_ledger.py) so that moment(b) < 1 and
moment(endpoint + 1e-3000) > 1 are certified (the supplier endpoint is certified to 1e-3000 by the repaired fine engines). kappa = 0.0016776417313433545642517275958639984231708545722735432722117400060454625429077941422798526440584702
(exact rational in `LEDGER.json`), above PR1699's exact kappa by 6.69e-25.


**Fine-prime package.** epsilon = 1 - DELTA_E with DELTA_E = 1.0009765625e-3080 (any DELTA_E > r0 = 1e-3080 is admissible, outer/FINE-PADDING-COMPOSITION.md), beta = 1 - 3 DELTA_E; all other slacks unchanged.

**Fixed-grid maximum.** The free gaps above are the point of PR2180 / PR2161 (dataisfire; stacking on this series' PR2044, PR1786 chafreaky / Chafik Boukhalfa and PR1673 Vlado Vojdanovski): r0 = 1e-3080, zeta = r0/100, layout slack = gap = r0,
stop = r0/10^6, b = C - r0, q = C - 2 r0, epsilon = 1 - (1025/1024) r0, beta = 1 - 3 (1025/1024) r0; the certified endpoint C, the floor grid F = 10^3046 and the backoff B = 10^-3022 are unchanged.
The ledger kappa is then exactly C - 1/F - B, the maximum of the declared floor-grid/backoff family (`outer/PROOF-GRID-MAX.md`). This is a statement about this grid and backoff only, not about other suppliers, backoffs or finer grids.
