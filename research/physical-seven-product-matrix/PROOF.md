# Exact seven-product matrices on a fixed tape inventory

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Prepared for @CubeJerry with substantial OpenAI assistance and separate
source-aware AI review. Apache-2.0. **No new κ.**

The seven-product identity and rounded boundary analysis are inherited.
CrocSwap/integer-mult-bounds#4186, retained in
`research/rounded-boundary-blocks/PROOF.md`, already supplies the numerical
order and conservative intermediate bounds. CrocSwap/integer-mult-bounds#5059,
`research/physical-boundary-pages/boundary_pages.py`, already implements the
physical inverse-block page caller with a classical matrix kernel. Its proof
explicitly leaves a seven-product tape refinement open. The present contribution
implements that refinement: literal quadrant movement, finite continuations,
serialized parked matrices, all real word products, and exact returned records.
It does not claim the algebraic identity, numerical stability theorem, or a
complete Gaussian or multiplication algorithm anew.

## 1. Exact product ABI and theorem

Let `B=2^ell>=1`, `w>=1`, and

\[
 U=w+\ell+2,\qquad V=2w+4\ell+4,\qquad W_{out}=2w+\ell+2.
\]

`SevenProduct.run(first,second,block,width,wide)` borrows two distinct binary
streams and three encoded `Count` descriptors for `B,w,W_out`. Each stream
contains exactly `B^2` signed, little-endian, two's-complement `w`-bit integers
in row-major order. Both heads start at canonical origin. Count tapes may alias
one another, as in the inherited caller, but are disjoint from both operands
and from every owned tape, including inactive scalar-service descendants.
The implementation validates positive `w`, an exactly dyadic `B`, and exact
`wide=2w+ell+2`. The fast entry has an explicit dyadic domain; the older classical
entry's domain of all positive block sizes is not silently changed.

On well-formed input, the protected return consists of the exact integer
matrix product in the same row-major order, with `W_out` bits per entry.
No precision `P` appears in the kernel and no numerical truncation is performed.
The caller retains its original completed residual/product rounding points.
Borrowed contents and origins are preserved. All private roles except the
return are cleared and their markers erased; `consume()` clears and erases the
return before reuse. An explicit pending flag protects it even if its head
has moved to the final blank. Ordinary input failures restore borrowed heads
and erase all private roles. Concurrent private/source mutation or interruption
inside an individual tape action is not a recovery promise.

Let `M(U)` and `S_word(U)` be the full time and retained-space contracts of the
unchanged authenticated real-word service. Its hypotheses remain explicit.
Set

\[
 \omega=\log_2 7,\qquad
 L=1+\ell+\lceil\log_2(w+2)\rceil.
\]

A sufficient complete invocation bound, including input validation/promotion,
exact return narrowing, cleanup and return consumption, is

\[
 C(B,w)=O\!\left(B^\omega\,[M(U)+V L^3]\right),\qquad
 S_{fresh}(B,w)=O(B^2V+S_{word}(U)).                 \tag{1}
\]

The space bound includes the two borrowed operands, protected output, parked
ancestor data, reverse buffer, all current blocks and encoded metadata.
On owner reuse, each physical role's maximum previously visited extent remains
charged; it is not replaced by a fresh-size bound for the latest input.
The deliberately conservative polylogarithmic factor in (1) pays the encoded
counters and scalar additions rather than assuming unit-cost machine words.

## 2. Encoded program and ownership

There are four active operand quadrants for each input, four partial answer
quadrants, two current row-major operands, one row-major returned product,
one accumulator replacement stream, one parked stack, one reverse-pop stream,
and one protected output. These are 19 fixed tapes. A fixed 256-role temporary
pool supplies all `Count` and `Signed` temporaries. One fixed `FftWord` child
supplies every leaf product. The complete declared closure contains 1338 tape
roles in the pinned cohort; independent object-graph enumeration agrees.

The host fields `closed`, `pending`, the traversal mode and the stage tag take
values in finite sets. The immutable operand/update tables have seven entries
and constant-size tuples. Variable dimensions, widths, loop bounds, data and
addresses remain encoded. Diagnostic node/product/frame counters do not affect
any branch, operation or returned bit; deleting them leaves the tape program.

There is one current dimension `n`, stored as a `Count`. `compute` is a single
flat loop, not a recursive function. Helper calls have fixed nesting depth.
All helper generators and their temporary scopes finish before the next child
is entered. No per-depth Python list, generator, context stack or live `Count`
object stores a parked ancestor. Global `U,V` and root descriptors are constant
in number. A parent's dimension is recovered as exactly twice its returned
child dimension, so only its finite continuation stage needs to be parked.

Within a physical invocation, construction is sealed and allocation sites
refer to the fixed pool. This includes arithmetic and encoded-loop temporaries;
no tape is allocated per scalar entry or recursion level. A separate manual
activation audit counts eight persistent kernel Counts, at most 16 other live
local roles before an innermost primitive, and at most eight additional roles
inside one such primitive. The source bounds for `Count.product`, `divide`,
`read_signed`, `write_signed` and signed difference are respectively 4, 4, 8,
6 and 3 local roles. Loop/counter constructors also have fixed smaller bounds.
Even a conservative reserve of 64 simultaneous local leases is below 256.
The scalar word cohort is separate: its allocations occur while this local
scope is suspended. These source activation bounds are independent of operand
length and recursion depth. The measured peak of 22 corroborates the finite
executions but is not used to infer the uniform bound.

### Quadrants and recombination

`split` makes one sequential row-major pass. In each top half-row it copies
one `n/2`-entry segment to A11 and one to A12, then similarly copies the bottom
half to A21/A22. The same applies to B. No indexed matrix fetch or transpose
is used. `join` performs the inverse four-stream row interleaving. The halves
are encoded Counts and every copied bit uses `copy_bits`/physical head steps.

The fixed schedule is the standard inherited identity:

\[
\begin{aligned}
 M_1&=(A_{11}+A_{22})(B_{11}+B_{22}),&
 M_2&=(A_{21}+A_{22})B_{11},\\
 M_3&=A_{11}(B_{12}-B_{22}),&
 M_4&=A_{22}(B_{21}-B_{11}),\\
 M_5&=(A_{11}+A_{12})B_{22},&
 M_6&=(A_{21}-A_{11})(B_{11}+B_{12}),\\
 M_7&=(A_{12}-A_{22})(B_{21}+B_{22}).
\end{aligned}
\]

The accumulator updates are

\[
 C_{11}=M_1+M_4-M_5+M_7,\quad C_{12}=M_3+M_5,\quad
 C_{21}=M_2+M_4,\quad C_{22}=M_1-M_2+M_3+M_6.
\]

`operand` computes the corresponding exact signed sums/differences and emits
one child operand. `add_return` applies each completed child immediately to
at most two C quadrants. It writes the complete updated quadrant into a
replacement stream before clearing/copying its destination. Thus ordinary
validation cannot leave an internal hole hiding later live entries.

## 3. Tip-only continuation and correctness invariant

At a nonleaf, split both operands, initialize four zero C quadrants, form the
first child operands, then append one frame. A frame consists of the eight
operand quadrants at width `U`, the four C quadrants at width `V`, and one
symbol from the fixed seven-symbol continuation alphabet. Every quadrant has
`(n/2)^2` entries. The stack head remains at its first blank after that frame.
After parking, all active parent quadrant streams are cleared and reused by
the child. The current dimension becomes `n/2`.

On return from a child of dimension `q`, `pop` reads the one stage symbol just
left of the stack tip. Its parent frame has exactly

\[
 q^2(8U+4V)
\]

body bits. It removes those bits right-to-left into one reverse buffer, then
walks that buffer backward while restoring the 12 parent streams forward.
Both removals delete a dense suffix, so no interior holes are created in either
stack. The stack ends at the first blank immediately after the previous frame.
Neither `push` nor `pop` calls `rewind()` on the parked tape or traverses any
older ancestor prefix. The only complete stack clear is final cleanup, or
cleanup after a failed invocation. The parent dimension is recovered as `2q`.

The restored stage says exactly which product has returned. Its signed updates
are applied to the restored C streams. If it was not stage seven, the next
child operands are formed and the updated parent frame is reparked. At stage
seven, `join` emits the completed parent product, all parent quadrant streams
are cleared, and the flat loop treats that product as a return to the next
older frame. A left marker immediately below the stack tip identifies the
root return. The implementation checks that its current dimension equals the
borrowed root dimension.

Induct on the number of completed subtrees. Immediately before descent, the
parked frame contains precisely the parent operands, completed partial sums,
and current child stage; the two active row-major streams contain precisely
that child's operands. On a child return, exact frame restoration recovers
that state. The stated Strassen updates yield the correct next partial sums.
At a leaf, the unchanged arithmetic child computes the exact signed product.
At a completed internal node, the inherited identity yields its exact product.
This proves the root result and exact row-major order for every dyadic size.
The argument depends on actual physical frame and stream invariants, not just
on a generic matrix identity.

## 4. Finite carriers, including the negative signed minimum

Let `A0=2^(w-1)` and similarly `B0`. These inclusive magnitude bounds cover
both signs, in particular the representable negative minimum. At depth `d`,
each operand entry is a signed sum of at most `2^d` original entries, because
every child operand adds or subtracts at most two parent entries. Its magnitude
is therefore at most `2^d A0` or `2^d B0`, and at most `B A0` or `B B0` over
all depths. These fit `U=w+ell+2` signed bits with room to spare.

Each leaf product has magnitude at most `B^2 A0 B0`. Each returned quadrant
combines at most four child products, including partial sums in the specified
order. Induction up at most `ell` levels bounds every product/accumulator
magnitude by

\[
 B^4 A_0 B_0=2^{2w+4\ell-2}.
\]

Consequently `V=2w+4ell+4` covers every exact intermediate signed record.
The unchanged word service is called at width `U`, not at the narrower root
input width. Its own exact product and sum scratch is included in `M(U)` and
`S_word(U)`. No temporary is rounded to fit a record.

The final root product also satisfies the stronger ordinary dot bound

\[
 |(AB)_{ij}|\le B A_0 B_0=2^{2w+\ell-2}.
\]

It therefore fits the inherited `W_out=2w+ell+2`. Reading a `V`-bit Signed value
and writing it at `W_out` preserves its integer value exactly; this is a checked
encoding change, not a numerical division or precision reduction. Every writer
checks signed headroom, including the case of negative minimum inputs.

Internal and final widths cannot be identified. At `B=8,w=4` with both inputs
entirely `-8`, the root entries are `512` and fit the 13-bit return. The first
three consecutive M1 operand sums produce `-64`, so the corresponding physical
leaf product is `4096`, which does not fit a positive 13-bit signed record.
The proper kernel succeeds. An executed wrong-width variant reaches exactly
that depth-three real scalar product and rejects with `signed data-word
headroom`; all input heads and owned roles are then restored/erased. This is
a demonstrated failure of that narrower internal carrier, not an obstruction
to the seven-product algorithm.

## 5. Complete work and retained-space accounting

For current matrix dimension `n`, a split or join scans `O(n^2(U+V))` bits.
Each operand combination, returned-product update and zero initialization
has the same allowance. A parent frame is parked/restored seven times, a fixed
constant, and contains `(n/2)^2(8U+4V)+1` symbols. Clearing the corresponding
active buffers and reverse stream also scans only that frame/current matrix.
No operation traverses a parked ancestor beyond the last frame.

All metadata values used for row sizes, bit extents and loop bounds have
`O(L)` bits. Encoded extent multiplication/division is performed by the pinned
bounded-integer helpers, not host arithmetic. Schoolbook manipulation of those
counts and a conservative `O(L)` allowance per counted bit visit fit
`O(n^2 V L^3)` per node. Signed addition/subtraction and record reads/writes
are linear scans with encoded controls, also within this allowance. This
bound deliberately permits polylogarithmic control overhead instead of claiming
a transition-optimal counter constant. The initial dyadic check, computed
widths and complete source promotion fit the root allowance as well.

With the *global* `U,V,L` retained at every recursion depth, the complete
recurrence is

\[
 T(1)\le C[M(U)+V L^3],\qquad
 T(n)\le 7T(n/2)+C n^2 V L^3.
\]

At level `j`, nonleaf matrix volume is `7^j(B/2^j)^2`; summing the geometric
series through `ell` gives `O(B^omega)`. There are exactly `7^ell=B^omega`
leaves, each executing one actual signed word product. Thus the recurrence
proves (1). The exact full-tree node count is `(7^(ell+1)-1)/6`; there is one
push and pop per nonroot node, namely `(7^(ell+1)-7)/6` of each. Diagnostic
counts agree with these identities in all executed fixtures.

Root input reading/promotion uses `O(B^2(U+w)L^3)`. Final result re-encoding,
borrowed origin restoration, erasure and consumption use `O(B^2 V L^3)` and
are already covered. An integrating caller additionally copies the `B^2`
returned words from the protected return to its declared destination and
consumes the return; that real `O(B^2 W_out L^3)` work also fits the same bill.
There is no free host matrix copy or scalar multiplication service.

At one instant, parked matrix sizes decrease geometrically:

\[
 \sum_{j=1}^{\ell}(B/2^j)^2(8U+4V)+\ell=O(B^2V).
\]

The active operands/quadrants/partial answers, one reverse-pop frame and
replacement stream add only a constant number of objects of that order.
The fixed temporary pool holds encoded scalars/counts and the word child has
its separately charged backing. This proves the fresh space bound in (1).

For a reused owner let `H_r` be the maximum visited extent of physical role
`r` over its complete history. Retained owner space is charged as `sum_r H_r`,
including inactive descendants, zeroed tails, old counter fields and prior
large matrices. Erasure changes live contents, not that retained backing.
Borrowed tapes' own historical extents remain part of their caller's storage
bill in addition to this owned-role sum.
The inherited `Tape.clear` rewinds and scans the *current dense live prefix*
to its first blank. Pop erases only a dense suffix, and the replacement method
avoids interior holes. Thus subsequent short calls do not rescan historical
blank tails. The executed grow/shrink control has identical current action
counts to a fresh small owner while retaining strictly more cells.

### Boundary consequence and limits

For a page caller with `K=ceil(n/B)` block rows and `J=ceil(R/B)` column batches,
the two passes make exactly `2(2K-1)J` matrix calls. Replacing only their exact
product implementation therefore gives

\[
 O\!\left(KJ B^\omega[M(w+\ell+2)+(2w+4\ell+4)L^3]\right),
\]

plus the inherited paid row/column layout, page manufacture and return handling.
The caller's real copies, row reversals and descriptor costs are separately
priced in BOUNDARY.md equation (1); they need not be lower-order for every
admitted metadata regime. Keep the ceilings for small or incomplete batches.
No original-reference perturbation, field gather or setup amortization is
supplied by a kernel substitution.

In the explicitly admitted fine-prime regime `B=O(p)`, `w=O(p)` and
`w=Omega(log B)`, the internal widths remain `O(p)` and `L=O(log(p+2))`.
Under the unchanged service invoice `M(U)=O(U log^2(U+2))`, this yields the
required power-zero polylogarithmic scalar-width overhead and replaces the
classical `B^3` leaf count by `B^log_2(7)`. The generic theorem retains `M(U)`;
it does not silently replace it by `M(w)` for arbitrary inputs. The word
service's all-size premises, the numerical factor/reference hypotheses and
the complete outer supplier remain inherited. A lower asymptotic exponent
for this component does not assert a finite-size speedup or a new κ.

## 6. Executed evidence and its boundary

`kernel_checks.run()` performs the actual instructions under the inherited
`no_decode` guard. Fixture generation, bit decoding, timing and the classical
integer dot-product expectations are external observers. No host arithmetic
oracle replaces a leaf or reads an online matrix element. The registered
package runner loads the authenticated physical cohort before invoking it.

The ordinary and optimized checks cover dimensions 1, 2, 4 and 8, including
negative minimum values, noncommuting and cancellation matrices, and a valid
case where two Count metadata ports share one tape. The 8-by-8 signed-minimum
case executes 343 scalar products, 400 traversal nodes and 399 pushes/pops.
All 1338 roles are erased at canonical origin after consumption. Borrowed
matrix and metadata bytes/origins are compared exactly. The largest local
lease peak in these fixtures is 22.

Nine ordinary guards cover duplicate operands, metadata/data aliasing, an
inactive child-role alias, a moved source origin, a too-small return carrier,
a nonbinary input, nondyadic size, a short matrix and a trailing matrix. A
second call with a moved but unconsumed output rejects without disturbing it.
Every executed failure is followed by complete cleanup checks and owner reuse.
An executed wrong M2 recombination sign changes the classical result; the
wrong internal-width variant fails only after its real depth-three product.
These are specific counterexamples to the changed code, not new algebraic
obstruction theorems.

After a larger call, the small `B=2,w=3` transaction has exactly the same
185955 reads, 52932 writes and 181670 moves as a fresh small owner. The reused
owner still retains 14614 cells, versus 2095 for the fresh owner. Those counts
cover run, literal return read, rejected pending call, consume and idle checks;
they are finite-alphabet actions, not bare-run or binary-machine transition
counts. A fixed alphabet coding changes only a constant factor.

A separate verifier supplies ordinary `i,j,k` exact integer dot products and
raw bit encoding/decoding without using the author's fixtures or Strassen
expression. Its same-owner calls include both an all-minimum and a mixed
8-by-8 matrix, with a short call between them. It independently discovers
reachable Tape objects, compares that closure with the declared inventory,
and checks every retained cell and head. The accompanying independent review
records the precise source hash and completed commands.

The fixtures use the retained scalar engine's base branch. They do not
independently prove or exhaustively test its all-size FFT branch. That service,
the existing exact-reference page producer, original factor bounds, numerical
rounding theorem and outer preparation/layout costs remain distinct pinned
obligations. The kernel result is the all-dyadic physical refinement proved
above, supported by these finite tests; the tests alone are not that proof.

## Open next questions

1. **Outer data layout and source assembly.** The page ABI starts from explicit
   batch-major coefficient fields. Connecting an earlier original row-major
   or packed-word caller still needs its paid gather and original-reference
   preparation/perturbation budget. No matrix identity removes that cost.
2. **Finite crossover.** Seven products asymptotically improve the matrix-size
   exponent but perform more framing and streaming than the classical kernel
   at small B. A future tuned hybrid could choose a crossover only after
   pricing its complete fixed-tape controls. No finite speedup is claimed here,
   and tuning a crossover is unnecessary for the present asymptotic refinement.

Credit the original Strassen identity; Jose Manuel's rounded-block analysis
in CrocSwap/integer-mult-bounds#4186; the authors and retained notices of the
literal boundary pages in CrocSwap/integer-mult-bounds#5059; the physical
Gaussian core in CrocSwap/integer-mult-bounds#3851; and the physical word,
ring and finite-role runtime lineage through CrocSwap/integer-mult-bounds#3787.
Their frozen sources and archives are unchanged. Publication of this scoped
component neither changes the selected frontier nor discharges all five
complete multiplication assumptions.
