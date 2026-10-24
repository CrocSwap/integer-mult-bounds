# Exact mixed-precision cancellation on bounded affine boxes

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Claim type: scoped algebraic proof, with exact finite corroboration.**
For a rational affine increment on a bounded integer box, agreement of two
half-up rounding precisions has an exact test using two affine extrema.
The algorithm also constructs a failing integer input without enumerating the
box. This extends woklerx's bounded scalar criterion in
[#1853](https://github.com/CrocSwap/integer-mult-bounds/pull/1853) to coupled
multivariable boxes. It is a new repository interface result; the elementary
rounding-cell and integer arithmetic ingredients are not claimed as new.

## Statement

Use coarse-grid units. Fix any finite dimension d, rational c,a_1,...,a_d,
nonnegative integer widths B_i, and a positive precision gap s. Define

```text
R(t) = floor(t + 1/2)
F_s(t) = 2^(-s) floor(2^s t + 1/2)
h = 2^(-s-1)
center(t) = t - R(t), in [-1/2,1/2)
r = center(c)
delta_i = center(a_i), if B_i > 0; otherwise delta_i = 0
m = r + sum_i min(0, B_i delta_i)
M = r + sum_i max(0, B_i delta_i)
```

Then, exactly,

```text
R(c + sum_i a_i z_i) = F_s(c + sum_i a_i z_i)
for every integer 0 <= z_i <= B_i

if and only if

-h <= m  and  M < h.
```

The lower endpoint is inclusive and the upper endpoint is strict. Zero-width
coordinates impose no coefficient restriction. The zero-dimensional case
checks only the offset. Arbitrary lower bounds L_i are handled by replacing
c with c + sum_i a_i L_i and B_i with H_i-L_i.

For the matrix source domain x=x0+Bz and increment Ax, apply the scalar test
separately to the rows of c=2^w Ax0 and D=2^w AB, with s=v-w>0. Thus the theorem
decides Q_w(Ax)=Q_v(Ax) on the declared box for rational matrices and arbitrary
0<=w<v. Signed updates y+=Q_w(Ax), y-=Q_v(Ax) then restore arbitrary target dirt
when x is unchanged and the updates themselves use exact addition/subtraction.
Correlations encoded by B are retained; independently certifying separate
summands does not certify their sum.

## Proof

The predecessor rounding-cell characterization says equality holds exactly
on the disjoint half-open cells [n-h,n+h), n integer. It follows directly by
asking that fine rounding equal the coarse integer n. Since h<=1/4, each fine
cell lies inside the corresponding coarse rounding cell. Credit woklerx
[#1848](https://github.com/CrocSwap/integer-mult-bounds/pull/1848) and Adam Gall
[#1908](https://github.com/CrocSwap/integer-mult-bounds/pull/1908) for this
characterization and its dirty-source boundary.

Suppose every box point is safe. Write e(z)=center(c+sum a_i z_i), so every
e(z) belongs to [-h,h). Along any present edge z to z+e_i, the difference of
these two residues lies in (-2h,2h), which is contained in (-1/2,1/2).
It is congruent to a_i modulo one. There is exactly one representative of that
class in [-1/2,1/2), so the difference equals delta_i. Following box edges
from zero proves e(z)=r+sum delta_i z_i at every point. Its extrema over the
integer box are m and M, attained at the sign-selected corners. Therefore
-h<=m and M<h are necessary. This includes coefficients congruent to 1/2:
no present edge can have both endpoints safe in that case.

Conversely, if both extremal inequalities hold, every lifted value
r+sum delta_i z_i lies in [-h,h). It differs from the original affine value
by an integer, so every original value belongs to a safe cell. This proves
sufficiency. No counting, independence of projected summands or continuous
relaxation of the integer source box is assumed.

### Constructive failure

If r is outside [-h,h), zero is a witness. Otherwise choose a failed upper
or lower inequality. Starting from zero, increase only the coordinates with
positive delta_i for an upper failure, or negative delta_i for a lower
failure, in index order. Jump over each complete safe coordinate block. In
the first block crossing the boundary, one exact integer division gives the
first crossing index:

```text
upper: ceil((h-current)/delta_i)
lower: floor((current+h)/(-delta_i)) + 1
```

This is an actual failing point, even if the extremal corner wraps back into
a safe cell. To see why, its preceding lifted value lies in [-h,h), and each
step lies in [-1/2,1/2). The next lift lies in [-h-1/2,h+1/2), a subset of
[-3/4,3/4). It cannot reach another safe cell. The nearest positive safe cell
starts at 1-h>=3/4; the nearest negative safe cell ends, exclusively, at
-1+h<=-3/4. Once the next lift exits the central cell it is therefore unsafe.
The construction uses O(d) exact rational operations and at most d integer
divisions, independent of the box volume. This is an arithmetic-operation
bound, not a bit-complexity or runtime improvement claim.

## Examples and scope boundary

At gap one, h=1/4. Each coefficient 1/8 is safe separately on {0,1}, but the
sum of two such inputs fails at (1,1). Two coefficients -1/8 on the same box
are safe, attaining the included lower boundary. The affine example
c=-1/5, a=2/5, B=1 is safe although its coefficient alone is unsafe at zero.
For a=1/2, B=2, both endpoints are safe integers but the interior point 1
fails. Raw corners or summand tests are not the new criterion.

This is an exact rounded-linear domain contract. The caller must establish
its actual source domain, unchanged source and exact target updates.
Internally rounded nonlinear increments, nearest-even or stochastic ties,
saturation, aliasing, changing sources and arbitrary disconnected parameter
sets are outside the theorem. No physical precision policy, compiler cost,
supplier admission, complete multiplication theorem, new kappa or selected
frontier change is claimed. The all-dimensional theorem is a written proof;
the executable reference accepts at most 32 coordinates, 2,048-bit rational
components/widths and gaps 1..256.

## Reproduction and evidence

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/affine-box-inverse-precision/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/affine-box-inverse-precision/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/affine-box-inverse-precision
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/affine-box-inverse-precision --check-source-history
```

Any CPython 3.12 executable can replace the local interpreter path. The direct
check prints PASS_AFFINE_BOX_INVERSE_PRECISION in a generated JSON stdout
receipt bound to every package file's SHA256. No receipt is handwritten and
normal verification writes no package files. The registered hook additionally
checks exact Git provenance. Predecessor implementations are not imported or
replayed.

Literal quotient/remainder rounding independently checks all 67,500 fixed
2D cases and their 405,000 points, including every rational coefficient
with denominator at most six and magnitude at most one in the declared
alphabet. Another 267 cases cover 4D boxes and dimension zero, with 8,772
points. Every reported unsafe verdict has its returned witness checked against
the literal failure set. Nine semantic fixtures include signed ties,
zero-width coordinates, affine offsets, coefficient reduction, unsafe sums
and a failing interior between safe endpoints. Two 32-dimensional boxes with
width 2^200 check arithmetic jumps; twelve invalid-input cases check the
boundary. Another 135 exact updates test arbitrary dirty-target restoration.
These finite domains corroborate the proof; they do not exhaust its domain.

## Credit, provenance and overlap

Woklerx supplies the original unrestricted product-grid theorem, the
unrestricted affine-lattice theorem #1848 and bounded scalar floor sums #1853.
Adam Gall #1908 supplies actual rounded-source closure counterexamples and
the explicit half-open-cell repair. Gareth Davidson, Chafik Boukhalfa's #628
and Ali Romman's kernel lineage supply the signed-increment and dirty-leaf
context. Their claims are cited premises, not reverified deliverables.
The new contribution is the exact bounded multivariable unwrapping theorem
and its volume-independent constructive failing-input algorithm.

The historical source pins are in SOURCES.json, at canonical base
624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7. TASK.json declares
the change from the uniform-transfer-audit card to this bounded interface
side result. The current selected source-binding positive control passed.
The retained selected result is kappa=0.00302015; it is unchanged.

The final overlap snapshot covers 397 open PR bodies at 22:44 UTC and 3,897
Discussion records at 22:45 UTC on October 22. The sparse helper searched
133 notes against 6,319 tracked notes and explicitly reported the omissions.
Distinctive searches across all main README paths and merged PR searches
supplemented this; relevant predecessor notes were read from the checkout or Git.
Searches exclude unpublished work, arbitrary diffs and most sparse local
notes. They are not proof of novelty. The local question lock was acquired
before the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134029).

## Open next questions

Bind the criterion to one actual rounded-linear caller with a proved bounded
affine source parameterization, including correlations and all intermediate
rounding. Start by deriving x0, B and integer coordinate bounds at the precise
inverse pair. A valid actual reachability invariant and the complete paid
precision/movement/storage bill remain blockers. Do not infer these from
ideal source closure or from this algebraic decision alone.

## Implementation constraints

The package retains a constructive checker and independent literal rounding
checks. No shared implementation or frozen source is changed.

Power of Ten review: there is no recursion, dynamic evaluation, process launch
or mutable global state in the new computation. Analysis and witness loops
have at most 32 iterations. Verification loops have the explicit finite
bounds above; stored literal failures have at most 36 points per small box.
Input types, dimensions, bit lengths and gap limits are checked before work;
first-exit and actual-witness invariants use explicit exceptions under -O.
All functions fit within 60 lines. Warning-strict execution and syntax checks
are used for both new Python files.

Rule 3 deviation: Python Fraction and arbitrary-precision integer operations
allocate during analysis. The affected scope is this bounded reference and
its fixed finite verifier. Input limits bound live rational bit lengths by
O(32*2048), with O(32) live coefficient/witness entries and fixed small test
boxes. The runtime's internal allocations are not directly instrumented.
The compensating controls are boundary-limit rejections and both huge-box
fixtures. A fixed-allocation implementation would be needed before claiming
this constraint for a native runtime. Rule 10 limitation: AST parsing and
warning-strict normal/optimized replay are the diagnostics used. No separate
type or lint analysis was run. This is not a fixed-resource runtime claim.
