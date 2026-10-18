# Source reconstruction, full replay and recorded evidence

The original local run completed fresh native replay for both changed providers
and all seven source-bound admission stages. The terminal statuses were
`PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE` and `PASS_RELEASE`.
The conditional modern outer value was exactly
`0.001730394391813963415120 - 10^-46 - 10^-70`.
The inherited all-size assumptions remain; see the package's main proof.
The published full wrapper has subsequently completed end to end as a separate
local run, described below; its receipts do not replace the original evidence.

This is a lean public derivative of that evidence. It deliberately omits the
complete generated source, runtime and native-cache archives. Their original
hashes and sizes are recorded in `ARCHIVE-OMISSIONS.json`. Source and runtime
manifests, selected native/runtime metadata, all seven stage summaries and
relevant logs are retained. No archive payload is authenticated by the public
summary check.

## Public summary check

```sh
python3 -B research/staged-release-retiming-t530/full-admission/check_recorded_summary.py
```

This standard-library check verifies public file hashes and internal recorded
status, exact κ/profile, native-versus-retained-reuse, seven-stage, physical and
prefix references. It returns `PASS_PUBLIC_RECORDED_SUMMARY_BINDINGS`. It is
not the private capsule's complete archive checker and does not rerun native,
owner, controller or outer computations.

`python3 -B research/staged-release-retiming-t530/full-admission/test_recorded_summary.py`
checks four repinned malformed summaries: missing fresh native stages, missing
providers, empty finite-invoice predicates and a changed certified endpoint.
Each is rejected at its corresponding content predicate.

Our workspace prefix in execution metadata is replaced with
`$RESEARCH_WORKSPACE`. `PUBLIC-PROVENANCE.json` records original SHA256, public
SHA256 and the normalization rule for each retained evidence file. Original hash
references are compared as recorded historical metadata, never falsely to the
normalized bytes. The original unnormalized bytes are not all supplied here.
Upstream source bytes, source manifests, words and mathematical fields are
unchanged. The original local capsule was left untouched.

`evidence/DERIVATION.json` preserves the historical PREPARED construction status.
It predates the completed native and full admission receipts. The older
supplier-only κ `0.001727405299371541` is a different layer: the original final
release binds the modern outer κ to the same supplier complex endpoint/profile.

## Fresh source reconstruction

From a full Git checkout containing canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`:

```sh
python3.12 -B research/staged-release-retiming-t530/full-admission/reproduce.py \
  --repo . --work /tmp/fresh-retiming-source --materialize-only
```

This path was actually run from the public layout. It exports exactly the 540
ancestor paths in `MAIN-INPUTS.json`, checks every SHA256, materializes the
predecessor with its unchanged authenticated materializer, appends the retiming
stage and runs the old and new reconstruction reviews. It reproduces all 654
source files and source manifest
`fb47533a401d1d13719be8b9aab91fe5313931ca62d40dba336eab6a96275aa0`.
`evidence/PUBLIC-SOURCE-REBUILD-RESULT.json` records that fresh check.
The checkout HEAD may be newer than the ancestor. No network or unmerged PR
Git objects are needed: the required PR3626 bytes at
`659fd5e7064d9466b668d7188cbb013b333a415a` are vendored with exact input pins.
Only its consumed source/owner closure is retained, with contributor notices.

## Complete scientific replay

From the repository root, run the full wrapper without `--materialize-only`
or an imported `--allocation`:

```sh
python3.12 -B research/staged-release-retiming-t530/full-admission/reproduce.py \
  --repo . --work /tmp/fresh-retiming-full
```

This runs fresh changed native providers, reconstructs all 1,946,160 literal
owner roles and executes the complete original admission. Use Python 3.12 with
numpy 2.5.4, scipy 1.18.1, sympy 1.14.0, mpmath 1.3.0,
gmpy2 2.3.2 and psutil 7.2.2. Assertions must be enabled. All output goes to a
fresh external work directory. The original scientific driver took about 20.3
minutes, plus native generation. The unchanged retained parent and two retained native
chains are authenticated and reused; this is not a fresh retained bootstrap.

The complete scientific driver ran successfully before publication, using this
same 654-file source. The published wrapper has now also run end to end at
commit `abc12f62e4fe9bfcb2e33c84703253c918668351`, in a fresh external work
directory with a regenerated allocation and no wrapper code fix. All seven
wrapper stages and all seven nested admission stages exited 0. It reproduced
the same source manifest and exact κ, ending in
`PASS_RETIMER_T530_COMPLETE_CONDITIONAL_RELEASE` and `PASS_RELEASE`.
All 295 tracked package files remained unchanged during the run.

The full-wrapper run took **1,271.668979667 seconds (21 minutes 11.67 seconds)**
on local macOS 27.0 arm64, Python 3.12.14 and the dependency versions above,
from 2026-10-18 12:37:09.414302 to 12:58:21.088357 UTC. This was a new work
directory in an already provisioned local environment, not an independent
external or clean-environment reproduction. Both changed native providers were
freshly replayed; the retained parent and two unchanged native chains remained
authenticated reuse. Runtime source patches and exact native/admission driver
copies are retained for inspection; no scientific gate was removed.

## Separate public full-replay evidence

[PUBLIC-FULL-REPLAY.json](../PUBLIC-FULL-REPLAY.json) indexes the new run.
Its selected records and original-to-public normalization hashes are in
`fresh-replay/`; the original scientific receipts, source-only reconstruction
receipt and bounded `PUBLIC-VALIDATION.json` remain unchanged. Check the new
recorded evidence and its rejection controls from the repository root:

```sh
python3 -B research/staged-release-retiming-t530/full-admission/fresh_replay_evidence.py check \
  --root research/staged-release-retiming-t530/full-admission/fresh-replay
python3 -B research/staged-release-retiming-t530/full-admission/fresh_replay_evidence.py controls \
  --root research/staged-release-retiming-t530/full-admission/fresh-replay
```

These are recorded-evidence checks; they do not rerun the scientific pipeline
or authenticate omitted archive payloads. Use `reproduce.py` above for a fresh
full computation. The original public summary checker retains its narrower
historical scope.

## Open next questions

- Reproduce the public full wrapper independently in another clean environment
  or platform. Its complete path has now passed locally; an external run would
  test dependency and platform portability. First provision the stated
  dependencies, run the full command in a fresh directory, and compare the
  mathematical payloads, source manifest and endpoint. This remains separate
  from the inherited general theorem assumptions.
- Evaluate the retiming with another chronological allocation only after its
  full owner/controller/prefix invoice is available. Start by comparing helper
  interfaces and exact local profiles; no untested composition is claimed.

The source and credit lineage includes Ross Richardson/PR3605,
hexapode/PR3626, dcharb78/PR3133, Jeremy Diviney/PR3148,
Marius-Paul Dumitrean/PR2979 and all retained notices. The new retiming and
integration used substantial OpenAI Codex assistance. Apache-2.0 applies.
