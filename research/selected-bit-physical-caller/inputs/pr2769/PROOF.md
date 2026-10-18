# Physical parking for fixed numerical banks

We connect the selected BIT Word interface to ywz65's finite two-tape parking
controller. We use one shared parking tape and one packet port through a
well-bracketed sequence of arbitrarily nested calls. We restore parent values
into their original register objects, so suspended aliases remain valid.

David Arias's concurrent PR2753 supplies the all-size logical caller. In its
`recursive_call.Frame`, he creates separate numerical arenas for each child
and leaves physical bank reuse open. We contribute this numerical interface;
we retain payload and controller serialization as separate obligations.

## Contract

Fix two arenas with capacities C_0,C_1 and word widths b_0,b_1. Each capacity
belongs to the fixed machine description. Each slot has one physical tape,
and each arena has one template tape. Throughout the nested run, keep the
widths and capacities fixed. The retained `words.py` gives each live word
b binary cells followed by RIGHT, with LEFT at position zero. Enter with
word and template heads immediately after LEFT.

Let ell_j=max(1,ceil(log2 C_j)). For a live slot i in bank j, we encode

    [one bank bit][ell_j little-endian slot bits][b_j word bits].

The record has s_i=1+ell_j+b_j bits. We omit the numerical RIGHT delimiter;
we use the packet port's `$` terminator and validate it against the destination
template during restoration. The bank bit selects one of two fixed extents.

The caller may grant a declared subset of live slots to its child. For
example, it can first copy modulus, width and depth into three fresh slots,
then grant those copies. We park the remaining parent slots. The child must
clear its grants and numerical work before restoration. We promise to restore
the parked slots, not values that the caller explicitly transfers to the child.

The caller issues trusted, well-bracketed PARK/RESTORE operations. We do not
authenticate an arbitrary callee's authority to close an ancestor frame.
We require well-formed words and the retained finite register-allocation
contract. We permit a different free-list order after return; we preserve
live slots, values, object aliases and heads. Allocation histories and meter
counters are observations, not restored data.

## Construction

`BankParking.park` checks the empty packet port and issues BEGIN. It visits
both fixed slot inventories in order. For each live ungranted slot, it:

1. Writes the bank label, slot label and word bits to the packet port.
2. Writes `$` and rewinds the word and port with unit head moves.
3. Executes the retained PUSH table, then erases/releases the source word.

The port is empty after each PUSH. At return, only the declared grants remain
live in the numerical banks. We allocate no checkpoint tape for an ancestor.

`restore` first requires empty banks and an empty port. It probes the previous
parking cell and returns the parking head to its top. At a record it executes
POP, decodes the bank and slot, and selects that exact erased slot. It then
initializes the slot through the retained `Arena.zero`, copies the word bits,
and requires `$` exactly when the numerical head reaches RIGHT. It clears
the consumed port, then rewinds both heads. At F it executes END.

We select the original `arena.words[slot]` object. Allocating a different
object and assigning it the old slot number would not restore aliases.
The finite free-slot map may choose a new order, but a suspended reference
to any live parent Word returns to the same object, tape, value and head.

## Correctness and nesting

For one word, serialization preserves each bit in its original order. The
bank and slot labels identify its physical destination. PR2635's PUSH/POP
proof supplies exact packet order and consumed-record erasure. The validated
template extent prevents silent truncation or padding. Erasing the source
after PUSH makes that slot available to the child without discarding its
saved parent value.

After any prefix of a PARK operation, we have saved exactly the visited
ungranted slots, released those slots, and left the remaining slots unchanged.
Each saved record has a unique bank/slot pair. After the child clears its
banks, reverse POP restores each saved slot once. At F we have restored the
parent's entire parked live set and removed its checkpoint records.

We induct over a well-bracketed command sequence. BEGIN places the child's
frame above the parent's saved records. Matching restore stops at the child's
F marker, so it neither reads nor writes the older checkpoint below that
frame. After the child returns and clears its own live slots, the parent's
restore has the same premises. This proves arbitrary finite nesting, including
empty frames, unequal bank widths, sparse slot sets and retained child grants.
The finite tests below do not establish this induction by extrapolation.

The physical inventory is

    C_0 + C_1 numerical slot tapes
    + 2 template tapes + 1 parking tape + 1 packet-port tape.

It is independent of nesting depth. Slot labels, liveness and free-slot
selection range over fixed finite sets and may live in finite control.
The codec branches on finite labels or scanned symbols; it does not decode
word values or use a host depth counter. Simulator coordinates and meters
record execution without selecting its control path. An implementation that
stores its free list on a separate tape must add that tape and its scans.

## Complete sequential operation invoice

Count source/target Word operations, codec operations and the retained
parking-table operations. Exclude child computation and the caller's initial
preparation of any granted copies. Let r count parked word records, let
L=sum_i b_i, and let S=sum_i s_i. A word counts again each time a caller parks
it. For d matched frame pairs, the exact tape-operation counts are

    reads       = 14S + 10L + 32r + 15d,
    writes      =  6S +  3L +  8r +  2d,
    unit moves  = 12S + 10L + 30r + 12d.

These are counts in the retained sequential read/write/move API, not Python
wall-clock measurements or a count of a fully expanded multi-tape transition
table. Fixed finite-control bookkeeping adds O(C_0+C_1+r) per frame. Thus the
complete operation has O(S+(C_0+C_1)d) cost, with fixed-capacity control.

We derive the counts from the literal scans. For one b-bit word at its left
boundary, the retained routines have these costs:

| Routine | Reads | Writes | Unit moves |
| --- | ---: | ---: | ---: |
| Word.erase / Arena.free | 2b+3 | b+1 | 2b+4 |
| Arena.zero into the same erased slot | 4b+5 | b+1 | 4b+6 |

The zero-initialization row includes both the word and template rewinds.
For one s-bit record, the added scans have these costs:

| Part | Reads | Writes | Unit moves |
| --- | ---: | ---: | ---: |
| Supply record and erase source | 2s+4b+8 | s+b+2 | 2s+4b+10 |
| Decode, initialize and consume returned record | 2s+6b+9 | s+2b+2 | 2s+6b+10 |
| Retained PUSH plus POP | 10s+14 | 4s+4 | 8s+8 |

For each frame, BEGIN/END, four empty-port checks and r+1 boundary probes
add r+15 reads, two writes and 2r+12 moves. Summing gives the displayed
formulas. We also check PR2635's separate exact table invoice:

    steps  =  5S +  7r + 3d,
    reads  = 10S + 14r + 6d,
    writes =  4S +  4r + 2d,
    moves  =  8S +  8r + 2d.

The checker reports an auxiliary action total: the three complete API counts
plus one per fixed-inventory slot test and one per parking-command dispatch.
With C=C_0+C_1, this total equals

    32S + 23L + 72r + (C+31)d.

This definition does not silently include unmetered child arithmetic or grant
copy preparation. The caller must charge those operations where it performs
them. Reusing a fixed bank does not make coefficient evaluation free.

## Space and source binding

At a completed parking boundary the stack contains one F per open frame and
one R plus s_i bits per stored record. The packet port uses at most
max_i(s_i)+2 cells, including its markers. A conservative bound for the full
numeric slot/template spans is

    (C_0+1)(b_0+2) + (C_1+1)(b_1+2).

We count these spans even for erased slots. Add the current parking stack
and packet-port span to obtain the component's storage bound. Opaque caller
contents below the granted stack origin remain preserved and separately
owned. We claim no new total caller reserve.

We retain byte-exact sources in `vendor/`. `words.py` comes from Jose Manuel's
PR2697 at `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`.
`parking_machine.py` comes from ywz65's PR2635 at
`1662dda699d9ea57b3fb13a23873b087d765149f`. The copied PR2753
`recursive_call.py`, at `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, is a
reference-only application boundary; we never import or replay that caller
in this package.

At that boundary, a caller can copy modulus/size/depth into fresh slots of the
shared banks, grant those copies, park the other parent words, and build its
child context in the available slots. It must close that context and grants
before RESTORE. Our grant fixture checks this transfer with distinct encoded
extents. Wiring the complete iterative caller to this interface, and
serializing its payload, directory and generator continuation, remain open.
We leave Petalas's arithmetic-scratch and continuation-content audits separate.

## Verification scope

The checker authenticates source bytes before imports. It covers all 64 pairs
of three-bit words, sparse and empty inventories, translated parking/port
origins, arbitrary opaque ancestors, 602-bit words, child input grants and
1,501 nested frames. It compares aliases, complete word bytes, heads, live
slots, cleared storage and the exact operation formulas.

Controls distinguish correct values in the wrong slot from proper restoration;
reject live child work and changed widths/inventories; and expose physical
bit corruption or uncleared checkpoint cells. We retain the trusted-command
and successful-word-format premises. We claim no general interruption rollback,
hostile-code isolation, full fixed-tape caller, new exponent or formal-kernel
verification. Jose Manuel (`jmbarrancoml`) prepared this work with substantial
OpenAI Codex assistance. The source notices and Apache-2.0 license remain in force.
