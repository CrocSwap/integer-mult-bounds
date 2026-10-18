# Maximum on the declared fixed kappa grid

Credit: this argument and its parameter point are PR2180 / PR2161 (dataisfire, with OpenAI Codex assistance) on this series' PR2044; the ledger formulas are PR1786 (chafreaky / Chafik Boukhalfa), PR1673 (Vlado Vojdanovski), PR1758 and the Kothe lineage. Re-derived here at this package's own endpoint.

Let C be the certified complex supplier endpoint, F = 10^60046 the floor denominator and B = 10^-60022 the positive backoff of `outer/check_ledger.py`. Every point of the free-gap family uses 0 < epsilon < 1 and 0 < q < b < C and reports K = floor(F epsilon q)/F - B. Since C F is an integer (asserted exactly) and epsilon q < C, integer ordering gives

    K <= C - 1/F - B.

This bounds the declared grid/backoff family, not arbitrary suppliers, other backoffs or finer grids.

Choose r0 = 10^-60080, zeta = r0/100, layout slack = gap = r0, stop = r0/10^6, b = C - r0, q = C - 2 r0, delta = (1025/1024) r0, epsilon = 1 - delta, beta = 1 - 3 delta. Then 0 < C - epsilon q < 1/F, checked exactly, so the reported K equals the bound C - 1/F - B (asserted in `outer/check_ledger.py`, `outer/independent_check.py`).

All 62 strict inequalities of the earlier ledger and all 17 rejecting controls are retained. The main-binding family condition is now an explicit 63rd strict row, `gaussian_above_main`: Gaussian saving minus main saving = delta (1 - 2q) > 0. It was previously implicit in the checked beta window; it matters for rejection controls because the kappa floor/backoff (1e-60046, 1e-60022) is coarser than the free gaps (1e-60080), so a beta outside the main-binding window could still exceed the rounded kappa. The gamma spare power is r0/1024 > 0. All eventual cutoffs remain asymptotic; no practical cutoff is claimed.

The supplier, native words, owners, invoice, endpoint and fine engines are unchanged (this package's own verify.py re-admits them in full). The ledger re-encloses the native moment sum at the new b = C - r0 (moment(b) < 1) and at the test endpoint C + 1e-60000 (moment > 1).
