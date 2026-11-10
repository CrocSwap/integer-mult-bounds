# A 12-dimensional cut of one moved 48-eigenspace

This note is an exact finite certificate. It is not a characteristic polynomial, not an irreducibility theorem, and not a multiplication bound. The selected conditional kappa stays `781451/250000000`.

## Hypotheses

The live input is the 8-by-112 query pinned by `research/centre-polynomial-cache-limits/`, SHA256 `5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`. Its columns lie in `{-1,0,1}^8`, each has weight 4, and `R R^T = 56 I_8`. The one-slot block at sector `c` is

    A_c = (1/4) sum_q r_q r_q^T ⊗ P_q(c)

on `C^8 ⊗ C[F_2^9]`, with `P_q(c) e_a = e_{a+q}` when `q·c = 1` and `P_q(c) e_a = (-1)^{q·a} e_a` otherwise. Write `B_1 = 4 A_1` for the integral form of the `c = 1` block. The factor `1/4` is not used in the matrix checks below.

`R` is the set of signed coordinate permutations whose underlying permutation preserves the 14 tetrads, whose port map is an `F_2`-linear isometry of the standard dot product, and which fix sector `1`. The verifier scans all `8!` permutations and all `256` sign patterns and finds `|R| = 3072`. It checks that this set is closed under the signed-permutation composition law and under inversion, and that each stored label map inverts on a port basis.

`H` is the order-16 subgroup of pure sign changes in `R` with positive sign on coordinate `0`. Those signs are exactly the flips of subsets of coordinates `{1,2,5,6}`. Its sixteen character dimensions on the `c = 1` block are the predecessor histogram `{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}`.

Let `χ` be the character of `H` with value `-1` on the flips of coordinates `1` and `2` and value `+1` on the flips of coordinates `5` and `6`. Let `χ'` be the character with those four values reversed. Each has dimension `192`. The predecessor involution `g = (1 2)(5 6)`, with output signs `-1` on coordinates `4` and `7`, preserves both. The involution `t = (1 5)(2 6)`, with output signs `-1` on coordinates `3` and `7`, swaps them. So both characters are moved by the pair `<g, t>`: they are not among the two characters that pair fixes.

Let `s` be the order-4 permutation `(0 4 3 7)(5 6)` with all output signs `+1`, and let `u` be the involution `(4 7)(5 6)` with all output signs `+1`. Both lie in `R`. They do not commute. For each of them the verifier checks the column transport identity `S r_q = ± r_{T q}` on all `112` ports, orthogonality of `T` on the standard basis of `F_2^9`, and `T(1) = 1`.

## Orbit basis and the eigenvalue-1 space

`H` preserves each of the eight query coordinates. On coordinate `c` a sign element acts by `e_a ↦ ε_c e_{T a}`. The image of the isotypic projector of `χ` is spanned by one nonzero orbit vector in each contributing orbit. Those vectors have disjoint supports. After scaling, every nonzero entry is `±1` and one pivot entry on each vector is `+1`. The same construction for `χ'` is independent. In both cases the verifier finds `192` vectors, matching the character dimension.

Every element of `R` that preserves `χ` acts on this basis by a signed permutation. The action is read by applying the geometric signed permutation to each basis vector and demanding that the image equal `±` one basis vector on every coordinate, not only at the pivot. The same holds for `χ'`.

On each character, `s` has cycle type `40` cycles of length `4` and sign `+1`, `8` cycles of length `2` and sign `+1`, and `8` cycles of length `2` and sign `-1`. A cycle of sign `+1` contributes one eigenvalue-`+1` eigenvector, with values propagated by `v_{next} = edge · v`. That produces a `48`-dimensional space `E`. The `48` eigenvectors have disjoint supports in the orbit basis, so they are linearly independent. This is the eigenvalue-`1` space of `s` on that character. It is the real eigenspace named in the question; the eigenspaces for `i` and `-i` are not given bases here.

## Census of the elements that preserve the character

`R` has `512` elements that preserve `χ`, and `512` that preserve `χ'`. On each of the two copies of `E` their restrictions fall into the same classes. Commutation with `s` is equality of the two composition orders in `R`. Scalar means the `48×48` integer matrix is `± I`. Trace is the sum of the diagonal in the eigenvector basis.

| class on `E` | count |
|---|---:|
| commutes with `s`, acts by `+1` | 32 |
| commutes with `s`, acts by `-1` | 32 |
| does not commute with `s`, acts by `+1` | 32 |
| does not commute with `s`, acts by `-1` | 32 |
| does not commute with `s`, involution of trace `+24` | 48 |
| does not commute with `s`, involution of trace `-24` | 48 |
| does not commute with `s`, order `4`, trace `+24` | 16 |
| does not commute with `s`, order `4`, trace `-24` | 16 |
| does not preserve `E` | 256 |

The four centralizer rows are the order-`64` centralizer from PR #7009, seen here by matrices rather than by the triangle inequality. On this real eigenspace the scalars are `±1`. The `64` noncommuting scalar elements preserve `E` and do not cut it. The `256` elements that fail to preserve `E` are not given an intersection dimension in this certificate.

An element of order `2` that preserves `E` satisfies `u^2 = I` on `E`, so its eigenvalues are `±1` and the multiplicities are `(48 ± trace) / 2`. Trace `+24` is the split `36 + 12`. Trace `-24` is the split `12 + 36`. Thus each of the `96` noncommuting involutions cuts `E` into invariant subspaces of dimensions `36` and `12`. The witness `u` is one of the trace-`+24` involutions, on both characters.

A signed permutation of finite order is diagonalizable over `C`, and the restriction of a diagonalizable operator to an invariant subspace remains diagonalizable. Each of the `32` noncommuting order-`4` elements is therefore non-scalar and diagonalizable on `E`, so it has a proper eigenprojection inside `E`. The four multiplicities are not determined by the real trace `±24`, and this note does not compute them.

## The exhibited 12-dimensional subspace

For `u` on each character, the matrix of `u + I` on `E` has rank `36` and the matrix of `u - I` has rank `12`. The right kernel `W` of `u + I` therefore has dimension `12`, and the `+1` space has dimension `36`. The verifier produces `12` content-free integer kernel vectors, checks that they are linearly independent, and checks that `u` sends each to its negative in the eigenvector coordinates.

Each kernel vector lifts to a finitely supported integer vector in `C^8 ⊗ C[F_2^9]`. The geometric actions of `s` and `u` fix that ambient vector and negate it, respectively. Both implementations of `B_1` — one looping by ambient basis vectors, one accumulating the dot product at each address before the port action — agree on these `24` vectors. For each of them, `B_1` lands in the `Q`-span of `W`: the image lies in the character space, then in `E`, then in the kernel span. A single off-support spike added to any such image is rejected by the character test, so that acceptance check is not vacuous.

Since `4` is invertible over `Q`, invariance under `B_1` is invariance under `A_1`. The subspace `W` is a `12`-dimensional `A_1`-invariant subspace of the `48`-dimensional eigenvalue-`1` space of `s`. The element `u` lies in the `c = 1` stabilizer, preserves the moved character, and does not commute with `s`. This is the cut asked for.

The same transport identity that puts `u` and `s` in `R` conjugates `A_1` to itself, so every element of `R` commutes with `A_1`. The direct image check above does not call that identity. The identity is what promotes the eigenprojections of the other `127` non-scalar preservers from invariant subspaces of those elements to `A_1`-invariant subspaces. The stabilizer scan accepts an element only after the transport identity has been checked on every port.

## What this does not say

The `12`-dimensional space is not shown to be `A_1`-irreducible. No characteristic polynomial of `A_1` on `W`, or on the `48`-dimensional space `E`, is computed. The `i` and `-i` eigenspaces of `s` are not given this basis. Elements of `R` that do not preserve `E` may still meet `E` in a partial intersection; that dimension is not proved here. For `χ` only, an exploratory rank computation modulo `1000003`, not part of the registered verifier, returned intersection dimension `0` for the `256` elements that move `E` and `48` for the `192` that preserve `E`. A modular rank is not an exact rational rank.

Sector `c = 3` is untouched. The degree-`881` one-slot polynomial is untouched. Selected conditional kappa stays `781451/250000000`.
