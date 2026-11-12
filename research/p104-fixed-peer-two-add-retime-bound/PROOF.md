# Fixed-peer signed two-ADD chronology

The exact predecessor contact receipt freezes four public mover
paths A→B→C. Each path has only two contacts between its paid
MOVEs, at the next two literal clocks after the first MOVE.
The same fixed public peer participates in both ADDs and each
ADD writes a different operand. In mover/peer order, the
first two windows have normalized matrix
`[[1,−1],[1/2,1/2]]` and the last two have
`[[1/2,−1/2],[1,1]]`. Both exact determinants are one.

| Mover | Paid MOVE clocks | A, B, C | Peer | Inclusive candidate cuts |
|---:|---|---|---:|---|
| 1305 | 41321, 44605 | 856, 983, 207 | 1488 | 41324–44605 |
| 1303 | 43854, 44615 | 854, 984, 207 | 1302 | 43857–44615 |
| 654 | 44564, 44617 | 856, 983, 207 | 1449 | 44567–44617 |
| 652 | 44585, 44619 | 854, 984, 207 | 1450 | 44588–44619 |

A cut c is the state after exactly c original events, before event
c when it exists. The old signed pair ends immediately before
the first cut. Placing the direct A→C MOVE at the old second
MOVE puts the mover on A for the retimed pair. The unchanged
peer is already on B at the old pair. Its public moves strictly
ascend, so it cannot meet the mover at A after the pair. This
excludes all 4,124 low-endpoint typed cuts.

Placing the direct MOVE at the old first clock puts the mover
on C for the retimed pair. The public peer must occupy that
exact chart and the corridor must be clear of all scalar and
lifetime contacts of either operand. Both source and destination
contacts of ADD and COPY count. A MOVE into a chart at clock t
first changes the chart at pre-event cut t+1. An ADD at t first
counts as a crossed event at cut t+1. This convention includes
the old second MOVE clock itself as a cut. All other paths and
the original signed ADD order stay fixed.

The forward walk classifies each late cut. The independent
reverse walk reconstructs exact chart and contact intervals.
Both agree on all four windows, every peer chart and relevant
MOVE, and the first blocking contact. None of the 4,124 late
cuts has the peer in C. Of these, 2,364 have clean scalar
corridors and 1,760 cross a scalar contact. The first three
windows first cross an ADD at 43649, 43859 and 44569 respectively.
The last window has 32 clean cuts, all in the wrong chart. Since
even a clear corridor cannot supply the required peer chart,
no exact signed prototype was necessary.

The same four keys are present in
[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
at exact head `349996445176e934ffb3c76813adcd230ca8f783`. Its
R69 geometry labels each `missing_low_or_high_stock` under
the maximal-component virtual-owned fusion guard. The
[published manifest](https://github.com/CrocSwap/integer-mult-bounds/blob/349996445176e934ffb3c76813adcd230ca8f783/research/p104-compensated-fusion-readout-bound/receipts/SHA256.json)
pins that geometry. This replay supplies the separate exact
high-endpoint obstruction for the specified public peers.

## Complete signed price

Each possible contraction replaces two rank-one paid calls by
one rank-two call. Across all 17 signed caller copies this
would change the paid histogram by {1:−34, 2:+17}. Paid
positions would change from 110,519 to 110,502 for one
edit or to 110,451 for four. Productive positions stay at
22,461 and signed rank surplus at 1,424. The priced resource
cap counts the eight distinct paid clocks and eight distinct
public operands only once. The compatible relaxation gives
about 0.08583213854035211 raw per edit and 0.34332855416140845
for four at the incumbent crossing upper. The complete fixed
target margin upper is about −139.38966768429373 at
κ = 0.0040075385047236. One added raw rank-one paid position
would exceed the entire optimistic credit.

The proof retains the native all-column, owned-erasure, compiler,
precision/tape and analytic recovery premises. Changed peer
itineraries, different windows and alternative scalar transports
remain outside the test. No new supplier, full changed-caller
replay or κ claim is asserted.
