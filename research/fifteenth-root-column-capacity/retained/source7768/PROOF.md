# A strict column-defect bound

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Let q>=5 be prime, b>=1, n=q+3 and 1<=m<=n. Suppose that A is an
n-by-m matrix over the roots of order 3q^b and A* A=nI. Set d=n-m.
Then

```text
m^2 < d^2(4d-3).
```

This is a necessary condition, not an existence theorem. It excludes an
eight-by-six matrix for every alphabet of order 3*5^b. It strengthens the
n-by-(n-1) obstruction in [PR #7762](https://github.com/CrocSwap/integer-mult-bounds/pull/7762).
At q=101 it excludes 91 columns in 104 rows; the strict inequality is
needed in this example. No physical supplier or new kappa follows.

## 1. The rectangular Hermitian block

Write omega for a primitive third root and eta for a primitive q^bth
root. The m<=3 case satisfies the bound directly: n>=8 gives d>=5.
Assume m>=4 from now on.

The projected-star proof in
[the pinned source, Section 1](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/PROOF.md)
applies without the n-1-column restriction. Here are the required steps.
Every zero column inner product has length q+3. The two-prime cycle
theorem makes it one 3-cycle and one q-cycle, because 3r+qs=q+3 has
only the solution r=s=1 in nonnegative integers. Discarding the eta
component gives projected Gram diagonal n and off-diagonal q times a
third root. An unbalanced triangle has determinant -3q^3+27q+27<0.
Thus column phases make every off-diagonal projected Gram entry q.
[Lam and Leung, Theorem 3.3 and Corollary 3.4](https://arxiv.org/pdf/math/9511209#page=7)

Make the first projected column constant. Each other column then has
omega at one row, omega squared at another, and 1 elsewhere. Two such
ordered pairs are compatible exactly when they have the same first
row, the same second row, or are reverses. A reverse pair admits no
third pair. At least three pairs therefore form one directed star.
Its m-1 leaves and centre use m rows; d rows remain unused.

If the centre exponent is s, multiply its row by omega^(-s). Order the
used rows so that the constant column matches the centre, and each
other column matches its leaf. The projected top m-by-m block has
omega^(-s) on its diagonal and 1 elsewhere. All bottom entries are 1.
Scale columns by eta powers to make every top diagonal q-part 1.
These operations preserve the alphabet and column orthogonality. Write

```text
A = Q + lambda E,       Q = [ K ],       E = [ I_m ],
                           [ R ]           [  0  ]
lambda = omega^(-s)-1.
```

K is m-by-m, R is d-by-m, all their entries are q^bth roots, and K_ii=1.
For columns i,j, the only two terms with a nontrivial third-root part
occur at rows i,j. The unique 3-cycle must contain both with equal
q-parts. These q-parts are K_ij and conjugate(K_ji), so K is Hermitian.
As lambda+conjugate(lambda)=-3 and |lambda|^2=3, orthogonality gives

```text
K^2 - 3K - qI = -R*R.                         (1)
```

In particular, the left side has rank at most d. No completion formula
or extra missing columns were assumed.

## 2. Equal quadratic-root multiplicities

Put F=Q(eta), Delta=4q+9 and p(t)=t^2-3t-q. Delta is 5 modulo 8,
so it is not a rational square; also q does not divide Delta.
The unique quadratic subfield of Q(zeta_q) is Q(sqrt(q*)), where
q*=(-1)^((q-1)/2)q. See
[Sharifi, Algebraic Number Theory, Lemma 3.2.2](https://www.math.ucla.edu/~sharifi/notes/algnum-ch03.html).
The extension F/Q(zeta_q) has odd degree q^(b-1). A quadratic subfield
of F must therefore lie in Q(zeta_q): its compositum with that field
would otherwise have degree two in an odd-degree extension.

The q-adic valuation of Delta is zero, while that of q* is one.
Their ratio cannot be a rational square. Thus Q(sqrt(Delta)) is not
this quadratic subfield, and p is irreducible over F.

The characteristic polynomial of K lies in F[t]. The two roots of p
have the same multiplicity k in it. K is Hermitian, so it is
diagonalizable. Let h=m-2k count its other eigenvalues. Equation (1)
gives h<=d. Each entry of K has modulus one, so

```text
trace(K) = m,                   trace(K^2) = m^2.
```

The sum and squared sum of the other h real eigenvalues are therefore

```text
T = m-3k = (3h-m)/2,
E2 = m^2-k(2q+9) = m^2-(m-h)(2n+3)/2.
```

Cauchy's inequality gives T^2<=h E2. This also holds when h=0,
where both actual sums must be zero. After multiplication by four,

```text
F(h) = (4n-3)h^2 - 4mdh - m^2 >= 0.           (2)
```

If d=0, h=0 contradicts F(0)=-m^2. Thus d>0. On [0,d], F is convex
and F(0)<0. Equation (2) implies F(d)>=0. Equivalently,

```text
m^2 <= d^2(4d-3).                              (3)
```

For a direct check, the chord excess is

```text
h F(d) + (d-h) F(0) - d F(h)
    = (4n-3)d h(d-h) >= 0.
```

## 3. Equality is impossible

Suppose equality holds in (3). The strict chord inequality in the
interior, and F(0)<0, force h=d and equality in Cauchy. All h remaining
eigenvalues of K are one common value

```text
beta = (3d-m)/(2d),             p(beta) = -m.
```

The second identity follows from m^2=d^2(4d-3) and q=m+d-3.
Equation (1) now says that `R*R` has nonzero eigenvalue m with
multiplicity d. Thus `RR*=mI_d`. The bound forces d>=2, so two rows of
R give a zero sum of m roots of order q^b.

Such a zero sum has length divisible by q. One direct proof writes
its multiplicities in a polynomial f of degree less than q^b. Since
Phi_(q^b) divides f, f(1) is divisible by Phi_(q^b)(1)=q. Hence q|m
and q|(d-3). But m>=4 gives 0<=d<=q-1, so this forces d=3. Equality
then gives m=9 and q=m+d-3=9, contrary to primality. This proves the
strict bound.

At q=101, the non-strict spectral relaxation allows m=91,d=13,
k=39 and beta=-2. The row-orthogonality argument removes that case.
Thus the strict conclusion is stronger than the trace relaxation.

## Evidence and limits

The checker authenticates all sixteen retained source files and runs
the PR7762 verifier unchanged, including its PR7744 replay. New exact
checks use the retained prime-power cyclotomic basis arithmetic.
There are 36 rectangular fixtures: q in {5,7,11}, b in {1,2},
m in {4,n-1,n}, and both star orientations. All 2,828 Gram entries
agree with (1), including nonempty and empty R blocks. Four altered
formulas fail. Synthetic block fixtures test the identity; they are
not claimed to be orthogonal examples of A.

The three polynomial identities have degree at most four in each
variable. They agree on a five-point grid in each variable, which
determines every coefficient over Q. This verifies all coefficients,
not only a sampled numerical inequality. Separate integer calculations
check all 11,193 possible multiplicity cases for the 24 primes from
5 through 101. They recover the strict equality control above.
A union of one 3-cycle and one q-cycle gives a valid two-column
positive control in each fixture alphabet; deleting a term fails.

| q | Rows | Minimum defect from this bound | Maximum columns from this bound |
| --- | --- | --- | --- |
| 5 | 8 | 3 | 5 |
| 7 | 10 | 3 | 7 |
| 11 | 14 | 4 | 10 |
| 13 | 16 | 4 | 12 |
| 17 | 20 | 5 | 15 |
| 101 | 104 | 14 | 90 |

The general theorem is the written argument. It uses the classical
cycle and quadratic-subfield theorems. The finite checks do not replace
these inputs. The upper bounds need not be attained. Other row counts,
larger powers of three, more prime factors, approximate orthogonality,
physical preparation and complete caller pricing remain open.
All five framework assumptions remain. No selected cold replay,
Lean, Docker, independent human acceptance or formal proof kernel was
used. No global literature priority is claimed.
