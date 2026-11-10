# Reverse-record parking

This is a scoped construction and written all-size proof. The finite replay
corroborates the proof. It is not a proof-kernel certificate or a complete
multiplication theorem.

## Contract

Use ywz65's PR2635 two-tape model. Each transition reads the parking head P
and packet-port head B, optionally writes either cell, and moves each head
by at most one cell. Every issued write counts, including an unchanged write.
The alphabet is `_,0,1,^,$,F,R`, where `_` is blank. A command selects one of
four entry states. All later actions depend only on a finite state and the
two scanned symbols. There is no length, depth, coordinate or floor register.

At entry P points at the first blank cell above its live suffix. Below that
top are frame delimiters F and records. The new representation of a packet
`b0 ... b(n-1)` is `R b(n-1) ... b0`. At the port, `^` occupies a-1 and B
points at a. A full packet has its bits at a through a+n-1 and `$` at a+n.
An empty packet is `$`. An empty port is blank on the cells the next output
will occupy. Length zero and unequal successive lengths are permitted.

PUSH requires a full packet and blank parking extension. POP requires a
record in the current frame and a blank destination port. BEGIN/END and
matched whole-packet PUSH/POP commands follow the trusted, well-bracketed
ownership discipline of PR2635. They do not expose arbitrary partial pops.
Every cell outside the described footprints may contain opaque arbitrary
data and must retain its value. The `^` marker and every boundary head return.

## Finite table

`controller.py` enumerates all 441 keys of nine states and two seven-symbol
reads. Each key has exactly one action. The nonrejecting rules are below.
An omitted write means no write, and an omitted move means no movement.

| State and read condition | Writes | Moves P,B | Next state |
| --- | --- | --- | --- |
| begin, P blank | P=F | +1,0 | done |
| end, P blank | none | -1,0 | end_check |
| end_check, P=F | P blank | 0,0 | done |
| push, P blank and B a bit or `$` | P=R | +1,0 | seek |
| seek, P blank and B a bit | none | 0,+1 | seek |
| seek, P blank and B=`$` | B blank | 0,-1 | copy |
| copy, P blank and B a bit b | P=b, B blank | +1,-1 | copy |
| copy, P blank and B=`^` | none | 0,+1 | done |
| pop, both blank | none | -1,0 | deliver |
| deliver, P a bit b and B blank | P blank, B=b | -1,+1 | deliver |
| deliver, P=R and B blank | P blank, B=`$` | 0,-1 | rewind |
| rewind, P blank and B a bit | none | 0,-1 | rewind |
| rewind, P blank and B=`^` | none | 0,+1 | done |

Two boundary rejection rules restore the initial P head without writes.
In end_check, a non-F cell causes P to move right and reject. In deliver,
P=F and B blank causes the same move and rejection. Other unspecified keys
reject without writing or moving. Every table move is in {-1,0,1}.

## PUSH invariant

Let P enter at h and the packet have length n. The entry writes R at h and
advances P to h+1. In seek, after k bit transitions, B is at a+k and every
packet bit is unchanged. Thus seek reaches `$` after exactly n transitions.
Its `$` transition erases the marker and places B at a+n-1.

After k copy transitions, for 0<=k<=n, the cells h+1 through h+k contain
`b(n-1) ... b(n-k)`, P is at h+k+1, and B is at a+n-1-k. The last k packet
bits are blank and all earlier bits are unchanged. This is immediate for
k=0 and follows for k+1 from the copy rule. At k=n, B sees `^`. Moving B
right terminates at a, with a reversed parked record, a wholly blank consumed
packet and P at h+n+1. No other cell changes. For n=0 the same rules erase
`$`, encounter `^`, and terminate after writing the single R record marker.

## POP invariant

Let the top record start at h, so entry P is h+n+1 and B is a. Entry moves
P left. After k deliver-bit transitions, for 0<=k<=n, the first k original
bits `b0 ... b(k-1)` occupy a through a+k-1. P is at h+n-k, B is at a+k,
and the consumed parking cells are blank. The remaining record prefix and
every earlier parking cell are unchanged. The inductive step reads b(k)
from the reversed record and writes it at a+k.

At k=n, P sees R. Its transition erases R, writes `$` at a+n, and moves B
left. Rewind crosses exactly n bits, then recognizes `^` and moves right.
It terminates with P=h and B=a. The original packet order and extent return,
the entire record is blank, and every other cell is unchanged. This also
holds at n=0. POP is therefore the complete-boundary inverse of PUSH.

## Frames, rejection scope and physical storage

BEGIN/END are inverse on an empty frame. POP never traverses an F delimiter.
An empty-frame POP and a nonempty-frame END reject with both entry heads and
every cell unchanged. Structural induction on any finite well-bracketed
command sequence now gives LIFO packet order, complete record/frame erasure,
head return and bit-for-bit opaque ancestor preservation. Nested packets
may have arbitrary finite lengths. No transition reads below the frame it
is allowed to inspect. The one shared packet port is supplied and consumed
by the caller, outside the parking tariff.

The blank-output precondition matters. Unlike PR2635's preflight scan, this
POP can write an earlier output bit before discovering an occupied later
cell. For example, park `R10`, let the output at a be blank and at a+1 be 1.
POP writes 0 at a and erases its parking copy before rejecting at a+1.
`mutation_checks` executes this exact scope control. No all-malformed-input
rollback or no-write-before-any-occupied-cell guarantee is claimed. A caller
requiring that guarantee needs a separately charged preflight.

At a valid boundary, the occupied parking suffix has exactly one cell per
live payload bit, one per live record and one per live frame, as in PR2635.
The full port has n bit cells and its two markers. There is no extra tape,
new alphabet symbol, runtime descriptor stack or increased occupied storage.
Erased backing capacity is not claimed to disappear. Existing forward-format
records cannot be read by this controller: all participants in an owned
parking region must use the new format, or pay for a separate conversion.

## Complete tariff and comparison

Count the literal table transitions in the preceding invariants.

| Operation | Steps | Reads | Writes | Unit head moves |
| --- | --- | --- | --- | --- |
| BEGIN | 1 | 2 | 1 | 1 |
| END | 2 | 4 | 1 | 1 |
| PUSH n | 2n+3 | 4n+6 | 2n+2 | 3n+3 |
| POP n | 2n+3 | 4n+6 | 2n+2 | 3n+3 |

For PUSH the transitions are entry, n seek, marker, n copy, terminal.
For POP they are entry, n delivery, marker, n rewind, terminal. The marker
transition writes twice for POP; every bit transition writes twice. Summing
the stated displacements proves the move counts, including empty packets.

For d balanced frame pairs, r matched packet pairs and total payload V,
counting each packet pair once, the new totals are

```
steps = 4V+6r+3d       reads = 8V+12r+6d
writes = 4V+4r+2d      moves = 6V+6r+2d.
```

PR2635's published totals are cited premises, not replayed here. Subtracting
the new totals from its `5V+7r+3d`, `10V+14r+6d`, `4V+4r+2d`, `8V+8r+2d`
gives exact savings of V+r steps, 2V+2r reads, zero writes and 2V+2r moves.
These quantities concern the valid matched-packet parking contract. They
are not a wall-clock benchmark, shortest-controller theorem, complete caller
invoice, recursive profile improvement or kappa gain.
