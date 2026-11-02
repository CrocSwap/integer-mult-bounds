# Exact determinant across an eliminated Gaussian interior

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let F be a field, let integers m>=b>=1, and index a matrix H by
0,...,m+2b-1. Assume H[i,j]=0 for |i-j|>b. Put

```text
L = {0,...,b-1}, E = {b,...,b+m-1}, R = {b+m,...,m+2b-1},
A = H[E,E], S = H[L union R,L union R]
                  - H[L union R,E] A^-1 H[E,L union R].
```

Assume A is invertible. All subsets inherit increasing order. Then

```text
det S[L,R] = (-1)^(bm) product(i=0,...,m+b-1, H[i,i+b]) / det A.    (1)
```

Consequently this b-by-b cross-rim block is invertible if and only if
every displayed outer-band entry is nonzero. No symmetry, definiteness,
Toeplitz assumption, or full-host invertibility is needed.

For the truncated Gaussian H[i,j]=t^((i-j)^2) when |i-j|<=b, zero
otherwise, with t any nonzero field element and A invertible, (1) becomes

```text
det S[L,R] = (-1)^(bm) t^(b^2(m+b)) / det A != 0.                (2)
```

The statement uses field exponentiation and is meaningful in every
characteristic. The finite checker uses rational arithmetic only.

## The triangular minor

Take the square minor B with rows 0,...,m+b-1 and columns b,...,m+2b-1.
In its local coordinates, B[i,j]=H[i,j+b]. If j>i then j+b-i>b, so
B[i,j]=0. Thus B is lower triangular, and

```text
det B = product(i=0,...,m+b-1, H[i,i+b]).                        (3)
```

Move its first b rows, indexed by L, past its last m rows, indexed by E.
This changes the determinant by (-1)^(bm). Its columns are already E,R.
The permuted matrix is

```text
[ H[E,E]  H[E,R] ]
[ H[L,E]  H[L,R] ].
```

The elementary block determinant identity, obtained by subtracting
H[L,E] A^-1 times the top block row from the bottom, gives determinant
det A times det S[L,R]. Combine this with (3) to prove (1). Each of
the m+b outer-band entries of a Gaussian is t^(b^2), giving (2).
These determinant identities are classical. The contribution is their
exact specialization to this retained Gaussian elimination boundary.

The condition m>=b makes H[L,R]=0, so the whole cross-rim block is
created by elimination. The proof does not need to assume that S itself
is invertible. Its diagonal and opposite cross block are unrestricted.

## A sufficient real domain and gauges

For real 0<t<=1/3, every interior A in the theorem is positive definite,
so (2) applies without a separate nonsingularity premise. Indeed its
off-diagonal row sum is at most

```text
2 sum(h=1,...,b, t^(h^2))
 <= 2 sum(h=1,...,infinity, t^(2h-1))
  = 2t/(1-t^2) <= 3/4 < 1.
```

For a real vector x, 2|x_i x_j|<=x_i^2+x_j^2 then gives
x^T A x >= (1-max_row_sum) sum_i x_i^2 > 0 for nonzero x.
This is the classical diagonal-dominance argument, not a new positivity
theorem. PR5207 already proves stronger ordered-minor positivity in this
range. Its result is credited rather than re-verified here.

If H'=D H Q for invertible diagonal D,Q, substitution into the Schur
formula gives S'=D[L union R] S Q[L union R]. In particular

```text
det S'[L,R] = product(i in L,D[i,i]) product(j in R,Q[j,j]) det S[L,R].
```

All interior gauge factors cancel. Hence the rank conclusion survives
arbitrary nonzero field-valued diagonal gauges, including signs or complex
phases. This does not bound their condition numbers, rounding errors or
implementation costs. Applying this identity to an actual caller still
requires its exact truncated-kernel and gauge contract.

## Exact channel obstruction

Any exact linear implementation whose entire R-to-L dependence factors
through k scalars has S[L,R]=U V, with U of size b-by-k and V of size
k-by-b. Matrix rank is at most k. Equation (2) therefore forces k>=b.
This is a bound on that complete linear factorization. It is not a bound
on the number of machine instructions, recursive calls or helper roles,
and says nothing about an implementation retaining additional direct
R-to-L paths. Arbitrary dirty state cannot change the conclusion if the
claimed final map still has this factorization on every independent input.

For b=2, m=3, t=1/2, the verifier obtains det A=135/256 and
det S[L,R]=1/552960. Thus even a short real Gaussian interior with
t>1/3 has no one-scalar exact factorization. This is a new exact
determinant fixture; it is not a replay of the predecessor sign census.

## What changes for the next construction

The bandwidth bound 2b-1 is a support statement. Full cross-rim rank b
also excludes a fixed rank below b as an exact compression of this
boundary, however long the eliminated interior is. Earlier real-entry
results imply nonvanishing minors in their sufficient t range; (1)-(2)
give their exact determinant and show there are no additional exceptional
nonzero Gaussian parameters in any field once A is nonsingular.

Approximate compression may still be useful because full rank alone gives
no useful lower bound on singular values. This proof changes neither the
O(b) representation cost already allowed by the caller nor the selected
frontier. It does not establish an all-size native supplier, numerical
recovery, the five framework assumptions or a multiplication theorem.
