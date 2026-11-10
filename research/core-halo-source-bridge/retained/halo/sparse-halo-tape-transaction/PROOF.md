# A sequential tape transaction for first-face halo copies

## 1. Statement, input contract, and contribution boundary

This note supplies the physical enumeration/sort/return obligation left open
in [the first open question of #4870](../halo-copy-enumeration/README.md).
The first-face partition, its source-membership predicates, and its volume
formula are inherited results. The new object is the fixed-role sequential
program in `tapes.py`, with the complete dense and sparse movement bill below.
It uses no numerical inverse oracle. An independently supplied halo consumer
remains responsible for producing correct returned *values*.

Fix integers

\[
 g\ge1,\quad \ell\ge1,\quad k_i\ge1,\quad E\ge0,\quad P\ge1,
 \qquad L=2^\ell,\quad S_i=2^{k_i}L,
\]

and integers \(0\le b<A\), \(L>4A\). There are \(2^E\) independent
spectator blocks. In a block, a point has coordinates
\(x_i=q_iL+r_i\), with \(0\le q_i<2^{k_i}\), \(0\le r_i<L\).
Put

\[
 B=E+\sum_i(k_i+\ell),\qquad M=2^B,\qquad
 K=2B+3g+1.
\]

The dense input is the complete lexicographic coordinate stream, containing
one opaque \(P\)-bit value per point. Every record has the same width. The
coordinate schema is a spectator field followed by the \(q_i,r_i\) fields;
the field widths are represented by delimiters and zero bits, not by
unbounded integers in control. The constants \(L,A,b\) are supplied as
\(w=\ell+2\)-bit unsigned fields. Well-formedness, the dyadic domain, and
the displayed inequalities are caller premises. This is not a parser for
arbitrary corrupted schemas. The program does check dense cardinality and
the semantic completeness of the final return stream.

For a core \(c\), face \(f\in\{0,\ldots,g-1\}\), and side
\(s\in\{0,1\}\), let

\[
 I=[A,L-A),\quad B_0=[0,A),\quad B_1=[L-A,L),
\]

\[
 T(c,f,s)=cL+I^f\times B_s\times[0,L)^{g-f-1}.
\]

Its saved domain \(D(c,f,s)\) expands each interval by \(b\) on both
sides, with coordinates reduced modulo the corresponding \(S_i\).
Each local offset is measured from the *unreduced lower endpoint* of this
expanded interval. Since every expanded length is at most \(L+2b<2L\le
S_i\), a local offset determines one distinct periodic coordinate.

Let \(C\) be the total number of saved records, counting copies to distinct
rectangles separately, and \(Q\) the number of target coordinates. For
\(N=2^{E+\sum k_i}\), the inherited identities are

\[
 C=N\sum_{f=0}^{g-1}2(L-2A+2b)^f(A+2b)(L+2b)^{g-f-1},
 \quad Q=N\{L^g-(L-2A)^g\}\le C.
\]

**Transport theorem.** There is one program with 30 tape roles, independent
of all these parameters, that:

1. Saves exactly one original input for every pair consisting of a rectangle
   and a point of its expanded domain, with its full destination/local key.
2. Stable-sorts the saved copies into rectangle and local lexicographic order.
3. Permits the dense core stream to be changed only after saving is complete.
4. Given an arbitrary-order stream of \(P\)-bit halo values with canonical
   \(B\)-bit global keys, rejects unless there is exactly one returned record
   for each target and none for a kept interior. On acceptance it keeps the
   current core value at every interior and installs the returned value at
   every target.
5. Erases its work with all movement charged, without claiming that erased
   backing becomes unallocated.

The transport performs

\[
 O\bigl(M(P+B)+C K(P+K)\bigr)
 \tag{1}
\]

finite-alphabet read/write/unit-move actions and retains

\[
 O\bigl(MP+C(P+K)+B+P\bigr)
 \tag{2}
\]

cells. Any numerical core/halo consumer work, coefficient pages, or extra
consumer backing must be added to (1)–(2). This theorem does not establish
correctness of arbitrary returned numerical values.

The common \(b\), complete dyadic periods, and supplied canonical input
stream are explicit restrictions. Nonbinary periods from the more general
combinatorial theorem in #4870 are outside this implementation. A dense
permutation needed to obtain this input stream is an additional caller cost.

## 2. What the physical program counts

Each tape has a left sentinel, finite content, and a right terminator. A head
reads one symbol, writes one symbol, or moves by one cell. There are 14 symbols:
blank, two bits, the sentinels, delimiters, and the finite descriptor marks.
`Tape` alone implements the simulator's cell map and integer head position;
neither the program nor any arithmetic/scheduling helper reads those private
objects. Its `inspect` and `ledger` methods are external observers only.

Program locals are booleans, individual symbols, one of three comparison
states, a finite phase, or one of a fixed set of tape handles. No growing
Python integer, coordinate tuple, list of records, input-sized recursive
stack, or array index is an execution resource. The fixed 30-role loop in
erasure can be unrolled. Procedure call depth is bounded independently of the
input; loops test current symbols. Thus all host control has a fixed finite
control compilation. The reported action counts are the actual tape
reads/writes/unit moves, not the count of Python instructions or a published
transition table.

For a binary-tape version, encode the 14 symbols in four-bit blocks and keep
each simulated head aligned with a block's first cell. A read or write uses
at most four binary reads/writes plus six unit head moves; a logical move
uses four unit moves. Therefore ten times the displayed action count is a
conservative bound for the tape primitives in this block simulation, before
a further fixed finite-control compilation factor. Four times the retained
logical-cell count suffices for the encoded backing. We do not call the raw
logical-cell counts exact binary transition counts.

The simulator initializes each input role with its supplied contents and
includes those cells in retained backing. Loading or generating caller
inputs is not a hidden subroutine in (1); it is the stated input contract.
An external numerical result stream may be loaded for tests, but it is
explicitly a consumer input, not a computed Gaussian answer.

`clear` first returns to the left sentinel, walks through the *current*
content to its terminator while erasing, returns, and places the terminator
at cell one. It does not traverse historical high-water backing. Every visit
is metered, and the high-water ledger never decreases. Reusing a tape after
a long record therefore pays that long erasure once, rather than imposing
its historical length on every later short record. This distinction is
needed for both (1) and (2).

## 3. Dense source work and admitted face records

The physical coordinate tape contains

```text
spectator bits & @ core bits # local bits ; @ core bits # local bits ; ...
```

All numerical bits start at zero. Increment scans backward with one carry
bit and skips delimiters. It is exactly the increment of the concatenated
\(B\)-bit address, so it visits the admitted lexicographic stream once,
including all periodic cuts. There is no quotient, long division, product,
or lookup per source value. Every increment plus repositioning takes
\(O(B+g)=O(B)\) actions. Overflow after the last coordinate resets it to
zero, supplying the starting counter for return. An early/late source end
is rejected.

One payload is copied to a reusable tape. The coordinate pass creates a
descriptor with the core and zero-extended local fields, a flat canonical
source key, and the following finite flags for each axis:

| Flag | Predicate |
|---|---|
| expanded interior | \(A-b\le r<L-A+b\) |
| previous full core | \(r<b\) |
| next full core | \(r\ge L-b\) |
| same-core lower face | \(r<A+b\) |
| same-core upper face | \(r\ge L-A-b\) |

The program computes the constant thresholds once by equal-width ripple
arithmetic. At a source it uses a fixed number of comparisons on each
\(\ell+2\)-bit local field. A one-bit prefix conjunction says whether all
earlier axes lie in their expanded interiors. Only while that conjunction
holds does it admit a lower face (same-core lower or next full) or an upper
face (same-core upper or previous full).

The next/previous candidates use only binary increment/decrement of the
\(k_i\)-bit core field. Arithmetic wraps modulo \(2^{k_i}\), which is
exactly the needed periodic core wrap. Under the strict parameter bounds,
the two alternatives for a *given side* are mutually exclusive. At most two
sides are admitted at an axis; every admitted side has at least one suffix
choice and thus at least one emitted copy.

An admitted face is stored as its unary axis number, a terminator, and its
side. If a source has \(f_x\) admitted faces and \(c_x\) copies, storing
and later clearing these unary records costs \(O(g f_x)\). This is **not**
claimed to fit in the dense \(O(B)\) work. Since \(f_x\le c_x\) and
\(g\le B\), it is charged to \(O(Bc_x)\). A source in the middle of
every core may have \(c_x=0\); it still pays the one payload/coordinate scan,
and no per-face or sparse-key processing is attempted.

The remaining descriptor construction, constant comparisons, counter work,
and current-content scratch clearing cost \(O(P+B)\) per source. Erasing
the previous source's face list is assigned to those previous emitted
copies. Consequently the total gather cost is

\[
 O\bigl(M(P+B)+C(P+B)\bigr),
 \tag{3}
\]

including all preparatory work below. There is no \(g\) multiplier on the
payload scan, and no fresh \(B\)-bit multiplication/division or \(B^2\)
key operation on all \(M\) sources.

## 4. Suffix choices and exact emitted keys

For one admitted face the program scans the descriptor to reset prior marks
and choices, follows its unary axis field by sequential traversal, marks
the face, and marks the later axes that have a neighboring full-core choice.
Every axis after the face always has its current core. It has a second
choice exactly when \(r<b\) or \(r\ge L-b\); these conditions are disjoint.
The marked binary choice fields form a physical odometer.

The initial all-zero choice is emitted. Backward descriptor scans increment
the marked choice bits, and the process stops at their overflow. No branch
has zero leaves. Thus, for a face with \(h\) eligible suffix axes, the
program emits its \(2^h\) choices exactly once. Both an emission and an
odometer step cost \(O(B+P)\), including descriptor head restoration. A
zero-bit odometer emits its one required leaf and stops.

For each leaf, the physical ripple routines form the destination core and
the following offsets. Here \(r\) is the source's local coordinate and
“previous/next” describes its *destination* core relative to its source core.

| Axis role and destination | Offset from expanded lower endpoint |
|---|---|
| Earlier expanded interior, current core | \(r-A+b\) |
| Lower face, current core | \(r+b\) |
| Lower face, next core | \(r+b-L\) |
| Upper face, current core | \(r+A+b-L\) |
| Upper face, previous core | \(r+A+b\) |
| Later full interval, current core | \(r+b\) |
| Later full interval, previous core | \(r+b+L\) |
| Later full interval, next core | \(r+b-L\) |

Each admitted value is nonnegative and less than its expanded interval
length, hence less than \(2L\). Intermediate sums are less than \(4L\).
The \(w=\ell+2\)-bit ripple routines are therefore exact for these
formulas; their modular truncation does not discard a needed high bit.
The core increment/decrement is deliberately modular, as required.

The complete binary key is

```text
spectator || destination core fields || one-hot face || side
          || expanded-rectangle local offsets || canonical source address
```

The face has \(g\) one-hot bits, the side one bit, the local offsets
\(g(\ell+2)\) bits, and the redundant canonical source suffix \(B\) bits.
Its width is

\[
 E+\sum k_i+g+1+g(\ell+2)+B=2B+3g+1=K=O(B).
\]

All fields are emitted by sequential scans; the \(P\)-bit payload follows
the key and a delimiter. No variable-length integer key is held in control.
The source suffix records provenance and does not alter the rectangle/local
order, since an expanded offset already determines a unique source.

For correctness, membership in a rectangle factors by axes. The inherited
source predicates above enumerate precisely the possible destinations on
each axis. The prefix conjunction supplies exactly the earlier interiors,
the marked face supplies the appropriate boundary interval, and the suffix
odometer supplies their full Cartesian product. Each choice sequence has a
different destination rectangle or local offset. Conversely any rectangle
containing the source supplies exactly one such sequence. This proves
equality with destination-first expanded-interval membership without any
finite-search premise.

## 5. Sparse stable radix on complete keys

For a stream of fixed \(h\)-bit keys and \(P\)-bit payloads, copy a unary
pass clock from the first key. One pass scans every record once, saves it
on a single reusable record tape, and remembers its final key bit in finite
control. It appends the record to bucket zero or one, rotating its key one
place to the right. The previous key bit is held only as a one-symbol
lookahead; the payload is copied unchanged. Concatenate bucket zero followed
by bucket one and advance the unary clock by one cell.

One pass preserves order among equal chosen bits. After \(t\) passes it
orders records by the original last \(t\) bits, most significant of those
bits first, with stable ordering on ties. Rotation exposes the original
next bit as the current last bit. After exactly \(h\) passes the key has
returned to its original position and the stream is stably sorted by the
entire original key. This proves the algorithm for all widths and record
counts, including duplicate keys. Empty input is handled separately.

Each pass costs \(O(R(h+P))\) for \(R\) records: record clearing,
distribution, every rewind, main-stream clearing, and bucket concatenation
are all complete sequential scans of at most a constant number of streams.
The pass clock costs \(O(h)\) to construct and erase and moves one cell per
pass. Thus the bill is \(O(Rh(h+P)+h)\), with no random lookup or hidden
host sort. Each of the two buckets and the main role retains at most
\(O(R(h+P))\) cells. Repeated passes reuse their origins; they do not need
\(h\) distinct backing regions.

Apply this first with \((R,h)=(C,K)\), then to returned target records
with \((R,h)=(Q,B)\). Since \(Q\le C\) and \(B\le K\), their sum is
the sparse term of (1). Local sorting or exposure required by the numerical
consumer is additional work until explicitly composed with that consumer.

## 6. Chronology and unique return

`gather` never writes the dense source. All its saved payloads therefore
belong to the input before any core mutation. A finite phase gate allows
the supplied test core to mutate the dense role only after gather. The test
core merely complements bits and is intentionally not a Gaussian inverse.
It witnesses the ownership distinction: saved source copies and current
core results occupy different roles.

The actual consumer contract has three parts: it reads the saved copies
without altering their numerical meaning, it returns a correctly computed
\(P\)-bit value for each target under the desired numerical contract, and
it finishes before the saved backing is erased. Numerical accuracy and
coefficient/reference consistency belong to that consumer. The transport
itself checks the target-domain part of the contract.

After sorting the returned \(B\)-bit global keys, retain only the next
return record on two small roles. Scan the current dense core stream once,
using the reset physical coordinate odometer. For each point, compare its
canonical key to the pending return key and check the unexpanded interior
condition \(A\le r_i<L-A\) for all axes. At a discarded target equality
is required, the returned value is emitted, and the next return is loaded.
At a kept interior, any pending key less than or equal to the current key
is rejected; otherwise the current core value is emitted. At dense end no
pending return may remain.

The first-face output rectangles form a disjoint partition of the discarded
set: choose the first axis whose local coordinate is outside \(I\), then
its unique lower/upper side. Thus the above keyed merge enforces exactly the
required target set. A missing key fails at its target. A duplicate remains
pending after its first occurrence and fails at a later coordinate or at
end. An interior return fails at that interior or earlier when it blocks
the next required target. No wrong target can be silently skipped. The
returned value replaces the current core value only on this partition.

The merge and its target tests cost \(O(M(P+B))\), plus loading \(Q\)
small return records, already covered by (1). The final erasure costs at
most the sum of current live lengths. Its touches are counted, and all
previously touched cells remain in the retained-backing bill.

## 7. Space, caller substitution, and compatible numerical consumers

The dense source and final stream each occupy \(O(MP)\). Saved copies and
their two radix buckets occupy \(O(C(P+K))\); the return stream occupies
\(O(Q(P+B))\), absorbed by that bound. Reusing buckets for later returns
does not add their lifetimes as disjoint storage. Descriptor/key/record
scratch is \(O(B+P)\). The largest unary face list is bounded by
\(O(gf_x)\le O(BC)\), also absorbed. Constants and the unary axis number
are \(O(B)\). The sum over the 30 high-water extents proves (2), even if
each bucket reaches its maximum on a different radix pass and even after
erasure.

In the source caller's admitted representation, \(P=\Theta(p)\) and
\(B=O(p)\), and the dense bit volume is \(V=MP\). The inherited volume
bound is

\[
 C\le 6M(gA/L)(1+2A/L)^{g-1}.
\]

When \(gA/L\) is bounded, the product factor is bounded. Equations
(1)–(2) give a per-group transport cost

\[
 O\bigl(V+C p^2\bigr)
   =O\bigl(V[1+(gA/L)p]\bigr),
\]

and retained backing \(O(V[1+gA/L])\). The source's deliberately looser
allowance \(O(V[1+(gA/L)p^2]\operatorname{polylog}p)\) therefore covers
this transaction. No dense \(Vp\) or \(gV\) term was absorbed into that
sparse allowance. Generic parameters retain the displayed \(C\) term;
one cannot call storage linear in \(V\) without bounding the copy ratio.

The dyadic core side and periods come from #4100's HALO/GAUSSIAN setting.
For the direct-Neumann splice in #6880, set the saved radius to any common
\(b\) with \(\max_i(J_i-1)W_i\le b<A\). Copies precede core mutation
as its theorem requires. If a numerical axis consumer needs a smaller
\(b_i\), a sparse pass retains offsets

\[
 b-b_i\le u_i < m_i+b+b_i
\]

and replaces them by \(u_i-(b-b_i)\), where \(m_i\) is the unexpanded
target length. This order-preserving filter yields exactly its original
expanded domain; its cost must be added, not assumed free. The constant
\(\ell+2\)-bit offsets may likewise be shortened by dropping checked
leading zeros. Payloads may be the consumer's full sign-magnitude complex
words because the transport treats them as opaque bits.

A returned local coordinate is lifted by its core origin and expanded
lower endpoint, then reduced modulo \(S_i\). Binary shift/concatenation,
ripple addition/subtraction, and truncation to the \(k_i+\ell\)-bit axis
field implement this conversion with a linear scan of the total coordinate
fields. Where rectangle descriptors or widths need production or decoding,
retain a conservative \(O(C(B+P)^2)\) sparse codec bill until an explicit
implementation is linked. That extra bill still belongs to sparse copies;
this package's tested transaction accepts the already canonical return
stream. A comparison with another consumer is not itself an executed join.

## 8. Evidence and remaining obligations

`verify.py` compares full emitted keys/payloads against a separate
destination-first Cartesian-interval oracle. It also checks exact source
preservation through a destructive core test double, sorted unique return,
work erasure with retained backing, and malformed return/chronology/radix
controls. Bit arithmetic is exhaustively checked for 1–5-bit fields.
These are finite corroborations of the universal invariants above, not a
formal proof kernel or a numerical inverse implementation.

The complete selected multiplication proof still retains its five
assumptions. This work addresses one explicit physical sub-obligation of
`precision_tape` and `analytic_recovery`; it changes neither the selected
certificate nor κ. Global reference generation, numerical consumer
admission, core correctness, outer transformations, full precision/recovery
budgets, and production of the canonical caller inputs remain outside this
transport theorem. **No new κ.**
