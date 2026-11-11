# The weight-3 shape (0, 0, 1, 1, 6, 7) at (1, 14) forces a 12 at (18, 21)

**Scoped positive result. No new κ.** In the unchanged unsigned dirty
connector, the weight-3 values of `q_1 + q_14` are the permutations of
`(7, 6, 1, 1, 0, 0)` and of `(6, 6, 1, 1, 1, 0)`. The first shape meets the
shared `q_18` multiset of families T4 and T5, and no other multiset among
the six separation-3 families of PR #7029. Its set of weight-3 extensions
to `(18, 21)` is nonempty, and every extension has two coordinates equal
to 12. The selected conditional κ remains
`363005817/100000000000`.

## Interface, unchanged

A floor word on `k = 6` sources in characteristic `c = 6` has length 36 and
calls each source exactly six times. `q_t` counts the first `t` letters, so
`q_0 = 0`, `q_36 = (6,6,6,6,6,6)`, and each step adds one basis vector.
Counts stay in `{0,...,6}` and are componentwise nondecreasing. A pair
realizes a **weight-3 mask** when every coordinate of `q_s + q_t` lies in
`{0,1,6,7,12}` and exactly three coordinates lie in `{1,7}`. This is the
interface of PR #4231, PR #4248 and PR #6107, as used by PR #6141, PR #6955,
PR #7029 and PR #7043.

The pair under test is `(1, 14)`. The sum `q_1 + q_14` has coordinate sum
15. The later index is 14, so `q_18 - q_14` is four letters and
`q_21 - q_18` is three letters. PR #7043 settled the gap-three pair
`(0, 15)`. The four-letter budget is the difference.

## The weight-3 sums at (1, 14)

Let `q` be a vector in `{0,...,6}^6` with coordinate sum 14, and let `j` be
a coordinate with `q_j ≥ 1`. The first letter may be source `j`, and
`S = q + e_j` is a value of `q_1 + q_14`. The coordinate sum of `S` is 15.
A weight-3 mask of sum 15 has carry `λ = 2`, because the coordinate sum is
`3 + 6λ`.

**Lemma.** The weight-3 values of `S` are exactly the following pairs.

- Shape B, the shape tested below. `S` is a permutation of
  `(7,6,1,1,0,0)` and `q_j = 6`. Then `q` is a permutation of
  `(6,6,1,1,0,0)`, and `j` is one of the two coordinates equal to 6.
  There are 180 such pairs and 90 such prefixes.
- Shape A, listed and not extended. `S` is a permutation of
  `(6,6,1,1,1,0)` and `q_j = 5`. Then `q` is a permutation of
  `(6,5,1,1,1,0)`, with the 5 in position `j`. There are 120 such pairs.

**Proof.** A coordinate of `S` equals `q_i` for `i ≠ j` and equals
`q_j + 1` at `j`. Thus every coordinate except possibly `j` lies in
`{0,...,6}`, and `S_j` lies in `{2,...,7}`. A weight-3 coordinate lies in
`{0,1,6,7,12}`, so `S_j ∈ {6,7}` and no coordinate equals 12. In
particular the sum-15 residue `(12,1,1,1,0,0)` is not a value of
`q_1 + q_14`.

The carry `λ = 2` is then two coordinates in `{6,7}`. The coordinate `j`
is one of them.

If `S_j = 6`, then `q_j = 5`. This coordinate contributes carry and no
mask bit. The other carry coordinate `i ≠ j` has `S_i ≤ 6`, so `S_i = 6`.
The remaining four coordinates lie in `{0,1}` and supply all three mask
bits, so they are three 1s and one 0. The sorted shape is
`(0,1,1,1,6,6)`. Choosing `j`, then the other 6, then the three 1s gives
`6 · 5 · 4 = 120` pairs.

If `S_j = 7`, then `q_j = 6`. This coordinate contributes carry and one
mask bit. The other carry coordinate is a 6, and the remaining four
coordinates supply two mask bits, so they are two 1s and two 0s. The
sorted shape is `(0,0,1,1,6,7)`. Choosing `j`, then the other 6, then the
two 1s gives `6 · 5 · C(4,2) = 180` pairs.

These cases exhaust `S_j ∈ {6,7}`. ∎

The same list is the census of the finite domain. Inclusion-exclusion
counts the vectors in `{0,...,6}^6` of sum 14:

```text
C(19,5) - 6 C(12,5) + 15 C(5,5) = 11628 - 4752 + 15 = 6891.
```

For each fixed first-letter source, the legal prefixes are the sum-13
vectors whose distinguished coordinate is at most 5. There are
`5796 - 325 = 5471` of them, and `6 · 5471 = 32826` pairs. `verify.py`
visits every tuple in `{0,...,6}^6`, finds those 6891 vectors and 32826
pairs, and finds that the weight-3 pairs are exactly the two orbits above.
The domain is finite and the loop visits every element. This is an
exhaustive census of length-14 count pairs. It is not a census of words.

## One shape against the six families

The tested shape is `(7,6,1,1,0,0)`. Its prefix `q_14` is a permutation of
`(6,6,1,1,0,0)`. PR #7029 classifies every weight-3 pair at `(18, 21)`
into six families. This package does not repeat that census. It uses the
six families through the multisets of `q_18` they allow.

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

on `{0,...,6}` and recovers these six rows and these four multisets.

**Proposition.** For `q_14` a permutation of `(6,6,1,1,0,0)`, the only
reachable multiset among these four is `(6,6,3,3,0,0)`, the common
multiset of T4 and T5.

**Proof.** Two coordinates of `q_14` are already 6, so they remain 6 in
`q_18`. T1 has no coordinate equal to 6. T2 and T3 have one. T6 has three.
A third 6 would have to be raised from a coordinate in `{0,1}`, which costs
at least five letters, and the gap supplies four. T4 and T5 require the
remaining piece `(1,1,0,0)` to become `(3,3,0,0)`. A 1 cannot fall. Both
0s therefore stay 0, and each 1 receives two letters. That bridge has sum
4 and respects the cap. ∎

The two families are distinguished by the three-letter bridge, not by
`q_18`. On the representative `q_14 = (6,6,1,1,0,0)` the unique four-letter
bridge into this multiset is `(0,0,2,2,0,0)`. The T4 bridges are
`(0,0,1,1,1,0)` and `(0,0,1,1,0,1)`. The T5 bridges are `(0,0,0,1,1,1)`
and `(0,0,1,0,1,1)`. Their separation sums are permutations of
`(0,1,7,7,12,12)` and `(1,1,6,7,12,12)`. Both are weight 3, and both
contain a 12.

## Forcing, on a nonempty extension set

In PR #7029, a mask **forces a 12** when its weight-3 extensions to
`(18, 21)` form a nonempty set and every such extension has a coordinate
equal to 12. The same definition is used here.

**Theorem.** The shape `(7,6,1,1,0,0)` forces a 12 at `(18, 21)`. Every
count extension of its prefix has two coordinates equal to 12, and at least
one extension is weight 3.

**Proof.** A realization has `q_14` a permutation of `(6,6,1,1,0,0)`. Those
two sources are at the cap, so every later letter lands on one of the other
four sources. Both `q_18` and `q_21` remain 6 on the capped sources, and
the separation sum is 12 on both. This holds for every four-letter bridge
and every three-letter bridge. It does not use the weight-3 predicate.

The extension set is nonempty. The floor word

```text
000000123111112233234223344444555555
```

has `q_9 = (6,1,1,1,0,0)`, `q_14 = (6,6,1,1,0,0)`, and
`q_1 + q_14 = (7,6,1,1,0,0)`. Its separation-3 sum is
`(12,12,7,7,1,0)`, which is weight 3. The same word is also weight 3 at
`(0, 9)`. Thus the shape, the mask at `(0, 9)`, and a 12 at `(18, 21)`
occur together in one floor word. ∎

The word shows that the price is not an incompatibility with hypothesis
(H1) of PR #7029. The five letters from index 9 to index 14 are five calls
of source 1, taking `(6,1,1,1,0,0)` to `(6,6,1,1,0,0)`.

## The same 12 under hypothesis (H2)

Write `S(s) = q_s + q_{39-s}`, and keep (H2) as in PR #7029: every pair
`(s, 39-s)` for `s = 4,...,18` is weight-3. Write (H114) for the statement
that `q_1 + q_14` is a permutation of `(7,6,1,1,0,0)` with the 7 on the
first letter.

The adjacent sums satisfy

```text
S(s+1) = S(s) + e_{w_s} - e_{w_{38-s}},
```

because `q_{s+1} = q_s + e_{w_s}` and `q_{39-s} = q_{38-s} + e_{w_{38-s}}`.
If `S(s)` and `S(s+1)` are both weight-3 and `S(s+1)_j = 12`, the letter
pair cannot move coordinate `j`: the moved values would be 11 or 13, both
outside `{0,1,6,7,12}`. Coordinate `j` stays 12.

**Corollary.** No six-source characteristic-6 floor word satisfies (H114)
and (H2) together.

**Proof.** (H2) at `s = 18` makes `(18, 21)` weight-3. By the theorem, a
source `j` that equals 6 in `q_14` equals 12 in `S(18)`. The one-step
identity keeps coordinate `j` equal to 12 for `s = 17, 16, ..., 4`. At
`s = 4` the partner is 35, so `S(4) = q_4 + q_35`. Each coordinate of
`q_4` is at most 4, and each coordinate of `q_35` is at most 6, so each
coordinate of `S(4)` is at most 10. It cannot be 12. ∎

The witness attains the bound 10 on the capped source at `s = 4`:
`S(4) = (10,6,6,6,6,5)`. That vector is not weight-3, so the witness does
not satisfy (H2). The corollary is the incompatibility of the two
hypotheses. It is not an unrestricted depth-two exclusion.

## Exhaustive count of the extensions

The cap argument and the explicit word prove the theorem. The checker also
counts the finite set of bridges, without using the family list to decide
which sums are weight-3.

For the representative, two coordinates are already 6. The four letters are
supported on the other four coordinates, each with room at least 5, so the
part bound is the letter count 4. The number of first bridges is

```text
C(4+4-1, 4) = 35.
```

Joining each of them to every legal three-letter bridge produces 684 pairs.
All 684 separation sums are 12 on the two capped sources, and 4 of the 684
are weight-3. Those four are the T4 and T5 bridges named above. A second
enumerator, ranging over the same caps by a direct product, returns the
same 684 pairs and the same four hits.

The 90 permutations of `q_14` each have this count. The orbit has
`90 · 684 = 61560` bridge pairs and `90 · 4 = 360` weight-3 extensions.
Every one of the 61560 sums is 12 on the capped sources, so every weight-3
extension has a 12. The loops visit every pair. This is an exhaustive
finite census of count extensions of this shape. A floor word realizing
the shape determines one of these prefixes and one of these bridges, so
every such word has a 12 in `q_18 + q_21`. The census is not a census of
words.

Two prefixes outside the orbit keep the enumerator honest. The vector
`(0,0,1,4,4,5)` has 3208 bridge pairs and no weight-3 extension. The
vector `(2,2,2,2,3,3)` has 6220 bridge pairs and 20 weight-3 extensions,
all equal to a permutation of `(6,6,6,7,7,7)`, and none contains a 12.
One of them is the T1 bridge `q_18 = (3,3,3,3,3,3)` with
`δ = (1,1,1,0,0,0)`. The same two enumerators agree on both prefixes.

## What remains for a human c=6 proof

Depth two requires every nonzero mask on some pair `s + t ≡ 3 (mod 6)`.
It does not require (H114), and it does not require (H2). The corollary
excludes only the words that satisfy both. The witness is a floor word in
which (H114), the mask at `(0, 9)`, and a weight-3 sum at `(18, 21)` all
hold, while `S(4)` is outside the allowed set.

PR #6141's solver verdict remains the evidence for the unrestricted
six-source depth-two exclusion. This package does not rerun it and does
not emit a DRAT certificate. PR #7043's emptiness result for `(0, 15)` is
not recomputed. The other shape at `(1, 14)`, whose prefix is a permutation
of `(6,5,1,1,1,0)`, is counted and not extended. PR #7176 places both
`(0, 15)` and `(1, 14)` outside its endpoint-window census. The residue
shape `(12,1,1,1,0,0)` remains the second open question of PR #7043.
Characteristic 5 is not tested. No supplier, consumer, or selected frontier
changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-sum15-pair114/verify.py
python3.12 -I -O -W error -B research/six-source-c6-sum15-pair114/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-sum15-pair114 --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C6_SUM15_PAIR114 vectors=6891 pairs=32826 weight3_shape_b=180 weight3_shape_a=120 shape=(0, 0, 1, 1, 6, 7) q14=(0, 0, 1, 1, 6, 6) families=6 family_hits=2 shape_trials=61560 shape_extensions=360 shape_extension_twelves=360 all_extension_sums_with_twelve=61560 live_zero_hits=0 live_t1_hits=20 live_t1_twelves=0 controls=19
```

Failures raise `SystemExit`. Optimized mode cannot silence them. No Lean,
Docker, or solver replay was run.

## Open next questions

1. Does the other weight-3 shape at `(1, 14)`, the permutations of
   `(6,6,1,1,1,0)`, force a 12 at `(18, 21)` on a nonempty extension set?
   *Why:* its prefix is a permutation of `(6,5,1,1,1,0)`. Only one source
   is at the cap, so the double-12 argument used for `(7,6,1,1,0,0)` does
   not apply, and the four-letter bridge can raise the 5. *First step:*
   test `q_14 = (6,5,1,1,1,0)` against the same six `q_18` multisets.
   *Blocked by:* this package extends only `(7,6,1,1,0,0)`.
2. For the tested shape, can hypothesis (H2) be shortened below the full
   chain `s = 4,...,18`? *Why:* the corollary uses every intermediate
   index, while the witness fails (H2) at `s = 4` and still realizes a
   weight-3 sum at `(18, 21)`. A different bridge might be weight-3 at
   `s = 4` and fail at another index. *First step:* build one floor word
   for each of the other three `δ` bridges on
   `q_14 = (6,6,1,1,0,0)` and record the smallest `s` in `4,...,17` at
   which `S(s)` is not weight-3. *Blocked by:* those three words are not
   assembled here.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 records the c=6 solver verdict.
PR #6955 supplies the two explicit floor words used here as controls.
PR #7029 supplies the six separation-3 families, the nonempty 12-price of
the mask at `(0, 9)`, hypothesis (H2), and the one-step identity applied
in the corollary. PR #7043 settled the gap-three pair `(0, 15)` and asked
the question answered here. PR #7176 records that `(1, 14)` lies outside
its endpoint-window package. Those classifications are not re-proved.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
