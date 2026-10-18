# A finite obstruction for Gaussian E8 hyperplane rectangles

## Object and restricted class

Use the 60 Gaussian E8 lines in the order constructed by `core.py`.
The coordinates use doubled standard E8 roots.
Successive coordinate pairs form Gaussian coordinates.
Let `G` be their Hermitian Gram matrix.
For each normal line `u`, define the 15-line root hyperplane support

```text
H_u = { i : G[u,i] = 0 }.
O[i,u] = 1 if i belongs to H_u, and 0 otherwise.
```

The matrix `O` is symmetric and has rank 60 over F2.
This rank does not impose a restriction on all hyperplane rectangles.
Allowing all 3,600 pairs makes the transformation `X -> O X O` invertible.

Consider only these 960 binary rectangle types:

- `H_u x H_v` when `u` and `v` are orthogonal, with `u != v`: 900 ordered types, each with pairing rank 2.
- `H_u x H_u`: 60 types, each with pairing rank 3.

The ranks follow from the dimensions of two hyperplanes and their normal lines.
The verifier also checks every rank directly over Q(i).
The class excludes the other 2,640 pairs of unequal, nonorthogonal normals.
It also excludes arbitrary subsets of hyperplanes.

## Proposition

Every fitting decoder formed from these 960 rectangle types costs at least 180.
This statement allows any number of terms and repeated rectangle types.
It does not give a bound for unrestricted asymmetric decoders.

## Exact finite identity

Write `x` for the binary coefficient vector of the 960 types.
Order the 900 orthogonal-normal types lexicographically, followed by the 60 equal-normal types in normal-line order.
Let `M x` list the 2,640 entries `B[i,j]` with `i != j` and `G[i,j] != 0`.
Let `D x` be the diagonal of `B`.
Let `S x` select the last 60 coefficients of `x`.

The exact finite certificate establishes

```text
rank_F2(M) = 880;
dim_F2 ker(M) = 80;
(D + S) x = 0 for every x in ker(M).
```

Thus, whenever the forbidden entries vanish, `B[i,i]` equals the coefficient of `H_i x H_i`.
Here `i` identifies the normal line of the hyperplane, not a line in its support.

The certificate lists 880 pivot-column indices and 80 independent kernel vectors.
The verifier reconstructs each rectangle from exact root coordinates.
It checks every kernel vector by direct XOR of its rectangle columns.
It then checks `D x = S x` on every basis vector.
Linearity proves the identity on the complete kernel.

The first 900 columns have rank 840 and kernel dimension 60.
Every vector in this smaller kernel has zero diagonal image.
Consequently, the rank-two subclass cannot supply any fitting diagonal by itself.

## Cost bound

A fitting decoder has `M x = 0` and `D x = (1,...,1)`.
The identity therefore forces all 60 equal-normal coefficients to be one.
Each corresponding rectangle costs 3, which gives the bound 180.

For repeated types, collect coefficients modulo two.
An odd coefficient requires at least one occurrence of that type.
All charges are nonnegative, so repeated terms cannot invalidate the lower bound.

The class is feasible.
The certificate includes an exact fitting decomposition of cost 820.
That decomposition is not optimized and gives no useful upper bound for the unrestricted problem.

## Reproduction and scope

Run this command from the repository root:

```sh
python3 -B research/gaussian-e8-asymmetric-copy/geometry/verify_geometry.py
```

The output contains the normal-pair ordering, kernel vectors, and the feasible coefficient vector.
The saved output is `geometry/verification.json`.
The verification uses standard-library integer and rational arithmetic.
It requires assertions to remain enabled.

The Gaussian line model follows the earlier `s1-extension-rings/gauss_geom.py` and `algebra_lines.py` setup in the decoder notes.
This implementation constructs its roots directly and does not import those files or their external paths.
The finite hyperplane coefficient identity is the result proved here.
