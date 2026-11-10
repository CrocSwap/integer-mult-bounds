# Separate physical child-shape replay

This author-side implementation executes the literal producer and linked-split
tables with its own sparse transition semantics. It never executes David
Arias's `Machine` or `Tape` interpreter. The exact unchanged predecessor code
is authenticated before the producer is imported. In the registered package,
the snapshot must also equal the adjacent active `shape/producer.py`.

The read-only normal and optimized checks rebuild 256 shape cases, 32 literal
producer-to-child-split cases and five rejecting controls. They check every
borrowed input byte and head, exact canonical binary grants, opaque child-data
order, untouched ancestor prefixes, and physical erasure of scratch and local
markers. Separate finite consumers erase delivered grants and child copies;
these are owned outputs with no productive credit.

The linked source is one complete parent bank of size `A_parent*R_parent`,
which equals `A_child*L*R_child`. It is not the full parent packet of size
`A_parent*L*R_parent`. The producer uses nine fixed tapes and the linked split
uses `L+11`. Every runtime row is a symbol branch, write, unit move, fixed jump,
halt or reject. The interpreter alone stores numeric heads and statistics.

The finite maximum recorded here is 72.75 producer microsteps per parent cell;
it is not a universal resource bound. The written induction and resource
proof are in `shape/PROOF.md`. The separate actual codec/stack case is in
`shape/verify.py`; this checker does not claim to independently replay that
whole boundary.

The physical H header is still an input. H-from-width, ancestor-weight
generation, arbitrary recursive traversal and a Gaussian child remain open.
No new generic arithmetic theorem, kappa, external review or scientific
admission is claimed. Arithmetic is standard; David Arias supplies the
unchanged machine/counter framework and PR6719 supplies the router. New
source-bound lowering and this separate review were prepared for thu-nmrc
with substantial OpenAI Codex assistance, Apache-2.0.

Run `python3.12 -I -B independent.py`, and repeat with `-O`.
