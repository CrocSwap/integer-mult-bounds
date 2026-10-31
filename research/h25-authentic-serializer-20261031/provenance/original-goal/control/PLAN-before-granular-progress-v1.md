# Verification data-handling plan

Address the six audited areas, starting with the inner runner's unbounded log reads. Use parallel GPT-6.1-sol agents at high for source investigation, implementation and independent review, with one parent-owned queue for compiler work, scientific execution, resource tests and measurements. The user explicitly authorized this plan, swarm and completion goal on 2026-10-28.

## Baseline and preservation

The comparison baseline is PR6029 publication `e05aad954689d0ee21baff19b4674f1fcb2e838f`, package `research/h25-bookkeeping`, in its complete combined native configuration. Local immutable stage v4 is `outputs/h25-bookkeeping-swarm-20261028/stages/v4`, SHA-256 `558eebbc1dc65e42bbcb3ffd9973f8bc86641a3539493ecc1d53d8077c39cdbc`. The previous performance goal is complete; its times, source and hosted CI are historical evidence, not new measurements or current upstream status.

Preserve every existing source, raw run, failure, receipt, archive and original thread. Synced `sources/` remains read-only. Author new candidates in this round; do not patch the prior publication checkout or immutable stages. Authenticate a separate reference closure before any run. Keep original and candidate computations in distinct instances/processes; never share mutable answers or saved validation PASS results between independent paths. Mathematical streams, unrelated feeds and automations remain paused.

Retain exact certificate/stdout/types, ordered witnesses/rank/complement bytes and prefixes, call coverage, fallback/error behaviour, source/ownership checks and runtime freshness. Failure artifacts remain visible. Published source snapshots stay immutable; any repaired implementation receives a new stage/version and keeps failed evidence.

## Parallel lanes and ownership

| Area | Agent | Owned directory | Initial deliverable |
|---|---|---|---|
| 1 Log handling | `data_log_guard` | `areas/log-handling/` | Minimal bounded-read fix and real file/process controls; first execution priority |
| 2 Construction memory | `data_construction` | `areas/construction/` | Reuse exact support unions; prove construction-index lifetime before retirement |
| 3 Witness serialization | `data_serialization` | `areas/serialization/` | Bounded serializer preserving exact bytes and final-file failure semantics |
| 4 Evidence retention | `data_retention` | `areas/retention/` | Immutable content-addressed archive, manifests and exact restoration; no existing-file deletion |
| 5 Cache validity | `data_cache_contract` | `areas/cache-validity/` | Mutation-safe cache contract and independent negative controls |
| 6 Hashing and rank observations | `data_digest_trace` | `areas/hashing-traces/` | Same-call digest reuse and bounded/reused immutable observation metadata |
| Independent review | `data_review` | `review/` | Source/contract gates, interference review and final evidence audit |
| Parent | Main agent | `control/`, `integration/`, `stages/`, `runtime/`, `validation/`, `publication/` | Shared interfaces, all execution, integration and delivery |

All agents use the explicit project workspace for filesystem commands. They are not alone in the workspace, may not revert others and may edit only their owned directories. Workers do not import/execute scientific modules, compile, decode large scientific corpora, run timings or publish. They may inspect source, read bounded existing receipts, AST-parse source and prepare controls. Research and disjoint implementation run concurrently after their gates; shared original-module transformations belong to the parent.

Reuse one parent inventory, run index and upstream refresh. Batch independent bounded reads. Reuse source-review results only while exact source digests and dependencies match. Refresh external state at the publication boundary; avoid repeated unchanged polling. This does not remove any live scientific check or declared cold cost.

## Area-specific work and completion gates

### 1. Fix bounded log handling first

The inner runner currently reads complete stdout/stderr into memory before its final output-cap check. Author a new runner revision that checks file sizes before materialization, stream-hashes complete retained evidence with bounded memory, emits only bounded previews and checks final sizes/counts after streaming. Preserve exact byte hashes/counts, STOP reasons, stderr rejection, all failed outputs, unique evidence directories, process cleanup and resource limits. The existing outer publication guard is a useful source precedent, not a reason to skip inner-runner repair.

Before other numerical work, independently review and run normal output, binary output, stderr failure, nonzero exit and bounded oversized/fast-exit controls. Verify STOP on oversize and bounded parent memory, including the post-exit path. Keep all adversarial fixtures small and predeclared. Integrate the fixed runner into this round's actual execution path; a library with no consumer is insufficient.

### 2. Reduce construction memory and duplicate unions

Compute each exact `sa | sb` union once and reuse that immutable value for the `(kind, mask)` lookup key and support storage. Preserve node identity/order, lookup semantics and every arithmetic assertion. Separately establish when construction is permanently finished. Retire or release the deduplication index only within a proven frozen-caller phase; preserve behaviour for APIs that can resume construction. Do not delete lookup state merely because it looks unused in one receipt.

Compare complete graph/witness bytes against the unchanged reference and test duplicate additions, kind distinctions, invalid/callback-bearing domains and the phase boundary. Measure memory after construction and the full-process peak; do not infer savings from object counts alone.

### 3. Bound witness serialization memory

The retained witness is 58,143,622 bytes; current encoding materializes large complete JSON buffers. Design bounded output using the exact existing sorted-key ASCII schema, integer representation and ordered collections. Investigate C-backed/chunked approaches before accepting a large Python serialization slowdown. The 7,311-byte typed return is not the dominant target.

Compute digests while producing exact bytes. Stage private temporary files and expose final artifact names only after all required serialization and expected-digest checks pass, preserving original rejection/write semantics. Keep the unchanged reference encoder separate. Cover Unicode/escaping, arbitrary-width integers, types, ordering, boundaries, malformed values, conversion exceptions and partial-write cleanup. Validate complete original artifact digests and measured peak RSS. Charge buffers, conversion, hashing, writes, controls and cleanup.

### 4. Reduce archival duplication without losing evidence

The audit freshly verified 12 distinct witness files with identical content, totaling 697,723,464 logical bytes. Create a new reversible archive containing immutable content blobs plus per-run manifests, modes, provenance and every individual receipt/failure. Verify blobs before reuse and verify exact restoration into a new external directory. Avoid writable hardlink aliases across runs. Reject path traversal, symlinks, missing/mutated blobs, wrong modes and incomplete manifests; bound memory and declared restored sizes.

Existing raw runs and archives remain untouched. Deduplication is post-run retention and must not remove the writes or controls paid by scientific measurements. Demonstrate a smaller derived archive and exact reconstruction, with archival cost reported separately. Integrate the new retention path for new completed runs after its correctness gate.

### 5. Make cache reuse valid under its declared data contract

`Label.key` is captured once while `basis` remains mutable, and verdict caches use that key. The frozen caller keeps bases stable; extending reuse to mutable requests requires explicit validation or invalidation. Design a source-bound cache boundary that cannot return a stale PASS after basis/key/dimension or relevant calling-environment drift. Keep supported mutable-API behaviour through validated snapshots/versioning or literal uncached fallback; reject unsupported drift before reuse. Do not substitute a shared oracle for an independent check.

Use independent uncached reference computations for mutation-between-request, alias, key collision, type, source/native binding and callback controls. Prove the original frozen caller is unchanged. Record the full cost of every added check and any retained cache state.

### 6. Remove duplicate digest work and improve rank observation retention

Reuse a digest of the same already-read bytes within one inventory/authentication invocation and compare it against every independent expected manifest. Retain distinct before/after trust boundaries and all required source checks. Never cache a source or runtime PASS across changes.

Rank observations retain 59,959 records covering 252 distinct matrices. Investigate interning exact immutable observational rows or a bounded exact recorder. Recompute all original arithmetic and retain every ordered event, result and final canonical byte; this is not rank-answer memoization or duplicate-call removal. Unsupported/callback-bearing values retain literal behaviour. Preserve collector interface and runtime closure identity; include admission, lookup, encoding and cleanup costs.

## Execution sequence

1. **G0: establish closure and interfaces.** Authenticate the baseline, freeze ownership/cost/error contracts and create the new ledger. Source research for all six areas begins in parallel. The independent reviewer prioritizes Area1 immediately.
2. **G1: deliver the log fix.** Review its minimal source patch, run bounded adversarial controls in the parent queue and prove the actual new runner uses it. No full verifier run precedes this gate.
3. **G2: parallel source construction, serial finite gates.** Each area supplies `PROPOSAL.json`, interface notes, source hashes and complete positive/negative control bill. Parent admits and executes candidates one at a time. Changes to common files are integrated only by the parent.
4. **G3: attribute memory and integrate.** Use one bounded full diagnostic if needed to distinguish construction, graph retention, witness materialization and encoding peaks. Finalize all helper/class/native bindings before guard capture; respect the existing private-set adapter's original-source authentication and final lease sealing. Never patch captured wrappers afterward. Freeze a source-reviewed combined stage and execute the complete old/new control union in normal/O modes, with the full caller assertion-on.
5. **G4: complete validation and measurement.** Reproduce exact full outputs, observe wall/CPU/peak RSS, measure archive size and restoration, and account for all new costs. Freeze a same-session comparison protocol before measuring; retain all samples and failures. New source gets new measurements; earlier PR6029 timings do not qualify a new factor. Assess regressions and revise mechanisms when required. This task has no newly invented percentage promise.
6. **G5: delivery.** Package reproducible source, controls, raw evidence, all six final dispositions and a compact checkpoint. Verify read-only/Git-free execution, external output paths, committed source/modes/raw ancestry and lossless export. Refresh applicable upstream guidance/overlap, use the established nonforce fork/Chrome PR workflow, and verify the published commit's hosted checks and required handoff readbacks. Preserve predecessor/license/AI credit and keep correctness separate from performance.

## Shared interfaces and conflict prevention

Workers return source-bound factories/helpers and do not edit the frozen `complex_circuit.py`, backend or full driver. Constructor, cache and rank changes interact with original-source admission and captured closures. The parent first authenticates original functions, installs reviewed variants in the declared order, finalizes trace/native wrappers and captures guard state, then seals the private caller lease around the actual CLI. The reviewer must approve the concrete ordering rather than assume each independent patch composes safely.

The serializer owns byte production; the rank lane owns observation representation; the retention lane owns post-run archive layout. They agree explicit interfaces before coding overlapping assumptions. Archive references never replace fresh computation, scientific outputs or independent comparison inputs.

## Resources and stopping rules

One parent lock/queue covers compilers, adverse process controls, scientific imports, finite/full runs and measurements. Initial feasibility allowance: 600 seconds of guarded commands; total new-round allowance: 2,400 seconds, including failures, controls, compilation, diagnostic and delivery replays. Cap each scientific command at180seconds and sampled memory at1GiB; ordinary output cap remains2MiB. Any intentionally larger output fixture has a separately declared bounded size and an expected STOP. No automatic retry or timing reroll. These are new authorized task limits; the previous ledgers remain unchanged.

Resource/source/output failures stop the affected run, retain evidence and require a reviewed new source version for repair. An implementation difficulty does not complete an area. If a proposed mechanism cannot preserve the contract, independently document the obstruction and pursue another safe mechanism; unresolved requirements remain explicit and the goal incomplete.

## Completion criteria

Complete only after the actual log-handling path is fixed and tested; construction and serialization improvements are implemented and validated; reversible archival reuse preserves every run's evidence; cache reuse has tested invalidation/fallback; digest/rank handling retains all checks and ordered observations; the combined complete caller and resource measurements pass; and delivery/required publication readbacks are finished. Keep source-derived expectations, measured improvements, hypotheses and unresolved risks distinct. No unrelated research, monitoring or automation is included.
