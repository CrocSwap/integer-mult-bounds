# Exact direct-swap boundary and the chronological k473 question

The frozen-source, pairwise-disjoint direct-swap model has exact minimum
`k=940`: a 123-edge matching attains it and a 123-vertex cover proves that no
more direct inverse swaps are possible. A literal `k=940` allocation and
123-swap journal are retained. Full chronological feasibility at `k=473`
remains unresolved: the single 600-second flow solve reached its time limit
without an incumbent. That solver outcome is not an infeasibility proof.

The question is whether the fixed PR2979 saturated-swap family has a literal
owner allocation at `k=473`. PR2987 proved `k>=473` necessary and checked the
shipped `k=1063` witness. This construction attempt changes only the allocation.
It does not change a native word or claim an exponent saving.

The optional generator is `solver.py`. Its output and solver receipt are under
`candidate/`. A solver status by itself is neither exact feasibility evidence
nor an exact infeasibility certificate. A candidate counts as a construction
only after exact integer checks, coloring and the independent literal checker.

## Frozen premises

The source is Marius-Paul Dumitrean's PR2979 at
`be191346391661f4d35fc0d1508d0a6029572576`. The independent boundary predecessor
is PR2987 at `02c3047a1e78e6e35e7573c12434ba26f6f9bd96`. Their notices, credits
and frozen evidence are in `sources/`. In particular, Yiyang Lu / PR2857 owns
the chronological flow and edge-coloring method adapted here; Mason Hale /
PR2917 supplied the T74 chronology, and the owner-engine lineage includes
Dugongue and Tekalign. The present adaptation was prepared with GPT-6.1 Sol.

Project the source T74 order by taking every even call and retaining replica
IDs `0..36`. The odd call is the same stage at replica `r+37`, with the same
provider. This gives exactly 333 calls, each having 408 *ordered* helpers.
The declared provider-indexed widths are used when emitting actual helper IDs;
both provider inventories are `{4:26,5:2,6:16,7:52,8:99,9:213}`.
Their derivation from native frames remains an inherited premise.

The legal time interval of a bin is the source interval `L<t<=U`, reconstructed
from the frozen template and projected order. There are 112 ports per owner
and retained idle child. A physical family is
`(owner,PLAN.pairs[child],PLAN.sides[child],port)`. A legal fill assigns each
`(call,helper)` once, avoids active data, uses each physical family at most once
per call, respects capacities and has disjoint integral masks forming a compact
prefix in each pending bin. Different child IDs do not waive family identity.

The exact target comes from 590 inverse swaps of the shipped mix. Its changing
counts are `[7,9]@16:15780`, `[8,8]@16:796`, `[7,8,8,9]@32:590`,
`[7,7,9,9]@32:473`; every other multiplicity is retained.

## Necessary equalities at the boundary

Let `I=[45,332]`. The PR2987 cut counts 14,976 width-7 roles in `I` and
13,440 capacity-16 bins whose windows meet `I`. Every allowed capacity-16
pattern has at most one width-7 slot. At `k=473`, there are exactly
`1063+473=1536` width-7 slots outside capacity 16. Therefore all inequalities
in

    14976 <= cap16_roles_in_I + outside16_roles_in_I <= 13440 + 1536

are equalities. Every capacity-16 bin meeting `I` must have pattern `[7,9]`,
with its width-7 role in `I`. Every width-7 slot outside capacity 16 must also
be used in `I`. The generator imposes these consequences to reduce the model;
they are necessary, not additional modeling assumptions. This argument alone
does not establish sufficiency.

## Integer flow model and literal realization

Group bins by `(capacity,exact set of eligible call times)`. For each group
`g` and allowed pattern `q`, use an integer `x[g,q]` for its number of bins.
For each eligible time `t` and width `w` occurring in `q`, use integer
`z[g,q,t,w]` for its number of assigned roles. All variables are nonnegative.
The equations and inequalities are:

* Each group uses exactly its available number of bins: `sum_q x[g,q]=n[g]`.
* Each pattern has its exact global target: `sum_g x[g,q]=target[q]`.
* For each width, `sum_t z[g,q,t,w]=q[w]*x[g,q]`.
* At every time and width, `sum_(g,q) z[g,q,t,w]=inventory[w]`.
* At every group, pattern and time, `sum_w z[g,q,t,w]<=x[g,q]`.

The last constraint enforces call-distinct bins rather than merely coordinate
capacity. The implementation additionally verifies that pending windows of
the same physical family are pairwise disjoint and that no legal bin time
has its family active as data. Thus the final per-bin time distinction also
implies the full same-call physical-family rule in this frozen model.

One bounded `scipy.optimize.milp` invocation is permitted, at most 600 solver
seconds. A returned vector is rounded and every bound and equation is checked
with integer arithmetic before any role is emitted. The support is then
independently recounted by group, global pattern, per-pattern width and call.
Floating infeasibility or timeout is recorded without an infeasibility claim.

For an integral flow, the source coloring method gives an explicit realization.
For fixed `(g,q)` with `n=x[g,q]`, split each width's `n*q[w]` demand among
`q[w]` slots, each of degree `n`. The time degree is at most `n` by the last
inequality. Pad with dummy slots to an `n`-regular bipartite multigraph. Repeated
perfect matchings decompose it into `n` bins, each with one role in each real
pattern slot and at most one role from any call. Every assigned time belongs
to the group's source window. Place each bin's roles consecutively from
offset zero and bind widths to the dispatched provider's actual helper IDs.
This proves the flow-to-fill step for arbitrary integral flows satisfying
these hypotheses; it does not prove such a flow exists at the requested target.

The implementation adapts PR2979's `color_pattern` transparently, using scipy's
bipartite matching. The emitted `FILL.json.gz` records every actual helper,
owner, child, port and offset. The parent's separate standard-library checker
must verify those rows directly, without importing this generator or scipy.

## Exact obstruction to a direct repair of the shipped fill

The same boundary question also has a smaller direct construction attempt.
Freeze every source helper identity, width and call time and allow only
pairwise-disjoint inverse swaps between a source `[8,8]@16` bin C and a source
`[7,7,9,9]@32` bin D. In one swap move both width-8 roles from C to D, and
move one width-7 and one width-9 role from D to C. Repack receiving coordinates
freely from offset zero; every other role's owner remains fixed. The swaps
must use each source C and each source D bin at most once.

Make a bipartite graph with all 1,386 source C bins on the left and all 1,063
source D bins on the right. A C/D edge exists precisely when both C call times
lie in D's legal source window and some choice of one 7-role and one 9-role
from D has both call times in C's legal source window. The two received C times
must be distinct, and the two retained D times together with the two incoming
C times must be four distinct times. The frozen-window active-data and
nonoverlap facts above ensure that these per-bin tests cover physical-family
conflicts after any matching of swaps. The inventory and capacities then
give exactly `[7,9]@16+[7,8,8,9]@32` from each matched pair.

The finite graph has exactly 26,959 edges. `candidate/repair/PAIR-GRAPH.json.gz`
lists its canonical vertex enumeration and the first legal role choice per
edge. `MATCHING-CERT.json` lists a 123-edge matching and a 123-vertex cover
(7 left vertices and 116 right vertices). Every listed matching edge belongs
to the graph, no matching endpoints repeat, and every graph edge touches the
listed cover. Thus weak matching/cover duality proves **123 is the exact
maximum for this graph**; no trust in a floating optimizer or a matching
library's optimality status is needed after these certificate checks.
Independent reconstruction of the entire eligibility graph is a separate
finite check, rather than an inference from the generator's own edge list.

Boundary member `k=473` requires 590 inverse swaps from source `k=1063`, so
pairwise-disjoint direct swaps with these frozen source roles cannot reach it.
The attained literal file under `candidate/repair/attained/` applies all 123
matching edges and realizes `k=940`, the minimum in this restricted class.
It retains all 135,864 actual `(call,helper)` identities, uses the unchanged
provider dispatch and is repacked by `(time,helper)` within each bin. The
four actual role moves per exchange are recorded in `JOURNAL.json.gz`.

Every subset of the 123 matching edges also composes legally: its changed
bins are disjoint, every received role remains in its source window, and
disjoint pending windows exclude a collision with another bin of the same
physical family. Retain the other bins and repack each selected bin. Taking
the first `j` edges for `0<=j<=123` therefore gives a written construction
for every `k=1063-j`, that is, all `940<=k<=1063`. This is a proof from the
verified matching and source premises, not 124 separate full literal replays.
The newly emitted full endpoint witness is `k=940`.

This does not obstruct a general flow, source-role retiming, vacancy relays,
reuse of a modified bin, multiple-bin exchanges or another reconstruction of
the same target. The complete chronological feasibility of `k=473` remains open.

The full model has 333 window groups, 189,965 integer variables (925 pattern
variables and 189,040 flow variables), 111,348 constraints and 677,975 nonzeros.
Its one invocation used a 600-second limit, zero relative gap and one HiGHS
thread. HiGHS reported `Time limit reached`, no primal incumbent, zero
branch-and-bound nodes and 220,018 LP iterations. Its logged solver time was
600.03 seconds (Python wrapper elapsed 600.185 seconds). The receipt is
`candidate/SOLVER.json`; `candidate/HANDOFF.json` records the unresolved target.
Python 3.12.12, numpy 2.4.2 and scipy 1.17.0 were reported; the raw solver banner
identifies HiGHS 1.8.0. No integral flow or `k=473` literal file was produced.

A useful next structural obligation is a legal coupled exchange using one C
bin, one D bin and a relay bin whose pattern is retained. Such a move may
perform one inverse face swap while rearranging the relay's actual roles,
escaping the fixed two-bin graph. The present cover does not constrain it.
The `k=940` witness is a concrete starting fill for that obligation; reaching
`k=473` would still need 467 additional inverse face swaps or a full new fill.

## Complete conditional cost and covered domain

All family members have the same residual histogram
`{1:8655,3:2478,5:864,48:14095}` at T37. The fully charged local per-call
profile remains `{1:2445,2:706,3:232,4:108,5:18,8:8}`. Hence a successful
literal fill has exactly 135,864 helper roles and complete paid profile

    {1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095}.

For the inherited recursive tariff `H`, its complete charged child cost is

    822840 H(1) + 235098 H(2) + 79734 H(3) + 35964 H(4)
    + 6858 H(5) + 2664 H(8) + 14095 H(48).

The rank mass is 2,408,256. In the standard source convention the normalized
moment is `M(a)=sum_r n_r*(r/73)^(1-a)/(896*T)`. If
`H_a(r)=r*(73/r)^a` for positive ranks, this equals the displayed child cost
divided by `73*896*T`; an arbitrary tariff `H` need not have this normalization.
The inherited conditional namespace/stock bookkeeping is
`896*37 +408 helpers +8 centres +91 private buffers +2 guards =33661`.
Two interleaved copies have T74, 271,728 roles, doubled paid profile and stock
`896*74+408+8+91+2=66813`; interleaving must still be checked literally.
These counts do not newly prove physical storage or physical execution.
Every saturated swap preserves the entire residual histogram, so the paid
cost change versus the shipped family member is exactly zero for every `H`.

The question and positive results cover only this exact T37 order, fixed
provider declarations, capacities and source windows. The emitted endpoint
is `k=940`; the subset argument covers the stated `940<=k<=1063` interval.
Native arithmetic, arbitrary dirty-input behavior and exact restoration,
entry/exit frames, phase handling, source access, backing stock, precision,
prefix and outer/all-size transfer remain inherited source obligations.
The flow-to-fill lemma is a written mathematical argument. Its instantiated
model and any emitted roles are finite exact computations. Neither supplies
a formal-kernel proof or a new recursive complexity admission.

## Reproduction

The search requires numpy/scipy; checking the final literal candidate does not.

    /opt/homebrew/bin/python3.12 -B research/rank7-face-boundary-fill/solver.py --seconds 600

The direct repair graph, exact matching/cover certificate and attained literal
fill can be regenerated without a MILP invocation into a fresh output directory:

    /opt/homebrew/bin/python3.12 -B research/rank7-face-boundary-fill/solver.py --repair --out /tmp/rank7-direct-repair

The generator refuses to overwrite an existing output directory. Do not rerun
the bounded search merely to reproduce a literal artifact: use the independent
checker and retained `FLOW.json.gz` / literal rows. Preserve a no-candidate
receipt as UNKNOWN rather than converting the time limit into a theorem.

Generation provenance: the one MILP invocation began before the optional
`--repair` mode and its helper functions were added to this same file. Its
MILP equations/options were retained, but the current whole-file hash is not
claimed to be the script hash at invocation. No historical hash or purported
exact source reconstruction is asserted. The recorded model dimensions,
versions, options and raw solver log describe the attempt; independent exact
graph/certificate/literal replay establishes the mathematical result. The
MILP was not rerun to bind the revised generator. The raw invocation evidence
is preserved in this run's external generation directory.
