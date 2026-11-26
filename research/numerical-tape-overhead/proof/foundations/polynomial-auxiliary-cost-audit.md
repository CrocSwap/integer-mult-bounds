# Constructive size audit for B-poly

Status: **proved in the stated arithmetic/indexing model; independent review pending**. This expands Section 3 of
[growing-arity-circuit-candidate.md](growing-arity-circuit-candidate.md); it does not establish physical tape
costs. All symbols refer to that note.

For a large fixed threshold satisfying `q^L<=m^3`, `R_m<=m` and
`D_route<=m`, bound every finite dimension before recursing:

| Object | Sufficient coarse bound |
|---|---:|
| Routing labels | `m^3` |
| Gram matrix entries | `m^6` |
| Nonempty rectangles, by counting total incidences | `2m^4` |
| Shift rows per label | `4m` |
| Address-column width | `4m` |
| Dimension of each coordinate map | `4m` |
| Base batch width | `4m^4` |
| Contracted batch width | `32m^(19/4)` |
| Predictor stages, both evaluations included | `2m` |
| Spectral table cases | `2^m` |
| Address-column tuple cases | `2^(4m)` |

The last two rows are setup tables, not per-entry loops. On a routed
pencil, one may enumerate every query, every incidence, every seed-row
input/output pair and every entry of each coordinate matrix. Their
product is `O(m^10)` per original spatial coordinate. Dividing by the
original row count only lowers that coarse bill. The predictor stage
count and finite contraction tree are polynomial too, so `m^20` is a
safe coarse arithmetic/index budget after enlarging the fixed threshold.
Retaining `K=50` allows slack for construction and bit lengths.

Binary Gaussian elimination on a Gram matrix of side `m^3` costs
`O(m^9)` field operations. Each coordinate subspace and paired basis has
dimension at most `m`; even separate elimination for every rectangle and
label remains polynomial. Repair table inversion has side at most `4m`.
Fraction-free elimination bounds its intermediate integers by minors of
polynomial-dimensional matrices whose entry bit lengths are polynomial.
The companion note gives `O(m^2 log m)` bits for table coefficients.
School multiplication and exact division therefore give polynomial bit
cost. Including the two exponential setup tables yields a bound of
`2^(C m)m^50` for some absolute effectively chosen `C`.

An index into a setup table has `O(m)` bits; a row index has `O(log m)`
bits; an array address has `O(k)` bits. They fit the source word model
when `m=O(k^gamma)`, `gamma<1`. No unbounded description is assigned
unit cost. A lookup is charged only in the same word-indexing model as
the source Fourier theorem.

The source-specific admission check is that every free-rectangle
endpoint and representative conversion is a finite coordinate/row map
of the dimensions counted above. No matrix-root construction or unknown
finite search remains in the rational replacement.

## Fully discrete parameter selection

No logarithm/root oracle is needed. Compute

    u = ceil(log_2 m),  v = ceil(log_2(u+2)),
    b = least positive integer with b^2 v >= u,
    L = 2b,  Q = 2+ceil(2u/L),  q=2^Q.

Then `q>=4m^(2/L)` and `q^L<=4m^2 2^(3L)`. The constant 4 changes no
rate. Also `L=Theta(sqrt(log m/log log m))`, so (R-rate) is unchanged.
All quantities are computed by integer comparisons, bit lengths and
integer square roots. For the arity choice, take the largest odd integer
at most the integer 1000th root of `k`; exact binary search suffices.

An intentionally enormous but explicit sufficient threshold is
`u>=65536`. Here `v<=u/256`, `L<=4sqrt(u/v)`, `Q<=3+sqrt(uv)` and
`log_2(1+Q)<=v`. The displayed pencil bound therefore has

    log_2 R_m <= 8+v+5sqrt(uv) < u-1 <= log_2 m.

The same estimates give `D_route<=m`, and
`log_2(q^L)<=2u+3L<=3(u-1)<=3log_2 m`. These establish the coarse
polynomial dimension regime with no unbounded verification search.
Smaller parameter values can use the exact finite formulas; the growing
family theorem may place them all in a fixed direct-transform base case.
No claim of practical thresholds is made.

## Source-operation enumeration in more detail

Construct free rectangles by enumerating all ordered label pairs, at
most `m^6`, and recording their first-differing-bit signatures. Equal
signatures define the source's product rectangles. A dense list of
rectangle membership costs at most `O(m^7)` bits. Each span of destination
vectors has dimension at most `m`, with at most `m^3` generators.
Computing its basis, complement and paired dual by elimination is
polynomial. Even doing these tasks separately for every rectangle and
label pair remains below a coarse `m^20` bit/field-operation bound.

At execution, a charged rectangle sums its input rows into a common
batch, makes the billed axis transforms, and distributes to its outputs.
A free rectangle first transforms each incident source row, then for
each query changes its common representative, sums sources, applies the
row matrix and accumulates destinations before their last transform.
All representative changes are binary linear maps on at most `4m`
column bits and signs. Even if one uses a dense source/destination-pair
enumeration instead of the source incidence optimization, the number of
such scalar/index operations is polynomial. The *axis calls* must still
use the source shared endpoint schedule to retain (R); only the ordinary
work may be overcounted in this way.

For column control, enumerate a tree of `f` digit columns. The number of
prefixes is less than twice the number of complete addresses because
the branching factor is at least two. Extending a prefix updates its
image address by a positional weight and accumulates the query parities.
The next tuple's binary linear maps and signs are precomputed in the
`2^(4m)` setup table, or calculated in `poly(m)` word operations. Neither
method scans all `f` columns independently for every output position.
The `poly(k,m)` positional-weight setup is absorbed in the local
exponential array volume, as in the source uniformity argument.

Thus the algebraic/indexing interface can use `K=50` and a sufficiently
large absolute generator constant `C`. The following source map audit
completes the coverage argument; no tape-time statement is attached.

## Exhaustive map types in the source kernel construction

This audit uses the actual subsections "The endpoint Fourier transforms"
and "The finite saving and recursion" of the pinned `kernel.tex`, plus
the normalization proof in `binary.tex`.

| Source operation | Finite representation and charged work |
|---|---|
| `S_(v,j),T_(v,j)` changes into common coordinates | Binary invertible matrices on at most `A_m<=4m` bits per column. Their entries and inverses are found by elimination. Each applies separately to the `f` columns. |
| Source/destination auxiliary bases | Bases of `d_v^perp`, their paired duals, the span `H` and a complement `C`. Dimensions are at most `D_route<=m`; the largest supplied generator list is a subset of `q^L<=m^3` labels. |
| Initial and final phases | Signs of bilinear forms in each column, accumulated by parity over columns. A column's contribution uses `O(m^2)` binary operations. |
| Charged common kernel | Exactly the billed `2D_route` one-axis calls per row, plus the preceding coordinate and phase maps. No extra full transform is hidden in ordinary work. |
| First free endpoint | The source's proof that `H` lies in `d_v^perp` places every transformed direction in the auxiliary axes. At most `2D_route` child calls, counted once per source incidence. |
| Changing coset representatives | Linear coordinate projections and changes of basis between `H` and its complement, plus the explicit sign from a shifted representative. These have the same polynomial-dimensional matrix/bilinear representation. |
| Middle operation for query j | Only those coordinate/sign maps and the `W`-by-`W` row matrix. It contains no child Fourier call, by the source endpoint factorization. Dense row arithmetic is allowed and counted. |
| Last free endpoint | The source's dual statement `H^perp` lies in `d_w^perp` puts it in auxiliary axes and permits summing over queries first. Its calls are counted once per destination incidence. |
| Rectangle weights | Rational constants from the explicit univariate `p(Delta)` and its binomial-basis expansion. No f-dependent search or coefficient is introduced. |
| Full spectral conversions in repair | Replaced by the explicitly finite contraction tree. Its leaves are direct A-axis transformations, included in the `A*4^(-h)` call bill. |
| Boundary equivalence between query product and target | Signs and a half-address exchange. Both are fixed binary column maps and phases of the above kind. |

There is no other operation in those source subsections. In particular,
the representative choices are made by linear complements and paired
bases, not by enumerating all spatial cosets afresh for each coefficient.
All descriptions in the second column have polynomial size in m.

For a conservative runtime count, enumerate every query, rectangle,
label, pair of seed-row coordinates and coordinate-matrix entry. This
has at most `O(m^12)` combinations. Source prefix enumeration executes
each corresponding index/sign map in `O(m^2)` operations per array
position without a factor f, as proved above. Charging the predictor
stage count and even all base-program occurrences in the contraction
tree leaves a bound below `O(m^30)`; choose `K=50` to absorb the finite
absolute constants and the bounded remainders. Actual source execution
uses much less ordinary work. Its *recursive* call bill remains (R)
because the first and last free endpoints keep their sharing order.

The source normalized binary implementation supplies exactly the
normalization factors from the child calls. It removes all signed
powers of two depending on f from the nonrecursive coefficient list.
Our replacement predictor, check matrices and division tables add only
the rational coefficients already bounded by `poly(m)` bits. Hence no
coefficient of unaccounted f-dependent bit length appears in B-poly.

This proves B-poly for exact rational linear circuits with the source's
word-addressing operations. Independent review should focus on the map
classification table and the normalization compatibility, not mistake
this for an assertion about physical data movement.

## Uniform array-space diagnostic

Process the rectangles of a pencil sequentially. Keep the original input
rows and the output accumulators. For a free rectangle, keep its first
transformed source rows while accumulating destination rows, then take
the shared final transforms and release its scratch. Each side is a
subset of the labels, so each collection has volume at most the original
batch. Charged rectangles need a common temporary batch. This uses a
fixed number of volume-sized arrays, independent of `m`, instead of
retaining every incidence simultaneously. It does not grant free
physical access to those arrays.

The contraction stack descends through `V/8`, while the spatial batch
stack descends through at most `V/W_m`. Separate nested depth-first
schedules have geometric parked volume. Setup tables of
`2^(C m)m^50` bits fit local volume beyond the fixed effective threshold.
This is a uniform row-array storage argument. Fixed-tape serialization
and movement remain separate obligations.

## Numerical-growth diagnostic

At most `m^50` local operations with coefficient magnitude at most
`2^(m^50)` imply logarithmic norm amplification at most `O(m^100)`.
Choose `gamma<=1/1000` for the growing arity. Along the spatial recursion,
logarithmic active widths decrease by a fixed factor. The sum of the
corresponding `O(m_i^100)` gains is `o(k)` in the root width `k`.
Completed normalized Walsh calls are unitary. Consequently this crude
estimate does not itself force more than `O(k)` precision per component.

The number of recursion nodes is polynomial in the root width: each
template has polynomially many calls in `m_i`, and
`sum_i log m_i=O(log k)`. A polynomial number of rounding events and
the bound on total amplification are compatible with an `O(k)`
fractional-bit precision after including the input norm and exact target
error. This is a diagnostic, not a complete scalar bit-cost proof.

The p-adic/division problem in the small-characteristic interchange
routine survives all these improvements. No physical multiplication
envelope is claimed here.
