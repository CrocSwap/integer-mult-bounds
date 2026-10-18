# Local regularity proof for the P104 tangent certificate

## Statement audited

Fix one live set `L` from a P104 frame-pair puncture and let

\[
X=\{K\in\mathbb C^{L\times L}: \operatorname{rank}K\le8,
  K_{ii}=4,\ K_{ij}=0\text{ whenever }G_{ij}=0\}.
\]

Let `K0 = 2G`. PR #1292's certificate asserts
`T_K0 X = T_K0 O`, where `O` is the orbit of `K0` under diagonal conjugation
`K ↦ D K D^{-1}` and `dim O = |L| - 1`. The audit asks whether this tangent
equality actually implies `X` and `O` have the same germ at `K0`.

## Dimension from the pinned certificate

For `v = |L|`, the M-system has `8v` variables. Its exact rational rank is
bounded below by its rank over `F_(2^31-1)`, because a nonzero minor modulo an
odd prime remains a nonzero rational minor. The explicit 64-dimensional
parameterization gauge and the `v - 1` independent torus directions give a
matching kernel lower bound. The source verifier reports:

| Live set | `v` | M-system rank | M-kernel | parameterization gauge | tangent/orbit dimension |
|---|---:|---:|---:|---:|---:|
| P120 | 120 | 777 | 183 | 64 | 119 |
| P112 | 112 | 721 | 175 | 64 | 111 |
| P104 class 0 | 104 | 665 | 167 | 64 | 103 |
| P104 class 1 | 104 | 665 | 167 | 64 | 103 |
| P104 class 2 | 104 | 665 | 167 | 64 | 103 |

In each row, `8v - rank = v + 63`; after quotienting the 64 null parameterization
directions, the tangent image has dimension `v - 1`. The independent torus
directions span exactly that image. The three P104 representatives cover the
1260 frame-pair punctures by the explicit stabilizer transformations in the
pinned checker.

The source checker builds the reduced M-system and certifies its rank over the
odd prime field. Its basis inversions are nonsingular modulo that prime, so
each row is the reduction of the corresponding rational elimination row. The
rank over `F_p` is therefore a lower bound on rational rank. The formulas for
the GL(8) gauge and torus directions put `64 + v - 1` independent rational
directions in the kernel; the wrapper independently checks every one of their
reductions against every reduced P104 row modulo `2^31 - 1`. These matching
bounds give the stated dimensions over `Q`, then over `C`. The finite-field
replay certifies the matrix rank and checks the displayed directions, while
the formulas supply rational kernel inclusion. Its deeper-puncture 64/64
sample is not used for this universal P104 statement.

## Algebraic regularity closes the local implication

1. `X` is an affine algebraic set: the rank bound is defined by the 9-by-9
   minors and the mask is a set of affine-linear equations.
2. Diagonal conjugation preserves rank, the diagonal entries, and every masked
   zero. Therefore the smooth algebraic-group orbit `O` lies in `X`. The
   pinned torus tangent rank gives `dim(O) = v - 1 = 103` on P104.
3. The certificate gives `dim(T_K0 X) = 103`. Since `O` lies in `X`, the local
   dimension of `X` at `K0` is at least 103. For any algebraic variety, local
   dimension is at most tangent-space dimension, so it is exactly 103. The
   local ring is regular; over `C`, this means `X` is a smooth complex manifold
   near `K0`.
4. The inclusion `O -> X` is a map between smooth 103-dimensional manifolds
   whose differential at `K0` is an isomorphism. The inverse function theorem
   makes the inclusion a local isomorphism. Hence some neighborhood of `K0`
   in `X` lies in `O`; the two germs agree.

The same argument applies to P120 and P112. Restricting the complex statement
to real matrices gives the real local result.

## Limits

This regularity argument does not rule out other components of `X` away from
`K0`. It also does not address rank-nine costly parts, different punctures,
physical copy trees, or a lower complete moment. The decoder consequence still
inherits PR #968's all-pairs classification and the selected construction's
interface assumptions. This is not a proof of the full multiplication theorem.
