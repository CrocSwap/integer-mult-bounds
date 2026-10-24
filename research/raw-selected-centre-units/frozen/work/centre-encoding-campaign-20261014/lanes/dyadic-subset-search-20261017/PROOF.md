# Two dyadic unit conditions from fewer than five complete minors

## Result and scope

An exact subset of 38 of the actual 112 centre columns passes both matrix
unit conditions. It is not a union of complete eight-column minors.
The construction also gives a subset of size 39. All coefficients and
inverse entries are dyadic rational numbers.

This result removes the forty-column threshold for the stated pair of
unit conditions. Forty was the least size among unions of complete
orthogonal minors. It was not a lower bound for all subsets.

The check in this folder is a matrix check. It does not run the native
local, build the global controller, or price the complete supplier.
The raw selected local and its native frame map are in
`../native-escape-20261017/RAW-MINOR-SUBSETS.md`. That proof gives the
application of the first unit condition to the borrowed block. The
second condition below is also available for the full response map.

## Exact source and witness

Read R from `../circuit-interface/INTERFACE.json`, with SHA-256

```text
5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3
```

R has eight rows and 112 columns. Each column v has four entries in
`{1,-1}` and four zero entries. The exact source gives

```text
R R^T = 56 I,
K = R^T/4,
R K = 14 I.
```

Select these zero-based ports:

```text
1, 3, 4, 17, 18, 19, 20, 23, 24, 26, 27, 29, 35, 36, 38, 39,
40, 42, 45, 60, 63, 66, 69, 74, 75, 77, 78, 84, 86, 88, 97, 99,
104, 105, 107, 108, 109, 111
```

Let `G = R_S R_S^T`. Let E_ij denote the elementary eight by eight
matrix. Define

```text
A = E_02 + E_03 + E_14 + E_15,
L = I + A/4.
```

The selected source columns give the exact identity

```text
G = 20 I - 8(A+A^T) - 2 A A^T,
52 I - G = 32 L L^T.
```

The checker computes G directly from the 38 columns. It compares every
entry with this identity. The identity is not a fitted numerical test.

## First unit condition

The matrix for the ordinary borrowed block is

```text
T = R_S K_S - 13 I = G/4 - 13 I = -8 L L^T.
```

A is strictly upper triangular and `A^2=0`. Thus

```text
L^-1 = I - A/4,
T^-1 = -(I-A^T/4)(I-A/4)/8.
```

These are exact dyadic matrices. Direct multiplication gives both inverse
identities. Also `det L=1`, so

```text
det(52I-G) = 2^40,
det T = 2^24.
```

For `H_U=I_U-K_U R_U`, the general subset identity gives
`H_U^-1=I_U+K_U T^-1 R_U`. Thus this borrowed block is a unit over
dyadic coefficients. This implication does not move a native Q operator
through a scalar centre factor.

## Second unit condition and a family

More generally, divide eight coordinates into k source coordinates and
8-k target coordinates. Let

```text
A = [ 0  W ],
    [ 0  0 ]
W W^T = 2 I_k.
```

Suppose the actual columns realize
`G=20I-8(A+A^T)-2AA^T`. The first unit proof still applies.
The trace gives

```text
4 |S| = trace G = 160 - 4k,
|S| = 40-k.
```

The second matrix has the block form

```text
4I-G = [ -12 I_k      8W       ].
       [   8W^T    -16 I_(8-k) ]
```

Eliminate its lower diagonal block. The remaining block is

```text
-12 I_k + 4 W W^T = -4 I_k.
```

Both diagonal blocks are dyadic units. This proves that `I-G/4` is a
dyadic unit and gives

```text
det(4I-G) = 2^(32-2k),
det(I-G/4) = 2^(16-2k).
```

For the displayed 38-column witness, W has two disjoint rows, each with
two entries equal to one. Thus k=2 and
`det(4I-G)=2^28`. The 39-column witness in the checker has k=1.

The matrix family permits k=3 or k=4, subject to an actual source subset
that realizes G. This file does not assert that such a subset exists.
Signed Hadamard targets for these two cases failed the bounded searches
in this folder. Solver failure does not prove a minimum.

## A general lower bound of twelve selected columns

This lower bound applies to the first unit condition alone. It does not
use the special shear form of the positive witness.

Let s be the selected size. If s<8, Sylvester's determinant identity
gives

```text
det(52I_8-R_S R_S^T)
    = 52^(8-s) det(52I_s-R_S^T R_S).
```

The second determinant is an integer. A nonzero result has an odd factor
13. A zero result is singular. In either case T is not a dyadic unit.

For `8 <= s <= 11`, put `B=G/4`. Each normalized selected column has
norm one. The exact source check gives pair inner products in
`{-1/2,0,1/2}`. The selected column Gram matrix therefore has each
absolute row sum at most `(s+1)/2`. Its nonzero eigenvalues are those of B.
Consequently all eight eigenvalues lambda_i of B satisfy

```text
0 <= lambda_i <= (s+1)/2,
sum lambda_i = s.
```

All factors `13-lambda_i` are positive. Their product is largest when the
eight lambda_i are equal. For the lower bound, move mass between two
coordinates while their sum is fixed. The product of the two factors is
smallest at an endpoint of the permitted interval. Repetition leaves
one coordinate at `(s+1)/2`, one at `(s-1)/2`, and six at zero. Hence

```text
13^6 (13-(s+1)/2)(13-(s-1)/2)
    <= det(13I-B)
    <= (13-s/8)^8.
```

The exact endpoints give

```text
2^28 < 13^6 * 7 * 8 <= det(13I-B) <= 12^8 < 2^29.
```

There is no signed power of two in this positive open interval. Since
`det T=det(13I-B)`, T is not a dyadic unit. Thus every subset that meets
the first unit condition has at least twelve columns.

The gap from twelve to the exhibited 38 columns is open. No minimum
claim is made for the 38-column witness.

## Reproduction and open obligations

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/dyadic-subset-search-20261017/check_dyadic_subsets.py
```

Expected output:

```text
PASS_EXACT_FIXED_SUBSETS_AND_TWO_UNIT_CONDITIONS
```

The check reads a pinned interface, uses exact rational arithmetic, and
writes `DYADIC-SUBSETS.json`. It checks both inverses, both determinant
conditions, all pair inner products, and the rational bounds for sizes
eight through eleven. It uses no optimizer.

The search scripts record how the witnesses were found. Their negative
results are only search records. The proof and checker above do not rely
on solver status, floating-point eigenvalues, or a claim that a search
was complete.

Independent proof review and the native application remain separate
obligations. No complete kappa improvement is claimed here. This work
builds on the exact centre interface and the general raw-subset theorem
in the adjacent lanes. It was produced with AI assistance.
