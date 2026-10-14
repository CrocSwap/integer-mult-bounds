# Phase 2 validation receipts

Receipt statuses distinguish source-only checks, ordinary Lean compilation,
axiom audits, semantic mutation controls and independently executed CI.
`PASS_SOURCE_CHECK_ONLY` is not a proof result. A full verifier `PASS` applies
to the manifest, dependency sources and runtime artifacts recorded in that
receipt. `freshNewModules` reports whether new oleans existed before that run.

The Phase 1 receipt remains in the frozen dependency and has not been replaced.
Its successful CI establishes the published baseline only.

Local and CI measurements will be recorded after validation completes. No
successful Phase 2 compilation or CI result is asserted by this scaffold.
