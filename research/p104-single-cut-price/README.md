# Exact price of the P104 nested-contact relaxation at cut 2429

The single-cut communication relaxation costs **864 added rank units** to
support 104 independent source-to-target flows. More precisely, for integer
`0 <= F <= 104`, its minimum dimension-gap price is

\[
C(F)=9\max(0,F-8).
\]

This answers the minimum-cost-flow first step in Michael Yee's
[Discussion #2164](https://github.com/CrocSwap/integer-mult-bounds/discussions/2164)
and [PR #2163](https://github.com/CrocSwap/integer-mult-bounds/pull/2163), head
`9f6e1f2783aef0c52bb3f26f587a918a8be32fa9`.
That predecessor supplied the temporal graph and showed that **free** nested
contacts at this cut raise its capacity from 8 to 104. The new result prices
those contacts exactly, with a feasible flow and a dual certificate.

**This is a finite graph optimum and scoped proof, not a correction circuit.**
Prices are one-way dimension gaps per transmitted array. Dirty restoration,
scalar coefficients realizing the identity, native phases, hosting and a
complete supplier bill are not supplied. No new supplier or kappa is claimed.
The result is author-checked, without independent human or formal-kernel review.

## Frozen object and exact model

The only mathematical input is the immutable
[PR1972 witness](../p104-native-channel/inputs/LOWRANK-WITNESS.json), authored by
Rohan Arun at `fd82d172f46933fd253c2c6de4bd5eaff5429cfd`, SHA-256
`0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`.
Its retained native realization is Chafik Boukhalfa's PR1991,
`6e222517e182e98499239bc9a4009f540e1c5520`.
The scientific base is main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
Exact contextual predecessor heads and task selection are in [TASK.json](TASK.json).

Use PR2163's per-register temporal network:

1. Preserve all original frame transports and private lifetimes. Replace the
   prescribed scalar additions by arbitrary common-frame communication at every
   cut. Each live register between consecutive structural layers carries at
   most one array. Initially only the 104 X inputs supply flow; finally only
   the 104 Y outputs consume it.
2. Cut `c` is after instructions `0,...,c-1`. Cut **2429**, predecessor layer
   701, is immediately before the first `transport D0` instruction. Here the
   live frames comprise 136 FULL registers (104 X and 32 G), 136 zero-frame
   registers (104 Y and 32 D), and eight distinct rank-eight Q frames.
3. At this cut only, add directed arcs both ways between every **strictly
   nested pair of live frame classes**. Charge each unit of flow on such an
   arc `abs(dim A - dim B)`. Their capacities are 104, which is sufficient
   for any source-to-target flow under consideration. All original arcs cost
   zero: their existing invoice is paid separately.
4. As in PR2163's `nested_layers` relaxation, frame hubs have unlimited transit
   capacity at the added-contact cut. The original incoming/outgoing register
   capacities remain. Chaining paid contacts through a hub is allowed. No new
   intermediate frame classes or contacts at other cuts are added.

There are 10 live classes and 34 directed paid arcs: FULL/zero, FULL/every Q,
zero/every Q. Distinct rank-eight Q frames are not nested. An arc is a priced
information-flow relaxation; it is **not** asserted to be a legal restored ADD.
In particular, neither the graph upper bound nor the numeral 864 is an upper
bound on the cost of implementing `I-G/2`.

## Certificate and proof

[model.py](model.py) compresses the unchanged frame-class chains into **2,604
nodes and 3,810 arcs**. It reconstructs subspaces by explicitly enumerating
all vectors in their spans. A frame-class epoch ends whenever a register
enters, leaves, is born or is discarded. A transport from class A to B has
one capacity-one A-to-B arc, a capacity `|A|-1` A carry arc and a capacity
`|B|` B carry arc. Private initialization has no source edge.

This compression preserves the flow problem. At each cut arbitrary
common-frame mixing allows any pairing of the incoming and outgoing occupied
registers in a class. Thus integral class flows can be assigned to the actual
register slots. A class unchanged between membership events has only a carry
chain of constant capacity, which can be contracted. If its epoch contains the
paid-contact cut, its incoming and outgoing original flows each remain bounded
by its register count, while the hub itself admits transit just as in the
uncompressed model. The verifier checks both occupancy bounds. Conversely,
summing the per-register flows gives a feasible compressed flow with identical
paid cost.

[CERTIFICATE.json](CERTIFICATE.json) supplies integral flows and integer node
potentials. The acceptance checker [verify.py](verify.py) **does not import or
run the optimizer**. It verifies every capacity, conservation equation and
residual reduced-cost inequality. For an arc `e=(u,v)` of capacity `b_e` and
cost `c_e`, put `r_e=c_e+p_u-p_v`. Any flow of value F satisfies

\[
\sum_e c_e x_e
=F(p_t-p_s)+\sum_e r_e x_e
\ge F(p_t-p_s)-\sum_e b_e\max(0,-r_e).
\]

The supplied potential has terminal gap **9** and total capacity penalty
**72**, proving `cost >= 9F-72`. Nonnegative costs also give `cost >= 0`.
The feasible 104-flow decomposes into **eight zero-price paths and 96 paths
of price nine**. Its only used paid arc carries 96 units from FULL to zero.
Taking subsets of these paths attains the lower bound for every integer F.
This proves the whole claimed cost curve, including `C(104)=864`.

A second checker reconstructs all **1,427 structural layers and 399,680 unit
register edges**, including the final 104 output edges. It uses Gaussian
elimination rather than span enumeration and never reads the compressed edge
list. It lifts the potentials to the full per-register graph: each entry takes
its preceding frame-hub potential and each exit its current hub potential.
The hub/entry/exit arcs then have zero reduced cost. Source, sink and all 34
paid arcs are checked explicitly. The only negative unit edges are:

| Register | First cut / penalty | Later cut / penalty |
| --- | --- | --- |
| Q0 | 1597 / 1 | 2462 / 8 |
| Q1 | 1592 / 1 | 2471 / 8 |
| Q2 | 1589 / 1 | 2478 / 8 |
| Q3 | 1585 / 1 | 2486 / 8 |
| Q4 | 1581 / 1 | 2494 / 8 |
| Q5 | 1577 / 1 | 2502 / 8 |
| Q6 | 1574 / 1 | 2509 / 8 |
| Q7 | 1570 / 1 | 2517 / 8 |

Their capacity-weighted penalty is `8*1+8*8=72`. This independently checks
the lower bound on the predecessor's uncompressed network; it is not a second
optimization run or independent human review.

## Conditional budget implication

The source-bound recount gives original local rank mass 2368 and boundary
coverage 2312. **Only under the inherited, unchanged-obligation coverage
contract** `N=9, m=73, W=832`, with no new productive-progress credit, the idle
mass is `72*832-9*2312=39096`, and the available extra rank is `328/9` per call.
The already optimistic one-way price 864 fails this screen:

\[
M(0)\ge\frac{9(2368+864)+39096}{73\cdot832}
=\frac{8523}{7592}>1.
\]

The verifier checks this rational arithmetic, not the coverage contract.
Bringing this expression merely to equality would require `7448/9` additional
units of valid rank credit per call; strict success needs more. Paid rank is
not automatically excess cost when a construction changes coverage, endpoints
or owner obligations. This comparison therefore does not exclude those changes.
There is no reason to synthesize this fixed-cut route under the unchanged bill.

## Reproduction and controls

Standard-library Python 3.12; all acceptance commands are read-only:

```sh
python3 -I -B research/p104-single-cut-price/verify.py
python3 -I -B scripts/research_package.py --package research/p104-single-cut-price
```

Expected verifier output:

```text
PASS_P104_SINGLE_CUT_PRICE cut=2429 flow=104 cost=864 baseline=8 dual=9*flow-72 frontier=0..104 no_new_kappa
```

The registered replay runs the verifier and seven test groups, normally and
with `-O`. Fifteen rejection cases cover capacity, conservation, cost, Boolean
substitution, invalid duals, underpriced contact, the expanded paid-arc guard,
nonmaximal baseline, moved cut, transport rank, nonnested transport, illegal
ADD frame, source bytes, intermediate price receipt and overwrite protection.
Positive controls include equivalent redundant frame bases and a small residual
rerouting instance where greedy path selection would give the wrong price.

For an optional fresh optimization, choose a nonexistent output path:

```sh
python3 -I -B research/p104-single-cut-price/solve.py --write p104-price-new.json
python3 -I -B research/p104-single-cut-price/verify.py --certificate p104-price-new.json
```

The optimizer refuses overwrites. Acceptance does not depend on identical
optimizer choices: a different valid optimal primal/dual witness is allowed.
Source pins and the graph model remain fixed. Use `verify.py --json` to inspect
the expanded dual and conditional budget receipt.

## Scope and overlap

PR2082/2090 establish the frozen temporal cut, PR2113 allows retiming, PR2127
allows added storage, and PR2136/2148 study retained-path subdivision. Those
are different domains; this result does not replace their bounds. PR2163's
free nested-contact observation is credited rather than repeated as novel.
Its second handoff, formalizing the one-array-per-transport implication, is
separate from this exact fixed-graph price. No other cut is priced here.

Not checked: a scalar identity or arbitrary-dirty restoration for the new
contacts; native Clifford/phase realization of a correction; actual owners,
COPY lifetimes, precision, tape, all-size lifting, complete cold replay, or a
formal translation of every physical program into this graph. Full flow only
certifies communication capacity, not prescribed source-to-target coefficients.
The old witness's scalar `G/2` endpoint is inherited, not replayed in this package.

## Open next questions

Also structured in TASK.json:

- Can one actual changed P104 trajectory earn enough *proved* productive
  progress credit to pass a complete moment? This matters because the present
  fixed-cut price exceeds the retained slack. First specify the changed owner
  and idle obligations and test a fully charged optimistic budget. A valid
  coverage identity and dirty-restored schedule remain the blockers.
- Multiple paid cuts change this theorem's hypothesis. Such a search should
  begin only with an explicit revised coverage contract or other source of
  headroom: the earlier general 96-transport floor already fails the unchanged
  budget. State the cut set and capacity semantics before another optimization;
  free reachability alone would not establish a supplier.

## Credit

Temporal-network model, free-contact sensitivity and handoff: Michael Yee
(PR2163), with the assistance credited in that package. Channel and native
realization: Rohan Arun (PR1972), Chafik Boukhalfa (PR1991). Cut/budget lineage:
David Arias, Adam Gall, Jeremy Diviney, Ross Richardson, Tairitsu-Aya,
Nick Petalas and Aaron Wang/navinor, with their geometry/coverage predecessors
retained. Their sources were consulted; no pending checker is imported as an
acceptance oracle. The new code and price proof are supplied here.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0.
