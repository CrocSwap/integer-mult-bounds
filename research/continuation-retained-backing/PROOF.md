# Complete retained backing of the nineteen-tape continuation bank

## Source and quantified domain

Fix the unchanged `Stack` of [#5356](https://github.com/CrocSwap/integer-mult-bounds/pull/5356)
and `return_output` of [#5368](https://github.com/CrocSwap/integer-mult-bounds/pull/5368).
Their exact heads and byte exports are in EXPORTS.json. There are k payload
tapes, one control tape, one descriptor tape and one relay; k=16 gives nineteen.
These pending predecessor implementations and their successful-call contracts
remain explicit premises, not independent supplier admission.

Consider any finite history of successful, properly nested calls in this bank.
Use its contiguous binary-segment ABI. Work appends binary symbols, reads and
moves within its current segment, and erases previously written body cells;
it does not write arbitrary blanks at remote addresses, change an ancestor,
replace a Tape, or shorten cells. Descriptor production obeys the same rule.
Each output return has the reserved empty parent role and distinct empty relay
required by the predecessor. Interrupted calls are outside the theorem.

The quantity counted is **the sum of lengths of all k+3 Tape.cells arrays**,
including initial prefixes, markers, parked words, erased tails and blank entry
history. It is neither nonblank content nor Python list allocator capacity,
object/heap memory, maximum visited address, physical allocation-controller
correctness or a complete recursive multiplication caller's stock. Reads and
moves in the literal Tape do not allocate; a write, even of BLANK, does.

For tape j let b_j be its initial origin, just after its fixed initial marker.
The marker and any dirty prefix occupy b_j cells. Let K_j be its entry backing
length, with K_j>=b_j; all cells after the initial current body are blank.
Warm blank tails are allowed. We state root entry with empty current bodies;
initial data loading is part of the history. Initial prefixes never change.

## Exact path and history formula

A node v is one current lexical segment. For payload role i, let a_i(v) be
the maximum binary body length reached *anywhere during that node*, including
work later erased and outputs delivered by its children. Let D(v) be the
maximum descriptor length reached, including erased interior production.
Exact maxima give equality below; proved upper bounds give a sufficient grant.

At a call edge e from parent u, write s_i(e) for each parked body length,
h_i(e) for its head offset, and d(e) for its descriptor length. Thus
0<=h_i<=s_i<=a_i(u) and d(e)<=D(u). Define relative payload origins by

```text
o_i(root) = 0
o_i(child) = o_i(parent) + s_i(e) + 1
f(e) = sum_i h_i(e) + 2k + d(e) + 3.
```

Every successful push creates a child node, including a child that does no
work. This convention accounts for the new payload LEFT delimiters even when
both bodies are empty. Let L(e) be the result length actually delivered along
an edge. For a forest of root invocations on the same bank, take all maxima
over the **entire history**, restarting o at zero for each root. Put

```text
E_i = max_v (o_i(v) + a_i(v))                    payload role i
E_c = max_root_path sum_e f(e)                  complete control frames
E_d = max_v D(v)                               shared descriptor
E_r = max_return_edge L(e)                      shared relay.

retained_j = max(K_j, b_j + E_j)
retained_total = sum_j retained_j.
```

Empty edge maxima are zero. This is a complete formula for every one of the
k+3 modeled tape arrays, not an extra space term to be added to an uncounted
continuation stack. Equality refers to the completed successful history (or
a history ending at a completed boundary). Its final historical maxima give
prospective grants that also bound every partial push/pop interior. A prefix
ending mid-push would need a partial-frame model for an exact online identity.

The coordinatewise history principle already appears for another implementation
in [#5286](https://github.com/CrocSwap/integer-mult-bounds/pull/5286). The new
source-specific content here is the nested payload-origin recurrence, the exact
unary-frame frontier, the descriptor/relay sharing and their composition through
the actual output-return schedule. The older coefficient evaluator's stack
backing results concern a different representation.

## Proof at individual operations

Tape.write extends cells exactly to max(old length, head+1); it never shrinks.
Its read and move methods do not extend cells. Thus capacity is its entry
length or one past its largest written address, whichever is greater.

At node v, its initial payload marker is at b_i+o_i(v)-1. Appending an a-symbol
word writes no farther than b_i+o_i(v)+a-1, giving capacity b_i+o_i(v)+a.
Erasure writes only within the previous word. A push scans the parent word
and writes LEFT at its end: the new capacity is b_i+o_i(parent)+s_i+1,
which is exactly b_i+o_i(child) even for an empty child. Partial pushes are
dominated by that completed child boundary. Pop clears existing delimiters
and words; it does not add a farther write. Output installation is a binary
append in the resumed parent node and is included in that node's a_i.
This proves the payload coordinates by induction on the nested calls.

The control push emits one complete f(e)-symbol frame at the previous top.
All older active frames form a contiguous prefix. Partial pushes write a
prefix of the completed frame. Pop only clears that existing frame and
restores the earlier top; the largest control address is therefore exactly
the largest active path sum. Different siblings reuse its erased tail.

The descriptor always has its single initial BASE, and push erases it before
child production. Pop erases the child descriptor and restores the parent's
saved word. Each restored word was already produced earlier, so restoration
cannot exceed the maximum D. This includes the original and restored copies
without charging a new descriptor tape at each depth.

The relay is empty between returns. Each return writes L symbols at its fixed
origin and erases them after copying to the parent. Hence its history maximum
is max L, with no depth sum. During the first copy the child output and relay
are both present; during installation the parent's output is included in its
payload coordinate. All these arrays are counted simultaneously in the sum.
Taking max with K preserves arbitrary erased entry capacity. All coordinate
maxima remain allocated even if attained on different branches or invocations.

If the supplied a,D are exact, each nonzero maximum is attained by an actual
binary write or delimiter/frame write. Therefore equality holds. If they are
only upper bounds, the same argument proves a prospective sufficient grant.

## Convenient complete grants and the missing production premise

Let V be a history-wide upper bound, at every node, for the sum of parked
ancestor payload extents plus the sum of that node's local role peaks. Let h
bound active edges, P the maximum path sum of parked descriptor lengths,
dmax=max D and Lmax=max L. Then E_i<=V+h, E_c<=V+(2k+3)h+P,
E_d<=dmax and E_r<=Lmax. Since K_j>=b_j,

```text
total <= K0 + (k+1)V + (3k+3)h + P + dmax + Lmax
      = K0 + 17V + 51h + P + dmax + Lmax       when k=16.
```

This grant is independent of the number of calls and includes historical
role rotation. The exact vector formula is usually much tighter.

Alternatively define G(v)=sum_i a_i(v)+D(v)+2k+3. If every root-to-node path
has sum_v G(v)<=B, each of the k+3 extents is at most B. Thus
**total<=K0+19B**. A proved geometric bound G(v)<=C*rho^depth*Vroot,
0<=rho<1, gives total<=K0+19*C*Vroot/(1-rho). The constant marker/header
term is already in G and cannot be omitted at small nodes.

These are conditional composition statements. A production proof must derive
the actual local peaks and descriptor/path summability, and charge K0. The
fixed-tape ABI alone does not imply O(Vroot). At depth D, parking M symbols in
one role at each level leaves D(M+1) cells in that role and D(2k+3) control
symbols even with zero head offsets and empty descriptors. All-empty nodes
still accumulate k payload delimiters and 2k+3 control symbols per edge.
Shrinking payload alone is insufficient if every frame copies a root-sized
descriptor. These are counterexamples to unsupported composition arguments,
not objections to the predecessor local-time theorems.

## A source-derived local peak for compact work

For unchanged successful `compact.execute`, let a valid complete binary layout
have b address bits, R=2^b records and positive record width w. Then every
lexical payload Role body has length at most **R(w+b)**, throughout execution:

| Source operation | Maximum body of any one Role |
| --- | ---: |
| ordinary digit exchange, digit permutation, flip | Rw |
| rotate left/right/output | Rw |
| repair good and output | Rw |
| repair holes | R |
| repair keyed bad, radix bucket/output | R(w+b) |

For rotation and digit operations each buffer receives only portions of one
complete rectangle, and output has R records. Repair emits at most one key
plus payload per exceptional record. Radix passes partition and concatenate
the same J<=R complete (b+w)-bit records; they do not duplicate records into
one buffer. All writes are append-only and erase resets the logical body.
This proves the bound for any number of valid passes. Successful slot reuse
places successive empty Role bodies in the same physical segment, so its
local high-water obeys the same bound. If b<=w, this is at most 2Rw; without
such a relation, the address-key cost cannot be discarded as a constant.

Erasure does not release a lexical owner: radix loop variables and repair
locals can retain erased Roles. This lemma does not prove sixteen-slot
sufficiency. The inherited weak-reference allocator, logical length facade,
source bulk read arrays, layout/control/descriptor production and a compiled
physical allocator remain outside the modeled tape-capacity theorem.

## Discriminating implementation evidence

The verifier authenticates all exports before compilation and executes the
unchanged methods. A checker-only guard rejects an insufficient coordinate
grant **before** each Tape.write can grow its array. It also checks literal
monotone write semantics. Declared small call trees predict capacities before
execution; endpoint snapshots and final array lengths are checked separately.

With k=16, sixteen root invocations each use a 64-cell child temporary in a
different role. Every fresh owner retains 142 cells, but one reused owner
retains **142,206,...,1102**. Taking the maximum standalone total would grant
142 and fail. A child that writes/erases 4096 cells before returning one bit
retains 4175 versus 80 for the same boundary sizes and a one-cell interior.
Those erased writes must be in a(v), not inferred from endpoint W or L.

The six compact-source calibrations execute both layouts with preserved
prefixes of lengths 0,257,4096, sixteen occupied parent roles and a complete
128-record, 1024-bit child output. The independently checked permutation and
complete return state agree; the predecessor's return bill remains 24388.
The source-derived local grant is R(w+b)=128*(8+7)=1920 per payload role.
These finite observations corroborate the source induction, not full
production recursion, selected-source admission or formal-kernel verification.

New proof/checker by zxv with substantial OpenAI Codex assistance. Predecessor
notices and contributor credit are retained in README.md and vendor/NOTICE.md.
