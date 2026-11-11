# The ++ 216-space is reducible under A_1

This is a finite exact certificate for one joint eigenspace of the historical
one-slot doubled centre block at Bell label `c=1`. It is not a characteristic
polynomial, not an annihilator of the full one-slot operator, and not a
multiplication bound.

## Operator and the two known involutions

The input is the 8-by-112 query retained by
`research/centre-polynomial-cache-limits/`. Its columns lie in `{-1,0,1}^8`,
each has weight 4, and `R R^T = 56 I_8`. The 112 port labels are distinct odd
vectors in `F_2^9`.

For a Bell label `c`, the block is

    A_c = (1/4) sum_q r_q r_q^T ⊗ P_q(c)

on `C^8 ⊗ C[F_2^9]`. A signed coordinate permutation `S`, with induced
orthogonal port map `T`, satisfies

    (S ⊗ U_T) A_c (S ⊗ U_T)^{-1} = A_{T c},

where `U_T` sends the address `a` to `T a`. Thus `T c = c` if and only if the
signed permutation commutes with `A_c`. The trace on the 4096-dimensional
block is `tr(S) · 2^{nullity(T-I)}`, and `tr(S)` sums the output signs on the
coordinates fixed by the permutation.

PR #6944, continuing JoyboyBrian's handoff in Discussion #1166, comment
19144258, exhibits two commuting involutions that fix `c=1`:

| name | permutation | output signs |
|---|---|---|
| `g` | `(1 2)(5 6)` | minus on coordinates 4 and 7 |
| `t` | `(1 5)(2 6)` | minus on coordinates 3 and 7 |

The pure sign stabilizer `H` of `c=1`, with positive sign on coordinate 0,
has order 16. Its trivial character space `V` has dimension 864. Both
involutions preserve `V`, and the four joint `(±1,±1)` spaces inside `V` each
have dimension 216. This package recomputes that anchor. It does not recompute
the `c=3` or `c=128` histograms from #6944.

Write `E_{α,β}` for the joint space on which `g` acts by `α` and `t` acts by
`β`. The question answered here is whether `E_{1,1}` is irreducible under
`A_1`.

## The signed-permutation group is finite and completely enumerated

Let `W` be the hyperoctahedral group of all signed permutations of the eight
coordinates, of order `8! · 2^8 = 10321920`. Let `A` be the subset that sends
every query column to a scalar multiple of a query column and induces an
orthogonal linear map of the port space.

The 13 signed permutations used as generators in
`research/exact-one-slot-gram/model.py` lie in `A`: seven sign flips on
coordinates `1..7`, and the six coordinate permutations listed there. Their
generated subgroup has order `344064`. The left cosets of this subgroup in
`W` number 30, and `344064 · 30 = 10321920`. Exactly one of those cosets
preserves the column lines, namely the subgroup itself. Therefore that
subgroup is all of `A`.

This is an exhaustive census of a finite set. The completeness argument is
the coset decomposition of `W`, not a search that stopped after failing to
find another generator. Every element of `A` is a product of the 13
generators, so every element induces an orthogonal linear port map.

The stabilizer `A(c=1) = {s ∈ A : T_s(1) = 1}` has order 3072. These are
exactly the signed coordinate permutations that commute with `A_1`.

## Centralizer census: commuting with both involutions does not split a block

Let `C` be the centralizer of `{g,t}` in `A(c=1)`. The census finds
`|C| = 16`. Every element of `C` is an involution, and on each of the four
spaces `E_{α,β}` its trace is `±216`. A finite-order operator with trace
equal to `± dim` acts by that scalar. Consequently every element of `C` acts
on each 216-dimensional joint space by `±I`.

No signed coordinate permutation that commutes with both `g` and `t` cuts any
of those four spaces. The earlier observation that a third commuting
involution had not been found is replaced here by this complete count. That
count is not a proof that `A_1` is irreducible on `E_{1,1}`.

## Normalizer: a dihedral action splits the ++ space

Let `N` be the normalizer of the Klein group `{1,g,t,gt}` inside `A(c=1)`.
The census finds `|N| = 96`. Every element of `N` also normalizes `H`. Two
explicit elements of `N` are

| name | permutation | output signs |
|---|---|---|
| `u` | `(4 7)(5 6)` | all plus |
| `r` | the order-6 word below | minus on coordinates 0 and 7 |

The stored inverse permutation and output signs of `r` are

    inv = (0, 1, 6, 7, 3, 2, 5, 4),
    eps = (-1, 1, 1, 1, 1, 1, 1, -1),

with `(S v)_k = eps[k] v[inv[k]]`. They satisfy `u^2 = 1`, `r^6 = 1`, and
`u r u^{-1} = r^{-1}`. Thus `r` and `u` present a dihedral group of order 12.

Conjugation by `r` fixes the trivial character of `{g,t}` and cycles the
other three characters. Conjugation by `u` fixes the two characters with
`g = +1` and swaps the two characters with `g = -1`. In particular both
preserve `E_{1,1}`. The kernel of the action of `N` on `E_{1,1}` has order
8, and the image is this dihedral group of order 12. The twelve words
`r^k` and `r^k u` are distinct modulo the kernel and exhaust the image.

Their traces on `E_{1,1}` are

| word | `1` | `r` | `r^2` | `r^3` | `r^4` | `r^5` |
|---|---:|---:|---:|---:|---:|---:|
| trace | 216 | -24 | 24 | -216 | 24 | -24 |

and the reflections `r^k u` have traces `72, -72, 72, -72, 72, -72`.

The rational irreducible characters of the dihedral group of order 12 in
which the central element `r^3` can act by `-1` are two linear characters
and one two-dimensional character. Evaluating the inner products against
these traces gives multiplicities `8`, `80`, and `64` respectively. The two
linear characters in which `r` acts by `+1`, and the two-dimensional
character in which `r^3` acts by `+1`, have multiplicity 0. The dimensions
`8 + 80 + 2·64 = 216` therefore exhaust `E_{1,1}`.

Each group element is the restriction of a signed permutation that commutes
with `A_1` and preserves `E_{1,1}`. The isotypic projector of a linear
character is the average of `±` those operators. Its trace equals the
multiplicity, so the corresponding rational image has that dimension and is
invariant under `A_1`. The same holds for the 128-dimensional isotypic
component of the two-dimensional character.

Thus `E_{1,1}` has rational `A_1`-invariant subspaces of dimensions **8**,
**80**, and **128**. It is reducible under `A_1`.

The same traces give a coarser rational splitting that does not need the
whole character table. The involution `u` has trace 72 on `E_{1,1}`, so its
`±1` eigenspaces there have dimensions `(216±72)/2`, that is 144 and 72.
Both are rational and `A_1`-invariant. The multiplicity-8 character takes
the value `-1` on `u`, so the 8-dimensional summand lies in the
72-dimensional eigenspace.

## The other three 216-spaces

`u` also preserves `E_{1,-1}` and has trace 72 there, so that space likewise
splits as 72+144. The element `r u` preserves `E_{-1,-1}` and has trace -72
there, with the same dimensions. The conjugate `r u r^{-1}` preserves
`E_{-1,1}` and has trace `±72` there. So each of the four joint spaces has a
proper rational `A_1`-invariant subspace of dimension 72.

Only `E_{1,1}` carries the full dihedral image. The order-6 element `r` does
not preserve the other three spaces, and this certificate does not give them
an 8-dimensional isotypic summand.

## Relation to the characteristic polynomial

The fork branch `cursor/a1-joint-216-charpoly-0702` at
`306f791048636c7dc91c83ecb8ae6e730908042c` computes the characteristic
polynomial of this same 216-dimensional space. Its recorded factorization
includes the distinct linear factors `x` and `x-2`, which already shows that
the space is reducible under `A_1`, without naming a subspace. This
certificate does not recompute that polynomial and does not claim that the
8-dimensional symmetry summand is one of those factors. The two arguments
are independent: one is a factored characteristic polynomial, and the other
is an explicit signed-permutation action.

## What this does not say

The centralizer census proves that no residual signed permutation commuting
with both `g` and `t` splits these spaces. It does not prove irreducibility.
The normalizer supplies an independent reducibility proof for `E_{1,1}`.

No characteristic polynomial of `A_1` on a 216-space, or on the 8-dimensional
summand, is computed. The certificate does not list a basis of that summand.
It does not claim that an element of `A(c=1)` outside `N` fails to preserve
the 8-dimensional summand. The degree-881 one-slot annihilator is untouched:
the minimal polynomial of the full operator is an lcm over invariant pieces,
and a subspace of one piece does not replace that polynomial.

The selected conditional kappa stays `781451/250000000`.
