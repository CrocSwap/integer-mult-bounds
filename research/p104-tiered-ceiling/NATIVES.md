# NATIVES: which premises of the tiered ceilings each word meets, and the script that computed it

Four word files were checked, each against every word-level premise of T1 (`ceiling_native_J`), T2a (`ceiling_noHJ`) and T2b (`ceiling_native_Z0`):

| name | word | file |
|---|---|---|
| st1 | the word of #7641 | `st1.json.gz` |
| w7637 | the #7637 word | `w7637.json.gz` |
| x1t2a | the x1t2a word | `x1t2a.json.gz` |
| e1 | the #7660 word | `e1.json.gz` |

All four share one owned layer (47 owned moves: 23 rises and 24 descents, mass 56 / 56) and one port set of 104 odd-weight vectors, so this is close to one data point, not four. A word that failed or could not be checked on any premise would be removed from the claims; none failed. **Lean treats every object in the three theorems as abstract and nothing in Lean ties a word to these hypotheses (in particular nothing ties the set `J` to a word).** The results below are exact computations by Python scripts (exact modular arithmetic over primes, exact integers, or outward-rounded 80-digit Decimal) run on the four word files, one core each. The scripts and word files are not part of this package. "Result" means the premise as computed, not a Lean fact.

Script key (all re-run on all four words, outputs identical where stated):
- `aud.py WORD PRIME`: per-arrival content replay, run with p = 2^61 - 1 and p = 2^64 - 59 (both agree on all four words).
- `aud2.py WORD`: public register dimension sequences (hmono, hd9, hmix) and owned rise/descent split.
- `aud2a.py WORD`: structural audit, FIX-1 split (ks, mr), Cap class and slack grid.
- `aud2b.py WORD`, `hc12.py WORD`: arrival-form junk set `J^arr`, SP checks; `hc12.py` adds legal-path reachability for every junk cell.
- `aud2c.py WORD`: decoder-route endpoints and rank of route-end X-contents.
- `aud2d.py WORD`: the 48-cells law over all port-spanned subspaces of dimension <= 4 of F2^9.
- `hc6.py` (word list extended to the four words): ks, mr, hF, hst, hY, hmass, hmd, hmr on an s grid.
- `j13.py` (the four words): hF and hEex as exact identities of exponential polynomials, hst ingredients, Cap margin on s in [.9, 1 - tJ0].
- `hc8.py WORD`, `hc11.py WORD`: route replay and forced-cell check.
- `hc9.py`, `jemit.py`, `emit.py`, `emit0.py`: certified bracket tables (word-independent).

## Premise x word

| premise (Lean name) | st1 | w7637 | x1t2a | e1 (#7660) | script |
|---|---|---|---|---|---|
| \|J^arr\| (for hJ : 4962 <= J.card) | 4962 | 4962 | 4962 | 4962 | `aud.py` (both primes), `aud2b.py`, `hc12.py` |
| per-row junk j_t; sum 1/(j_t+1) | [38, 48]; 2.1381 | same | same | same | `aud.py` |
| rank M | 11 | 11 | 11 | 11 | `aud.py` (15 distinct arrival vectors, rank 11) |
| D (arrival vectors, one per owned descending move; hD : D <= 56) | 24 | 24 | 24 | 24 | `aud.py`, `aud2a.py` (24 descents, 20 carry arrivals) |
| LawAModel hspan | holds | holds | holds | holds | `aud.py` (rows are combinations of the 15 arrival vectors by construction; rank equals rank M) |
| LawAModel hdiag (no zero diagonal) | 0 zero | 0 zero | 0 zero | 0 zero | `aud.py` |
| LawAModel hodd (odd off-diagonals vanish) | 0 odd | 0 odd | 0 odd | 0 odd | `aud.py` |
| LawAModel hpart (even partners <= 48) | 48 per row (4992) | 48 | 48 | 48 | `aud.py` |
| hmono | 0 violations | 0 | 0 | 0 | `aud2.py`, `aud2a.py` |
| hd9 | 0 violations | 0 | 0 | 0 | `aud2.py`, `aud2a.py` |
| hmix (<= 5) | 5 (tight) | 5 | 5 | 5 | `aud2.py`, `aud2a.py` |
| hk (every k in 1..9) | true | true | true | true | `hc6.py`, `aud2a.py` |
| hmass (56 <= ks.sum) | 102 | 102 | 102 | 102 | `hc6.py`, `aud2a.py` |
| hmd (8 <= len ks) | 37 | 37 | 37 | 37 | `hc6.py`, `aud2a.py` |
| hmr (8 <= mr) | 10 | 10 | 10 | 10 | `hc6.py`, `aud2a.py` |
| hY (104 <= st + len ks + mr) | st = 1266: 1313 | 1266: 1313 | st = 1265: 1312 | 1265: 1312 | `hc6.py`, `aud2a.py`, `j13.py` |
| hF (Finv s n <= ...) | exact identity, coefficient difference {} | {} | {} | {} | `j13.py` (and `hc6.py` on a grid: slack 0 up to 2e-12 float noise) |
| hEex (E := that exponential polynomial) | identity | identity | identity | identity | `j13.py` |
| hst | gaps >= 1, every main moves; grid slack >= 158 | >= 159 | >= 158 | >= 158 | `j13.py`, `hc6.py`; `aud2a.py` slack 0.0 at s = 1 only |
| Cap class (own cells, 48 N_f) | margin 19.349538 on s in [.9, 1 - tJ0] (`aud2a.py` grid: 19.356) | same | same | same | `j13.py`, `aud2a.py` |
| hcong / hdist support: every J^arr cell has a legal owned-descent-free path; no cell needs a cut | 0 cells without path | 0 | 0 | 0 | `hc12.py`; Cap margin as above |
| forced cells carry nonzero arrival coefficient | 2536 of 2536 | 2536 of 2536 | 2536 of 2536 | 2536 of 2536 | `hc11.py` |
| 48-cells law (max n*m over port-spanned subspaces) | 48 | 48 | 48 | 48 | `aud2d.py` (also `hc8.py`: native frames max 24) |
| 8 decoder routes, rank of route-end X-contents | 8 | 8 | 8 | 8 | `aud2c.py` |
| no public register enters any D_t; 0 SP violations; 0 even entries in Y_t | holds | holds | holds | holds | `aud2b.py`, `hc12.py` |

Reading the table against the Lean statements:
- `hcong`, `hdist` are real-analytic statements about a given `J` and `distF`. The scripts compute the combinatorial and numerical ingredients (legal paths for every J^arr cell, the Cap margin on s in [.9, 1 - tJ0], which contains the T2 ranges s <= 1 - tN0 and s <= 1 - tZ0); the step from these computations to the Lean `hcong`/`hdist` for `J = J^arr` is the lane's paper argument and is not formalised.
- `hspMono`, `hcstMono` (monotonicity of spF, cst on [t0, 1/10]) are a paper theorem, not computed on a word and not formalised; they are word-independent.
- The bracket hypotheses (`hspTab`, `hcstTab`, `hspTabJ`, `hcstTabJ`, `hspTabN`, `hcstTabN`) are word-independent. `hc9.py` (C tables) and `jemit.py` (J tables) re-run with every inequality certified (outward-rounded Decimal, weights rounded down, constants rounded up). `emit.py` and `emit0.py` (N and Z tables) were re-run with their output redirected: the emitted rational tables are identical to `CongestionNativeNDefs.lean` and `CongestionNativeZDefs.lean`. The Lean hypotheses (`spFlo <= spF t`, `cst t <= cH`) remain hypotheses.
- Informational (`hc8.py`, not a Lean premise, identical on all four words): the route-end contents are not proportional to the cfg6 rows and the prefix property fails on 5 route events. Nothing in the three theorems uses them.
- The link from the Lean `n` and `caller 6 7` / 17 to each word's invoice is the pricing script's (`pricekit`), not Lean's.

## What is not covered

- Words with |J^arr| < 4962 are outside T1. They are covered by T2a/T2b only if they meet all the other hypotheses of that theorem (hmix <= 5, hmono, hd9, hk, hmass, hmd, hmr, hY, hF, hst, hEex, hcong, hdist, and for T2a the LawAModel premises, hD, hJdef). None of these has been checked on any such word. No such word is known.
- Words with D > 56: T2b only, with the same proviso. No such word was checked.
- Decoders with 9 or more rows: T1/T2 hard-code `corrC <= 8 * cH` and `capC >= unLo / 48`, which model 8 decoder rows and 48 partners per row. Such decoders are outside the model.
- That an owned mass above 56 never pays is a paper argument, absent from the Lean chain.
- The class-wide bound |J| >= 1936 for decoders that are not rank 8, C = 56 is a conjecture.
- Network decoders.
