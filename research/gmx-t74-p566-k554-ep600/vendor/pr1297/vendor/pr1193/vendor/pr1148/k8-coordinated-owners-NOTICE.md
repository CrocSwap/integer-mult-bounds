# Attribution and scope

Prepared for Thomas DiFiore with OpenAI Codex assistance, October 13, 2026.
Licensed under the repository's Apache-2.0 license.

This contribution changes the whole-helper ownership map for the circuit from
Jeremy Kothe's PR1018 (`eac7547cb191f875d5f5ea5f9bbb1d2b8c51c4ef`). The
eight no-helper mutable-source cells, R480 circuit, frame optimization and
construction controls come from Jeremy Kothe and the credited contributors to
PR1005. The seven additional triangle slots come from PR1018 using Rohan Arun's
PR987 search and NewBArch's PR869 builder. None of those circuit improvements
are claimed as new here.

The starting ownership map is G44Pack3's K8c8, descended from chafreaky's PR685
and PR741 maps through G44Pack's relabeling and width changes. This package adds
coordinated complete-call reassignment by grouped integer packing, with
explicitly serialized owners and an unchanged independent admission verifier.

The separate all-replica upper bound adapts jon314159's PR942 arithmetic
implementation and proof, using chafreaky's PR795/890 signed-dual prices. Its
new contribution is the application to PR1018's changed local profile and
helper inventory. The two rational numerical engines retain their upstream
authorship. `independent/UPSTREAM.json` records the source file and hash.

All construction, controller, spectator, native phase, finite invoice, exact
moment and outer-transfer implementations retain their upstream authorship
and notices. The runtime copies PR1018's verifier files byte for byte. It
changes the owner nomination, its derived PLAN fields, and expected-value SPEC.
The original packages remain unchanged.

The bit supplier is the unchanged PR589/PR555 punctured-star construction;
this run reprices its pinned profile and reruns its admission controls. It does
not rebuild the bit circuit. Earlier complex ancestry is inherited through the
pinned PR741 initial word and PR622/PR558 reviewed parent artifacts. The run
freshly rebuilds the k8 leaver circuit, all later layers, and the seven slots.

This is a conditional finite construction, not an unconditional integer
multiplication theorem. All-size compilation, common-label and mutable-source
realization, whole-call hosting, precision/tape, analytic transfer and bit H1–H5
assumptions remain. No independent human peer review is claimed. Optimizer
outputs and floating relaxations are discovery evidence, not admission proofs.
