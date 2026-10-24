# Integral copied owners from grouped source windows

This is a finite owner construction for the changed STAGED644-660 words. It
assumes the source-bound provider interface: 408 indivisible helpers, ordered
widths obtained from the literal native entry/end frames, and local paid profile
`{1:2439,2:726,3:224,4:102,5:20,8:8}`. In each provider the old helper indices
389 and 397 have width seven instead of eight. Every other width is unchanged.
The inventory is `{4:26,5:2,6:18,7:52,8:97,9:213}`. This document does not prove
the changed word or its numerical precision contract.

The fixed source is dcharb78's PR3133 head
`51eb9c4ee9e4722010d308aa3309e039d3940cc2`, and the prior cap-attaining fill is
Jeremy Diviney's PR3148 head `f2927a4b8afcf0701a6b945e14f30de1d94f5176`.
The source-window/checker lineage includes Tekalign's independent owner checker,
Marius-Paul Dumitrean's joint endpoint words, Yiyang Lu's pattern/flow realization,
and Nick Petalas's copied-owner constructions. The old cap remains a conditional
fixed-inventory result. Its numerical cap does not apply to these changed words.

## Grouped integer witness

Take the first of the two exactly interleaved T37 copies in the source T74
ORDER. Compute its windows directly from the retained source execution template.
They have the form `lo < t <= hi`, with `lo=-1` for an initially available source.
A group g collects the n_g physical bins with one common capacity and the same
integer interval. Every bin in a group has a distinct physical family while that
interval is open. Windows belonging to successive children of the same physical
family have disjoint open/closed integer intervals. `portable_expand.py` checks the latter
property from the literal plan, rather than assuming distinct child labels mean
distinct physical stock.

Fix S copies. An aggregate witness consists of nonnegative integers X_(g,p),
the number of bins of each capacity-feasible width pattern p, and Z_(g,t,w), the
number of width-w roles from macro-call t placed in group g. Its exact equations
and inequalities are:

* Sum_p X_(g,p) = S n_g.
* Sum_t Z_(g,t,w) = Sum_p p_w X_(g,p).
* Sum_g Z_(g,t,w) = S I_w, for every macro-call t and width w.
* Z is zero outside `lo_g < t <= hi_g`.
* Sum_w Z_(g,t,w) <= S n_g.

Every pattern's total width is at most its bin capacity. Its number of nonzero
helper slots is at most S. Our actual S is twenty; the admitted pattern
catalogue has at most six slots. The pattern optimizer is only a search tool.
The published compact witness contains exact integers. `verify_aggregate.py`
checks every equation, capacity and source-window bound using integer arithmetic;
`portable_expand.py` uses only those checked integers. No fractional assignment
or total-unimodularity assertion is used as a literal owner witness.

## Exact call-copy decomposition

First allocate the X bins and their slots. For each group and width, assign its
Z roles arbitrarily to slots of that width. A bin may now contain several roles
of one macro-call. That is allowed at this intermediate step. It has at most S
such roles because the entire pattern has at most S slots.

For one macro-call, regard every remaining role as an edge from its bin to its
width. Let R be the number of call copies still to assign. The maintained
invariants are: width w has R I_w remaining roles, every bin has degree at most
R, and group g has degree D_g at most R n_g.

To select the next actual call, use a finite lower-bounded network:

* Source to group g has bounds `[max(0,D_g-(R-1)n_g), n_g]`.
* Group g to each of its nonempty bins has upper bound one and lower bound one
  exactly when that bin has degree R.
* Bin to width edges represent the actual remaining roles, with integral
  multiplicity capacities.
* Width w must deliver exactly I_w units to the sink.

The assignment giving each remaining role weight 1/R is a feasible fractional
flow. The group upper bound follows from D_g<=R n_g. For the lower bound,
`D_g/R >= D_g-(R-1)n_g` follows from the same inequality. A bin of degree R
delivers one unit, all other bins deliver at most one, and each width delivers
exactly I_w. Integral capacities and lower bounds give an integral feasible
flow after the standard circulation reduction. The implemented augmenting-path
algorithm produces this integral flow directly. Removing its selected roles
preserves all three invariants with R replaced by R-1. Repeating constructs S
actual calls, each with every required width count, at most one role from a bin,
and at most n_g roles from each group.

This argument is an all-parameter written realization lemma under its stated
integer-flow and pattern-size hypotheses. Feasibility of this particular
aggregate witness is finite computation, not an all-parameter packing theorem.

## Physical owners and endpoint availability

For a group, the physical stock is exactly S copies of its n_g source bins.
A bin containing any role at macro-time hi requires an owner-copy index at
least the largest call-copy index among those endpoint roles. Other bins have
no lower requirement on their owner-copy index.

For each j, the number of bins requiring owner index greater than j is at most
the number of endpoint roles assigned to actual call-copy indices greater than
j. The preceding decomposition bounds that number by `(S-1-j)n_g`, exactly the
number of physical bins in those owner copies. These nested Hall inequalities
justify sorting bins by decreasing requirement and assigning the physical
owner copies in decreasing order, with n_g bins per owner copy. The construction
checks every resulting requirement separately. Original owner, child and port
labels are retained when allocating each copy's n_g bins.

The literal chronology is
`(stage,r) at macro-time t -> (stage,r+37*j) at time S*t+j`.
Provider dispatch is copied along that embedding. If a source window has
noninitial lower endpoint lo, every admitted macro-time satisfies t>=lo+1;
therefore `S*t+j > S*lo+k` for every owner-copy k. For an upper endpoint,
t<hi is automatically safe for all copies, and t=hi is safe because the owner
index k is at least j. Initial `lo=-1` stays initially open. Thus the exact
windows are preserved, including their strict lower and closed upper endpoints.

For two bins of the same physical family at one actual call, their source
children must belong to overlapping macro-windows, contrary to the checked
successive-window disjointness; if their child is the same, their owner-copy,
owner, child and port keys identify the same bin, where the call decomposition
already allows only one role. This proves the full physical-family exclusion,
not merely disjoint coordinate masks.

Finally assign the actual ordered native helper identities bijectively to the
slots of their widths at each actual call. Every `(call,helper)` occurs once.
Sort each bin's delivered roles by their actual call times, then assign
consecutive offsets `0,w_1,w_1+w_2,...` in that chronological order. Consequently
every intermediate pending mask, as well as the final mask, is a compact prefix;
it has integral disjoint coordinates. Each bin's charged idle rank is its capacity minus the exact
sum of these widths. No zero-width stub, role deletion or unpaid family stock
is introduced.

## Paid scope and remaining obligations

At S=20 there are T=740 replicas, 6,660 actual calls, 2,717,280 helper roles and
896T=663,040 live families. Dispatch has 2,500 gauge44/base and 4,160 extra calls.
The physical stock is `896T+408+8+91+2=663549`; all 91 private cleanup buffers
remain charged. The complete recursive histogram is 6,660 local bills plus
the independently reconstructed idle histogram, with rank mass 65088T.
The fresh `PORTABLE-REPLAY.json` and independent owner audit record the attained
histogram; the optimizer's fractional target is not substituted for it.

The corrected literal witness generated by `portable_expand.py` attains exactly
`idle={1:174156,3:48334,4:1,5:10792,6:3,48:283185}` and
`H={1:16417896,2:4835160,3:1540174,4:679321,5:143992,6:3,8:53280,48:283185}`.
Its rank mass is 48,165,120. The predecessor checker passed all 2,717,280 rows;
the separate chronological offset check covers every intermediate pending
prefix. The standard-library aggregate verifier checks the integer primal and
four semantic corruptions without importing an optimizer. The original width-ordered offsets failed the intermediate-prefix obligation
and are not admitted or supplied as candidate input.

The separate fresh arithmetic check derives a complex-root interval
`[0.001730006549538841847005,0.001730006549538841847006]` at m=73,
checks its strict sides with three exact interval engines, and runs the modern
outer and bootstrap inequalities. This is not a formal-kernel consequence of
the owner checker. Complete source/native/precision/prefix/outer admission must
still bind to the corrected fill's semantic payload.

The copied network flows are finite offline construction of a fixed supplier;
their search and generation work is not charged as free recursive arithmetic.
Runtime controller, native entry/end frames, source access, numerical precision,
prefix payload and outer invoice are separate interfaces that must bind to the
emitted ORDER/FILL/DISPATCH and actual words. This owner result alone certifies
no multiplication theorem, selected frontier, all-size implementation or formal
kernel theorem. No Lean kernel proof is claimed.
