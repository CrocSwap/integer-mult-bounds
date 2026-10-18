# Independent flow sufficiency and direct-repair audit

The frozen source admits exactly **123 disjoint direct inverse swaps** of the
specified kind. The complete eligibility graph has 1,386 capacity-16 vertices,
1,063 capacity-32 vertices and 26,959 edges. A matching and a vertex cover both
have size 123. Applying that matching gives the retained literal member
`k=940`, with 135,864 actual helper roles and the unchanged complete conditional
child profile. Any subset of those swaps also composes, giving a written
construction for every integer `940<=k<=1063`. Reaching `k=473` from this source
would require 590 inverse swaps.
Thus this particular direct repair cannot reach the boundary. This is neither
general `k=473` infeasibility nor an obstruction to adaptive or broader repacking.

This independent audit also establishes the source premises needed for the
grouped-flow sufficiency lemma below. It does not establish that the unrestricted
boundary integer-flow instance has a solution. A solver timeout or an absent
candidate does not settle that question.

## Attribution, pins and independence

The changed helper inventory and source allocation are Marius-Paul Dumitrean's
PR2979 at `be191346391661f4d35fc0d1508d0a6029572576`. PR2987, pinned at
`02c3047a1e78e6e35e7573c12434ba26f6f9bd96`, established the necessary boundary
`k>=473` and the saturated pattern cost identity. Those results are predecessors,
not new findings here. Yiyang Lu / PR2857 is credited for the chronological
flow and edge-coloring method; Mason Hale / PR2917 for the chronology; retained
owner-engine and source contributors keep the attribution in `sources/CREDITS.md`
and `sources/NOTICE`. The present derivation and independent implementation were
prepared by Ross Richardson's automation with OpenAI GPT-6.1 Sol assistance.

`independent.py` uses only Python's standard library. It does not import or
execute `solver.py`, the parent's `verify.py`, the source owner checker, any
predecessor checker, scipy or an optimizer. It independently reconstructs source
windows by searching backward through source events for the preceding touch,
binds the result to every stored PLAN window, enumerates all legal direct-swap
choices, and checks the matching, cover and literal journal. Hard-coded hashes
bind the actual ORDER, DISPATCH, PROVIDERS, FILL, PLAN and TEMPLATE bytes to the
source export. The source declarations of helper widths and local costs remain
premises; this is not a native-frame reconstruction.

## The family property which makes grouping sufficient

The projected source has 37 replicas and 333 calls. Source T74 calls `2*t` and
`2*t+1` are the same stage at replicas `r` and `r+37`, with the same provider.
The first copy is exactly the stored PLAN order. Every replica traverses stages
`0..8` in source order.

For a pending idle child, its upper endpoint `U` is its source idle sweep's call.
Its lower endpoint `L` is the preceding local invocation or bridge touching the
same pair, or `-1` if no such event exists. The source contract admits
**`L<t<=U`**, since a sweep follows its call but the preceding touching event does
not expose a helper slot at its own call. The independent reconstruction agrees
with all 666 PLAN `(owner,child)` windows, including their exact eligible call
sets. There are 112 ports per window, hence 74,592 bins.

The physical family is `(owner,pair,side,port)`. Child pair and side are derived
from the idle sweep's pair and the child's position in its two-sided list, then
checked against PLAN. Across the 296 `(owner,pair,side)` identities:

1. Distinct child windows of one physical family have disjoint eligible call
   sets. The same physical family may therefore be reused at later children,
   but it cannot host roles in two such children at one call.
2. At every eligible call, the family is excluded from the active data pair.
   This uses both the owner replica and the active pair, rather than merely
   comparing child IDs or coordinates.

These are finite properties of the pinned event schedule, not general facts
about arbitrary owner interfaces. If windows of one family overlapped, a
per-bin flow would miss cross-child same-call collisions and the sufficiency
claim below would need stronger constraints.

## All-parameter grouped-flow sufficiency lemma

Let bins be partitioned into groups having the same capacity and the same exact
set `T_g` of eligible calls. Let `n_g` be a group's number of bins. A pattern
`q=(q_w)` consists of whole helper slots and has `sum_w w*q_w<=capacity(g)`.
Suppose nonnegative integers `x[g,q]` and `z[g,q,t,w]` satisfy:

* `sum_q x[g,q]=n_g`;
* every pattern has its required global multiplicity;
* `sum_t z[g,q,t,w]=q_w*x[g,q]`;
* `sum_(g,q) z[g,q,t,w]=d[t,w]`, the actual call's width inventory;
* `sum_w z[g,q,t,w]<=x[g,q]` for every `g,q,t`;
* flow is supported only on `t in T_g` and widths appearing in `q`.

Assume the two physical-family properties above, and bind every actual call's
helper indices to its declared ordered widths. Then there is a literal whole-
helper fill with compact integral prefixes, no same-call physical-family reuse,
no active-data family use, and exactly the specified patterns.

To prove it, fix `(g,q)` and set `n=x[g,q]`. If `n=0` there is no work. An empty
pattern simply supplies `n` empty bins. Otherwise let `m=sum_w q_w` and let
`K=|T_g|`. Split the `n*q_w` incidences of width `w` among `q_w` labeled slot
vertices, each of degree `n`. Connect them to their required time vertices.
This is an integral bipartite multigraph; each time has degree at most `n`.
Counting its edges gives `mn<=Kn`, so `m<=K`. Add `K-m` dummy slot vertices,
each of degree `n`, filling the time deficits. The deficits have total
`(K-m)n`, so integral greedy filling completes an `n`-regular balanced graph.

For any set of time vertices, regularity gives `n|A|<=n|N(A)|`; Hall's condition
therefore supplies a perfect matching. Remove one perfect matching and repeat.
The resulting `n` colors each contain one edge at every real slot and at most
one edge at every time. Assign each color to one physical bin of this pattern.
This realizes every prescribed width/time incidence and gives distinct call
times within each bin. All bins of the group have the same eligibility, so any
bijection from colors to those bins works.

Across different bins, a same-call collision on one physical family is ruled
out by disjoint child-call sets; within one bin it is ruled out by the color's
distinct times. The active-data property applies to every assigned incidence.
Finally place whole slots successively at offsets `0,w1,w1+w2,...`; the pattern
capacity bound gives a compact, disjoint integral prefix. The inventory equations
allow an arbitrary bijection from same-width incidences to the actual helper
indices of that call. This proves the literal allocation claim.

The proof is written for all finite integral instances satisfying these exact
hypotheses. The program checks the finite source hypotheses and can verify a
retained integer boundary flow and its literal realization. This is not a
formal-kernel proof. Conversely a legal fill induces these integer variables,
so the model represents the stipulated pattern support under the verified
source properties.

At `k=473`, PR2987's cut `[45,332]` has 14,976 width-7 demands, at most 13,440
eligible capacity-16 slots and exactly 1,536 width-7 slots outside capacity 16.
Equality forces every capacity-16 bin meeting the cut to have `[7,9]` with its
width-7 role in the cut, and all outside-capacity-16 width-7 roles to be in the
cut. Thus the generator's corresponding zero bounds are equality consequences,
not an additional restriction. The checker tests them on a retained exact flow;
the necessity result is credited to PR2987.

## Complete direct-swap graph and composition

Freeze all projected source helper identities, call times and bin contents.
Choose an initial `C=[8,8]@16` bin and an initial `D=[7,7,9,9]@32` bin. A direct
inverse swap moves both width-8 roles from `C` to `D`, and one width-7 plus one
width-9 role from `D` to `C`. The receiving bins may be repacked from offset
zero; all other roles keep their bins and times. Each initial bin may participate
at most once.

For each of all `1386*1063` bin pairs, the checker enumerates every choice of the
moved width-7 and width-9 roles. An edge exists precisely when both old `C` times
are in the `D` window, both chosen `D` times are in the `C` window and distinct,
and the four final `D` times are distinct. These conditions are necessary and
sufficient: receiving widths sum to 16 and 32, all unchanged roles were legal,
and compact repacking supplies the masks. The universal source-family properties
above rule out collisions with third bins, including other children of the same
physical family. Consequently no separate third-bin exclusion is missing.

The independently reconstructed edge set equals the retained graph exactly.
The certificate lists 123 edges with distinct endpoints and a cover consisting
of 7 left and 116 right vertices. Every one of the 26,959 edges meets that cover.
Any disjoint direct-swap set has cardinality at most 123 because its edges must
meet distinct cover vertices; the matching attains that bound.

Distinct matching edges affect disjoint initial bins, hence disjoint roles.
Their window and distinct-time conditions persist when performed together.
Cross-child same-family conflicts remain impossible by the source invariant.
Therefore the 123 swaps compose. The independent checker reconstructs all 492
moved roles and their journal entries, then rebuilds every bin's offsets in
`(call,helper)` order. Its complete 135,864-row result equals
`candidate/repair/attained/FILL.json.gz` byte-decoded data exactly. The full
resulting pattern inventory is `k=1063-123=940`.

More generally choose any subset of the 123 matching edges. Each receiving bin
is then either its valid frozen source bin or the independently validated
exchanged bin. The same disjoint-support and physical-family argument applies
without change. If the subset has `s` edges, its pattern inventory is exactly
`k=1063-s`; every `s=0..123` is available. A deterministic construction at any
integer `940<=k<=1063` takes the first `1063-k` certificate edges, applies their
journal moves to the frozen source roles, then repacks each bin. This proves the
finite family interval by a written composition argument; it does not claim
124 exhaustive full literal replays. Combining this with PR2987's necessary
bound leaves `473..939` unresolved by these artifacts.

This optimality is only for a single matching between these frozen initial `C`
and `D` bins and these direct exchanges. Different pattern supports, changes to
other role owners/times, sequential reuse of changed bins, vacancy relays and
general integer flows are outside the graph. No conclusion about those is drawn.

## Complete conditional paid cost and proof level

Each direct inverse swap replaces saturated `C+D` by saturated
`[7,9]@16+[7,8,8,9]@32`, preserving the helper inventory and every residual rank
separately. The attained positive residual histogram is
`{1:8655,3:2478,5:864,48:14095}`. Add all 333 source-declared paid local profiles
`{1:2445,2:706,3:232,4:108,5:18,8:8}`. The complete conditional child tariff is

    822840 H(1) + 235098 H(2) + 79734 H(3) + 35964 H(4)
    + 6858 H(5) + 2664 H(8) + 14095 H(48).

The allocation changes this cost by exactly zero for every tariff `H`. Its rank
mass is 2,408,256; the inherited normalization is `73*896*37`. The source's
conditional namespace invoice is `896*37+408+8+91+2=33661`, or 66,813 at T74.
This audit does not prove physical backing, precision or continuation lifetimes
for that invoice. No scalar-operation or recursive exponent improvement is
claimed. The result tests realization slack in the source's changed cost
structure and identifies the limit of one concrete repair strategy.

Reproduce with:

    python3 -B research/rank7-face-boundary-fill/independent.py
    python3 -O -B research/rank7-face-boundary-fill/independent.py

The code uses explicit exceptions, so optimization does not disable its checks.
Negative controls reject overlapping same-family child windows, an active data
pair in a window, deletion of one eligible graph edge, a width-8 role presented
as the moved width-7 witness, deletion of a required cover vertex, an unperformed
journal move and a changed literal prefix offset. The constructive graph/literal
check and exact finite counts are
finite computations; the flow/coloring/composition arguments are written proofs.
Neither is a formal-kernel proof. Native arithmetic, arbitrary dirty inputs,
literal native restoration, frames/phases, paid source access, physical stock,
precision and outer/all-size recursive transfer remain inherited obligations.
