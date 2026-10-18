# One control-work constant across selected BIT root contexts

We address the physical-charge handoff in PR2289/2295. PR2234 states a
nonchild bound `C V(n+w)` but leaves its control preparation in polynomial
notation. We give an explicit compiler discipline and polynomial envelope
for that preparation, including field access after a unit reset. We retain
the selected literal schedule and the completed payload primitives.

The result concerns their nonchild work. It does not prove the entire
selected machine, rerun its GL64 payload, or improve the selected exponent.
We claim no new recurrence or moment result. Gareth Davidson's PR2289/2295
formalize those separate implications; their physical premises remain
distinct from the Lean proof.

## 1. Quantified context

Fix q, an odd prime, and the selected dimension 64 and literal word. The
production construction chooses q>2^80; the argument here only needs q>=3.
For an original digit width e>=1 set

    c=17/10000, w=ceil(e^c), B=q^w.

Keep w fixed throughout that coarse recursion. Global generation depth h
counts every descent, including unit and orientation children. The selected
proper-width rule gives `h<=2 ceil(log2(max(2,e)))`; at e=1 there are no
descendants. The incoming atom width n is at most e. Each generated weight
reads only earlier frozen matrix fields and its fixed descriptor. It does
not read the current fresh matrix, unused stock or arbitrary spectators.

We implement each bounded-dimensional modular preparation using schoolbook
binary arithmetic. Constants may depend on q and the fixed selected word,
but not on e,w,n,h, matrix values, arbitrary spectator cardinalities, row
multiplicity or the parking-stack position. We count full payload volume V
at the current node, after any enclosing one-time padding.

**Claim.** For the pass compiler below, one scalar/atom pass costs O_q(V),
one fixed header route costs O_q(Vw), and the selected node's complete
nonchild work costs `C_q V(n+w)` with one constant C_q across these contexts.
We include coefficient preparation, local metadata, counters, rewinds,
scratch erasure and parked control state. This statement uses the retained
linear payload-pass and parking constructions at their stated boundaries.

## 2. A shared descriptor and a local evaluator

Store one chronological chain of Good, FallbackPair and unit-reset records.
Each record holds its parent index, atom extent, finite request/low-class
metadata and global frozen-field slot. A unit reset starts a new constant
weight expression but increments the global age. It does not delete a
physical coordinate or silently renumber later field references.

For a fixed prefix fibre, maintain its generated matrix fields as local
counters. A field has 4096 radix-q digits per high layer and a fixed low
matrix. Accessing a requested field scans this compact control band and
returns its head. The band excludes arbitrary spectator and unused-stock
counters. Build the full-ring projector and the unweighted normalizer or
128-by-128 fallback plan from this field. No parent weight appears in that
matrix preparation.

The weight grammar, with m=64 and f=floor(parent_size/m), is

    Root(i)=a;
    Good(i)=Parent(i)*delta_floor(i/f);
    Pair(i)=d_j * B_(pi(j),t) / B_(j,t),
    B_(r,t)=Parent(r*f+t) for r<m, and 1 otherwise;
    t=i or f-1-i according to the physical orientation.

All divisions use units modulo q^w. These are the exact value methods in
commdata2338's PR2188 descriptor, as retained by PR2234. A Good node makes
one parent request; a Pair makes at most two. A unit reset evaluates to 1
and makes no request to its discarded expression ancestry.

Evaluate with a stack of requests, returned values and multiplication or
quotient continuations. A continuation stores only O_q(w+log(e+1)) bits.
Read a field's complete fixed-size preparation table, retain the needed
coefficient, then release that temporary table. The compiler can recompute
it on the next request. It never recursively builds a full parent vector.
If an adapter requests a vector, emit its at most e values sequentially
using this evaluator and erase the temporary vector before a child call.
Alternatively, the selected head/cross/pair formulas request at most two
weights for a gate and can avoid the vector altogether.

Induction on the stack's pending expressions proves the same value as the
recursive grammar. At a reset, the physical prefix still contains earlier
fields; a later Good/Pair reads its new field at the retained global slot.
A different compiler could relabel unused fields coherently, but dropping
fields while keeping the old references does not implement this contract.

## 3. An explicit polynomial envelope

For w>=2, root coupling gives

    e^17<=w^10000, e<=w^589,
    h<=2 ceil(log2 e), 2^(h+1)<=8e^2.

Thus one weight evaluation visits at most 8e^2 grammar nodes. Both local
indices and the generated control chain fit
`O_q(h(w+log(e+1)))=O_q(w^2)` bits, since
`log2 e<=589 log2 w` and `log2 w<=w`. This includes sequential table
location and return of the local head, rather than a unit-cost random read.

Modular operands have O_q(w) bits. Long multiplication and reduction cost
O_q(w^2); Euclidean inversion has O_q(w) division steps of O_q(w^2) cost,
so O_q(w^3) suffices. The 64/128 matrix dimensions are fixed. Their complete
projectors, bases, elimination, coefficient and scalar preparation therefore
cost O_q(w^3), independent of rank, high values and pivot itinerary. The
stack/control scan fits within that allowance. Preparing at most e requested
values and their fixed-size plans costs

    E(w)<=A_q e^3 w^3<=A_q w^1800.

For an exact exponent check, raise to the seventeenth power:
`e^51 w^51<=w^30051<=w^30600=(w^1800)^17`.
The constant A_q also covers root parsing, a literal vector if requested,
local scratch erasure and the finite initial cases. We do not scan a vector
of length e inside each grammar node; such a different implementation needs
its own bound.

When w=1, root coupling forces e=1. There is no recursive ancestry or
growing descriptor. The high-header field has cardinality 1, and its route
takes the retained identity bypass. Fixed low-class operations still have
a q-dependent constant cost. Thus the same envelope covers this case.

## 4. Uniform absorption, including high-header fibres

For any positive integers w and A,

    w^A/A! <= binomial(w+A-1,A) <= 2^(w+A-1).

The first inequality compares the factors w,w+1,...,w+A-1 with w; the
second uses the sum of the row of Pascal's triangle. Since q>=2,

    w^1800 / q^(w-1) <= 2^1800 * 1800!.

Define `K_q=A_q*2^1800*1800!`. We obtain E(w)<=K_q q^(w-1) for all
w>=1, with no cutoff depending on the root context. The body target has
the larger range q^w. We do not substitute q^w for a header's q^(w-1)
range or infer this assertion from numerical sampling of w.

For a complete atom pass, at most V/q^w target fibres each require one
coefficient preparation. Splitting and merging each perform one such scan;
they may recompute rather than save an enormous coefficient table. Hence

    O_q(V) + O_q((V/q^w) E(w)) = O_q(V).

The actual retained controlled-ADD implementation prepares once per parent
prefix before its unused/source/middle loops, which is less frequent than
this conservative count. At header boundaries use V/q^(w-1) instead.
The fixed route uses O(w) elementary passes and therefore costs O_q(Vw).

## 5. Arbitrary spectators require separate counters

An unrelated prefix can have bit length L independent of w. Repeatedly
reading it at each target fibre would cost `Theta(V L/q^(w-1))`, which
the preceding bound does not cover. In particular, the finite Python
header model's `(prefix//middle)%radix` must not become a fresh division
of a long flattened address on each visit.

Compile the pass as nested counters for `before`, active source x, `middle`,
target blocks and suffix bits. The offset reads only x, permitted generated
fields and fixed low carries. Hold x while the middle loop runs. Advance
and reset arbitrary spectator counters in their own bands; do not include
them in an ancestry scan. For fixed header scaling, update the piece index
as a finite residue state, since its multiplier belongs to the fixed route
alphabet. Prepare its endpoints once per pass.

Copy target blocks by nested block/suffix counters. Do not multiply an
arbitrarily long suffix descriptor into a fresh flattened length at each
fibre. A suffix counter reset costs O(log(2S)) and precedes S copied bits;
`log2(2S)<=2S` absorbs it. Ripple carry/decrement visits amortize over a
complete counter traversal. Initialize arbitrary shape lengths once per
pass, charging their fixed polynomial in log(2V) to O(V). The source's
fixed collapsed-field convention supplies exactly these local counters.

This is a compiler choice within the retained stream interface. We do not
claim the Python indexed-address model already implements bit-cost arithmetic
or that arbitrary spectral/row counters have O(w) bits.

## 6. Node charge, reset boundary and parking

The selected good and fallback bodies use O(n) atom passes, with fixed
dimension, rank and low-class multiplicities. Fixed header routes contribute
O(Vw); selection, XOR, copy/erase and packet replacement contribute O(V).
The peeled remainder has fewer than 64 atoms and costs O(Vw). Summing these
charges gives one `C_q V(n+w)`.

Before a recursive call, discard numerical preparation and pass a shared
symbolic descriptor. Copy the needed local metadata once; keep the frozen
field coordinates in the complete I/O prefix. The child reconstructs their
values through its local counters. It reads no buried ancestor record.
The remaining descriptor/control volume has a polynomial bound in w and
can be charged to the same complete-fibre allowance. Add its O_q(V) copying,
parking, restoration and cleanup to the retained unequal-buffer wrapper.
No counter needs an additional tape per recursive depth: the stacks and
records occupy a fixed set of marked work tapes.

The constant may be enormous and depends on the selected program and q.
It is independent of ancestor values, root width, arbitrary spectator sizes,
row multiplicity and stack offset. This supplies the uniform-control and
local-state portion of the nonchild-charge premise. The complete selected
payload endpoint, physical pass implementation and recursion remain the
named PR2234 construction; we do not equate a control evaluator with its
entire realization or claim a new Lean instantiation.

## 7. Evidence and credit

The finite checks compare an iterative evaluator with an attributed recursive
reference for the retained weight grammar, exercise unit-reset descendants
with global field slots,
and test counter-based offsets against address formulas. They include
independence from fresh stock, stale/compacted-field rejection and stack/head
cleanup. Exact inequalities certify the polynomial exponent and factorial
absorption. Finite operation counts supplement the all-size argument above;
they do not bound Python runtime or enumerate the selected GL64 payload.

We credit commdata2338's shared descriptor grammar, Ross Richardson's
fallback algebra, the selected supplier lineage and the existing PR2234
stream constructions. Gareth Davidson's PR2289/2295 supply the separate
formal recurrence/moment results and the explicit physical-charge handoff.
Jose Manuel (`jmbarrancoml`) prepared this contribution with substantial
OpenAI Codex assistance. Independent review remains necessary.
