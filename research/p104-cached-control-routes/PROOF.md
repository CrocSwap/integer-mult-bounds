# Local physical control cache

## Contract

Take the 43 width-64 gate templates emitted in PR6511. The first two ribbons
hold the two component words. The third ribbon holds one clean carry bit.
For ADD and COPY the words are target and source. For SCALE they are real and
imaginary parts. Each ribbon has its own head. The heads start and end at zero.
Two finite-control bits start and end at zero. Each unit move, bit read and bit
write costs one. A conditional write includes a read and write even when its
condition is false. PR3241 supplies this model and the unchanged Tape class.

This is a compiled fixed-width interface. Gate addresses, cache tags and the
instruction pointer are part of the compiled controller. They are not an
unpriced variable-size RAM. The construction does not provide an encoded-width
controller or acquire these local ribbons from the caller's owner store.

## Correct cache use

A cache slot is empty or contains the bit at one named wire. Loading an empty
slot uses XOR with that wire. Clearing a full slot uses XOR with the same wire.
No gate can write a cached wire. Thus the wire value is unchanged between its
load and clear, and each clear returns zero. Before a gate, its required
controls must be cached and its target must not be cached. A fixed mask selects
the one or two required cache slots for the conditional target write.

Induction over instructions proves equality with the logical gate stream for
every input bit string. Slot identity does not alter this argument: the
compiler assigns a free slot at each load and emits its actual mask. No
physical swap of cache values is implicit. The independent route checker
tracks wire tags at physical head positions. It checks every load, clear,
target, mask and exit. It does not inspect the optimizer's state trace.

The logical arithmetic, source restoration and clean carry contract remain
PR6511's result. This package binds those exact circuit bytes. Arbitrary bit
fixtures check gate equality; aligned signed fixtures also check Fraction
arithmetic. A test outside an arithmetic precondition proves only gate equality.

## Exact optimization domain

A state at a gate boundary consists of the cached wire set and three head
positions. The carry head is always zero. For the next gate:

1. Keep every already cached required control.
2. Choose any subset of the other cached wires, except the target, to retain.
3. Clear the other old cache entries and load missing required controls in any
   order that never uses more than two slots.
4. Move to the target and execute the gate.

Loads only name missing current controls. There is no prefetch, repeated
load/clear cycle or unrelated detour. Every visit uses a shortest direct path
on that ribbon. At exit, clear all cached values in either order and return
all heads to zero. This is the complete claimed policy class. An unrestricted
physical optimum, a weighted-cost optimum or a different circuit optimum is
not claimed.

The layer graph includes every allowed transition and every reachable state.
The producer uses exact integer dynamic programming. The retained certificate
contains all layer potentials and one path. A separate checker requires
exact reachable-state coverage, start potential zero and, for every edge,
`d(v) <= d(u) + cost(u,v)`. It also requires the claimed total to be no greater
than `d(v) + exit_cost(v)` for every allowed exit. Therefore the claimed total
is a lower bound on every permitted route. The retained path is checked edge
by edge and attains that total. This proves the stated optimum. It does not
rely on the producer having found a minimum correctly.

## Complete source-weighted bill

The source WORD supplies every scalar occurrence. ADD and COPY run once for
each real/imaginary component. SCALE runs once for the pair. For each template,
the checker compiles the unchanged PR3241 route and the new route and compares
their complete move/read/write bills. Every target write is retained. The
new cost is no greater for every template. RESULT.json gives all 43 rows and
their exact occurrence weights. Multiply these totals by payload dimension D
when the local interface is supplied separately for each coordinate.

All 62 INIT/CLEAR events have 128 bit-reset requests at width 64. Those 7936
requests are reported separately; they are not physically implemented here.
No native MOVE, global field acquisition, allocation, coordinate dispatch,
reset realization, owner cleanup or outer compiler cost is assigned zero.
The local saving is not a new kappa or a complete multiplication theorem.
