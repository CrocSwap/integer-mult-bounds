# Source-bound numerical contract for the full periodic inverse

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This file proves the source, range, precision, and preparation contract for
`periodic_pages.py`. The companion physical proof must establish that the
executed caller implements these operations and charges their movement.
The q-LDU/run factorization and two-call Schur identity are inherited from
CrocSwap/integer-mult-bounds#5571. The folded-band mechanism is inherited from
CrocSwap/integer-mult-bounds#4879. Neither is claimed as a new lemma.

## 1. Fixed target and ordinary runs

The source is the pinned `rational-unitary-fft` Reference, with source size S,
excess k, target size T=S+k, theta=k/S, alpha>=1, source halfwidth w>=1,
2w<S, and positive delta=`Reference.narrow_gap`. In particular delta<=1.
All parameters and actual rational entries remain those of this fixed
Reference. The producer never silently raises its entry precision or width.
The source files and frozen RUN/folded dependencies are pinned in the package
manifest. RUN is the source-bound implementation published at
https://github.com/CubeJerry/integer-mult-bounds/tree/41defd0faaad9656e5f0c3d15445cb94e61077ea/research/physical-fine-gap-run.
The unchanged folded caller/pages are published at
https://github.com/CubeJerry/integer-mult-bounds/tree/d8c9d2c366925682e03cb9e38bc1a9c7d8d16c1b/research/folded-cyclic-tape.

Let q_i=i+floor(theta*i+1/2). On selected target coordinates q_i the narrow
Reference is the exact rational matrix A. Its other coordinates are identity
holes, with zero coupling to selected coordinates. Thus the complete narrow
inverse is A^-1 on selected data and exact identity on holes. This statement
does not include normalization, broad Gaussian stages, or the outer caller.

Partition source indices 0,...,S-1 into maximal ordinary intervals on which
floor(theta*i+1/2) is constant. There are at most k+1. The intervals touching
the original period cut remain separate. Every interval satisfies 2(n-1)<S:
for k>=2 its phase cell has length S/k<=S/2; for k=1 the two end intervals
have length at most ceil(S/2). Consequently each interval meets the frozen
RUN's ordinary, same-phase, zero-nearest-lift contract. The F factors inside
RUN remain indexed relative to each original interval's own beginning.

Define B as the block diagonal of the ACTUAL principal A matrices on these
intervals. This is not the ideal unrounded Gaussian used internally by RUN.
Let J contain the first and last w positions of each interval, taking their
union. A run of length<=2w contributes all its positions. Let V select J in
increasing original source order. With E=A-B, every nonzero E entry has both
endpoints in J, including the original period wrap. Put

    K=VEV^t,  SB=(VB^-1V^t)^-1,  SA=SB+K.

SB is the exact Schur complement of B after eliminating the other positions;
SA is the corresponding exact Schur complement of A. Setup constructs SB
from rational B, not from ideal Gaussian factors or approximate RUN output.

## 2. Inherited stability and geometry used by the caller

The source has diagonal one, row gap at least delta, and row absolute mass
at most 2. Deleting off-block entries gives the same bounds for B. Exact
Schur elimination preserves row gap and does not increase row mass. In a
surviving row, pivot k changes its absolute mass by at most

    -|a_ik| + |a_ik| sum_(j!=k)|a_kj|/|a_kk| <= 0.

The companion gap calculation uses the positive excess of the diagonal over
the off-diagonal row sum. It follows that SB and SA have gap>=delta and
norm<=2. K has norm<=1 because it consists only of A's removed off-diagonal
entries. All relevant inverse infinity norms are <=1/delta. These arguments
need row strict diagonal dominance, not symmetry or positive definiteness.
The Reference is generally nonsymmetric.

The boundary size m satisfies 2<=m<=2w(k+1). A single run contributes a
contiguous block of at most 2w boundary coordinates, so its SB block has
linear bandwidth<=2w-1 in that boundary order. Compressing the source
circle to J cannot increase the cyclic distance of a retained E entry.
Thus K has circular bandwidth<=w and SA has circular bandwidth<=2w-1.
The inherited alternating-end fold gives ordinary bandwidth<=4w-2.
We use b=min(m-1,4w-2). All masks, the fold, and the declared exact bands
are checked in preparation, including short runs and original period wrap.

The exact two-call identity used is

    y=B^-1 b_in,
    z=SA^-1 SB V y,
    x=B^-1(b_in - V^t K z)=A^-1 b_in.

This is inherited algebra. The new composition obligation is to execute
these exact source interfaces with charged movement and controlled errors.

## 3. Complete error telescope at actual computed inputs

Let R>=1 be an integer bound for input complex component-l1 radius, and
epsilon=2^-t the requested final component-l1 error. Allocate
epsilon_r=epsilon/2 to each real component. Each real input has radius<=R.
The real programs use the same source pages; adding their error bounds gives
the requested complex guarantee. This extra split is conservative relative
to the children, whose numerical contracts already cover component-l1 error.

Let e1,e2,e3,e4,e6 denote the complete errors of the first B inverse, SB
application, SA inverse, K application, and second B inverse. Inverse-call
errors include native input-grid conversion. They are measured at the actual
input supplied to each stage. Exact masks, permutations, upconversions and
the common-grid subtraction add no numerical error. Direct substitution gives

    ||x_computed-A^-1 b_in||
       <= (2e1+e2)/delta^2 + (e3+e4)/delta + e6.                 (1)

For example the first error passes through B^-1 V^t K SA^-1 SB V, whose
norm is <=2/delta^2. The second error omits SB, and the last error has no
following amplification. This telescope never assumes a rounded child is
linear. The final B call is made on the corrected actual input, not on an
unrounded ideal vector.

Set e=epsilon_r*delta^2/16 and fund each stage by e. Equation (1) is then
at most 6epsilon_r/16. The following radii include prior errors e<=1/16:

    Y=(R+1)/delta                after the first B inverse;
    T_in=3(R+1)/delta            at the SA right-hand side;
    Z=4(R+1)/delta^2             after the SA inverse;
    C_in=6(R+1)/delta^2          at the second B inverse input.

Use X=ceil(C_in) for both B calls and every run, so the same pages can be
reused. Use X_D=ceil(T_in) for the folded solve. A child's proof applies to
its actual input because these inequalities close the induction. Native
internal ranges can be much larger than these completed-stage radii; their
original proved carriers are retained.

## 4. Native grids, matrix pages, and completed carriers

Choose

    u=ceil(log2(4/(e*delta)))
     =ceil(log2(64/(epsilon_r*delta^3))).

Prepare every RUN at (radius=X, accuracy=u), and the folded SA solver at
(radius=X_D, target=u). Keep the producers' original native fractional
precisions f_i and signed widths W_i. The RUN formula gives f_i>=u+1.
For folded solve, its native error constant is at least 4/gap(SA)>=2,
so its precision is also at least u+1. No producer is modified to pretend
its already rounded coefficients have more precision.

Choose common fractional precision F at least every native precision. Before
an inverse child, truncate each component toward zero from F to its native
grid. This decreases its magnitude. Its error after exact inversion is at
most 2*2^-f_i/delta; the factor two is conservative for one real component.
The child's native guarantee adds at most 2^-u. Thus a complete converted
inverse call has error

    2*2^-f_i/delta + 2^-u <= e/4+e/4 <= e/2.                 (2)

The output is exactly raised to common F. In particular negative values
must be truncated toward zero, not arithmetically right-shifted with floor
rounding. Both native input conversion and exact output width/grid changes
are physical operations in the caller. The original borrowed coefficient
streams retain their native grids and their native ownership contracts.

For SB and K, apply the same alternating-end permutation as the folded
solver to both rows and columns. A coefficient bank has m rows and exactly
2b+1 records per row, in offset order -b,...,+b, with zeros outside the
ordinary folded index range. All coefficient records are on common F.
An exact rational coefficient is truncated toward zero, giving absolute
error<=h=2^-F and preserving its sign/magnitude bound. The bank constructor
checks exact zero outside the declared band before emitting any bank.

A row with at most s=2b+1 terms is evaluated as one complete exact integer
dot product followed by one truncation to F. At actual input radius H its
error is at most (sH+2)h; again two rounding units conservatively cover one
real component. Because rounded coefficient magnitudes are inward, their
row norm cannot exceed the exact source row norm. Choose

    F >= ceil(log2((s*ceil(Z)+2)/e)),

as well as all native precisions. This funds both matrix applications.
Splitting one row into separately rounded pieces would require a different
rounding allowance; the executed caller must match the completed-row rule.
Folding and unfolding themselves are exact permutations with norm one.

The common transport width is at least

    F+ceil(log2(X+1))+2,
    ceil(log2(T+1))+2,
    ceil(log2(b+1))+2.

All completed common-grid intermediate components have magnitude<=X.
For the final output this follows from (1), giving
`|x| <= R/delta+epsilon_r <= (R+1)/delta <= X`, rather than from the much
looser independent estimate X/delta. Local native stages retain their own
proved carriers for their larger partial values. Raw matrix dot products
use separately sized exact product/accumulator words, as in the inherited
physical `subtract_row` arithmetic. They are not asserted to fit common W
before their single rescaling. No overflowing conversion is tolerated.

The implementation records sharper complete errors: the maximum native
RUN `total_error` plus input conversion, the folded producer's actual
allocated error plus conversion, and `(sY+2)h`, `(sZ+2)h` for the matrices.
Substitution into twice (1) gives `plan.complex_error`. Exact inequalities
check all stage allowances, the final requested tolerance and the final
common carrier. These checks are input-independent setup, not posterior
measurement of the online vectors.

## 5. The fixed-Reference gate is not optional

Let E_N be exactly `reference.errors["narrow"]`. Every RUN must pass

    X*E_N/[delta*(delta+E_N)] <= 2^(-u-1).                   (3)

The frozen RUN proof establishes this comparison directly on an ordinary
same-phase zero-lift interval. Its corresponding ideal gap is delta+E_N
because delta is exactly the retained Reference definition. An arbitrary
stronger gap certificate cannot be substituted into that identity. A
principal periodic ideal matrix comparison by itself would not suffice.

Equation (3) pays the discrepancy between the actual within-run block B
and the ideal Gaussian used by the physical run. It applies at the enlarged
second-call radius X, so no ideal-input assumption remains hidden. Source
entries used in SB, K, SA and their LU are the exact rational Reference
entries. Their preparation never replaces B by the ideal Gaussian.

A sufficient, deliberately conservative admission condition is

    E_N <= epsilon_r*delta^7/[2048(R+1)].                   (4)

Indeed X<=8(R+1)/delta^2 and
`2^(-u-1)>=epsilon_r*delta^3/256`. The exact existing gate (3), rather than
this simplification, decides. If it fails, this fixed source is rejected.
Increasing only entry precision does not remove a deficient omitted-tail
budget; increasing halfwidth or precision defines a different Reference.

For delta>=1/poly(p), (4) requires only O(log p) additional guard bits beyond
the requested O(p) accuracy and input logarithm. This is a conditional
parameter consequence, not a claim that an arbitrary previously prepared
outer source already satisfies the gate.

## 6. Exact source preparation and page ABI

`prepare(reference,R,t,run_coefficients=C,folded_pages=D)` receives no online
payload. C and D are authenticated frozen dependency modules. It enumerates
the ordinary runs, selected target positions and boundary union exactly.
Only the 2w+1 retained cyclic source offsets per row request Reference
entries; all more distant entries are exactly zero by the pinned source
definition. It then forms rational A,B,K, computes SB by exact Schur
elimination and SA=SB+K, and checks the source norms, gaps and support.
The folded producer prepares exact rational LU followed by its proved
factor/reciprocal quantization. This never substitutes rounded RUN outputs
for a source matrix or prepares a coefficient using an online vector.

The returned object contains these input-independent data:

* a T-bit target mask (one for a selected coordinate), an S-bit boundary
  mask, and an S-bit run-end mask;
* consecutive ordinary runs, each with its original source start, frozen
  native bundle and native header (n,L,W_i,f_i);
* six native coefficient streams per run, concatenated by the physical
  emitter in ordinary run order, with exact residual record lengths;
* two common-grid m(2b+1)-record folded matrix banks for SB and K;
* the unchanged folded solver's native factors and descriptors.

All Signed records use the inherited two's-complement bit ABI. A residual
length in a physical header is a copy bound, not permission to omit the
native child's exact n,L-dependent extent checks. The masks and native
headers allow monotone source/page dispatch; they do not authorize a
separate full-S pass to locate each run or each boundary entry.

Exact matrices in `bundle.exact`, hashes and receipts are preparation or
verification evidence, not online ports. They may be discarded after page
serialization. The physical proof separately states fixed tape roles,
restored borrowed heads, pending-output ownership and sequential reuse.

## 7. Explicit polynomial setup tariff

Preparation uses rational/interval integer algorithms, not a measured
finite-control trace. Its bill includes source access; there is no
constant-cost entry oracle. Let B0 dominate native interval budgets,
entry precision, retained source weight/kernel working precisions,
parameter heights, alpha^2(w+1)^2, alpha^2/theta, log(S+1), t, log(R+1),
log(delta^-1), and 16. Generic bounds retain B0 explicitly.

The pinned exponential service uses O(B0) Machin terms with rational
temporary heights O(B0^2), then O(B0) dyadic Taylor terms and O(B0)
range-reduction/squaring steps. Conservative schoolbook rational arithmetic
gives O(B0^8) bit work per decay. At most O(Sw) source entries/weights/kernels
and O(S) RUN coefficients are requested, giving O(S^2 B0^8) work before
rational linear algebra. Long global source weights can occur in this
offline setup; they never multiply online RUN data.

Exact matrices start with rational entry heights O(B0). Clearing row
denominators and using the determinant bound gives O(S^2(B0+log S))
heights for minors/quotients defining exact Schur and LU values. Partial
sums below use these original-source heights: SA is the exact Schur
complement of A, so its folded LU is continuation of original-A elimination
in the order interior first, then folded boundary. Its factors are therefore
quotients of original-A minors. We do not apply a generic entry-height bound
twice to an unrelated matrix of Schur coefficients. Likewise SB comes from
original B, whose nonzero entries are original A entries. Partial
sums of at most S such rationals have the conservative height
H=O(S^3(B0+log S)). The reused simple Schur routine performs at most
O(S^4) rational operations, including repeated solves for separate columns.
Schoolbook arithmetic and Euclidean reduction cost at most O(H^3) per
operation. Quantization is rational division at the same bound. Hence
O(S^2 B0^8+S^4 H^3) is a conservative arithmetic bit tariff.

This bill does not assume free array lookup. Each indexed access can be
simulated by a scan of the polynomial encoded setup store, whose size is
D=O(S^2 H+SP+B0^2), with P dominating emitted data/control widths.
Charging one such scan per elementary setup step gives a conservative
fixed-tape tariff

    O((S^2 B0^8+S^4 H^3)*D),

with retained/setup space O(D). Finite loops and schoolbook scalar routines
suffice for this sequential simulation. Receipt call counts are not
substituted for this bit bill. Serialized pages alone occupy
O(SP+mwP+(k+1)log(SP)+T) bits. The caller performs no analytic, exact-height,
or source-matrix validation anew for each right-hand side.

The O(D) setup space statement starts with a fresh interval namespace.
This includes caches built during the current preparation: at most O(S^2)
new precision/source queries retain O(B0)-bit interval results, already
covered by D; O(B0^2)-bit series temporaries are separately included. The
producer does not clear shared caches or discard another preparation's
state. If an existing namespace retains historical pi/root or other cache
data of encoded size C_hist, replace D by D+C_hist in both the space and
sequential-access time bills. Several retained source-axis preparations must
likewise sum their storage instead of counting only the most recent one.

For theta=Theta(p^-2), alpha^2=Theta(log p), logR+t=O(p),
delta>=1/poly(p), and logS=O(p^(1-eta)), B0=poly(p) and setup is 2^o(p).
An axis family must still pay its explicit number of independent setups.
This does not establish amortization by an unrelated outer interface.

## 8. Complete online favorable consequence and limitations

Let P be the maximum common/native scalar record width and encoded control
size. `maximum_scalar_width` records this scalar quantity. It does not
bound packed integer products: the native convolution's word arguments can
have O(L_i P) bits, and its internal retained storage follows that larger
argument size under its own proved invoice.
Both calls to every real RUN cost, up to a fixed constant,

    O(S M(P)+sum_runs ceil(n_i/L_i) M(L_i P)+SP),

with each short window capped by its run length. The two real components
multiply that cost by two. Boundary matrix applications and folded solve
cost O(mw M(P)+mwP). Sequential source scans, saved-input preservation,
masks, fold/unfold and native/common conversions add O(SP+mwP). Every
child boundary requires the actual physical ownership suspension and
restoration mandated by the frozen implementations.

In the production regime above, native RUN bounds give L_i=O(p/log p)
unless capped by n_i, and all fractional/control/carrier widths are O(p).
The inherited exact word cost M(v)=O(v log^2(v+2)) consequently yields

    O(S p log^2 p+(k+1)w^2 p log^2 p).

For w^2=O(p/log p), k=S theta and theta=Theta(p^-2), the boundary work is
smaller than the run term. This includes both inverse calls, SB/K products,
complex components, holes and claimed transport. The companion literal
caller must establish this movement tariff and ownership contract; an
algebraic operation count alone is insufficient.

The target is one full fixed narrow Reference inverse on the prescribed
radius and precision. Holes are preserved exactly. The following corollary
also binds it to the inherited analytic periodic narrow inverse. Neither
claim implements the broad transform, normalization, tensor/CRT/integer
assembly, or removes all project assumptions. There is no new kappa.

## 9. Same-program analytic periodic corollary

Let N be the ideal periodic narrow map in the pinned
`rational-unitary-fft/RAW-GAUSSIAN-PROOF.md`, including the full winding sum
on selected coordinates and identity on holes. This is a global periodic
comparison; it is distinct from the direct ordinary-run comparison in §5.
The inherited equations (11)–(13) give

    ||N-A_ref||_infty <= E_N,
    ||N^-1||_infty <= 1/(delta+E_N),
    ||A_ref^-1||_infty <= 1/delta.

Here A_ref includes the target-sized identity holes. Equation (12) bounds
the ideal omitted/neighbor mass including nonzero diagonal aliases, so the
ideal row-gap bound delta+E_N remains valid despite its diagonal aliases.
The classical resolvent identity therefore gives

    ||N^-1-A_ref^-1|| <= E_N/[delta*(delta+E_N)].

For a component-l1 input bound R the extra action error is R times this
quantity. The producer conservatively uses 2R times it, which also covers
separately bounded real and imaginary components. By (3) and R<=X, this
extra error is at most 2*2^(-u-1)=2^-u. Together with (1) it remains below
epsilon. `reference_to_ideal_error` and `ideal_complex_error` record and
check these exact rational bounds.

No coefficients, tape instructions, or online costs change. This is a
source-bound corollary of an inherited global comparison, not a new
Gaussian identity or a claim about broad/normalized transforms. Original
Reference numerical tests validate the rational target; the independent
analytic allowance is justified by the cited universal source proof.

## 10. Executed preparation checks

`preparation_checks.py` receives the separate original-matrix oracle. It
compares all source entries and obtains expected SB/SA by Gauss-Jordan
inversion of original inverse subblocks, not the producer's Schur/LU
algorithm. This is independent of that algebraic implementation; source
entry evaluation still uses the same pinned Reference and interval service.
The checks exercise Reference(17,1,2,2,3,96), target 24, and
Reference(7,2,2,1,3,96), target 16, both at radius one. The latter has
native run headers (2,2,145,89), (4,2,145,89), (1,1,91,62), including
different actual native grids and a short final run.

On both sources an exact original right-hand side of radius one produces
a corrected second-call radius greater than 1.00000348. Its enlarged
allocation is therefore necessary as a contract, not just a hypothetical
cost guard. Exact coefficient controls reject omission of original
period-cut K entries. A higher target on the same short-width source rejects
the fixed omitted-tail budget. These controls do not claim a general
impossibility theorem. Normal and optimized isolated Python checks passed;
physical execution and complete original-Reference output checks belong to
the companion verifier. Finite checks do not replace the universal bounds.
