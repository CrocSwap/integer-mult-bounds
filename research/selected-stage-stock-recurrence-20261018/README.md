# Native stage-one stock factorization and its missing coefficient

**Result:** a source-bound factorization and depth slope for the first native stopped stage of the selected #1094 branch. The factorization is concrete, but the numerical stock coefficient remains unproved because the retained sources do not quantify the row divisor or the old-leaf reserve.

## Question and scope

For the selected native branch, what parent stock divisor does the first stopped stage require, and which parts of its coefficient are actually fixed by the selected source? This narrows the assigned selected-stock-envelope card to stage 1 and the parent-versus-inner reserve split. It does not repeat the recorded cutoff or headroom arithmetic.

The selected record at the pinned base selects the #1094 finite witness, whose exact complex supplier is the binding side. The pinned #1094 review identifies #1087 as its direct parent. In the frozen #1087 assembler, the native branch invokes the seven-step outer witness on the selected complex lower bound with m=73. This identifies the selected producer and branch; the cutoff values themselves are not recomputed here.

Final live-overlap check: PR #3742 remained open at head 89f6af270c550dd02bdb05d7a69987159aa110f2 (updated 2026-10-18 19:21 UTC). Its DONE note answers the cutoff-location question and explicitly leaves sigma uncomputed. This pass takes that adjacent reserve-factorization obligation; it does not repeat PR #3742's chain arithmetic or publish a Discussion update.

## Source-bound stage-one recurrence

The retained stopped construction uses atom width w = ceil(e^s). At stage 1, its parent stock is the cover-tree row divisor times the inherited A0 ordinary-leaf reserve. Writing W(w) for the per-level row divisor, R0(w) for the A0 reserve and D(e) for the cover depth, the sufficient divisor has the form

    S1(e,w) = W(w)^D(e) R0(w).

The retained row note bounds the depth by

    D(e) <= 47 ceil(log2(max(2,e))) + O(1).

The leading depth coefficient 47 is source-bound. The additive depth constant is not supplied. The row note names W(w) but gives no selected numeric function or bound for it. It describes the old-leaf reserve as logarithmic but supplies no coefficient. Therefore this source chain does not give a numerical sigma_1 satisfying log_q S1(e,w) <= sigma_1 w(1+log2 e) over the selected stage's width domain.

The inner-call split is explicit. The reviewed PR185 contract says a completed A0 call borrows from the two chunks passed to it, keeps outer fields as spectators, restores its row coordinate, and contributes zero additional externally supplied stock. The parent does not multiply its reserve by the number of sequential completed leaves. The retained 252 is unused allowance, not A0's measured internal reserve.

This also distinguishes two selected-source fields with sigma-like names from the missing recurrence coefficient. The PR1094 audit records 7,870 actual 73-column maps; its producer computes that field as the length of the sigma-map list. The finite invoice separately records 7,670 physical stock cells as 7,168 data/owner families + 492 local helpers + 8 private centres + 2 coefficient-work cells. These are real selected finite ledgers, but neither gives W(w) or R0(w) as functions of variable e and w.

The 57,604 w ceil(log2(max(2,n))) term is explicitly from the m=120, four-level historical bit candidate. It is not imported into the selected m=73 branch. The source also does not license treating 252 as the old-leaf coefficient.

## Stop result

The bounded success test was to bind one selected stage's parent reserve, depth coefficient and external inner-borrowing contribution to its sources, then decide whether those facts give a numerical uniform stock coefficient. The first three items are bound: S1 factors as above, the depth slope is 47, and completed inner leaves add zero external reserve. The numeric coefficient is not bound. The missing implementation lemma is an explicit same-domain bound for W(w), an explicit coefficient for R0(w), and a numerical additive depth term, all for the selected stage.

This is a scoped source audit, not a stock-fit proof, supplier admission, new kappa or multiplication theorem. It does not infer a coefficient from the huge cutoff headroom, the finite invoice, 57,604, or 252.

## Reproduction

From the repository root, run:

    python3 -B research/selected-stage-stock-recurrence-20261018/verify.py
    python3 scripts/research_package.py --package research/selected-stage-stock-recurrence-20261018 --check-only
    python3.12 scripts/research_package.py --package research/selected-stage-stock-recurrence-20261018

The source receipt pins the selected assembly, its PR1087 archive, the actual #1094 invoice and map-count producer, and the retained PR387/PR185 row contract. The check verifies these source relationships and the finite invoice identity. It deliberately does not calculate cutoff headrooms.

## Open next questions

Can the original completed-row implementation give an explicit uniform formula for W(w) and R0(w), with an explicit additive constant in D(e), on the selected stage-one atom domain? This matters because those are the missing terms in sigma_1. First inspect the pinned PR182/PR185 row-conversion implementation and trace its exact row field through the selected A0 wrapper. The current retained proof only says logarithmic, so the coefficient is blocked until that implementation-level bound is found.

## Credit and overlap

The selected construction and source lineage are Rohan Arun's PR1094 and Jeremy Kothe's PR1087, reviewed in the selected #1099 record. The selected stock audit and its proof-boundary analysis are ToikY's package on Josie Elliston's PR1956/PR1965 work. The stopped-stage recurrence and completed-row interface come from Rohan Arun's PR387 and the reviewed PR185 proof. The m=120 stock estimate is eumemic's five-stage source-bank note and is retained only to delimit its scope. Nick Petalas's open PR #3742 locates the selected complex cutoff sequence but explicitly leaves sigma uncomputed; this note audits the next, distinct reserve-factorization obligation. No independent human review is claimed.

Prepared by OpenAI Codex, worker homelab-10, with substantial AI assistance. New text and verifier are Apache-2.0; predecessor source files remain unchanged.
