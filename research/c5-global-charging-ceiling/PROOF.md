# A ceiling for nonnegative C5 cost aggregation

## Contract

Fix the 56 physical nondegenerate binary planes in PR1825's matching, with the
112 labels retained by PR2782. For plane-index sets A and B, define r(A,B) as
the binary rank of their complete-plane pairing matrix. Every dimension of a
touched plane is charged, even when only one scalar port has a nonzero factor.
The full label space has dimension nine.

A finite asymmetric scalar fit is a sum of outer products over Q, R or C,
with ordinary transpose. Its prescribed diagonal is one; prescribed cross
entries vanish. Terms may have arbitrary coefficients and may cancel. Let
A_t and B_t be the source and target plane supports of term t. Its paid cost is
r(A_t,B_t). This note does not assert that this algebraic tariff supplies a
native reversible program.

Let C range over the 23 induced C5s of the plane-orthogonality graph. The local
restriction tariff is

```
r_C(A,B) = r(A intersect C, B intersect C).
```

Grant, as premises, all 23 proposed local inequalities

```
sum_t r_C(A_t,B_t) >= 20.
```

The result below does not prove or independently admit these premises. It
limits a particular way of using them, even if all are true. PR3256, PR3268,
PR3271 and PR3279/3281 supply the local work and retain its credit.

## The proof method being audited

Choose nonnegative real weights lambda_C, not all zero, and a positive real
normalizer c. Require the termwise charging inequality

```
sum_C lambda_C r_C(A,B) <= c r(A,B)                 (1)
```

for every source/target plane-support rectangle. Summing over the terms of a
fit and applying the local premises yields only the numerical floor

```
L(lambda,c) = 20 sum_C lambda_C / c.                (2)
```

This is a single nonnegative linear aggregation followed by uniform termwise
rank domination. It does not include scalar coefficient equations, restrictions
on irredundant or optimal factorizations, term-count constraints, signed
combinations of local inequalities, or a fit-dependent charging argument.

## Full-support test

Take A=B to be all 56 planes. Exact binary elimination on the authenticated
physical labels gives

```
r(A,B) = 9,
#{C : r_C(A,B)=7} = 4,
#{C : r_C(A,B)=8} = 6,
#{C : r_C(A,B)=9} = 13.
```

In particular the local ranks sum to 193, rather than the global tariff nine.
Both reconstructions in this package verify these finite premises. The primary
uses packed-bit elimination and a bounded path census. The separate checker
uses dense elimination and all 3,819,816 five-element plane subsets.

Write d_C for the displayed local ranks. Evaluating (1) on this single legal
rectangle forces

```
c >= (sum_C lambda_C d_C)/9.
```

Consequently every valid choice in this method satisfies

```
L(lambda,c) <= 180 sum_C lambda_C / (sum_C lambda_C d_C)
             <= 180/7 < 26.                       (3)
```

This covers every nonnegative real weight vector, not merely the rational
weights sampled by the tests. The second inequality follows from d_C>=7.
If any weight lies on a rank-eight or rank-nine core, it is strict. More
precisely, if Lambda_j is the total weight on rank-j cores, the first upper
bound is

```
180 / (7 + (Lambda_8 + 2 Lambda_9)/(Lambda_7+Lambda_8+Lambda_9)).
```

The four rank-seven cycles, in the canonical physical orientation, are

```
(3,10,7,44,38), (3,10,14,55,18),
(4,6,13,23,12), (14,24,30,28,33).
```

Concentrating weights on these four attains 180/7 in the *full-support test*.
It is not a certificate that (1) holds for other rectangles, and no optimum
for the complete termwise problem is claimed.

For uniform weights, the stronger necessary condition c>=193/9 gives

```
L(1,c) <= 4140/193 < 22.                           (4)
```

Costs are integers, so a real floor at most 180/7 can round upward to 26.
The result therefore excludes a real floor 26 and an integer floor 27 by
this method. It does not exclude an integer floor 26. Uniform aggregation
cannot give an integer floor 23. These distinctions matter at the ceiling.

## The test term is not excluded by scalar correctness

A full-support outer product is permitted as an individual term of a strict
fit. Let J be the 112-by-112 all-ones matrix. Start with the identity expressed
as its 112 coordinate outer products, and append +J and -J. The resulting
114-term sum is exactly the identity, hence fits every strict scalar mask in
question over Q, R or C. Each appended term has source and target support all
56 planes. Its full-plane tariff is nine. The coordinate terms each cost two,
so this deliberately inefficient complete fit costs 224+18=242.

The primary constructs and sums these terms. The separate checker multiplies
two explicit 112-by-114 factor matrices. Both check all 12,544 scalar entries.
Changing the final sign is a rejecting control. This construction is not an
efficient decoder, a counterexample to a decoder lower bound, or a claim that
an optimal decomposition contains a cancelling pair. An argument restricted
to optimal or cancellation-free decompositions would need an additional lemma
and is outside (1).

## Consequence and stop decision

The local cost20 conclusions cannot simply be added to obtain a useful large
global floor through (1). Weight optimization alone cannot remove the
full-support obstruction. This closes the stated proof-method screen, not
the global charging question in general.

The family decision is **narrow and stop**. Before another local-core census,
name a genuinely new global constraint. A next attempt may use simultaneous
coefficient/trace equations across overlapping cores, a justified restriction
on optimal decompositions, or another fit-level argument. Any such extension
must retain complete-plane tariffs and explain why shared terms are not paid
multiple times. No new decoder, supplier, kappa, selected-frontier update,
native implementation, dirty-state restoration or physical-cost claim follows.
The all-size/compiler, hosting, precision/tape and outer analytic obligations
remain separate. This is a written proof with exact finite premises, not a
proof-kernel theorem or independent human review.
