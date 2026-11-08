# Exact seven-product substitution in the inherited boundary caller

Prepared for @CubeJerry with substantial OpenAI Codex assistance. **No new κ.**
The page protocol, rounded block residual theorem and two-pass layout come
from CrocSwap/integer-mult-bounds#4186 and #5059. The new contribution here is
substitution of the physically implemented exact seven-product kernel at that
specific caller. The old source files are unchanged.

## 1. Restricted entry and exact function

`FastBoundaryPages.run(D_L,B_L,D_U,B_U,rhs,n,R,B,w,P)` has the inherited
five-stream, encoded-count ABI, restricted explicitly to `B=2^ell`, `ell>=0`.
The original `BoundaryPages` still accepts arbitrary positive B; this separate
entry rejects a nondyadic block by scanning the encoded count. It does not
silently narrow or replace the old entry point.

Let `K=ceil(n/B)`, `J=ceil(R/B)`, `N=KB`. Pages have B² row-major signed
w-bit records. For one explicitly named exact rational reference `L U`, the
unchanged `prepare_pages` emits the P-grid diagonal inverse and preceding-block
coupling pages of L and of the reversal of U on all N padded rows. Each exact
diagonal inverse is computed before its single P rounding. Padding extends
both factors by the identity. Complete adjacent-block support is checked.
The supplied RHS has J batches, each N rows by B columns; inactive rows and
columns must be zero and are physically checked.

The inherited lower pass evaluates

\[
 v_0=y_0,\qquad v_i=\operatorname{trunc}_P(y_i-B_i x_{i-1}),\quad
 x_i=\operatorname{trunc}_P(D_i v_i).
\]

Products and the RHS difference are completed exactly before their displayed
P-grid rounding. Whole-row reversal then exposes the upper pages in the same
lower-pass order; the second whole-row reversal restores the original order.
`pass_blocks` and `run` are inherited byte-for-byte. Only the exact product
method and the ownership preflight/return boundary are overridden.

A child invocation returns the exact integer product in B² records of width
`wide=2w+ell+2`, exactly the inherited temporary width. It accepts no P
parameter and performs no grid rounding. The adapter copies every wide result
bit into the old destination, checks the exact extent and consumes the child's
protected return. It then permits the unchanged old recurrence to truncate.
Induction on the ordered block passes proves byte-for-byte equality with the
old completed-product function for every admitted input and all dyadic B.
The inherited rounded numerical theorem therefore has exactly the same input,
output, rounding sites and reference. No new numerical allowance is needed
for substituting the exact kernel.

## 2. Ownership and physical execution

The subclass owns a separate SevenProduct owner, so its scalar-word workspaces
never borrow the inherited caller's active local pool. Before any metadata
read, all five data tapes must be distinct and disjoint from every role of
both owners, including all inactive descendant pools. Metadata may alias one
another, as in #5059, but may not alias data or any owned role. Canonical
origins are checked by paid local delimiter reads, without inspecting a host
head index. A pending flag rejects reuse even after the return head has moved
to its terminal blank.

Each matrix call runs under the parent's `scope.suspended()`. Its borrowed
operand and metadata tapes remain unchanged at origin. On return the parent
scope copies the exact output, then consumes and erases the child. A finally
block consumes any pending child and restores all three product heads. The
inherited outer finally restores data/count origins, empties its own pool and
erases its markers. The explicit outer `consume` clears the final return and
checks both children idle. The inherited scalar owner remains unused but is
still included in every ownership/space inventory.

No dimension, matrix entry, address or recursive schedule is decoded into
host arithmetic by the new online adapter. It introduces only fixed calls,
encoded products for copy lengths, literal moves and the finite pending flag.
The kernel's own serialized continuation proof supplies the variable-depth
part. Diagnostics and finite test observers do not drive online execution.

## 3. Complete caller invoice and ceilings

There are exactly `Q=2(2K-1)J` matrix calls and `Q*7^ell` actual scalar
children. This includes every coupling and diagonal call in both passes and
every padded RHS batch. Real and imaginary components are already counted
among R; they must not be multiplied in a second time.

Let `T_7(B,w)` and `S_7(B,w)` be the complete kernel time/backing bounds proved
in `PROOF.md`, including width growth, quadrant moves, stack traffic, scalar
work, exact return narrowing and cleanup. Set

\[
 F=KJB^2,\qquad h=\lceil\log_2(n+R+2)\rceil,\qquad
 L=1+\ell+\lceil\log_2(w+2)\rceil.
\]

A complete online caller bound, including consuming the final return, is

\[
 Q T_7(B,w)+O\bigl(F(w+h+\ell+1)L^3\bigr).                  (1)
\]

Here is a source-specific account of the second term. Padding validation
copies/adds the encoded batch start and compares row/column indices, at
`O(h+ell)` bits per entry; signed record reads cost `O(w)`. Within each pass,
inner dimensions and widths have only `O(L)` descriptor bits. All completed
residual additions/truncations, factor rereads, local block copies, exact
wide-result copies and clears therefore fit `O(B^2(w+ell+1)L^3)` per block.
Each adapter copy has exactly `B^2(2w+ell+2)` bits; its two encoded length
products fit this bill. No numerical value is rounded during that copy.

The two inherited reversals make a complete forward scan and then local
row-sized backsteps. They do not scan a full batch once per row. Their actual
Counter/indices ripple is amortized; literal batch movement is linear in its
bits. Per-batch start/row-length products cost `O((h+L)L)`. The one-time
ceiling divisions cost `O((h+L)^2)`. These fit (1), since `F>=nR>=n+R-1`,
`F>=B^2`, and the logarithm squares are bounded by a constant times the
corresponding nonzero record counts. Initialization, final head restoration,
output consumption and all scans are included.

When an actual source has `h=O(w)`, the additional caller term becomes
`O(KJ B^2(w+ell+1)L^3)`; it does not introduce a full `log(n+R)^2` factor
per payload bit. This sharper tariff is a static derivation from the pinned
Count/Counter, signed-record, page and reversal code, independently reviewed
separately from the finite action census.

Substituting the proved seven-product recurrence yields the subcubic matrix
term. If `n,R>=B`, its leading scalar count is
`O(n R B^(log2(7)-2))`, each at the actual internal width `U=w+ell+2`.
The complete time retains `M(U)` and the displayed movement/control terms. For n or R below B, retain K and J exactly: dropping either
ceiling can give a false bound. Existing two-column work in #5499 deliberately
uses only the two active columns and can be better for R=2. This package
supplies the many-column exact kernel; it does not claim every small batch
gets faster or establish an outer source of many simultaneous fields.

Current caller storage, including all borrowed factor/RHS banks and the full
protected output, is

\[
 O\bigl(KJ B^2w+B^2(w+\log(B+1))\bigr)+S_7(B,w).             (2)
\]

There are only a constant number of live full-batch buffers and local blocks.
The child uses a separate fixed inventory. Every prior per-role maximum,
including cleared parent batches and child parked frames, remains in the
retained-space bill. The current-call time uses only live body extents;
erased historical tails are not silently freed or repeatedly rescanned.

Exact reference construction, the unchanged rational `prepare_pages`, and
input field packing are setup, with their actual costs added to (1). They
are not manufactured by the online adapter or assigned zero cost. The page
producer scans complete support, computes every exact inverse using its
encoded rational Matrix/inverse service and serializes all coefficient
records. Its inherited polynomial setup/height bill remains in force. The
original reference's own construction and any amortization must be justified
by its caller. The finite evidence reports first-pass work, physical page
setup and packing separately from online transactions.

## 4. Actual source fixture, reference and scope

`caller_fixture.py` adapts the supplied-factor fixture of #5499
(`physical-two-column-boundary-kernel/source_fixture.py`) only by exposing
three explicitly specified signed complex input payloads. All three share
exactly the same factors and reference. The unchanged `Core.gather` and
`Core.first_cell`, through the unchanged #5483 `source_pair.py`, compute
all six actual RHS columns. Fixture setup physically copies their returned
bits into the inherited batch-major bank; it does not decode and re-emit
computed numerical values. The independent first-pass expectation checks
every component before the solver is invoked.

The eight selected-row fixture leaves five Schur boundary rows. Its exact
reference is `LU(round_P(S))`, as constructed by that inherited supplied
fixture, at P=16 and w=32. This is not automatically the inverse of original
S. The block pages are manufactured by the actual unchanged encoded
`prepare_pages`, including its rational inversion, and not by the host
Fraction oracle. The separate oracle independently inverts the exact factor
blocks, rounds once, applies classical dot products and the precise two-pass
rounding sequence. The completed physical baseline is also executed.

The main B=4, R=6 case has K=2, J=2, both partial rows and a partial final
RHS batch. Every output bit agrees between the fast implementation, the old
classical implementation and the independent rounded-block oracle. It executes
12 matrix calls and 588 actual scalar children, against 768 classical children.
A second invocation on the same owner has identical transaction actions,
returned bits and retained backing. A B=1 singleton case covers empty coupling
banks and a one-entry exact return. Guards cover nondyadic input, duplicate
or metadata-aliased sources, inactive descendants of both owners, nonzero
padding and a truncated coupling after a completed child has been consumed.
A constructor census independent of `forbidden()` identifies all 2658 owner
roles. All their retained cells are blank at canonical origins after consume;
all source, metadata and arbitrary dirty spectator bytes are preserved.

The measured B=4 checked transaction is **slower**, despite fewer scalar
children: 212,425,677 finite-alphabet read/write/unit-move actions versus
44,814,681 for the classical baseline. The fast cost includes its rejected
pending-output probe; both include an output-head scan and complete consume.
These finite counts establish implementation coverage and its present
constant cost, not a finite-size speedup or a measurement of the Python
interpreter. The universal subcubic invoice comes from the proved recurrence.

Three source payloads provide a finite many-column integration witness. They
do not prove a new outer many-field supplier or a zero-cost field gather.
#5483/#5499 already bind the actual two-component first pass, and #5506 already
returns that supplied-factor function through unchanged second-cell,
normalization and final-disk operations. Those results are not claimed anew.
#5500 separately studies the original old-H rounded-Schur/LU growth under its
own positivity, diagonal-dominance, norm and geometry hypotheses. Installing
this fast many-column caller into that full source/error chain requires a
compatible complete accounting argument; this package does not assume it.
No selected assumption or complete multiplication exponent is changed.
