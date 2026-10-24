# Sharp high-contact floor in the round-three word

Prepared by Cinna Davis / 1337isnot1337 with substantial OpenAI Codex
assistance; Apache-2.0. This is a written scoped proof with exact finite
witnesses, not a proof-kernel check or a new multiplication theorem.

## Statement

Use the exact scalar opcode, coefficient, order and persistent-field incidence
of Cao Yifan's round-three word in `SOURCES.json`, separately in either
orientation. At every scalar event, all its persistent operands have one
common binary frame subspace in F2^9. Between consecutive scalar contacts on
a persistent field, with no intervening native warp, require containment in
chronological order. The main entrance subspaces stay fixed. The helper
entrances/exits, all scalar contact subspaces and all native warp boundaries
may otherwise vary. In particular, do not impose a relation across any native
warp and do not require final endpoints in this relaxation.

Then each of the eight high owned contacts has dimension at least eight. The
original word simultaneously attains eight at all of them, so these bounds are
sharp. For a center job between that high contact and the zero subspace, its
rank is therefore at least eight. Retaining all eight jobs gives paid rank
mass at least 64 and, at every positive rank exponent t, center moment at
least 8 times 8^t. This is a bound on the center contribution. It does not
optimize the remaining paid/helper moment.

In the forward orientation the contact is the persistent source of an owned
COPY immediately before the descending center job. In the backward orientation
it is the persistent destination of the owned output ADD immediately after
the ascending job. `verify.py` checks these actual macro boundaries and the
initial/final owned CLEARs adjacent to the high side.

## Path lemma

Matarener's PR5060 (`research/owned-centre-wire-floor/PROOF.md`, Lemma1)
already uses forward joins and backward meets to force contact subspaces,
and proves a complete nested owned-wire floor with fixed warps and helpers.
The containment propagation below is the same elementary invariant. The new
source-specific coverage removes all native relations and helper boundaries,
retains only fixed main entrance seeds, and supplies explicit path witnesses
for the newer round-three word. It proves the high-contact floor in that
larger domain, not the predecessor's full owned-wire conclusion there.

Associate a vertex with each main entrance and scalar contact. For each
persistent field, draw an edge from its previous entrance/contact to the next
scalar contact. A native warp terminates that chain: its output begins a new
unconstrained chain, and no relation across the warp is retained. Identifying
the two operands of a scalar ADD at one contact gives their common subspace.
No edge for a productive helper target or final endpoint is needed.

If v lies in a fixed main entrance space and a directed path leads from that
entrance to contact q, then v lies in the space at q. This follows by induction
on the path length, using the containment hypothesis on every edge. Thus k
linearly independent fixed entrance vectors with paths to q force dimension
at least k, regardless of all other contacts, helper choices and native maps.

This argument uses the common physical frame of scalar operands, not their
data coefficients or nonzero logical dependence. Data cancellation does not
remove a required physical contact. Splitting operands into independent gauges
requires a different paid scalar interface and falls outside this statement.

## Source-bound witnesses

The source has 632 persistent fields, of which 224 are main and 408 are
independent arbitrary helpers. Raw event ordinals below omit `climb` events
and start at zero. The graph contains 31,630 distinct monotone edges in each
orientation. Every one of the 240 native events per orientation is cut.
All owned scalar contacts, including the low scatter/gather side, are released
while proving the high-side floor. Helper spaces do not supply witness seeds.

| Persistent role | Forward high event | Backward high event | Original frame ID | Eight independent entrance vectors |
| --- | ---: | ---: | ---: | --- |
| 92 | 10344 | 10367 | 254 | 276, 351, 266, 74, 44, 193, 247, 14 |
| 57 | 10370 | 10393 | 274 | 304, 379, 259, 67, 37, 131, 254, 14 |
| 81 | 10396 | 10419 | 619 | 471, 386, 73, 506, 164, 194, 254, 388 |
| 224 | 10422 | 10445 | 279 | 471, 386, 73, 506, 164, 194, 304, 74 |
| 11 | 10448 | 10471 | 621 | 268, 274, 164, 194, 146, 289, 67, 388 |
| 240 | 10474 | 10497 | 280 | 268, 274, 146, 289, 304, 379, 164, 247 |
| 9 | 10500 | 10523 | 624 | 268, 274, 146, 289, 471, 386, 67, 14 |
| 256 | 10526 | 10549 | 281 | 247, 145, 290, 196, 268, 274, 471, 304 |

Each integer encodes a nine-bit binary vector. `WITNESSES.json` records the
actual fixed entrance role and every graph vertex on each path. It contains
128 paths and 2,204 links across both orientations. The verifier checks every
seed, chronological link, target, binary rank and equality of the resulting
eight-dimensional span with the original high contact. The path lemma proves
the bound for arbitrary candidate subspaces, without enumerating them.

The original full source has paid histogram
`{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}` and productive-helper histogram
`{4:28, 7:7, 8:47, 9:326}` in both directions. These are reconstructed as
baseline controls, including every center. They are not a claimed new invoice.
No solver, power approximation or floating tolerance enters the certificate.

## Decision and limits

The independent-contact/shared-native-map proposal in
[the preceding claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4611#discussioncomment-19139586)
released the high COPY chart while keeping the opposite owned chart at zero.
Its proposed center reduction is impossible under monotone persistent paths.
The proof already holds in a relaxation that forgets every shared-map equation.
No MILP is required to decide that center reduction.

Other bridges or productive boundaries might still improve while all centers
retain rank eight. This theorem proves no whole-profile optimum. Moving the
low center side can also change the job rank, which is then a relative rank
between two nonzero spaces rather than the dimension bounded here. Nonmonotone
transitions, changed scalar chronology, split scalar contacts, phase/general
gauges, changed main entrances and sharing different owned macros need separate
analysis. In particular the previous common-kernel prototype allowed
nonmonotone edges and is not excluded by this theorem.

The source-specific finite statement is distinct from native all-column
realization, precision, movement, owned erasure, compilation and the outer
integer-recovery theorem. Those are not reverified or strengthened here. The
selected conditional kappa remains 0.00302015.
