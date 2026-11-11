# The characteristic-5 adjacent centre on `s + t = 13` freezes no coordinate

**Classification. No new κ.** In the unchanged unsigned dirty connector, the
only adjacent pair on the sum `σ = 13` is `(6, 7)`. Every legal value of
`q_6 + q_7` is a weight-3 mask with coordinates in `{0, 1, 6}`. The only
immovable value in the allowed set is `10`, so this centre freezes no
coordinate. It therefore does not freeze a coordinate that meets a positive
share of the twenty weight-3 masks.

The selected conditional κ stays `781451/250000000`. This note does not rerun
a SAT solver, does not touch the DRAT certificate in open PR #6216, and does
not replace the sum-33 chain argument in open PR #7038.

## Definitions

The interface is the depth-two interface of PR #4231 and PR #4248, as used by
PR #6141 and PR #7038. A floor word of length 30 calls each of six sources
exactly five times. Write `q_t` for the count of the first `t` letters, so
`q_0 = 0` and `q_30 = (5, 5, 5, 5, 5, 5)`. Each coordinate of a prefix lies in
`{0, ..., 5}`.

A pair `(s, t)` with `0 ≤ s ≤ t ≤ 29` is **legal** when every coordinate of
`q_s + q_t` lies in

```text
A = {0, 1, 5, 6, 10}.
```

The mask bit of a value in `A` is `1` for `{1, 6}` and `0` for `{0, 5, 10}`.
The coordinate sum of a legal pair is `s + t`, and its mask weight `w`
satisfies `s + t ≡ w (mod 5)`.

A value `v ∈ A` is **immovable** when neither `v - 1` nor `v + 1` lies in `A`.
A coordinate of a legal sum is **frozen** when its value is immovable. This is
the meaning of the frozen coordinate `10` in PR #7038. The move table on `A` is

| move | values |
|---|---|
| `+1` stays in `A` | `0 → 1`, `5 → 6` |
| `-1` stays in `A` | `1 → 0`, `6 → 5` |
| immovable | `10` only |

There are `C(6, 3) = 20` weight-3 masks. Coordinate `j` **meets** a mask `m`
when `m_j = 1`. Each coordinate meets `C(5, 2) = 10` of the twenty masks, a
share of `1/2`.

The pair `(s, s + 1)` is the **adjacent centre** on the odd sum `2s + 1`.
On `σ = 13` that pair is `(6, 7)`, and it is the only pair of indices on this
sum that differ by 1. Sum `28` is even, so it has no such pair. The repeated
index `(14, 14)` is a different centre and is not classified here.

## Proved statement

**Theorem.** Every legal adjacent centre on `s + t = 13` has centre letter
`w` satisfying `q_6[w] = 0`, exactly two other coordinates equal to `3`, and
the remaining three coordinates equal to `0`. The centre sum is `1` at `w`,
`6` at the two sources counted three times, and `0` elsewhere. There are
`6 · C(5, 2) = 60` such count vectors. Every one is a weight-3 mask, every
one is the prefix of a floor word, and none has a coordinate equal to `10`.

In particular the adjacent centre freezes no coordinate. Since every
coordinate meets ten of the twenty weight-3 masks, the centre does not freeze
a coordinate that meets a positive share of those masks.

The type split is the case analysis below. The checker exhausts every vector
in `{0, ..., 5}^6` of sum `6` and every centre letter with a remaining call.
That enumeration is an exhaustive finite census of a finite domain. It checks
the case split. It is not a heuristic search and not a solver verdict.

## Case split

Let `r = q_6` and let `w = w_6`, so `q_7 = r + e_w`, `∑ r_j = 6`, and
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
`n_0 + n_3 + n_5 = 5`.

**Centre count `0`.** The count equation is `3 n_3 + 5 n_5 = 6`.

| `n_5` | equation | solution |
|---:|---|---|
| 0 | `3 n_3 = 6` | `n_3 = 2`, so `n_0 = 3` |
| 1 | `3 n_3 = 1` | not an integer solution |
| `≥ 2` | at least `10` | above `6` |

The only solution has mask weight `n_3 + 1 = 3`. Its values are one `1`, two
`6`s and three `0`s. It contains no `10`.

**Centre count `2`.** The centre contributes `2`, so
`3 n_3 + 5 n_5 = 4`. The case `n_5 = 0` gives `3 n_3 = 4`, which is not an
integer solution. The case `n_5 ≥ 1` is at least `5`, which is above `4`.
This case is empty.

These rows are the whole legal centre. The sixty realizations come from
choosing the centre coordinate in `6` ways and the two coordinates equal to
`3` in `C(5, 2) = 10` ways.

Each of those sixty vectors extends to a floor word. After the centre letter,
`q_7` still has coordinates in `{0, 1, 3}` and the residual quotas `5 - q_7[j]`
sum to `23`, which is the number of letters left. The checker builds one such
word for every vector and recomputes the centre sum.

## The one-step neighborhood is not a freeze

The diagonal step on this sum is

```text
S(s - 1) = S(s) - e_{w_{s-1}} + e_{w_{13-s}},
```

where `S(s) = q_s + q_{13-s}`. At the adjacent centre, `S(6) = q_6 + q_7`.
A subtraction letter is realizable only when it occurs in `q_6`. On the legal
shape those letters are the two sources of count `3`. Every one of the six
possible added letters keeps `q_8` inside `{0, ..., 5}`, because `q_7` is
coordinatewise at most `3`.

That is `60 · 2 · 6 = 720` realizable steps. Exactly eight per centre are
legal:

- the two steps that add the same triple source they subtract, which leave
  the sum unchanged;
- the six steps that subtract a triple source and add a source of count `0`,
  sending `6 → 5` and `0 → 1`.

All `480` legal steps keep the centre coordinate equal to `1`. The `360`
steps of the second kind show that a coordinate equal to `6`, and a
coordinate equal to `0`, can both move inside `A`. This census is exhaustive
for the one-step neighborhood of every legal adjacent centre.

The same arithmetic explains the centre coordinate without listing the steps.
Its value is `1`. The only in-`A` neighbor of `1` is `0`, and reaching `0`
requires subtracting the centre letter. That letter does not occur in `q_6`,
so the subtraction is not realizable. Adding the centre letter sends `1` to
`2`, which is outside `A`. A legal step therefore leaves the coordinate at
`1`. The value `1` itself is movable inside `A`; what is unavailable is the
letter that would move it.

## Invariance along a legal diagonal

**Lemma.** Suppose `S(6)` is a legal adjacent centre with centre letter `w`,
and suppose `S(s)` is legal for every `s = 0, ..., 6`. Then `S(s)_w = 1` for
every such `s`.

The classification gives `S(6)_w = 1`. Proceed downward. The step from `s` to
`s - 1`, for `s = 6, ..., 1`, subtracts `w_{s-1}`. The index `s - 1` lies in
`{0, ..., 5}`, and `q_6[w] = 0`, so the subtracted letter is not `w`. Once the
coordinate equals `1`, adding `w` would replace `1` by `2`, which is outside
`A`. A legal image therefore leaves the coordinate equal to `1`, and the next
step starts from that same value. The coordinate stays `1` at every slot,
including `S(0) = q_13`.

This hypothesis is realizable. The floor word

```text
111222022311400003333444455555
```

has centre letter `0` and the seven sums

| `s` | partner | `q_s + q_{13-s}` | mask |
|---:|---:|---|---|
| 6 | 7 | `(1, 6, 6, 0, 0, 0)` | `(1, 1, 1, 0, 0, 0)` |
| 5 | 8 | `(1, 6, 6, 0, 0, 0)` | `(1, 1, 1, 0, 0, 0)` |
| 4 | 9 | `(1, 6, 6, 0, 0, 0)` | `(1, 1, 1, 0, 0, 0)` |
| 3 | 10 | `(1, 6, 5, 1, 0, 0)` | `(1, 1, 0, 1, 0, 0)` |
| 2 | 11 | `(1, 6, 5, 1, 0, 0)` | `(1, 1, 0, 1, 0, 0)` |
| 1 | 12 | `(1, 6, 5, 1, 0, 0)` | `(1, 1, 0, 1, 0, 0)` |
| 0 | 13 | `(1, 5, 5, 1, 1, 0)` | `(1, 0, 0, 1, 1, 0)` |

Every entry lies in `A`, every mask has weight `3`, and coordinate `0` stays
equal to `1`. The three distinct masks all meet coordinate `0`. That
coordinate meets ten of the twenty weight-3 masks. The lemma fixes it on this
diagonal only. Masks may still be realized on another sum, and this word does
not realize the other seven masks that also have a `1` in coordinate `0`.

The invariance is not the freeze in the theorem. It uses the missing letter
in the prefix. It does not make `1` immovable, and it does not force a `5`
into `q_4`. A coordinate equal to `1` splits as `0 + 1` or `1 + 0`, and a
length-`4` count can hold either part.

The other coordinates are not invariant. The floor word

```text
111222030000112233334444455555
```

has the same legal centre `(1, 6, 6, 0, 0, 0)` and a legal image

```text
S(5) = (1, 6, 5, 1, 0, 0).
```

Coordinate `2` moves from `6` to `5`, and coordinate `3` moves from `0` to
`1`. Replacing the added letter `3` by the centre letter `0` produces a `2`,
which leaves `A`.

## What remains outside this pair

The published floor word of PR #7038,

```text
000001231234512345123451234545
```

has adjacent sum `(10, 2, 1, 0, 0, 0)`, which is illegal, and realizes the
weight-3 mask `(10, 1, 1, 1, 0, 0)` at the non-adjacent pair `(5, 8)`. A
weight-3 mask on sum `13` does not make the adjacent centre legal. A `10` can
occur on this sum, on a pair this note does not classify. On a legal pair the
value `10` is a mask bit `0`, so an immovable coordinate is a `0`-bit of the
mask that contains it.

PR #7038 proves that every legal centre on `s + t = 33` freezes a `10`, and
that the chain hypothesis (H) on that one diagonal is empty. This note does
not rerun that argument. Question 1 of that PR, whether every depth-two floor
word satisfies (H), is untouched. The characteristic-6 centre and the
characteristic-7 diagonal are untouched. Open PR #6216 is untouched.

No supplier, consumer, or selected frontier changes. The live selected record
at the base commit is κ `= 781451/250000000 = 0.003125804`. The priority note
on this same commit still quotes the older selected figure from PR #5599;
this package follows the selected record.

## Evidence class

1. **Proof.** The case split enumerates every nonnegative integer solution of
   `n_0 + n_3 + n_5 = 5` against the two count equations. One solution
   survives. The move table on the five-element set `A` shows that `10` is
   the only immovable value, and the surviving solution does not use it.
2. **Exhaustive finite census.** Every sum-`6` vector in `{0, ..., 5}^6`,
   every legal centre letter, and all `720` realizable one-step letter pairs
   were enumerated. The counts agree with the proof: `60` centres, `0`
   coordinates equal to `10`, `480` legal steps, all of them preserving the
   centre coordinate.
3. **Witnesses.** Two explicit floor words realize the legal centre. One
   keeps all seven diagonal slots legal. The other moves a `6` in one legal
   step. The published word shows an illegal adjacent centre beside a legal
   pair that contains a `10`. These words are witnesses. They are not a
   census of floor words, and a witness is not an unrestricted exclusion.

A classification of this one pair is not an unrestricted characteristic-5
exclusion, not a proof that no depth-two word exists, and not a change to κ.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/c5-sum13-adjacent-centre/verify.py
python3.12 -I -O -W error -B research/c5-sum13-adjacent-centre/verify.py
python3.12 -B scripts/research_package.py --package research/c5-sum13-adjacent-centre --check-only
```

The marker is

```text
PASS_C5_SUM13_ADJACENT_CENTRE centres=60 weight3=60 frozen10=0 immovable=[10] mask_bit10=0 share=10/20 adjacent_pair=(6,7) sum28_adjacent_pairs=0 legal_steps=480 moving_steps=360 diagonal_slots=7 centre_bit=1 published_adjacent=illegal controls=6
```

The six controls are the near-miss centre `(2, 2, 2, 0, 0, 0)`, the pair
geometry on sums `13` and `28`, the fully legal diagonal word, the one-step
word that moves a `6`, the centre-letter increase that leaves `A`, and the
published word above. No Lean, Docker, or historical suite was run.

Overlap was checked with `scripts/find_overlap.py` on 2026-11-10 at base
`17469fff78c22941280f04d39dc5a1faee09c840` (339 open PRs, complete pagination;
7013 discussion records, complete pagination; local note inventory complete,
10178 head records). The query matches open PR #7038, which asks this
question and does not answer it, plus the characteristic-6 and
characteristic-7 centre notes and unrelated centre-path discussions. No match
classifies `(6, 7)`.

## Open next questions

1. Does the adjacent centre on one of `σ ∈ {3, 23, 43, 53}` contain a
   coordinate equal to `10`?
   *Why:* those are the other adjacent sums congruent to `3` modulo `5`.
   A `10` there would be the immovable freeze already proved for sum `33`,
   on a diagonal the sum-33 walk does not see.
   *First step:* repeat the count equation at `s = (σ - 1) / 2` for one named
   sum, at characteristic `5` only.
   *Blocked by:* each adjacent sum has a different prefix total, so the
   sum-`13` row does not decide it.
2. Which legal values can the repeated centre `2 q_14` take on `s + t = 28`?
   *Why:* sum `28` is the other sum named beside `13`, and it has fifteen
   pairs, none of them adjacent. The doubled prefix has no centre letter, so
   it can still contain a `10`.
   *First step:* enumerate `r ∈ {0, ..., 5}^6` with `∑ r_j = 14` and
   `2 r ∈ A^6`.
   *Blocked by:* there is no centre-letter equation on a repeated index. The
   split used here does not apply.
3. How many distinct weight-3 masks can one fully legal sum-`13` diagonal
   realize under the centre-bit lemma?
   *Why:* the lemma leaves at most the ten masks that meet the centre
   letter, and the explicit word realizes three. A sharp count would say
   whether this diagonal alone can hold a positive share of the twenty masks.
   *First step:* classify one non-adjacent pair on sum `13`, for example
   `(5, 8)`, at characteristic `5` only.
   *Blocked by:* the two prefixes differ by more than one letter, so the
   adjacent-centre equation does not determine that pair.

## Credit

The depth-two interface is Nick Petalas's (PR #4231, PR #4248), with the Ross
Richardson PR #934 / PR #943 lineage. PR #6107 supplies the weight identity.
JosieElliston's PR #6141 is the solver exclusion at characteristics 5 and 6.
queelius's open PR #6216 is the characteristic-5 DRAT certificate; it is not
replayed here. The sum-33 centre freeze, the published witness word, and the
question answered here are open PR #7038, head
`3240f7d58d608a97449d4c07f04e8995b9761c15`, from the same account. The
characteristic-7 chain is discussion comment 19493159. The characteristic-6
centre classification is separate and is not used.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
