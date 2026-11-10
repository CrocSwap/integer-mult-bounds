# A source-bound physical folded boundary caller

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The folding theorem is inherited from CrocSwap/integer-mult-bounds#4879;
the unchanged `BandedSolve` and word engine are #3851 and #3787. The
effective reciprocal-pivot interpretation is inherited from #5319. Exact
row-gap elimination and factor growth are classical and are retained in
the pinned `old-h-rounded-schur-lu-growth/PROOF.md`. This package supplies
their coefficient-bound physical caller and complete local invoice.

## 1. Quantified result and its boundary

Let A be a real rational n by n matrix, n>=1, with positive diagonal,
absolute row-sum norm M and positive row gap

    d = min_i (A_ii - sum_(j!=i) |A_ij|) > 0.

Let P enumerate the simultaneous folded order 0,n-1,1,n-2,... . Supply
a positive padded band b such that PAP^-1 is b-banded. `pages.prepare`
checks this property and that the exact triangular factors retain it.
Choose input radius R>=1 and integer target t>=0. The plan defines grid
h=2^-p and signed record width W. Prepare its two factor tapes with
`factor_tapes.EncodedFactors`, preserving their association with this A.

For any r>=1 real p-grid right-hand sides of norm at most R, presented
RHS-major in original order, the physical `FoldedSolve.run` returns
exactly rn W-bit records, also RHS-major in original order. Each returned
vector differs from A^-1 applied to its input by at most the plan's
`error_bound <= 2^-t`. The same allowance applies to paired real/imaginary
passes with max_i(|Re x_i|+|Im x_i|)<=R. No factor r enters that per-column
error bound. All eight borrowed numerical/Count ports are preserved at
their origins. All owned storage except the protected return is erased;
`consume` erases that final return. All retained blank backing is charged.

The factor-page hypothesis is essential: arbitrary modified pages do not
inherit this result. No matrix, coefficient or payload is silently
replaced by an oracle inside the online call. The actual numerical child
is the pinned `gaussian_boundary.BandedSolve`, including its actual exact
word engine and completed-row rounding.

For a cyclic band with one proper arc eliminated, #4879 supplies the
folded upper bound min(n-1,2w); n=1 may use a padded band one. This upper
bound applies to arbitrary coefficients with the stated support and
invertible eliminated block. Its negative-host sharpness theorem is not
assumed for positive Gaussian coefficients. Multiple eliminated arcs
require their own valid band, not an automatic reuse of 2w.

This is a Schur-system service. Forming its online right-hand side,
recovering eliminated variables, handling the full selected/hole layout,
and the complete periodic Gaussian/integer caller remain outside this
claim. The five selected framework assumptions are not removed. **No new κ.**

## 2. Exact factor bounds with a variable gap

Write B=PAP^-1; its exact factors are the L,U used below. Permuting rows
and columns together preserves d and M. In a principal
elimination step, pivot c=C_kk>0 and multiplier l=C_ik/c give

    C'_ij = C_ij - C_ik C_kj/c.

The triangle inequality shows that the remaining row gap increases by
at least |l| times the pivot-row gap, while its absolute row mass falls
by at least that amount. Thus every active matrix has positive diagonal,
gap at least d and row norm at most M. All pivots lie in [d,M]. Ordinary
banded elimination retains the band: a fill outside it has at least one
zero factor in its elimination update.

For a fixed row, summing its mass losses gives

    d sum_(k<i)|L_ik| + ||U_i||_1 <= ||A_i||_1 <= M.

The final row contains a pivot at least d. Therefore, writing ell=M/d,

    ||L|| <= ell,    ||U|| <= M,    ||B^-1|| = ||A^-1|| <= 1/d,
    ||L^-1|| = ||U B^-1|| <= M/d.

These are inherited row-gap facts, not new discoveries. They hold for
arbitrary signed off-diagonal entries. In particular a principal Schur
complement of an admitted row-dominant source retains its gap and cannot
increase its row mass. An exact source correspondence is still needed;
a matrix with similar-looking coefficients is insufficient.

## 3. Stored reciprocals and explicit precision

The preparation computes exact rational LU of PAP^-1, then truncates
factor entries toward zero to the h-grid. It does not first truncate A.
Thus there is no hidden initial Schur-matrix rounding term. A caller using
the older round-Schur-then-LU producer must add that separate perturbation.

Let Lhat have exact unit diagonal and the stored strict lower entries.
Store z_i=trunc_h(1/U_ii). The online upper diagonal is effectively 1/z_i,
not z_i and not a truncation of U_ii. Define Ustar by that effective
diagonal and the stored strict upper entries. If h<=1/(2M), then
z_i>=1/(2U_ii)>0 and

    |1/z_i-U_ii| <= 2M^2 h.

Set

    uc=b+2M^2,       lc=ell+b,
    ec=b*M+lc*uc,    rc=2+4M*lc.

The band gives ||Lhat-L||<=bh and ||Ustar-U||<=uc*h. Also
||Lhat||<=lc. Hence

    ||Lhat Ustar - PAP^-1|| <= ec*h.

The plan enforces both h<=d/(2ec) and h<=d/(2bM). Neumann perturbation
of B and L respectively then gives

    ||(Lhat Ustar)^-1|| <= 2/d,    ||Lhat^-1|| <= 2M/d.

The two conditions serve different purposes and are both retained.

## 4. Error on actual computed inputs and complete carriers

The child rounds once after each complete forward dot product. For two
real component streams, let its row error be e_f, ||e_f||<=2h. Its actual
forward vector satisfies Lhat*yhat=Px+e_f. In the backward pass the child
first completes the residual, multiplies by z_i exactly, and then rounds
once. The two-component output rounding is at most 2h. Multiplying by
1/z_i<=2M gives an effective-U equation residual e_b with ||e_b||<=4Mh.
Consequently its actual return obeys

    Lhat Ustar*xhat = Px + e_f + Lhat*e_b,
    ||e_f+Lhat*e_b|| <= rc*h.

There is no assumption that a rounded map is linear or that its input is
an exact ideal intermediate. The resolvent and residual equations give

    ||xhat - (PAP^-1)^-1 Px||
      <= (2ec*R/d^2 + 2rc/d)*h.

The plan chooses h no larger than the reciprocal of this constant times
2^-t, in addition to the earlier admission conditions and h<=1. All
comparisons are exact rational comparisons. This proves the stated error.

The same equations yield actual completed-value bounds

    Yf = (2M/d)*(R+2h),       Xf = (2/d)*(R+rc*h).

The carrier uses C=max(1,R,ell,M,1/d,Yf,Xf) and

    W >= p+ceil(log2(C+1))+2,
    W >= ceil(log2(b+1))+2, ceil(log2(n+1))+2.

It therefore holds every stored coefficient, input and completed solution
value. One may first define the recurrence over unbounded integers, prove
these bounds, and then induct on the identical finite-width operations.
No measured peak is used to select W.

Raw intermediates are separately allocated. A row's shifted RHS and b
exact products have magnitude below (b+1)*2^(2W-2). The inherited child
uses `wide=2W+ceil(log2(b+1))+2` for its reciprocal-product operand, and
the word engine supplies the exact larger product before shifting by 2p.
Neither this raw residual nor the three-grid product is claimed to fit W.

## 5. Literal fold, return and ownership

`fold` first reverses one complete line by whole-record copies. It then
alternates the next record of the original and reversed tapes. This emits
pi(2j)=j, pi(2j+1)=n-1-j, without decoding an index or a payload word.
The two source prefixes have ceil(n/2) and floor(n/2) records, disjoint
original index sets which cover the line. `unfold` splits alternating
positions, reverses the second half and concatenates both. For n=1 the
second half is empty; the unchanged reversal accepts encoded length zero.
Both transformations preserve every payload bit, so they add zero error.

One input line is copied from the monotonically advancing RHS tape. One
output line is appended to the protected return. No output rewind occurs
between RHSs. The six transport buffers and the whole child return are
cleared after each line. The parent suspends its allocation-site factory
scope around `BandedSolve.run`, preserving its leases while the child uses
its own fixed roles. Reinstalling that parent scope after the call is paid
fixed control, not a new physical allocation.

All eight borrowed tape ports, including Count descriptors, must be
pairwise distinct and outside every owned descendant role. The inventory
includes inactive base, product, nested-word and twiddle pools. Origin
checks use a paid left move, LEFT read and right move; the host backend
head integer is never queried by the control program. Variable lengths
and numeric values stay in encoded Count/Signed tapes. The fixed role
tuples, finite flags and passive diagnostic counters are not payload RAM.

A finite pending flag protects a return independently of its current
head position. A new invocation rejects while pending, even when the
caller has advanced to the trailing blank. `consume` physically clears
the complete body, erases its marker and releases it. On failure the
parent clears partial output and live buffers, restores borrowed origins,
and clears any already returned child result. The child itself owns
cleanup when its invocation fails before returning. All tape constructors
are sealed during ordinary execution.

## 6. Complete online time and retained space

For r RHSs, line length n, band b and record width W, the unchanged child
executes exactly 2rnb scalar products of width W and rn reciprocal
products of width 2W+ceil(log2(b+1))+2. Both factor banks are reread on
every RHS. Its bounded row windows and factor traversal cost
O(rn(b+1)W). Fold/unfold, line copies, reversals, source/return rewinds,
all buffer erasures and eventual protected-return consumption cost
O(rnW). Reversal uses local backward record steps, not a full seek for
each output record.

With the actual word cost Mv(v), including preparation, numerical recovery
and cleanup, the generic online invoice is

    O(rn [ b*Mv(W) + Mv(2W+ceil(log2(b+1))+2) + (b+1)W ]
      + log(r+1)).

The plan's W>=log2(b+1)+2 makes the wider argument O(W). The inherited
#3787 bound Mv(v)=O(v log^2(v+2)) therefore yields

    O(rn(b+1) W log^2(W+2) + log(r+1)).

Encoded `indices` uses amortized ripple increment/countdown. Initial
descriptor copies cost their full lengths; there is no repeated full
comparison with r at each payload bit. Products such as nW and the
half-line extents have encoded operands. Their work is absorbed by the
displayed scans because W includes log(n+1) and log(b+1).

The parent requires O(nW) transport scratch and O(rnW) protected return;
the child requires O((n+b)W) and its word workspace O(W+log(b+1)). Add
borrowed factor banks O(n(b+1)W), RHS input O(rnW), and O(log(r+1))
descriptor cells for a complete-call storage bound. These are retained
cells, including erased backing. Over reuse charge each role's historical
maximum, not only its current live prefix. Literal `Tape.clear` scans to
the first current BLANK; it never rescans a longer historical blank tail.
Separate long-then-short tests and the inherited code establish this
cleanup behavior.

The measured receipt counts finite-alphabet read/write/move primitives,
including literal return consumption and erasure. A fixed-length binary
encoding changes these by a constant factor. They are not claimed to be
the complete Python VM instruction count or a fully emitted transition
table. The actual arithmetic engine is executed, rather than replaced by
a host multiplication callback. The finite fixtures exercise its fixed
base branch; correctness and asymptotics of its FFT branch are inherited.

## 7. Preparation, source formation and serialization

Preparation is input-independent ordinary integer arithmetic with an
explicit bit tariff. It is not advertised as an observed fixed-role
online tape trace. `pages.lu` performs O(n^3) rational operations; for a
q-row original source, `pages.schur` may repeat a factorization for each
retained column, so its conservative count is O(q^4), not a linear-band
setup claim. Full rational matrices and all intermediate source data are
charged.

For original entries of numerator/denominator height at most B, clearing
their q^2 denominators gives integer height O(q^2 B). Determinant bounds
give O(q^3(B+log(q+2))) heights for the relevant minors and ratios. An
unfinished sum of at most q rational products has height
O(q^4(B+log(q+2))). Enlarge a guard H by the requested grid/target,
radius height and band descriptor lengths. Schoolbook arithmetic with
conservative Euclidean normalization costs O(H^3) per rational operation.
If every requested matrix entry is located by a full sequential scan,
an explicit fixed-tape realization costs

    O(q^4 [q^2 H + H^3]) work,       O(q^2 H) retained space.

This intentionally conservative polynomial bound pays matrix access;
unit-cost random addressing is not assumed. The Python preparation is
one implementation of those exact rational operations, not a measured
binary-step benchmark.

`EncodedFactors` emits exactly n(2b+1) signed W-bit records and five
distinct canonical Count tapes. All bit writes and later erasures are
explicit. A conservative ordinary-integer serialization charge is
O(n(b+1)W^2 + log^2(r+1)), with physical factor storage O(n(b+1)W).
The host prepared lists remain charged while retained. Their coefficient
integers never become unit-cost online arithmetic operands.

If A is formed from the retained Reference, pay its production too. For
source size S, excess K, alpha, retained halfwidths w,w_t and entry bits e,
let B_ref dominate e, rational geometry heights, alpha^2/theta,
alpha^2(w+w_t+1)^2 and 64, where theta=K/S. This covers the actual global
weight and kernel precision, not just the final entry grid. The pinned
Machin/Taylor/range-reduction algorithms admit a conservative O(B_ref^8)
ordinary bit bound per requested exponential. Querying a full selected
matrix, including finite cache scans instead of free dictionary access,
can therefore be charged O(S^4 B_ref^8) time and
O(S^2 B_ref+B_ref^2) source/setup space. Add the Schur/factor and emission
bills above and physically erase the serialized setup work when released.
`clear_reference` only releases host caches; it is not a secure erasure
trace and is not substituted for that charge.

These setup terms can dominate a small batch. Their amortization, the
actual outer axis ranges and any replacement by a more efficient producer
are separate caller obligations. No complete multiplication bound follows
merely by dropping these polynomial source/setup terms.

## 8. Actual source evidence and remaining obligations

The registered fixture authenticates `Reference(9,1,1,2,3,32)`, whose
selected targets are [0,1,2,3,4,6,7,8,9] and whose identity hole is 5.
It forms the exact selected principal matrix, eliminates source index 0,
and retains sources 1 through 8. A separate verifier constructs the
one-coordinate Schur complement directly. The folded matrix has band 4;
target 16 and R=1 give p=25 and W=30. Four physical real RHSs represent
two complex inputs. Every returned bit agrees with both the integer page
replay and a separately authored rational completed-row implementation.

Exact Gauss-Jordan inversion of the original Schur matrix, with all 64
matrix-product residuals checked, gives maximum component-l1 error about
9.316e-8. Six nonzero original entries cross the source period cut.
Omitting those entries or omitting the final unfold violates the declared
error allowance. The independently written allocation and transport
checks provide additional bounded cases and rejection controls; their
scope and independence are recorded in REVIEW.md.

These finite observations corroborate the written universal result; they
are not a proof by enumeration. The unresolved interfaces are online
Schur-RHS assembly, eliminated-variable recovery, multiple-arc band
selection, the full selected/hole caller and complete outer accounting.
