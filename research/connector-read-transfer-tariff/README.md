# Exact connector tariff when reads and transfers trade off

**All-length query-model theorem and exact attaining words; no new kappa.**
For one fixed three-source/two-root interface, minimizing the number of
target reads first can miss the cheapest fully priced call word. The exact
frontier is:

| Root transfers U,V | Reads of each proper nonzero mask | Reads of full mask7 | Total reads |
|---|---:|---:|---:|
| 2,2 | 2 | 4 | 16 |
| 3,3 | 2 | 3 | 15 |
| 4,2 | 2 | 3 | 15 |

All six source calls are retained in every word. At unit complete-call prices,
the first word costs **26**, versus **27** for the best minimum-read word.
With unequal positive transfer prices u,v and full-mask read price a7, the
extra-read word wins exactly when `a7 < min(u+v,2u)`. This is an exact price
region, not a claim of a measured physical speedup.

[PR2538](https://github.com/CrocSwap/integer-mult-bounds/pull/2538) optimizes
root transfers across all **minimum-read** decompositions at fixed source
word/colors; it explicitly excludes read/transfer tradeoffs and unequal
shear prices. That result remains correct. This contribution solves the
positive-tariff question for the specified interface over arbitrary read
and transfer multiplicities. It includes an all-length hand proof and a
complete count-Pareto state search. It is not a new instance of the same
lexicographic objective or a claim that PR2538's solver is wrong.

## Fixed interface and theorem

Sources x0,x1,x2, two roots z0,z1, and seven output rows y_m are arbitrary
dirty rows over F2. Source maps B_j and reader maps A_m may be singular and
noncommuting. All children use physical z0, restore their own disjoint scratch
and heads, and preserve other data rows. Output targets are not observed
until the end. The endpoint is

```
y_m += A_m(sum_(j in m) B_j x_j), for m=1,...,7;
all sources and both roots unchanged.
```

The optimum is over formal words that implement this endpoint for **every**
compatible choice of the maps, treating the children as opaque. It is not a
map-specific optimum: for example, known zero reader maps could remove reads.

The source word is **B0 B0 B1 B1 B2 B2**, with normalized colors
`v0=v1=(1,0)`, `v2=(0,1)`. At source event j the current root frame must
satisfy `G v_j=(1,0)`, the same fixed-color legality rule as PR2538. Paid
root transfers are U: z0+=z1 and V: z1+=z0. There are no extra roots, clean
resets, source mutations, output mixing, combined child calls, or changed
source order. Root frames start and finish at identity.

For positive complete child prices b_j,a_m and independent positive shear
prices u,v, the exact optimum is

```
2 sum_j b_j + 2 sum_(m=1)^7 a_m
  + min(2u+2v+2a7, 3u+3v+a7, 4u+2v+a7).
```

[PROOF.md](PROOF.md) proves the lower bound for every finite legal word.
The key point is that each normalized source interval has only one live
source label. Three reads of mask7 must therefore occur at the three
different source intervals with all three distinct nonzero dirt functionals.
Their chronology forces at least three U transfers; source legality and
restoration force at least two of each orientation, and GL2(F2) parity gives
the two three-read cases. Four or more reads are bounded by the first case.
No transfer-depth cutoff or finite-search extrapolation is used in this proof.

The three full words in `RESULT.json` attain the lower envelopes and restore
every arbitrary dirty row. The formal coefficient argument is valid for
arbitrary compatible F2-linear maps and data length, not only scalar inputs.

## Complete finite corroboration

The primary search in `synthesis.py` uses the credited PR2538 state
`(source cut, physical frame, available read vectors)`. It retains all
componentwise minimal `(U,V)` labels at each state instead of stopping at a
minimum-read terminal. Source advances have zero additional cost since their
six complete prices are fixed. Transfers add their own coordinate. Terminal
read vectors are chosen by shortest XOR paths separately for every target;
the target's fixed positive price makes minimum count optimal at that terminal.
All targets are unread and independent, so each chosen read can be placed at
its first exposed occurrence without competing for capacity or changing roots.

A dominated label at the identical state cannot improve any continuation.
The state graph is finite; removing a repeated-state cycle weakly lowers both
cost coordinates. Thus a minimal label has a simple representative, and the
complete label search terminates. The implementation raises on 20,000 states
and emits no optimum after truncation. This instance uses **830 states and
1,145 nondominated cost labels**. Every terminal invoice is Pareto-filtered;
all three resulting words are emitted and replayed.

`oracle.py` is separate code: it evolves the two physical formal rows directly,
enumerates every word state in the rectangle U<=4,V<=3, and uses exhaustive
read-vector subsets instead of XOR BFS. Its entire canonical minimal-state
rectangle agrees with the primary engine, including unavailable terminal
cases. This finite rectangle corroborates the three attainers and hand proof;
the all-length claim does not come from treating that rectangle as exhaustive
of longer words. The primary full-state and independent rectangle digests are
recomputed, not trusted in lieu of the states.

Further checks execute **1,728 full dirty basis columns forward and inverse**
across widths1,2,3 and eight deterministic map fixtures per width/word.
They include singular and noncommuting maps. Source and target order are
explicit. Five effective controls reject missing reads/sources/final transfers,
resource-cap truncation and the false claim that minimum reads minimize price.
Twenty-seven exact rational price cases include unequal orientations and tie
boundaries. The untouched PR2538 solver is authenticated before import and
reproduces its applicable 15-read/6-transfer baseline on this new input.

## Reproduce

Python3.12 or later, standard library only, from the repository root:

```sh
python3 -I -O -B research/connector-read-transfer-tariff/verify.py
python3 -I -B research/connector-read-transfer-tariff/check_integrity.py
python3 -I -B scripts/research_package.py --package research/connector-read-transfer-tariff
```

Expected primary marker:
`PASS_CONNECTOR_READ_TRANSFER_TARIFF front=3 states=830 dense=1728`.
Default replay is read-only. `--write NEW_PATH` creates a receipt exclusively.
The integrity command tests a Git-free relocation, changed executable source
rejection before execution, typed receipt corruption, and occupied output.

## Prices, provenance and limits

Complete prices include each call's actual access, row passes, frames, private
scratch return, heads and dispatch. Admission/root stock, preparation, emission,
precision, parking and hosting costs outside those calls must also be added.
The exact formula assumes such extra terms are common or separately charged;
a word-dependent overhead can reverse the one-call unit-price improvement.
No selected supplier exposing this abstract interface is established here.
There is no recursive rank profile, contracting moment, runtime measurement,
formal-kernel theorem, general source-order/color optimum or new kappa.

Main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority4, was freshly fetched.
The prescribed 945-pairing connector control and selected binding check passed.
Picker seed `ea16ef89596ce9a1ec58478afdb9cac5` selected connector-alphabet-change.
`TASK.json` explicitly records the changed scope: same fixed alphabet, changed
price objective, with an all-price frontier rather than a new unpaid operation.

`SOURCES.json` pins main context. `VENDOR.json` pins PR2538's unmodified README
and synthesis code at `4f854bec19601ea0ed6fb07f17b441e5f0011c84`; they retain
their attribution. PR2538 (ywz65 with Codex) receives credit for joint read-set
synthesis and its lexicographic solver; conorholds/PR2208 for fixed-color root
frames and the read-decomposition handoff; Ross Richardson/PR943/934 and the
retained commutator lineage for the generic dirty connector model. The existing
one-root weighted source/read tradeoffs use a different alphabet and price
question. No priority for Pareto search, XOR-distance BFS or dirty cancellation
is claimed. Live overlap coverage and its limitations are recorded in TASK.

Prepared under ywz65 with substantial OpenAI Codex assistance in proof, code,
checks and prose, and separate AI peer review. No independent human review or
hosted-CI pass is claimed. New work Apache-2.0; predecessor notices retained.

## Open next questions

1. Which actual caller has fixed source colors/order and complete tariffs in
   the extra-read region? First bind its roots, child ports, row length and
   all overhead differences. None is supplied by this abstract example.
2. Can a source-bound larger walk have a useful read/transfer frontier?
   First derive a lower proof or complete state certificate for its exact
   word; do not extrapolate the present 830-state search or presume free
   schedule generation. Resource and physical-overhead limits remain open.

Structured questions, blockers and source/overlap details are in TASK.json.
