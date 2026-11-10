# Selected scalar fields on four tapes

## Physical contract

Fix W=64 and an integer payload dimension D>=1. The owner tape contains all
799 fields. Each complex field has D adjacent pairs of W-bit real and
imaginary records. Field f begins at `2*D*W*f`. Public and owned fields retain
the source WORD's identities and lifetimes. Reserve two clean staging tapes
of 2DW bits each, one clean one-bit carry tape and two finite-control bits.
The owner backing is 102272D bits; staging backing is 256D bits. These are
allocated bits, including cells that become zero during a move.

A unit head move, bit read or bit write costs one. There are four tapes for
all D. Each instantiated schedule is compiled for its fixed D and W. This
is not an encoded-D uniform controller. Initial layout construction, external
native calls, actual reset and outer compiler costs are not included.

## Clean record transfer

Let the source bit be x and the destination bit be zero. XOR-read x into a
clean control bit, XOR it into the destination, XOR it into the source, then
XOR-read the destination to clear the control. The result is `(0,x,0)`.
The four reads and two writes cost six. No payload bit is erased: running
the transfer back restores `(x,0,0)`. Traverse the whole record in increasing
address order. All moves are unit steps in the executable implementation.
The transfer requires a clean destination; the control detects a violation.

For ADD or COPY, move the full target and source fields to the two staging
tapes. Their owner slots become zero. Run the attributed local circuit once
for each of the 2D component records. Translate only its two data-ribbon
addresses by the record offset; the carry address remains zero. Every offset
change is charged as head travel. Return the full fields to their zero owner
slots, and rewind both staging heads. Source restoration is PR6511's circuit
contract. COPY retains its clean-target precondition.

For SCALE, move each real record to ribbon zero and each imaginary record to
ribbon one, in owner order. Run the paired local circuit at each coordinate.
Return the records in owner order. The unused staging tails stay zero. All
staging, carry and finite-control bits return to zero after each event.

Only the named fields are absent from the owner tape during a scalar event.
No other operation runs during this interval. Induction over the selected
word proves the original scalar action on every live field and preservation
of all other owner cells. Before every MOVE, INIT, CLEAR and final exit,
return the owner head to zero. The external operation must return the same
owner layout, clean staging/carry, and all heads at zero. Its own work is
not charged here. The full source lifetime check rejects dead or aliased
operands. This does not prove native behavior or physical erasure.

## Exact movement costs

Put L=2DW. For an ADD/COPY, choose either order for acquisition and either
order for return. If the successive field starts are a,b,c,d, the owner head
starts at h and visits each record in increasing address order. Movement is

```
|h-a| + |a+L-1-b| + |b+L-1-c| + |c+L-1-d|
+ 12*(L-1) + 4*(2D-1)*W.
```

The 12 terms include traversal of the owner and staging ribbons and their
rewinds. The last term moves both staging heads between local component
calls and back. For SCALE at field start a the movement is

```
|h-a| + 3*(L-1) + 8*(DW-1) + 4*(D-1)*W.
```

ADD/COPY transfers 8DW bits; SCALE transfers 4DW bits. Each transferred bit
costs four reads and two writes. The local circuit's complete move/read/write
bill is additional: 2D calls for ADD/COPY and D calls for SCALE. Physical
fixtures compare these formulas with actual Tape method counters.

## Minimum over visit orders, for every D

After an event the owner head is at the end of one named field, or at zero
at an external boundary. Thus at most two head states occur at a layer.
Acquisition and return choices give every allowed transition. This policy
returns all fields after each event; it does not cache whole fields between
events or vary their layout or internal traversal direction.

Every transition cost is affine in D for D>=1. For example, travel from the
end of field i to the start of field j is
`abs((j-i-1)*2WD + 1)`. Its sign is fixed on D>=1: it is positive for j>i
and negative for j<=i. Travel from origin and all within-field costs are also
affine. `affine_options` implements these exact signed formulas, separately
from the numerical distance evaluator.

The producer uses numerical minima at D=1,2 to propose affine potentials.
Those two samples are not the proof. The checker evaluates every symbolic
edge. For a potential inequality whose difference is AD+B, it requires both
A>=0 and A+B>=0. These two exact conditions prove nonnegativity for every
D>=1. It also checks every reachable state and a single symbolic attaining
path with the stated cost. The feasible potentials bound every allowed path
from below; the attaining path proves equality for every positive D.

The minimum staging movement is `1060978176D - 5196390`. Staging adds
38620160D reads and 19310080D writes. PR6513's local circuits add 117253520D
operations. The total is `1236161936D - 5196390`. The separate 7936D reset
requests are not physically implemented.

## Comparison and limits

The initial coordinate-at-a-time construction is retained in staging.py.
It uses only two W-bit staging ribbons and the same owner layout, local
circuits and unit operation tariff. Its complete visit-order minimum is
computed at D=1,2,3,17. Whole-field staging saves 822169424 moves at D=1 and
463823251912 moves at D=17. This is a space/time tradeoff: 256D versus 128
staging bits. The owner backing and local arithmetic are the same.

Repeated coordinate acquisition crosses field gaps of order D on each of D
coordinates; whole-field acquisition crosses them a fixed number of times.
The latter construction therefore has linear scalar work in D at fixed W.
The all-D formula is a scoped physical result, not a complete recursive
supplier tariff, a wall-clock speedup, an all-width claim or a new kappa.
Native/reset/layout/controller/outer work and independent acceptance remain
open. The 86 physical fixtures execute all 43 templates at D=1,2. They are
not a physical execution of the whole word or its native operations.
