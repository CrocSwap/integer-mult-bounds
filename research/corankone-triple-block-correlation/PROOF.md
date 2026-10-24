# A pair of binary full guards is negatively correlated with a third guard

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let U1,U2,U3 be pairwise orthogonal rank-one idempotents on F2^m,
where m>=3, and let Ei be the event that every leading principal minor
through rank m-1 of G(I-Ui)G^-1 is nonzero. All three events use the same
uniform complete header G in GL_m(F2).

**Theorem.** Pr(E1 E2 E3) < Pr(E1 E2)Pr(E3), for every m>=3.

This is a scoped counting proof with an exact computer-assisted finite
component. It answers the first bounded step in Open next question 1 of
Nick Petalas's [#4767](https://github.com/CrocSwap/integer-mult-bounds/pull/4767).
The pair and triple counting laws below are cited predecessor theorems,
not re-proved or independently audited here. The new result compares a
two-event block with a singleton. Symmetry gives every permutation of
the split. No statement about arbitrary increasing functions is claimed.

## Cited inputs and the new reduction

Write n=m-1, X=2^m, and define

```text
A = 9^n - 2*7^n + 5^n,
B = 3^n A = 27^n - 2*21^n + 15^n,
T = 27^n - 6*21^n + 6*19^n - 6*17^n + 16*15^n
    - 18*13^n + 9*11^n - 2*9^n.
```

Nick Petalas's #4227, #4261 and #4275 respectively supply

```text
p1 = Pr(E3)       = 3^n / ((X-1)2^n),
p2 = Pr(E1 E2)    = A / ((X-1)(X-2)2^(2n)),
p3 = Pr(E1 E2 E3) = T / ((X-1)(X-2)(X-4)2^(3n)).
```

These are complete-header probabilities. All source proofs are pinned as
historical provenance in SOURCES.json. No predecessor executable is used.
The sharp difference from the earlier comparison p3<p1^3 is that the
denominator of the new ratio contains the nontrivial pair numerator A.

For n>=2, A>0 by strict convexity of t^n at 5,7,9. Equivalently, the
even terms of (7+2)^n+(7-2)^n-2*7^n are positive. Thus B>0, and

```text
R = p3/(p2 p1) = (T/B)(X-1)/(X-4).
R<1  iff  (X-4)B - (X-1)T > 0.                         (1)
```

The factor (X-1)/(X-4) must be retained. Treating complete headers as
independent factor coordinates would omit it.

## Uniform tail, n>=42

Put x=(7/9)^n. The terms of T below base 21 have absolute coefficient
sum 57 and bases at most 19. Exact integer arithmetic gives

```text
57*19^42 < 21^42.
```

Since 19/21<1, for every n>=42,

```text
0 <= T <= 27^n - 6*21^n + 57*19^n < 27^n - 5*21^n.
```

The lower bound uses the cited interpretation as a count. Since
27^n-2*21^n < B < 27^n, this yields

```text
T < B - 3*21^n,
T/B < 1 - 3*21^n/B < 1 - 3x.
```

The last upper bound is positive at n=42, as checked by
3*7^42<9^42, and remains positive for larger n.

For n>=3, X>=16, so X-4>=3X/4. Also
2<(14/9)^2 and 14/9>1 imply 2/2^n < (7/9)^n for n>=2. Consequently

```text
(X-1)/(X-4) = 1 + 3/(X-4) <= 1 + 4/X
            = 1 + 2/2^n < 1 + x.
```

Every factor needed to multiply these upper bounds is nonnegative.
Therefore, for n>=42,

```text
0 <= R < (1-3x)(1+x) = 1-2x-3x^2 < 1.
```

## Exact finite component, 3<=m<=42

The verifier evaluates all 40 integers in (1), using unrestricted-precision
integer arithmetic, and requires each to be strictly positive. It also
computes p1,p2,p3 independently as rational expressions and requires their
ratio to equal (1)'s ratio. The generated stdout receipt lists every m,
its integer gap and its exact ratio. There is no floating-point tolerance.
At m=3 the triple count is zero and the pair count is positive. At m=4,

```text
p1=9/40, p2=1/80, p3=1/1680, R=40/189.
```

This finite component and the uniform tail cover every m>=3. The extra
86 exact comparisons at 43<=m<=128 corroborate the tail bound, without
being a substitute for its quantified proof. The verifier also rejects
grouped independence, a reversed leading spectral sign, an omitted
finite-GL correction and invalid replay dimensions. QED.

## Scope

Only binary arithmetic, orthogonal kernel lines and uniformly weighted
complete GL headers are covered. The pairwise inequality from #4767 and
the three-independent-marginal inequality from #4275 do not imply this
split inequality; those predecessor results retain their credit.

This result alone does not prove negative association of the three-event
Bernoulli vector. For example, comparison of E1 union E2 with E3 would
require a second inequality. Larger blocks, odd fields and restricted
header distributions remain open. A request producer, header selection,
emission, dispatch, dirty restoration, stock, precision and a full paid
physical caller are not supplied. No new kappa, supplier admission or
complete multiplication theorem follows. Independent human and formal
proof-kernel review are unclaimed.
