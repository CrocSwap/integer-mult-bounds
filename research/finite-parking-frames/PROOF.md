# A finite controller for the parking subinterface

The result is a refinement of the **matched push/pop usage** in PR2574's
`frame.invoke`, not a replacement for every call to `ParkFrame.pop(size)`.
That wrapper pushes complete inactive packets, then pops those same extents
in reverse order. It also opens a second view above its own parked packets
before delegating a callee. We replace those particular extent/floor
descriptors by physical record/frame delimiters. Packet production, dynamic
logical-tape allocation, arithmetic, arbitrary-size partial pops and the full
invocation dispatcher remain outside this result.

## 1. Two-tape domain and finite control

There are two bi-infinite tapes, P (parking) and B (one packet port), and a
fixed alphabet `{blank,0,1,^,$,F,R}`. One step reads the two head cells,
optionally writes either, and moves either head by -1, 0 or 1. The ten
nonhalting states and 490 symbol-pair entries are explicit in `TABLE.json`.
The only action-selection key is `(state, scanned P symbol, scanned B symbol)`.
Neither a width, coordinate, stack, depth, length nor floor is a control
register. The simulator's integer coordinates and counters implement and
measure the mathematical tapes; they do not select a transition.

At each public entry P points to the first blank cell at its top. Its live
suffix encodes nested frames by F and individual packets by `R b0 ... b(n-1)`.
The packet port has a fixed `^` at position a-1 and its head at a. A full
packet has bits at a through a+n-1 and `$` at a+n. An empty *packet* is `$`;
an empty *port* has blank cells available for the next packet. These are
different states. A PUSH requires a full finite packet and blank parking
extension. A POP requires a blank port through its eventual end marker.
All payloads, including parked caller data, may be arbitrary binary strings.

BEGIN appends F. END is legal only when that F is the top occupied cell.
POP is legal only when the top item is a record in the current frame. Nested
BEGIN/END requests must be properly bracketed by the caller, and a delegated
callee must not issue END for its caller's frame. This is the same trusted
sequential ownership discipline as the predecessor, not hostile-code
isolation. Markers prevent POP from consuming an empty frame's ancestor data;
they do not authenticate which program issued an END command.

One invocation starts by BEGIN at an arbitrary opaque caller prefix, operates
within that frame, and ends by END after consuming its own records and child
frames. The caller prefix can use every alphabet symbol and is neither
scanned nor modified. A nested invocation begins above the parent's parked
records, implementing the predecessor's second-view boundary.

## 2. PUSH invariant

Let the entry parking head be h and packet length n>=0. The entry writes R
at h and advances P. After k iterations of `push_copy`, for 0<=k<=n:

* P contains `R b0 ... b(k-1)` at h through h+k, and its head is h+k+1;
* those k packet cells are blank, B's head is a+k, and the remaining packet
  and its end marker are unchanged.

Each bit transition proves the induction. At `$`, the controller erases the
end marker and moves B left. `push_rewind` crosses exactly n erased cells,
recognizes `^`, and moves right to a. P stays at h+n+1. The complete record
is parked, the whole consumed packet including `$` is blank, both boundary
heads are in their specified positions, and every other cell is unchanged.
The same argument includes n=0: only R and `$` are written/erased.

## 3. POP invariant and why the first pass is necessary here

Suppose the top record is `R b0 ... b(n-1)` beginning at h. Entry P is
h+n+1, B is a. `pop_measure` walks backward over the n bits while advancing
B over blank cells. It stops on R with B at a+n. This determines the output
end position by a head displacement, without a binary/unary length counter
or an extra tape. No payload cell is written in this pass. Encountering F
on an empty frame rejects and restores both entry heads without writes.

`pop_return` walks P forward through the same n bits to its blank top,
holding B at a+n. It writes `$` there and moves both heads left. After k
`pop_copy` transitions, for 0<=k<=n, the final k bits of the record are
erased from P and installed in their original order at the final k packet
positions; the two heads are h+n-k and a+n-1-k. For k=n, P sees R and B
sees `^`. Erasing R and moving B right completes the operation with P at h
and B at a. This proves order preservation, exact packet extent, complete
record removal and exact preservation of all other cells, including n=0.

The first pass checks all future output bit/end cells are blank before the
first output write. It is not a lower bound on the cost of other models.
Malformed tapes may reject after intermediate movement or writes; no general
rollback semantics is claimed. The two valid-boundary rejection statements
(POP of an empty frame and END of a nonempty frame) are exact no-write
statements, not a universal malformed-input guarantee.

## 4. Nested preservation and correspondence to the caller

BEGIN and successful END are mutually inverse on an empty frame and leave B
unchanged. PUSH and POP are mutually inverse at their complete operation
boundaries, including erasure/restoration of `$`. Their transition machines
are not claimed locally reversible: rejecting/clearing transitions need not
be injective on all malformed configurations.

No operation within an open frame scans below its own F. PUSH only extends
the top; a successful POP stops at its top record's R; an empty POP inspects
F; END inspects/removes only the top F. By structural induction on any finite
well-bracketed sequence of nested frames, closing a frame restores its entry
parking prefix and top exactly. Arbitrary contents below the entry position
are opaque and survive bit-for-bit. All nested packet lengths may differ,
be zero, and be chosen from the actual caller's values.

Map each predecessor matched `push(packet)` to one physical PUSH and map its
later matching `pop(saved_extent)` to POP. The R markers identify packet
boundaries, including zero-length records, so the externally saved extent is
unnecessary for this usage. Replace each local/child `ParkFrame` boundary by
BEGIN and its successful `close` by END. Properly bracketed calls, matched
records and the second frame above caller records give the same ordered
payload restoration and ancestor preservation. The implementation does not
expose predecessor partial pops that split or join saved records. Serializing
several caller tapes through B, supplying packets and consuming outputs are
additional caller operations and are not free work claimed by this table.

## 5. Exact charges and physical storage

A step reads both cells, including ignored symbols. Count a write whenever
the table issues one, and a move per unit head displacement. Reads, writes,
moves and steps are distinct accounting measures; they are not summed into
the predecessor's payload-only tariff.

| Operation | Steps | Reads | Writes | Head moves |
|---|---:|---:|---:|---:|
| BEGIN | 1 | 2 | 1 | 1 |
| END | 2 | 4 | 1 | 1 |
| PUSH n | 2n+3 | 4n+6 | 2n+2 | 3n+3 |
| POP n | 3n+4 | 6n+8 | 2n+2 | 5n+5 |

The loop invariants count each scan and prove these equalities for all n.
For a complete balanced segment with d frame pairs, r matched packet pairs
and total packet volume V (each pair counted once), the exact totals are
`steps=5V+7r+3d`, `reads=10V+14r+6d`, `writes=4V+4r+2d`, and
`moves=8V+8r+2d`. These are parking-controller costs only. All parent and child
uses are counted when they occur; there is no uncharged runtime descriptor
stack. At a boundary the occupied parking suffix contains exactly the live
payload volume plus one cell per live record and one per live frame. The
single packet port needs n bit cells plus its two markers for length n.
No bytecode, width table or depth-dependent finite-control alphabet is hidden.

## 6. Evidence and limits

The finite transition table, exact bit-string endpoint tests, separate dense
interpreter, translated heads, large packets, deeply nested frames and actual
boundary controls corroborate the invariants. The all-size statement follows
from the written induction, not extrapolation of those finite tests.

PR2574's exact source and its retained `pipeline.py`/`streams.py` are pinned as
reference text and never executed. Its selected numerical leaf, arithmetic
precision, registry access discipline and complete return wrapper are not
reproved. This closes one concrete parking control interface; it does not
provide fixed-tape allocation for the whole supplier, a complete invocation
dispatcher, current source-production cost, recursive reserve, a native
supplier, a new kappa or a proof-assistant theorem.
