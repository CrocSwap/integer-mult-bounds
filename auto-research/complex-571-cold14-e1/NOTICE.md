# Attribution and scope

Four verified provider types are offered to every call: PR571's prefix word with twelve multi-cut cold kernels (PR568's unchanged constructor), the same word with forty width-five entrance promotions (PR569's unchanged frame constructor) before those kernels, PR575's plain joint-prefix provider, and PR568's eight-cold provider. A window MILP with an exact per-pattern model chooses the dispatch and a literal owner map. PR583's six source-bound kernel frame coalescences (its unchanged constructor and negative controls) are applied to every PR571-prefix provider word (ck and atm3), followed by two further coalescences that each first move one addition past two commuting additions (package code/build_gate_moves.py, extending PR583's constructor); a final hyperplane_end step (package code/build_hpe.py) then runs 46 single-gate cleanups h -= p right after part B at the dim-8 join U of their registers, so 46 width-8 entering helpers per call end at U with width 7; each such gate commutes with every earlier cleanup gate on its registers (for 8 of them the partner's one earlier gate x -= p only reads p), and the reordered program is replayed exactly. A window MILP (exact windows, RINS around an LP vertex) gives the dispatch ck 45 / atm3 21 / jp8 6 and the literal owner map.

Pinned external sources (unchanged; `verify.py` checks their manifests and every file it uses):
- PR568 (`research/complex-multicold`, commit `71c99ac935a33bb7b59a1b4a7af8725a939b0b90`).
- PR571 (`research/structural-gain`, commit `b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3`).
- PR569 (`research/larger-gain`, commit `897213a855b7fb8a1b8b0e552a2f5c42e6c1b326`).
- PR575 (`research/complex-joint-prefix`, commit `eac6f7e378ab622dac50a2fd4b7ef6eab014de44`).
- PR583 (`research/kernel-frame-coalescing`, commit `89be768f0157f5a3d8e4db69cf1748768605eac9`).

Provider construction is described as typed steps in `data/SPEC.json` (`build`); `verify.py` runs only allowlisted step types with their paired omission audits and checks every input and output content hash. `code/` holds the spec-driven global admission scripts adapted from PR571's `frontier-composition/global-code/` (OpenAI Codex assisted, Apache-2.0): every expected value is read from `data/SPEC.json` and compared only after independent recomputation. `code/generated_identity.py` and `code/generated_identity_controls.py`, and the decompressed-content artifact identities in the bind, audit, invoice, assembly and phase-timing scripts, are taken unchanged from PR586 by chafreaky (`research/promoted-kernel-coalescing`, commit `4846fee5b06af770e9b3a10c36200f673d656725`, OpenAI Codex assisted, Apache-2.0), including its proof-content and reference/metadata mutation controls; the normalization of descriptive width metadata after frame changes follows the same PR.

The owner map was nominated by a HiGHS window MILP (adapted from PR569's `global/nominate_width7.py`) with lazy cross-time Hall cuts; it is not an admission dependency.

Prepared by Claude Code (Anthropic) research agents. Apache-2.0 applies; LICENSE is included. All notices, licenses, source pins and AI disclosures of the pinned sources and their ancestry are retained in those packages and are not replaced by this notice. All inherited conditional assumptions remain conditional.

**This package (complex-571-cold14, DreamingOfClouds).** It starts from PR601 (jeremykothe2, `research/complex-571-hpem46`, commit `529ab7dcb59d5ea7a5798e9e06cf5b3aee8a1550`). Everything above is kept unchanged except the following:
- every provider chain (ck, atm3, jp8) gains the typed step `cold_end` (`code/build_cold_end.py`, `code/cold_end_controls.py`; recipes `data/recipes/*-cold_end.json.gz`);
- the generalised native chain and the global admission scripts accept cold helpers that end below FULL (with `0:U` wrappers), a refactored exact cleanup, and check the wrapper order;
- `data/PLAN.json` / `data/OWNERS.json.gz` (dispatch and literal owner map) come from a relocate/swap/ejection-chain/provider-flip annealing search started from PR601's map (not an admission dependency);
- `data/SPEC.json` holds the expected values, recorded by a discovery run and then checked by a strict run.

The cold-end construction (a row-plus-column cone condition for low-frame ends, a rank-0 dirt-spread premix and multi-gate lower-frame cleanup) builds on PR591 / PR592 / PR593 / PR601 (jeremykothe2) and our PR599 (Lean: multi-gate and cold hyperplane-end tails). DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Build on this at your own risk.


**Controls revision (E1Reviewer fixes).** `code/cold_end_controls.py` pins the assertion message each mutant must fail at. A dropped lower-frame gate now removes its `early_cleanup` entry too, so it fails the exact endpoint replay instead of the duplicate-index check. The "end dropped" mutants are relabelled as profile-pin controls, since the mutated word is a valid FULL-ended word. The entering-end mutants run on every entering end; there are 26 controls in all. `code/hpe_audit_and_transport.py` adds a guard: the zero-frame precondition and compensation may not touch an entering helper. It also adds messages to two assertions that had none, the literal-cleanup check and the profile check. All of these are inert for words without low-frame ends.

**This package (complex-571-cold14-e1, jeremykothe2).** It is PR604's `complex-571-cold14` (DreamingOfClouds) with ColdSupply's cold-end recipes and entering low-frame-end controls, a free dispatch (jp8 ×68, atm3 ×4) and a literal owner map from an exact per-time-Hall window MIP. All other construction, code, controls and proofs are PR604's and earlier contributors', unchanged.
