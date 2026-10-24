# Independent review of the phase-class reduction

Status: PASS within the stated scope.

This review binds the root proof to
`PHASE-CLASS-CAPTURE-FREEZE-20261020.json`, SHA-256
`eab4612fa42657ae663a652d9ea5afdfb8205ce5c17a706d7559c19e31ba0d6c`.
The proof hash is
`dacaf9624bb8ec32fd473570380988bacb7369126c3fe4c9fdf1afd67275ba43`.
The final source change only states the status of the separate dyadic
packet. It does not change the reviewed equations or scalar words.

## Ordered proof

Let the field space be a direct sum of copies of an arbitrary spatial
vector space. Use one anchor operator `Z_g` for each global phase class.
Let `Z` repeat that anchor on the class, and put `A=Q Z^-1`. Assume that
each field map in `A` is an admitted monomial map. A scalar matrix `T`
that preserves each class commutes with `Z`. This follows entry by entry:
the left and right anchor on every nonzero entry of `T` are equal.

For `C=T^-1 S T`, direct multiplication gives

```text
Q C Q^-1
 = A Z T^-1 S T Z^-1 A^-1
 = A T^-1 (Z S Z^-1) T A^-1.
```

If `S` reads and changes only the active set `J`, its passive block is
identity and both off-diagonal blocks are zero. Therefore
`Z S Z^-1 = Z_J S_J Z_J^-1 direct-sum I`. This proves equation (1).
It uses no commutation between `A` and any scalar code. It applies to
arbitrary input fields and does not use an owned zero field.

The same factorization with `S_J^-1` gives the inverse. It uses the same
alignment maps. If every anchor and inverse anchor has an admitted
rank-one implementation, the factorization has `2|J|` native children.
This statement does not pay for the scalar words, alignment maps, entry
frame, or exit frame.

If `K` preserves each class, then `ZK=KZ`. Thus
`Q K Q^-1 = A K A^-1`, which proves equation (2). This is an operator
identity. An implementation of `K` still needs a valid arithmetic word.
In particular, an additive coupler and an in-place nonunit matrix are
different services.

These arguments do not use a spatial dimension. They therefore prove
the stated identities at every width, subject to the same typed map
premises.

For the transported inverse, the exact order is

```text
Q C^-1 Q = (Q C^-1 Q^-1) Q^2.
```

The rightmost `Q^2` acts first. If it is an admitted translation, the
first alignment can be the ordered product `A^-1 Q^2`. No factor is
moved through another factor in this step.

## Resolved proof finding

The original negative-conjugation statement needed an extra premise.
The fact that `Q_i Z_g^-1` is monomial does not in general imply that
`Q_i^-1 Z_g` is monomial. For example, let

```text
Z = [[1, 1], [1, -1]],   A = diag(1, i),   Q = A Z.
```

Then `Q Z^-1=A` is monomial, but `Q^-1 Z=Z^-1 A^-1 Z` is dense.
The final proof requires the new alignments explicitly. In the actual
directional-phase case the phases commute, so those maps are `A_i^-1`.
The final proof states this restriction. The finding is resolved.

## Independent scalar check

The checker imports one pinned matrix helper from an earlier independent
review. It does not import the root producer or its matrix, replay, or
invoice functions. It reads the frozen rank-sixteen response and the
frozen physical pair code.

From those inputs it reconstructs the eight signed blocks of size six
and the eight blocks of size eight. It also reconstructs the fourteen
actual `q+R` classes for `R=span(30,45,75,384)`. Each class has eight
ports. The physical pair code preserves these classes.

For each source block the checker forms

```text
u = 2e-d,    v = 2d/k-e/2,    S = I+u v^T
```

and derives the inverse with the rank-one inverse formula. It checks
`1+v^T u=2(4-k)/k`, both inverse orders, and all 112 columns of the
physical capture and the response conjugation. The coded response has
no nonzero coefficient between distinct phase classes.

A distinct reverse-output interpreter checks the literal forward and
inverse words on all 640 arbitrary field inputs. It checks all 528
unchanged roles and the concatenated restoration word. It does not
infer these results from the producer receipt.

The same interpreter reconstructs the literal reduction `T`, its
inverse, and the reduced word. All 112 columns satisfy
`T C T^-1=S_reduced`. Exactly 56 coordinates are active. The passive
rows are identity, and the active rows do not read a passive input.

The exact scalar invoices are:

| Word | Old real scalar units | Extra real scans | Maximum prefix row one-norm |
| --- | ---: | --- | ---: |
| Capture | 4204 | 16 divisions by three | 12 |
| Inverse | 4204 | 16 multiplications by three | 12 |

The odd scans are separate services. A dyadic matrix entry does not by
itself make a nonunit determinant available from old unit scalings.
The inverse scan invoice is therefore necessary in this baseline.

## Scope

The conditional 112-child count uses the rank-four frame for `R`. It
does not apply to the current rank-one `W45` exit. The root note records
the bridge lane's finding that all 56 proposed pair ratios have rank
two in that exit. This review does not repeat that physical phase audit.

No native recipe, frame preparation, frame removal, helper completion,
routed caller, terminal decoder, or recursive supplier is verified here.
The review establishes the general ordered theorem and the actual
rational scalar baseline. The separate dyadic capture has its own
frozen packet and distinct peer review.

AI assistance was used. No PR, push, or publication is authorized.
Before any PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
