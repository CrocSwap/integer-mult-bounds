# PR306 finite scalar-bound transport

Prepared with substantial OpenAI assistance. This is an independent review; no upstream program was executed.

## Result and present status

The PR306 scalar checker uses cancellation-free majorants: start every coordinate at 1 and apply v[a] += |c| v[b] for each scalar ADD a += c b. The reported largest intermediate value is therefore the maximum coordinate of its final nonnegative vector. Its scalar-checker bytes are identical to PR305's and bound by the PR306 manifest.

Consequently, a literal fresh full norm recurrence is not mathematically necessary for the reorder-only changes. The concrete crossed intervals and separation from the candidate's outer shear layers must still be verified independently. This review establishes the transport theorem, not that concrete admission.

If that admission passes, the baseline bounds F=86453 and B=2766560 carry unchanged; the previous 156-candidate conservative bounds F=438151 and B=14104135 also carry unchanged. No assertion that the candidate satisfies the old 104-bit cap follows. Its inherited payload bound 64 F^3 B^2 = 1070888631470889114458162912766400 has 110 bits and requires the previously named 112-bit fixed-recipe ceiling. The full primitive constant remains uninstantiated.

## Exact unsigned commutation lemma

An ADD a += c b acts on the majorant vector by M = I + |c| e_a e_b^T. A crossed ADD x += d y acts by N = I + |d| e_x e_y^T. When y != a and x != b, both cross-products of the off-diagonal summands vanish. Thus MN=NM exactly, over the nonnegative integers, for every starting vector. This remains true when a=x or b=y. Reversing a scalar ADD changes only the sign, which the majorant removes. The identical argument therefore applies to the reversed word.

A COPY/ERASE crossing additionally needs the source copied from a not to be touched by the moved destination a; this is exactly the frozen transform's exclusion of copies touching a. In the concrete selected region, verifying that the copied-centre lifetimes have already finished is a stronger sufficient check. Physical MOVE records change frames, not the scalar vector. Pairwise-disjoint move operands ensure that multiple selected moved ADDs also commute when their intervals cross.

Moving one event through its certified interval is thus a sequence of commuting unsigned-operator swaps. Doing all swaps preserves the complete terminal majorant vector. Every coordinate in the recurrence is nondecreasing, so the terminal maximum dominates and equals the largest prefix value. Forward and inverse prefix bounds are invariant.

## Composition with the 156 candidate

Write the old actual candidate word as an initial compensation prefix Q', followed by its new setup A, the unchanged old suffix S, and the appended inverse setup A^-1. A reorder wholly inside S leaves all new factors outside its crossed intervals. Removing initial compensation reads also changes no such interval. Therefore the exact same local commute proof applies to the actual candidate word and its reversal.

This route transports the already proved bound on the actual PR305 candidate. It does not require commuting an artificial over-word used to prove that bound. Some proof-only restored reads could fail a commuting screen; that does not matter once the old bound on the actual word has been established.

Needed concrete evidence:

1. Reconstruct or otherwise independently bind each selected source record, anchor and actual crossed interval to the pinned PR306 input words.
2. Verify all crossed scalar and copied-centre conditions in both rounds, with no new candidate shears inside an interval.
3. Verify the initial-compensation cut lies before every moved interval and final inverse setup after every interval.
4. Separately verify the changed frame paths, source spans, first-frame/entrance/residual invariants and inherited chart/compiler obligations. Scalar commutation alone does not imply physical admission.

## Finite formula and bootstrap

The full finite checker AST is unchanged after removing precisely two new assertions for the reorder stages. All numerical inventory inputs to the displayed invoice are unchanged by the reorder. The independently recomputed baseline coefficient is 90312891518490001. The provisional 156 composition coefficient is 90417469526202901, with all 5090 new setup/inverse events charged per stage and no credit for removed reads.

The exact new coarse root bound 376021808895381/500000000000000000, the freshly priced receipt hash, positive tau/linear gaps and all three rational bootstrap gap checks are bound in finite-review.json. The 156 displayed-coefficient cutoffs log2 are 125004767561877, 221024550975833775858, and 390799911770465175736198773. These are displayed-bill cutoffs only, not cutoffs for the unspecified full machine/primitive constant.

The inherited 281 changed charts and normalizer bound 815 are recorded explicitly as conditional on the changed-geometry bridge. The numerical invoice does not certify that bridge by itself.

## Exact chart-transport audit

check_chart_transport.py verifies the candidate digest, all underlying immutable word/frame/sink bytes against the PR306 manifest, all 706 old chart use inputs, and all 281 exact inverse factor programs. It independently maps the compacted scalar registers and finds precisely 18 touched candidate roles, all on late side-root moves from rank21 to rank22; every such role has an earlier first required frame of rank3 or rank5. No selected forward gate touches a candidate member.

The 281 programs are not a certificate of every later frame pair. They consist solely of first-frame quotients, pivot residual charts and donor line-entrance charts. All those inputs are unchanged. The additional rank22 visits affect baseline306 interior paths, whose fresh chronology, source-span and chart/compiler admission remains a separate bridge obligation. This distinction is explicit in chart-transport-inputs.json. The exact replay retains maximum508 factors for changed programs, maximum615/810 for factor numerator/denominator, the inherited576-factor baseline allowance, and normalizer bound815.
