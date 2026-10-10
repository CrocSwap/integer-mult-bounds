# Scoped gen5b donor matching argument

Substantial OpenAI Codex assistance. Apache-2.0. Generator, exact frames,
physical alias contract and module data are inherited from PR296
`b15a33ce4f0e31379be685139f78b9c1e7ffa77b`, with PR168/PR200/PR285 lineage.
This investigation changes the matching rule after the existing producer
endpoint descent. It does not claim invention of compensated reuse.

## Fixed graph

The independently regenerated graph contains 65,920 eligible edges. Donors
are ungauged, non-root, non-source roles with an exact nondegenerate final
frame contained in the recipient's gauge frame and with last operation before
the admissible read time. All incident recipient frames have rank 21.
Lower-rank recipients have no edges in this screened graph. Target chronology
is checked exactly, including stable order for equal read times.

For a donor whose final frame has rank e, appending a rank-21 recipient
replaces its final rank-(24-e) child by a rank-(21-e) child. The recipient's
remaining path is retained; its independent rank-21 entrance disappears.
At a fixed positive moment exponent p in (0,1), the donor-dependent benefit is

    (24-e)^p - (21-e)^p,

with 0^p = 0. This benefit is positive and strictly increasing with e:
the increment (x+3)^p-x^p decreases with x because p*x^(p-1) decreases.
The bank-stock and removed-entrance terms depend on matching cardinality,
not donor identity, since every eligible recipient has rank 21.

Donor subsets admitting an injective assignment to recipients are independent
sets of a transversal matroid. The standard greedy independent-set rule,
processing donors in decreasing e and inserting by an augmenting path,
therefore maximizes the donor-only benefit for every such fixed p. All
weights are positive, so it also reaches maximum cardinality. An independent
Hopcroft-Karp computation confirms cardinality 1,728. The pinned matching has
1,726 pairs; rerunning after endpoint descent creates two additional pairs.

This is a scoped mathematical argument for the fixed graph. It does not
optimize producer frames, module recipes, gauge selections, signed prefix
cost, subsequent kernel opportunities or the entire finite construction.
Those interactions require the actual emitted word and full invoice.

## Local evidence

The rank-aware matching selects 878 rank-21 donors (pinned:706) and 405 rank-3
donors (pinned:674). Its exact PR200 row has 15,432 dirty registers and 18,952
formal variables. All F2 columns equal the identity target contract; all
integer columns equal the retained defining decoder, with every source and
dirty column restored. Exact frames, handoff containment and complete role
and target chains pass. The latter integer check is a defining-decoder check,
not a claim that the integer word equals the F2 identity.

Virtual word SHA256:
`9144bc371104df43abf65f8fcff7a0f195301118ccb4c37b02799799d9f2eec1`.

Fresh scalar discovery retains all 904 concave retimings and 220 target groups.
The independent matching producer re-derives all 65,920 edges and compares its
1,728-pair cardinality with the inherited Hopcroft-Karp implementation. The
complete regeneration command compares all five bit files with the pinned
submission, comparing compressed JSON after decompression.

The final composition retains all 1,720 PR299 kernel entries, mapped by logical
role to the new literal indices; all 440 restorations and seven terminal sinks
are re-derived. The unchanged checker cores verify those stages, all physical
columns and both reflected ledgers. The final global namespace uses 15,425 dirty
registers. All twelve immutable stages and the complete finite invoice must
pass under verify.py; the admitted conditional kappa is
375528459906701/500000000000000000. This does not establish whole-construction
optimality or eliminate any inherited all-size assumption.
