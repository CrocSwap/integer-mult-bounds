# Merge native progress across unused cuts

The reciprocal response has zero coefficients at some transfer positions
in the old cyclic word. After those zero transfers are removed, some
intermediate native frames have no scalar use. This packet removes those
unused cuts from the native schedule.

For each field, collect consecutive native advances until the next scalar
event that reads or writes that field. Emit one advance before that scalar
event. At the end of the word, emit the remaining advances. Do not change
any scalar instruction, coefficient, frame, or scalar-event order.

This transformation preserves the exact physical operation. Moving a
native gate across an event on other fields is legal because the two gates
act on disjoint fields. A chain of frame maps then telescopes:

```text
(Gamma_k Gamma_(k-1)^-1) ... (Gamma_1 Gamma_0^-1)
    = Gamma_k Gamma_0^-1.
```

The original subspaces are nested. Thus the new rank is the sum of the
old ranks in that chain. The producer compiles the new ordered-frame
map and checks its exact phase. It does not infer the phase from a
subspace label.

The complete local profile becomes

```text
971 H1 + 237 H2 + 46 H3 + 12 H4 + 5 H5 + 11 H6 + 10 H7.
```

There are 1292 native children, with total rank 1792. This removes 340 child
calls from each frozen word. The direct forward and reciprocal backward
words still cost 6440 real scalar primitives. Each word still has 224
endpoint monomial maps, and the native side-map bound falls to 2584.
The two explicit metric-wrapper variants still cost 7080 primitives.

Every original native event belongs to exactly one emitted chain. The
payload records the source event indices for each chain. The checker
reconstructs the transformation, verifies every old and new frame, and
replays all 640 arbitrary input columns in all six words for both
providers. All 416 outside fields remain unchanged.

The 206 new native recipe records receive an exact independent phase
check. The check uses all 18 Pauli images and an exact reference column
to determine the complete 9-axis Clifford map, including global phase.
All remaining native recipes and all 224 endpoint adapters are retained
from the frozen source. No scalar phase convention changes.

For every 0<t<1, combining two positive child ranks r and s decreases
their native moment contribution:

```text
(r+s)^t < r^t + s^t.
```

Use t=1-b for the supplier exponent b. Each merged chain therefore
reduces the native moment at fixed dimension and width. The packet
does not turn that local comparison into a complete supplier bound.

Run `python3 -I -B emit_coalesced.py --out <new-directory>` and repeat
with `-O`. Compare the decompressed native payload and receipt bytes.

The full native contracts, scalar words, and all open caller obligations
are those in `NATIVE.md`. In particular, this packet does not supply
centre retention, helper progress, a terminal decoder, or a recursive
host.

The source response and cyclic path came from the coordinating,
new-core-transfer, and independent-review lanes, as cited in the frozen
model and native packets. This lane supplies the legal cut removal and
its full phase and content check. AI assistance was used.

No PR, push, commit, or publication is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
