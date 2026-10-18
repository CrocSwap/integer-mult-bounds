# Local task card

- **Task / scope:** `complex-masked-decoder`, catalogue scope `2a6f2c726b78f9ae7d26`, refined to the two-sided, eight-term even-mask Jacobian at the canonical P112 decoder. Selector nonce `c4cb3fadd3712193711993a2fb0dac76`, priority revision 1.
- **Base:** `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` (current main fetched 2026-10-13). Selected record SHA256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`; selected conditional kappa `836330098538459/500000000000000000`.
- **Question:** For the 112 E8 root lines outside one orthogonal frame, do the linearized diagonal/orthogonality constraints admit any directions beyond global factor-basis changes and reciprocal per-port scalings?
- **Changed restriction:** Both decoder factors may leave the live root-coordinate column space. Unlike PR1191, neither factor is required to remain root-linear. Exactly eight terms and a neighborhood of the canonical factorization are retained.
- **Method / domain:** Independently construct rational E8 roots, form all ordered even-inner-product mask equations, compute the exact Jacobian rank via a certified nonzero modular minor and explicit rational nullspace generators. Single P112 domain, no heuristic sweep or all-puncture claim.
- **Hypothesis / falsification:** Predicted nullity 175 (64 factor-gauge dimensions plus 112 reciprocal scalings, minus their one-dimensional overlap). A larger kernel falsifies rigidity; report the additional exact directions rather than infer global nonexistence.
- **Budget:** At most 30 minutes for a decisive rank experiment, then at least 25% of the session for separate verification and packaging. At most one bounded pivot.
- **Optimistic cost gate:** A pure row scaling preserves each factor-column support; a basis change yields an existing all-pairs root-linear decoder before scaling. If these exhaust the local family, mask relaxation provides no new local copied-information mechanism. No scalar savings, physical supplier invoice or new kappa are claimed.
- **Nearest overlap:** PR968/1077 prove eight-term all-pairs copy floors. PR1180 (`75b408646d558147a4eb250fc407d1fbfcb8df4e`) treats overcomplete all-pairs root-linear factors. PR1191 (`640b43bb13d3d476a2d83b74ef0d33f14d1b5711`) proves one-sided masked-to-all-pairs rigidity. Their open PR bodies were read. This task instead checks the first-order two-sided rank-eight boundary, with explicit non-all-pairs scaling examples.
- **Overlap evidence:** Read discussion 1163 and all five active discussions including 1166/1167/1202; scanned titles and bodies of 814 open PRs including drafts, plus local research and the ledger. Public coordination posting has not been specifically authorized, so this card stays local.
- **Predecessor credit:** DreamingOfClouds (PR717/595 decoder and cost model), themilkman216 (PR968), woklerx (PR1077/1180), Philipp / mightyOil (PR1191), Joel Pulikkan / GamingPuzzled (PR620), icekylinx (P112), and the retained supplier lineage. Source pins and precise delta will accompany the result.
- **Artifact:** One scoped research directory, exact checker, deterministic evidence, written mathematical scope, and independent verification. Planned command: `python3 -I -B research/p112-masked-tangent-audit/verify.py`.
- **Disclosure:** Substantial OpenAI Codex assistance, including separate AI review. Apache-2.0. No human peer review or complete multiplication theorem claim.

## Outcome

Both exact computations matched rank 1617 and nullity 175. A graph-based
closedness argument upgrades the tangent result to classification of the
coordinate connected component, without another search or a second task.
The final question is therefore whether an entire continuous exact eight-term
path can escape the all-pairs orbit up to reciprocal row scalings; it cannot.
See PROOF.md and VALIDATION.md. No construction target was silently lowered.
