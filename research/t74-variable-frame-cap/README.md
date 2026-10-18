# Variable-frame cap for the PR2322 T74 words

**Exact scoped cost bound; no new κ.** The two borrowed words of
[PR2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322) cannot reach
primitive **b = 0.0016972**, even after jointly optimizing all their A, B,
restoration and rank-zero handoff frames and allowing arbitrary fractional
whole-helper packing into the unchanged T74 bin stock. Both source words are
identical as parsed JSON to those in
[PR2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374), head
`5449da65da12bdfd94675dccc38731eaa91e93b6`, whose conditional κ claim is
0.001697194950901770. That comparison was checked locally; this package does
not independently admit PR2374's complete supplier or outer theorem.

This narrows one constructive question: **can a frame refit, including moving
the handoff charts, improve this fixed scalar/operator word substantially?**
The bound leaves less than 5.05e-9 above PR2374's primitive endpoint. It permits
repacking, so changing only its owner assignment does not escape the result.
Changing scalar gates, their order, logical handoff maps, helper endpoints or
the parent inventory remains outside the theorem.

The concurrent [PR2402](https://github.com/CrocSwap/integer-mult-bounds/pull/2402)
by Sagar Thakrar, head `2e2cb4ffa2785e40f6e3443fec8765e4dade7cff`, gives the tighter
**b < 0.001697195759** packing cap when the local frames are fixed, and prices
hypothetical circuit moves. The new question answered here is whether changing
all permitted intermediate and transported handoff frames escapes that narrow
packing regime. This package's broader but slightly looser cap covers those
frame changes. PR2402 was read for overlap; its certificate is not replayed or
used in this proof. Earlier #1995/#2013 frame bounds concern the selected older
scalar word and cleanup contract; they do not bind these changed borrowed words.

The computational contribution is a small exact min-sum elimination engine.
It resolves the complete finite frame-assignment relaxation in about one second
for both providers together on the author's machine. General CP-SAT searches
had left a lower-bound gap after minutes; those unsuccessful searches are not
used as proof. No claim of a new variable-elimination algorithm is made.

## Fixed inputs and permitted changes

`INPUTS.json` pins the two PR2322 words, the PR2269 T74 parent plan and the
inherited directed power engine. Prefix/precondition/compensation frames, cut
producer frames, target levels and all initial/final frames remain fixed.
The scalar A/B/restoration gate sequence, operands and coefficients remain fixed.
Every handoff keeps its role, chronological position and invertible binary map
G; its entry and exit subspaces may change jointly subject to **E = G(U)**.
The initial target response and exact scalar operators are not resynthesized.

Every variable frame can be *any* binary subspace of GF(2)^9 satisfying the
literal monotonicity and transported-equality constraints. Domains are not
restricted to frames occurring in the input. A physically valid native refit
must satisfy these conditions; this proof may admit more possibilities, so it
needs no claim that every allowed assignment has a native implementation.

Each source word has local profile
`{1:2335, 2:512, 3:426, 4:120, 5:38, 8:8}`, including COPY64, and local rank
mass 5371. Both have 434 helper widths
`{4:33, 5:9, 7:38, 8:114, 9:240}`, total 3515. The parent has 666 calls,
m = 73, W = 66304 and bins
`{8:49728, 16:33152, 32:33152, 48:33152}`. These counts are recounted from the
pinned words and plan. The cap permits any mixture of the two providers.

## Why the finite frame computation is complete

A node represents a scalar gate's common frame. Each role contributes an edge
from its previous frame to the gate's frame. Initial/final/cut nodes are fixed.
A handoff has two nodes with E = G(U), rather than a paid edge between them.
Ordinary edges require inclusion and charge the rank difference. Parallel edges
are retained with their multiplicity: two shared roles pay twice.

For a variable node, propagate a lower subspace forward by span/join of incoming
bounds and an upper subspace backward by intersection of outgoing bounds.
Across a handoff use G forward and G^-1 backward. Induction in the chronological
DAG proves every feasible frame lies in its resulting interval [L,U].
`domains.py` enumerates every subspace between them by generating all subspaces
of the quotient U/L. It checks the full GF(2)^3 lattice as a control; there are
1, 7, 7 and 1 subspaces in the respective dimensions.

A lossless reduction simplifies the graph before enumeration. Let a free node
have equal incoming and outgoing multiplicity, and a single distinct predecessor
with frame P. Assign that node the frame P. It remains below every successor Q.
For each continued role, its two increments x and y become x+y. For
0 < p = 1-b < 1,

    c_x + c_y >= c_(x+y),   c_r = (r/73)^p, c_0 = 0.

Thus the change cannot increase true cost. The analogous assignment to a single
distinct successor is also valid. Fixed anchors and transport nodes are never
contracted. Repeating this operation preserves an optimum of the true objective;
it removes 1434 nodes for each provider. The final assignment is reconstructed
and checked against every edge and transport in the original graph.

After bounds and contractions, each provider has 1118 variable nodes in 25
components. Factor tables record every legal adjacent frame pair, its paid
cost, and every transport equality. Variable elimination sums all factors
containing one node and minimizes over *all* its possible frames, retaining the
result on its neighbors. Induction proves that this is exact minimization over
the eliminated variables. The largest table contains 1,953,125 entries; no
branch-and-bound solver or heuristic stopping criterion is involved.

`eliminate.py` uses NumPy int64 arrays for these exact integer operations.
Invalid entries have saturated infinity 2^60; every addition is capped at that
value, and two such entries sum below int64's limit. A feasible complete cost is
checked to lie below infinity. A separate exhaustive 81-assignment cyclic
factor problem verifies elimination and reconstruction. A split-climb positive
control exercises an actual improving graph contraction; fixed anchors and
unbalanced incidences are preserved.

## Directed prices and the cap

Set b = 4243/2500000 = 0.0016972. Define

    f_b(r) = [73 (r/73)^(1-b) - r]/b,   f_b(0) = 0.

The immutable directed moment engine from PR2322 computes rational lower
bounds for every f_b(r), with explicit logarithm and exponential tail bounds.
Its runtime grid is 2^-256, with 100 logarithm and 96 exponential terms.
Each local table uses the **floor** of 2^40 times that lower bound. The
min-sum engine therefore proves a lower bound for the local excess, using
only integer operations. No floating-point result enters a proof comparison.
The floats printed on success are diagnostics only.

Contraction is justified for the true concave costs, **not** for their rounded
versions: every original feasible assignment has a no-more-expensive contracted
assignment, whose true cost is at least the minimum rounded-down cost computed
on the contracted graph. This distinction avoids assuming that rounding
preserves subadditivity.

The rounded optimum equals the source profile's rounded cost for each word.
This is not a claim of exact real-valued optimality: a gain below the rounding
resolution is left open. The cap below incorporates all downward rounding.
Rank mass remains exactly 5371 for every assignment because edge differences
telescope and transports preserve dimension; the eight fixed rank-eight cut
copies are separately included.

Whole-helper packing uses the established PR1129/PR2360 relaxation. All 1163
integer patterns for capacities 8,16,32,48 and widths 4,5,7,8,9 are enumerated.
The rational dual in `DUAL.json` is checked against directed lower costs, giving
an idle-excess lower bound D for every nonnegative fractional combination of
patterns with these helper and bin counts. It ignores chronology, family and
physical-port restrictions. Nine dual coefficients were nominated with SciPy
HiGHS; verification neither calls nor trusts an optimizer.

Let L be the smaller certified local excess of the two providers. Total rank
mass is 4,816,512 = 73 × 66304 - 23680. For every permitted frame assignment,
provider mixture and packing, the recurrence moment satisfies

    M(b) >= [4,816,512 + b (666 L + D)] / (73 × 66304) > 1.

The exact rational lower endpoint in `EXPECTED.json` exceeds 1 by approximately
**1.17422517347e-8**. Each positive child rank is less than 73, so every fixed
assignment's moment increases with b. The same lower bound at this b therefore
excludes every larger b as well. This proves **b < 0.0016972** for the stated
model. It establishes no new outer κ or unconditional multiplication theorem.

## Reproduce

Python 3.12 and NumPy 2.5.4; no network during replay. With those installed:

```sh
python3 -I -O -B research/t74-variable-frame-cap/verify.py
python3 -I -B research/t74-variable-frame-cap/check_export.py
```

Expected: `PASS_T74_VARIABLE_FRAME_CAP 4243/2500000 ... max_table_states 1953125`
and `PASS_T74_VARIABLE_FRAME_EXPORT controls 8`.

The repository's registered runner uses the exact dependency pin:

```sh
python3 scripts/research_package.py --package research/t74-variable-frame-cap --check-only
python3.12 scripts/research_package.py --package research/t74-variable-frame-cap
```

`--record NEW_PATH` regenerates the complete receipt and refuses overwrite.
Normal verification writes nothing and compares every receipt field. Source
hashes, incorrect billing, singular transports, an overstated packing dual,
input/receipt tampering, optimized execution and standalone export are checked.
The original plan is gzip-compressed locally with its uncompressed upstream
hash retained. `.gitattributes` preserves the directed engine's original CRLFs.
The finite verifier needs no Git history; the repository metadata checker needs
history for `SOURCES.json`'s historical task/selected-result provenance.

The arithmetic loader executes the exact source bytes checked against
`INPUTS.json`, without consulting Python bytecode caches. `-B` alone suppresses
cache writes but still permits cache reads. Four export controls install
conflicting timestamp or unchecked-hash caches and replay in both normal and
optimized mode; every run must retain the original receipt and leave the export
unchanged. This repairs the same source/cache distinction identified in the
related [PR2766](https://github.com/CrocSwap/integer-mult-bounds/pull/2766).
[PR2553](https://github.com/CrocSwap/integer-mult-bounds/pull/2553) isolates the
registered runner's cache namespace; this fix also covers direct verifier calls.
The arithmetic source, inputs, dual and expected mathematical receipt are unchanged.

## Open next questions

1. **Change a logical circuit choice, not just its frame.** The proof fixes the
   scalar gates, ordering and G maps. A new kernel, different lender or retimed
   preparation can escape it. First generate a valid changed word and run the
   frame optimizer and whole-width cost check before native/global admission.
   The blocker is an exact arbitrary-input construction with favorable total cost.
   New words need their own source pins, fixed-point prices and bill: the small
   elimination engine is reusable, while `verify.py` checks this pinned cap.
2. **Optimize a changed parent inventory.** Different capacity counts change
   the dual constraint. First derive the parent's coverage and fully charged
   costs, then rerun the packing bound. A hypothetical bin histogram is insufficient.
3. **Reuse the elimination engine on wider frame domains.** Larger changes may
   create a large separator table. First inspect domain sizes and elimination
   widths; seek a proved contraction or separator decomposition before raising
   the memory cap. The current implementation deliberately rejects tables above
   ten million states.

## Credit and limits

Jeremy Diviney, with substantial OpenAI Codex assistance: this source-bound
variable-frame relaxation, transported-domain computation, contraction and
exhaustive elimination implementation, exact cap and controls. The algorithms
of subspace propagation and min-sum variable elimination are standard; the
contribution is their checked application to these newer borrowed words.

Cinna Davis/PR2226 supplies anticipatory dirty borrowing. Jeremy Kothe's
PR2269/2312/2374 and Rohan Arun's T74 lineage supply the parent, kernels,
existing frame refits and ownership. Vlado Vojdanovski/PR2322 supplies the
coherent handoff words, reference frame invoice and directed numerical engine.
WildIdeas' earlier refit work remains credited. Ali Romman/PR1129 and the
incorporated R480 pattern-dual audit supply the existing packing-relaxation
lineage; our PR2360 applied it to a different fixed 400-helper inventory.
PR2359 independently audits the original raw frame delta. Sagar Thakrar's
PR2339/2387 provides related low-alias construction and packing evidence; it is
not an input to this cap. Original notices are retained under `vendor/`.

No local scalar/phase replay, complete physical owner admission, compiler,
stock/precision, all-size or outer theorem is newly certified. Such constraints
can only remove assignments or add costs inside the stated fixed model. The
selected frontier and predecessor packages are unchanged. No independent human
review is claimed. New work is Apache-2.0; see `NOTICE.md`.
