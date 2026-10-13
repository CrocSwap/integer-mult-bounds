# Coordinated owner repair on PR623

Conditional kappa = **0.001635527380375392**, exactly `51110230636731/31250000000000000`.
This improves PR623's `.001635490664920455` by `36715454937/1000000000000000000`.
The dispatch remains 64 JP8 + 8 CK, with 492 helpers per call.
Every supplier constructor, native verifier, controller, invoice and
assembly engine is byte-identical to PR623 and PR622.

The change reassigns whole helpers among literal owner bins. The separate
checker reconstructs every helper width and both program orientations
from newly built native artifacts, then checks chronology, physical
families, capacity, disjoint footprints, rank mass and exact moments.
Search scores nominate maps; the unchanged strict engine admits them.

## Replay

Python 3.11 or later, a C++ compiler and Boost headers are required by the
inherited baseline. All declared source packages are bundled and pinned.

```sh
bash research/complex-k492-owner-repair/verify.sh /tmp/k492-owner-replay
```

Set `K492_PYTHON` to select Python. The wrapper checks declarative inputs
and outputs, runs the complete fresh construction chain, then independently
checks the literal map and exact rational moment. Supplemental checks stay
active under `-I -O`; inherited verification runs with assertions enabled.

`comparison/` retains the credited PR622/PR623 inputs and exact native
hashes. Historical construction notes, `data/cand.json` and `data/search/` remain
unchanged PR623 provenance; they do not describe this new map. Source review and
platform receipts are in `../complex-k492-owner-repair-validation`.

## Proof boundary

This finite conditional witness retains the inherited all-size compiler,
common-label/mutable-source realization, whole-call hosting, precision,
tape/exact recovery, analytic transfer and bit H1-H5 assumptions. It is
not an unconditional multiplication theorem, kappa=1, a complete Lean
proof, a practical speedup or a packing optimum. See NOTICE.md for credit.
