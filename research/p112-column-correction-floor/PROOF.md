# Arbitrary one-column corrections retain the two-coordinate COPY floor

This is a scoped theorem in the separate-term COPY model of PR717/PR968.
It does not assert physical realization or change a selected supplier.
The support-stratum and small-erasure method comes from commdata2338's PR1375,
following Arham Tahir's PR1331. Cinna Davis's PR1373 already gives the
three-active-product obstruction at one coordinate pair for arbitrary
rectangles. This proof removes the size restriction for one-column
or one-row corrections and includes the pure-factor branch for every pair.

The submission refresh found Hanson Sun/bbMisk's concurrent PR1432, covering
the fixed 24-row boundary with arbitrary amplitudes, and PR1460, covering
arbitrary nonzero rectangles at the fixed pair (4,6). The boundary result and
the general idea of charging compensation are credited to that parallel work.
This is an independently derived all-pair one-column proof and complete
certificate. No code or theorem from either concurrent PR is assumed.

## 1. Model and statement

Use the 112 live E8 root lines obtained by deleting the fixed orthogonal
eight-frame in the retained PR845/PR717 geometry. Let X be the real 112 by 8
coordinate matrix, with entries in {0,1,-1} and XX^T=2G. Binary labels l_i
are distinct and nonzero and span a nine-dimensional space with a
nondegenerate symmetric form B satisfying

`B(l_i,l_j) = (G_ij+1) mod 2`.

In particular B=1 on the diagonal and on orthogonal pairs, and B=0 on
odd-inner-product pairs. A scalar term d t^T costs

`rho(d,t) = rank_F2 B[supp(d),supp(t)]`.

Complex scalar values determine whether entries vanish; they are not reduced
modulo two. Every transpose in the scalar decoder is ordinary transpose.

Fix any two distinct coordinate columns x,y of X and any live index j. Let
`O_j={i:B(l_i,l_j)=0}`; every such set has 52 indices. Choose any complex
u supported on O_j, including zero, and v=lambda e_j with lambda nonzero.
Thus u v^T is a free correction on the unconstrained odd entries. For any
M in GL(3,C), set

`D=[x,y,u] M`, `T=[x,y,v] M^(-T)`.

These three terms replace xx^T+yy^T by xx^T+yy^T+uv^T; the other six
coordinate terms remain fixed. The complete nine-term product equals
2G+uv^T on every entry and 2G on every constrained even entry. Transposing
the construction gives the corresponding arbitrary one-row correction.

**Theorem.** For every such choice, if r_1,r_2,r_3 are the replacement
COPY ranks, then for every real 0<q<=1,

`r_1^q+r_2^q+r_3^q >= 2*8^q`.

The complete COPY sum is at least 64 and the complete COPY power bill is
at least 8*8^q. Both bounds are sharp for every allowed u,v: M=I has
replacement ranks (8,8,0). There is no size cap on supp(u) beyond its actual
free-neighbor domain O_j, and no restriction to real or rational amplitudes.
The statement concerns all 28 coordinate pairs and all 112 singleton sites.

## 2. Complete finite geometric premises

Every nonzero complex combination ax+by has one of five supports:
x, y, x+y, x-y, or the union supp(x) union supp(y). Indeed, rows with two
nonzero coordinates can cancel only at coefficient ratio +1 or -1; the
coordinate axes give the first two cases. Every remaining complex ratio
has the union support. This is an exhaustive algebraic classification.

For each pair the binary support spans and erasure distances are:

| Stratum | Size | Span dimension | Positive erasure distance | Free-compatible distance |
|---|---:|---:|---:|---:|
| x | 56 | 8 | 24 | 24 |
| y | 56 | 8 | 24 | 24 |
| x+y | 76 | 9 | 12 | 34 |
| x-y | 76 | 9 | 12 | 34 |
| generic union | 88 | 9 | 24 | 40 |

These facts and the original pairing ranks reproduce PR1375, with credit.
The erasure distance is the minimum nonzero weight of a binary functional
on the support. The free-compatible minimum restricts to those positive
functional supports having a common odd neighbor. All 511 nonzero
functionals are tested for all 140 supports, including zero weights in the
complete spectra. All 700 ordered within-pair support pairings have rank
at least eight: 448 have rank eight and 252 have rank nine.

Two consequences are used:

1. Deleting any singleton preserves the span of every stratum, since all
   positive erasure distances are at least twelve. The program also directly
   checks all 15,680 singleton deletions.
2. If U is contained in an odd neighborhood and |U|<=23, deleting U
   preserves the span of every stratum. Otherwise a functional annihilating
   the survivor span but not the original support has a nonempty support
   W contained in U. The common odd neighbor of U is also one for W,
   contradicting the free-compatible minimum of at least 24. This includes
   U empty, where preservation is immediate.

The additional finite premise, covering complete odd-neighborhood erasure,
is particularly simple. For every one of the 28 pairs and every j,

`dim span{l_i : i in S and B(l_i,l_j)=1} >= 7`

for each stratum S. All 15,680 ranks are computed and independently checked:
6,272 have rank seven and 9,408 have rank eight. The x and y strata have
rank seven in every slice; the other three have rank eight. Thus deleting
*any* subset of O_j leaves at least seven dimensions. This bound does not
require preservation of the original span.

These are complete finite facts about the specified geometry, not samples
of M or complex amplitudes. The primary engine uses the pinned simple-root
labels and high-pivot elimination. The second engine constructs the Euclidean
root lines, derives B directly from their Gram matrix, represents labels by
full 112-bit pairing evaluations, generates the complete dual code, and
eliminates from low pivots. It imports no primary or predecessor geometry.
The two engines compare every support, spectrum, slice, pairing and receipt
field; they share only serialization/integrity utilities.

## 3. Support containment and the coupled factor identity

Put N=M^(-T). Write a_h in C^2 for the first two entries of column h of M,
and b_h in C^2 for those of column h of N. The corresponding factors are

`d_h = a_0h*x+a_1h*y+M_2h*u`,
`t_h = b_0h*x+b_1h*y+N_2h*v`.

The top-left block of M N^T=I gives

`sum_h a_h b_h^T = I_2`.

Consequently at least two products have both a_h and b_h nonzero: a sum
of fewer than two rank-one matrices cannot have rank two. On each side
there is at most one column with zero original-coordinate projection,
because the first two rows of an invertible matrix have rank two.

When a_h is nonzero, let S be its stratum support. Outside U=supp(u),
the correction cannot cancel any entry, so S minus U is contained in the
actual support of d_h. In particular S intersect O_j-complement survives,
giving a left span of dimension at least seven. When b_h is nonzero, its
stratum survives outside {j}; singleton erasure preserves the entire
original right span, which has dimension at least eight.

For two subspaces A,C of the nine-dimensional nondegenerate label space,

`rank B[A,C] >= dim(A)+dim(C)-9`.

This follows from dim(A intersect C-perp)<=9-dim(C). Pairing rank is
monotone under enlarging either support. Hence every product with both
original projections nonzero costs at least six, for arbitrary U.

If |U|<=23, the stronger erasure fact preserves the entire original left
span as well. Each of the at least two active products then retains its
original stratum pairing of rank at least eight. This proves the theorem
in the small-support branch, including u=0, and reproduces the applicable
part of PR1375.

## 4. The large-support branch and the pure-factor charge

Assume |U|>=24. There are three cases, exhausted by the projection pattern.

**A right factor has zero original-coordinate projection.** Suppose b_h=0.
Since N is invertible, its column is (0,0,c)^T with c nonzero. The identity
M^T N=I implies M_2k=0 for every k different from h. Therefore the other
two left factors are pure nonzero combinations of x,y, with no u cancellation.
Their right projections are nonzero and singleton erasure preserves the
original right support spans. Both products have pairing rank at least
eight by the original stratum table. This uses the coupled inverse, not
independent choices of factor supports.

**All right projections and all left projections are nonzero.** All three
products cost at least six by Section 3. This is the three-active branch
already studied for arbitrary rectangles at one pair in PR1373; here the
finite premises cover every pair in the one-column domain.

**All right projections are nonzero, and one left projection is zero.**
The latter factor is a nonzero scalar multiple of u, since its column of
M is nonzero. Its support is exactly U. Distinct nonzero binary labels in
a space of dimension at most four would give at most 15 labels. Since
|U|>=24, the label span of this factor has dimension at least five. Its
right partner, which has nonzero original projection, has span at least
eight. The pairing-rank inequality therefore charges this pure factor
at least 5+8-9=4. The other two products each cost at least six. After a
permutation, the three ranks dominate (6,6,4).

Discarding this last factor would erase the charge that closes the
exactly-two-projected-product branch. This argument does not equate a
zero coordinate projection with a zero factor or a free COPY.

## 5. The complete power comparison

The proof gives one of the componentwise lower envelopes, up to permutation:

`(8,8,0)`, `(6,6,6)`, or `(6,6,4)`.

For 0<q<=1 and 0<=t<=8, `(t/8)^q >= t/8`. Each of the displayed vectors
has total at least sixteen and every entry at most eight. Its sum of q-th
powers is therefore at least 2*8^q. Monotonicity transfers this to the
actual ranks, which may be larger. Adding the six unchanged rank-eight
terms proves the complete floor 8*8^q. At q=1 it is the rank sum 64.
For q>1 this particular comparison fails, for example
6^2+6^2+4^2=88<128=2*8^2; the exponent domain is essential.

For unchanged width, normalization and common multiplicity, set q=1-a.
The new separate COPY contribution cannot beat the baseline at any
0<=a<1, even if every additional gathering, preparation, frame conversion,
mixing, restoration, hosting and management charge is granted zero.
This is a necessary-condition screen with six other terms fixed. It does
not bound changes in other work, normalization, shared-COPY semantics or
an entirely different supplier contract.

## 6. An exact boundary where the former per-child assertion fails

Use PR1375's canonical pair (0,1), singleton site j=0 and its published
24-row free-boundary support U, in the pinned canonical root order:

`27,28,31,32,69,70,73,74,77,78,81,82,85,86,89,90,93,94,97,98,103,104,107,108`.

Define u_i=x_i on U and zero elsewhere, and v=e_0. This is a valid free
correction: U has common odd neighbor {0}. The label span of U is seven;
deleting it from supp(x) lowers that span from eight to seven.

The matrix

```
M = [ 1 0 0 ]
    [ 0 1 0 ]
    [-1 0 1 ]
```

gives D=[x-u,y,u] and T=[x,y,x+v]. Their replacement ranks are exactly
(7,8,7); only one rank is at least eight. Nevertheless their sum is 22
and the complete COPY sum is 70. Original mixing gives (8,8,0) and 64
for the same completion. The shifted factor cannot be dropped: that would
remove u(x+v)^T from the identity. The full factors have rank nine and
the verifier checks every one of the 12,544 scalar entries. Transposition
gives the same counterexample on a row correction.

This example is independently reproduced, not claimed as a new boundary
finding. Hanson Sun/bbMisk's concurrent PR1432 proves the fixed-support theorem
for arbitrary amplitudes and supplies the same (7,8,7) example. Our proof
covers arbitrary amplitudes on all one-column supports. PR1375's original
<=23 result remains valid. PR1460 independently handles arbitrary nonzero
rectangles at (4,6), using a compensation-support argument; its theorem was
not imported or re-verified by this package.

## 7. Limits

Rectangles with at least two rows and two columns, more than two mixed
coordinate terms, other punctures and shared-COPY pricing remain open
here. This is a written proof with complete finite premises, not a Lean
proof or independent human review. No physical word, legal frame itinerary,
restoration schedule, owner/hosting admission, native replay, selected cold
replay, precision/tape proof, all-size compiler or analytic transfer is
provided. No new multiplication bound follows.
