# The c=7 diagonal equality case carries no six-source depth-two block

**Scoped obstruction. No new κ.** In the unchanged unsigned dirty connector,
no length-42 floor word makes every pair on the diagonal `s + t = 45` a
weight-3 mask. That is the equality case of the weight-3 count at
characteristic 7: twenty masks and twenty candidate slots. The case is empty.
Whether a six-source depth-two block still exists by using some pair off this
diagonal is open.

## Interface, unchanged

A floor word on `k = 6` sources in characteristic `c = 7` has length 42 and
calls each source exactly seven times. `q_t` is the count vector of the first
`t` letters, so `q_0 = 0`, `q_42 = (7,7,7,7,7,7)`, and each step adds one
basis vector. Counts stay in `{0,...,7}`. The word has depth two when every
nonzero binary mask is congruent modulo 7 to `q_s + q_t` for some
`0 ≤ s ≤ t ≤ 41`. This is the interface of PR4231/PR4248, as used by
PR6141.

A pair realizes a **weight-3 mask** when `q_s + q_t` has every coordinate in
`{0,1,7,8,14}` and exactly three coordinates in `{1,8}`. The value 15 cannot
occur: each count is at most 7. The coordinate sum of any such vector is
`3 + 7λ` with `λ` the number of coordinates in `{7,8,14}` counted as
`1,1,2`, and the identity `s + t = 45` on this diagonal forces the total
`λ`-mass to be 6.

The pairs with `s + t = 45`, `s ≤ t ≤ 41` are exactly `(s, 45-s)` for
`s = 4,...,22`. There are 19 of them. Together with the single early pair
`(0,3)`, PR6107's weight identity gives 20 slots, and `C(6,3) = 20`. Nick
Petalas's handoff of 2026-11-03 records that this restricted model is the
tight case, and that a SAT encoding of it had no verdict. This note proves
the model is empty. The early pair `(0,3)` is not needed for the
contradiction.

## Proof

**Centre.** At `s = 22` the partner is `t = 23`, so
`q_23 = q_22 + e_c` for the single letter `c` in position 22. Write `r`
for `q_22`. Each coordinate of `2r + e_c` lies in `{0,1,7,8,14}`, the centre
source satisfies `r_c ≤ 6`, and `∑ r_j = 22`. The only pairs `(r_j, δ_j)`
that work are:

| `δ` | `r` | sum | mask bit | `λ` |
|---|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 4 | 8 | 1 | 1 |
| 0 | 7 | 14 | 0 | 2 |
| 1 | 0 | 1 | 1 | 0 |
| 1 | 3 | 7 | 0 | 1 |

Let the centre be type `(r,δ) = (0,1)` or `(3,1)`, and let `n_0, n_4, n_7`
count the other five coordinates of types `(0,0)`, `(4,8)` and `(7,14)`.

- Centre type `(0,1)`. Weight 3 forces `n_4 = 2`. The count sum
  `8 + 7 n_7 = 22` forces `n_7 = 2`, so `n_0 = 1`. Two coordinates equal 14.
- Centre type `(3,1)`. Weight 3 forces `n_4 = 3`. The count sum
  `15 + 7 n_7 = 22` forces `n_7 = 1`, so `n_0 = 1`. One coordinate equals 14.

There is no third type. Every weight-3 centre therefore has at least one
coordinate equal to 14, and both counts on that coordinate are 7.
`verify.py` exhausts all `8^6` count vectors of length 22 and finds 300
realizations: 180 of the first type and 120 of the second. All 300 have a 14.

**One step.** Write `S(s) = q_s + q_{45-s}` and let `w_t` be the letter in
position `t`. The prefix identity `q_{t+1} = q_t + e_{w_t}` gives

```text
S(s+1) = S(s) + e_{w_s} - e_{w_{44-s}}.
```

This is the same recurrence as the handoff. If `w_s = w_{44-s}` the sum is
unchanged. Otherwise one coordinate increases by 1 and another decreases by
1. Inside `{0,1,7,8,14}`, a `+1` is possible only from 0 to 1 or from 7 to 8,
and a `-1` only from 1 to 0 or from 8 to 7. The value 14 is on neither list,
so that coordinate is not `w_s` and not `w_{44-s}`. It stays 14, on the same
source.

**Induction.** Suppose every pair `(s, 45-s)` for `s = 4,...,22` is a
weight-3 realization. The centre has a source `j` with sum 14. Each step
down to `s = 4` keeps coordinate `j` equal to 14. At `s = 4` both `q_4[j]`
and `q_41[j]` are 7. But the coordinates of `q_4` sum to 4, so none of them
is 7.

Therefore no such word exists.

## What this does not say

The argument needs every index `s = 4,...,22` to be a weight-3 realization.
One failed index stops the induction. An off-diagonal pair, with
`s + t ∈ {3,10,17,24,31,38,52,...}`, can realize a weight-3 mask; the prefix
`jjjjabc` does so at `s + t = 10`. The full depth-two question at `c = 7`
asks whether those pairs can replace the diagonal slots. This package does
not decide that, and it does not rerun the SAT search. No supplier, consumer,
or selected frontier changes. The selected conditional κ remains the record
in `certificates/selected-result.json`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-diagonal-obstruction/verify.py
python3.12 -I -O -W error -B research/six-source-c7-diagonal-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-diagonal-obstruction --check-only
```

The marker is `PASS_SIX_SOURCE_C7_DIAGONAL_OBSTRUCTION centres=300 type01=180 type31=120 frozen_coordinates=480 moves=+[0, 7]/-[1, 8] controls=4`.
The 480 frozen coordinates are two per type-`(0,1)` centre and one per
type-`(3,1)` centre. The checker rejects a five-4s near-miss centre, treats
14 as immovable, and rejects every length-4 count vector in `{0,...,7}^6`
that already contains a 7.

## Open next questions

1. Does a six-source depth-two block exist at `c = 7` once a weight-3 mask
   may be realized off `s + t = 45`? *Why:* this is now the whole of PR6141's
   first question, and it decides whether 7 or 8 is the smallest such
   characteristic. *First step:* let exactly one index in `4..22` fail and
   test one replacement pair. *Blocked by:* the induction uses every index,
   and no replacement inequality is proved here.
2. Can the frozen-14 step be turned into a human proof of the `c = 5` and
   `c = 6` exclusions? *Why:* PR6141's exclusions are solver verdicts.
   *First step:* repeat the centre classification on `s + t = kc + 3`.
   *Blocked by:* those characteristics have fewer than 20 middle slots, so
   off-diagonal pairs have to be bounded separately.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR4231, PR4248, PR6107), with the Ross Richardson PR934/PR943 lineage.
JosieElliston's PR6141 leaves `c = 7` open and records the slot count.
Nick Petalas's handoff on 2026-11-03
([discussion comment 19384981](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19384981))
isolates the diagonal equality case and the Johnson-path formulation this
proof replaces. zxv's PR6057 and JosieElliston's PR6061 supply the `c ≥ 8`
words, which have spare diagonal slots and are outside this obstruction.
queelius's open PR6216 is a `c = 5` certificate, a different question.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
