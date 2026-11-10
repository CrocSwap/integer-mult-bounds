# Independent folded-solve numerical and source review

Separate source-aware AI review for @CubeJerry, 2026-11-08. No independent
human or formal-kernel acceptance is claimed. No standalone contribution.
The reviewed implementation is pages.py;
the exact tested SHA256 is printed by check_allocation.py and recorded in RESULT.json. The physical child is the
unchanged pinned physical-gaussian-core/gaussian_boundary.py BandedSolve.

## Universal numerical allocation

Let A be a real rational matrix with positive row diagonal-dominance gap
d and maximum absolute row sum M. Symmetric folding preserves both.
The inherited no-pivot row-gap facts apply. A direct row-mass telescoping
also justifies the constants: eliminating column k lowers row i's active
absolute row sum by at least d*|l_ik|, because the pivot row's off-diagonal
mass is at most u_kk-d. The final active row still has mass at least d.
Thus ||L||_infty<=M/d=ell, ||U||_infty<=M and every pivot lies in [d,M].
Also ||L^-1||<=M/d from L^-1=U A^-1. These are inherited facts, not new
claims of this caller package.

Write b for padded band and h for the data grid. Toward-zero factor
rounding gives ||Lhat-L||<=b h and strict-upper error at most b h.
The child stores z_i=trunc_h(1/u_ii), not a rounded diagonal. Under
h<=1/(2M), z_i>=1/(2u_ii)>0. The exact effective upper matrix Ustar has
diagonal 1/z_i and the stored strict-upper entries. Its diagonal error is
at most 2M^2 h. Consequently

    uc=b+2M^2,
    ||Ustar-U||<=uc*h,
    ||Lhat||<=ell+b=lc,
    ||Lhat Ustar-A||<=ec*h,
    ec=b*M+(ell+b)*uc.

The h<=d/(2ec) admission yields ||(Lhat Ustar)^-1||<=2/d. Separately,
h<=d/(2bM) yields ||Lhat^-1||<=2M/d. These are two different perturbation
conditions; both are present in allocation(). The reciprocal/effective-U
interpretation agrees with the inherited #5319 convention.

The actual BandedSolve rounds once after the complete forward dot product,
and once after the complete backward residual times z_i. For two real
component streams the respective row errors are bounded by 2h and 2h.
Multiplying the latter error by 1/z_i<=2M gives a Ustar-equation residual
at most 4Mh. Therefore the final approximate solution satisfies

    (Lhat Ustar) xhat = rhs + r,
    ||r||<=rc*h,  rc=2+4M*lc.

For every admitted input with component-l1 radius at most R, without
assuming observed peaks, this implies

    ||xhat-A^-1 rhs|| <= [2ec*R/d^2+2rc/d]*h.

The source's error constant and hmax match this formula. This is the
universal argument; the finite tests below are additional evidence, not
a substitute for it. Arbitrary rational R>=1 is allowed, provided input
values lie exactly on the admitted data grid.

## Complete values and raw intermediates

The same equations give the actual completed-vector bounds

    ||yhat|| <= (2M/d)*(R+2h),
    ||xhat|| <= (2/d)*(R+rc*h).

Together with R, M/d, M and 1/d these cover all stored inputs, coefficients
and solved values. The allocated signed width has ample extra sign space.
One can define the completed-row rounded recurrence over unbounded integers,
derive these bounds, then induct on the identical finite-tape operations;
no observed finite peak is used to justify the carrier.

In a raw dot product each W-bit signed coefficient/data magnitude is below
2^(W-1). The shifted RHS and b exact products sum in magnitude to less than
(b+1)*2^(2W-2). The child's wide=2W+ceil(log2(b+1))+2 covers this residual.
The subsequent exact product by the pivot reciprocal uses the word child's
separately allocated larger temporary width, then shifts by 2p. Thus its
three-grid raw product must not be charged as a W-bit stored scalar.

The latest allocator also includes ceil(log2(n+1))+2 in W. For arbitrary
RHS count, the lead inspected the actual indices(count)/stream.Counter
implementation: its ripple counter is amortized O(count+log(count+1));
there is no repeated full encoded comparison to count. Retain the initial
descriptor copy and its O(log(count+1)) space rather than unnecessarily
making numerical page width depend on the batch count.

## Original Reference one-arc fixture

The recommended finite source is Reference(9,1,1,2,3,32), target period10,
selected target coordinates [0,1,2,3,4,6,7,8,9]. Use its exact rational
selected principal matrix, remove source index0, and retain sources1..8
in original cyclic order. The one-coordinate Schur complement is computed
independently as H_ij-H_i0*H_0j/H_00, not using pages.schur or its LU.

The resulting 8x8 matrix is genuinely source-bound, has the certified row-gap
property, and its exact folded half-bandwidth is4. target16,R=1 gives
precision25,width30. This exercises periodic entries, the omitted identity
hole in selected coordinates, a nontrivial elimination and a nonconstant
right-hand side. It tests the Schur solver; it does not establish complete
original-H inversion or the missing Schur RHS assembly/recovery caller.

## Independent executed evidence

allocation_review.py independently implements Gauss-Jordan inversion and rational
completed-row rounding, using no pages.lu, pages.exact_solve or
pages.rounded_oracle for expectations. It checks effective matrix
perturbation, both inverse bounds, completed forward/backward radii,
full residual and original-matrix error.

The finite domain is27 signed cyclic-band rational matrices: n=1..9,
scales1/128,1,16, deterministic seed720053, two complex RHS per matrix.
All passed. The largest observed error/bound ratio among these was below
0.001058. The actual Reference Schur fixture also passed; its maximum
error is approximately9.316e-8, below0.0088 of the certified allowance.
Exact fractions and the tested pages SHA256 are printed by check_allocation.py; RESULT.json retains the actual physical source case.
The stopping rule was completion of these fixed cases, not an open search.

An omitted-unfold return order fails the original Reference comparison.
A separate scalar2I check distinguishes the stored reciprocal1/2 from
the effective upper diagonal2. These controls address actual interface
and reciprocal-model risks. No physical execution is claimed by this
independent numerical script; the lead owns literal fold/solve/unfold
execution and lifecycle verification.

## Physical caller issue found and disposition

The first reviewed folded_consumer called BandedSolve while its own
OuterScope remained installed. ScratchPool.install specializes only globals
and defaults equal to Tape; a nested installation can therefore miss sites
already replaced by the parent factory. The required child boundary is
`with self.scope.suspended(): solver.run(...)`, retaining the caller's live
leases without its allocation-site specialization. The lead implemented
this correction and owns the subsequent physical replay.

No other numerical/source blocker was found in this review. Subsequent
source changes require their own targeted replay or hash confirmation.
