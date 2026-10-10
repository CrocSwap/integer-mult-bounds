# Additional early-cut response pairs

This is a finite, source-bound improvement under the same all-size hypotheses
as PR259, PR263 and PR265. It does not prove those hypotheses or claim an
unconditional integer-multiplication theorem.

## Scalar extension across cuts

Retain the original 518 kernel entrances and add 369 pair entrances at original
record 676559. Each pair has one distinct pivot p and one donor d. Its complete
target-response columns at that cut agree over F2. No pivot is a donor in any
selected pair or original block. Every selected helper is unmodified before its
own cut; its only permitted prefix reads are the original zero-frame target
compensations. COPY ownership and source ownership are unchanged.

For a pair, remove the pivot's initial target compensation, insert d += p at its
cut, and subtract p from d at the final full frame. This is the original
response-kernel rewrite with kernel vector e_p + e_d. Its effect on targets is
zero because the removed pivot correction equals the donor's suffix response.
Its two basis operations restore arbitrary helper contents. Scalar correctness
is over F2; the actual signed integer operations remain in the coefficient and
prefix invoices and are not claimed to satisfy the same integer cancellation.

Sharing a donor across different cuts requires a simultaneous argument. Write
N_i for the injected donor updates at cut i. Global pivot/donor disjointness gives
N_i N_j = 0 for every i,j. Thus the added shears commute as helper maps and their
inverse is the sum of their signed inverse updates. Before a later pivot is
used, that pivot has not been written by the original program, nor by an earlier
basis update. Consequently its value is still its own original dirty input.
Linearity separates the contributions of the distinct pivot inputs. The original
prefix hypotheses ensure that an injected donor perturbation can contribute to
target data but cannot create an unaccounted value in a later pivot. Each pivot
contribution therefore cancels by its own cut's response identity. At the end,
the inherited full-word identity returns that contribution in its donor only;
the final inverse update removes it. This argument permits correlated arbitrary
initial dirty values, without assuming independent or zero scratch contents.

The independent prefix checker verifies each selected block at its own actual
cut, including prefix eligibility and every target-response equality. The
original transform checks all 20,107 local formal columns in both directions.
The separate five-stage checker checks all 23,627 global formal columns.
Omitted forward/inverse basis controls must fail. These checks bind the
simultaneous argument to the emitted program, not merely to pairwise hashes.

## Frames and completed banks

For each pair choose an exact nondegenerate entrance E inside both original
first-use frames after the cut. The pivot starts in E; the donor retains its
zero entrance. A donor shared between cuts must encounter nested entrance
subspaces in chronological order. At equal cuts the inherited dimension order
visits any such chain increasingly. The actual emitted MOVEs must all be nested;
dimension ordering alone is not accepted as a containment proof.

No address compiler is changed. The unchanged independent legality checker
rechecks every emitted frame transition and COPY lifetime. The unchanged bank
checker constructs exact rational projector charts from the actual bases and
checks every bank assignment and the full-bank identities in both directions.
An additional rational elimination audit validates every candidate basis B and
annihilator A: their ranks equal the recorded dimension and codimension, AB^T
vanishes, and the weighted Gram matrix is nonsingular. New frame IDs cannot
overwrite inherited frames; every emitted frame reference must resolve.

The new entrances contribute 372 dimensions: 345 fresh pairs contribute 348,
and 24 pairs sharing existing donors contribute 24. Of those 24, 19 share across
cuts and five only within a cut. The total entrance dimension is 1716 and there
are 887 pivots. The inherited 40-replica construction therefore has normalized
stock 173883 - 1716/3 = 173311 and literal stock 866555. Rank mass decreases by
the corresponding amount; the normalized deficit remains 35200. Every added
basis gate, inverse gate, chart, selector and copied center remains charged.

## Retiming and exact price

The inherited 25-gate retiming is rebound only after all original scalar and
COPY events outside compensation/basis categories agree byte for byte and in
order with the freshly reproduced baseline. Its original checker revalidates
source spans, nondegeneracy, nesting, endpoint identity and both ledgers.

An additional 29 role-disjoint connected blocks contain 57 ADDs. Within each
block the old operations share a frame. Individual gate moves can be blocked by
adjacent gates at that same frame; moving the whole block removes that artificial
boundary. Discovery constructs exact joins of entry requirements and
intersections of exit requirements, tests nondegeneracy and prices the complete
resulting rank histogram. The frozen witness is admitted without trusting that
search: full scalar-core alignment binds all 57 operations; every new MOVE is
checked for exact containment, and every changed non-target operand's defining
integer source span is checked inside its new frame. All new frames receive the
unchanged exact rational chart and prime-guard audit. The scalar/COPY projection,
initial and final frames, total number of calls and rank mass are unchanged.
Thus the plateau change improves only the distribution of charged child ranks.
Its complete histogram delta is independently recounted in the final invoice.

Every final histogram is reconstructed from the emitted word. The unchanged
native price checker reconstructs the PR249 baseline by subtracting the complete
delta and must reproduce its exact old price. The independent finite invoice
recounts the literal five-stage histogram and requires equality to five times
the normalized price profile.

The additive fixed-prime calculation retains PR265's prime 2^127-1, full fallback,
eta=10^-24, beta=10^-9 and 10^-27 grid. It uses the unchanged, hash-pinned two
rational interval engines and outer assembly. Every finite bootstrap gap and
cutoff is checked, all 47 strict constraints and seven margins must pass, and
the adjacent grid point must fail. No limiting infinite-level saving is claimed.

The final reproduction regenerates the original source baseline, compiles its
unchanged native checkers, emits this candidate, and binds all fresh outputs to
the frozen witnesses and receipts. Discovery scores and stored PASS labels are
not accepted in place of those executions.
