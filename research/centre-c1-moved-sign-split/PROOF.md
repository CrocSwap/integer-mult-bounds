# Moved c=1 sign characters

This note records an exhaustive finite census. It is not a minimal polynomial, not an irreducibility theorem, and not a multiplication bound. The selected conditional kappa stays `781451/250000000`.

## Hypotheses

The live input is the 8-by-112 query pinned by
`research/centre-polynomial-cache-limits/`, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Its columns lie in `{-1,0,1}^8`, each has weight 4, and `R R^T = 56 I_8`. The 112 port labels are distinct odd-parity vectors in `F_2^9` and span that space. Their supports are 14 tetrads, and each tetrad carries all eight projective sign patterns.

A signed coordinate permutation acts by

    (S v)_k = eps[k] v[sigma^{-1}(k)]

and sends a column to a signed column only when `sigma` preserves the tetrad set. Scanning all `8!` permutations finds exactly 1344 tetrad automorphisms. Because every tetrad carries every projective sign pattern, each of the `1344 * 256` signed pairs preserves the projective columns.

For a Bell label `c`, the one-slot block is

    A_c = (1/4) sum_q r_q r_q^T ⊗ P_q(c)

on `C^8 ⊗ C[F_2^9]`. The factor `1/4` is not used below. If the signed permutation induces an `F_2`-orthogonal linear port map `T`, the predecessor identity gives

    (S ⊗ U_T) A_c (S ⊗ U_T)^{-1} = A_{T c}.

Thus `T c = c` is the intertwining condition for `A_c`. The trace on the 4096-dimensional block is the signed count of coordinates fixed by `sigma`, times `2` to the nullity of `T - I`.

## The residual stabilizer

`R` is the set of those `1344 * 256` signed pairs whose port map is linear, preserves the standard dot product, and fixes sector `c = 1`. The basis image of a linear map determines the map, so a candidate whose basis image moves sector 1 is excluded before the full port check. Every candidate whose basis image fixes sector 1 was checked on all 112 ports. The accepted set has order **3072**. It is closed under the signed-permutation composition law and under inversion, and the stored label map of each inverse agrees with the inverse matrix on a port basis.

`H` is the order-16 subgroup of coordinate sign patterns in `R` with positive sign on coordinate 0. It is elementary abelian. Its character dimensions on the `c = 1` block are

    {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}.

Every element of `R` normalizes `H`, so `R` permutes these sixteen characters. The trace of an element `s` on the `chi`-isotypic component is

    |H|^{-1} sum_{h in H} chi(h) tr(s h),

which is the trace of `s` restricted to that component when `s` preserves `chi`.

The predecessor involutions, already certified for the characters they preserve by the package behind PR #6944, are

| name | permutation | output signs `-1` |
|---|---|---|
| `g` | `(1 2)(5 6)` | coordinates 4 and 7 |
| `t` | `(1 5)(2 6)` | coordinates 3 and 7 |

Coordinates are numbered `0..7`. Both lie in `R`, square to the identity, and commute. `g` sends sector 3 to 343, so this pair still does not act on the `c = 3` block. On `c = 1` they preserve exactly two characters: the trivial character, of dimension 864, and the unique character of dimension 32. The other fourteen characters are the moved characters. Under `<g, t>` they form one orbit of four 432-dimensional characters, three orbits of two 192-dimensional characters, and one orbit of four 80-dimensional characters. The full group `R` fuses each dimension into a single orbit.

PR #6944 splits the two preserved characters. This note does not recompute that 216-dimensional decomposition.

## Which elements split the moved characters

An element of `R` preserves a character when conjugation by that element fixes the character. On each moved character the verifier enumerates every preserving element. Every such element has order 1, 2, 3, 4, or 6. The complex eigenvalue multiplicities are the Fourier transform of the character traces of its powers. For a real operator the non-real multiplicities come in conjugate pairs, and the denominators divide exactly. Summing the multiplicities recovers the character dimension.

The census, constant on each dimension by the transitivity just recorded, is:

Dimension 432, 768 preserving elements:

| multiplicity of `1, ζ, ζ^2, ...` | count |
|---|---:|
| `(432,)` | 1 |
| `(432, 0)` and `(0, 432)` | 15 and 16 |
| `(264, 168)` and `(168, 264)` | 96 and 96 |
| `(144, 84, 120, 84)` and `(120, 84, 144, 84)` | 96 and 96 |
| `(264, 0, 168, 0)` and `(168, 0, 264, 0)` | 48 and 48 |
| `(160, 136, 136)` | 32 |
| `(0, 136, 0, 160, 0, 136)` | 128 |
| `(160, 0, 136, 0, 136, 0)` | 96 |

Dimension 192, 512 preserving elements:

| multiplicity tuple | count |
|---|---:|
| `(192,)` | 1 |
| `(192, 0)` and `(0, 192)` | 15 and 16 |
| `(96, 96)` | 112 |
| `(120, 72)` and `(72, 120)` | 32 and 32 |
| `(48, 48, 48, 48)` | 128 |
| `(0, 96, 0, 96)` and `(96, 0, 96, 0)` | 64 and 48 |
| `(120, 0, 72, 0)` and `(72, 0, 120, 0)` | 32 and 32 |

Dimension 80, 768 preserving elements:

| multiplicity tuple | count |
|---|---:|
| `(80,)` | 1 |
| `(80, 0)` and `(0, 80)` | 15 and 16 |
| `(56, 24)` and `(24, 56)` | 96 and 96 |
| `(32, 12, 24, 12)` and `(24, 12, 32, 12)` | 96 and 96 |
| `(24, 0, 56, 0)` and `(56, 0, 24, 0)` | 48 and 48 |
| `(32, 24, 24)` | 32 |
| `(0, 24, 0, 32, 0, 24)` | 128 |
| `(32, 0, 24, 0, 24, 0)` | 96 |

Tuples of length 1, 2, 3, 4, and 6 are the eigenvalues of elements of that order, in the order `exp(2 π i k / order)`. The length-1 and the pure `± dimension` length-2 rows are the scalars `±1` on that character space. Every other row is a split.

The involution rows give the real `±1` decompositions

| dimension | character trace | invariant dimensions |
|---:|---:|---|
| 432 | `±96` | `264 + 168` |
| 192 | `0` | `96 + 96` |
| 192 | `±48` | `120 + 72` |
| 80 | `±32` | `56 + 24` |

No preserving involution has trace 0 on a 432-dimensional or 80-dimensional moved character, so none of those involutions halves the character space.

Two explicit involutions realize the balanced and the trace-96 rows. The permutation `(4 7)(5 6)` with all signs `+1` preserves two 432-dimensional characters and has character trace 96 on each, hence splits each as `264 + 168`. The permutation `(1 2)(5 6)` with signs on coordinates 0 and 3 preserves a 192-dimensional character with character trace 0, hence splits it as `96 + 96`.

## The order-4 splitter and its centralizer

Let `s` be the order-4 permutation `(0 4 3 7)(5 6)` with all signs `+1`. It lies in `R`. It preserves two characters of each moved dimension. On those characters the power traces produce the eigenvalue multiplicities

| dimension | multiplicities of `1, i, -1, -i` |
|---:|---|
| 432 | `144, 84, 120, 84` |
| 192 | `48, 48, 48, 48` |
| 80 | `32, 12, 24, 12` |

For every moved character `chi` of one of these dimensions, some element `r` in `R` carries a character preserved by `s` onto `chi`, and `r s r^{-1}` has the same power traces on `chi`. The search runs through all of `R`. These eigenspaces are invariant under `A_1` because `s` commutes with `A_1` and each spectral projection is a polynomial in `s`.

Each signed permutation in `R` is unitary: the coordinate factor is a monomial matrix with entries in `{±1, 0}`, and the port factor is a permutation matrix. `R` is finite, so each element is diagonalizable over `C` with roots of unity as eigenvalues, and the same holds on any invariant subspace. On each character preserved by `s`, the elements of `R` that preserve the character and commute with `s` form a set of order 64. Commutation with `s` preserves each eigenspace. The character-trace formula gives each of those elements a trace on each eigenspace whose absolute value equals the multiplicity, and whose value is a fourth root of unity times that multiplicity. Equality in the triangle inequality forces the element to act by that scalar. So no element of this centralizer splits any of those eigenspaces further.

The same trace computation does not see an element that preserves the character and fails to commute with `s`. Whether such an element meets one eigenspace in a smaller `A_1`-invariant subspace is open. The trace formula does not list a basis of the eigenspace.

## What this does not say

A 48-dimensional invariant subspace does not replace the degree-881 one-slot minimal polynomial, and it does not identify the characteristic polynomial of any block. The `c = 3` centre block is not a sector fixed by `g`. No basis of a moved-character eigenspace is constructed here.
