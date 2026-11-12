# Signed permutations outside the {g,t} normalizer on the ++ 216-space

This is an exhaustive finite census, together with one explicit witness, for
the trivial-character `(+1,+1)` joint space of the historical one-slot doubled
centre block at Bell label `c=1`. It is not a characteristic polynomial, not
an annihilator of the full one-slot operator, and not a multiplication bound.

The selected conditional kappa stays `781451/250000000`.

## Operators

The input is the 8-by-112 query retained by
`research/centre-polynomial-cache-limits/`. Its columns lie in `{-1,0,1}^8`,
each has weight 4, and `R R^T = 56 I_8`. The 112 port labels are distinct odd
vectors in `F_2^9`.

A signed coordinate permutation acts by `(S v)_k = eps[k] v[inv[k]]` and by
the linear port map `T` that carries each port to the port of its image
column. On `R^8 ⊗ R[F_2^9]`, of dimension 4096, the operator is `S ⊗ U_T`.
Both factors are orthogonal, so the operator is orthogonal. Its trace is

    tr(S) · 2^{nullity(T - I)},

where `tr(S)` sums the output signs on the coordinates fixed by the
permutation. This is the trace formula used by PR #6944 and PR #7008.

PR #6944 fixes two commuting involutions that preserve sector `c=1`:

| name | permutation | output signs |
|---|---|---|
| `g` | `(1 2)(5 6)` | minus on coordinates 4 and 7 |
| `t` | `(1 5)(2 6)` | minus on coordinates 3 and 7 |

PR #7008 lets `N` be the normalizer, inside the `c=1` stabilizer, of the
Klein group `{1, g, t, gt}`. That package proves `|N| = 96` and that the
image of `N` on the trivial-character `(+1,+1)` space `E_{1,1}` is the
dihedral group of order 12. This note uses that same normalizer. It does not
reprove the dihedral character table.

## The group is finite and completely enumerated

Let `W` be the hyperoctahedral group of all signed permutations of the eight
coordinates, of order `8! · 2^8 = 10321920`. Let `A` be the subset that sends
every query column to a scalar multiple of a query column.

The 13 signed permutations used as generators in
`research/exact-one-slot-gram/model.py` lie in `A`, and each induces a linear
port map that preserves the mod-2 dot product. Their generated subgroup has
order `344064`. The left cosets of this subgroup in `W` number 30, and
`344064 · 30 = 10321920`. Exactly one of those cosets preserves the column
lines, namely the subgroup itself. Therefore the subgroup is all of `A`.
Every element of `A` is a product of orthogonal generators, so every element
induces an orthogonal linear port map.

This is an exhaustive census of a finite set. The completeness argument is
the coset decomposition of `W`, not a search that stopped early. The
stabilizer `A(c=1) = {s ∈ A : T_s(1) = 1}` has order 3072. These are exactly
the signed coordinate permutations that commute with the `c=1` block.

## The 216-space as the invariants of a group of order 64

Let `H` be the group of coordinate sign patterns in `A(c=1)` with positive
sign on coordinate 0. It has order 16. Its character dimensions are the
histogram `{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}` recomputed by the
verifier. The trivial character space has dimension 864.

The 64 products `k h` with `k ∈ {1, g, t, gt}` and `h ∈ H` are distinct and
form a group `M`. The average of their traces is 216, so the subspace `E` of
`M`-invariants has dimension 216. The same 216 is the joint `(+1,+1)`
dimension

    (tr_V(1) + tr_V(g) + tr_V(t) + tr_V(gt)) / 4,

where `tr_V` is the trace on the trivial character space of `H`, and
`tr_V(1) = 864`. Every vector of `E_{1,1}` is fixed by `H`, by `g`, and by
`t`, hence by every product of those operators, hence by `M`. Thus
`E_{1,1} ⊆ E`. The dimensions agree, so `E = E_{1,1}`.

Let `P = (1/|M|) ∑_{m ∈ M} m`. This is the orthogonal projector onto `E`:
it is the standard invariant projector, and `P` is symmetric because `M` is
a group and every element satisfies `m^{-1} = m^T`.

## Preservation and scalar action

For `s ∈ A`, write `Q = s P s^{-1}`, the orthogonal projector onto `sE`.
Then

    tr(P Q) = (1/|M|^2) ∑_{a,b ∈ M} tr(a s b s^{-1}).

The operator `P - Q` is symmetric and

    tr((P - Q)^2) = 2 · 216 - 2 tr(P Q).

If the correlation `tr(P Q)` equals 216, then `P = Q`, so `sE = E`. If `s`
preserves `E`, the restriction `s|_E` is orthogonal. Its trace equals
`tr(s P) = (1/|M|) ∑_{m ∈ M} tr(m s)`. For an orthonormal basis `w_i` of `E`,

    ∑_i ⟨s w_i, w_i⟩ = tr(s|_E),

and Cauchy-Schwarz gives `⟨s w_i, w_i⟩ ≤ 1`, with equality if and only if
`s w_i = w_i`. Therefore `tr(s|_E) = 216` if and only if `s|_E = I`, and
`tr(s|_E) = -216` if and only if `s|_E = -I`. Any other trace means that the
action on `E` is not scalar.

These identities are exact integer arithmetic. The verifier rejects a sum
that is not divisible by `|M|` or `|M|^2`.

## Census

The verifier evaluates the correlation and the trace on `E` for every one of
the 3072 elements of `A(c=1)`.

| set | order | traces on `E` |
|---|---:|---|
| elements with `sE = E` | 768 | `216: 64`, `-216: 64`, `72: 192`, `-72: 192`, `24: 128`, `-24: 128` |
| `N` | 96 | `216: 8`, `-216: 8`, `72: 24`, `-72: 24`, `24: 16`, `-24: 16` |
| preservers outside `N` | 672 | `216: 56`, `-216: 56`, `72: 168`, `-72: 168`, `24: 112`, `-24: 112` |

Every element of `N` preserves `E`. Every correlation on `A(c=1)` is either
`0` or `216`: a stabilizer element either preserves `E` or meets it
orthogonally. Of the 672 preservers outside `N`, the 112 elements of trace
`±216` act by `±I`. The other **560** act non-scalarly.

The setwise stabilizer `Stab = {s ∈ A(c=1) : sE = E}` is a subgroup of order
768. Its kernel on `E`, the elements acting by `I`, is the set of preservers
of trace 216 and has order 64. The image in `GL(E)` therefore has order
`768 / 64 = 12`. The same count inside `N` gives image order `96 / 8 = 12`.
The image of `N` is contained in the image of `Stab`, so the two images are
equal. Every signed permutation in `A(c=1)` that preserves `E` acts on `E`
through the dihedral image of order 12 already produced by `N`. The 560
elements outside `N` supply further lifts of those same twelve operators.
They do not enlarge the signed-permutation action on `E`, and they do not
cut an `A_1`-invariant subspace beyond the rational isotypic decomposition
certified by PR #7008.

## Witness

Let `h` be the sign flip of coordinate 1, with output signs
`(1, -1, 1, 1, 1, 1, 1, 1)` and trivial permutation. Let `u` be the
involution `(4 7)(5 6)` with all output signs positive, the normalizer
element used by PR #7008. The witness is

    w = u h = h u.

Its permutation is `(4 7)(5 6)` and its only negative output sign is on
coordinate 1. It is an involution. It lies in `A(c=1)`, it does not
normalize `{1, g, t, gt}`, it preserves `E`, and its trace on `E` is 72.

The same sign `h` lies in `H`, preserves `E`, and has trace 216, so
`h|_E = I`. Therefore `w|_E = u|_E`. The `±1` eigenspaces of `w` on `E` are
the same 144- and 72-dimensional spaces already cut by `u`. The new fact is
that this operator is also induced by a signed permutation outside `N`.

The conjugate `h g h^{-1}` has the same coordinate permutation as `g` and
output signs minus on coordinates 1, 2, 4, and 7. That signed permutation is
not in `{1, g, t, gt}`, so `h` itself lies outside `N`. Since `u ∈ N` and
`N` is a group, `w = u h` lies outside `N` as well. The verifier checks the
conjugate and the normalizer membership directly.

## What this does not say

The census is restricted to `A(c=1)` and to the one subspace `E_{1,1}`. It
does not claim that an arbitrary orthogonal operator outside `A` fails to
preserve `E`. It does not decide whether an element of `A(c=1)` that moves
`E` can preserve the 8-dimensional dihedral isotypic summand inside `E` and
act non-scalarly there. Elements that do preserve `E` act through the
dihedral image; on a linear-character isotypic component that image acts by
scalars, but this note does not rebuild that 8-dimensional projector and does
not decide irreducibility of the summand under `A_1`.

No characteristic polynomial is computed. The degree-881 one-slot annihilator
is untouched. The selected conditional kappa stays `781451/250000000`.
