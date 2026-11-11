# The characteristic-5 adjacent centre on `s + t = 43` contains a coordinate 10

**Chosen sum, written down before the argument: `σ = 43`.** Classification.
No new κ. In the unchanged unsigned dirty connector, the adjacent centre is
the pair `(21, 22)`. Every legal value of `q_21 + q_22` is a weight-3 mask
with either two or three coordinates equal to `10`. The value `10` is the
only immovable value in `A`, so each of those coordinates is frozen. Both
shapes occur, sixty times each, and each extends to a floor word.

The selected conditional κ stays `363005817/100000000000`. This note does not
rerun a SAT solver, does not touch the merged DRAT certificate in PR #6216,
and does not replace the sum-33 chain argument in open PR #7038 or the sum-13
classification in open PR #7044. The sums `σ ∈ {3, 23, 53}` are not read.

## Definitions

The interface is the depth-two interface of PR #4231 and PR #4248, as used by
PR #6141, PR #7038 and PR #7044. A floor word of length 30 calls each of six
sources exactly five times. Write `q_t` for the count of the first `t`
letters, so `q_0 = 0` and `q_30 = (5, 5, 5, 5, 5, 5)`. Each coordinate of a
prefix lies in `{0, ..., 5}`. Letters are `w_0, ..., w_29`, and
`q_{t+1} = q_t + e_{w_t}`.

A pair `(s, t)` with `0 ≤ s ≤ t ≤ 29` is **legal** when every coordinate of
`q_s + q_t` lies in

```text
A = {0, 1, 5, 6, 10}.
```

The mask bit of a value in `A` is `1` for `{1, 6}` and `0` for `{0, 5, 10}`.
The coordinate sum of a legal pair is `s + t`, and its mask weight `w`
satisfies `s + t ≡ w (mod 5)` (PR #6107). Here `43 ≡ 3 (mod 5)`, so a legal
pair on this sum has weight `3`.

A value `v ∈ A` is **immovable** when neither `v - 1` nor `v + 1` lies in
`A`. A coordinate of a legal sum is **frozen** when its value is immovable.
The move table on `A` is

| move | values |
|---|---|
| `+1` stays in `A` | `0 → 1`, `5 → 6` |
| `-1` stays in `A` | `1 → 0`, `6 → 5` |
| immovable | `10` only |

The pair `(s, s + 1)` is the **adjacent centre** on the odd sum `2s + 1`.
On `σ = 43` that pair is `(21, 22)`, and it is the only pair of indices on
this sum that differ by 1. The eight slots are `(14, 29)` through `(21, 22)`.

## Proved statement

**Theorem.** Every legal adjacent centre on `s + t = 43` has centre letter
`w` of count `0` or `2` in `q_21`, and at least two other coordinates equal
to `5`. The centre sum is `10` on each of those coordinates. There are two
shapes:

| `q_21[w]` | other counts | centre sum, up to permutation | realizations |
|---:|---|---|---:|
| 0 | two `3`s and three `5`s | one `1`, two `6`s, three `10`s | `6 · C(5, 3) = 60` |
| 2 | three `3`s and two `5`s | one `5`, three `6`s, two `10`s | `6 · C(5, 2) = 60` |

Every one of the `120` vectors is a weight-3 mask, every one is the prefix of
a floor word, and every one has a coordinate equal to `10`. The minimum is
two and the maximum is three. The `10` is a mask bit `0`. It never sits on
the centre letter: that letter contributes `1` or `5`.

The type split is the case analysis below. The checker exhausts every vector
in `{0, ..., 5}^6` and every centre letter with a remaining call. The product
has `6^6 = 46656` tuples, and the sum filter keeps the prefixes of length
`21`. That enumeration is an exhaustive finite census of a finite domain. It
checks the case split. It is not a heuristic search and not a solver verdict.

## Case split

Let `r = q_21` and let `w = w_21`, so `q_22 = r + e_w`, `∑ r_j = 21`, and
`r_w ≤ 4`. The centre sum is `2r + e_w`.

A non-centre coordinate is legal only for `r_j ∈ {0, 3, 5}`:

| `r_j` | `2 r_j` | in `A` |
|---:|---:|---|
| 0 | 0 | yes, mask bit 0 |
| 1 | 2 | no |
| 2 | 4 | no |
| 3 | 6 | yes, mask bit 1 |
| 4 | 8 | no |
| 5 | 10 | yes, mask bit 0 |

The centre letter is legal only for `r_w ∈ {0, 2}`:

| `r_w` | `2 r_w + 1` | in `A` |
|---:|---:|---|
| 0 | 1 | yes, mask bit 1 |
| 1 | 3 | no |
| 2 | 5 | yes, mask bit 0 |
| 3 | 7 | no |
| 4 | 9 | no |

Let `n_0, n_3, n_5` count the five non-centre coordinates, so
`n_0 + n_3 + n_5 = 5` and every variable is a nonnegative integer at most `5`.

**Centre count `0`.** The count equation is `3 n_3 + 5 n_5 = 21`.

| `n_5` | remainder | solution |
|---:|---|---|
| 0 | `3 n_3 = 21` | `n_3 = 7`, above `5` |
| 1 | `3 n_3 = 16` | not divisible by `3` |
| 2 | `3 n_3 = 11` | not divisible by `3` |
| 3 | `3 n_3 = 6` | `n_3 = 2`, so `n_0 = 0` |
| 4 | `3 n_3 = 1` | not divisible by `3` |
| 5 | `3 n_3 = -4` | negative |

The only solution is `(n_0, n_3, n_5) = (0, 2, 3)`. Its centre sum has three
coordinates equal to `10`. Mask weight `n_3 + 1 = 3`.

**Centre count `2`.** The centre contributes `2`, so
`3 n_3 + 5 n_5 = 19`.

| `n_5` | remainder | solution |
|---:|---|---|
| 0 | `3 n_3 = 19` | not divisible by `3` |
| 1 | `3 n_3 = 14` | not divisible by `3` |
| 2 | `3 n_3 = 9` | `n_3 = 3`, so `n_0 = 0` |
| 3 | `3 n_3 = 4` | not divisible by `3` |
| `≥ 4` | at least `20` | above `19` |

The only solution is `(n_0, n_3, n_5) = (0, 3, 2)`. Its centre sum has two
coordinates equal to `10`. Mask weight `n_3 = 3`.

These two rows are the whole legal centre. Both have `n_5 ≥ 2`, so both
contain a coordinate equal to `10`. There is no legal centre of another
weight, and there is no legal centre with `n_5 = 0` or `n_5 = 1`.

Each of the `120` vectors extends to a floor word. Place the length-`21`
prefix in any order that realizes `r`, then the centre letter, then any order
of the residual quotas `5 - q_22[j]`. Those residuals are nonnegative because
every coordinate of `r` is at most `5` and `r_w ≤ 2`, so `q_22` is at most
`5` coordinatewise. They sum to `30 - 22 = 8`.

## One legal step keeps every coordinate 10

On this diagonal the prefixes obey

```text
S(s - 1) = S(s) - e_{w_{s-1}} + e_{w_{43-s}},
```

where `S(s) = q_s + q_{43-s}`. At the adjacent centre,
`S(20) = S(21) - e_{w_20} + e_{w_22}`.

A subtraction of source `sub` is realizable for a count vector `r` when
`r_sub ≥ 1`: the last letter of the length-`21` prefix can be that source.
An addition of source `add` keeps the later prefix inside `{0, ..., 5}` when
`q_22[add] ≤ 4`. If `sub = add`, the image equals `S(21)`. If `sub ≠ add`,
one coordinate decreases by `1` and another increases by `1`.

**Stationary steps.** The image equals the centre sum, which is legal. The
sources that occur in `r` and still have room in `q_22` are:

- centre count `0`: the two coordinates equal to `3`. The three fives are
  already at quota `5`, and the centre source is absent from `r`.
- centre count `2`: the centre source and the three coordinates equal to `3`.
  The two fives are at quota `5`.

That is two stationary steps on the first shape and four on the second.

**Moving steps.** The decreased value must lie in `{1, 6}` and the increased
value must lie in `{0, 5}`.

- Centre count `0` uses the values `{1, 6, 10}` only. The unique `1` sits on
  `w`, and `r_w = 0`, so that coordinate cannot be decreased. No coordinate
  equals `0` or `5`, so none can be increased. There is no legal moving step.
- Centre count `2` uses the values `{5, 6, 10}`. The only decreasable value
  is `6`, on a source of count `3`. The only increasable value is `5`, on
  `w`. All three choices are feasible: the triple has count `3`, and
  `q_22[w] = 3 ≤ 4`. The image replaces one `6` by `5` and the centre `5` by
  `6`. Both coordinates equal to `10` stay equal to `10`. Weight stays `3`,
  because a `1`-bit and a `0`-bit trade places.

These rows are the whole legal neighborhood: `60 · 2 + 60 · 4 = 360`
stationary images and `60 · 3 = 180` moving images, `540` in all. Every legal
image keeps the set of coordinates equal to `10`. The same conclusion is the
move table: `9` and `11` lie outside `A`, so a legal step cannot be the step
that changes a `10`.

The checker builds one floor word for every feasible letter pair and recounts
the legal images. That is an exhaustive finite census of the one-step
neighborhood of every legal adjacent centre.

## What a fully legal diagonal would carry

Write `(H43)` for the hypothesis that `S(s)` is legal for every
`s = 14, ..., 21`. This note does not decide whether `(H43)` is empty.

**Lemma.** Assume `(H43)`. Then at least two coordinates equal `10` at every
slot `S(s)`, `s = 14, ..., 21`, and each of those sources equals `5` in
`q_14` and in `q_29`.

The classification gives the coordinates at `S(21)`. A step whose two
endpoint vectors both lie in `A^6` preserves every coordinate equal to `10`,
because that coordinate cannot be the one that moves. Seven such steps reach
`S(14)`. The only way to write `10` as a sum of two integers in `{0, ..., 5}`
is `5 + 5`.

The earliest prefix therefore has length `14`. A length-`14` vector in
`{0, ..., 5}^6` can contain a `5`; one example is `(5, 5, 4, 0, 0, 0)`. That
example is a capacity witness only. It is not a legal slot of a diagonal, and
it is not a floor word. The numerical stop used for `s + t = 33`, where the
walk ended at a prefix of length `4`, does not apply to this sum. Emptiness
of `(H43)` is open.

## Witnesses

The floor word

```text
112223333344444555551010000122
```

has centre letter `0` and `q_21 = (0, 3, 3, 5, 5, 5)`. Its centre sum is
`(1, 6, 6, 10, 10, 10)`. The letters `w_20 = w_22 = 1` are a stationary step,
and `S(20)` equals the same vector. All three coordinates equal to `10` stay.

The floor word

```text
001122233344444555551000112233
```

has centre letter `0` and `q_21 = (2, 3, 3, 3, 5, 5)`. Its centre sum is
`(5, 6, 6, 6, 10, 10)`. The letters `w_20 = 1` and `w_22 = 0` are a moving
step, and

```text
S(20) = (6, 5, 6, 6, 10, 10).
```

Coordinate `1` moves from `6` to `5`, the centre coordinate moves from `5` to
`6`, and coordinates `4` and `5` stay equal to `10`.

These two words are witnesses. They are not a census of floor words, and a
witness is not an unrestricted exclusion. A sum-`21` prefix can still leave
`A`. The count vector `(5, 5, 5, 5, 1, 0)` with centre source `5` has centre sum `(10, 10, 10, 10, 2, 1)`.

## Scope

The theorem is the adjacent centre on the single named sum `σ = 43`. It is
the immovable `10` on that centre. It is not a proof that `(H43)` holds, not
a proof that `(H43)` is empty, and not a proof that every floor word has a
legal pair `(21, 22)`.

PR #7038 proves that every legal centre on `s + t = 33` freezes a `10`, and
that the chain hypothesis on that diagonal is empty. This note does not rerun
that walk. PR #7044 proves that the adjacent centre on `s + t = 13` freezes
no coordinate. This note does not rerun that classification. Questions 2 and
3 of PR #7044, the legal values of `2 q_14` and the number of weight-3 masks
on a fully legal sum-13 diagonal, are untouched. The characteristic-6 centre
and the characteristic-7 diagonal are untouched. PR #6216 is untouched.

No supplier, consumer, or selected frontier changes. The live selected record
at the base commit is κ `= 363005817/100000000000 = 0.00363005817`. The
priority note on this same commit still quotes the older selected figure from
PR #5599; this package follows the selected record.

## Evidence class

1. **Proof.** The case split enumerates every nonnegative integer solution of
   `n_0 + n_3 + n_5 = 5` against the two count equations at prefix total `21`.
   Two solutions survive, and both have `n_5 ≥ 2`. The move table on the
   five-element set `A` shows that `10` is immovable. The one-step case split
   lists every legal image and shows that each image keeps those
   coordinates. The conditional lemma, that a fully legal diagonal would
   carry the same `10`s down to `q_14`, is the same immovability applied
   seven times, plus the unique split `5 + 5`.
2. **Exhaustive finite census.** Every vector in `{0, ..., 5}^6` was visited
   (`46656` tuples). The `120` legal centres of sum `21` agree with the proof:
   `60 + 60`, weights `{3: 120}`, `300` coordinates equal to `10`, minimum
   `2`, maximum `3`. Every feasible one-step letter pair was realized by a
   floor word: `540` legal images, `360` stationary and `180` moving, none of
   them moving a `10`.
3. **Witnesses.** Two explicit floor words realize the two shapes. One keeps
   three coordinates equal to `10` under a stationary step. The other keeps
   two under a moving step. The length-`14` vector `(5, 5, 4, 0, 0, 0)` shows
   that a prefix of that length can contain a `5`. These are witnesses. A
   witness is not a census of floor words and not an unrestricted exclusion.

A classification of this one pair is not an unrestricted characteristic-5
exclusion, not a proof that no depth-two word exists, and not a change to κ.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/c5-sum43-adjacent-ten/verify.py
python3.12 -I -O -W error -B research/c5-sum43-adjacent-ten/verify.py
python3.12 -B scripts/research_package.py --package research/c5-sum43-adjacent-ten --check-only
```

The marker is

```text
PASS_C5_SUM43_ADJACENT_TEN sigma=43 centre=(21,22) centres=120 shape0=60 shape2=60 frozen10=300 min10=2 max10=3 weight3=120 steps=540 stationary=360 moving=180 slots=8 earliest_prefix=14 capacity_has_5=yes controls=6
```

The six controls are the near-miss centre `(5, 5, 5, 5, 1, 0)`, the eight
slots and the unique adjacent pair `(21, 22)`, the length-`14` capacity
example, the shape-0 word, the shape-2 word, and the count-feasible
subtraction of a `10` that leaves `A` at `9`. No Lean, Docker, or historical
suite was run.

Overlap was checked on 2026-11-11 at base
`e54523517d0f03e58352e647c403a5af3e525a57`. Upstream `main` was fetched at
session start and was that commit. `scripts/find_overlap.py --offline` searched
the local note inventory (complete head inventory, 10178 head records) and
matched no note that classifies `(21, 22)`; the remote snapshot was absent, so
that command is not a PR or discussion search. A full title list of the 500
open upstream PRs, paginated to an empty page, contains this adjacent-centre
question only as open PR #7044, which asks it and does not answer `σ = 43`.
The other `c = 5` centre titles on that list are PR #7038 and PR #7058. PR
#7058 leaves the adjacent-centre question untouched. An earlier body search
for `adjacent centre` returned those three PRs and then the search API
rate-limited, so this is not a second full-text refresh. The last 15 comments
on discussion #1166 at session time do not mention this sum. No fork branch
on the session-start `cursor/*` list classifies `σ = 43`.

## Open next questions

1. Does any floor word satisfy `(H43)`, that `S(s)` is legal for every
   `s = 14, ..., 21`?
   *Why:* the lemma says any such word carries at least two fives in `q_14`.
   The sum-33 numerical stop does not apply, and this centre census stops at
   one step.
   *First step:* from a shape-2 centre, classify `S(19)` under the same
   characteristic-5 alphabet, using the moving image `S(20)` already listed.
   *Blocked by:* the prefixes `q_19` and `q_24` differ from the adjacent
   centre by more than one letter.
2. Does the adjacent centre on `σ = 23` contain a coordinate equal to `10`?
   *Why:* `23` is one of the three sums left from the list in PR #7044 after
   `σ = 43` is removed. The same immovable value would sit on a different
   diagonal.
   *First step:* the count equation at `s = 11`, characteristic `5` only.
   *Blocked by:* the prefix total `11` is not the prefix total `21` solved
   here.
3. Does the adjacent centre on `σ = 3` contain a coordinate equal to `10`?
   *Why:* `3` is another sum on the same PR #7044 list, with adjacent pair
   `(1, 2)`.
   *First step:* the count equation at `s = 1`.
   *Blocked by:* a prefix of length `1` is a different equation. This package
   does not evaluate it.
4. Does the adjacent centre on `σ = 53` contain a coordinate equal to `10`?
   *Why:* `53` is the last sum on that list, with adjacent pair `(26, 27)`.
   *First step:* the count equation at `s = 26`.
   *Blocked by:* a prefix of length `26` is a different equation. This
   package does not evaluate it.

## Credit

The depth-two interface is Nick Petalas's (PR #4231, PR #4248), with the Ross
Richardson PR #934 / PR #943 lineage. PR #6107 supplies the weight identity.
JosieElliston's PR #6141 is the solver exclusion at characteristics 5 and 6.
queelius's merged PR #6216 is the characteristic-5 DRAT certificate; it is not
replayed here. The sum-33 centre freeze is open PR #7038, head
`3240f7d58d608a97449d4c07f04e8995b9761c15`. The sum-13 adjacent centre, and
open question 1 answered here for the single named sum `σ = 43`, are open PR
#7044, head `53b56df645f591ea26da3c6f5b478dd88c50e1f8`, from the same account.
The characteristic-6 centre classification and the characteristic-7 diagonal
are separate and are not used.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Workflow feedback (optional)

Naming `σ = 43` before the case split kept the other three prefix totals out
of the census. The sum-13 row really does not decide them: the right-hand
side of the count equation is the prefix length. Link once:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1200
