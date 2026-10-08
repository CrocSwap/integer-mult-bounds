# Aligned partitions and legal frame order

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance.
The weighted pair construction, split operation, interval layouts, and balanced
coarse sums retain the attribution recorded in `partition_graph.py` and the
archived contributor notices.

## Frozen finite choices

The two dimensions remain 23 and 25. The exact choices are frozen in
`selection.json`: h23 uses `[first6,1,1]`, h25 uses `[first9,1,1,2]`.
An integer 1 selects the first group, 2 the middle group, and 3 the last;
`firstK` selects the first K groups. Only actual pairs are split. An omitted
level requests no split. The contraction cap below always takes precedence.
For each common point, the first six or nine intact global pairs are moved
to the front of the original alternating point order.

At each of the first three recursion levels, the coarse edge `(i,j)` is
summed by columns when `i+j<ng-1`, and by rows otherwise. Later levels use
columns. Both choices sum every original cross edge exactly once.

The archive's original pair graph is checked against SHA-256
`3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420`.
`expected_scalar_sha256` pins each selected ordered graph; the full receipt
and its independently expanded dense support audit are retained.

The complete fresh scalar receipts, including node counts and numbering,
agree exactly with the exploratory compiled words. Independent dense global
triple-coordinate checks also agree before and after renumbering, and a
literal edge/output remapping audit confirms the selected node order.

## Contraction and weighted identities

Suppose the original partition of `n` points has `g` groups, each of size one
or two. It has exactly `n-g` two-point groups. Splitting `s` of these pairs
adds `s` groups. The implementation caps `s` by `max(0,n-g-1)`, so whenever
splitting is allowed the resulting partition has at most `n-1` groups and
retains at least one pair. It retains every point exactly once and preserves
point order. Small inputs use the inherited base cases. Thus every recursive
call contracts; the argument does not depend on the selected finite counts.

For a group, its recursive weight is the sum of its vertex weights and its
internal edges. For two different groups, their coarse edge is the sum of
all edges between them. These terms partition the original weighted graph.
The inherited recursive exclusion identities and the retained singleton/pair
assembly formulas therefore apply to any selected partition into groups of
size one or two. Splitting several pairs uses the same identities as one
split. Row or column grouping only reassociates each complete coarse edge sum:
first sum over the first group's point for each point of the second group,
then sum those columns. Every summand is retained exactly once.

The anchor operation first takes disjoint intact global pairs that omit the
common point, then appends all remaining points in their original order.
It is a permutation of exactly the points other than the common point.
Global triple input labels are unchanged. Dense support checks verify each
addition has disjoint operands and each prescribed partial output has exactly
the required global triple support.

## Core renumbering

For each addition frame `(core,cover)`, retain the original node order within
that frame. Sort the groups by
`(popcount(cover)-popcount(core), -core, cover, first_original_node)`.
Retain all source IDs, then remap every edge and output by the resulting
bijection. Clear the support cache before checking the relabeled graph.

Along an addition edge, the core can only shrink and the cover can only
grow. The difference of their cardinalities cannot decrease. If that
difference stays equal, neither set changed, so the two nodes lie in the
same frame. Consequently every edge between different frames has strictly
increasing rank, while the original order handles all edges inside a frame.
The new numbering is topological. The verifier checks the literal operand
IDs, dense supports, exact core/cover recurrences, and complete output set.

## Scope of the transfer

The partition changes neither the complete triple input basis nor the
prescribed output family. The finite data geometry and its multiplicities
are therefore the inherited ones. The physical compiler must still emit and
pay every operation and every actual frame transition; those obligations are
checked by the separate dirty-basis replay, exact profile, and moment gates.
The fixed coordinate basis is still `I+J`, so the inherited bounds for its
nested-frame matrix ranks and minors apply to these same types of transitions.

This supplies a different verified finite network to the same conditional
transfer theorem. It does not assert an unconditional improvement to integer
multiplication, and introduces no additional all-size hypothesis beyond the
inherited analytic and transfer assumptions.
