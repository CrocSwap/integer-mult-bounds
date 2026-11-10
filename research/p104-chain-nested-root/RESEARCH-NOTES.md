# Scope and boundaries of the chain-nested root

The object is one exact caller for the unchanged #6824 native word. The frozen
heads and scope are in `TASK.json`. Notes of earlier steps stay as
`RESEARCH-NOTES-6824.md` and `RESEARCH-NOTES-6805.md`.

The selected shape is `(9|9)`: every child has size one, so there are no binary
supplier nodes. `chain_root.py` is parametric in shape. `(4,4,1|1,4,4)` is built
in every replay as the gate. Only those two shapes are priced in this package;
the formula is not asserted for a shape it does not replay.

The ordinary bases use pivots of absolute value one only, so all caller scalars
are integers (`ADD` coefficients in {±1, ±2, −3}, `SCALE` by −1). This raises the
gate count compared with a dyadic-pivot form and changes neither the invoice nor
the crossing.

No exhaustive novelty search or optimality claim is made.
