# P104 third target: a collector-rank obstruction and an attaining word

The natural incidence-separated extension of PR2445 from Y0/Y1 to **Y0/Y1/Y2**
needs **94 dirty helper lifetimes: 90 source acquisitions plus four collectors**.
An exact restored word attains that bound in the architecture stated below.
The four extra lifetimes arise because three groups have dependent coefficient
rows but must deliver at incomparable target endpoints. Merely counting the
90-source union misses this gate.

**This is not an unrestricted 94-lifetime minimum.** In fact the predecessor's
first-expansion escape argument fails at Y2 for twelve sources. The union size
90 is not claimed as an unrestricted lower bound. The unrestricted acquisition
question remains open; the Y0/Y1 predecessor's 78 lower bound is retained.
No complete 104-target supplier, favorable global moment or new kappa is claimed.

This answers the named third-target collector/chronology handoff in
[Ross Richardson's PR2445](https://github.com/CrocSwap/integer-mult-bounds/pull/2445),
head `6def43ad673b91dbd491389964d1dcd059bf2ac2`. Its two-target shear, source
acquisition argument, and dirty compensation idea are credited predecessors.
The new content is the three-target rank obstruction, its sharp restricted
construction, and the failure of the naively extended escape premise.

## Exact scope and lower bound

Let C = I-G/2 on the frozen ordered P104 roots. Partition its 90 nonzero source
columns for rows 0,1,2 by the nonempty target incidence set S. We consider this
precise **initial-line, incidence-separated collector architecture**:

1. Each group has one dedicated dirty acquisition helper per source s. At cut 0,
   it captures one nonzero scalar multiple of Xs at its initial line. It has no
   subsequent source read until final FULL-frame cleanup. Extra helpers are
   source-independent, arbitrary dirty inputs, never assumed clean.
2. Helpers belonging to different incidence groups do not mix. A group gathers
   through invertible rational ADD shears in J_S = intersection of its target
   endpoint frames. No allocation, erasure, fresh capture or source reread
   intervenes between this gather and delivery.
3. Each target in S receives its group's entire correction row from one
   designated collector, with a nonzero rational output factor. The collectors
   are simultaneously present after gathering and distinct. Each climbs to
   its target's endpoint and adds there; the frozen endpoints are distinct
   dimension-eight hyperplanes, so a monotone collector cannot visit two.
4. All new frames climb monotonically ZERO to FULL. At FULL, inverse gather
   shears and source cleanup restore every logical dirty input. Initial
   ZERO-frame target compensation is permitted. Original G/Q/D/private roles
   and target inputs are never read by the correction.

The restriction to one designated collector per group/target is part of the
theorem, not an asserted normal form for arbitrary relay programs. The verifier
binds the literal certificate's source reads, group mixing, common frames and
deliveries to this class. An independent endpoint replay checks actual correctness.

For one group, write n for its source count, q=|S|, k for its extra helpers,
and D for the invertible diagonal capture coefficients. Before gathering, the
source coefficient matrix of its helpers is [D;0], of size (n+k) by n. Gather
is invertible, and its q designated distinct collector rows, scaled by the
nonzero output factors, form a rank-q matrix R on the independent dirty inputs.
Their source matrix R[D;0] must equal C_S, of rank r. Restricting a row map to
a codimension-k subspace can lower rank by at most k. Thus **q <= r+k**, or
**k >= q-r**. Arbitrary initial dirty compensation cannot change source rank.

| Incidence S | Sources n | rank C_S | dim J_S | Extra floor q-r |
| --- | ---: | ---: | ---: | ---: |
| {0} | 16 | 1 | 8 | 0 |
| {1} | 16 | 1 | 8 | 0 |
| {2} | 12 | 1 | 8 | 0 |
| {0,1} | 10 | 2 | 7 | 0 |
| {0,2} | 14 | 1 | 7 | 1 |
| {1,2} | 14 | 1 | 7 | 1 |
| {0,1,2} | 8 | 1 | 6 | 2 |
| Total | **90** | | | **4** |

All entries are recomputed over the rationals from the pinned root fixture;
the common frames are computed as exact binary subspaces. In the rank-one
groups, all target rows are identical after the common capture normalization.
Gather their sum in one acquisition helper and shear it into q-1 extra dirty
helpers. This preserves invertibility: the new outputs include distinct extra
dirty coordinates. Those coordinates are compensated at cut 0. Group {0,1}
uses PR2445's determinant-one two-total shear on opposite coefficient ratios.
Every source line is contained in its group's common frame. These constructions
attain all seven lower bounds simultaneously, hence 94 in this stated class.

## Chronology and arbitrary dirty values

[CIRCUIT.json](CIRCUIT.json) inserts preparation at cut 0 and delivery/cleanup
at cut 4058, preserving every original event in order. Before the original word,
we subtract from each target the exact dirty row that its future collectors
will deliver. Capture and gathering then occur while original X initial lines
are available. Noncollectors climb to FULL; collectors wait in J_S. After the
original channel completes, each collector climbs to its target endpoint,
delivers, then climbs to FULL. Inverse gathering at FULL and subtraction of
captured X terms restore every new helper. The original channel never reads Y
inputs, so the initial dirty compensation propagates as the same target offset.

Two implementations replay the original channel and the literal insertions.
The exact endpoint is `Yt <- yt+xt` for t=0,1,2; the other 101 targets retain
`yt+(Gx)t/2`. All 104 sources, all 72 original dirty helpers and all 94 new
dirty helpers retain their logical inputs in their prescribed final frames.
The original eight owned private-copy lifetimes are inherited without change.

The third-target escape audit finds that the first expanded frame is still
inside H2 for sources **0,1,3,6,7,12,15,20,24,29,96,100**. These are exactly
the twelve sources exclusive to Y2. Their expanded dimensions range from 3
to 6. [RESULT.json](RESULT.json) retains the complete access witnesses. For
Y0/Y1 all 96 predecessor escape premises still check. Therefore the old proof
cannot simply establish a 90-source acquisition lower bound for all three.

## Complete finite local bill

| Quantity | This three-target word |
| --- | ---: |
| Added dirty helper lifetimes | 94 |
| Added scalar ADDs / original-source reads | 532 / 180 |
| Added nested transports | 287 |
| Added dimension-gap profile | 149 H1 + 37 H2 + 7 H3 + 8 H5 + 40 H6 + 46 H7 |
| Added ZERO-to-FULL rank mass | 846 = 94 times 9 |
| Full events / independent input columns | 4,877 / 374 |
| Full endpoint coefficients checked | 139,876 |
| Full profile | 1223 H1 + 95 H2 + 93 H3 + 104 H4 + 56 H5 + 64 H6 + 54 H7 + 8 H8 |
| Full rank mass | 3,214 |
| Maximum ideal logical row l1 / denominator | 106 / 4 |

Hr here denotes a nested abstract frame transport with dimension gap r. This
is **boundary progress, not a hosted recursive excess-cost invoice**. Telescoping
makes 846 sharp within the stated 94-lifetime ZERO-to-FULL class; ADD and
histogram optima are not claimed. Native phase/scalar-address compilation,
reverse supplier orientation, global owners, idle/residual children, physical
precision/tape, all-size admission and the remaining 101 corrections are unrun.
Logical l1 and denominator bounds are not a physical roundoff proof. The full
selected frontier replay is not relevant evidence for this partial word and
was not run. No supplier acceptance gate is claimed passed.

## Reproduce

Python 3.12, standard library. Default commands are read-only and need no Git
or network; source bytes are hash-pinned before arithmetic.

```sh
python3.12 -I -O -B research/p104-third-target-collector-rank/verify.py --regenerate
python3.12 -I -O -B research/p104-third-target-collector-rank/independent.py
python3.12 scripts/research_package.py --package research/p104-third-target-collector-rank
```

The primary interpreter uses sparse Fraction rows and enumerated subspaces.
The separately implemented audit uses dense dyadic integer rows and binary
echelon frames; it imports neither the builder nor primary verifier. Both compare
all endpoint coefficients, not sampled states. Ten primary mutation controls
and three independent mutations reject missing dirty compensation, capture,
fanout, delivery or restoration and incorrect frame/billing/access behavior.
Positive controls include the original 280-input channel, equivalent frame
bases and a one-extra-coordinate rank fixture. Regeneration compares the entire
parsed circuit. Hosted CI and independent human/proof-assistant review are not
claimed. Provenance and scope are in [SOURCES.json](SOURCES.json) and [TASK.json](TASK.json).

## Open next questions

Can the twelve Y2-exclusive sources use their later still-contained frames to
share acquisitions, or can cross-group mixing avoid the four collector extras?
First enumerate equal-frame chronological contacts for the listed twelve
sources and H2, then produce a literal restored word and complete local bill.
This changes the initial-line/separated premise; the 94 theorem does not block it.

Can this exact 94-helper word receive native phase-correct transport and scalar
lowering? First compile its 287 new transports against the pinned frame charts,
then check arbitrary input columns under the actual address maps. Neither the
old native channel nor a native proof of the different two-target word admits
these operations automatically. Global hosting remains a later obligation.

## Credit

Prepared for **ywz65**, with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. New material is Apache-2.0. Credit Ross
Richardson / PR2445 for the two-target sharing word and explicit third-target
handoff; commdata2338 / PR2393 for the one-target acquisition proof; Hiroki
Kumazaki / PR2353 and Philippe Van Velzen for the monotone relay model and
lifetime/cover distinction; Rohan Arun / PR1972 for the channel; Chafik
Boukhalfa / PR1991 for native realization; Adam Gall / PR1940, Josie Elliston /
PR1071, Ali Romman / PR1125 and the retained PR968/717/446/595/620 lineage.
Their frozen sources and notices remain unchanged. No literature-priority
guarantee or independent human review is claimed.
