# Source reconstruction and recorded full-admission summary

The original local run completed fresh native replay for both changed providers
and all seven source-bound admission stages. The terminal statuses were
`PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE` and `PASS_RELEASE`.
The conditional modern outer value was exactly
`0.001730394391813963415120 - 10^-46 - 10^-70`.
The inherited all-size assumptions remain; see the package's main proof.

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

Omit `--materialize-only` to run fresh changed native providers, reconstruct
all 1,946,160 literal owner roles and execute the complete original admission.
Use Python 3.12 with numpy 2.5.4, scipy 1.18.1, sympy 1.14.0, mpmath 1.3.0,
gmpy2 2.3.2 and psutil 7.2.2. Assertions must be enabled. All output goes to a
fresh external work directory. The recorded full driver took about 20.3 minutes,
plus native generation. The unchanged retained parent and two retained native
chains are authenticated and reused; this is not a fresh retained bootstrap.

The complete scientific driver ran successfully before publication, using this
same 654-file source. The public wrapper's materialize-only path was tested;
its full end-to-end wrapper has not been rerun. The public summary checker is
intentionally a smaller claim. Runtime source patches and exact native/admission
driver copies are retained for inspection; no scientific gate was removed.

## Open next questions

- Independently run the public full wrapper from a clean environment. This
  checks environment and export portability beyond the tested source rebuild;
  first provision the stated dependencies and run in a fresh directory. It
  requires time for the full pipeline and remains a separate review action.
- Evaluate the retiming with another chronological allocation only after its
  full owner/controller/prefix invoice is available. Start by comparing helper
  interfaces and exact local profiles; no untested composition is claimed.

The source and credit lineage includes Ross Richardson/PR3605,
hexapode/PR3626, dcharb78/PR3133, Jeremy Diviney/PR3148,
Marius-Paul Dumitrean/PR2979 and all retained notices. The new retiming and
integration used substantial OpenAI Codex assistance. Apache-2.0 applies.
