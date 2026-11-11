# Exact sender support and chronology exclusions

Replay the literal selected #7001 word over 659 independent binary input
rows. ADD applies XOR in its declared common chart. SWAP exchanges rows and
charts, MOVE changes the chart, and INIT and CLEAR use the retained owned
allocation and erasure semantics. The complete final chart vector and all
arbitrary-input public rows match the selected interface. This proof uses
the necessary chart and linear-row contracts of that replay.

## Fixed recipient route

There are 360 consecutive public-sender contact triples `MOVE F→H`,
`ADD A→B`, `MOVE H→G`, with ranks `(6,7,8)` and nonzero cargo. A direct
`F→G` can expose the sender only on its endpoint charts in the isolated
window. The 120 original recipients B are owned. The verifier checks their
entire literal lifetimes. Their chart ranks are seven and, for nine summary
owners, zero. Neither sender endpoint can be cocharted with B, even if every
recipient contact barrier is waived and the fused MOVE may occur anywhere
in the sender's contact gap. Correcting XORs across a recipient observation
do not change this missing chart.

## Rebind the owned chart

Each owner has three incoming sends on the same middle chart. If all three
senders use their early endpoints, the new owner requires a common rational
rank-six subspace. Exact annihilator tests reject all 120 groups. If the
owner uses the common late chart, all three senders can supply full-rank
rows in the relaxed timing model. For 111 owners, the one original consumer
never occupies any rank-eight chart in its whole trajectory. Its unchanged
route therefore cannot consume the full-rank owner by a direct ADD.

The other nine owners descend to chart zero before their first read. Their
old descent has rank seven. A full-rank rebind changes its rank to eight.
Put p=1−κ. Three rank-one pairs replaced by three rank-two MOVEs save
`3(2−2^p) < 6κ`. By integration, the added descent cost
`8^p−7^p` is at least `p·8^(−κ) ≥ (1−κ)/8`. At the exact target κ the latter
bound exceeds `6κ`. All nine late rebinds lose before any additional costs.
This scope keeps the original one consumer or one descent per owner.

## Keep the owned chart and replace sender rows

For each owner, keep its rank-seven chart and its original first output
barrier, which is the sole outgoing rank-seven ADD or the summary descent.
Choose a nonempty subset of its three input senders to fuse. For each
chosen sender, remove its original transient rank-seven availability from
the first MOVE through the second. Leave other old rows intact. Grant free
XOR access to the union of every other literal row in the owner's chart
from INIT through the output barrier, including other valid appearances of
a chosen sender outside its removed interval. The owner itself starts zero.
Even with arbitrary copies, its additional row contribution must lie in
this granted span. The old unselected inputs are kept, so the extra target
is the XOR of exactly the chosen source rows.

Exact elimination excludes all 840 nonempty subsets, with zero unresolved
cases. All 840 controls pass when the removed source rows are restored to
the pool. The full receiver-window union deliberately overgrants simultaneous
availability and erasure. The conclusion does not cover altered producer
rows or alternative routes for the original public consumers.
