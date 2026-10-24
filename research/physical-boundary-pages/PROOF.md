# A literal inverse-block page contract, with a charged classical kernel

This implements the page/return function in Jose Manuel's PR4186. It does
not implement the conjectured fast tape boundary solver of the retained
radical_reduction_ultra proposal. All matrix products below use a declared
classical sequential fallback. This distinction is part of the result.

## 1. Reference and page format

Supply exact rational factors L,U of one explicitly named reference matrix,
with positive no-pivot setup diagonals. L and J U J must be block lower
bidiagonal for the chosen block width B, where J reverses the **padded**
row range. A scalar half-bandwidth at most B suffices. The producer also
accepts any finite instance whose actual block support satisfies the same
condition; it checks the complete factor and rejects every omitted block.

Let n be the actual row count, R the actual RHS count, K=ceil(n/B),
J_b=ceil(R/B), and N=K B. Extend each exact factor by an identity block
on rows n,...,N-1. Reverse all N rows/columns of U before partitioning it.
The four physical streams are, in this order:

1. rounded inverse diagonal blocks D_L, in increasing lower block order;
2. rounded preceding-block couplings B_L, omitting the first zero block;
3. rounded inverse diagonal blocks D_U of J U J;
4. rounded preceding-block couplings B_U of J U J.

Every page has exactly B² signed fixed-width records, in row-major order.
D=round_P(A_exact^-1) and B_page=round_P(B_exact), using truncation toward
zero componentwise. The inverse is computed from the exact reference block,
then rounded. Inverting an already rounded block is a different contract.
`prepare_pages` uses the actual encoded `gaussian_matrix.Matrix`, its exact
rational Gauss-Jordan `inverse`, reduced `gaussian_rationals.Rational`,
encoded loops, and fixed-width signed writers. It invokes no host inverse.
Full matrix scans in this setup are real work; setup time is not included
in an online payload bound or silently amortized.

The existing physical Gaussian `Preparation` computes LU after rounding its
Schur matrix S. Such factors can define an exact reference round_P(S), but
they are not automatically the factors of the original S in a theorem about
that reference. A caller must identify its reference and pay any additional
perturbation separately. This contribution does not change that producer.

## 2. RHS and output ABI

The entry point borrows five distinct streams and encoded Count metadata
(n,R,B,w,P), whose tapes are disjoint from all five page streams. Metadata
counts may share a tape with one another. This check precedes metadata reads.
All input heads return to their canonical initial position.
The RHS stream is **batch-major**: for each group of B adjacent columns,
write N rows, each with B signed w-bit values. Entries outside n actual rows
or R actual columns must be zero; the runtime checks them. Real factors
apply separately to real and imaginary components, as in PR4186. Complex
RHS tests execute both components using the same reusable owner.

For every batch the lower pass executes the literal sequence

    v_0 = y_0,
    v_i = round_P(y_i - B_i x_(i-1)),  i>0,
    x_i = round_P(D_i v_i).

Each product and sum is exact on its integer carrier before the indicated
rounding. It then reverses N **whole rows**, preserving the B column order,
executes the same pass with the upper pages, and reverses whole rows back.
The result has the same padded batch-major order. The output is one owned
return; its caller consumes and clears it before reuse.

The actual old `BandedSolve` has scalar band rows and rounded pivot
reciprocals, with a different per-row rounding schedule. The two functions
are not interchangeable even when the exact factors are the same.

## 3. Literal physical refinement

Online payload values are encoded Signed/Count objects or sequential tape
records. `BoundaryPages` performs no host matrix lookup, host payload
integer conversion, dense array arithmetic, or inverse computation.
`no_decode` is enabled while the actual setup and online calls run.
The pinned `FftWord` and `Arithmetic.multiply` execute every signed scalar
product; a host multiplication oracle is not installed in their place.

For each product, transpose its second operand by B complete scans. Each
scan reads all B² records and emits one column. Copy one row of the first
operand into a bounded row tape, then consume the transposed operand in
order while rewinding that one row. This executes exactly B³ scalar products
and accumulates each output without an intermediate P-grid truncation.
All transposes, row copies, rewinds and clears are performed, not inferred
from the final arithmetic identity.

All products of P-grid inputs use the 2P-grid. A temporary record width

    2w + ceil(log2 B) + 2

is sufficient for B products and the shifted RHS difference, for every
positive B and P<w. Each w-bit signed magnitude is below 2^(w-1); a product
is below 2^(2w-2), and the sum/difference has at most B+1 such terms. The
extra two bits cover the sign and the B+1 boundary. Completed P-grid results
must fit w bits; the actual source writer rejects an overflow. The inherited
PR4186 magnitude hypothesis determines a sufficient w. This package does not
replace its numerical theorem or assert a new rounded-child error budget.

The block recurrence follows by induction. The first predecessor is absent;
later blocks read exactly the preceding returned block. Every inverse and
coupling page is consumed once per pass/batch, and a trailing or short page
fails closed. Reversal conjugates the padded upper factor to the required
lower block order. Thus the output is exactly the independent PR4186 rounded
block function under the supplied page and width contracts.

## 4. Ownership and failure behavior

The runtime has a fixed 256-role local pool, one owned output, and the
retained fixed scalar-product child owner. The largest named data objects
are a constant number of B×B blocks plus one padded RHS batch and its pass
returns. No tape is allocated per matrix row, RHS column or recursion level.
Encoded metadata and scratch leasing use the retained protected cohort.

Temporary clears that retain a lease use `borrowed_tape(...).clear()`;
final clears release that lease. Each successful pass restores borrowed
heads; the outer finally restores all external heads, releases every local
lease, checks the empty pool and erases owned role markers. Failed output is
cleared. Distinct external ports are enforced before starting. A caller's
separate nonzero dirty tape is neither read nor changed. Failure controls
are followed by a successful invocation on the same owner.

## 5. Complete paid invoice and precise remaining gate

For n,R,B as above, the complete two-pass invocation has exactly

    2(2K-1) J_b   matrix products,
    2(2K-1) J_b B³   actual signed scalar-product calls.

Each matrix product pays B³ signed-record visits in its explicit transpose,
plus O(B³) row/read work and O(B²) result records. If M(w) is the retained
physical scalar-product cost, a sufficient online bound is

    O(K J_b B³ [M(w)+w polylog(n+R+B+w)]).

The two reversals and full batch copies cost O(K J_b B² w). Factor banks
are reread for each batch. Initialization and erasure costs fit the same
displayed bound. Setup uses reduced exact rational matrix operations and
sequential scans; its polynomial matrix/bit complexity is separately paid.
For full batches the leading scalar-product count is O(n R B).

This is a **classical fallback**. Replacing B³ by B^log2(7) has not been
implemented or proved by this code. The retained abstract seven-product
identity does not implement its tape quadrants, parked recursion frames or
complete scan cost. There is also no caller-level row-major-to-batch-major
RHS field gather here. The runtime starts from its explicit batch-major
stream. Both are genuine remaining adoption gates, and neither is zero-cost.

| Obligation | Status |
|---|---|
| Exact-reference diagonal inverses, rounded D/B physical pages | Constructed with actual encoded rational setup |
| Both ordered passes, row reversals, incomplete row/column zero padding | Constructed on literal tapes |
| Borrowed page/RHS/dirty ownership and successful/failing cleanup | Checked on the protected runtime |
| Complete classical products, transposes, copies, scalar child calls | Executed and charged |
| PR4186 numerical constants and exact Strassen identity | Inherited; not re-proved |
| Fast fixed-tape seven-product kernel/quadrant stack | Unimplemented |
| Caller RHS field gather and installation into actual Core | Unimplemented |
| Global reference preparation/amortization and original-S perturbation | Separate caller obligation |
| Full Gaussian supplier/compiler/stock/outer acceptance or new kappa | Not established |

The family decision is NARROW: preserve this actual page/return function and
its cost. Do not use the fallback to claim the faster Gaussian boundary row.
A future fast kernel must refine the same product/rounding ABI and include
all movement/parking work before inheriting that asymptotic claim.

## 6. Discriminating actual-source fixture

Use n=4, B=2, P=6, with L_ii=1 and
L_ij=(-1)^(i+j)/32 for i>j; U_ii=3/2 and U_ij=(-1)^j/32 for i<j.
All unspecified entries are zero, and indices are zero based. Both factors
have only two blocks, so all finite couplings are represented, including
the nonzero scalar-distance-three edge. With RHS

    (-3/8, -5/16, -1/4, -3/16),

the actual source `BandedSolve` returns second entry -13/64, while the
new literal inverse-block protocol returns -3/16 = -12/64. The verifier runs
both physical programs against independent exact arithmetic. This one-grid
difference proves that a page-format relabeling would not preserve the new
function. It is not a claim that the old solver is numerically incorrect.

Additional fixtures run three arbitrary real and imaginary RHS columns,
incomplete batches and rows, nonzero parked dirt and owner reuse. Bad padding,
trailing pages, aliased ports (including all 25 metadata/page pairs) and a coupling across two earlier blocks reject.
No native cover, whole Gaussian transform, Lean, Docker, historical suite or
complete multiplier is executed.

Credit Jose Manuel/jmbarrancoml PR4186 and physical Gaussian core; Vlado
Vojdanovski's blocked proposal and prototype; Cinna Davis PR4100; the retained
Gaussian/Harvey–van der Hoeven and physical word/ring/runtime lineage. Source
files and archives are unchanged and exactly pinned. Prepared for JoyboyBrian
with substantial OpenAI Codex assistance. Apache-2.0. Automated checks do not
constitute independent human or formal-kernel acceptance.
