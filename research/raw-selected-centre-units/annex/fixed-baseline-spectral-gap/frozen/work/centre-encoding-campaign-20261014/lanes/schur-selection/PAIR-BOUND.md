# Selected Schur blocks for the actual centre matrix

This note gives a sharp bound in one specified selection class. It does
not give a lower bound of 40 for all selections. The general lower bound
proved here is 24. Independent agent review is still required.

Let R be the actual 8 by 112 matrix from the frozen supplier. Put
K = R^T/4. For a selected set S, let U be its complement and define

    D_S = I - R_U K_U = R_S R_S^T/4 - 13I.

The required condition is that D_S be invertible over Z[1/2]. Thus its
determinant must be a nonzero signed power of two. The fixed subsets are

    A = [0, 7, 20, 27, 36, 46, 57, 111]
    T = [21, 37, 47, 76, 81, 87, 92, 110].

They are disjoint, and R_A R_A^T = R_T R_T^T = 4I.

## A general lower bound

Every admissible S that contains A and T has at least 24 columns.

To prove this, let V contain the r = |S|-16 additional columns. Then

    D_S = -11I_8 + VV^T/4.

For r < 8, the determinant identity gives

    det(D_S) = (-11)^(8-r) det(-11I_r + V^T V/4).

The second determinant is in Z[1/2]. Hence det(D_S) is zero or has the
odd factor 11. It is not a unit of Z[1/2]. This proves the bound.

## The split-pair class

Split the eight coordinates into 0 through 3 and 4 through 7. The fixed
set A union T consists of the two complete four-coordinate support
planes. Each other column has two nonzero entries in each half. All
nonzero entries are 1 or -1.

The 96 other columns form 48 pairs. Each pair has representatives

    (a,b), (a,-b),

up to an overall sign on either column. Each of a and b is a signed
two-coordinate vector in four dimensions. The split-pair class requires
the additional columns in S to be a union of these complete pairs.
This is a restriction on S, not a requirement of the supplier.

A pair contributes

    2 diag(aa^T, bb^T)

to R_S R_S^T. If there are p additional pairs, then D_S is block diagonal.
The negative of twice its first block is

    B = 22I_4 - sum_a n_a aa^T.

There are twelve possible vectors a up to sign: e_i+e_j and e_i-e_j,
where 0 <= i < j < 4. Each type occurs in four of the 48 actual pairs.
Thus 0 <= n_a <= 4 and sum n_a = p.

If |S| < 40, then p <= 11. The determinant of each block of D_S is an
integer divided by 16. A unit determinant of the full block diagonal
matrix would require det(B) to be a nonzero signed power of two.

The finite check covers every multiplicity vector with

    0 <= n_a <= 4,  sum n_a <= 11.

There are exactly 1,130,168 such vectors. This count is also the sum of
the coefficients of degrees 0 through 11 in (1+x+x^2+x^3+x^4)^12.
No vector gives a nonzero power of two for det(B). The enumeration drops
the restrictions from the second block, so it checks a superset of all
actual split-pair selections. It proves |S| >= 40 in this class.

The first check uses exact integer elimination. The second check uses
the explicit four-dimensional determinant polynomial and verifies the
count with polynomial multiplication. The second check also derives R
from the frozen supplier word and checks every pair and multiplicity.

## Sharpness

The following 40-column set is in the split-pair class:

    [0, 1, 2, 4, 6, 7, 9, 12, 14, 17, 20, 21, 22, 25, 27, 29,
     31, 32, 36, 37, 38, 41, 46, 47, 48, 52, 57, 59, 61, 64,
     68, 76, 81, 87, 92, 97, 106, 109, 110, 111]

It contains A and T. Its twelve additional pairs give one copy of each
signed root type in each half. Direct integer multiplication gives

    R_S R_S^T = 20I,  D_S = -8I,  D_S^-1 = -I/8.

Thus 40 is the exact minimum in the split-pair class. This result does
not improve the existing five-minor construction. It shows that a
smaller support must break the complete split-pair restriction.

There is a useful family at the boundary. Regard each of the 48 pairs
as an edge from its first root type to its second root type. The actual
graph is the disjoint union of three copies of K_(4,4). A perfect matching
in each copy selects one pair of each root type in both halves. Every
such choice gives the same Gram matrix 20I. This gives (4!)^3 = 13,824
distinct 40-column supports with D_S = -8I. The family permits a later
choice of ports for native access or routing. No cost benefit from this
choice has been checked here.

## Source and replay

The source base is bce54fb3f895cbe5cd4c0eb477c3afeed100190f. The archive
and its members are checked by the published native source-code loader.
The receipt records the exact source and loader hashes.

From the repository root, run:

```sh
clang++ -O2 -std=c++17 work/centre-encoding-campaign-20261014/lanes/schur-selection/enumerate_four_block.cpp -o work/centre-encoding-campaign-20261014/lanes/schur-selection/enumerate_four_block
work/centre-encoding-campaign-20261014/lanes/schur-selection/enumerate_four_block > work/centre-encoding-campaign-20261014/lanes/schur-selection/FOUR-BLOCK-CANDIDATES.json
python3 -B work/centre-encoding-campaign-20261014/lanes/schur-selection/check_pair_bound.py
```

The final command prints `PASS_SPLIT_PAIR_BOUND` and 1,130,168 checked
vectors. It writes [PAIR-BOUND.json](PAIR-BOUND.json). The new code and
proof used OpenAI Codex assistance. The native source-code package
supplies the pinned loader. The encoded-controller lane supplied the
five-minor 40-column comparison. No full supplier, native controller,
recursive invoice, or kappa improvement is claimed here.
