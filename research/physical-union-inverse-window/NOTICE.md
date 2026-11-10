# Attribution and exact-source provenance

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance in
research, proofs, physical implementation, integration and verification.
The transaction author, exact-source producer and independent source-aware
reviewer were separate AI researchers. Independent checking is scoped in
`INDEPENDENT-REVIEW.md`; no human or proof-assistant acceptance is implied.
New work uses the repository's Apache-2.0 license.

Credit is retained for Vlado Vojdanovski and the original construction
contributors, Jose Manuel for the common rational Reference/core work,
Mason Hale for interval arithmetic, and the contributors identified in the
source packages and their notices. Generic predecessor mechanisms are
inherited rather than claimed as new here.

- CrocSwap/integer-mult-bounds#4100 supplies the Gaussian factorization,
  union schedule and outer construction. Its current rational Reference and
  proof inputs are pinned at canonical base
  `7c49fe32c55de02c2c873655c804b16e4c3fef0a` in `SOURCES.json`.
- CrocSwap/integer-mult-bounds#4327 supplies the record-level union
  head-travel audit. `retained/pr4100-union-head-travel__verify.py` is
  exactly canonical blob `b308e7a111c174e414b76188dcdda9a61b7b0ff0`.
  `schedule_hook.py` makes three checked in-memory fixture substitutions,
  documented in `PROOF.md`; the retained file itself is unchanged.
- CrocSwap/integer-mult-bounds#4583 supplies the explicit header ABI.
  `retained/union-header-encoding__header.py` is exactly canonical blob
  `424699d49c57e762ca5f04091bfab8f8d145d14c`. Its host encoder is the
  prepared-input fixture, not a claimed literal global emitter.
- CrocSwap/integer-mult-bounds#4376 and
  CrocSwap/integer-mult-bounds#4645 already prove short-field movement and
  ledger absorption. CrocSwap/integer-mult-bounds#5275 concerns a historical
  structured exponent point, not the current dense balance. Open
  CrocSwap/integer-mult-bounds#6626 optimizes header width and supplies no
  physical payload caller.
- CrocSwap/integer-mult-bounds#4186 supplies completed-product residual
  reasoning and seven-product guards. CrocSwap/integer-mult-bounds#5059
  supplies physical inverse-page preparation and the exact rounded two-pass
  function. Canonical numerical/runtime source bodies remain unchanged.
- `retained/seven_product.py` and `retained/fast_boundary.py` are exact
  copies from CubeJerry/integer-mult-bounds commit
  `f821cba68f44048e70e78afb75603ed4dde99f11`, paths
  `research/physical-seven-product-matrix/{seven_product.py,fast_boundary.py}`.
  `DEPENDENCIES.json` records their Git blob and SHA256 pins. No upstream
  PR number is assumed for that published predecessor. This branch starts
  from canonical main and retains only those two component files.
- `reference_source.py` reuses unchanged
  `research/shrinking-reference-halo/source.py` from CubeJerry/integer-mult-bounds
  commit `a99c4dce9f6bf1972b13f0f239e082ac70a9e5e8`. Its SHA256 is
  `20c0fb2e4aa95de976ef6ce74ded4bf1cb9073732eca7eda8f61e45d239afa2c`.
  Executed original numerical bodies are separately pinned in
  `SOURCES.json`; the adapter changes import bindings only.
- CrocSwap/integer-mult-bounds#5499 and
  CrocSwap/integer-mult-bounds#5506 supply a different two-active-column
  classical refinement and normalized supplied-factor return. Their old-H
  fixture is not identified with this current Reference. The growth result
  in CrocSwap/integer-mult-bounds#5500 is not silently substituted for the
  current-reference admission in `NUMERICS.md`.

The source producer and numerical proof are retained from the separate
source researcher. The independent oracle, transport, off-block and partial
failure controls are retained from the separate reviewer. `TASK.json`
preserves the original priority card and records the narrower scope.
No merged or closed research contribution is treated as scientific acceptance
of this result. **No new κ.**
