# Dense-polar small-T gain screen (scoped negative; no κ claim)

**What this is.** A bounded, exact screen of the open question posed as item 3 of
[this request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590)
(DreamingOfClouds, 2026-10-14): the `T^2` threshold law of
[PR 2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125) is only
argued, and *"a proof, or a `T <= 6` configuration with cost < v, would settle
it"*. **No `T <= 6` configuration with cost < v was found** in the declared
domains below. This is a scoped negative over those domains, not an
impossibility proof.

Contributor: **Aaron Wang**, with help from opencode (substantial AI
assistance). Base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision 4, chooser nonce `f29c10b2afbbb16fee6c3f9fda099134`.
The drawn `recursive-interfaces` cards were covered or live-claimed at entry;
this takes the named open request instead (scope change recorded in
`TASK.json`).

## Model (unchanged, from #1590 / #446 Theorem C / PR 2125)

A configuration is a list of root lines `t = 1..v` with vectors
`p(t) = q(t)` in `Q^T`. The full-orthogonal-pattern pairing `B` has unit
diagonal and `B_ts = 1` exactly where `p(t)·p(s) = 0` (admissible). The exact
coordinate Gram decoder `M = sum_j p_j q_j^T = Gram` is priced

```text
cost = sum_{j=1..T} rank_F2 B[R_j, A_j],  R_j = supp p_j,  A_j = supp q_j,
```

Theorem C without the floor `w` (so any lower bound on this cost is the
stronger statement). A **gain** is `cost < v`, as in the PR 2125 table where
E7 (49 < 63) is the first gain found.

## Established

**1. Positive control: the PR 2125 table reproduces exactly** under an
independently written implementation (`search.py` re-derives roots, the exact
coordinate decoder over `Q`, and the F2 block ranks; PR 2125's code is pinned
but not imported):

| unit | v | T | cost (B0 or stored B) | expected (PR 2125) |
|---|---:|---:|---:|---|
| D4 / D5 / D6 (standard coords, B0) | 12 / 20 / 30 | 4 / 5 / 6 | 12 / 20 / 30 | 12 / 20 / 30 (CHECKED) |
| A4 / A5 / A6 (first-independent basis, B0) | 10 / 15 / 21 | 5 / 6 / 7 | 16 / 25 / 36 | 16 / 25 / 36 (B0 upper bounds) |
| E6 (stored basis + stored B) | 36 | 6 | 36 | 36 (CHECKED) |
| E6 (first-independent basis, B0) | 36 | 6 | 37 | 37 (recorded) |
| E7 (first-independent basis, B0) | 63 | 7 | 49 | 49 (CHECKED, first gain) |
| E8 (first-independent basis, B0) | 120 | 8 | 72 | 72 (CHECKED) |

F4 is record-only: standard coordinates with B0 give 36; PR 2125's recorded 24
is a value from a searched pairing/basis. Both are upper bounds on the F2
minimum (PR 2125 states its table costs are costs of specific `B`).

Mutation controls pass: replacing `B` by the identity changes the cost on D5
and E7, so the pricing is sensitive to the pairing as required.

**2. Exhaustive puncture censuses (no gain, exact coverage).** For every
nonempty subset of lines, with the decoder and `B` restricted to the subset:

| family | lines | subsets checked | gains (`cost < v`) | min(`cost - v`) | ties |
|---|---:|---:|---:|---:|---:|
| all {−1,0,1}^3 lines (T = 3) | 13 | 8,191 | 0 | 0 | 63 |
| D4 punctures (T = 4) | 12 | 4,095 | 0 | 0 | 63 |
| D5 punctures (T = 5) | 20 | 1,048,575 | 0 | 0 | 1,023 |

So `cost >= v` holds exactly (with frequent ties) on **all 1,056,861 tested
subsets**, including every `T = 3` configuration over the {−1,0,1}^3 alphabet.
The T = 3 slice is consistent with the open core statement (A) of PR 2111
(`cost >= v` at T = 3) on this alphabet.

**3. Full configurations at T <= 6 and bounded searches.** B5, B6, C6, D4,
D5, D6 and E6 tie at `cost = v`; A4-A6 and F4 (standard, B0) and the
{−1,0,1}^T line sets (v = 40 / 121 / 364 at T = 4 / 5 / 6) are strictly above
v. Notably the {−1,0,1}^T sets have `v > T^2` at T = 5, 6 (121 > 25,
364 > 36) and show **no** gain (cost − v = 184 / 824): `v > T^2` is not
sufficient for a gain, consistent with the law being a necessary-condition
claim. Seeded greedy and random puncture searches on E6, D6, B6, A6 and the
{−1,0,1}^T sets, and seeded basis pivots on E6, D6, B6, {−1,0,1}^4, {−1,0,1}^5
(cost depends on the basis; 120 random bases each plus the stored E6 basis),
find `min(cost - v) = 0` at best. No gain anywhere.

## Scope and limitations

- Cost is that of **one decoder per configuration** (the coordinate Gram
  factorization in the declared basis) with **`B = B0`** (or the stored E6
  pairing). The configuration's minimum over all admissible `B` and all
  exact factorizations can only be lower; a gain found here would have been a
  true gain, but a negative here excludes only the tested decoder/pairing
  pairs. PR 2125's annealed values (e.g. A5 at 21 < 25) confirm that other
  pairings can price lower.
- Covered exhaustively: subsets of the {−1,0,1}^3 line set, D4 and D5, in the
  declared bases. Everything else is bounded (seeded, recorded in
  `CERTIFICATE.json`): no exhaustive claim over E6/D6/B6/{−1,0,1}^T punctures,
  no non-root configurations, no `p != q` pairs, no overcomplete (`m > T`)
  decoders, no fields other than `Q`/`F2`.
- No claim about `T >= 7`, no supplier, no kappa change, no selected-record
  change. The T^2 law itself is not proved here.

## Open next questions

1. **Overcomplete punctures.** Does any `T <= 6` configuration admit an
   `m = T + 1` exact factorization (as in the E6 one-extra-frame families of
   PR 2240 / PR 2247) with cost < v? It matters because the coupling-lemma
   square floors fix `m = T`; a first step is the D5 puncture space with one
   redundant frame; blocker: the factorization space is infinite over `Q`
   and needs a finite support-cell reduction like the lambda-cell method.
2. **Pairing minimisation on the ties.** D5 punctures show 1,023 ties with
   `B = B0`; is `min_B cost = v` for these, or does a sparser `B` price below
   v? First step: exact search over `B` on the largest tie punctures; blocker:
   `rank_F2 B[R, A]` is not monotone in `B`, so branch-and-bound must be
   rank-aware.
3. **Basis sensitivity at T = 6.** The E6 stored basis prices 36 with `B = B0`
   and 37 in the first-independent basis. A GL_6(Q) optimisation of the basis
   (or a proof that the minimum over bases is >= v) would sharpen the screen.

## Reproduce

```sh
python3 -B research/polar-law-small-t-screen/verify.py
```

Expected final line: `PASS_POLAR_SMALLT_SCREEN`. Runs in a few minutes with
Python 3.10+ and the standard library only (no third-party packages, no SAT,
no solver). `search.py` writes `CERTIFICATE.json`; `verify.py` reruns the
screen and checks the certificate against the pinned expectations.
