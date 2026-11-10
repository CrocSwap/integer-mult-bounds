# The weight-3 shape at (0, 15) does not force a 12 at (18, 21)

**Scoped negative result. No new κ.** In the unchanged unsigned dirty
connector, the only weight-3 value of `q_15` is a permutation of
`(6,6,1,1,1,0)`. That shape meets none of the six separation-3 families
recorded in PR #7029. Its set of weight-3 extensions to `(18, 21)` is
empty, so it does not force a 12 onto that slot in the sense used for the
mask at `(0, 9)`. The selected conditional κ remains
`781451/250000000`.

## Interface, unchanged

A floor word on `k = 6` sources in characteristic `c = 6` has length 36 and
calls each source exactly six times. `q_t` counts the first `t` letters, so
`q_0 = 0`, `q_36 = (6,6,6,6,6,6)`, and each step adds one basis vector.
Counts stay in `{0,...,6}` and are componentwise nondecreasing. A pair
realizes a **weight-3 mask** when every coordinate of `q_s + q_t` lies in
`{0,1,6,7,12}` and exactly three coordinates lie in `{1,7}`. This is the
interface of PR #4231, PR #4248 and PR #6107, as used by PR #6141, PR #6955
and PR #7029.

The pair under test is `(0, 15)`. Its sum is `q_15`, the coordinate sum is
15, and the later index is 15, so the gap from that index to 18 is three
letters. Among the index pairs with `s + t = 15` and `s ≤ t`, this is the
pair whose gap is three. The pairs `(1, 14)` through `(7, 8)` have gaps 4
through 10 and are outside this package.

## The weight-3 sums at (0, 15)

Let `q` be a vector in `{0,...,6}^6` with coordinate sum 15. A weight-3 mask
uses only values in `{0,1,6,7,12}`. Intersecting with the prefix range leaves
`{0,1,6}`, and the only mask value in that set is 1. Exactly three
coordinates are therefore equal to 1. The other three coordinates lie in
`{0,6}` and sum to 12, so they are two 6s and one 0.

Thus every weight-3 value of `q_15` is a permutation of `(6,6,1,1,1,0)`.
There are `6!/(2! 3! 1!) = 60` such vectors. This is a complete case analysis
on a finite set of coordinate types.

The same arithmetic lists every weight-3 vector of coordinate sum 15 with
entries in `{0,1,6,7,12}`, whether or not it is a prefix. The sum 15 forces
carry `λ = 2`. One coordinate equal to 12 spends that carry, so the vector
is a permutation of `(12,1,1,1,0,0)`. With no 12, the carry is two
coordinates in `{6,7}`. Writing `b` for the number of 7s gives the three
shapes `(6,6,1,1,1,0)`, `(7,6,1,1,0,0)` and `(7,7,1,0,0,0)`, for `b = 0, 1, 2`.
The last two, and the shape with a 12, each have a coordinate greater than 6,
so none of them is a length-15 prefix.

The same list is the census of the finite domain. Inclusion-exclusion counts
the vectors in `{0,...,6}^6` of sum 15:

```text
C(20,5) - 6 C(13,5) + 15 C(6,5) = 15504 - 7722 + 90 = 7872.
```

`verify.py` visits all `7^6` tuples, finds those 7872 vectors, and finds that
exactly 60 of them are weight-3, all in the orbit above. The domain is
finite, the loop visits every element, and the count matches the closed form.
This is an exhaustive census of length-15 count vectors. It is not a census
of words.

## One shape against the six families

The shape tested here is `(6,6,1,1,1,0)`, which represents the whole orbit.
PR #7029 classifies every weight-3 pair at `(18, 21)`. This package does not
repeat that census. It uses the six families through the multisets of
`q_18` they allow. A coordinate equal to 12 in the separation-3 sum occurs
only on the row `(r, δ) = (6, 0)`, so the number of 12s is the number of
those rows.

| family | `q_18` up to permutation | coordinates equal to 12 |
|---|---|---:|
| T1 | `(3,3,3,3,3,3)` | 0 |
| T2 | `(6,3,3,3,3,0)` | 1 |
| T3 | `(6,3,3,3,3,0)` | 1 |
| T4 | `(6,6,3,3,0,0)` | 2 |
| T5 | `(6,6,3,3,0,0)` | 2 |
| T6 | `(6,6,6,0,0,0)` | 3 |

The dependency check re-solves the three recorded budget equations

```text
n_{0,1} + n_{3,1} = 3,
n_{0,0} + n_{3,0} + n_{6,0} = 3,
3 n_{3,0} + 3 n_{3,1} + 6 n_{6,0} = 18
```

on `{0,...,6}` and recovers these six rows and these four multisets. It does
not enumerate the 700 count pairs of PR #7029.

A three-letter bridge from `q_15` to `q_18` is a nonnegative integer vector
`ε` of coordinate sum 3 such that `q_18 = q_15 + ε` still has coordinates at
most 6. Every nonnegative vector of sum 3 has parts at most 3.

**Proposition.** No such `q_18`, for `q_15` a permutation of
`(6,6,1,1,1,0)`, lies in one of these four multisets.

**Proof.** The two coordinates equal to 6 stay equal to 6, because a prefix
coordinate is already at the cap. T1 has no coordinate equal to 6. T2 and
T3 have one. T4 and T5 have two, so those two coordinates of `q_18` are
exactly the two coordinates already equal to 6 in `q_15`: every other
coordinate of the multiset is at most 3. The remaining piece of `q_15` is
`(1,1,1,0)`, which would have to sit under `(3,3,0,0)`. A 1 cannot sit under
a 0, and two zeros are available for only one 0. T6 has three 6s. After the
two frozen 6s occupy two of those three positions, the remaining piece
`(1,1,1,0)` would have to sit under `(6,0,0,0)`. Three 1s cannot sit under
three 0s. That alignment is also out of budget on its own: raising a 1 to 6
costs five letters, and the gap supplies three.

The shape therefore meets none of the six families. In particular it does
not meet a family by carrying that family's 12, because it meets no family.

## Forcing, and the empty extension set

In PR #7029, the mask at `(0, 9)` **forces a 12** because its weight-3
extensions to `(18, 21)` form a nonempty set and every extension has a
coordinate equal to 12. The prefix there does not empty the slot.

**Theorem.** The shape `(6,6,1,1,1,0)` does not force a 12 at `(18, 21)`.
Its set of weight-3 extensions is empty.

The proposition gives this under the recorded family list. The checker also
proves emptiness directly, without using that list. A three-letter bridge is
a vector in `{0,1,2,3}^6` of coordinate sum 3 that respects the cap 6. Every
nonnegative vector of sum 3 automatically has parts at most 3, so this is
every count increment the gap can produce. Letter order does not change the
counts. For the representative prefix the first gap has

```text
C(3+4-1, 3) = 20
```

bridges: two coordinates are already 6 and accept no letter, and the other
four accept the whole sum of 3. Joining each of them to every legal bridge
from `q_18` to `q_21` produces 397 pairs. All 60 permutations produce
`60 · 397 = 23820` pairs. None of the 23820 sums `2 q_18 + δ` is weight-3.
The loops visit every pair. This is an exhaustive finite census of count
extensions of this shape, and it is a proof that the extension set is empty.
It is not a census of words, and a word would determine one of these count
triples, so no floor word realizes the shape at `(0, 15)` and a weight-3
mask at `(18, 21)` together.

The census admits bridges that use a coordinate step `(2, 2)` or `(2, 3)`.
Emptiness does not depend on the letter-budget exclusion of those rows.

The empty-set reading of "every extension has a 12" is not the price proved
for `(0, 9)`. This package does not report one. There is no realized slot
here on which a 12 is frozen, and there is nothing to carry down the
diagonal.

## What remains for a human c=6 proof

Write (H15) for "the pair `(0, 15)` is weight-3" and keep (H2) as in
PR #7029: every pair `(s, 39-s)` for `s = 4,...,18` is weight-3. (H2) at
`s = 18` requires a weight-3 sum at `(18, 21)`. The theorem says (H15) and
that one index cannot hold together, so (H15) and (H2) cannot hold together.
The earlier indices `s = 4,...,17` are not used. The obstruction is the
empty slot, not a 12 propagated to `s = 4`.

Depth two requires every nonzero mask on some pair `s + t ≡ 3 (mod 6)`. It
does not require (H15), and it does not require (H2). A floor word can miss
`(0, 15)`. The explicit separation-3 word

```text
333333444444555555012000001111122222
```

has `q_15 = (0,0,0,6,6,3)`, which is outside the shape, and has separation-3
sum `(1,1,1,12,12,12)`. The slot `(18, 21)` is nonempty for other prefixes.
The same prefix has 13 weight-3 extensions to `(18, 21)`, and all 13 carry a
12. That count is a failure control for the enumerator. It is not a price of
the named shape, and this package does not claim that the rest of the
diagonal is weight-3 for any word with that prefix.

The `(0, 9)` witness

```text
333333012000001111122222444444555555
```

has `q_9 = (1,1,1,6,0,0)` and separation-3 sum `(12,11,4,12,0,0)`. Its
`q_15 = (6,2,1,6,0,0)` is a different vector. The price of that mask is
PR #7029 and is not recomputed here.

PR #6141's CaDiCaL 1.9.5 and MapleChrono UNSAT verdicts remain the evidence
for the unrestricted six-source depth-two exclusion. This package does not
rerun them, does not emit a DRAT certificate, and does not treat that UNSAT
as a human proof. The multiset `(6,6,6,7,7,7)` along the diagonal is the
other open question of PR #7029 and is not tested here. Characteristic 5 is
not tested here. No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-sum15-pair015/verify.py
python3.12 -I -O -W error -B research/six-source-c6-sum15-pair015/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-sum15-pair015 --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C6_SUM15_PAIR015 vectors=7872 weight3=60 shape=(0, 1, 1, 1, 6, 6) families=6 family_hits=0 shape_trials=23820 shape_extensions=0 live_prefix_extensions=13 live_prefix_twelves=13 controls=19
```

Failures raise `SystemExit`. Optimized mode cannot silence them. No Lean,
Docker, or solver replay was run.

## Open next questions

1. Does one weight-3 shape at the pair `(1, 14)` force a 12 at `(18, 21)`
   on a nonempty extension set? *Why:* `(0, 15)` is the only total-15 pair
   whose gap to 18 is three letters, and its only shape empties the slot
   instead of pricing a 12. The `(0, 9)` mechanism is not reproduced on this
   gap. *First step:* list the weight-3 sums `q_1 + q_14` and test one shape
   against the same six `q_18` multisets, with a four-letter bridge.
   *Blocked by:* four letters are a different bridge budget. This package
   does not enumerate that gap.
2. Can the residue shape `(12,1,1,1,0,0)`, which is not a length-15 prefix,
   occur as `q_6 + q_9` and still force a coordinate 12 at `(18, 21)` on a
   nonempty extension set? *Why:* a coordinate 12 in a sum of total 15
   requires both indices to be at least 6, so `(6, 9)` and `(7, 8)` are the
   only candidate pairs, and a 12 already present in the sum is the other
   way a later slot could be forced. *First step:* list the weight-3 values
   of `q_6 + q_9` whose sorted shape is `(12,1,1,1,0,0)` and test one such
   value against the six families, with the nine-letter gap from 9 to 18.
   *Blocked by:* that gap is longer than three letters, and the six families
   do not transfer to it.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 records the c=6 solver verdict.
PR #6955 supplies the empty centre and the two explicit floor words used
here as controls. PR #7029 supplies the six separation-3 families, the
nonempty 12-price of the mask at `(0, 9)`, and the question answered here.
Those classifications are not re-proved. queelius's PR #6216 is the
characteristic-five certificate. zxv's PR #6057 and JosieElliston's
PR #6061 supply the `c ≥ 8` words.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
