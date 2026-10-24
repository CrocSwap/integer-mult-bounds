# Spectral bounds for unpaired selections

This note excludes selected sizes 24, 25, 26, 28, 29, 30, and 31 for the
actual centre matrix and the fixed sets A and T below. The selection need
not contain complete split-sign pairs. With the earlier factor-11 bound,
every admissible selection has at least 27 ports. A selection of size 27
must have det(-4D) = 2^42. Its existence is not proved. Sizes 32 through
39 also remain open. The result does not change the supplier or kappa.

## Matrix and required unit

Let R be the pinned 8 by 112 integer matrix. Set K = R^T/4. The fixed
sets are

    A = [0, 7, 20, 27, 36, 46, 57, 111]
    T = [21, 37, 47, 76, 81, 87, 92, 110].

They are disjoint and each has Gram matrix 4I. Let S contain A and T,
let V be the additional selected columns, and write v = |S|-16. Then

    M = R_V R_V^T,
    D = I - R_U K_U = -11I + M/4,
    B = -4D = 44I - M.

Here U is the complement of S. A dyadic-unit D requires det(B) to be a
nonzero power of two. This condition applies to the selected-baseline
source interface. It is not a bound on interfaces that change those
baselines. The independent cover-algebra note gives this distinction:
[SELECTED-BLOCK-NECESSITY.md](../cover-algebra/SELECTED-BLOCK-NECESSITY.md).

The source check verifies that every column of R has squared norm 4.
For distinct columns the inner products are 0, 2, or -2. The respective
unordered pair counts are 3,304, 1,960, and 952. Thus there are no repeated
or antipodal columns. No numerical eigenvalue computation is used below.

## Clique bound and moments

For any selected columns, form a graph with an edge when the inner
product is nonzero. Every clique has at most eight vertices.

To prove this, consider a clique with at least four roots. Change signs
so that the first root has inner product 2 with each other root. If two
other roots x and y have inner product -2, their sum has squared norm 4
and inner product 4 with the first root. The first root is therefore
x+y. A fourth root cannot have inner product 2 with this sum: its two
inner products are each 2 or -2 and their sum is -4, 0, or 4. Thus every
inner product in the changed clique is 2. Its Gram matrix is 2I+2J. It
has full rank, so the clique has at most eight roots in dimension eight.

The following weighted graph bound will be used twice. If a graph has
clique number at most w, and nonnegative weights have sum one, then

    sum_{ij an edge} x_i x_j <= (1 - 1/w)/2.

For a proof, take two nonadjacent vertices with positive weights. Move
their combined weight to the vertex whose weighted neighbor sum is
larger. This does not decrease the edge sum and reduces the number of
positive weights. Repeat until the support is a clique. On a clique of
size k <= w the edge sum is (1-sum x_i^2)/2 <= (1-1/w)/2.

Let E be the number of graph edges, s = tr(M), and q = tr(M^2). Equal
weights and the inner products give

    s = 4v,
    E <= min(v(v-1)/2, floor(7v^2/16)),
    q = 16v + 8E.

Let L bound the largest eigenvalue of M. Three valid bounds are

    L <= 2v+2,
    L <= 4+7v/4,
    L <= (s + sqrt(7(8q-s^2)))/8.

The first bound is the row-sum bound on R_V^T R_V. For the second, use
absolute values of a unit vector's coordinates in the weighted graph
bound, then use (sum |x_i|)^2 <= v. For the third, the other seven
eigenvalues have squared sum at least (s-L)^2/7. Replace q by its upper
bound when applying this formula.

## A stronger bound for fifteen roots

Any fifteen distinct roots in R^8 with squared norm 4 and pair products
in {0,2,-2} have at most 93 edges. This lemma does not require the fixed
sets A and T or the split-sign pairs.

Let w be the clique number. The previous section gives w <= 8. If
w <= 6, the weighted graph bound gives

    E <= floor((1-1/6)15^2/2) = 93.

If w = 8, change signs on an eight-root clique so that its Gram matrix
is 2I+2J. Its inverse is (I-J/9)/2. For an outside root, write its eight
inner products as 2 epsilon_i, where epsilon_i is 0, 1, or -1. Put
h = sum epsilon_i^2 and z = sum epsilon_i. Since the clique spans R^8,
the root's squared norm gives

    9h-z^2 = 18.

The only possible (h,z) are (2,0), (3,3), (3,-3), (6,6), and (6,-6).
Each of the seven outside roots has at most six neighbors in the clique.
Hence E <= 28+7*6+21 = 91.

It remains to consider w = 7. Change signs on a seven-root clique C so
that its Gram matrix is 2I+2J. Its inverse is (I-J/8)/2. The orthogonal
complement of its span has dimension one. For an outside root with
inner products 2 epsilon_i, define h and z as before. Its projection and
residual squared norms are

    projection norm squared = 2h-z^2/4,
    residual norm squared = (z^2-8h+16)/4.

No outside root has h=7, since there is no eight-root clique. Call an
outside root high if h=6, and let t be the number of high roots. A high
root has z=6 or -6. Change its sign so that all six nonzero products are
2. Its projection has squared norm 3 and its residual is sigma u, where
sigma is 1 or -1 and u is a fixed unit vector normal to C.

At most one high root can omit each clique index. Two with the same
omitted index and the same residual would be equal. Two with opposite
residuals would have product 2 and, with their six common clique
neighbors, form an eight-root clique. Thus t <= 7.

There are 8-t low roots, each with h <= 5. Choose the overall sign of a
low root so that z >= 0. Write its residual as a u, where a can have
either sign. For a high root that omits index i, the inner product is

    z/2 - 2 epsilon_i + sigma a.

The allowed values are 0, 2, and -2. The complete residual cases give
the following upper bounds for the number d_H of high neighbors:

| h | z | a^2 | Bound on d_H |
|---|---|-----|--------------|
| 0 | 0 | 4 | t |
| 1 | 1 | 9/4 | min(t,6) |
| 2 | 0 | 0 | min(t,2) |
| 2 | 2 | 1 | t |
| 3 | 3 | 1/4 | min(t,4) |
| 4 | 4 | 0 | min(t,3) |
| 5 | 5 | 1/4 | min(t,2) |

In every case, h+d_H <= max(7,t+2). The case h=2,z=2 is needed; it
does not permit the constant bound 7 when t is 6 or 7. The checker
enumerates all epsilon in {0,1,-1}^7 and both residual signs to verify
this table's combined inequality. It allows independent choices of the
high residual signs, so the check uses a superset of the actual cases.

For t=0 or 1, the direct edge bound is

    E <= 21 + 6t + 5(8-t) + 28 = 89+t.

For 2 <= t <= 7, count the clique edges, clique-to-high edges,
high-to-high edges, all edges from a low root to C or the high roots,
and low-to-low edges. This gives

    E <= 21 + 6t + binom(t,2)
             + (8-t) max(7,t+2) + binom(8-t,2).

The six values are 91, 87, 85, 85, 89, and 93. This proves E <= 93.
For v >= 15, count edges in all fifteen-root subsets to obtain

    E <= floor(93 v(v-1)/(15*14)) = floor(31v(v-1)/70).

## Exact determinant bounds

Use the smallest of the three eigenvalue bounds. The checker rounds
the square root upward to a rational number with denominator 256.
For every v from 8 through 23 it certifies 0 < L < 44. Thus B is
positive definite and det(B) is a positive integer.

Since tr(B) = 8*44-s, the arithmetic-geometric mean inequality gives

    det(B) <= (44-v/2)^8.

There are two lower bounds. For the first, put a=floor(s/L) and b=s-aL.
The logarithm of the determinant is concave in the eight eigenvalues
of M. Under their sum and interval constraints, a minimum has a values
equal to L, one equal to b, and the others equal to zero. Thus

    det(B) >= (44-L)^a (44-b) 44^(7-a).

The second bound retains the second moment. For 0 <= x <= L/44,
the power series for -log(1-x)-x gives

    -log(1-x)-x
      <= (44x/L)^2 [log(44/(44-L))-L/44].

Sum over the eight eigenvalues divided by 44. If q_0 bounds q, then

    log det(B) >= 8 log 44 - s/44
      - (q_0/L^2) [log(44/(44-L))-L/44].

All logarithm comparisons use rational intervals. For 1 <= x <= 2,
set z=(x-1)/(x+1) and use the first 32 terms of

    log x = 2 sum_{k>=0} z^(2k+1)/(2k+1).

The omitted tail is nonnegative and at most

    2 z^65 / (65(1-z^2)).

Other positive arguments are reduced to this interval by powers of
two and, when needed, reciprocals. The checker uses the upper endpoint
for each subtracted logarithm and for the power-of-two comparison. The
resulting lower endpoint is therefore conservative. The receipt stores
each exact rational margin used to exclude a size.

The resulting strict intervals are:

| Selected size | Strict determinant interval |
|---------------|-----------------------------|
| 24, 25, 26 | 2^42 < det(B) < 2^43 |
| 28, 29, 30, 31 | 2^41 < det(B) < 2^42 |

For size 31, the fifteen-root lemma gives q_0=984 and the rational
eigenvalue bound L=29815/1024. Its exact logarithmic lower endpoint is
strictly greater than 41 log 2. This narrow comparison is certified by
rational arithmetic, not a decimal approximation.

For unresolved sizes, the remaining exponents e in det(B)=2^e are:

| Selected size | Remaining exponents |
|---------------|---------------------|
| 27 | 42 |
| 32, 33, 34 | 41 |
| 35, 36 | 40 |
| 37 | 39, 40 |
| 38 | 38, 39, 40 |
| 39 | 37, 38, 39, 40 |

An exponent in this table is a necessary condition only. It is not an
existence claim. The split-pair bound still excludes every size below
40 in its narrower class. Neither bound excludes interfaces that change
the selected source baselines.

## Source, replay, and scope

The source base is bce54fb3f895cbe5cd4c0eb477c3afeed100190f. The source
reconstruction receipt [PAIR-BOUND.json](PAIR-BOUND.json) has SHA256
77e6d0e69dacc72a8bf110d13bd5708283ebcae8155d1b6666613806ee1be5a0.
The checker verifies that receipt and the actual matrix hash. The
earlier checker rebuilt the matrix from the pinned supplier archive;
this check does not repeat its million-vector split-pair enumeration.

From the repository root, run:

```sh
python3 -B work/centre-encoding-campaign-20261014/lanes/schur-selection/check_spectral_bound.py
```

The command prints `PASS_UNPAIRED_SPECTRAL_EXCLUSIONS` and the excluded
sizes `[24, 25, 26, 28, 29, 30, 31]`. It writes
[SPECTRAL-BOUND.json](SPECTRAL-BOUND.json). The code uses only Python's
standard library, exact integers, and fractions. It does not use a
solver, random search, floating-point arithmetic, or a determinant
enumeration.

The coordinating agent supplied the first spectral interval lead.
The prior split-pair lane supplied the actual root data and fixed sets.
OpenAI Codex assisted with the proof and code. Independent review must
bind the final proof, checker, and receipt bytes before this result is
used as a reviewed theorem. No native controller, full recursive cost,
or complete kappa calculation was changed here.
