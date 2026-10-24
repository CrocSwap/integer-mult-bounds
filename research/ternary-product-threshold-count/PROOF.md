# The ternary threshold population

## Statement and cited input

Let K=F3 and R=K^4. A target has two roles and four invertible
components M_i in GL_2(K). Paid factors are I+u y^T with u in R^2 and
y in K^2. Common GL_2(K) maps are free anywhere. Components and their
order are distinguished; scalar multiples are different matrix targets.

Exactly 9,216 of the 48^4=5,308,416 targets have paid cost three.
The exact fraction is 1/576. The corresponding unordered sets of four
projective actions are precisely the left cosets of the regular C4 and
V4 subgroups of S4. Eighteen cosets have cyclic type and six have Klein
type, giving respectively 6,912 and 2,304 ordered matrix targets.

This is a new counting consequence of ToikY's field-product theorem in
[PR #4334](https://github.com/CrocSwap/integer-mult-bounds/pull/4334),
retained at the source pinned in SOURCES.json. Sections 2 and 3 there
are cited inputs:

* cost is at most two exactly when some nonzero common row phi and
  column t satisfy phi M_i t != 0 for every component;
* every invertible field-product target costs at most three.

Those statements and their proof are not reverified here. They follow
the low-factor criteria of Nick Petalas #4276 and the alphabet of
Wentao Li #4099 following #2513. The count below is in that exact model.

## 1. Reduction to four permutations

The projective input lines are represented by (1,0), (0,1), (1,1), (1,2).
For each nonzero vector M_i t there is exactly one projective row phi
annihilating it. Thus the cited criterion fails exactly when, for every
input line T, the four output lines M_i T cover all four projective lines.
The upper bound then makes the cost exactly three.

GL_2(F3) has (3^2-1)(3^2-3)=48 elements. Its action on these four lines
has kernel {I,-I}. Indeed, fixing the coordinate lines forces a matrix
to be diagonal; fixing the line of (1,1) forces equal diagonal entries.
The resulting faithful quotient has order 24, so its image is all S4.
Every permutation has exactly two matrix lifts.

Write p_1,...,p_4 for the projective permutations. A cost-three target
therefore has {p_1(T),...,p_4(T)} equal to the whole line set for every T.
In particular these permutations are distinct. Their 4-by-4 output array
is a Latin square. We count it directly, without importing a Latin-square
table or claiming the classical order-four enumeration as new mathematics.

## 2. Classify the normalized supports

Let S be a four-permutation support with the stated coverage. Left-multiply
all its elements by the inverse of any element g in S. Coverage is
preserved, and the normalized support H=g^-1 S contains the identity.
Every other element of H is a derangement, and any two elements disagree
on every input.

The derangements of S4 are its three double transpositions and six
four-cycles. If H contains no four-cycle, it consists of the identity and
all three double transpositions. This is the regular Klein group V4.

If H contains a four-cycle c, relabel its points so c=(1 2 3 4). A
permutation d compatible with both identity and c must satisfy
d(i) not in {i,c(i)} for all i. There are exactly two such permutations,
c^2 and c^3. For completeness, if d(1)=3, then d(3)=1 and the remaining
values force d=(3,4,1,2)=c^2. If d(1)=4, the remaining distinct values
force d=(4,1,2,3)=c^3. Hence H={1,c,c^2,c^3}, a regular cyclic group.

There is one regular Klein subgroup and three cyclic subgroups of order four,
since the six four-cycles pair with their distinct inverses. Conversely,
each of these four regular subgroups, and each of its left cosets, meets
the coverage condition. This proves the claimed classification.

## 3. Count without duplicate cosets

Each subgroup has index six in S4 and therefore six left cosets. Cosets
arising from different subgroups cannot coincide. If S=gH=g'H', choose
s in S; then s^-1 S equals both H and H', so H=H'. Consequently there
are 3*6=18 cyclic supports and 1*6=6 Klein supports, 24 in total.

Every support has 4!=24 orders and each of its four permutations has two
independent matrix lifts. The number of matrix targets is therefore

```text
cyclic: 18 * 24 * 2^4 = 6,912
Klein:   6 * 24 * 2^4 = 2,304
total:  24 * 24 * 2^4 = 9,216
fraction: 9,216 / 48^4 = 1/576.
```

There is no quotient by the free maps in this enumeration. A free map
changes the paid metric but does not identify distinct target matrices.
Likewise, ordering the algebra components is part of the target data.
Counting supports without the 24 orderings or forgetting the sixteen
scalar lifts would answer different questions.

## Scope and credit

This is a scoped counting proof with an exhaustive finite certificate.
The cited theorem supplies the cost interpretation. The new result is
its exact ternary four-component population and its projective coset
classification, produced by Nick Petalas. ToikY #4334, Nick Petalas
#4276/#4243, Wentao Li #4099 and the #2513 lineage retain predecessor
credit. The projective action, elementary permutation groups and
order-four Latin squares are classical.

Other fields, other component counts, singular targets and local-algebra
lifts are outside this theorem. Native coefficient preparation, routing,
control, restoration, precision, stock and complete supplier costs remain
unknown. No supplier, selected frontier or complete multiplication theorem
changes. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.
