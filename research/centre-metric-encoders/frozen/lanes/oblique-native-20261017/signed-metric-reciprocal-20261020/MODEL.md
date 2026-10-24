# A dyadic signed metric on the actual112 ports

This packet gives a reciprocal response with a diagonal physical metric.
It uses eight6-mode blocks and eight8-mode blocks. The common-frame code
uses dyadic operations. It does not use an odd division.

For n in {6,8}, put m=n-4 and use coordinates (a_0,...,a_(n-3),b,c).
Define

```text
u = (1,...,1,m,0)^T,       ell = (-1,...,-1,1,0),
R = I + u ell,            P(a,b,c) = (a,c,b),
E = P R,
J = diag(1,...,1,-1/m,-1/m).
```

The product ell u is -2. Thus R^2=I and E^-1=R P. Also Ju=-ell^T
and ell J^-1 ell^T=2. Expansion gives R^T J R=J. The two last metric
entries agree, so P^T J P=J. Consequently

```text
E^T J E = J,              E^-T = J E J^-1.
```

Both E and E^-1 have zero diagonal. In full coordinates they are

```text
E:    a' = a - sum(a) + b,   b' = c,
      c' = -m sum(a) + (m+1)b;
E^-1: a' = a - sum(a) + c,   b' = -m sum(a)+(m+1)c,
      c' = b.
```

These formulas also show that E-P has rank1 and E-I has rank2 in
each block. In the latter case, the two nonzero factors are independent.
The exact112-column check gives ranks16 and32 for the full response.

## Actual physical placement

The source placement is the frozen signed-probe packet from the
new-core-transfer lane. In each large block, use the roles in this order:

```text
centre, pair_difference_a, pair_difference_b, negative_difference,
contrast, negative.
```

Use the stored port order for each small8-clique. The final two modes
are b and c. No sign vector from an earlier response is used.

Let H be the actual24 physical pair codes, with identity on the small64
ports. The physical matrices are H^-1 E H, H^-1 P H, H^-1 R H, and
H^-1 J H. The notation E,P,R,J below refers to those physical matrices.
The b modes and c modes each use a complete matching of physical pairs.
The physical metric therefore remains diagonal. Its entries are

```text
80 entries 1,    16 entries -1/2,    16 entries -1/4.
```

All pair blocks of H have H^T H=2I. This scale is constant on each
large component and commutes with the mode response. Therefore the
metric identity survives the physical change of coordinates.

Both E and E^-1 have zero diagonal in physical coordinates. No response
entry joins the two modes of the same physical pair: those modes
belong to different large blocks. Each nonzero physical response entry
joins orthogonal actual port labels. The checker verifies these facts
from the complete112 matrices and the pinned labels.

P is identity on80 physical fields and maps the other32 fields into
themselves. It is not a physical permutation. It has160 nonzero entries;
the large16-field part includes signed half entries.

The physical reflection factor is R-I=U L, where U=H^-1 u and L=ell H
block by block. Its centre Gram matrix is

```text
L J^-1 L^T = diag(4 I8, 2 I8).
```

The factor4 on the large centres comes from the physical pair code.
These entries are dyadic units. A later centre-code construction must
retain this normalization.

## Complete common-frame scalar words

The checker emits a paid pair code, the local reflection word, and the
inverse pair code. In each block the reflection word first subtracts
all a fields from b, adds that b value to each a field, negates b, and
adds all updated a fields to b. A paid signed swap then gives E.

Every word is replayed on all640 arbitrary input fields. It leaves all
528 fields outside the112-field code unchanged. The invoice is:

| Word | Real scalar primitives |
| --- | ---: |
| E, E^-1, E^-T | 3308 each |
| R | 2892 |
| P, supported on32 fields | 728 |
| J E J^-1 | 3628 |

The diagonal conversion adds320 primitives to a common-frame E code.
This is a one-bank code cost. It is not the cost to conjugate a two-bank
native shear. That cost must include both unchanged baseline banks.

No word uses an extra field or an odd denominator. Every prefix has
binary denominator height at most1 in the supplied words.

## Verification and scope

Run `python3 -I -B check_model.py --out <new-directory>`. Repeat with
`-O` and compare the decompressed response and receipt bytes.
The checks use exact fractions for all matrices, inverses, ranks,
support tests, scalar words, and costs.

This packet does not claim a native caller, a terminal decoder, helper
progress, a recursive host, or a change to the selected bound. A separate
native packet will bind this response to the actual transfer word.

The coordinating agent supplied the signed-metric E=P R identity.
The new-core-transfer lane supplied the actual pair-closed role placement.
The independent-review and controller lanes supplied the physical pair
geometry and cyclic native grammar. This lane binds these parts and
checks the complete physical response and paid scalar words. AI
assistance was used.

No PR, push, commit, or publication is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
