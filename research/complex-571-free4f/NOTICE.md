# Attribution and scope

Four verified provider types are offered to every call: PR571's prefix word with twelve multi-cut cold kernels (PR568's unchanged constructor), the same word with forty width-five entrance promotions (PR569's unchanged frame constructor) before those kernels, PR575's plain joint-prefix provider, and PR568's eight-cold provider. A window MILP with an exact per-pattern model chooses the dispatch and a literal owner map.

Pinned external sources (unchanged; `verify.py` checks their manifests and every file it uses):
- PR568 (`research/complex-multicold`, commit `71c99ac935a33bb7b59a1b4a7af8725a939b0b90`).
- PR571 (`research/structural-gain`, commit `b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3`).
- PR569 (`research/larger-gain`, commit `897213a855b7fb8a1b8b0e552a2f5c42e6c1b326`).
- PR575 (`research/complex-joint-prefix`, commit `eac6f7e378ab622dac50a2fd4b7ef6eab014de44`).

Provider construction is described as typed steps in `data/SPEC.json` (`build`); `verify.py` runs only allowlisted step types with their paired omission audits and checks every input and output content hash. `code/` holds the spec-driven global admission scripts adapted from PR571's `frontier-composition/global-code/` (OpenAI Codex assisted, Apache-2.0): every expected value is read from `data/SPEC.json` and compared only after independent recomputation.

The owner map was nominated by a HiGHS window MILP (adapted from PR569's `global/nominate_width7.py`) with lazy cross-time Hall cuts; it is not an admission dependency.

Prepared by Claude Code (Anthropic) research agents. Apache-2.0 applies; LICENSE is included. All notices, licenses, source pins and AI disclosures of the pinned sources and their ancestry are retained in those packages and are not replaced by this notice. All inherited conditional assumptions remain conditional.
