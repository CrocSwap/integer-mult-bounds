# A complete periodic Gaussian source-to-solver interface

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a written conditional proof, supported by exact finite tests.

## Contract and result

Let R be the unchanged narrow `Reference` of Jose Manuel's
`research/rational-unitary-fft/gaussian_reference.py`, pinned in SOURCES.json.
Its source size is n, excess is e with 0<e<n, target period is N=n+e,
and retained source halfwidth is w with 2w<n. All other Reference parameters
keep their original meaning. Let H be its complete N by N rational narrow
matrix, including the hole rows and columns. Suppose the original source
gives a positive narrow gap g<=1 and an error E>=0 such that

    H_ii=1, H_ij>=0, sum_(j!=i) H_ij <= 1-g,
    ||H-H0|| <= E

for the ideal analytic matrix H0. The norm on vectors is the maximum of
|Re z_i|+|Im z_i|. The first premises are also checked on all generated
nonzero positions. The analytic approximation premise is inherited from the
source. This package does not independently certify its interval backend.

Let d be the largest number 2^-k, k>=0, with d<=g. Thus g/2<d<=g, including
arbitrarily small g. Choose a target t>=1, epsilon=2^-t, rational radius Y>0
and boundary precision P>=t+3. Admit the source only if

    E<d,    analytic = Y E/[d(d-E)] <= epsilon/4.

Choose p>=P so that

    coefficient = Y (2w) 2^-p/d^2 <= epsilon/4.

These are explicit exact gates. They can fail for an insufficient source
precision or tail width. The statement is for every source and caller that
satisfies them, not an assertion that an unnamed production policy does so.

**Theorem.** For every admitted unchanged Reference, preparation succeeds and
the consumer returns y with ||y-H0^-1 u||<=epsilon for every signed complex
P-grid input u with norm at most Y. All N coordinates are returned. Hole
coordinates are copied exactly. The direct factorization uses at most
4nw^2 products and each complex solve at most 8nw products, plus full target
scans and grid conversion. Factor/solve numeric storage is O(n(w+1)+N).
Coefficient generation and physical movement are separate paid costs below.

## 1. Original-coordinate reduction

Put rho=N/n and k_i=i+nearest_up((rho-1)i)=nearest_up(rho i). Since rho>1,
the k_i are strictly increasing and lie in [0,N). For the source's reverse
map, |k_i/rho-i|<=1/(2rho)<1/2, so nearest_up(k_i/rho)=i. Thus there are n
selected coordinates and exactly e holes, without an ambiguous inverse.

The literal source returns the identity if either coordinate is a hole.
For selected row k_i and column k_j it computes

    lift = -nearest_up((j-i)/n),   h=j+lift*n-i.

It returns zero if |h|>w. Since 2w<n, the retained positions are exactly
j=(i+h) mod n for -w<=h<=w. Cross-cell and cross-period entries remain in
this list. Their values are obtained from the original entry producer; they
are not replaced by an ordinary Toeplitz row or translated weight formula.
The selected block B is a cyclic band of halfwidth w. Permuting the target
coordinates puts H into diag(B,I_e). No actual permutation of the source
matrix or replacement Reference is required: gather selected inputs, solve
B, then scatter the selected outputs and copy the holes.

Preparation requests n(2w+1)+e original entries, including every selected and
hole diagonal. It checks nonnegativity, unit diagonal and each selected row
sum. The support proof just given supplies the zero entries. Finite tests
also read every original matrix entry, independently of that sparse list.

## 2. Coefficient and analytic errors

Round each selected coefficient downward to the p-grid, leaving the unit
diagonal exact. Let Bhat be the stored selected matrix, and let Hhat include
its identity hole block. Downward rounding cannot reduce the diagonal gap:

    gap(Hhat)>=d,    ||Hhat||<=2-d,
    ||H-Hhat|| <= (2w) 2^-p = Delta.

The maximum-coordinate row argument gives ||H^-1||,||Hhat^-1||<=1/d. The
resolvent identity then gives

    ||Hhat^-1 u-H^-1 u|| <= Y Delta/d^2 = coefficient.

Since E<d, the same argument gives ||H0^-1||<=1/(d-E). A second resolvent
identity gives the separate analytic term Y E/[d(d-E)]. No computed output
is used as the exact RHS for these two comparisons.

## 3. Direct solve and final output grid

Apply the retained variable-gap theorem from
[PR #5284](https://github.com/CrocSwap/integer-mult-bounds/pull/5284) to Bhat,
with size n, width w, gap d, norm M=2-d, input precision p, radius Y and
solve tolerance epsilon/4. Its unchanged proof and implementation are in
`vendor/`. Set K=max(1,2M). Its exact integer allocator chooses q>=p such that

    2^-q <= d/(2nK),
    2^-q <= (epsilon/4)d^2/(2nKY+4d+12M^2).

The retained proof establishes positive pivots, a complete factor residual,
both rounded triangular solves, and a uniform signed word range. It gives
an internal selected result v with error `solve<=epsilon/4` against
Bhat^-1 u_selected. It does not depend on a constant lower bound for d.
Since q>=p>=P, the input lift to the internal grid is exact.

Round each selected real and imaginary component toward zero to the P-grid.
This adds at most `output=2*2^-P<=epsilon/4` in the stated norm. Copy each
hole input exactly. The returned vector therefore satisfies

    ||y-H0^-1 u|| <= analytic + coefficient + solve + output <= epsilon.

In particular the required precisions have logarithmic dependence on n,
1/d, Y and 1/epsilon. Source entry precision and the input/output precision
can be larger, and are not hidden by this statement. The factor theorem's
word bound also applies unchanged. The source interval/rational arithmetic
has a separate, potentially much larger bit range.

A raw residual of the finally rounded output divided by d can be a loose
error certificate. Its rounding contribution is amplified by the row norm
and 1/d. The verifier therefore also computes the original-H residual of
the internal q-grid solution, checks that the public output is its exact
P-grid truncation, and adds the final rounding and analytic allowances. It
retains the final-output residual as a separate diagnostic. This distinction
does not weaken the consumer target or assume that truncation is linear.

## 4. Complete local invoice and ownership

The source producer and its original precision policy are executed. Setup
includes the n(2w+1)+e entry requests, up to n retained weight records, up to
w kernel records, source interval/pi caches, the selected/holes map and the
quantized matrix. Cross-period exponential calls and rational weight
construction are included in source setup; the entry count is not a bit-time
bound for these calls. `RESULT.json` records actual cache counts and source
precision fields before verifier-only matrix reads.

Factor preparation retains the direct cyclic fill. The inherited bounds are
4nw^2 factor products and at most (4w+1)n factor records. Quantized source
rows and active factor workspace coexist during preparation. A complex solve
uses at most 8nw products and 4n component divisions. It also pays a complete
2N-component input/radius scan, a 2n-component gather, 2n final truncations
and scatter writes, a complete target staging copy and returned tuple, and
all buffer clears. Hole values remain exact on the original P-grid.

The input tuple and retained factors are borrowed and unchanged. The source
object and its caches remain caller-owned. `execute` requires the unchanged
Prepared object returned by `prepare`; arbitrary caller-built or modified
factor dictionaries are outside the theorem. The retained solver clears its
2n-component forward buffer. The adapter clears its 2n-component internal
answer and 2N-component staging list after a successful solve, including an
exception during final conversion. The gathered tuple holds references to
immutable input pairs and is released. These are logical array operations,
not physical allocator zeroization or a multitape ownership theorem.

The complete local cost is source formation plus factorization plus each
solve and the O(N+n) boundary scans. No source, gather, scatter, persistent
factor or cache cost is assigned zero. Physical ordered delivery, primitive
acceptance and the full outer multiplication invoice remain open.

## Evidence, scope and credit

The finite checker compares all original entries and all outputs across
several source sizes, excesses, widths and source precisions. It uses a
separate pivoted rational dense solver on small cases and original-source
residuals on larger cases. It checks periodic couplings, multiple holes,
signed complex inputs, exact hole returns, source and factor preservation,
precision gates and a gap below any fixed 16-bit threshold.

The theorem is an all-parameter conditional interface; finite tests do not
prove production parameter funding. There is no production-family or native
supplier admission, complete kappa improvement or selected-frontier change.
No independent human or proof-kernel review is claimed.

Jose Manuel supplies the immutable Reference and its analytic contract.
JoyboyBrian's [PR #5159](https://github.com/CrocSwap/integer-mult-bounds/pull/5159)
supplies the earlier complete periodic recurrence and source/error boundary;
[PR #5216](https://github.com/CrocSwap/integer-mult-bounds/pull/5216) supplies
its weighted-power improvement. Ali Romman's
[PR #5260](https://github.com/CrocSwap/integer-mult-bounds/pull/5260) supplies
the fixed385-row direct consumer, and
[PR #5284](https://github.com/CrocSwap/integer-mult-bounds/pull/5284) supplies
the unchanged all-size cyclic solver used here. Dugongue's
[PR #4554](https://github.com/CrocSwap/integer-mult-bounds/pull/4554) and
Ryanson Jonathan's audit supply the earlier band/Woodbury scope. Retained
notices credit Vlado Vojdanovski, Jeremy Kothe, Cinna Davis, Mason Hale and
the Gaussian/precision lineage. Gaussian elimination, diagonal dominance,
resolvent bounds and coordinate permutations are classical. The new result
is their complete binding at this Reference caller, not a new general solver.
