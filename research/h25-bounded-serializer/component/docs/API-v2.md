# Area 3 implemented API, revision 2

Status: source and finite-control implementation authored; AST validation only. No scientific/module execution, compilation, control execution or timings by this lane. V1 proposal/API/control bill remain unchanged under reviewer snapshot. Parent admitted the following regular-file contract; this document supersedes the unresolved API points in v1.

## Parent integration

Place this lane on the isolated stage's module path and import `bounded_serialization`. After loading the authenticated original comparison module, construct:

```
writer = bounded_serialization.make_writer(
    comparison.write_scientific,
    comparison.canonical,
    comparison.EXPECTED,
    comparison.require,
    batch_bytes=1048576,
    batch_rows=1024,
    copy_bytes=1048576,
)
```

The return is `writer(output, result, witness, rank_calls)`, returning exactly the original scientific receipt structure. Select it at the existing side-serialization phase in the candidate arm only. The reference arm retains its original function/module/process. Keep the existing eager witness, typed full return, certificate, stdout, complement checks and original source checks unchanged. The serializer owns only result.json, witness.json and rank-trace.json in the supplied side-observation directory.

Create the writer and finish all closure/guard assembly before final sealing. `writer._h25_serialization_bindings` is a tuple of `(owner, attribute_name, captured_object)` entries for actual JSON and _json modules/class attributes. Some entries are classes or Python functions, so this tuple is NOT the native-only entry protocol. `writer._h25_serialization_faults_enabled` must be False in a complete caller. The writer checks these identities plus original function code/default/closure identities and relevant original global bindings on every call. Parent must separately authenticate source and actual runtime binary custody; upstream CPython source is not a binary attestation. Expected-receipt mutation is rejected on every call. There is no scientific PASS cache.

`writer.last_operation` is the supplemental JSON-safe operational record. Read it after success, or in the parent's failure handling if desired; do not add it to the frozen scientific receipt. It includes status, phase, staging path, configured bounds, batch count/largest batch, per-file stage/hash/copy byte counts, original/copy digests, cleanup progress and bounded error metadata. A successful record's stage path names the now-removed private stage. Literal fallback records status only. This mutable reporting attribute is not consulted by computation or acceptance.

## Admission and literal fallback

Exact known witness dictionaries, exact list/tuple arrays and scalar leaves, exact rank list/event tuples/integers, depth and byte bounds are freshly checked. Output must be an exact local Path whose destination directory and preexisting final files fit the regular-file contract. Unsupported argument/object domains invoke the untouched original function with untouched arguments before candidate writes or conversion callbacks. The supported fast caller is source-checked, single-threaded and frozen; arbitrary concurrent mutation and arbitrary file-like sinks are not promised. Missing/nonregular/symlink destinations use original behavior. There is no fixed-word integer cap; original Python decimal conversion and digit-limit exceptions remain.

## Accepted publication and failure semantics

Generate all three private staged artifacts and hashes, compute original rank counts, and require the original EXPECTED equality before changing a final filename. Copy into regular binary `wb` files in original result/witness/rank order. Each bounded write must return precisely its requested length; otherwise raise OSError without retry. Synthetic short-return behavior intentionally differs from the original caller, which ignored its single write's return value. Actual OS failure-prefix length may differ with chunking; no stronger equivalence is claimed.

Every copy rehashes/counts its existing read stream, checks source fstat/path identity/size/timestamps before and after reading, and checks final size. After streams close, require copy digest/count equal to the accepted staged values. No additional full read is performed. A rejected copy can leave its corrupt/partial final visible, earlier finals intact and later names absent. It cannot return a success receipt or remove its failure evidence. Successful stages are removed only after all copies pass. Actual IO exceptions propagate; close/manifest failures do not mask an existing primary exception. Failure manifests remain inside the unique private stage, bounded at 64 KiB.

## Controls

Import `serialization_controls` and call:

```
receipt = serialization_controls.run_controls(comparison, fresh_external_control_directory)
```

This must run only in the parent's guarded serial queue after G1, once per required normal/-O finite arm. The supplied comparison module is the unchanged reference. Controls reconstruct separate fixtures, clone its exact writer code into separate globals only to supply finite EXPECTED values, and never edit the imported reference module. All complete scientific original/candidate comparisons still run in separate processes. Controls preserve raw failure files and write controls.json. They start no compiler, scientific import, complete caller or timer themselves.

The private `_make_writer(..., fault=...)` test seam exists exclusively for injected finite IO controls. Production `make_writer` has no fault argument. Faults permit deterministic errors/short returns/content corruption while preserving actual regular files; they are not a production file-like API.

Full expected bytes/hashes remain those in PROPOSAL.json: 527-byte result, 58,143,622-byte witness, 2,674,272-byte rank trace; 59,959 rank calls and 252 distinct matrices. Future full results must establish all of them afresh. No measured gain exists yet.
