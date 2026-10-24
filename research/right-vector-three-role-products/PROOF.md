# A sharp five-factor bound for binary three-role products

## Model and claim type

Put K=F2 and R=K^k for a positive integer k. A paid factor on three roles is

```text
P(u,b) = I + u b^T,     u in R^3, b in K^3.
```

The embedding K into R is diagonal. Thus b is common to all k components,
whereas u may have a different binary three-vector in each component. Free
maps are common matrices in GL3(K), allowed anywhere. No extra roles are
allowed. This is the formal alphabet of Wentao Li #4099 following #2513,
with the free-map normal form retained in Nick Petalas #4243. ToikY #4334
proved the sharp two-role field-product result and its common-direction
upper construction.

This package supplies a complete finite certificate and a scoped algebraic
consequence of that certificate:

1. Every invertible three-role target over F2^k costs at most five paid factors.
2. The target U over F2^168 whose components list GL3(F2) costs exactly five.
   Therefore the uniform bound is sharp, also for every k>=168 by padding.
3. For that U the column lower bound delta(U) is exactly three. Its gap from
   the exact cost is two.

No minimum component count for cost five is asserted. No all-field,
extra-role, local-ring or native-supplier statement is asserted.

## 1. Reduction to common direction words

Conjugation by a free matrix S preserves the alphabet:

```text
S P(u,b) S^-1 = P(Su, S^-T b).
```

Move all free maps to the right. A word of length L is a product of L paid
factors followed by one common free S. For chronological direction sequence
b1,...,bL, define the paid product as P_L ... P_1, with P_1 applied first.
A zero direction gives the identity. It can be replaced by b=e1,u=0.
Words shorter than four can likewise be padded to four.

If a component of the target is invertible, every square factor in that
component must be invertible, by rank submultiplicativity. In K, write a
component paid factor as I+a b^T. It is invertible exactly when b.a=0.
Indeed when b.a=0 its square is I. When b.a=1, a is nonzero and the factor
kills a. For each nonzero b there are exactly four eligible a, including
zero. These are all possibilities, not a restriction to coordinate vectors
or to some chosen gate library.

There are seven nonzero directions. For a fixed ordered word of length
four there are exactly 4^4 eligible parameter tuples. Its reachable set is
computed from {I} by left multiplication by each of the four eligible
factors at each step. There are exactly 7^4=2401 ordered direction words.

## 2. The complete finite certificate

`verify.py` encodes a binary matrix by its three rows, each a three-bit
integer, least significant row first. Thus I has encoding 273. It builds
GL3(F2) by rank-three elimination on all 512 matrices. Independently, it
builds every binary linear bijection on the eight vectors by enumerating
all ordered triples of nonzero basis images and retaining the bijections.
Both groups contain the same 168 matrices.

The matrix calculation propagates reachable sets through all four steps.
The independent calculation composes permutations of the eight vectors:
first all 16 parameter choices for each two-direction word, then every
pair of two-step results. It explicitly enumerates all
7^4 * 4^4 = 614656 direction/parameter tuples. The two implementations agree
on the complete 168-bit endpoint mask for every one of the 2401 direction
words, rather than merely on cardinalities.

The resulting complete histogram is:

| Reachable group elements | 4 | 16 | 24 | 64 | 96 | 144 |
|---|---:|---:|---:|---:|---:|---:|
| Ordered four-direction words | 7 | 126 | 420 | 504 | 672 | 672 |

In particular no four-direction word reaches all 168 matrices.

For the fixed chronological sequence

```text
b1,b2,b3,b4,b5 = e1,e2,e3,e1,e2,
```

the matrix calculation constructs one literal five-factor witness for each
of the 168 matrices. The action calculation independently enumerates all
4^5=1024 parameter tuples and reaches all 168 endpoints. Every constructed
witness is also evaluated on all eight binary inputs, giving 1344 complete
component/input checks. This proves the upper-bound certificate. The
verifier hashes the complete four-word endpoint table and the complete
five-factor witness table. It also emits a generated receipt bound to the
six package files and two pinned predecessor inputs.

The computations are exact and use no randomness, numerical tolerance,
symmetry reduction or pruning. All validations remain active under -O.
They are executable finite evidence, not formal proof-kernel checking.

## 3. Sharpness with arbitrary free maps

For any common S in GL3(F2), the components of U S^-1 again list every
element of GL3(F2), since right translation permutes the group. If U had a
word with at most four paid factors and any free maps, Section 1 would give
a common four-direction word for U S^-1 after identity padding. Its
components would then have to lie in a reachable set of at most 144
elements. They contain all 168, a contradiction.

For any invertible M over F2^k, each component M_i has the Section 2 witness
with the same five directions. At step j assemble its k left coefficients
into u_j in R^3. Componentwise multiplication now gives M in five paid
factors. Arbitrary componentwise left coefficients are permitted by the
stated model; componentwise free maps or right directions are never used.
This proves the quantified upper bound and cost(U)=5. Appending arbitrary
invertible components to U preserves its lower bound by projection and its
five-factor upper bound by the same construction.

## 4. The column-bound gap

The predecessor's general column bound is

```text
delta(M) = min over T in GL3(F2) of dim_F2 ((M T - I) F2^3) <= cost(M).
```

For U and any T, its translated components range over every group element.
If a nonzero v were in the common kernel, every A in GL3(F2) would satisfy
A v=v. But GL3(F2) sends a given nonzero v to every nonzero vector. This is
impossible. Hence that map from F2^3 is injective and delta(U)=3. The
verifier separately stacks all component rows and checks rank three for
every one of the 168 free choices. It also checks all 4704 labelled
factor/free-map conjugations, including the seven identity labels.

Thus the column bound does not give an exact cost, or a uniform
three-factor bound, even for invertible targets over a product of copies
of the base field on only three roles. This is compatible with the exact
local-algebra result in #4787: F2^168 is not local.

## Attribution and relation to classical work

This contribution was produced by Nick Petalas. The new contribution is
the complete common-direction certificate and its sharp cost consequence
in the repository's alphabet. ToikY #4334 supplied the field-product
question, the shared-direction viewpoint and the two-role predecessor.
Nick Petalas #4243/#4265/#4276 and #4749 supplied the retained normal form,
column bound applications, general-target question and semilocal context.
The alphabet and original column expansion are Wentao Li #4099 following
#2513. Their packages are preserved unchanged.

Short linear register-update programs have a classical literature. See
Gadouleau and Riis, [Memoryless computation: new results, constructions,
and extensions, Section 3.3](https://arxiv.org/html/1111.6026#S3.SS3), and
Cameron, Fairbairn and Gadouleau,
[Computing in matrix groups without memory](https://arxiv.org/abs/1310.6009).
The general idea of short update programs and the generic 2n-1 upper-bound
phenomenon are not claimed as original here. Our finite lower certificate
ranges over every common binary covector sequence, with a common free
GL3 map absorbed at the end. It concerns simultaneous product components.

Native preparation, access, reversible restoration, precision, stock,
physical implementation and a complete recursive invoice remain unknown.
No complete multiplication theorem, supplier admission or new kappa follows.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
