# Exclusive field cache for the selected scalar caller

## Contract and ownership

Keep PR6527's field-major owner tape, two clean complex-field staging tapes,
one clean carry bit and two payload control bits. At width W=64 and positive
payload dimension D, each staging tape has L=2DW bits. Owner backing is
102272D bits and clean staging backing is 256D bits. There are four tapes.
The compiled controller names fields and physical banks. Those static names
and the instruction pointer are not additional payload arrays. As in the
predecessor, no uniform encoded-D controller is supplied.

A live field has exactly one authoritative location: its owner slot or one
staging tape. If it is staged, its complete owner slot is zero. A free staging
tape is zero. Cache tags do not authorize a read from an evacuated owner slot.
All data-ribbon heads are at zero between local events, except the owner head,
whose last field position is retained and priced. The carry and two control
bits return to zero after every circuit and transfer.

Acquisition moves a complete field from its owner slot to a free staging tape.
Eviction moves it back to its zero owner slot. Use PR6527's exact clean transfer:
four reads, two writes per bit, with unit traversal and complete control return.
This is reversible data movement, not a copy followed by unpriced erasure.

An ADD/COPY needs the two distinct named fields. Keep any required resident
field in its current bank. Evict unneeded fields and acquire missing operands.
The physical circuit takes the target and source bank in that order; a bank
assignment changes the compiled tape names, not the data. Run all 2D component
circuits and rewind both staging heads. Retain both complete fields afterward.
The ADD restores its source. COPY keeps its original clean-target precondition.

Before SCALE, flush both cached fields and execute the exact PR6527 SCALE
protocol. It returns empty staging tapes and a complete owner tape. Before
MOVE, INIT, CLEAR and final exit, flush both fields and return the owner head
to zero. The external operation's payload work is not executed or priced here.
Its complete owner layout, clean-workspace and origin-return contract remains
a premise. Physical reset and native implementations remain open.

The invariant is inductive: acquisition and eviction move the sole value;
the scalar circuit changes only its target and restores source/carry; the
flush restores the complete owner state before any external work. Unrelated
owner cells are never changed. Thus the selected scalar actions and ownership
are preserved for arbitrary valid record inputs and any positive D.

## Exact policy class

The policy has two whole-field buffers, no prefetch and no field relabeling.
A required resident field is kept in its current bank. For a missing field,
try each free-bank assignment. Try every order of the required evictions and
acquisitions that keeps each acquisition destination clean. Each transfer
traverses its record in increasing order. No payload field is acquired unless
the current ADD/COPY needs it. Every SCALE and external boundary flushes.
The scalar event order, layout, local circuits and workspace are fixed.

A state is the ordered pair of resident field labels and the last owner-head
field, or the origin. At most four states occur at each selected event layer.
The state graph includes every allowed action order. No pruning or heuristic
search is used. The optimum does not cover other circuits, a SCALE that remains
cached, arbitrary prefetch, other layouts or weighted operation tariffs.

## Affine cost proof

Let the owner head be at the end of field i. The distance to field j is
`abs((j-i-1)*2WD+1)`. Its sign is fixed for every D>=1. From origin, the distance
is `2WD*j`. A full-field transfer adds `3*(2DW-1)` moves and `12DW` reads/writes.
It therefore costs the seek plus `18WD-3` operations. This includes both tape
traversals, staging rewind, every data read/write and clean control return.

For an ADD/COPY, the unchanged local circuits cost `2D*local_cost`, and the
record-to-record travel and final rewind cost `4*(2D-1)*W`. SCALE uses the
predecessor's complete exact movement formula, adds `24DW` transfer reads and
writes and `D*local_cost`, after all required evictions. A boundary adds every
eviction and the final owner-head return. Every edge is affine in D.

The producer uses D=1,2 minima to propose affine potentials. The checker uses
the exact symbolic edge formulas. For each edge difference AD+B, it requires
A>=0 and A+B>=0, which proves the potential inequality for every D>=1. It also
checks all reachable states and an attaining symbolic path. These checks give
a lower bound for every permitted path and a path that attains it. Two sample
dimensions alone would not prove this result.

The complete scalar cost is `800847760D - 5118198`. The freshly checked PR6527
baseline is `1236161936D - 5196390`. The improvement is
`435314176D - 78192`, strictly positive for every D>=1. This is about 35 percent
of the complete predecessor scalar bill, with exactly the same workspace.
All 7936D unimplemented bit-reset requests remain separate. No native,
initial-layout, uniform-control, full supplier or outer cost is set to zero.

## Evidence and limits

An independent symbolic checker tracks field authority and live ownership
without calling the optimizer's transition function. It checks the complete
selected word, every acquisition/eviction and all external boundaries. A
second whole-word evaluator runs all actual scalar gates and compares every
owner record at every prefix with exact signed arithmetic. Its native calls
are explicit fresh-grid stubs and its INIT/CLEAR actions are explicit reset
stubs. It does not prove native semantics, native accuracy or physical reset.

Literal physical windows cover every one of the 43 scalar templates at D=1,2,
zero/one/two cache hits, SCALE flushes and all external boundary types. They
start from complete valid cache/owner states of the source policy. Arbitrary
window payloads check exact bit-circuit equality and exclusive-owner cleanup;
arithmetic preconditions are checked by the complete scalar/grid-stub trace.
All physical payload access uses the unchanged metered Tape methods. Direct
snapshots are only fixture observations, outside the execution bill.

Each instance has compiled fixed-width and fixed-dimension control. The
all-D statement is about the family of these physical schedules, not a
uniform multiplication algorithm. The complete physical native word, actual
reset, precision admission, full supplier funding, outer transfer, independent
human review and proof-kernel acceptance remain open. No new kappa or selected
frontier change follows from this scalar result.
