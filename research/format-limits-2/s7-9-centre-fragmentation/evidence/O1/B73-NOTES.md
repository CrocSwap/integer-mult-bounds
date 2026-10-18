# B73 NOTES: overlapping cell cover for X faces. VERDICT: KILL at gate (20-min), LOCAL-PRICE [scope: SA heuristic upper bounds, not exhaustive]. ship=false

## Method (cell.c; reuses B68 line geometry/face census; one process, <1 min per run)
Faces = 4-sets of the 112 lines with raw reach >= 10 (24192, reproduces B68). A cell is a line subset; a face is confined iff all 4 lines are in one cell. SA (swap moves, 3e6 iters) maximizes faces inside ONE s-subset; summing over the 222/s cells that fit the 110-extra-copy budget (every line in <= 2 cells, 224 slots) gives an upper bound on the confined fraction (union only lowers it).

## Numbers (best single cell; per-cell max faces; bound = sum over cells in budget; bar = 12096 = 50%)
- s=8  : 36  of C(8,4)=70    -> 28 cells: <= 1008  (4.2%)
- s=16 : 322 of 1820          -> 14 cells: <= 4508  (18.6%)   [reach>=9: 657 of 91392 faces]
- s=24 : 648 of 10626         -> 9.25 cells: <= 6000 (25%)
- s=32 : 1120 of 35960        -> 7 cells:  <= 7770  (32%)
- s=56 : 3796 of 367290       -> 4 cells:  <= 15000 (62%, summed, overlaps double-counted; a 56-line cell is 7 blocks, no D4/centre frame, so it is not a block-sized cell at all: it is the whole X problem restated at half size)
High-reach faces are spread (~864 per line); in any s-set density is only 1.8-2% at s=16 vs the 0.4% global, nowhere near what a cell needs.
=> No block-sized cover (s<=32, the only sizes where a cell can carry a D4-type centre frame) confines >=50% with <=110 extra copies; best ~32% at an extra-copy count that already equals the budget, before any legality charge (B11/B16 shared-read rules) and before the 56 totals are even addressed. Break-even needs the 56 totals gone, so a 32% confinement does not remove them.
Gate failed -> no ledger pricing / B15 invoice run.

## Escapes (>= 3)
1. Cells = 2-flats / D4 structure of the faces' own 4 lines: not tested separately; the SA above is cell-shape-free so it bounds any shape of that size.
2. Faces not confined but the totals supplied differently (B7 esc.1, <= 10 helpers); this card shows overlap does not substitute for it.
3. Larger cells (s>=56) with a half-system frame: bound 62% summed but needs a new frame/centre structure (centres per cell) -- #646-type skeleton, unpriced; centre cost 22.6% b/unit (B15) makes any extra centre set prohibitive.
4. Partial confinement hybrid: B7 prices hybrids -0.10% b per converted block.
## Rescue check
Run CP-SAT/exact max-density on s=16 (a 322 SA result could be a local optimum; D4-sub-lattice seeds not tried); to reach 50% at s=16 it would need ~2.7x the SA value, implausible. Not run.
Files: cards/B73/cell.c
