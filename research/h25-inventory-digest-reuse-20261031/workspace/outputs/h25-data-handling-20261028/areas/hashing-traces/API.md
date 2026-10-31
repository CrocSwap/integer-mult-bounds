# Area 6 stable implementation API, revision 1

All functions below are candidate-only. The parent authenticates files before loading them, preserves separate baseline/reference modules and owns all edits to shared drivers, native backends and publication wrappers. No helper or control has been executed in this lane.

## Native observer

`row_interner.make_row_interner()` returns `intern_rows(rows)`. It accepts no rank or result argument. It returns the original input for unsupported domains or an equal exact tuple for eligible rows. It uses a private bounded dictionary; callers must neither expose nor mutate it. It preserves every event through the original exact built-in list collector. No serializer interface change is required.

`row_interner.make_runtime_guard(base_guard_class, intern_rows)` returns a guard class with the original backend guard constructor signature. Pass a fresh helper from the authenticated factory before its first use. The guard factory verifies the original code/environment and initial closure domain, exact empty dictionary, exact sentinel, primitive identities and fixed limits. The returned guard runs every original base check first, then checks actual helper-module and builtin bindings plus helper code, defaults, effective environment and closure cell identities. Empty-cell errors propagate literally.

The parent-derived backend adds a final optional parameter `rank_row_intern=None` to `bind`. Only its original native-success recording block changes:

```python
rows, rank = answer  # unchanged fresh native answer
if rank_calls is not None:
    require(_TYPE(rank) is _INT, "Native rank output type changed")
    observed_rows = rows if rank_row_intern is None else rank_row_intern(rows)
    rank_calls.append((observed_rows, rank))
```

The preceding `native_gram(basis)`, its exception/NotImplemented handling, all counters/returns and `attach_trace` remain unchanged. Do not invoke the helper on literal fallback, direct traced rank, or when recording is disabled.

Finalize the combined base guard (existing guard optimization, trace/native checks and other new additions), create one fresh helper, set `backend.RuntimeGuard = make_runtime_guard(base, helper)`, then call the derived `bind(..., rank_row_intern=helper)`. The exact same helper identity must be passed to the guard factory and bind. No wrapper/function/closure is replaced afterward. The existing private caller lease seals only after all adaptations. The guard factory captures no scientific state and importing this module imports no scientific module.

## Digest snapshots

`digest_snapshot.DigestSnapshot()` creates one authentication invocation's private table. Construct it inside each `authenticate()` call. Its methods are:

- `record_file(name, path) -> hexdigest`: stream a current file in chunks of 1 MiB, then record the digest. No whole payload is retained.
- `record_bytes(name, raw) -> hexdigest`: hash exact bytes already read in this invocation. This supports the small STAGE manifest so its parsed bytes are exactly the hashed bytes.
- `observed(name) -> hexdigest`: retrieve an observed digest for another independent expected comparison. This is not a validation result.

Recording a duplicate logical name rejects. Names/bytes have exact str/bytes admission. There is no module-global cache. Digest table keys are caller-owned canonical publication names; path validation, census, modes and expected identities remain the wrapper's responsibility.

Inside the CODE loop retain the original per-name validation and error order, then record current bytes once and perform the original CODE comparison. For `payload/STAGE.json`, retain the read bytes for later parsing. If CODE omits STAGE, freshly record/read it at the original fixed-STAGE check rather than introducing an early missing-key error; the original payload-protection test must still reject that omission. Perform the fixed STAGE identity check and parse its same bytes, then retain schema/count/runner/coverage checks. Compare the stored payload digests independently against every STAGE expected identity. Retain the payload census and applicable mode checks. Never pass this snapshot into copied-stage inventories, source-module load authentication or a subsequent before/after `authenticate` call: those keep fresh reads. Do not store the snapshot or a PASS in returned authentication receipts.

For `full_driver.inventory`, no helper is needed: compute one local `raw_digest = sha(raw)` after the existing read and reuse it for the existing expected comparison and metadata field. Every invocation and read remains unchanged.

## Parent-run controls

`metadata_controls.run_controls(row_module, digest_module, scratch)` exercises row/type/callback/table-bound/value-pollution controls, helper guard dependency/cell/initial-state controls and current-call digest/hash/read controls. It creates one new scratch directory with a declared 2,097,172-byte binary fixture and replaces its content for the fresh-invocation mutation check. It imports no science.

`native_observation_controls.run_bound_controls(reference, candidate, helper)` takes two fresh environment dictionaries, each with `module`, `binding` (the backend bind result) and `rank_calls`. The candidate must already use the final helper and extended guard; the reference must use its unchanged backend. It compares native/fallback returns, callback errors, ordered prefixes, counters and retained row identity, then tests helper/native drift before work. It never installs a scientific binding. Fresh environments are required for each normal/O run.

`inventory_controls.run_controls(original_inventory, candidate_inventory, scratch)` exercises the actual supplied inventory functions on fresh tiny files, list/string pins, missing/extra/symlink inputs, mode changes and mutation between calls. The mode is returned for the original boundary equality check; the inventory alone does not reject changed modes.

The metadata controls do not exercise actual driver/wrapper census or mode consumers. Parent integration controls must additionally test tiny original/new inventory fixtures and actual publication manifests (wrong CODE/STAGE/fixed identity, missing/extra/symlink/mode/path/schema/count/runner drift) plus fresh copy/load/before-after boundaries. Run the complete original native finite suite and full independent caller comparisons as required by PLAN.md. All control failures and their resource costs remain evidence.
