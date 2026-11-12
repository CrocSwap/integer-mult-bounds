# A c=1 stabilizer element carrying the 8-dimensional joint basis

This note answers the transporter question left open by the characteristic
polynomial of one 8-dimensional `c=1` joint eigenspace. The selected
conditional kappa stays `781451/250000000`. Nothing here recomputes that
polynomial, the degree-216 polynomial, or a nullity on the 216-by-216 matrix.

Two claim types are used.

- A **proof of one finite identity** exhibits one signed permutation, checks
  that it lies in the `c=1` stabilizer and outside `<H, g, t>`, and checks
  that it carries each pinned basis vector onto the named basis vector of
  another joint space.
- An **exhaustive finite census** classifies every element of the
  order-3072 stabilizer. The set, the enumeration, and the reason the list
  is complete are stated below. It is not a sample. It is not a statement
  about signed permutations outside this stabilizer, and it is not an
  unrestricted nonexistence theorem.

## Operators and the inherited basis

The input is the pinned 8-by-112 query, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Its columns lie in `{-1,0,1}^8`, each has weight 4, and `R R^T = 56 I_8`.
The 112 port labels are distinct odd-parity vectors in `F_2^9`. Coordinates
`0..7` are the vectors of `F_2^3`.

A signed coordinate permutation acts by `(S v)_k = eps[k] v[sigma^{-1}(k)]`
and by the port map `T` induced on `F_2^9`. Predecessor packages record that
a symmetry satisfies `(S ⊗ U_T) A_c (S ⊗ U_T)^{-1} = A_{T c}`, so this note
uses the same cut `T(1) = 1` for the `c=1` stabilizer. It does not replay
that conjugation on all 4096 coordinates. It does apply `B = 4 A_1` directly
to the two joint bases below and checks that the exhibited element
intertwines those two restrictions.

`H` is the order-16 group of diagonal signs supported on coordinates
`{1,2,5,6}`, with positive sign on coordinate 0. The character is

```text
chi(eps) = eps[1] eps[2] eps[5] eps[6].
```

The involutions are `g = (1 2)(5 6)` with minus signs on coordinates 4 and 7,
and `t = (1 5)(2 6)` with minus signs on coordinates 3 and 7. Both preserve
sector 1. On the `chi`-isotypic component their joint spaces have dimension
8. The `(+1,+1)` space is supported on coordinate 0. Its canonical basis has
pivots

```text
128, 129, 134, 135, 170, 171, 172, 173
```

and its first vector is

```text
(128, +), (158, +), (230, +), (248, +), (256, -), (286, -), (358, -), (376, -).
```

These are the basis and the support coordinates recorded for this space.
The verifier rebuilds them from the eigenvalue equations. The trace formula
on `H`, twisted by `chi`, gives dimension 32, and the joint formula gives
dimension 8 for each sign pair, so each explicit basis is the whole joint
space. `chi` is `-1` on the coordinate-1 sign, so this is not the trivial
character. The four bases have disjoint supports and together occupy 256
coordinates.

Let `L = {0,3,4,7} = {x in F_2^3 : x_0 = x_1}`. The four joint spaces are
supported on the four points of `L`:

| `(g, t)` | support |
|---|---:|
| `(+1,+1)` | 0 |
| `(+1,-1)` | 3 |
| `(-1,+1)` | 4 |
| `(-1,-1)` | 7 |

In each ordered basis, the matrix of `B = 4 A_1` on the `(+1,+1)` space and
on the `(+1,-1)` space is the same integer matrix

```text
  4  -4   0   0   0   0   0   0
 -4   4   0   0   0   0   0   0
  0   0  -4  -4   0   0   0   0
  0   0  -4  -4   0   0   0   0
  0   0   0   0   4  -4   0   0
  0   0   0   0  -4   4   0   0
  0   0   0   0   0   0  -4  -4
  0   0   0   0   0   0  -4  -4
```

The verifier checks both restrictions by applying `B` to the eight basis
vectors and reading coefficients at the pivots. It also checks that those
eight coefficients reconstruct the image, so `B` does not leave the span.

## The stabilizer is the signed setwise stabilizer of L

**Census of the automorphism group.** All `8! = 40320` coordinate
permutations were tested. The permutations that preserve the 14 column
supports are exactly the affine maps `x ↦ M x + b`, where `M` runs through
`GL(3,2)` and `b` runs through `F_2^3`. So the support automorphism group is
`AGL(3,2)`, of order 1344.

A signed coordinate permutation preserves the projective column set only if
its underlying permutation preserves those planes. Every symmetry therefore
has underlying permutation in `AGL(3,2)`, and the symmetry group has order
at most `1344 · 256 = 344064`.

**The signed affine maps are symmetries.** The eight coordinate sign flips,
the shear `(1 3)(5 7)`, the 7-cycle `(1 2 4 3 6 7 5)`, and the translations
by `1`, `2` and `4` induce orthogonal linear port maps, checked on all 112
ports. The five permutations generate `AGL(3,2)`. An arbitrary sign pattern placed
to the left of an unsigned affine permutation is that permutation with those
output signs, so every signed affine map is a product of these generators in
the hyperoctahedral group. The port of a composite column image is the
composite of the ports, and the verifier checks that the label maps multiply
on every generator pair. A product of symmetries is a symmetry. The symmetry
group is therefore the whole signed affine group.

**Stabilizer of sector 1.** The generator orbit of the address `1` has size
112, so the stabilizer has order `344064 / 112 = 3072`. Separately, `T(1)`
was evaluated for every one of the 344064 signed affine maps. Exactly 3072
give `T(1) = 1`, and each of the 112 orbit labels has a fiber of that same
size. Each of those 3072 elements was checked on all 112 ports, and each
label map is orthogonal and invertible. The orbit-stabilizer count and the
rebuilt list agree, so the list is the whole stabilizer.

The underlying permutations in that list are exactly the 96 affine maps that
preserve `L` setwise. Setwise preservation of one 4-point linear subspace is
a different count from the port scan; the two sets are equal, not merely the
same size. Each of the 96 permutations has exactly 32 sign patterns in the
stabilizer.

## One explicit transporter

Take `sigma = (0 3)(5 6)` with every sign equal to `+1`. As an image tuple,

```text
sigma = (3, 1, 2, 0, 4, 6, 5, 7).
```

This permutation preserves `L` and sends `0` to `3`. It is one of the 3072
stabilizer elements. The 32 signs that accompany it are exactly the patterns
that are constant on `L` and arbitrary on the complement `{1,2,5,6}`. The
all-positive pattern is the constant value `+1`. The single minus sign on
coordinate 0 is not in that fiber; the verifier rejects it.

The group `<H, g, t>` is the set of 64 products of `H` with `{1, g, t, gt}`.
The verifier multiplies all 64 · 64 pairs and checks closure, and checks that
every product lies in the stabilizer. All four permutations fix coordinate 0,
and every diagonal sign fixes every coordinate, so every element of this
group satisfies `sigma(0) = 0`. The witness sends `0` to `3`, so it lies
outside `<H, g, t>`.

On each of the eight canonical `(+1,+1)` basis vectors, the witness produces
exactly the canonical `(+1,-1)` basis vector with the same address
coefficients, supported on coordinate 3. In particular the pivots land on

```text
1664, 1665, 1670, 1671, 1706, 1707, 1708, 1709,
```

which are those same addresses shifted by `3 · 512`. Each image vector
satisfies the `chi` eigenvalue equations and the `(g, t) = (+1,-1)`
equations. The witness is invertible, as is every stabilizer element, so the
image of the 8-dimensional space is the whole `(+1,-1)` joint space.

Because the ordered bases correspond index for index and the two matrices of
`B` are equal, this element intertwines the two restrictions of `B`. That is
why those two joint spaces have the same matrix, not merely the same
characteristic polynomial. The polynomial itself is not recomputed here.

## Census of the whole stabilizer

Every one of the 3072 elements was applied to the eight basis vectors. Two
independent tests were required to agree:

- the transported address patterns are exactly the eight patterns of the
  joint space supported on `sigma(0)`;
- each image vector satisfies the `chi` equations and the `(g, t)` equations
  of that same joint space.

Both tests pass for every element, and `sigma(0)` lands in `L` for every
element. The fibers have size 768:

| image of coordinate 0 | joint signs | elements | of which outside `<H,g,t>` |
|---:|---|---:|---:|
| 0 | `(+1,+1)` | 768 | 704 |
| 3 | `(+1,-1)` | 768 | 768 |
| 4 | `(-1,+1)` | 768 | 768 |
| 7 | `(-1,-1)` | 768 | 768 |

The 64-element group sits entirely in the first row. The other three rows,
2304 elements, are transporters onto a different joint space, and every one
of them lies outside `<H, g, t>`. The witness above is one element of the
second row.

The same partition shows that lying outside `<H, g, t>` does not by itself
move the basis: 704 further stabilizer elements preserve the `(+1,+1)` space.
Their action on that space is not computed here.

## Evidence class

The witness is a proof of one finite identity: one named signed permutation,
checked against the rebuilt basis and the rebuilt stabilizer equations. The
fiber counts are an exhaustive census of a set of order 3072. The
completeness argument is the identification of the symmetry group with the
signed affine group, the orbit-stabilizer count, and the agreement of that
count with the `T(1) = 1` scan. No step is a partial search. The result does
not constrain operators outside this signed-permutation stabilizer, and it
does not change kappa.

## What this does not say

The degree-8 characteristic polynomial and the degree-216 characteristic
polynomial are left as recorded. The geometric multiplicity of any eigenvalue
on the 216-by-216 matrix is not computed. The 8-dimensional dihedral
isotypic summand inside the trivial-character 216-space is a different
subspace; this basis lies in `chi` and is not that summand. A signed
permutation that does not preserve the 14 planes is not a symmetry of this
query, but this census does not speak about operators outside the signed
affine group.
