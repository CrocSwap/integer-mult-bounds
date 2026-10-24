# A local rank bound for all common-line products

This note gives a local bound. It does not price the complete program.
It does not require one fixed line or one binary bit per wire component.

Let `A subset U subset F_2^n`. Write `e=dim(U)`. Let `s` be the rank of
the standard dot product restricted to `A`. Each endpoint of the native
descent from the canonical frame `T_U` to the identity can have any gauge
that is a product of translation-line operators `C_a`, with `a in A`.
The changed native rank is at least `e-s`.

## Proof

The binary action of `C_a` on a Pauli label is

    (x,z) -> (x+a(a dot z),z).

The product, inverse, and relative product of these gauges therefore have
the form

    S_B(x,z)=(x+Bz,z),  B=sum_j a_j a_j^T,  a_j in A.

Thus `im(B) subset A` and `B(A-perp)=0`. On `A`, the map `B` factors
through the dot-product map from `A` to its dual. Therefore
`rank(B|A)<=s`.

The two binary labels for the changed descent can be compared as

    L_U={(u,u+v): u in U, v in U-perp},
    S_B L_0={(Bz,z): z in F_2^n}.

An element of their intersection satisfies `z+Bz=w in U-perp`.
Put `u=Bz`. Since `im(B) subset A subset U` and `B(U-perp)=0`, this is
equivalent to

    z=w+u,  w in U-perp,  u in U,  Bu=u.

This representation is unique. Indeed, a fixed vector of `B` that lies
in `U-perp` is zero. The intersection has dimension

    n-e+dim ker(I-B|U).

Each fixed vector belongs to `A`. The fixed space therefore has dimension
at most `rank(B|A)<=s`. Since the native rank is `n` minus the intersection
dimension, the exact formula and bound are

    r=e-dim ker(I-B|U) >= e-s.

The comparison depends only on the relative gauge. It therefore applies
when both endpoint gauges are arbitrary products from this group.

## Application to the eight actual centres

At source commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, the common
intersection of centre frames 415 through 422 has basis

    30, 45, 75, 128, 256.

Its Gram matrix has binary rows `0,0,0,8,16`, so its rank is two. Each
centre has dimension eight. Thus every centre descent has rank at least
six under arbitrary common-line product gauges. The product
`C_128 C_256` attains rank six at each of the eight centres.

The source-derived frame intersection, Gram rank, and eight sharp ranks
were checked with the pinned source reader used by `verify_odd_paths.py`.
Separate-agent review checked the proof and repeated the source checks
with symplectic pairing matrices. Its receipt is
`encoded-controller/review/COMMON-PRODUCT-RANK-REVIEW.json`. This bound
does not exclude a complete-cost gain that leaves rank-six centre children,
or a gauge that uses lines outside the common intersection.

Before any PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
This note was prepared with OpenAI Codex assistance.
