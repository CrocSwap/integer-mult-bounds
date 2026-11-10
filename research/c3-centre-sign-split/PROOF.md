# Signed permutations that split every c=3 character

This note answers one question left open by the c=1/c=128 sign-character
certificate: which residual signed permutations split every sign character of
the `c=3` centre block. The selected conditional kappa stays
`781451/250000000`. Nothing here is a minimal polynomial, an irreducibility
theorem, or a search that was stopped early.

Two claim types are used, and they are not interchangeable.

- A **proof** is an identity or a group-generation argument checked on a
  generating set, together with the trace formula for commuting involutions.
- An **exhaustive finite census** lists every element of a named finite set.
  The set, the enumeration, and the reason the list is complete are stated
  below. It is not a sample and it is not a proof that no symmetry outside
  this signed-permutation group can split the spaces.

## Operators

The input is the pinned 8-by-112 query, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Its columns lie in `{-1,0,1}^8`, each has weight 4, and `R R^T = 56 I_8`.
The 112 port labels are distinct odd-parity vectors in `F_2^9`.

Coordinates `0..7` are the vectors of `F_2^3` under integer xor. The 14
column supports are exactly the affine planes. On each plane all eight
projective sign patterns occur once. A signed coordinate permutation therefore
preserves the projective column set if and only if its underlying permutation
preserves those planes.

The signed permutation acts by `(S v)_k = eps[k] v[sigma^{-1}(k)]`. When the
image of every column is a projective column and the induced port map `T` is
linear and orthogonal on `F_2^9`, the predecessor intertwining identity gives

    (S ⊗ U_T) A_c (S ⊗ U_T)^{-1} = A_{T c}.

Thus `S` commutes with `A_c` exactly when `T c = c`. Sector `c=3` is the
subject of this note. The factor `1/4` in `A_c` is not used.

## The symmetry group is the full signed affine group

**Census of the automorphism group.** All `8! = 40320` coordinate permutations
were tested. The permutations that preserve the 14 planes are exactly the
1344 affine maps `x ↦ M x + b`, where `M` runs through the 168 invertible
3-by-3 matrices over `F_2` and `b` runs through `F_2^3`. So the support
automorphism group is `AGL(3,2)`.

**Proof that every signed affine map is a symmetry.** The eight coordinate
sign flips, the translations by `1`, `2` and `4`, the shear `(1 3)(5 7)`,
and the 7-cycle `(1 2 4 3 6 7 5)` are symmetries: each induces an orthogonal
linear port map. Breadth-first multiplication shows that the five permutations
generate all 1344 affine maps. Every sign pattern is a product of coordinate
flips, and the composition rule

    sigma = sigma_left ∘ sigma_right,
    eps[k] = eps_left[k] · eps_right[sigma_left^{-1}(k)]

writes an arbitrary signed affine map as such a product. The set of symmetries
is closed under composition because a product of orthogonal linear port maps
is an orthogonal linear port map. It is therefore the whole semidirect product,
of order `1344 · 256 = 344064`. It is not larger: any symmetry has to preserve
the planes. Generator products were rebuilt from the query, and their label
maps multiply.

## Stabilizer of sector 3

**Proof of the order, then a matching census.** The label maps of the
generators act on `F_2^9`. The orbit of the address `3` has size 112, so the
stabilizer has order `344064 / 112 = 3072`.

Separately, `T(3)` was evaluated for every one of the 344064 signed affine
maps. Exactly 3072 give `T(3) = 3`, and each of the 112 orbit labels has a
fiber of that same size. Each of those 3072 elements was rebuilt with the
full 112-port linearity and orthogonality check. The orbit-stabilizer count
and the rebuilt list agree, so the list is the whole stabilizer.

## Sign characters

The diagonal symmetries that fix sector 3 were read off that list. There are
32. Their signs are constant on the even coordinates `{0,2,4,6}` and arbitrary
on the odd coordinates `{1,3,5,7}`. The 16 with positive even signs form the
group `H` used for characters; coordinate 0 is even, so these are exactly the
patterns with positive sign on coordinate 0. This is the same order-16
stabilizer recorded for `c=3` by the predecessor certificate.

The trace of a symmetry on the 4096-dimensional block is the signed count of
fixed coordinates times the number of fixed addresses of `T`. The dimension of
the `chi`-isotypic component is `|H|^{-1} ∑_{h in H} chi(h) tr(h)`. Recomputing
it gives

    {864: 1, 432: 4, 192: 6, 80: 4, 32: 1},

indexed by the `F_2^4` character on coordinates `(1,3,5,7)`. Weight 0 has
dimension 864, weight 1 has 432, weight 2 has 192, weight 3 has 80, and weight
4 has 32. The dimensions are positive and sum to 4096.

Each of the 32 diagonal symmetries is an involution. On every character space
its trace equals ± the dimension. An involution is diagonalizable over `C`,
so each of these 32 operators acts by that scalar. None of them splits a
character.

## Which stabilizer elements preserve every character

Conjugation inside the signed permutation group sends a diagonal sign `d` to
the diagonal sign `k ↦ d(sigma^{-1}(k))`. The output signs cancel. For an
element of the sector-3 stabilizer, the conjugate of each element of `H` lands
in the 32 diagonal symmetries that fix sector 3. Those act by known scalars
`s(k, chi) = ±1`.

The conjugate `g h g^{-1}` acts on the `chi`-space by `chi(h)` for every
`h` and every `chi` if and only if `g` preserves every character space. The
verifier applies that test to all 3072 stabilizer elements. Exactly 128 pass.
Set equality, not a sample, identifies them with the 128 elements described
next.

## The 96 involutions that split every character

**Census inside `AGL(3,2)`.** Exactly four affine maps fix the four odd
coordinates: the identity and the three even double transpositions

    (0 2)(4 6),    (0 4)(2 6),    (0 6)(2 4).

The odd points are an affine plane, so this is the full pointwise stabilizer
of that plane in `AGL(3,2)`.

For each of those three permutations, the signs that put the signed map in
the sector-3 stabilizer are exactly the 32 patterns in which each 2-cycle is
uniformly signed, the two cycles carry opposite signs, and the four odd signs
are free. That is 96 elements. All 96 are involutions. A pattern that puts the
same sign on both cycles, including minus signs on all four even coordinates,
is still a symmetry but sends sector 3 elsewhere; the all-even-minus pattern
on `(0 2)(4 6)` sends it to 48.

On a character of weight `w` every one of the 96 has absolute trace
`0, 96, 0, 32, 0` for `w = 0, 1, 2, 3, 4`. Each absolute value is strictly
smaller than the character dimension, so both eigenvalues occur:

| weight | dimension | ±1 dimensions |
|---:|---:|---|
| 0 | 864 | 432 + 432 |
| 1 | 432 | 264 + 168 |
| 2 | 192 | 96 + 96 |
| 3 | 80 | 56 + 24 |
| 4 | 32 | 16 + 16 |

Each involution commutes with `A_3`, and its spectral projections are
polynomials in the involution, so both eigenspaces are `A_3`-invariant.
This is the list of residual signed permutations that split every c=3
character. The other 32 all-character preservers are the diagonal signs,
and they do not split any character. No other element of the order-3072
stabilizer preserves every character.

## The four-way pairs are one Klein group modulo signs

**Census of the 128-element preserver set.** All `128²` products were formed
with the signed composition rule. The set is an elementary abelian 2-group:
it is closed, every element is an involution, and every pair commutes.

Modulo the 32 diagonal signs there are four cosets, one for each permutation
above. Two elements from different nontrivial cosets multiply into the third
coset. Their joint spectral formula therefore has four positive dimensions on
every character. There are `3 · 32 · 32 = 3072` such unordered pairs, and the
verifier counts 3072. Two elements of the same nontrivial coset differ by a
diagonal sign. That sign acts by a scalar on each character space, so the
joint split is only the two-way split of either involution. There are
`3 · C(32,2) = 1488` such pairs.

There is no third independent involution inside the preserver group. Four
joint spaces are the finest simultaneous split of all 16 characters available
from this stabilizer.

## One explicit pair

Take

| name | permutation | minus signs |
|---|---|---|
| `u` | `(0 2)(4 6)` | coordinates 0 and 2 |
| `v` | `(0 4)(2 6)` | coordinates 0 and 4 |
| `uv` | `(0 6)(2 4)` | coordinates 0 and 6 |

All three are among the 96. For this choice of signs the odd-weight traces
are positive, and the joint dimensions `(eigenvalue of u, eigenvalue of v)` are

| weight | dimension | `(+,+)`, `(+,-)`, `(-,+)`, `(-,-)` |
|---:|---:|---|
| 0 | 864 | 216, 216, 216, 216 |
| 1 | 432 | 180, 84, 84, 84 |
| 2 | 192 | 48, 48, 48, 48 |
| 3 | 80 | 44, 12, 12, 12 |
| 4 | 32 | 8, 8, 8, 8 |

Any other cross-coset pair has the same multisets; only the slot of the large
piece moves with the trace signs. These numbers are the output of the trace
formula, not a fitted approximation.

## The predecessor pair does not do this

The involutions of the c=1 certificate are `g = (1 2)(5 6)` with minus signs
on coordinates 4 and 7, and `t = (1 5)(2 6)` with minus signs on coordinates
3 and 7. Both are symmetries of the query. `g` sends sector 3 to 343, so it
does not act on this block. `t` does fix sector 3, but it moves odd
coordinates and preserves only 8 of the 16 characters. It is not one of the
96. The c=1 characters that this older pair moves are a different question.

## What is not claimed

The joint spaces give invariant subspaces. They do not upper-bound the
minimal polynomial of the full one-slot operator, and they do not replace the
degree-881 certificate or the coarse all-width annihilator. No characteristic
polynomial and no basis of a joint space is computed. Payload involutions are
outside this signed-permutation group; this census does not exclude a split
coming from them. The selected conditional kappa is unchanged.

A failed search was not used. The stabilizer list is the orbit-stabilizer
count together with a rebuilt element for every hit, and the preserver list
is the scalar-conjugation test on every one of those elements.
