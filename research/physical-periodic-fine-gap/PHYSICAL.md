# Complete physical caller and bill

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a source-aware mathematical argument and executable finite replay, not
proof-kernel or human acceptance. Exact dependency pins are in `SOURCES.json`.

## 1. Proposition and boundary

Fix a rational `Reference` accepted by `periodic_pages.prepare`, with source
size S, target size T, positive source halfwidth w and narrow row gap δ>0.
Let A be its actual selected narrow matrix, including period-cut entries. Let
N_ref be the target-sized narrow matrix, obtained by embedding A at the selected
coordinates and putting the identity on the remaining coordinates. The
preparer binds all coefficients to this fixed rational source; its exact
matrix/Schur/LU work and physical serialization are separately paid.

For a complex T-record input on the prepared common dyadic grid, satisfying
the promised component-l1 radius R, `PeriodicInverse.run` returns a T-record
complex vector approximating N_ref^-1 b with the error proved in `NUMERICAL.md`.
Its computation uses a fixed number of physical tape roles, restores every
borrowed tape body and entry origin, and erases owned scratch. The protected
return is consumed through `consume` before reuse. Count descriptors, masks,
coefficient banks and input are distinct external tapes at canonical origins.
No host payload array or decoded variable index is used during execution.

This closes the periodic execution seam for the stated prepared Reference
interface. It does not instantiate the outer Gaussian/tensor recovery caller,
remove all five selected multiplication assumptions, or change κ. The frozen
word multiplier's hypotheses remain inherited. **No new κ.**

## 2. Inherited mathematics and actual interfaces

The two-call Schur identity comes from CrocSwap/integer-mult-bounds#5571.
The ordinary-run inverse is the frozen physical RUN component, with both
recurrence orientations, recentered residuals and all F maps. The scalar
word engine and `gaussian_boundary.subtract_row`, `push_window`, and
`BandedSolve` are inherited from CrocSwap/integer-mult-bounds#3851 and #3787.
The fixed folded solver component supplies `fold`, `unfold` and `FoldedSolve`.
The fold permutation is 0,m−1,1,m−2,... . No new Schur identity, generic band
solver, convolution factorization or fold theorem is claimed.

The actual source is partitioned into ordinary nonwrapping phase runs. B is
the block diagonal matrix of the rational Reference principal run blocks.
J contains the first and last w positions of each run, with short runs
included completely and no duplicate positions. Writing V for restriction
to J, K=V(A−B)V^t and SB=(VB^-1V^t)^-1, the exact Schur matrix is SA=SB+K.
The preparer checks source support and gaps and prepares SB, K and the unchanged
folded solver for SA. Source-page computation and its error analysis are in
`periodic_pages.py` and `NUMERICAL.md`.

## 3. Physical source catalogue

`EncodedPeriodicPages` emits nine distinct canonical Count tapes for
(S,T,m,r,b,W,F,W_D,F_D), two one-bit masks, a framed header stream, six run
coefficient banks, two common-grid matrix banks, and two native D factor
banks. Here m=|J|, r is the number of ordinary runs and
b=min(m−1,4w−2). A run header consists of (n_i,L_i,W_i,F_i,R_i), where R_i is
the exact record count in either residual page. The first four values are the
unchanged native RUN header; R_i merely delimits local page extraction.
The child itself checks the full residual body against n_i,L_i.

Each global coefficient bank concatenates native run bodies in increasing
original source order. Widths may vary between runs. Every header digit and
payload bit is emitted through the physical Count/Signed ABI. Host integers
occur only in separately paid preparation. The online owner receives only
the fixed tuple of physical ports and counts, not the `Bundle`, exact matrices,
interval list or host coefficient tuples.

## 4. Two passes and unchanged native grids

The input extractor walks the T target positions once, reads both Signed
components, and copies selected values to two physical source tapes. It
counts exactly S selected positions. The original complex tape is borrowed
and unchanged. For each of the two real components:

1. Stream every run through RUN, gathering only J into `vy`: the rounded
   counterpart of VB^-1b.
2. Apply the common-grid folded SB bank and unfold the answer.
3. Downconvert to F_D, call public `FoldedSolve` for SA, consume its complete
   native return, and exactly upconvert to F.
4. Apply the common-grid folded K bank and unfold the correction.
5. Stream original b again. At each J mask bit subtract the next correction,
   dispatch the resulting run to RUN, and retain all S output records.

For each run, the dispatcher extracts six complete coefficient bodies into
six reused buffers. Global heads advance only forward across the catalogue.
One native RHS buffer is filled from the current source interval. Each
common-grid value is truncated toward zero by F−F_i, then written in W_i bits.
The child receives four separate canonical controls and seven distinct data
ports. Its entire result is consumed, left-shifted by F−F_i and written on
the common grid. Clearing a local buffer preserves its lease for the next
run. No child role is recreated. Singleton runs use the unchanged singleton
path, including its page checks.

The first pass reads J mask bits while consuming the child return. The second
reads them while forming its child RHS; the correction stream is consumed
once. Encoded totals validate sum n_i=S, exactly m boundary positions, and all
global bank/header endpoints. Global pages and masks are rewound once per
complete pass, never once per run. One complex RHS therefore makes **four
real RUN invocations per run**, not two.

Finally the target mask merges the two solved S-record streams with the
original complex values at identity holes. Both outputs, masks and original
input are checked to have their expected extent. Hole values are returned
exactly, with no solve or rounding at those positions.

## 5. Actual complete-dot SB/K application

`band_apply` physically folds its m-record vector using the inherited
reverse/copy routine. The initial local window contains b leading zeros and
the first b+1 records, with out-of-range zeros. At row i the window is exactly
the vector coordinates i−b,...,i+b. The prepared row has 2b+1 records in this
offset order.

`subtract_row` starts from zero on the 2F grid and subtracts every signed
coefficient product exactly. Negating gives the completed dot product. The
only numerical rounding is its final truncation by F. The accumulator uses
at most 2W+ceil(log2(2b+1))+O(1) bits, hence O(P) below. No product is separately
rounded.

`push_window` removes one record, copies the remaining 2b records and appends
the next source record or zero. The folded source advances at most once per
row and never returns to its whole-vector origin inside the loop. Induction
on i proves the invariant. Both windows are reused, including a harmless
final shift. The complete bank and folded vector are checked at the end,
and products are physically unfolded to original J order. Each apply uses
exactly m(2b+1) scalar products and O(mbP) local copy/clear work; folding and
unfolding add O(mP).

## 6. Roles, cleanup and preparation history

`PeriodicInverse` owns one RUN owner, one public FoldedSolve owner, a 512-role
outer pool and one protected output. Scalar products outside the children
reuse the folded child's word owner, with parent scope suspended. All calls
are sequential and each word/RUN/folded return is consumed before reuse.
Passive host call counters are diagnostics only and never select an action.
Only fixed-length tuples and finite booleans are host control; variable loops
use Count/Counter tapes. The inventory includes inactive word descendants,
not only roles activated in one fixture.

Every external Count tape is included in distinctness and deep owned-role
alias checks. Origin checks use paid neighboring-delimiter reads. On success,
all borrowed bodies/heads are restored, all parent leases and temporary Count
bodies close, and owned scratch markers are erased. Only the protected return
remains. A public `pending` flag prevents reentry before `consume`. The caller
owns that returned body until consumption; this does not promise recovery
from arbitrary modification of private child tapes.

The inherited dense-prefix `Tape.clear` stops at the first blank, without
rescanning old blank backing. A later narrow or singleton run incurs its
current live-body cleanup bill. Old allocated backing remains charged as
retained space. Source preparation also retains any rational-source cache
or previous prepared bank until explicitly disposed. A fresh setup bound
does not make arbitrary earlier preparation history free.

## 7. Complete time and space

Let P dominate W, W_D, all W_i and logarithmic index/header widths. Let M(v)
be the charged inherited exact v-bit product cost. Write
r_i=ceil(n_i/L_i) and N_ij<=2L_i for the actual residual window lengths.
Per real RUN invocation the unchanged bill is

    O(n_i M(W_i) + sum_j M(N_ij W_i) + n_i P).

Both residual orientations and their four-product convolution factorization
are absorbed only as fixed constants. This bill is multiplied by four for one
complex call. The two matrix applications per real component use exactly
4m(2b+1) scalar products in total. Two real folded solves add the unchanged
O(mb M(P)) bill. Full input extraction/merge, six-bank extraction, header
reading, grid conversions, folds, borrowed restoration, output consumption
and live-body clearing contribute O(TP+SP+mbP). Count/header arithmetic is
absorbed by these terms; no variable host arithmetic replaces it. A complete
envelope is therefore

    O(TP + S M(P) + sum_i sum_j M(N_ij P) + mb M(P)).

Run page volume is O(sum_i n_i W_i), since
R_i=3n_i+2L_i(r_i−1)<=5n_i. SB/K and LU pages have O(mbP) bits. Current parent
input/result tapes use O((T+S+m)P), local RUN pages O(max_i n_i W_i), and local
band windows O(bP). Packed convolution words can have O(L_i W_i) bits; their
child storage is included in the inherited RUN linear bound and is not
mistaken for an O(P)-bit scalar record. Retained space includes per-role
historical maxima and every still-live prepared page. Repeated calls do not
license discarding earlier maxima from the invoice.

Under the inherited physical word bound M(v)=O(v log²v), capped L_i and the
fine-gap specialization in `NUMERICAL.md`, the online envelope becomes
O(S p log²p + (K_source+1) w² p log²p), for T=O(S), P=O(p) and
log(L_i P)=O(log p). Exact source preparation is polynomial-time rational
work plus physical emission and is paid separately. This corollary retains
the word routine's hypotheses and source admission inequalities.

## 8. Verification boundary

Physical returns are compared with a separate exact integer rounded-schedule
replay and independently with the original rational Reference inverse.
Borrowed bytes/origins, erased fixed roles, exact product counts and a
heterogeneous-grid grow/shrink/singleton lifecycle are checked. Finite replay
is evidence for implementation and interfaces. The all-size statement rests
on the source/precision proof, the streaming invariants above, and inherited
exact word/solver contracts. Controls distinguish exact-bit disagreement from
a demonstrated violation of a numerical norm allowance.
