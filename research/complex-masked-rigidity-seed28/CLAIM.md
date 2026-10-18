# Local sprint claim — seed 28

- Track: complex supplier (20–39); OS randomness returned 28.
- Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
- Started: 2026-10-13 19:38 UTC; expected finish: 20:19 UTC.
- No pinned coordination issue exists (live GraphQL check); the three discussion-board starter threads have no claims. Claim is local under the supplied sprint instructions.
- Three narrow candidates considered: (1) one additional fixed-reader lift on P112 (overlaps #845/#998/#1133); (2) delivery of asymmetric P104 centres (overlaps #1071/#1125); (3) root-linear masked decoders on P112, its 112 one-line punctures, and the 1260 frame-pair P104 punctures. Choose (3).
- Exact question: can replacing the all-pairs identity by the even-inner-product mask improve a decoder whose two factors remain in the rational/complex span of the root-coordinate columns, with any number of terms?
- Method/domain: exact rank of the 64-column tensor-constraint matrix on P112, all 112 P111 deletions, and all 1260 second orthogonal frames in P112; seek small exact certificates and a written linear-algebra proof. Seed 28 determines deterministic row ordering for witness selection. A stronger universal argument may replace repeated elimination if separately justified.
- Optimistic cost screen: first give mask relaxation every possible implementation saving. If the masked and all-pairs feasible products coincide in this class, it has no copied-information headroom even with free mask enforcement. No physical supplier or new kappa will be claimed from this test.
- Expected deliverable: one scoped obstruction or exact escape example; deterministic standard-library checker, positive and semantic negative controls, source pins, proof/scope/credit, and one focused PR.
- Stop after this specified domain and one evidence-driven pivot at most; reserve the last ten minutes for independent review and packaging.
- Nearest predecessors: DreamingOfClouds #717 (B14 model), PR968 frame-pair decoders, @woklerx #1077 complex extension. They exclude masked identities from their stated coverage; this investigation keeps the root-linear factor restriction explicit. Open PR titles and bodies were searched for masked, root-linear and bilinear overlap; no matching task found in the 786-PR snapshot.

## Evidence-driven refinement

The covariance argument establishes the stronger one-sided condition on exactly the same live-set domain: one factor is root-linear, while the opposite factor and the term count are unrestricted. The independent implementation therefore checks 143,584 local masked-neighbour spans, which is stronger evidence than the initially proposed 64-column tensor rank alone. The general written lemma also covers deletions contained in at most eight orthogonal sets; no enumeration of that larger domain is claimed.

## DONE — local result update

Completed: a one-sided root-linear mask-rigidity theorem for the full claimed domain, plus the stated orthogonal-cover extension. Exact covariance evidence and a separate implementation certify all 1373 domains and 143584 local spans. No new kappa or physical supplier. All relevant local checks and the five selected-record integrity tests pass.

Result: [proof and reproduction](README.md). Publication artifact: [focused branch package](https://github.com/mightyOil/integer-mult-bounds/tree/research/complex-masked-rigidity-seed28/research/complex-masked-rigidity-seed28). The submission handoff records the eventual PR URL. The final overlap check includes the complementary PR1180; its cost theorem is not imported.
