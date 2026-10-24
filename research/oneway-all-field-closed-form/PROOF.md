# All-field closed form for one-way coupled full guards

This scoped counting proof was produced by Nick Petalas. Apache-2.0.

Let K be a finite field of order q, m>=2, and n=m-1. Let U,V be rank-one
idempotents on K^m with UV nonzero and VU=0. Set P=I-U and Q=I-V.
Choose a complete header G uniformly in GL_m(K). A request passes when
every leading principal minor of its conjugate, through order m-1, is
nonzero. Define

```text
alpha=(q^2-q+1)^2, beta=q^3-q+1, gamma=q^3-q^2+1,
D=(q^m-1)(q^m-q)q^(2m-4).
```

The exact joint passing fraction is C(q,m)/D, where

```text
C(q,m) = (q-1)/q^2 * [(q-1)alpha^n - (q-2)beta^n - gamma^n].       (1)
```

Thus the number of complete passing headers is C(q,m)|GL_(m-2)(K)|.
This replaces #4274's all-field transfer by a closed formula. Its binary
specialization was already proved there; the new claim is the all-field
expression. There is no new kappa or supplier claim.

## Cited input and changed initial matrix

Nick Petalas's [#4274 transfer theorem](https://github.com/CrocSwap/integer-mult-bounds/pull/4274),
retained in the main-branch source pinned by SOURCES.json, identifies
normalized pairs YX=L, with L=[[1,1],[0,1]], and equal header fibers.
The partial Gram sum A must have A_11,A_22 different from 1 until its
last increment. For any 2 by 2 matrix H let w(H) equal 2q^2-1 at zero,
q-1 at nonzero rank one, and zero at rank two.

Make the substitution B=L-A. Its diagonal restriction is exactly that
both diagonal entries of B are nonzero. The initial state is B=L and
the terminal weight is h(B)=w(B). Negation preserves w. Consequently

```text
C(q,m) = (T^n h)(L),
(Tf)(B) = sum_(C with nonzero diagonal) w(B-C)f(C).
```

The transfer and header-fiber theorem are predecessor credit, not new
results or independent audits in this contribution.

## Solving the invariant coordinates

Use the three-function identities proved in Nick Petalas's
[#4747, PROOF.md, Three invariant functions](https://github.com/petalas/integer-mult-bounds/blob/f51dcebce79b8b8958427a9a9b7bc8feca352c9d/research/corankone-all-field-law/PROOF.md).
This is an exact external theorem citation at commit
f51dcebce79b8b8958427a9a9b7bc8feca352c9d; no source code from that
pending package is imported or replayed. Put r=q-1 and
z(B)=1_(B_12=0)+1_(B_21=0). The cited identities are

```text
T1 = alpha 1,
Tz = 2r^3 1 + beta z,
Th = r^2(q^2-3q+4)1 - r^2 z + gamma h.                         (2)
```

Write T^n h=a_n 1+b_n z+c_n h. This representation need not be unique
on small fields; the following coefficient solution still proves the
function identity. From (2), starting at (a_0,b_0,c_0)=(0,0,1),

```text
a_(n+1) = alpha a_n + 2r^3 b_n + r^2(q^2-3q+4)c_n,
b_(n+1) = beta b_n - r^2 c_n,
c_(n+1) = gamma c_n.
```

Direct substitution gives, for every integer n>=0,

```text
q^2 a_n = r^2 alpha^n + 2r beta^n - r(q+1)gamma^n,
q^2 b_n = -qr(beta^n-gamma^n),
c_n = gamma^n.                                               (3)
```

For clarity, the polynomial identities needed in this substitution are

```text
beta-gamma=qr,
alpha-beta=qr^3,
(q+1)(alpha-gamma)=q r[2r^2+q(q^2-3q+4)].
```

The initial coefficients in (3) are 0,0,1. The last recurrence is
immediate; the first two follow from these identities. Induction proves
(3) without a characteristic restriction. All divisions here occur in
the rational counting coefficients, not in K, so characteristic two is
included.

Finally, z(L)=1 and h(L)=0 because L has one zero off-diagonal entry
and is invertible. Hence C=a_n+b_n. Combining (3) yields (1).
The cited equal-fiber theorem supplies the probability denominator and
the complete-header count. This proves the stated all-field result.

## Boundary examples and scope

At m=2 the numerator simplifies to
(q-1)^2(q^2-3q+3). For q=2,3,4,5 the passing fractions are respectively
1/6, 1/4, 7/20, 13/30. At q=3,m=3 the fraction is 53/351, agreeing
with #4274's one-way transfer example. For q=5 the new formula is

```text
C(5,m)=(4/25)[4*441^n-3*121^n-101^n].
```

Only the closed form is new. No negative-correlation theorem for odd
fields, classification of two-way coupling, restricted header theorem,
or physical implementation is claimed. Selection, emission, dispatch,
dirty restoration, precision and stock costs are unknown. The proof
uses the cited all-field invariant identity as a predecessor theorem;
independent human and formal proof-kernel review are unclaimed.
