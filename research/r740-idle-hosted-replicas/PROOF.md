# Composition and proof boundary

## Unchanged local and global identities

PR443 reconstructs its primitive retiming, rank138 shared-donor kernel and B-frame
retiming from frozen witnesses. Its verifier checks all 980 local columns, integer
source spans, 7,620 unbanked scalar columns, explicit residual isometries, bank
routes and finite geometry. We run that verifier unchanged. All 288 local calls
and their orientations, data owners and local instruction lists are retained.
The compressed schedule, final exchange, private centres and data geometry are
also retained exactly. The independent hosting audit compares these fields to
the freshly generated parent rather than trusting emitter declarations.

## Hosted residuals

We use the hosting lemma of PR442 (`../idle-axis-hosting/PROOF.md`, sections 1–2).
A full dirty local invocation acts on each helper stream by the coordinate factor
of its residual projector, for arbitrary correlated input. A pending idle advance
is the product of commuting factors on its pending coordinates. Assign a whole
helper residual to a disjoint subset of those coordinates on a data pair that is
untouched from that invocation until the idle advance. Move the factor to the
advance and leave the advance only its complementary coordinates. Their product
is the original idle advance, so the endpoint operator is unchanged.

A hosted route first uses PR443's exact residual isometry, then a slot permutation
and the idle basis map from PR442. The residual isometries here are coordinate
permutations, but the invoice keeps the parent's conservative 144-factor extra
charge and adds PR442's two hosting factors. Hosted families are outside the
active pair. Distinct hosted slots are disjoint, while their route classes and
families keep local owners injective. The complete invocation theorem admits the
correlated contents of these data streams. This last interface extension remains
a mathematical assumption/review point; ownership checks alone do not prove it.

The audit independently derives the last-touch windows from the unchanged
schedule. For every slot it checks stage, helper, data-copy bounds, exact residual
width, coordinate range, uniqueness and disjointness. It checks every replica's
physical owner, exact remainder histogram and complete stage-specific bank
coverage. All 213,120 helper occurrences are accounted for: 159,168 hosted and
53,952 banked. Banks per stage are (1968, 2272, 2504, 0, 0, 0, 0, 0, 0).

The bit profile is

```
rank:       1       2      3       4      5     6      7     8
count: 728640  305600  80832  111584  33984  8576  16704  2592
```

Its rank mass is 2,387,712, and 64×37,464 − 2,387,712 = 9,984.
All banks are full, and 64² > 2×8² establishes depth-two halving.
Fourteen controls reject changes to slots, windows, call identity, orientation,
replica ownership, bank stage, live stock and remainder summaries. A fresh hash
covers the expanded renamed instruction stream; the old bank-only hash differs.

## Finite accounting and composition

All helper routes, including hosted routes, are charged twice in the splice
count. The finite coefficient includes unchanged additions, bridge operations,
copy/erase episodes, private centres, all paid calls, compiler and selector costs,
the inherited prefix bound, and the new physical stock. The prefix bound has
123 bits and is charged at 128; the two-level coefficient has 286 bits and is
charged at 512. The row bound is 18,355 < 20,161. Hosting preserves the local
program and uses orthogonal coordinate factors, so the parent's conservative
prefix envelope remains valid under the hosting interface.

The wrapper reruns the whole PR442 verifier, including its complex phase replay,
independent hosted audit and finite invoice. We recompute both complex moments
and its finite invoice from those fresh outputs. Its larger inherited per-vertex
bill is retained. The bit lower endpoint and complex supplier are checked by two
rational moment engines with the inherited bad-branch allowance. The outer
assembly uses six bootstrap steps, η = β = 10^-18 and 47 strict inequalities.
The next 10^-18 grid point, zero η, zero β and unit β are rejected.

The resulting exact κ is 623036752743971 / 500000000000000000.
All parent interfaces and PR442's idle-data hosting extension remain explicit;
this finite certificate does not discharge the all-size hypotheses.
