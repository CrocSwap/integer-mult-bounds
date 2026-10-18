# Classical rich configurations at T = 3: Pappus and Desargues census (no kappa claim)

**Status: scoped negative result with exact per-instance minima. No counterexample to the
T = 3 core (Q <= F2), no new kappa, no supplier or selected-record change.** Contributor
Aaron Wang, with help from opencode (substantial AI assistance; no independent human review).

## What this establishes

The open-ends list of DreamingOfClouds
([discussion 1166 comment 18932893](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18932893),
item 4) names Pappus, Desargues, Reye and D4 line arrangements as untested classical rich
configurations that could be tight atoms (`cost = v`) or counterexamples (`cost < v`) for the
rank-3 decoder core. This package closes the first two of those four, on a stated bounded
domain, with exact arithmetic:

- **No falsifier.** Among **1,326,413** sub-configurations of the Pappus and Desargues valid
  pair sets priced exactly over *all* admissible pairings `B`, none has `cost(B) < v`.
  Every sub-configuration of size `v <= 4` is covered exhaustively (1,319,225 instances);
  sizes `v = 5..10` use a fixed-seed sample (7,188 further instances). The full pair sets
  (Pappus `v = 54`, Desargues `v = 70`) survive a randomized falsifier search.
- **Tight atoms are common at small sizes and vanish in the sample from size 7.**
  `cost = v` occurs at every size `v <= 6` in both geometries (Pappus 8,130 tight instances,
  Desargues 18,178; counts are dominated by the exhaustive `v <= 4` census). In the fixed-seed
  samples the smallest observed minimum rises strictly above `v` from size 7 on
  (Pappus `v = 7`: min 8; `v = 8`: min 10; `v = 9`: min 12; `v = 10`: min 14 on 1 exact instance).
- **The full pair sets are far from tight.** Best pairings found by randomized single-bit
  descent cost 108 on `v = 54` (block ranks 36,36,36) and 146 on `v = 70` (block ranks
  49,48,49), against dense-pairing costs 109 and 145 and identity-pairing costs 104 and 137.
  Nothing near `v` occurs, so the full Pappus/Desargues pair sets are not where the
  `cost >= v` question is tight.

This is a finite census, not a proof of `cost >= v` at T = 3 and not a general statement about
classical configurations.

**Nearest overlapping work (found at the pre-submission overlap refresh; credit below).**
[PR 2274](https://github.com/CrocSwap/integer-mult-bounds/pull/2274) (thakrarsagar, claim
[#1163 comment 18936306](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18936306))
already treats **the same object** (Desargues 10_3 and Pappus 9_3 as T = 3 decoder atoms) by a
different method: frame-universal char-2 (CR2) certificates, which give `cost >= v` for every
configuration of non-incident pairs in a certified frame, **conditional on Lemma CR2 of #2162**,
plus exact pairing-cost minima only for the 18 enumerable non-CR2 instances of one special
Pappus frame. This package is an independent, unconditional corroboration by direct exact
enumeration of raw pairing costs over all admissible `B`: it carries no CR2 premise, covers
1.3M small sub-configuration instances across both geometries (including the exhaustive
`v <= 4` census and tight-atom counts that PR 2274 does not compute), and adds the full
pair-set landscape. Neither result implies the other; PR 2274's frame-conditional coverage is
far broader in `v`.

## Model

The model is exactly the one of
[`research/three-total-decoders`](https://github.com/CrocSwap/integer-mult-bounds/pull/2111)
README section 1 (DreamingOfClouds), re-derived here and cross-read against that package's
`lib/kit.py`; no predecessor code is imported. A configuration is a set of lines
`t = (p(t), q(t))` with `p` a point in `Q^3`, `q` a covector, and `p(t) dot q(t) != 0`. Put
`R_j = {t : p_j(t) != 0}` and `A_j = {s : q_j(s) != 0}` for `j = 1..3`. An admissible pairing
`B` over `F2` has unit diagonal and `B_ts = 1` (`t != s`) only where `p(t) dot q(s) = 0`. The
cost is `cost(B) = sum_j rank_F2 B[R_j, A_j]` and the raw pairing cost of a configuration is
the minimum of `cost(B)` over all admissible `B`. The T = 3 core `(Q <= F2)` of that line,
together with the lift identity Lemma B of the merged #1590, predicts `cost >= v` for every
rank-3 configuration; `cost < v` would refute it.

## Configurations tested

The classical configurations are built from exact rational coordinates and checked to be
3-uniform (3 points per line, 3 lines per point):

- **Pappus** (9 points, 9 lines, 27 incidences): `A = (0,0,1), (1,0,1), (2,0,1)` and
  `B = (0,1,1), (1,1,1), (3,1,1)`, with the three cross-intersection points and the nine
  lines derived as cross products; the Pappus collinearity is asserted.
- **Desargues** (10 points, 10 lines, 30 incidences): triangles `(1,0,1), (0,1,1), (2,3,1)` and
  their images under central projection from `(0,0,1)` with parameters 2, 3, 5, plus centre,
  three axis points and the axis; the Desargues collinearity is asserted.

A configuration in the census is any set of valid pairs `(p, q)` with `p` a point and `q` a
line of the geometry and `p dot q != 0`, the same "all valid pairs and their subsets" reading
under which the #2111 pool is all primitive pairs in `{-1,0,1}^3` and `tied_min` is drawn from
the cube-diagonal / B3 two-support pairs. The full valid pair sets have 54 pairs (Pappus) and
70 (Desargues).

## Domain, method and measured counts

For each sub-configuration the exact minimum over **all** `2^f` admissible `B` is computed by
exhaustive enumeration (`f` = free incidences inside the three blocks), whenever `f <= 20`.
Sizes `v <= 4` are exhaustive over the whole pair set; sizes `v = 5..10` use `random.Random`,
seed 20261015, sampling the stated number of sub-configurations per size. RESULT.json holds
every count.

| Size v | Pappus tested / exact / tight | Desargues tested / exact / tight |
| --- | --- | --- |
| 1 | 54 / 54 / 20 | 70 / 70 / 25 |
| 2 | 1,431 / 1,431 / 198 | 2,415 / 2,415 / 308 |
| 3 | 24,804 / 24,804 / 1,310 | 54,740 / 54,740 / 2,510 |
| 4 | 316,251 / 316,251 / 6,579 | 916,895 / 916,895 / 15,318 |
| 5 | 3,000 / 3,000 / 20 | 3,000 / 3,000 / 15 |
| 6 | 1,500 / 1,500 / 3 | 1,500 / 1,500 / 2 |
| 7 | 300 / 300 / 0 | 300 / 300 / 0 |
| 8 | 60 / 56 / 0 | 60 / 60 / 0 |
| 9 | 20 / 13 / 0 | 20 / 17 / 0 |
| 10 | 10 / 1 / 0 | 10 / 6 / 0 |

"Exact" counts instances with `f <= 20` (fully enumerated); the remainder is recorded as
`skipped_f_cap` and was not priced exactly. Falsifiers are zero in every row.

## Controls

- **Positive, pinned:** `data/cex_wholeTS_v9.json` (from the #2111 head) must reproduce its
  documented exact minimum 18 with block ranks (7,4,7) and 16 minimisers, and
  `data/cex_joint_v7.json` its documented minimum 12 with block ranks (4,4,4) and 4
  minimisers. Both pass, from fixture bytes only.
- **Failure:** two ill-formed lines (`p(t) dot q(t) = 0`) are rejected; tampering with one
  fixture coordinate moves that fixture's optimum to 19 (so the positive control binds);
  disallowed `B` positions exist and are excluded by the admissibility filter.

## Reproduce

Standard library only, CPython 3.10+. From the repository root:

```sh
python3 -B research/classical-t3-config-screen-seed3e11/verify.py
python3 scripts/research_package.py --package research/classical-t3-config-screen-seed3e11 --check-only
```

Expected marker (measured 470 s on CPython 3.12.14, Windows x64):

```text
PASS_CLASSICAL_T3_CONFIG_SCREEN controls=18/12 pappus_exact=347410 pappus_tight=8130 desargues_exact=979003 desargues_tight=18178 falsifiers=0 full_best=108/146 no_new_kappa
```

The run writes `RESULT.json` with the per-size counts, the full-pair-set landscape and the
control receipts.

## Not checked

No lower bound is proved: `cost >= v` is verified only on the enumerated instances, and the
full pair sets carry only upper bounds (dense, identity, search best). The Reye configuration
and D4 line arrangements of the same open-ends item are not covered. The `(Q <= F2)` witness
form G1' (rank-preserving rational lift) and the rational side (Lemma B) are not re-checked.
No cold replay, supplier admission or selected-record change is involved; kappa is unchanged.

## Open next questions

- **Reye and D4 line arrangements.** The remaining two families of comment 18932893 item 4.
  Why it matters: it completes the named untested list. First step: fix a point/covector
  encoding for the Reye 12-point/16-line structure and rerun this census unchanged.
  Blocked by: no predecessor package pins an encoding for configurations whose classical
  lines are not covectors of a projective plane.
- **A whole-set lower bound.** Why it matters: the full pair sets are the actual rich
  configurations and enumeration cannot reach them. First step: try PR 2176's fixed-minor
  technique or the #2111 multi-copy certificate on the Pappus full pair set and record the
  certified value against v = 54. Blocked by: that certificate machinery is defined in
  #2111/#2162 package code not vendored here.
- **Tight atoms at sizes 7..12.** Why it matters: `tied_min` is tight at v = 12 in the
  `{-1,0,1}^3` world; a size >= 7 tight atom here would show the phenomenon is not special to
  that construction. First step: enlarge the fixed-seed samples or bias toward incidences as
  the #2111 Hesse experiment did. Blocked by: exact enumeration stops at f <= 20.

## Provenance and credit

Base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, task catalogue priority revision 4.
The model, the T = 3 open core, the lift route and the untested-classical-configurations lead
are DreamingOfClouds' ([#2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111),
[#2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162),
[comment 18932893](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18932893)
item 4); the Hesse-configuration experiment of #2111 section G7 is the model precedent for
drawing configurations from a classical geometry's point/line pairs. **thakrarsagar's
[PR 2274](https://github.com/CrocSwap/integer-mult-bounds/pull/2274)**
(`research/three-total-classical-configs`, claim
[#1163 comment 18936306](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18936306))
covers the same Pappus/Desargues object by frame-universal CR2 certificates conditional on
#2162's Lemma CR2; this package is a method-independent corroboration on its own bounded
domain, and that predecessor is not superseded by it. The two control fixtures
are vendored unmodified from the #2111 head `98da76c2839ba38538b510420dec54546ccabf0b`
(`research/three-total-decoders/data/cex_wholeTS_v9.json`, git blob
`a843cce049a2aadd5352763edeedd911cc2ebd1e`, SHA-256
`9e92b7b5f1221c180af3637ff70940aca5255b92f7b641efe3c615433e54761a`; and
`research/three-total-decoders/data/cex_joint_v7.json`, git blob
`cf7a3db872787a5480d6d6d49b5e52218a1c3905`, SHA-256
`6ef2af941ccad9f8a1c38f3a26020425022b5b09e15183b52dc0a3651261cde8`). Everything else in this
package is new. Apache-2.0.
