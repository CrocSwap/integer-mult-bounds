# Polar-law screens at T >= 7 and a small-T overcomplete census

**Scoped negative results; no new kappa.** The dense-polar small-T screen of
[PR 2272](https://github.com/CrocSwap/integer-mult-bounds/pull/2272) left three obligations open: the T^2
threshold law at T >= 7, overcomplete (m = T + 1) decoders, and pairing minima on its 1,023 cost = v ties.
This package attacks the first two. No configuration at T = 7 or T = 8 outside the already-checked E7/E8
gains has dense-polar cost below v under the checked decoders, and no overcomplete decoder in the one-extra
rank-one family of [PR 2240](https://github.com/CrocSwap/integer-mult-bounds/pull/2240) beats v on any of
144,953 exhaustively censused punctures at T <= 4 or on any of 13 full sets at T <= 5.

Model, as in [PR 2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125) / PR 2272: a configuration
is a list of root lines `t = 1..v` with vectors `p(t) = q(t)` in `Q^T`. The full-orthogonal-pattern pairing
`B0` has unit diagonal and `B_ts = 1` exactly where `dot(p(t), p(s)) = 0`. An exact coordinate Gram decoder
`M = sum_j p_j q_j^T = Gram` is priced `cost = sum_j rank_F2 B[R_j, A_j]` (Theorem C without the floor),
where `R_j = supp p_j` and `A_j = supp q_j`. A gain is `cost < v`. All arithmetic is exact (integers,
rationals, F2 bitsets), standard library only.

## 1. Positive control: the checked table reproduces exactly

The engine re-derives the root systems, the exact coordinate decoders and the F2 block ranks independently;
PR 2125's `data/e6_best.json` is pinned read-only (SHA-256 in `SOURCES.json`) and supplies only the E6
stored basis and stored pairing. Before any new number was computed, the controls reproduced PR 2272's
checked table (PR 2125 values) exactly:

| unit | v | T | cost | expected | status |
|---|---:|---:|---:|---:|---|
| D4 (standard coords, B0) | 12 | 4 | 12 | 12 | CHECKED |
| D5 (standard coords, B0) | 20 | 5 | 20 | 20 | CHECKED |
| D6 (standard coords, B0) | 30 | 6 | 30 | 30 | CHECKED |
| E6 (stored basis, stored B) | 36 | 6 | 36 | 36 | CHECKED |
| E6 (first-independent basis, B0) | 36 | 6 | 37 | 37 | CHECKED |
| E7 (first-independent basis, B0) | 63 | 7 | 49 | 49 | CHECKED |
| E8 (first-independent basis, B0) | 120 | 8 | 72 | 72 | CHECKED |

The A4/A5/A6 first-independent-basis values 16/25/36 reproduce as well, and the mutation controls
(replace B by the identity) change the cost on D5 and E7, so the pricing is sensitive to the pairing.

## 2. Exact full-system screens at T = 7 and T = 8

Twelve systems, same rigor as PR 2272's full-system table (exact coordinate Gram decoder, B0). The
B/C/D families use standard coordinates, A7/A8 and E7/E8 the first-independent span basis, matching
PR 2272's conventions. Width is the decoder width (= span dimension); T^2 in the last column is width^2.

| unit | v | width | cost | cost - v | gain | v > T^2 |
|---|---:|---:|---:|---:|---|---|
| A7 | 28 | 7 | 49 | +21 | no | no |
| B7 | 49 | 7 | 49 | 0 | no | no (v = T^2 exactly) |
| C7 | 49 | 7 | 49 | 0 | no | no (v = T^2 exactly) |
| D7 | 42 | 7 | 42 | 0 | no | no |
| E7 | 63 | 7 | 49 | -14 | yes | yes |
| {0,+/-1}^7 | 1093 | 7 | 4501 | +3408 | no | yes |
| A8 | 36 | 8 | 64 | +28 | no | no |
| B8 | 64 | 8 | 64 | 0 | no | no (v = T^2 exactly) |
| C8 | 64 | 8 | 64 | 0 | no | no (v = T^2 exactly) |
| D8 | 56 | 8 | 56 | 0 | no | no |
| E8 | 120 | 8 | 72 | -48 | yes | yes |
| {0,+/-1}^8 | 3280 | 8 | 15760 | +12480 | no | yes |

Findings:

1. **No new T >= 7 gain.** The only systems with cost below v are E7 and E8, both already inside
   PR 2272's checked table. Every other T = 7/8 system ties or exceeds v under the checked decoder.
2. **The law's necessary condition survives T = 7 and T = 8.** Both gains have v above T^2
   (63 > 49 and 120 > 64); every system with v at or below T^2 has no gain. The B family sits exactly
   on the boundary: v = T^2 = cost at both T = 7 and T = 8. The {0,+/-1}^T sets again show that
   v above T^2 is not sufficient for a gain (cost - v = 3408 and 12480 under the checked decoder),
   extending PR 2272's T = 4/5/6 observation (40/121/364 lines).
3. The A family costs T^2 strictly above v at both T = 7 and T = 8 (49 and 64), continuing the
   A4-A6 pattern 16/25/36.

## 3. Bounded falsification searches at T = 7 and T = 8 (seeded 20261015)

Basis pivots (300 seeded random span bases each, exact recomputation of supports) and seeded
greedy/random puncture searches (12 restarts x 250 steps plus 200 random subsets, minimum size 2).
These are bounded searches, not exhaustive: no claim outside the recorded domains.

| unit | search | best cost | v of best | min(cost - v) |
|---|---|---:|---:|---:|
| A7 | basis pivots | 46 | 28 | +18 |
| B7 | basis pivots | 49 | 49 | 0 |
| D7 | basis pivots | 44 | 42 | +2 |
| E7 | basis pivots | 49 | 63 | -14 |
| A8 | basis pivots | 64 | 36 | +28 |
| B8 | basis pivots | 66 | 64 | +2 |
| D8 | basis pivots | 56 | 56 | 0 |
| A7 | punctures | 2 | 2 | 0 |
| B7 | punctures | 10 | 10 | 0 |
| D7 | punctures | 22 | 22 | 0 |

No puncture or basis pivot produced cost below v at T = 7 or T = 8 (E7's -14 is the already-known
in-table gain). The std coordinate decoder remains the best known for D7 (42) and B7 (49); the
random pivot search did not find it (minima 44 and 49).

## 4. Overcomplete (m = T + 1) decoders: one-extra rank-one census

The identity of PR 2240 with T + 1 terms (exact for every nonzero direction `a` and rational
`lambda != 0`, verified exactly in the replay):

```text
p_i = X e_i                      q_i = X(H e_i - lambda a_i a),  i = 1..T
p_{T+1} = X a                    q_{T+1} = lambda X a
```

Here `X` is the exact coordinate matrix of the lines in the declared basis and `H` the basis Gram, so
`sum_j p_j q_j^T = G = X H X^T`. The census enumerates every projective `{-1,0,1}^T` direction plus
every configuration line as direction, and for each direction every rational lambda support cell
(each open interval between consecutive breakpoints of the linear forms `p(t) . q_i` and each
breakpoint itself). Supports and F2 block ranks are constant between breakpoints, so the census is
exact on the declared family and alphabet, with B = B0 fixed.

Full sets (13 configurations, T = 3..5):

| unit | v | T | directions | cells | min cost | min - v |
|---|---:|---:|---:|---:|---:|---:|
| A3 | 6 | 3 | 13 | 102 | 9 | +3 |
| B3 | 9 | 3 | 22 | 120 | 9 | 0 |
| {0,+/-1}^3 | 13 | 3 | 13 | 88 | 18 | +5 |
| A4 | 10 | 4 | 40 | 340 | 16 | +6 |
| B4 | 16 | 4 | 56 | 320 | 16 | 0 |
| C4 | 16 | 4 | 56 | 320 | 16 | 0 |
| D4 | 12 | 4 | 52 | 288 | 12 | 0 |
| F4 | 24 | 4 | 56 | 416 | 36 | +12 |
| {0,+/-1}^4 | 40 | 4 | 40 | 360 | 84 | +44 |
| A5 | 15 | 5 | 121 | 1086 | 25 | +10 |
| B5 | 25 | 5 | 146 | 856 | 25 | 0 |
| C5 | 25 | 5 | 146 | 856 | 25 | 0 |
| D5 | 20 | 5 | 141 | 804 | 20 | 0 |

Exhaustive puncture censuses at T <= 4 (every nonempty subset of lines, family restricted to the
subset; the per-subset live-count prefilter is validated against unfiltered exact minima on five
deterministic subsets per configuration):

| unit | subsets | directions | members per subset | min(cost - v) | gains | ties |
|---|---:|---:|---:|---:|---:|---:|
| A3 | 63 | 13 | 102 | 0 | 0 | 13 |
| B3 | 511 | 22 | 120 | 0 | 0 | 91 |
| {0,+/-1}^3 | 8191 | 13 | 88 | 0 | 0 | 95 |
| A4 | 1023 | 40 | 340 | 0 | 0 | 37 |
| B4 | 65535 | 56 | 320 | 0 | 0 | 1279 |
| C4 | 65535 | 56 | 320 | 0 | 0 | 1279 |
| D4 | 4095 | 52 | 288 | 0 | 0 | 183 |

Finding: **no overcomplete decoder in this family beats v anywhere in the declared domain.** The
minimum over the family equals v exactly on every B/C/D-family full set and on 2,977 punctures
(counted ties), and exceeds v elsewhere. In particular, within this family no D5 decoder with
m = 6 terms reaches the requested cost 18 (minimum 20 = v), and no D4 or {0,+/-1}^3 puncture
admits an m = T + 1 factorization with cost below its v. Total: 144,953 subsets censused with
zero gains.

## Scope and limitations

- Cost is that of the declared factorizations priced with B = B0 (or the stored E6 pairing in the
  control). A gain found here would be a true gain, but the negative excludes only these
  decoder/pairing pairs: a sparser admissible B could price below the B0 values, so pairing
  minimization (PR 2272's open question 2, its 1,023 D5 ties) remains open.
- The overcomplete census covers exactly one factorization family: the one-extra rank-one identity
  above with the p_i = X e_i frame fixed, over the declared direction alphabet (all projective
  ternary directions in the declared basis plus all configuration lines). Unrestricted (m = T + 1)
  factorizations with moving frames are not covered; the finite support-cell reduction over Q for
  arbitrary factorizations is the recorded blocker.
- E6 is not in the overcomplete family census (PR 2240 and the transvection extension of
  [comment 18938558](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18938558)
  cover it in the pinned basis, with family minima 40 and 37 against the 35 target; the
  unrestricted seven-term E6 question stays open).
- D5 punctures (2^20 - 1 subsets) and all T >= 7 punctures are not enumerated (compute); the D5
  full set and the T = 7/8 full systems are covered exactly.
- Basis pivots are seeded (300 per unit) and bounded; no claim over all GL_T(Q) bases. The
  E7 basis question (is 49 the minimum over bases?) is open, mirroring PR 2272's E6 36-vs-37 question.
- The greedy/random puncture searches at T = 7/8 are seeded and bounded as recorded in
  CERTIFICATE.json. No kappa, supplier, paid-profile or selected-frontier change is claimed.

## Open next questions

1. **Pairing minima on ties.** On the tied D7/B7/A7 punctures (cost = v at B0), is the minimum over
   admissible pairings B exactly v, or can a sparser B price below v? That is PR 2272's open
   question 2 now at T = 7. First step: exact branch-and-bound over B on the largest tied punctures.
   Blocker: rank_F2 B[R, A] is not monotone in B, so no monotone relaxation is known.
2. **Unrestricted overcomplete factorizations at T = 3.** Does any (m = 4)-term exact factorization
   of the {0,+/-1}^3 Gram matrix with a moving frame beat v = 13? First step: a two-direction
   correction family (two independent extra frames) with its own exact support-cell reduction.
   Blocker: no finite support-cell reduction over Q is known for arbitrary (p_j, q_j) tuples.
3. **E7 basis minimum.** Is the B0 cost of E7 at least 49 over all GL_7(Q) bases (the T = 7 analogue
   of PR 2272's 36-vs-37 E6 question)? First step: deterministic basis descent with exact
   recomputation of supports. Blocker: support patterns are not continuous in the basis.

## Reproduce

From the repository root, with Python 3.12 or newer and only the standard library:

```sh
python3 -B research/polar-law-t7-overcomplete-screen/verify.py
```

Expected final line `PASS_POLAR_T7_OVERCOMPLETE_SCREEN` (about 316 s on this host). The registered
replay was run locally under Python 3.12; `make` is not installed on this host, so
`scripts/research_package.py` was used directly:

```sh
python3 scripts/research_package.py --package research/polar-law-t7-overcomplete-screen --check-only
```

prints `PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)`. To regenerate the
certificate after changing the search, run each stage with `--emit`, e.g.
`python3 -B research/polar-law-t7-overcomplete-screen/search.py --stage t7t8 --emit`.
Obligations not checked: host CI replay (queued), human review, and everything listed under
Scope and limitations.

## Credit and links

Model, cost formula and the threshold question: DreamingOfClouds,
[PR 2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125),
[PR 2228](https://github.com/CrocSwap/integer-mult-bounds/pull/2228),
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111), requests
[comment 18934590](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590)
item 3 and
[comment 18936173](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18936173)
Q1. Small-T screen, checked table and the three open obligations: Aaron Wang with help from opencode,
[PR 2272](https://github.com/CrocSwap/integer-mult-bounds/pull/2272). One-extra rank-one identity,
support-cell method and E6 family minima: 1337isnot1337,
[PR 2240](https://github.com/CrocSwap/integer-mult-bounds/pull/2240) and
[comment 18938558](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18938558).
Prior lattice work
[PR 446](https://github.com/CrocSwap/integer-mult-bounds/pull/446),
[PR 595](https://github.com/CrocSwap/integer-mult-bounds/pull/595),
[PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590). The E6 stored basis and pairing
are PR 2125's `data/e6_best.json`, pinned by SHA-256 in `SOURCES.json`. Prepared by Aaron Wang with
help from opencode (substantial AI assistance; no independent human review claimed). Apache-2.0.
