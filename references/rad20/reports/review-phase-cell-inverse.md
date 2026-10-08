# Independent review of the phase-cell Gaussian inverse

The phase-cell replacement is valid after the explicit downward-weight
approximation repair. The reviewed construction preserves the scalar
disk/error interface and fixed finite-tape model while reducing inverse
application to short Toeplitz convolutions and a smaller cyclic boundary
solve. No remaining all-size precision, endpoint-cell, or amortization gap
was found. This is a conditional transfer conclusion: the original
complete multiplication interfaces and the separately certified finite
motifs remain inputs, not newly established results of this review.

Campaign: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Reference: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.
Reviewed derivation: [downstream-phase-cell-inverse.md](downstream-phase-cell-inverse.md).
This review continues the independent [banded inverse audit](review-reusable-banded-inverse.md).
Fresh evidence: `runs/20261007T235722Z-review-phase-inverse`.

## Scope and retained prerequisites

Retain `rho=t/s=1+theta`, the nearest-integer indices with ties upward,
periodic `beta_j` in `[-1/2,1/2)`, `u=alpha^2`, and the exact Gaussian
matrix `N=I+E`. The preceding independent review established, for
`p>100`, `u>=ceil(log2(8p))`, `theta>1/(4p)`, and `1<rho<2`,

```text
||E||<1-mu,
mu=min(u*theta,1)/4>=1/(4p),
||N^-1||<=4p.
```

It also established that width `w=ceil(sqrt(16p/u))+2` leaves total
periodic lattice tail below `2^(-46p)`, including diagonal aliases. The
actual prime intervals give `1/(4d)<theta<1/(2d-1)`. The forward blocked
Gaussian map and normalized positive diagonal evaluation retain their
previous proof. The phase route changes the inverse application and
stopped-guard estimate.

## Cells, endpoint exceptions, and exact structure

Write `K=t-s`. Since the physical index is integral,
`q_j-j=round(Kj/s)`. The full phase cells have floor or ceiling `s/K`
points. The first cell has `ceil(s/(2K))` points and the last has
`floor(s/(2K))`; the end cells are separate, with their cyclic interaction
handled at the boundary. In particular every cell has between `d-2` and
`4d+1` points. There are exactly `K+1` cells. When
`epsilon>(1-r)/2`, `d/w` tends to infinity and eventually every cell
has more than `4w` points. There is no unaccounted short end cell.

An addition/comparison generator suffices. Initialize remainder `R=s`
and phase zero. At index `j`,
`R=2Kj+s-2s*phase`, `0<=R<2s`. Then the phase is `q_j-j` and
`beta_j=(R-s)/(2s)`. Advance by adding `2K`; if `R>=2s`, subtract
`2s` and increment the phase. Because `K<s`, one subtraction suffices.
Each index therefore needs O(p)-bit additions and comparisons; the proof
does not hide a large-integer division for every input record.

Within one cell the rounding jump `g` is zero. The independently reviewed
weighted identity gives

```text
u*phi(j,l-j)=u*rho*(l-j)^2+F_j-F_l,
F_j=u*(1/4-beta_j^2)/theta.
```

Thus the cell matrix equals `diag(a) G diag(a)^-1`, where
`a_j=exp(-pi*F_j)` and `G_delta=exp(-pi*u*rho*delta^2)`. The common
constant in `F` scales all weights equally. Under the explicit eventual
`ud<=p` cutoff, `2^(-8p)<a_j<=1`.

Crucially, the within-cell Toeplitz matrix keeps the same width-`w`
truncation. Keeping its full dense Gaussian tail would invalidate the
sparse coupling and smaller-boundary argument. The reviewed derivation
does retain this truncation.

## Computable rounding and perturbation

At work precision `P=32768p`, put `eta=2^-P`. A finite exponential oracle
does not necessarily return the exact downward P-grid rounding of an
irrational weight. Use Harvey--van der Hoeven Lemma 2.13, subtract two
ulps from its real approximation, and clip at zero. This produces a
computable lower approximation with error below `4eta`. The original
phase draft's `<eta` wording was repaired accordingly before approval.
The same routine supplies the truncated Toeplitz coefficients.

Define the rational within-cell entries exactly by
`a_hat_j*G_hat_delta/a_hat_l`; across cells use downward dyadic entries.
The diagonal is one. This structured matrix `H` preserves Toeplitz
similarity exactly, but its within-cell entries can be slightly above
the true entries. Therefore downward row dominance cannot simply be
reused. Independently expanding the weight-ratio error gives

```text
||H-N|| < p*2^(16p+7)*eta+2^(-46p).
```

This is below `mu/2`, giving `H` row-dominance gap at least `mu/2`, row
norm below two, and `||H^-1||<=8p`. Its exact rational numerators and
denominators have O(p) bits. The non-dyadic ratios are setup objects;
online coupling entries are rounded separately to O(p)-bit dyadics.

## Gohberg--Semencul identity and local conditioning

For a symmetric truncated Toeplitz interior matrix `G`, its off-diagonal
row sum is below `1/8`. Thus `G` is positive definite and its inverse has
row norm below two. Symmetry also bounds the first inverse column's
l1 norm below two. Let `x=G^-1 e_0`; then `x_0>1/2`. Put
`z=(0,x_(L-1),...,x_1)` and write `L(v)` for a lower triangular Toeplitz
matrix. The reviewed orientation is

```text
G^-1=(L(x)L(x)^T-L(z)L(z)^T)/x_0.
```

There is a short independent displacement proof. Let `J` be the lower
shift. Symmetric Toeplitz matrices are invariant under reversing both
coordinates, so their inverse's last column is the reversal of its first.
Block inversion at the first and last coordinate shows

```text
G^-1-J G^-1 J^T=(xx^T-zz^T)/x_0.
```

Indeed the shifted lower-right block and upper-left block have the same
inverse of the size-`L-1` principal Toeplitz matrix; their differences
are the two corresponding outer products. On the first row/column the
identity reduces to the definition of `x`. On the other hand,
`L(v)L(v)^T-J L(v)L(v)^T J^T=vv^T`. The two candidate inverses have
the same displacement. Recursing from the first row and column uniquely
determines every entry, proving the formula. The size-one case also
holds, with `z=0`.

The general identity is equation (2.4) in Ting-ting Feng, Gang Wu, and
Yimin Wei, *Inexact Shift-and-Invert Arnoldi for Toeplitz Matrix
Exponential*, arXiv:1503.04886v1, submitted 2015-03-17 00:57:32 UTC.
[Primary manuscript](https://arxiv.org/abs/1503.04886v1). The paper supplies
the established formula; this audit derives the specialized bounds and
does not assume generic numerical stability. The primary PDF identity,
hash and date are retained in the run protocol.

Each of the four triangular products is an ordinary convolution on a
single cell. Reverse the input for an upper product and reverse the
retained first `L` results. Signed real/imaginary parts use a fixed number
of nonnegative integer packings. Coefficient guards include O(p) integer
bits for the weight reciprocal, O(log p) summation bits, and exact product
fractional bits. The unconditional published multiplier is invoked only
on O(Lp)-bit integers, with `L<=5p`; its cost is
`O(L*p^(1+delta))`. There is no invocation of the stronger multiplier
being investigated.

## Explicit local and global error chains

Let `K_a=||diag(a_hat)^-1||<=2^(8p+1)` and `L<=5p`.
Each exact triangular Toeplitz factor has norm below two; its rounded
factor differs by at most `L*eta` and has norm below three. Each product
is exact on the packed dyadics until one completed-coordinate rounding.
The rounded weight reciprocal/input step has error
`O(eta)*max(1,||b||)` and magnitude O(`K_a max(1,||b||)`). A convolution
therefore propagates at most three times the preceding error, plus
`L*eta` times the preceding exact magnitude, plus its rounding unit.
Apply this to both two-factor chains, then subtraction, the rounded
reciprocal of `x_0`, and the final `a_hat` multiplication, whose norm is
at most one. Including both real components, the total local bound can
be chosen as

```text
2^14 * p * 2^(8p) * eta * max(1,||b||),
```

well below the report's allowance
`LA=2^(32p)*p^8*eta*max(1,||b||)`. This is an absolute-error bound.
Subtraction may cancel large intermediate terms, but no relative-error
assumption is used.

The boundary Schur complement is row-dominant with gap at least `mu/2`
and inverse norm at most `8p`. Rounding its entries before LU leaves gap
at least `mu/4`. Its no-pivot banded factors and cyclic correction have
polynomial norms as in the preceding inverse review. The fixed changes
in gap and wrap norm fit the conservative allowance
`SB=2^60*p^20*eta*max(1,||b||)`, including the rounded Schur perturbation.

For a unit-norm input, exact interior output has norm at most `8p`, the
boundary right-hand side at most `17p`, the exact boundary solution at
most `136p^2`, and the final interior right-hand side at most `273p^2`.
Each rounded coupling has row error at most `p*eta` and norm below two.
One explicit propagation is

```text
boundary_rhs_error <= 3 LA,
boundary_output_error <= 24p LA+18p SB,
whole_output_error <= 1024p^2 LA+512p^2 SB+2048p^4 eta.
```

Here `LA` and `SB` in the last display are their unit-input allowances;
the stated intermediate norms account for later input scaling. For
`p>100`, this is below `2^(64p)*p^64*eta`. Only a fixed number of
completed maps appears. Taking a maximum over rows/cells introduces no
factor exponential in the number of cells or in `s`.

Perturbing `H` back to `N` adds at most
`32p^2*(p*2^(16p+7)*eta+2^(-46p))`. The work precision leaves total
inverse error below `2^(-p-10)`. The normalized inverse
`N^-1/2^j`, `j=ceil(log2(32p))`, has norm at most `1/8`. Completing
the result and rounding toward zero to the p-grid preserves the disk
interface. Together with the retained forward and diagonal maps, the
same scalar `p^2` error interface and scale
`gamma=d*(2u+j+1)` remain valid.

## Boundary geometry, setup, and fixed tapes

Keep each cell's first/last `w` coordinates as boundary. Its remaining
interior can connect only to that cell's two boundary groups, because
the matrix was truncated to width `w`. Eliminating the interior can fill
between those groups. Original cross-cell entries connect adjacent end
groups; cross-period entries connect the first and last groups. Hence the
ordered boundary matrix is circular-banded with halfwidth at most `2w`,
on `2w(K+1)=O(sw/d)` vertices. Interior elimination preserves row gap
and cannot increase row norm, irrespective of the signs of the filled
entries. The two-cell finite equality case has disjoint wrap groups;
the cyclic solver remains valid when its dimension equals twice its
halfwidth. In the eventual regime many cells are present.

Both coupling matrices have O(w^2) nonzeros per cell. Scan cells in
physical order, retaining their original inputs, computing the first
interior solve and boundary right-hand side, and writing ordered
boundary records. Solve the boundary with the prior forward/backward
banded scans and cyclic correction. Scan cells again for interior
recovery, then merge in inherited order. A constant number of tapes and
O(w)-record endpoint windows suffice. Local convolution and generator
rewinds cost O(Lp) per cell; coupling buffer rewinds cost O(wp) per row.
Reset the online tables after each complete line, at their sequential
volume cost. There is no line-length convolution or random access to
another cell's interior.

All exact rational precomputation is once per tensor axis. Clearing
denominators and using fraction-free elimination bounds determinant and
factor bit lengths by a polynomial in `s,p`. The weights' rational
denominators are finite P-bit integers. A straightforward polynomial
setup algorithm on the fixed tapes is sufficient. Since
`log s=O(p/d)` and fixed `epsilon>0` gives `s=n^o(1)`, this setup,
table conversion and cleanup are `n^o(1)` and can be absorbed into the
asymptotic algorithm. Online records have O(p) bits.

Per-line inverse cost is `O(t*p^(1+delta)*(1+w^2/d))`. Tensoring gives
`O(d*T*p^(1+delta)+T*w^2*p^(1+delta))`; with `Tp=Theta(n)` and
`w^2=O(p/u)`, the normalized exponents are `epsilon+delta` and
`1-r+delta`. This matches the proposed two Gaussian margins.

## Guard, cutoffs, and exact parameter audit

The stopped one-piece depth is the retained `9B^2*d^(5-4beta)`.
For fixed `zeta>0`, the actual piece count is at most
`m*(1+1/zeta)*d^zeta`. Adding the bounded preprocessing/outer/shift
depth gives a valid bound with
`C1=5-4beta+zeta` and `C0=32mB^2*(1+1/zeta)`. For the conservative
choice `zeta=1/20`, `beta>=999/1000`, the separate tighter count gives
`9*21+18=207<256`, so `C0=256mB^2`, `C1=11/10` are sufficient.
The larger generic constant would be 672 at this zeta; it is not the
justification for the stated 256.

The optimized family uses the retained packed/leaf balance root
`x=1-beta`, `C1=1+4x+zeta`,
`epsilon=(1-2^-20)/C1`, `r=(1-epsilon)/2`, and `delta=r/8`.
The guard gap, both Gaussian margins, cell/band separation, prefix,
normalization and remaining recurrence constraints are positive. The
exact checker independently verifies all eight current rows, their
logarithm enclosures, root signs, 32 strict conditions each, and strict
absorption on the 10^-30 grid.

It also verifies full-constant cutoffs: gamma, logarithmic alpha,
`C0*d^C1<b/2`, and `d-2>4w`. For the last, the cutoff ensures
`b^(epsilon-(1-r)/2)>=512`; meanwhile
`w<10b^((1-r)/2)+3` and `d-2>=b^epsilon-3`. The explicit inequality
512>40+15 covers both floor/ceiling losses. BHP prime packing and the
other retained interfaces still have their own eventual thresholds.

| h50 roles | Family | Independently checked kappa |
|---:|---|---|
| 509,194 | Conservative | `3955009008227/(5*10^29)` |
| 487,650 | Optimized | `1193902884521/(125*10^27)` |
| 486,200 | Optimized | `9606057843781/10^30` |

All eight rows strictly support `2^-57`, including the unchanged graph.
The envelope optimized row requires `log2 b>=6161257267345`, plus the
other eventual thresholds. These very large cutoffs do not imply useful
practical performance.

Within this guard family the scoped upper objective is
`b_complex*x_star/(1+4x_star)`. The packed term
`a_bit^2(1-x)/[(1-a_bit*x)(1+4x)]` decreases with `x`; the leaf term
`b_complex*x/(1+4x)` increases. Their intersection is the same balance
root. Increasing either primitive saving improves the pointwise minimum,
so using upper primitive enclosures supplies a valid family ceiling.
This ceiling does not rule out other guards, recurrences or finite motifs.

## Independent finite evidence and reproduction

The checker [review_phase_inverse.py](../code/review_phase_inverse.py)
compares rounded producer operations against independent dense rational
inverses and an independently assembled Schur complement. It checks:

- 1,300 GS entries and 1,300 shift-displacement identities, sizes 1-12
  with positive and negative near-identity Toeplitz coefficients.
- 205,071 exact phase-generator records, 1,674 nearest-round ties,
  18,923 cell lengths and 325,952 original/filled boundary edges.
- A 20-coordinate rounded inverse with internal weight reciprocal
  `2^126`, 256 fractional work bits, all 20 basis vectors plus two
  additional inputs. Absolute error is below `2^-80`, despite the large
  internal scale; its compact outward bound is about `2.3e-40`.
- A complete three-cell 48-coordinate solve, 36 interiors and 12
  boundary vertices of halfwidth four, original gap `2^-12`.
  Every global basis vector and two signed probes pass against the
  independent exact dense inverse; absolute error is below `2^-64`.

These are deliberately distinct from the parent's five rational-interval
Gaussian tests. They calibrate the actual rounded GS/Schur operations and
precision amplification but are not a simulation of the asymptotic tape
machine. The mathematical arguments above supply that transfer.

The independent parameter checker is
[review_phase_assembly.py](../code/review_phase_assembly.py). Both use only
the standard library plus retained review/producer modules, with source
hashes, input identities, actual interpreter version and commands in the
run protocol. Reproduce from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/integer-multiplication-bounds/code/review_phase_inverse.py \
  --output "$OUT"
PYTHONDONTWRITEBYTECODE=1 python3 research/integer-multiplication-bounds/code/review_phase_assembly.py \
  --certificate "$PHASE_CUTOFF_CERTIFICATE" --output "$PARAMETER_OUT"
```

The source's finite failed equality check and the corrected weight-bound
wording remain documented by the producer. No original input was edited.
This review makes no broader priority or novelty claim for established
Gaussian similarity, Toeplitz inversion or Schur-complement methods.
