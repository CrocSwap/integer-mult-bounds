# Separation-3 pairs on s+t=39, and the price of the (0,9) mask

**Scoped classification and a conditional exclusion. No new κ.** In the
unchanged unsigned dirty connector, the separation-3 slot `(18, 21)` on the
diagonal `s + t = 39` realizes a weight-3 mask in exactly six families. The
explicit mask at `(0, 9)` is the unique weight-3 shape of that pair. Every
weight-3 extension of that shape to `(18, 21)` carries a coordinate equal to
12, so no floor word can be weight-3 both at `(0, 9)` and at every diagonal
index `s = 4,...,18`. The unrestricted six-source depth-two exclusion at
characteristic 6 remains the solver verdict of PR6141.

The selected conditional κ remains `781451/250000000` in
`certificates/selected-result.json`.

## Interface, unchanged

A floor word on `k = 6` sources in characteristic `c = 6` has length 36 and
calls each source exactly six times. `q_t` counts the first `t` letters, so
`q_0 = 0`, `q_36 = (6,6,6,6,6,6)`, and each step adds one basis vector.
Counts stay in `{0,...,6}`, and `q_t` is componentwise at most `q_u` whenever
`t ≤ u`. The word has depth two when every nonzero binary mask is congruent
modulo 6 to `q_s + q_t` for some `0 ≤ s ≤ t ≤ 35`. This is the interface of
PR4231/PR4248, as used by PR6141 and by the centre classification in PR6955.
Boundary 36 is identified with 0 because `q_36 = 6·1 ≡ q_0`.

A pair realizes a **weight-3 mask** when every coordinate of `q_s + q_t`
lies in `{0,1,6,7,12}` and exactly three coordinates lie in `{1,7}`. Every
sum of two counts in `{0,...,6}` is an integer in `{0,...,12}`, and the
members of that range congruent to 0 or 1 modulo 6 are exactly
`{0,1,6,7,12}`. Write `λ` for the carry count of such a vector: a coordinate
in `{6,7}` contributes 1 and a coordinate equal to 12 contributes 2. The
coordinate sum is then `3 + 6λ`. PR6107's weight identity is this arithmetic,
specialized to `c = 6`.

The diagonal pairs with `s + t = 39` and `s ≤ t ≤ 35` are `(s, 39-s)` for
`s = 4,...,19`. Their coordinate sum is 39, so a weight-3 realization has
`λ = 6`. PR6955 shows that the centre `s = 19` has no residue-legal sum.
This package does not repeat that census. The separation-3 slot is the
remaining index pair with `t - s = 3`, namely `(18, 21)`.

## Local types and the letter budget

Let `r = q_18` and let `δ` be the three letters in positions 18, 19 and 20,
read as a count vector. Then `∑ δ_j = 3`, each `δ_j` is in `{0,1,2,3}`,
`r_j + δ_j ≤ 6`, and the separation-3 sum is `2r + δ`. The pairs
`(r_j, δ_j)` whose double-and-step lands in `{0,1,6,7,12}` are:

| `r` | `δ` | sum | mask bit | bridge letters |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 1 | 1 |
| 2 | 2 | 6 | 0 | 2 |
| 2 | 3 | 7 | 1 | 3 |
| 3 | 0 | 6 | 0 | 0 |
| 3 | 1 | 7 | 1 | 1 |
| 6 | 0 | 12 | 0 | 0 |

These seven rows are every pair with `r ∈ {0,...,6}` and `δ ∈ {0,1,2,3}`
inside the cap. In particular `(r, δ) = (5, 2)` sums to 12 but has
`r + δ = 7`, so it is outside a floor word. The value 12 occurs only as
`(6, 0)`.

Let `n_{rδ}` count coordinates of each row, and write `M` for the three
mask coordinates. Each mask coordinate consumes at least one bridge letter,
because its only rows are `(0,1)`, `(3,1)` and `(2,3)`. The three bridge
letters are therefore all consumed by `M` precisely when every mask
coordinate is `(0,1)` or `(3,1)` and every non-mask coordinate consumes no
letter. A coordinate `(2,2)` or `(2,3)` would spend two or three letters on
one coordinate. The budgets `|M| = 3` and `∑ δ_j = 3` leave no remainder, so

```text
n_{2,2} = n_{2,3} = 0,
```

the bridge letters are three distinct sources, and those sources are exactly
the mask. The same identity excludes `(5, 2)` even if the cap `r + δ ≤ 6`
is relaxed to 7: that row spends two letters and contributes no mask bit.
The widened enumeration below finds no weight-3 pair that uses a coordinate
with `q_21 > 6`.

The surviving equations are `n_{0,1} + n_{3,1} = 3`,
`n_{0,0} + n_{3,0} + n_{6,0} = 3`, and

```text
3 n_{3,0} + 3 n_{3,1} + 6 n_{6,0} = 18.
```

Set `n_{0,1}` from 0 to 3 and `n_{6,0}` from 0 to 3. Non-negative solutions
are exactly the six rows below. Each labeling of a row satisfies the cap, so
the number of count pairs is the multinomial coefficient.

| type | `(0,1)` | `(3,1)` | `(0,0)` | `(3,0)` | `(6,0)` | sorted sum | pairs |
|---|---:|---:|---:|---:|---:|---|---:|
| T1 | 0 | 3 | 0 | 3 | 0 | `(6,6,6,7,7,7)` | 20 |
| T2 | 0 | 3 | 1 | 1 | 1 | `(0,6,7,7,7,12)` | 120 |
| T3 | 1 | 2 | 0 | 2 | 1 | `(1,6,6,7,7,12)` | 180 |
| T4 | 1 | 2 | 1 | 0 | 2 | `(0,1,7,7,12,12)` | 180 |
| T5 | 2 | 1 | 0 | 1 | 2 | `(1,1,6,7,12,12)` | 180 |
| T6 | 3 | 0 | 0 | 0 | 3 | `(1,1,1,12,12,12)` | 20 |

T6 is the type named in PR6955. Up to permuting sources,
`q_18 = (0,0,0,6,6,6)` and the sum is `(1,1,1,12,12,12)`, with three
coordinates equal to 12. The witness

```text
333333444444555555012000001111122222
```

is one such floor word. Its centre sum contains a 2, as PR6955 records.

T1 is the only row with no coordinate equal to 12. A legal diagonal step
adds 1 on a coordinate in `{0,6}` and subtracts 1 on a coordinate in
`{1,7}`, or changes nothing when the two letters agree. Inside
`(6,6,6,7,7,7)` every such step exchanges a 6 with a 7, so the multiset is
unchanged. The value 12 is on neither list, so a coordinate equal to 12 is
fixed by every step that stays inside `{0,1,6,7,12}`.

## The mask at (0, 9)

The pair `(0, 9)` has sum `q_9`. A floor-word coordinate of `q_9` is at most
6, so the allowed values that can appear are `{0,1,6}`. Weight 3 forces
three coordinates equal to 1. Their contribution is 3, and the remaining
three coordinates are in `{0,6}` and sum to 6, so they are one 6 and two 0s.
Thus `q_9` is a permutation of `(1,1,1,6,0,0)`. There are
`6!/(3!2!1!) = 60` such vectors. The PR6955 word

```text
333333012000001111122222444444555555
```

has `q_9 = (1,1,1,6,0,0)` and is one of them. Its own separation-3 sum is
`(12,11,4,12,0,0)`, which is outside the allowed set. That word pays for the
mask at `(0, 9)` and does not pay for the slot `(18, 21)`.

Now let `q_9` be any of the 60 vectors, and suppose `(q_18, δ)` is a
weight-3 separation-3 pair with `q_18 ≥ q_9`. The coordinate where `q_9`
equals 6 is still 6 in `q_18`. The only legal row with first entry 6 is
`(6, 0)`, whose sum is 12. A positive bridge letter on that source would
make the sum at least 13, outside the allowed set. Every weight-3 extension
therefore freezes that source at 12.

This is the price. The explicit mask contributes `λ = 1`, through a single
6. On the separation-3 slot that same source is charged `λ = 2`, through a
12, and the slot still has to make up `λ = 6` in total. The three-12 family
T6 is incompatible with the prefix: T6 needs three coordinates of `q_18`
equal to 0, while three coordinates of `q_9` are already 1. The zero-12
family T1 is incompatible as well: T1 needs every coordinate of `q_18` equal
to 3, while one coordinate of `q_9` is already 6. The extensions that remain
are T2, T3, T4 and T5, with one or two coordinates equal to 12.

The finite set of extensions is every way to distribute the remaining nine
calls without passing 6, then every legal bridge. For each of the 60
prefixes that set contains 32 weight-3 pairs: 8 of type T2, 12 of type T3,
6 of type T4 and 6 of type T5. Exactly two of the eight T2 pairs repeat the
mask already realized at `(0, 9)`; the other 30 pairs realize a different
mask. Two floor words show that the count is positive:

```text
012333333001122444012001122444555555
012333333001122444015001122244455555
```

The first has separation-3 sum `(7,7,7,12,6,0)`, the same mask `{0,1,2}`.
The second has sum `(7,7,6,12,6,1)`, the mask `{0,1,5}`. Both keep
`q_9 = (1,1,1,6,0,0)`. The prefix therefore does not empty the slot. It
forces a 12 onto whatever mask the slot carries.

## Conditional exclusion

Write `S(s) = q_s + q_{39-s}`. The one-step identity is

```text
S(s+1) = S(s) + e_{w_s} - e_{w_{38-s}}.
```

**Hypotheses.**

- (H1) The pair `(0, 9)` is a weight-3 mask.
- (H2) For every `s = 4,...,18`, the pair `(s, 39-s)` is a weight-3 mask.

**Theorem.** No six-source characteristic-6 floor word satisfies (H1) and
(H2) together.

**Proof.** By the shape lemma, (H1) puts a 6 in some coordinate `j` of
`q_9`. Hypothesis (H2) at `s = 18` makes `(18, 21)` weight-3, so the price
above forces `S(18)_j = 12`. Solving the one-step identity for the earlier
index gives

```text
S(s) = S(s+1) - e_{w_s} + e_{w_{38-s}}.
```

Suppose `S(s)` and `S(s+1)` are both weight-3 and `S(s+1)_j = 12`. The
earlier sum differs from the later sum by moving one unit off `j`, onto
`j`, or by leaving `j` fixed. Moving it produces 11 or 13, both outside
`{0,1,6,7,12}`. Both sums are weight-3, so `j` is neither letter and
`S(s)_j = 12`. Starting at `S(18)` and repeating for `s = 17, 16, ..., 4`
keeps coordinate `j` equal to 12.

At `s = 4` the partner is 35, so `S(4) = q_4 + q_35`. The coordinates of
`q_4` sum to 4, and each coordinate of `q_35` is at most 6, so each
coordinate of `S(4)` is at most 10. It cannot be 12.

The chain in (H2) stops at `s = 18`. It does not include the centre
`s = 19`, which PR6955 already showed is empty. The immovable value on this
chain is 12, which is `2c` at `c = 6`. The integer 14 is congruent to 2
modulo 6 and is not an allowed coordinate here.

## What remains for a human proof of the unrestricted exclusion

Depth two requires every nonzero mask, on some pair `s + t ≡ 3 (mod 6)`. It
does not require (H1), and it does not require (H2). The theorem excludes
only the words that satisfy both. Three gaps remain visible from this slot.

T1 realizes a weight-3 separation-3 sum with no coordinate equal to 12, and
legal steps preserve that multiset. A word whose `q_9` is not a permutation
of `(1,1,1,6,0,0)` can sit in T1, and (H2) alone does not give the
propagation a 12 to carry. The balanced floor word with
`q_18 = (3,3,3,3,3,3)` and bridge `(1,1,1,0,0,0)` is one T1 count pair. Its
length-9 prefix is `(3,3,3,0,0,0)`, which is outside the allowed set.

If some index in `4,...,17` fails to be weight-3, a 12 at `s = 18` need not
survive down to `s = 4`. The two explicit words above satisfy (H1) and are
weight-3 at `s = 18`, with the forced 12, and this package does not claim
that their other diagonal indices are weight-3.

Masks on sums other than 9 and 39 are outside the price. The slot count on
`s + t ∈ {3, 39}` is the restricted model already settled by counting in
PR6955. PR6141's CaDiCaL 1.9.5 and MapleChrono UNSAT verdicts remain solver
evidence for the unrestricted statement. This package does not rerun them,
does not emit a DRAT certificate, and does not treat that UNSAT as a human
proof. The c=5 centre and the c=6 certificate budget named beside PR6216
are separate questions.

## Census and controls

The case analysis above is the classification. `verify.py` repeats it on the
finite domain and checks the orbit sizes.

The length-18 domain is every vector in `{0,...,6}^6` summing to 18. Inclusion-exclusion gives

```text
C(23,5) - 6 C(16,5) + C(6,2) C(9,5) = 9331.
```

Each vector is joined to every bridge in `{0,1,2,3}^6` that sums to 3 and
respects the cap. Two enumerators, direct products and a recursive
composition, agree on the bridge count of every length-18 vector,
`327216` bridges in total, and on the `700` weight-3 pairs, split
`20 + 120 + 180 + 180 + 180 + 20`. A box search over type-counts in
`{0,...,6}` recovers the same six solutions. Admitting `q_21 = 7` adds no
weight-3 pair.

Separately, all `7^6` vectors summing to 9 contribute exactly the 60
permutations of `(1,1,1,6,0,0)` as weight-3 masks. Each of those 60 prefixes
has exactly 32 weight-3 extensions, with the type split above. The move
table fixes every 12 on all 700 sums: `3060` legal steps were checked, and
the `180` legal steps on the 20 sums of type T1 preserve the multiset
`(6,6,6,7,7,7)`. All `756` pairs `q_4 + q_35` have coordinates at most 10.

These domains are finite, the loops visit every element, and the counts
match the closed forms. This is an exhaustive census of count pairs. It is
not a census of words, and it is not a SAT run.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-separation3-classification/verify.py
python3.12 -I -O -W error -B research/six-source-c6-separation3-classification/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-separation3-classification --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C6_SEPARATION3_CLASSIFICATION vectors=9331 bridges=327216 weight3=700 types=20+120+180+180+180+20 widened_only=0 pair09=60 priced_extensions=32 same_mask=2 orbit=60 moves_preserving_12=3060 type1_moves=180 short_pairs=756 controls=15
```

Failures raise `SystemExit`. Optimized mode cannot silence them. No Lean,
Docker, or solver replay was run.

## Open next questions

1. Can one floor word keep the multiset `(6,6,6,7,7,7)` at every diagonal
   index `s = 4,...,18`? *Why:* T1 is the only separation-3 family with no
   frozen 12, and legal steps preserve that multiset, so the exclusion above
   uses (H1) in an essential way. A word would show that (H2) by itself still
   has a one-step model. An obstruction would be a different human step.
   *First step:* split each coordinate of that multiset into a pair of prefix
   counts and test whether the splits at `s = 4` and `s = 18` can sit in one
   monotone chain. *Blocked by:* the move closure constrains the sum multiset
   and does not determine the split.
2. Which weight-3 shape on one pair with `s + t = 15` forces a 12 at
   `(18, 21)`? *Why:* depth two also quantifies over sums other than 9 and
   39. The pair `(0, 9)` is one early slot. *First step:* list the weight-3
   sums realizable at one index pair of total 15, and test one shape against
   the six families. *Blocked by:* a gap longer than three letters has a
   different bridge budget, so the six families do not transfer to that pair.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR4231, PR4248, PR6107), with the Ross Richardson PR934/PR943 lineage.
JosieElliston's PR6141 records the c=6 solver verdict and leaves the human
proof open. Nick Petalas's handoff on 2026-11-03
([discussion comment 19384981](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19384981))
states the diagonal slot count and the off-diagonal prefix. The frozen-12
propagation along a weight-3 diagonal is the c=6 form of the equality-case
step proved for c=7 in the fork draft
[PR156](https://github.com/unpaidmoon/integer-mult-bounds/pull/156), recorded
upstream as discussion comment 19493159. PR6955 supplies the empty centre,
the two explicit floor words, and the question this package answers. It is
not re-proved here. queelius's PR6216 certifies characteristic five. zxv's
PR6057 and JosieElliston's PR6061 supply the `c ≥ 8` words.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
