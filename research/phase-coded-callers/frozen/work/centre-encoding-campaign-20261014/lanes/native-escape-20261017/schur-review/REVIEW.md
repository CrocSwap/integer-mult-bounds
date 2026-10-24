# Independent review of the translation Schur inverse

The frozen translation Schur result passes an independent exact check.
For the actual supplier graph, the operator

```text
T = B Q_U^2 D,       D=B^T,       BD=13I
```

has the same ten possible eigenvalues at every positive tensor width:
`-13,-11,-5,-3,-1,1,3,5,11,13`. It has the stated inverse translation
kernel with 256 shifts, 4,544 nonzero coefficients, and common denominator
8,580. This review also proves that no nonzero Gaussian-dyadic constant
alpha gives a uniform Gaussian-dyadic inverse for `I+alpha B Q_U D`.
The latter operator is different from T.

## Independent method and source scope

`check_schur_review.py` does not import the producer checker. It reads the
pinned primary R matrix and native q labels, then forms each graph column
in the selected basis. It adds the eight missing directions to obtain
the complete 120-root table. It checks every entry of the complete-root
Fourier identity for all 512 characters.

For each actual eight-by-eight T character matrix, the checker computes
the first eight power sums by integer matrix multiplication. It compares
them with the claimed spectral multiset. The first eight power sums
determine the degree-eight characteristic polynomial by Newton's
identities in characteristic zero. Each matrix is real symmetric. Thus
the multiset determines its spectrum with multiplicity, and the stated
ten-root polynomial annihilates it. The checker also verifies the inverse
polynomial at each of those ten roots.

The review then reads the literal rational translation kernels. It uses
direct character sums, without the producer's Walsh inversion. For each
character it verifies both matrix products with the inverse numerator.
Both products are exactly `8580 I`. It also verifies the forward kernel
and the stated row one-norms. There are 1,024 inverse-order checks.

For any width, the eigenvalue of `Q_p^2` is

```text
(-1)^(q_p . XOR_j chi_j).
```

All 512 characters occur, and every character tuple maps to one of them.
Thus the finite check proves the same identity at every positive width.
Each kernel translation applies its nine-bit shift in every tensor
copy. This is not a tensor power of a width-one matrix inverse.

The producer proof, receipt, and checker hashes are checked before and
after the review. The receipt records the primary source pins and the
review checker hash. The review does not change the frozen sources.

## A stronger constant-feedback obstruction

Let `R=Z[i,1/2]` and `S=B Q_U D`. At width two, take both spatial
characters equal. Direct evaluation of the actual graph gives

```text
chi=71:  S=-I,       chi=204: S=I,
chi=30:  S=-3I,      chi=460: S=3I.
```

Zero characters in the other copies extend these witnesses to each
width at least two. Suppose `I+alpha S` has an inverse over R in every
case, where alpha is a constant in R. The first two witnesses imply
that `u=1+alpha` and `v=1-alpha` are units of R, with `u+v=2`.

Write `pi=1+i`. Each unit of R is `epsilon pi^k`, where k is an integer
and `epsilon` is one of `1,-1,i,-i`. The pi-adic valuation of 2 is 2.
If u and v have different valuations, their smaller valuation must be
2. Divide the sum by `pi^2`. The larger remaining power of pi is a
difference of two fourth roots of unity. A nonzero such difference has
valuation 1 or 2. Hence the two original valuations are 2 and either
3 or 4.

If the valuations are equal to k, the sum of their two unit factors is
nonzero. Its valuation is 1 or 2. Thus k is 1 or 0. These two cases
prove that it is enough to check `epsilon pi^k` for `0<=k<=4`; negative
valuations cannot occur. Exact enumeration then gives

```text
alpha in {0, i, -i, 3, -3, 1+2i, 1-2i, -1+2i, -1-2i}.
```

Every nonzero candidate fails at one of `S=3I` and `S=-3I`. The norm of
the corresponding `1+alpha S` scalar has an odd factor: the rejecting
norms are among 10, 40, 52, and 100. An element of R is a unit only if
its nonzero norm is a power of two, with an integer exponent. This
contradiction proves the claim for every nonzero constant alpha in R.

The checker verifies the finite unit equation and every rejecting norm.
This is a uniform ring-invertibility obstruction. It is not a native
child lower bound. It does not exclude an exact odd-grid inverse where
the operator is nonsingular, an operator-valued feedback coefficient,
or a joint unit on data and centre fields.

## A constructive consequence with a precise limit

The translation inverse gives an exact right inverse with positive line
orientation. Define

```text
A = B Q_U,
K_plus = Q_U D T^-1.
```

Then `A K_plus = B Q_U^2 D T^-1 = I`. Also,

```text
K_plus = Q_U^2 (q_U D) T^-1,       q_U=Q_U^-1.
```

The extra ordinary factor `Q_U^2` is a translation. The centre factor
`T^-1` has a finite translation implementation with fixed odd
arithmetic. Thus this is a precise operator conversion between a
dense inverse-line scatter and a dense positive-line right inverse.
It does not provide the scatter for free. A physical construction must
still give the selected cut, available centre owners, legal source
access, complete local prices, and the final data and helper endpoint.

The operator S also has the stated nonnormal witness. The review forms
its real and imaginary parts directly from the q labels at width-two
characters `(1,2)`. Their commutator entry `(0,1)` is `1/2`; hence the
same entry of `S* S-S S*` is i. This excludes a single unitary conjugate
of a diagonal phase operator. It does not exclude products of factors.

## Reproduction and status

Run with one process from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/schur-review/check_schur_review.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/schur-review/check_schur_review.py
```

Both runs print `PASS_INDEPENDENT_SCHUR_REVIEW`. Their receipts are
byte-identical. This review covers the spectral theorem, the exact
kernels, the two scoped obstructions, and the algebraic right inverse.
The new literal translation-service word has a separate review. No
complete controller, supplier admission, or kappa improvement is
claimed here. OpenAI Codex assisted this review and its exact checker.
No PR, push, or commit was made. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
