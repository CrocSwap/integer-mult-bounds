# Rank 3 blocks a universal length-30 singleton word

This note proves one obstruction and three size floors. It does not decide
whether a universal length-30 word exists. The inherited gap
`28 <= f(8) <= 32` stays in force, and the selected exponent is unchanged.

The rank-at-most-2 obstruction, the rank-3 bent lower bound of 17 layer-0
points, and the 4+4 prefix-set obstruction are cited from the length-30
sojourn package (upstream pull request 6943, head
`c1cf726df3a06e50ef655ae91e8c8aac942b19a7`) and are not reproved here.

## Model

Sources `x_0,...,x_7` are the standard basis of `F_2^8`. A word of length
`L` has prefixes `q_0 = 0` and `q_t = e_{w_1} + ... + e_{w_t}`. Restoration
means `q_L = 0`, so every source occurs an even number of times. The word is
universal when

```text
P + P = F_2^8,  P = {q_0, ..., q_(L-1)}.
```

Addition is XOR. At `L = 30` the deletion bound `f(7) = 24` forces every
multiplicity into `{2,4,6}`, and every such vector has a source of
multiplicity 2. Fix one such source at word positions `f < g`. The bit of
that source equals 1 exactly on the `m = g - f` prefixes with `f < t <= g`.
Those prefixes form layer 1. The other `30 - m` prefixes form layer 0.
Deleting the coordinate, write `Q0` and `Q1` for the two projected sets.
Universality is equivalent to

```text
Q0 + Q1 = F_2^7,
(Q0 + Q0) ∪ (Q1 + Q1) = F_2^7.
```

The open sojourn is the interior word `w_(f+1), ..., w_(g-1)`. Its distinct
sources span an `r`-dimensional space `V`, `Q1` lies in one coset of `V`, and
`Q1 + Q1` is contained in `V`.

Translating the origin to the vertex immediately before one occurrence of the
double source makes that source the first letter and puts `0` in `Q1`.
Renaming coordinates then makes the double source label 7 and the sojourn
labels `{0,1,2,...,r-1}`. Differences are invariant under that translation and
under permutation of the basis, so a cover in the original word exists exactly
when the normalized word covers.

## Pair-count floors

`Q1 + Q1` misses every vector outside `V`. Those `128 - 2^r` vectors are
nonzero, and every one of them must lie in `Q0 + Q0`. Distinct nonzero sums
of an `n`-point set number at most `C(n,2)`. Therefore

```text
|Q0|(|Q0| - 1) / 2 >= 128 - 2^r.
```

The smallest integers `n` that pass are

```text
r = 3: n >= 16,    r = 4: n >= 16,
r = 5: n >= 15,    r = 6: n >= 12.
```

At rank 7 the outside of `V` is empty, so this count gives no floor. At rank
3 the cited bent argument is stronger (`|Q0| >= 17`); the pair count is the
new information at ranks 4, 5 and 6.

The same coset decomposition gives a second floor. Identifying each coset of
`V` with `V`, every coset fiber `S` of `Q0` must satisfy `S + Q1 = V`, so
`|S| >= ceil(2^r / |Q1|)`. There are `2^(7-r)` cosets, and
`|Q0| + |Q1| <= 30` because the two layers partition the 30 prefixes. The
verifier checks the boundary pairs of these windows. In particular:

- rank 3 forces `|Q1| = 8`, hence `Q1` is the whole 3-flat, and `16 <= |Q0| <= 22`;
- rank 4 forces `8 <= |Q1| <= 14` and `|Q0| >= 16`;
- rank 5 forces `6 <= |Q1| <= 15` and `|Q0| >= 15`;
- rank 6 forces `|Q0| >= 12`.

A fiber of size 7 or less at rank 3 would need at least two points in each of
16 cosets, hence at least 32 layer-0 points. Layer 0 has at most 29 prefixes.

## Height steps in the rank-3 normal form

Now `r = 3`, `Q1 = V = span{e_0,e_1,e_2}`, and the word is `[7] + A + [7] + B`.
The arc `A` has length `a` and uses only labels `{0,1,2}`. Its partial sums,
including the start, are exactly `Q1`, so `a >= 7` and the walk visits all
eight points of `V`. Layer 1 then has `a + 1` prefixes and layer 0 has
`29 - a` prefixes. The complementary arc `B` has length `b = 28 - a`.
Since `B` contains at least 16 quotient steps, `b >= 16` and therefore
`a <= 12`. That upper bound is the quotient-length constraint, not the cited
bent floor of 17.

Call a step of `B` a height step when its label lies in `{0,1,2}`, and a
quotient step otherwise. Quotient steps move the `F_2^4` spanned by
`e_3,...,e_6`. Visiting all 16 quotient points takes at least 15 quotient
steps. Each quotient label occurs an even number of times, so the number `q`
of quotient steps is even, hence `q >= 16`. The remaining `k = b - q` steps
are height steps.

Let `h_t` be the `{0,1,2}`-component after `t` steps of `B`, with `h_0` equal
to the endpoint sum `s` of `A` and `h_b = 0`. The stored layer-0 heights are
`{h_0,...,h_(b-1)}` together with the global origin `0`. At most `k` of the
steps that produce stored prefixes are height steps: the last step of `B` is
not stored, and if it is a height step then only `k - 1` height steps remain
in the stored range. A stored walk with `m` height changes has at most `m + 1`
heights. Adding the origin therefore yields at most `k + 1` heights in `Q0`.

Those heights must form a difference basis of `F_2^3`. Otherwise some
component `v` is missed by every sum of two layer-0 points, and every outside
vector with that component is missed. Every 4-point subset of `F_2^3` has at
most `C(4,2) = 6` nonzero sums, so it is not a difference basis. A basis has
at least 5 points. Thus `k >= 4`.

Combined with `q >= 16` and `b = 28 - a`, this leaves only two families:

```text
a = 7, b = 21, q = 16, k = 5,
a = 8, b = 20, q = 16, k = 4.
```

Every larger `a` has `k <= 3`. The verifier exhausts every height-step word of
length `k <= 3` and every placement of those steps in an arc of length at most
21; none of the stored height sets is a difference basis of `F_2^3`.

## The two families do not cover

A quotient word is a walk of length 16 on the 4-cube, based at 0, that visits
every vertex and uses each of the four directions 2, 4 or 6 times. There are
2592 such words. Relabeling the four quotient coordinates acts freely on them,
with 108 orbits. The verifier recomputes the orbit count and checks that the
search program's representatives are exactly those 108 orbits. A cover exists
for some quotient word if and only if it exists for the representative,
because the relabeling is a linear automorphism fixing the height coordinates
and preserving sums.

For each family the search runs over every word of length `k` in the alphabet
`{0,1,2}` and every set of `k` insertion slots in the arc of length `16 + k`.
A placement whose stored heights do not form a difference basis is rejected.
Every remaining placement is scored on all 108 representatives. The score is
the number of vectors outside `V` missed by `Q0 + Q0`. The minimum score is 2.
No placement scores 0.

The two programs agree on a fixed control: the quotient word
`0 1 2 3 0 1 2 1 0 1 2 3 0 1 2 1`, height word `0 0 1 1 2`, and the five slots
`0,1,2,3,4`, with start height 4, misses 60 outside vectors. That value was
also matched against the prefixes of the corresponding length-30 word.

Therefore no normalized rank-3 word is universal, and neither is any
rank-3 word before normalization. Every multiplicity-2 sojourn of a universal
length-30 word has rank at least 4, once the cited rank-at-most-2 obstruction
is included. The rank-3 half does not use that citation.

## What this does not say

The recorded length-30 word

```text
1 5 4 0 4 3 6 4 7 4 1 7 6 4 2 6 5 6 7 0 6 5 6 2 5 0 3 7 4 0
```

still has 30 distinct prefixes and coverage 255, missing only mask 131. Its
three double sojourns have ranks 6, 4 and 7, with 20, 21 and 9 distinct
layer-0 projections. All three sit in the integer windows above. The new
floors do not remove this near-miss.

The length-32 Gray concatenation remains universal, so the upper bound
`f(8) <= 32` is unchanged. No supplier, readout schedule, or selected
frontier is changed. `f(7) = 24` is an inherited hypothesis and was not
replayed. The unpublished annealing search in the handoff was not replayed.
Length 28 was not searched.
