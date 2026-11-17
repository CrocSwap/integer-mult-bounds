# Sharp error with norm-bounded rectangular adapters

This is a scoped written proof over the complex numbers, with exact finite
corroboration. It is not a physical fusion construction or a multiplication
theorem. The result was produced by Nick Petalas.

## Model and theorem

Put a=(1+i)/2, b=(1-i)/2 and

```
C = [a b; b a],  U_f = C^(tensor f).
```

Let f>=1 and r>=2 be integers. Write d=2^f, N=2^(rf), and
alpha=sqrt(d/N)=2^(-(r-1)f/2). The target is T=diag(U_f,U_f), on two
independent d-coordinate inputs. Every target column has exactly d nonzero
entries of modulus 1/sqrt(d) and Euclidean norm one.

Permit any finite spectator multiplicity s>=1 for the child K=I_s tensor U_(rf).
Every child entry has modulus at most 1/sqrt(N). Permutations and unit
rephasings of the child preserve this fact and the lower bound below.

The relaxed returned map is F=BKA+H. Both adapters may be rectangular, complex,
width dependent and singular. For a prescribed real M>=0 require

```
||A||_1 ||B||_infinity <= M,
```

where these are maximum absolute column sum and maximum absolute row sum.
The bypass H has at most h nonzeros per column, for an integer 0<=h<=d. It has
no coefficient-size, row-support or implementation restriction. Additional
workspace may be initialized and discarded; no inverse is required.

Define E_col(F,T)=max_j ||(F-T)e_j||_2. This is precisely the induced
l1-to-l2 norm of F-T. Define E_rms(F,T)=||F-T||_F/sqrt(2d), the root mean
square of the Euclidean column errors.

**Theorem.** In this relaxation, allowing any finite spectator multiplicity,
the minimum of either error is

```
E_min(f,r,M,h) = sqrt(1-h/d) max(0, 1-M alpha).
```

Both minima are attained simultaneously with s=2. The lower bound applies to
each individual column for every permitted s. In particular, restricting the
bank stock cannot invalidate this necessary bound, but may remove its attainer.

## Lower bound

For every pair of external indices i,j, the triangle inequality gives

```
|(BKA)_ij|
 <= max_uv |K_uv| sum_u |B_iu| sum_v |A_vj|
 <= M/sqrt(N).
```

In column j, at most h of the d nonzero target positions can belong to the
support of H. At each of the remaining at least d-h positions,

```
|(T-F)_ij| >= max(0, 1/sqrt(d) - M/sqrt(N)).
```

Squaring and summing just those positions gives the stated squared lower
bound for every column. Taking a maximum or an average proves both claims.
This proof allows arbitrary cancellation, cross-spectator mixing and arbitrary
coefficients in both adapters. It uses no assumption of a reversible decoder.

## Attainment

Take s=2 and K=diag(U_(rf),U_(rf)). Let E embed each target lane into its
own child block by fixing the high (r-1)f tensor coordinates at zero. Let P
project the same coordinates back out. Since C_00=a,

```
P K E = a^((r-1)f) T.
```

Set m=(r-1)f, gamma=min(1,M alpha), A=E and
B=gamma a^(-m) P. Each encoder column has one unit entry, and each readout row
has one entry of modulus gamma/alpha. Thus

```
||A||_1 ||B||_infinity = gamma/alpha <= M,  B K A = gamma T.
```

For each column choose any h of its d target positions and set H to
(1-gamma)T there and zero elsewhere. Its column support is at most h.
The error is zero on the chosen positions and (1-gamma)T on exactly d-h
others. Every column therefore has squared error
(1-h/d)(1-gamma)^2. This equals the lower bound, including M=0, h=d and the
zero-error norm threshold M=1/alpha.

The construction uses 2N child coordinates for 2d external coordinates, a
bank expansion N/d=2^((r-1)f). Moreover the bypass is only a sparse linear
map in this relaxation. No preparation, coefficient, routing, precision,
restoration, returned-owner or tape cost has been supplied for it. Attainment
of the mathematical minimum does not supply an affordable paid child.

## Consequences and one exact example

For fixed M and r>=2, if h/2^f tends to zero, both minimum errors tend to one.
Thus this norm-bounded class cannot approach even a fixed error less than one
using a sublinear number of bypass entries per column. This statement concerns
the retained normalization and these two error metrics.

When M alpha<1 and a prescribed tolerance delta satisfies
0<=delta<1-M alpha, the exact minimum bypass support is

```
ceil(d [1-(delta/(1-M alpha))^2]).
```

At f=8, r=2, M=1, alpha=1/16. Error at most 1/2 requires h>=184 out of
256 target positions per column. The verifier enumerates all 257 integral
supports to obtain this threshold. The formula is sharp in the same relaxed
model. It is not a spectral-norm optimum, an error estimate for a full rounded
caller, or a recursive invoice.

## Relation to predecessor work

ToikY's [#7166 proof](https://github.com/ToikY/integer-mult-bounds/blob/6efb5d028b3212fba68edfb725608413622d6ab6/research/p104-rectangular-clifford-adapter-bound/PROOF.md)
supplies the exact rectangular amplitude obstruction and the projected tensor
control. Those are credited starting points. The new step counts every target
position missed by the bypass, proves a positive approximation floor and shows
that this floor is the exact relaxed optimum for every parameter above.
No predecessor scientific verifier or count is replayed.

Earlier fusion boundaries include Clear1nsight's #4932 Fourier-grade model,
#4045 monomial model and #3989 paid nonmonomial transfer. Their physical words,
counts and recursive bills are not assumptions of this self-contained theorem.
The Gaussian tensor normalization follows the retained native lineage,
including zxv, Clear1nsight #7161 and Rohan Arun #7113 as credited in #7166.

## Verification boundary

The universal quantifiers rest on this written proof. The finite checker uses
Gaussian-rational pairs, literal rectangular matrix multiplication and separate
Kronecker/bit-count constructions. It tests six (f,r) pairs with rf<=6, five
rational gains and every support h in each target lane. Gains parametrize
M=gamma/alpha exactly, so odd m is checked without floating point. Additional
mixed-lane rectangular adapters and bypasses test the lower bound at even m.
All checks remain active with Python optimization enabled.

The Python verifier has managed-runtime allocation and diagnostic limits.
Fraction arithmetic, matrices and Python runtime objects allocate
dynamically. All matrices have at most 128 rows and columns, exponents are at
most six, and the fixture lists bound every loop. This compensates the memory
deviation only within this finite checker. Warning-strict normal and optimized
runs plus source compilation are the available diagnostics; a repository-wide
static-analysis policy is outside this isolated package. A larger fixture must
first raise and justify these explicit capacities. The checker has no recursive
calls, network access or subprocesses; its sole optional write creates a new
receipt with exclusive creation and refuses overwrite.
