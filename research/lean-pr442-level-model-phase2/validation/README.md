# Phase 2 validation receipts

`local-phase2.json` records a full **PASS** on source commit
`730fbac0e82affa1dc62e17310fac801b9588691`. The four new modules were
rebuilt from clean Phase 2 artifacts. Frozen Phase 1 and invocation dependencies
were already compiled from their unchanged pinned sources in this workspace;
they were not cleared or reverified as a separate Phase 1 task. Mathlib cache
setup returned HTTP 403 locally, so its required targets were built from the
pinned source. Cache/setup time is separate from the measured verifier run.

Measured local results:

* Full verifier: **76.954 seconds**.
* Ordinary `lake build`: **8.067 seconds**.
* Complete permanent axiom audit: **10.483 seconds**, all **116** named new
  declarations, containing **92** theorem statements. Only `propext`,
  `Quot.sound`, and `Classical.choice` occur.
* Eight controls: **51.320 seconds** including separate candidate typechecks.
  All 16 original/mutant propositions typecheck, all eight originals compile,
  and all eight mutants fail with explicit semantic false diagnostics. The
  ambient-complement mutant reduces to `1 = 0`; the omitted-exterior mutant
  reduces to `0 = 1`.
* Independent Python corroboration: **2.657 seconds**, 2,640 exact rational
  geometry checks, 960 owner joins and six rejected mutations. This is
  external evidence, not Lean proof or successful CI.
* All **542** protected files and six compressed/uncompressed input hashes
  pass. The Phase 1 package, its 38 statements and its receipt are unchanged.
* Lean **4.21.0**, Mathlib `308445d7985027f538e281e18df29ca16ede2ba3`, default
  new-source settings, no environment overrides; inherited stack limits remain
  `[8388608, -1]` before and after the run.

The receipt fingerprints the executable, source manifest, all dependency
sources and runtime artifacts (including frozen Phase 1 and InvocationProof).
It applies to those exact fingerprints. This receipt's following commit adds
validation documentation only, outside the proof-source manifest; the compiled
Lean files and verifier manifest are unchanged.

`local-phase2-initial-control-failure.json` preserves the earlier full run on
`2fa8307598c710fa3279cdac89c99e05e5a9d9d0`. Its clean build and 116-declaration
audit passed in 9.311 and 11.063 seconds, but its first positive frame control
hit the default recursion limit. Its status is **FAIL**; that error was not
accepted as a rejected mutation. The control harness was corrected using
certified joins and symbolic outside-coordinate lemmas before scalar decisions,
without changing theorem sources or raising limits. Draft compilations before
these measured passes are not treated as proofs.

The dedicated Phase 2 Actions workflow independently runs the same verifier and
uploads its receipt as `pr442-level-model-phase2`. Its run status and artifact
are the CI evidence; the local PASS alone does not establish successful CI.
The published Phase 1 run `38482036983` establishes the frozen baseline only.
`PASS_SOURCE_CHECK_ONLY` is also distinct from a proof build. The independent
source review's earlier receipt is `source-review.json`.
