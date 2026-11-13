# Fixed-cut ingress and whole-bank collision

In the normalized chart model, a typed MOVE leaves the normalized coordinate fixed. ADD and SCALE act linearly on coframed rows. The pinned frame spans for charts 3, 1051 and 127 are strictly nested, with rank differences 5 and 4. Helper 1310 begins at chart 3 and ends at chart 127.

Before the tested cut, the only events incident to old helper 1310 are ADD35424, ADD35425 and MOVE38217. The first two add historical donor rows from 890 and 943. Write their sum as g. At the cut just before ADD38219, old role 1310 has coordinate x1310+g, and none of the 11 other chart-1051 rows has seen x1310. This includes role 1311, delivered by the already-paid MOVE38218. Exposing the independent old output and substituting a new independent input y for the suffix requires returning x1310 while supplying y+g to the original continuation.

The reverse solve computes the 11 coframed rows and g exactly, finds bank rank 11, and separates g with x890=1 and every other old input zero. The donor responses are (1,0), so g=1. Independent forward replay verifies all bank responses and the first outward ADD38220 into role 1312.

For the stronger collision, also set x1310=−1. The independent replay confirms that the historical donor responses and all 11 other rows remain fixed. The old 1310 row becomes zero. Set y=0 as well. Then the local inputs for this repair are identical to those on the all-zero input, although the required exposed old value is −1 instead of zero. No deterministic correction using only those local inputs can return the required old value, even if granted arbitrary use of the old 1310 row. The claim fixes the cut, old prefix, caller and independently chosen fresh input. It leaves a changed source encoding, earlier recovery, or other transport or boundary open.

## Directed price

The hypothetical paid-neutral split would change productive counts by +17 rank-four, +17 rank-five and −17 rank-nine across the 17 signed calls. The exact price is the directed interval for 17 × (4^κ + 5^κ − 9^κ) at the pinned #7481 crossing. The rational bounds are in `receipts/LEAD.json`. Even the upper endpoint is below 0.38075659829390936 raw. A new paid rank-one child per call costs 17 raw. The tested route failed the necessary ingress gate, so no physical lowering, signed adjoint, complete ownership or restoration, or compiler, precision and tape invoice was advanced.
