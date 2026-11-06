# A linear marked-tape positive half

## Contract

Let W>=2, let x be any signed W-bit two's-complement integer, and let
u be a resident read-only bit. Write x=2q+p with p in {0,1}. The positive
stochastic half has the convention used in zxv's PR6092:

```
S(x,2,u) = q + p(1-u).
```

One work tape initially contains the consecutive cells

```
P0  b0 b1 ... b_(W-2) S(b_(W-1)).
```

The payload is little endian. `P0,P1` are parity-marker symbols;
`S0,S1` mark the most significant value bit. Interior bits use `0,1`.
The tape head starts on `P0`. A second read-only tape supplies u under its
stationary head. Both tapes may have arbitrary exterior contents.

There is no addressed operation, width counter, unary program or work area.
The machine reads only its state, the scanned work symbol and u. One transition
writes one work symbol and moves its head by -1, 0 or 1. It never writes the
coin tape. `TABLE.json` is the complete fixed table, with 33 rows in each
direction. Direction is a compiled choice between the two tables, retained by
the caller. A call starts in `F0` or `I0` and returns in the fixed state `H`.
The start/return handshake is the declared call convention, not an erased
input-dependent control value.

The forward endpoint is the same marked layout holding

```
(x, P0, u) -> (S(x,2,u), Pp, u).
```

The inverse restores x and P0. Both heads return to their starting positions.
The visited data interval is exactly W+1 cells. Including the stationary coin,
the complete visited extent is W+2 cells on two tapes. Exactly one initially
clean bit becomes retained parity. There are no other initially clean cells.
The markers and resident coin are supplied premises whose preparation and
delivery have not been charged by this local result.

## Forward invariant

`F0` moves from P0 to the first bit. `FS` walks right across the interior
bits. On `Ss` it leaves that symbol unchanged, stores s in the finite state
`FDs` and moves left. In `FDc`, reading an interior bit b writes c and
continues left in `FDb`. Thus, after processing bit j, all positions above j
contain the next higher original bit, and the finite state contains the old
bit j. The marked sign remains unchanged.

At P0 the state therefore contains p, while the value is q=floor(x/2).
Writing Pp clears the last data-dependent state bit into its retained cell.
If p=0 or u=1, the machine returns. Otherwise `FI` increments q modulo 2^W.
It replaces low ones by zeros until the first zero, which it replaces by one.
At the marked sign cell it flips that bit and turns around, including the
all-ones overflow case. `FR` walks left only over the zeros just written and
returns at P1. Every head movement is in the table.

Since

```
-2^(W-2) <= q <= 2^(W-2)-1,
-2^(W-2) <= q+p(1-u) <= 2^(W-2),
```

the result fits in W signed bits. Modular increment agrees with signed
addition, including q=-1 becoming zero. No additional arithmetic guard bit
is required. The marked sign cell remains the most significant result bit,
even when its value changes.

## Inverse invariant and exact image

`I0` branches on the retained parity and coin. If p=1,u=0, `ID` first
decrements the result modulo 2^W and `IR` returns over the newly written
ones. In the other cases this decrement is absent. At Pp the machine stores
p in `IUp`, writes P0 and moves right.

In `IUc`, reading an interior b writes c and continues in `IUb`. This shifts
the recovered q left and inserts p. At the marked sign cell it requires that
the incoming carry equals the scanned sign. This is precisely the necessary
sign-extension equality between the two highest bits of q. The matching
rule discards no bit: its sign is still present in the marked cell. `IB`
then returns left to P0 in the fixed return state.

For any signed y,p,u presented at the inverse boundary, put

```
q = y-p(1-u),   x = 2q+p.
```

An input belongs to the forward image exactly when x fits in W signed bits.
This is equivalent to q having a signed W-bit representation with its two
highest bits equal. If decrement wraps a signed extreme outside the range,
its two highest bits differ. Consequently the sign check rejects exactly
the nonimage inputs and accepts every valid inverse input. The forward
calculation and inverse shift prove both endpoint compositions on their
declared domains. The finite verifier also checks the complete inverse
boundary domain through width eight, including rejected points.

## Exact time and finite-state reversibility

The right scan and left shift, including entry and parity handling, cost
2W+1 transitions. When the increment is enabled, let k be the first zero
position of q, capped at W-1. If all W bits are one, set k=W-1. Increment
and return add exactly 2(k+1) transitions. Hence each direction costs

```
T(W,x,u) = 2W+1                         if p(1-u)=0,
T(W,x,u) = 2W+2k+3 <= 4W+1             otherwise.
```

The decrement in the inverse follows exactly the same number of bits as
the corresponding forward increment, so its time is identical. The bound
4W+1 is attained for x=-1,u=0, for every W>=2. It is an exact worst-case
bound for these tables, not a minimum constant among all programs.

Each directional table satisfies a standard sufficient criterion for an
injective partial Turing-machine transition map. Every target state has
one incoming head direction. For fixed coin, the target state and written
symbol identify at most one source row. To invert a microstep, recover that
direction, inspect the symbol at the preceding head position, recover its
unique source row and undo its write. The verifier checks this finite
criterion for every row. The direction selector is retained, so separate
forward/inverse calls are not identified when both end in H. This does not
construct a repeated-call compiler or claim a total permutation on malformed
tape configurations.

Linear time has the correct asymptotic order in this local layout. If a
deterministic one-work-head machine failed to visit the marked sign cell,
flipping just that input bit would leave its observations and all lower
writes unchanged. The two required outputs differ by 2^(W-2) in their lower
W-1 bits, a contradiction. The head must therefore travel distance W from
P and return, requiring at least 2W unit movements. The supplied program
is within a factor of two in its leading worst-case transition count.

## What changed and what remains

zxv's PR6092 supplies the signed-half contract and a reversible Boolean word
with W clean working cells. Its literal unary-walk lowering has an O(W^2)
program/time envelope. These are cited predecessor statements, not replay
targets here. This result changes the physical compilation interface: the
sign and parity are marked, and a fixed local table replaces that unary
program. It supplies a linear, scratch-free positive-half implementation
under this boundary. It is not a drop-in cost replacement in PR6244's
different packed caller.

Negative-coefficient halves, conversion to this layout, coin acquisition,
marker preparation, caller allocation, other arithmetic, native MOVE,
precision selection and the complete supplier invoice remain separate.
All five selected framework assumptions remain. No new kappa or complete
integer multiplication theorem follows.

## Verification scope and code constraints

The universal statements above have a written proof. The finite replay
executes the literal table, compares to integer divmod, checks complete
round trips, exact times, exterior cells, the inverse image and rejecting
faults. It imports no predecessor executable and writes no files. Stdout
contains a newly computed receipt bound to all package-file hashes.

All executable loops have finite bounds. Tape simulation is capped at
4W+1 transitions and the executable accepts 2<=W<=4096. The theorem is not
limited to that executable guard. Table initialization has 66 rows, the
declared exhaustive domains are explicit, and each function is below 60
lines. There is no recursion or dynamic source evaluation. Python-managed
allocation is a deviation from static allocation: the interpreter and
verifier allocate bounded tape copies and finite-domain records. Those
allocations are verification instrumentation, not hidden physical cells in
the transition model. The table owns no mutable global state, and every
mathematical check remains enabled under -O. The mutation-test callbacks
have a fixed finite target list and are not physical machine operations.

## Credit

This contribution was produced by Nick Petalas. Credit zxv's PR6092 for the
local contract and faster-layout question, PR6066 for the logical restoration
interface, JoyboyBrian's PR6095 for the related marker interpreter,
AAAmirinu's PR6244 for the separate reached-coin interface, Nick Petalas's
PR6026, Ali Romman's PR5599 and the retained stochastic/native lineage.
Binary shifts, ripple increment/decrement and the reversible-machine local
criterion are classical. The contribution is the explicit fixed table,
its exact all-width signed boundary and its complete local resource bound.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
