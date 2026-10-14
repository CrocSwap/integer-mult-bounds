# Strict slacks of the PR1673 capped phase-cell fusion outer in this package

Construction, proof and every formula are Vlado Vojdanovski's PR1673 (vendored verbatim under `vendor/pr1673`); the classical-matrix boundary
constant c = 3/10 is Chafik Boukhalfa's PR1699 specialisation of Francois Le Gall's published exponent (`CLASSICAL-BOUNDARY.md`), further generalised in this lineage via rectangular boundary batching (`outer/RECT-BOUNDARY.md`, Alman et al. arXiv:2404.16349, $\omega(1,1,2) < 3.250035$, $\tau_{\text{eff}} = 2.2500351$, $c = 0.37498245$). With our 600-digit certified complex supplier endpoint (Breakthrough 23 lineage), all outer slacks are refined to the $10^{-105}$ scale:

| constant | PR1673 | PR1699 | PR1725 | here | why free |
|---|---|---|---|---|---|
| b (complex saving) | 17-decimal truncation | endpoint (22 digits) - 1e-30 | certified endpoint - 1e-64 | certified endpoint - 1e-105 | must lie strictly inside the certified supplier endpoint |
| q gap (q = b - gap) | 1e-10 | 1e-30 | 1e-64 | 1e-105 | q < a_eff < b strictly |
| backoff after truncation | 1e-11 | 1e-42 | 1e-76 | 1e-105 | strict gap absorbs polylog factors |
| layout slack s0 | 1e-5 | 1e-30 | 1e-64 | 1e-105 | positive layout slack (carried by boundary row) |
| r0 | 1e-6 | 1e-30 | 1e-64 | 1e-105 | only eventual u = alpha^2 <= p^r0 |
| zeta | 1e-8 | 1e-32 | 1e-66 | 1e-107 | r + zeta > 0 gives g a B = o(p) |
| stop exponent | 1e-9 | 1e-36 | 1e-70 | 1e-110 | any t_stop > 0 with (1-t)b > a_eff, q < (1-t)b |
| decimal floor | 1e-18 | 1e-48 | 1e-100 | 1e-105 | rounding grid only |

The exact enclosure of the native moment sum uses a 1e-110 grid (130 log terms, 45 exponential terms) certifying moment(b) < 1 and moment(endpoint + 1e-64) > 1.
Certified kappa = 0.001677992607205282520732088774830808372222877897034109604209719498410908357589381610785525491892884241714 (exact rational in `LEDGER.json`), strictly exceeding PR1725 by +1.995811e-64 > 0.
