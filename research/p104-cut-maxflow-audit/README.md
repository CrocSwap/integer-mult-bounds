# Independent max-flow audit of the P104 rank-eight cut family

The revision-4 `p104-side-correction` scope map ([#2133](https://github.com/CrocSwap/integer-mult-bounds/pull/2133))
concludes that the interleaved and terminal `I-G/2` routes are closed within
their premises. That conclusion rests on five author-checked cut packages,
none independently replayed: [#2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082),
[#2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090),
[#2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113),
[#2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127) and
[#2136](https://github.com/CrocSwap/integer-mult-bounds/pull/2136).
This package rechecks their shared **finite premises** with a separately
written implementation and a different method: max-flow/min-cut duality on a
time-expanded network, certified by an explicit feasible flow and an explicit
separating cut of the same size.

**Result: every checked premise is reproduced exactly; no discrepancy found.**
There is no new construction, supplier, κ or selected-frontier change.

## Input and independence

The only mathematical input is the PR1972 frame-model witness
`research/p104-native-channel/inputs/LOWRANK-WITNESS.json`
(SHA-256 `0f541bef…580e`, head `fd82d172`), which the checker authenticates
before use. No predecessor checker was read, imported or executed. The
authors' numbers were taken only from their PR descriptions at the heads listed
in `TASK.json`, and are compared after the computation. The shared trust root
is the witness itself. Its native Clifford realization is inherited from
#1991 and is not rechecked here.

## Model

Registers are the 280 persistent lifetimes (104 X, 104 Y, 32 G, 32 D, 8 Q)
plus the eight private `C` lifetimes. A frame is a GF(2) subspace of `F_2^9`,
canonicalized by its reduced echelon basis. Every event is legality-checked:
`add`/`copy` in one common chart, nested transports with the stated rank, and
private zero/erase lifetimes. Cut `c` is the state after events `0..c-1`.

**Frozen chronology (#2082/#2090 model).** The original transports and
lifetimes are kept. At every cut, each equal-frame class may mix
arbitrarily. Node `(r, layer)` carries one array (capacity 1). A hub per class
joins all members to all members of the next layer, which encodes complete
common-chart mixing exactly. Layers merge runs of cuts with an unchanged frame
state; mixing is also allowed after the final event. Any linear program in
this model is a sub-network, so its X→Y block factors through any vertex
cut, which gives `rank <= (min cut)·d`.

## Results

| Claim checked | Author value | This audit |
| --- | --- | --- |
| Events / cuts / distinct frames | 4058 / 4059 / 444 (#2090, #2113) | 4058 / 4059 / 444 |
| Frame-path intervals | 1698 (#2113) | 1698 |
| Ordered equal-frame pairs over all cuts | 106,254,468 (#2090) | 106,254,468 |
| Cross-register equal-frame interval pairs | 71,224 (#2113) | 71,224 |
| Transport profile, rank mass | `{1:1074,…,8:8}`, 2368 | identical, 2368 |
| Upward / downward transports | 1402 / 8 (#2136) | 1402 / 8 (all private rank-7 descents) |
| Frozen-chronology X→Y capacity | 8 arrays (#2082, #2090) | **max-flow = min vertex cut = 8** |
| Separator: Q0..Q7 at cut 2429 | separates; cones meet in Q (#2090) | separates; each query alone reopens; forward 104X+32G+8Q, backward 104Y+32D+8Q, meet = Q0..Q7 |
| Event after cut 2429 | first D transport (#2090) | `transport D0`, the first D transport |
| Union of all interleavings: 8 descents separate | 0 targets; each descent reopens 52 (#2113) | 0; each reopens 52; intact 104 |
| Collapsed frame graph without descents | 222 / 222 partition (#2127) | 222 source-reachable, 222 target-coreachable, disjoint, all 444 |
| Target hyperplanes distinct | yes (#2083 premise) | yes; 104 distinct source lines too |
| Replayed X→Y block `M` | `G/2`, rank 8 (#1991, #2090) | rank 8, symmetric, unit diagonal, `M² = 13M` |
| Residual | `(I-G/2)^(-1) = I-G/24` (#2082, #2090) | `(I-M)(I-M/12) = I` |
| Row support of `I-G/2` | 48 off-diagonal nonzeros (#2083) | 48 in every row |
| Minor on ports `[0,1,2,3,7,14,22,33]` | det 1/256 (#2090) | 1/256 |

**Extremal minimum cuts (new detail).** The residual-graph certificates give
the two extreme minimum vertex cuts of the frozen chronology:

- Source side: Q7, Q6, …, Q0 at cuts 1570, 1574, 1577, 1581, 1585, 1589,
  1592 and 1597 (Q0 through 2429).
- Target side: C#0, …, C#7 immediately after their rank-seven descents (cuts
  2464–2524).

So #2090's query cut and #2113's descent cut are both minimum. They bracket
every minimum cut of the frozen schedule. The eight flow paths each traverse
all 1427 layers. The exact rational replay also confirms that all X, G, D and
Q inputs are restored, that `Y = y + Mx` has no helper dependence, and that the
eight private discards each drop a nonzero value. That last point is the
inherited private-copy semantics, stated here for reviewers.

**Budget-line constants, now source-bound.** #2133 reproduced the moment
fractions from constants copied out of PR bodies. Here the constants come from
the witness: boundary coverage `2312` (initial/final frame dimensions),
private descent mass `56`, idle coverage `39096`. Under the inherited
conditional contract `s=N=9, m=73, W=832` the zero-saving moments are
`7551/7592` uncorrected, `7659/7592` with 96 added ranks, `1917/1898` with
104, and `7785/7592` with 208, and the per-call slack is `328/9`. The contract
itself is **not** verified here.

**Premise sensitivity (new observation).** Suppose nested charts (`A ⊂ B`),
not only equal charts, may mix at a single cut. At cut 2429 the max-flow
then rises from 8 to the full **104** (registered command). A local run gives
104 at cuts 1570, 2000 and 2470 as well. So the frozen schedule has no
combinatorial bottleneck beyond the equal-chart rule. The whole obstruction is
the price of cross-chart transfer, and a construction must change exactly that
premise or how it is credited.

**Controls.** Every control moves the answer in the stated direction:

- One added cross-frame contact gives 9.
- Nested-chart mixing at the #2090 cut gives at least 9 in the fast check (104 uncapped).
- Deleting one private lifetime gives 7.
- Max-flow engine fixtures match known path counts.
- `test_verify.py` rejects modified source bytes, a wrong transport rank, an add outside its common chart, a non-nested transport, a scalar-coefficient corruption (frames legal, attainment fails), a corrupted receipt and an overwrite attempt. An equivalent frame-basis presentation reproduces the identical receipt.

## Scope and what is not established

- The step from "rank `<= (8 + k)d` with `k` added cross-frame transports" to
  "at least 96 added transports" (#2082, #2127) is the authors' written
  argument. Its finite premise, the cut and partition, is checked here. The
  reduction from arbitrary added-storage/retiming programs to that count is
  not machine-checked.
- #2136's nested-refinement model is not recomputed; only its interval counts
  are reproduced. The later #2148 (`B >= 48`) builds on that separator and is
  likewise not covered. #2083's terminal 104/208 floor is a different, written
  argument; only its distinct-hyperplane and row-support premises are checked.
- The coverage contract, native Clifford/phase recipes, global hosting,
  precision, all-size lifting and the selected cold replay are untouched.
  This is a finite audit of one pinned witness, not a universal P104 barrier.

## Reproduce

Standard-library Python 3.10+ (registered: 3.12). About 30 s, 50 s and 3 min respectively:

```sh
python3 -I -B research/p104-cut-maxflow-audit/verify.py
python3 -I -B research/p104-cut-maxflow-audit/verify.py --premise-sensitivity 2429
python3 -I -B research/p104-cut-maxflow-audit/test_verify.py
python3 scripts/research_package.py --package research/p104-cut-maxflow-audit
```

Expected first line:
`PASS_P104_CUT_MAXFLOW_AUDIT max_flow=8 rank=8 frames=444 union_reopen=[52] partition=222/222`.
The verifier compares its complete canonical receipt with `RESULT.json`.
`--write PATH` writes a fresh receipt to a new file and never overwrites.

## Open next questions

1. **What is the cheapest legal single-cut exchange that the nested
   relaxation exposes?** At cut 2429, nested-chart mixing admits a full
   104-array matching.
   - *Why it matters:* pricing each nested exchange by its transport rank
     (with dirty restoration) gives a sharp single-cut correction bill. That
     bill is the number a changed coverage interface (#2133 route 2) would
     have to credit.
   - *First step:* a min-cost-flow over the layer-701 nested-frame graph with
     arc costs `|dim A - dim B|` for out-and-back excursions.
   - *Blocked by:* under the retained contract the 96-transport floor already
     exceeds the `328/9` slack. The question only matters with a changed
     coverage law.
2. **Can the "+1 array per added transport" reduction be machine-checked?**
   - *Why it matters:* this is the remaining unchecked step behind the
     96-transport floors.
   - *First step:* state the added-storage/retiming program class precisely
     and prove that each added cross-frame transport raises the
     collapsed-frame-graph edge cut by at most one.
   - *Blocked by:* a formal program model shared by #2082 and #2127.
3. **What is the exact capacity in #2136's nested-refinement model?** Only
   the upper bound 56 is claimed.
   - *First step:* extend the union graph with every intermediate frame of
     each transport interval and compute the max edge-flow.
   - *Blocked by:* the size of the subspace-lattice intervals, and agreeing
     on the capacity semantics of refined chains.

## Credit

The audited results belong to David Arias (#2082), Adam Gall (#2090, #2083,
#1940), Jeremy Diviney (#2113), Ross Richardson (#2127), Tairitsu-Aya (#2136)
and Aaron Wang/navinor (#2133). The channel is due to Rohan Arun (#1972) and
its native realization to Chafik Boukhalfa (#1991). The geometry and coverage
lineage is credited in those packages. Prepared for Michael Yee with
substantial Claude (Anthropic) assistance in method design, implementation,
verification and prose. There has been no independent human review.
Apache-2.0.
