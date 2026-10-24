# Independent review of the unpaired spectral bound

The frozen proof passes. For a selected set S that contains the specified
disjoint sets A and T and keeps the stated source baselines, the dyadic
unit condition excludes sizes 24, 25, 26, 28, 29, 30, and 31. Together
with the factor-11 argument for smaller sets, this gives |S| >= 27.
Size 27 is open. Its determinant must equal 2^42 in the normalization
used below. This review does not prove that such a set exists.

This is a bound for the stated source interface. It is not a general
bound on centre information, native cost, or the supplier. The existing
split-pair result has a narrower selection class. Its exhaustive search
was not repeated here.

## Source binding and separate replay

The review reads the archive from the Git object at
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. It checks archive SHA256
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
It checks both compressed and decoded hashes of the canonical word and
local scalar programs. It does not import the producer or its loader.

The review propagates the eight centre output forms backward through
the 12,550-event source prefix. Their coefficients on all 112 source
inputs reproduce the pinned R. This is a different propagation path
from the producer's full forward matrix replay. The review then checks
RR^T = 56I, both fixed minor Grams 4I, and their disjointness. It checks
all 6,216 unordered root pairs. Their products are 0 in 3,304 cases,
2 in 1,960 cases, and -2 in 952 cases. Every root has squared norm 4.

Write V for the extra selected columns, v = |S|-16, and M = VV^T.
Then D = I-R_U K_U = -11I+M/4 and B = -4D = 44I-M. In the range
checked here, B is positive definite. A dyadic-unit D therefore needs
det(B) to be a positive power of two. For v < 8, the determinant lemma
gives a factor 11^(8-v) in det(D), with a dyadic second factor. That
factor cannot cancel 11. This proves the earlier exclusion below 24.

The selected-baseline condition was also checked against
`../cover-algebra/SELECTED-BLOCK-NECESSITY.md`, SHA256
`2f9bf455a73dfbd176d1a634df9f2a662178e72ad8dfec4cdf1f7a4ee712198d`.
If F has the specified selected rows and (JF)_U is the ordinary U
selector, put C=FE^-1. Then C has lower selected block [0,I]. Its U
block is a unit and J_UU C_UU=I. Thus J_UU is a unit. The ordered block
identity makes this equivalent to a unit D. This condition does not
apply when the selected baselines or the target interface may change.

## The fifteen-root lemma

The graph argument is valid for any fifteen distinct real roots in
dimension eight with these norms and pair products. It does not need
the particular list of 112 columns.

An unbalanced signed triangle can be switched so that x has product 2
with y and z, while y has product -2 with z. The norm identity gives
x=y+z. A fourth common neighbor cannot exist: its product with x would
be a sum of two values in {2,-2}, and that sum cannot be 2 or -2.
Thus every clique of size at least four can be switched to the positive
Gram matrix 2I+2J. This matrix has full rank, so the clique size is at
most eight.

The weighted graph bound in the proof is valid. Moving all weight from
one of two nonadjacent support vertices to the other does not decrease
the objective when the larger neighbor sum is chosen. The support
decreases at each step. The final support is a clique. Cauchy's
inequality on that clique gives the stated weighted bound.

For clique number at most six, the resulting integer edge bound is 93.
For clique number eight, the inverse Gram matrix is (I-J/9)/2. The
outside-root equation 9h-s^2=18 has exactly the five listed solutions.
Its maximum h is six, so the total edge count is at most 91.

For clique number seven, the inverse Gram matrix is (I-J/8)/2. The
projection and residual formulas follow by direct multiplication. A
root of clique degree six has six products of the same sign and a
residual of length one. After sign choice, its projection is
(sum C)/4-C_i, where i is its omitted clique index. Two high roots
with the same i either coincide or, with six clique roots, give an
eight-clique. Thus the high roots have distinct omitted indices.

For each remaining root, the review checks all 2,187 possible product
patterns epsilon in {-1,0,1}^7. Exactly 281 have h <= 5 and nonnegative
residual square. The seven possible (h,|s|,a^2) classes and maximum
numbers of possible high neighbors are:

| h | abs(s) | a^2 | Possible omitted indices for an edge |
|---|-----|-----|--------------------------------------|
| 0 | 0 | 4 | 7 |
| 1 | 1 | 9/4 | 6 |
| 2 | 0 | 0 | 2 |
| 2 | 2 | 1 | 7 |
| 3 | 3 | 1/4 | 4 |
| 4 | 4 | 0 | 3 |
| 5 | 5 | 1/4 | 2 |

For each omitted index, both residual signs are checked through the
integer expression 2<w,w_i> = s-4 epsilon_i +/- 2a. The allowed values
are -4, 0, and 4. The check permits a separate high-root sign choice
at every index. It therefore covers a superset of the actual compatible
configurations. All 2,248 resulting degree checks satisfy
h+d_H <= max(7,t+2).

The h=2, |s|=2 class prevents replacement of this bound by a constant
seven. The proof uses the correct t+2 term. For t from zero through
seven, the total edge bounds are 89, 90, 91, 87, 85, 85, 89, and 93.
All clique cases are covered. Averaging over fifteen-element subsets
gives E <= floor(31v(v-1)/70) for every v >= 15.

## Exact determinant intervals

The three eigenvalue caps are valid. The first comes from the absolute
row sums of V^T V. The second follows from the weighted graph bound
and the absolute coordinates of a unit vector. For the third, Cauchy's
inequality on the other seven eigenvalues gives
8 lambda^2-2s lambda+s^2-7q <= 0. The stated positive root is its
upper endpoint. Replacing q by a larger bound increases this endpoint.

The review checks the upward square-root rounding and the selected
rational cap L for every v from 8 through 23. Each cap is below 44.
The extreme-point determinant lower bound follows from concavity on
the eigenvalue box with fixed sum. The second-moment bound is also
valid: the positive-coefficient series
[-log(1-x)-x]/x^2 is increasing for 0 <= x < 1. Its value at L/44
therefore bounds each summand. The subtracted factor is positive, so
an upper bound on q gives a valid lower determinant bound.

The independent interval routine uses direct rational powers and 64
terms, rather than the producer's 32-term recurrence. It also reproduces
every saved 32-term rational margin exactly. All 16 size rows, all
moment bounds, and every remaining exponent agree with the receipt.

For size 31, q <= 984 and L=29815/1024. The 64-term calculation proves

    lower_bound(log det B) - 41 log 2 > 1/1250 > 0.

This is an exact rational comparison. The upper bound is below 2^42.
Thus size 31 is excluded without a floating-point estimate. The full
excluded intervals are 2^42 < det(B) < 2^43 at sizes 24 through 26,
and 2^41 < det(B) < 2^42 at sizes 28 through 31.

## Replay and pins

Run from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/temporal-reuse/review_spectral_bound.py
```

The command was run and printed
`PASS_INDEPENDENT_UNPAIRED_SPECTRAL_BOUND`. It uses explicit checks that
remain active under `-O`. It writes `SPECTRAL-BOUND-REVIEW.json`.

| File | SHA256 |
|------|--------|
| Producer proof | 6dd2afed08d8873a2277ccfef4edd1bc212e831b8495bb659809f76d77802af1 |
| Producer checker | ecc031e20c309c4e1d04443b60a58fe03d32ce73a5a3b43078e9cb673341c61c |
| Producer receipt | d1124af128b6e526461c7587c2a7331dc4d19c9d90433d8d08bf9676c33a8a84 |
| Independent checker | 83de0b4694a8ef1ee501130bca9ddedf6e265f6be44b855e61e327646a7529d9 |
| Independent receipt | 9639db0bdbc82255ef85273ac15a0aff68d5c659190557bf331d260eb714964f |

No producer file was changed. No native word, ownership schedule,
recursive invoice, or complete kappa calculation was checked by this
review. OpenAI Codex assisted with this independent proof review and
verification code.
