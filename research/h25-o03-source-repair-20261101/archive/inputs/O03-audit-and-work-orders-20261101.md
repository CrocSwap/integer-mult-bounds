# O03 source audit and proposed Sol work orders

Prepared 1 November 2026 for Chris / Clear1nsight.

## Decision

Retain the existing C-backed bounded-batch algorithm as the first design to qualify on authentic complete retained values. Do not replace it with a Python token-streaming encoder before obtaining a valid complete-workload comparison. Do not dispatch another target operation yet.

The immediate work is a new, independently reviewed execution envelope, bounded structured timing readback, and a narrow audit/hardening of secondary-exception bookkeeping. Preserve every frozen source and failed record. A changed implementation or envelope needs a new immutable version, dependent source review, and fresh concrete admission. This document supplies neither an execution grant nor a new resource allowance.

The byte-framing argument is sound under the stated exact-built-in, frozen-input, authenticated-runtime assumptions. The one-MiB limit is an encoded-batch limit, not a total-memory guarantee. Complete-artifact eligibility, complete output validation, and actual memory/cost evidence remain absent for O03.

## Scope of this review

The four PR heads were checked through the GitHub connector. PR6029 is merged. PR6326, PR6332, and PR6328 remain open drafts at the requested heads. Canonical upstream main was checked at the beginning and again before this handoff and remained `626e936ce4d61f2584316914fc71baf96940c512`. Repository guidance was read from main. This was an explicitly assigned analytical task, not a new mathematical task selection.

The complete candidate writer, eager reference, loader, full consumer, independent validator, consumer-control runner, relevant API documents, original plan/rubric, feasibility decision/review/probe specification, observer, bootstrap, custody helper, parent readback, serial coordinator, and selected runtime metadata were inspected. The raw observer STOP and raw outer timing file were inspected alongside the retained failure review. Historical finite evidence was examined through its published outcome and control specification, not independently replayed.

This is not an exhaustive attestation of the 134-file A export. Not every ancillary manifest, review companion, control body, or raw finite-run bundle was re-read. The three authentic transports were not downloaded and authenticated as a complete local stage, decompressed, parsed, or passed through the loader. No target imports, control executions, benchmarks, or scientific computations were performed. No repository files were changed and no PR was opened by this review.

### Frozen inputs

| Name | Commit | Package |
|---|---|---|
| A | `85fa502d063c132a48eadeb4dc8a188e668a88e0` | `research/h25-authentic-serializer-20261031` |
| S | `90df75ee32d0c51acbcc5b63ebbe6f26011ee92b` | `research/h25-bounded-serializer` |
| B | `e05aad954689d0ee21baff19b4674f1fcb2e838f` | `research/h25-bookkeeping` |
| Inventory context | `c95f76dfad324e6488a88dab9988ce534ee2a481` | `research/h25-inventory-digest-reuse-20261031` |

All these commits are addressed in `Clear1nsight/integer-mult-bounds`. Later revisions require separate assessment. The connector reports the same Git blob, `70c4587a67a9f11f87dcc333b3cc84c4b17de773`, for A's candidate writer and S's component writer. That establishes repository object identity for this file, not actual execution custody.

## 1. Checked formulation

### Objective and admissible baseline

The original rubric defines O03 in terms of bounded exact witness serialisation on complete artifacts with memory/cost evidence. Other gates explicitly require the complete caller. The original Area 3 plan requires exact bytes, private staging before acceptance, an independent unchanged reference, complete artifact validation, and charged memory/cost evidence. It does not impose a numerical speedup or a mandatory reduction in total-process peak RSS.

I therefore accept complete retained-value replay as a source-supported O03-only route. This conclusion follows from the original criterion and separation of gates, not merely from the earlier feasibility review's acceptance. The replay cannot establish fresh scientific construction, original alias topology, caller peak memory, or completion of the wider six-area programme. A measured no-gain or regression outcome can be submitted for an O03 decision when every required correctness and measurement condition is satisfied, but neither a regression nor the absence of a numerical target makes acceptance automatic. [R1, R2]

The O03 baseline is the literal eager `write_scientific` on freshly restored complete values. The candidate is production `make_writer` on independently restored values in a separate fresh process. PR6029's earlier performance percentage and PR6328's inventory-only improvement are not serializer targets, measurements, or transferable credit. [R3, R14]

### Authentic and generic domains

The authentic loader implements the brief's result projection, exact scalar types, tuple restoration, ordered arrays, coefficient pairs, and rank counts. Its public entry point fixes the input pins and counts. It rejects duplicate JSON keys, nonfinite constants, floating overflow, incorrect shapes, and `bool` in integer positions. It retains valid Boolean fields and the finite floating `roles_per_target`. Rational pairs are retained values, not newly validated or normalised fractions. [R4]

The writer's generic fast path is broader. It accepts exact built-in scalar/container values under the recursive byte/depth checks, including nonfinite floats accepted by the unchanged encoder. Result may be any admitted value. Witness and code require their exact key sets, array fields may be exact lists or tuples, and rank events have the stricter exact list/tuple/integer structure. Ancestor tracking rejects cycles but permits repeated acyclic references. Container depth is checked separately from each array record, not as a single traversal of the entire witness. [R5]

Factory limits are exact integers, excluding `bool`. The full consumer fixes batch/copy limits at 1,048,576 bytes and row batches at 1,024. Unsupported data or destinations delegate before candidate file creation. Factory, reference-shape, and freshness failures are separate rejection paths. Literal fallback cannot qualify as bounded execution. [R5, R6]

The exact output contract remains unchanged.

| File | Bytes | SHA-256 |
|---|---:|---|
| result.json | 527 | `342e99212b12e518902ae9598613f5484113bacee8747c27a13b58a4b1d3986c` |
| witness.json | 58,143,622 | `4b170c1dbfc33c7cb141a2284c6fd69eac7b6d100971d3e9ee625502b5893f82` |
| rank-trace.json | 2,674,272 | `85006ca332bbc57c2ba9fd06f61a0281d4cee600c9f3b449342379bf2aedec8f` |

There are 59,959 ordered rank events and 252 distinct row tuples. These counts plus the three hashes are the original five-field EXPECTED. The scientific return adds only `serialized_bytes`. Candidate instrumentation stays in supplementary operational records. No sequence order or duplicate may be changed. [R3, R4, R6]

## 2. Conditional byte-equivalence argument

### Assumptions

The theorem concerns exact, non-mutating admitted built-ins under the authenticated reference/runtime configuration, with successful required conversions, allocation, and I/O. It assumes the original canonical encoder, reference functions, and EXPECTED have not changed. The supported caller and filesystem ownership contract exclude hostile concurrent mutation. Exceptions, fallback, and publication are addressed separately; this is not a theorem of identical arbitrary I/O traces.

### Record bounds

Write `C(x)` for the authoritative canonical ASCII encoding. For an integer with bit length `k`, the estimator is `floor(k * 30103 / 100000) + 2`. Since `log10(2) < 30103/100000`, this covers the decimal digits and any minus sign; zero is also covered. It introduces no fixed-word integer restriction and performs no decimal conversion during admission.

A string of `n` Python code points contributes at most `12*n + 2` ASCII bytes under the required escaping. A supplementary-plane character can require two six-byte surrogate escapes. Other characters require no more. The constants for null and Booleans dominate their literal lengths. The float bound of 32 is conservative for the intended binary64 CPython representation, including the encoder's nonfinite literals, but is a runtime-specific premise rather than a statement about arbitrary Python implementations.

For lists and tuples, the estimator starts with two brackets and adds one punctuation byte plus each child bound. For dictionaries, it adds escaped key bounds, a colon/comma allowance, and child bounds. Induction proves an upper bound for every successfully admitted subtree. Crucially, an early over-limit return is only a rejection witness; it need not bound the unread remainder of that subtree. This distinction does not impair admission because an over-limit result is rejected. [R5, R15]

### Batch invariant and framing

Each record is admitted only when its bound plus three fits B. Each nonempty batch starts with bound 2 and adds a record only while the accumulated estimate fits B, subject to the row cap R. The first record necessarily fits, so every iteration advances. Every batch contains at most R references and its canonical encoding has at most B bytes.

For a nonempty batch, removing only its outer brackets leaves exactly the comma-separated encodings of its elements. Concatenating consecutive nonempty batch interiors with one comma produces the same interior as encoding the full original array. Adding the outer brackets completes the identity. The empty array emits `[]`. No element is omitted, duplicated, normalised, or reordered.

The manually emitted witness keys are exactly the canonical lexical order `active,args,code,kind,labels,pieces,support`. The code keys are `gates,outputs,roles,sources`. Result, roles, keys, and batch contents still use the unchanged canonical encoder. Nested dictionary sorting, tuple/list array treatment, integer formatting, float formatting, signed zero, escaping, and generic nonfinite handling therefore remain delegated to the same primitive. The artifacts have no trailing newline. [R3, R5]

### Receipt and freshness

Incremental SHA updates over the proven concatenation hash the same byte sequence as the eager reference. The rank count and distinct-row expression are the same. The complete original receipt is checked before any final file is opened. The byte counts are then added in the original return structure.

Every call performs new structural admission and entry freshness checks. Pre-cleanup and exit checks add detection of relevant reference/runtime drift. These checks do not replace the frozen-caller and ownership assumptions, and before/after checks are not a defence against an arbitrary adversary that mutates and restores state between checks. `last_operation` supplies evidence under authenticated source; it is not an independent mathematical oracle. [R5, R6]

The argument establishes conditional byte equivalence. Hash matching remains a required operational check, while the independent validator's complete comparisons remain necessary evidence for an actual run.

## 3. Space and cost analysis

The rigorous implementation-facing formulation is

`M_aux = O(R + C + D + U + K) + E_runtime(B, D)`.

Here B is the encoded-batch cap, R the batch-reference cap, C the copy-read cap, D traversal depth, U the distinct rank-row count, K captured reference/runtime and fixed operational metadata, and `E_runtime` the encoder, sorting, escaping, and numeric-conversion workspace for a bounded call. When the authenticated provider's workspace is linear in the bounded representation, this reduces to the brief's successful-fast-path model

`M_aux = O(B + R + C + D + U + K)`.

The candidate source establishes bounded encoded calls, row slices, and reads. The additional provider premise must not be silently inferred from the output cap alone. The inspected upstream C encoder uses a Unicode writer and sorted-item storage; its integer branch delegates to Python integer representation. The inspected CPython integer source also contains a build-dependent large-integer helper path. The actual build, digit-limit configuration, reachable conversion providers, and their workspace therefore belong in runtime/source review. This observation is not evidence that authentic H25 reaches that helper or fails. [R5, R15, R16]

The bound excludes retained input objects and disk. It includes temporary old/new slices, possible overlapping old and new encoded buffers, Unicode and ASCII buffers, escaping and sorting temporaries, hash state, and ancestors. It is not a claim that at most one batch-sized allocation exists. The distinct-row set needs O(U) additional references even though the tuples themselves are already retained. U is 252 on the intended successful complete output.

Fallback is eager. Error-string conversion and failure-manifest encoding occur before their final length checks. Consequently there is no established all-path bounded-space theorem. The diagnostic hardening recommended below preserves primary exceptions; it does not by itself prove an all-path allocation bound. [R5]

The loader still materialises the logical input and parsed/restored containers, with overlapping lifetimes. The independent validator streams the witness but collects and parses the rank trace. Allocator retention and common eager-loading peaks can mask a writer-phase benefit. Neither file sizes nor the auxiliary-space expression determine process RSS. A lifetime high-water RSS difference is not a writer-phase allocation measurement. [R4, R6, R7]

With S = 60,818,421 bytes, the successful writer-only logical bill is exact.

| Quantity | Eager | Candidate |
|---|---:|---:|
| Bytes supplied to writer hashing | S | 2S |
| Bytes written by writer | S | 2S |
| Stage-to-final reads | 0 | S |
| Final artifacts | S | S |

Candidate staging plus finals can occupy 121,636,842 logical bytes. Retaining baseline finals as well makes 182,455,263 bytes before transports, source stages, controls, logs, receipts, and failures. These are logical bytes, not measured storage blocks or device traffic. Factory setup, repeated admission/bound walks, all authentication, local readbacks, independent validation, and cleanup remain additional paid work. [R2, R3, R5]

## 4. Publication, failure, and source findings

### Established sequencing

The candidate stages all three artifacts, checks their identities/sizes and the full receipt, then copies into final files in result/witness/rank order. Before acceptance, the final names remain untouched. After copying starts, an earlier final can be complete and a later final partial or corrupt. Subsequent finals are not opened following failure. Short writes raise without retry. Neither atomic triplet publication nor fsync/crash durability is promised. Different syscall grouping and different failure-prefix lengths are already admitted. [R5, R8]

### Copy authentication is not final-file authentication

The copy hash authenticates bytes read from the staged source. Final size checks do not independently prove final content. The full consumer's complete hash readback and the independent validator's complete byte comparison close that operational evidence requirement. Neither may be removed or moved outside the substantive measured operation by an optimisation claim. [R5, R6, R7]

### Retained-stage wording needs precise scope

A copy rejection occurs before successful cleanup and normally retains staging. Cleanup itself can partially remove the stage, and exit freshness runs after cleanup. A late failure can therefore have no stage in which to write a manifest. `FAILED_EVIDENCE_RETAINED` is a status label, not a guarantee that every temporary byte survives every failure. I accept the brief's clarification. It must remain explicit in any later API summary. [R5, R8]

### New source-derived primary-exception gap

In `managed`, when an operation has a primary exception and close then raises, the handler appends a record through `info.setdefault(...).append(...)` without protecting that bookkeeping. Allocation failure there can replace the original primary exception. The outer failure handler also performs its secondary-error metadata assignment outside a further protective boundary. These are conditional source counterexamples to an unrestricted claim that diagnostic failures can never mask a primary exception. They are not observed failures, and they do not contradict the recorded ordinary close/manifest controls. [R5]

I recommend a narrow new-version change that makes all secondary diagnostic recording best effort and leaves the original exception authoritative. Keep the batch algorithm, reference, EXPECTED, and original 70 controls unchanged. Add deterministic, source-reviewed injected bookkeeping failures rather than attempting actual memory exhaustion. Any change invalidates dependent source hashes and requires fresh review. This audit does not rewrite the historical I1/I2 acceptance records.

### Execution-envelope failures are corroborated

The raw observer record reports the missing locale archive at initial runtime closure, contains no worker execution result, and records zero reaped-child CPU. The raw timing file contains the nonzero-exit diagnostic followed by one JSON timing record. `parent_readback.py` parses this whole file before initialising its structured report. The stated failure attribution is supported by code and raw records, not merely by the review summary. [R9, R10, R11]

The new runtime inventory must authenticate actual mapped files and providers for the chosen host. Adding a pathname to an allow-list is insufficient. Pin and authenticate its actual bytes/metadata, review the complete dependency closure, and preserve the historical record. I prefer sealing the required locale data under the intended environment before changing locale semantics. A different deterministic locale policy remains a separately reviewed alternative.

## 5. Design assessment

The present approach is a sensible first candidate because it keeps the authoritative encoder, uses bounded slices, and avoids a new native serializer. It does pay a full preflight walk, another bound walk while batching, C encoding, stage and copy hashing, duplicate writes, and freshness checks. A record that does not fit the current batch can be bounded again at the next boundary. Conservative string estimates can reduce batch occupancy. These are plausible costs, not measured bottlenecks. [R5, R12]

Refining bound computation or batching is a later controlled hypothesis. Caching every record estimate would add storage proportional to the number of records. Interleaving admission with staged output can change the requirement that unsupported input selects literal fallback before candidate writes. Neither is a free replacement.

Ordinary `JSONEncoder.iterencode` selects Python traversal in the inspected source. Its API alone does not bound token size. Conversely, the C one-shot implementation builds its completed encoding rather than exposing bounded chunks of the whole witness. A streaming replacement needs scalar/escaping/error parity and a paid CPU comparison, not an iterator-shaped interface. [R15]

The stage hash and copy hash protect different byte observations across a mutable storage boundary. PR6328's reuse of a digest of the same in-memory bytes does not justify removing the copy hash. Reusing a digest already produced within the same authenticated observation may be valid, but it must retain every independent comparison and later trust boundary. [R5, R14]

Rename publication changes visible failure behaviour and inode/visibility semantics. Lazy witness projection changes input lifetimes and error timing. A native encoder adds parity, provider authentication, cold-build, and maintenance costs. All are possible separately reviewed designs, but none is justified as the next implementation on the present evidence. [R8, R12]

Change approach after, not during, a declared operation that demonstrates unsupported authentic records, resource failure, or an explained but unacceptable complete-workload regression. Preserve that first result. Do not adapt batch caps, inputs, EXPECTED, or sample selection within the operation.

## 6. Next validation and measurement design

Preserve Q1 through Q5. First close exact source/control review, then actual immutable source/input/runtime custody, then fresh operation/resource admission, then executed controls and full comparison, and finally independently accepted cost/disposition evidence. Source-only findings do not award later gates. [R2]

P0 authenticates and stages all exact sources, inputs, providers, and observer dependencies. It must reject aliases, unexpected modules/maps, changed pins, and reused PASS. Actual metadata is obtained for the new stages, never copied from the old host's example identities.

P1 executes the unchanged 70 serializer cases, 39 loader cases, and 15 consumer cases in each Python mode, plus the newly frozen diagnostic/parser and observer controls. The existing subtotal is 124 per mode, or 248 case-mode executions, not 248 distinct cases. Additional tests need their own exact names, order, fixture limits, and independent expected outcomes. Historical controls are not a substitute for this new operation. [R13]

P2 runs one complete eager baseline at optimisation level 0 with fresh restored inputs. P3 then runs one production candidate at level 0 with independently restored inputs. Require the original hashes, sizes, counts, receipt, local readbacks, custody, `faults_enabled=False`, `BOUNDED_SERIALIZATION_PASS`, phase `complete`, actual batch evidence, per-file stage/hash/copy counters, and cleanup. Literal fallback stops qualification.

P4 runs the independent validator against a separately authenticated original input stage and both output roots. Require complete logical witness/rank comparisons, independent result projection, exact EOF, rank schema/counts, scientific receipts, operational records, and cleanup/custody checks. P5 closes the predeclared finite records and evaluates the actual source, failure, resource, and gain/no-gain/regression disposition. [R2, R6, R7]

Start outer timing and resource observation before staging, source/runtime authentication, imports, controls, and loading. Include factories/preflight, all writer work, local readbacks, independent validation, logging/custody checks, cleanup, and substantive closing checks. Preserve a finite explicit tail for unavoidable final observer-record publication and one parent readback. Unknown tail costs remain unknown and nonzero; do not move endpoints retrospectively.

Retain inclusive elapsed time, aggregate CPU with each process counted once, simultaneous sampled process-tree RSS, sampling interval and PID/race/missed-peak limits, individual kernel maxRSS separately, and any cgroup figure under its own accounting definition. The current observer uses 10 ms sampling and does not collect cgroup peak. Its aggregate peak and the consumer's writer timestamps do not provide a complete writer-phase memory trace. [R10]

Before admission, add or independently approve bounded phase attribution for load/restore, factory, writer, readback, and validation. Writer CPU snapshots and phase-tagged RSS observations must be supplementary records, not changes to the scientific receipt. Do not subtract lifetime maxRSS values to infer writer allocation. A claim about precise Python/native auxiliary allocation requires an explicitly selected allocation measurement method and its charged overhead; RSS alone is not that metric.

Freeze hardware/runtime/filesystem context, cache/order limitations, resource limits, and all instrumentation before the first pair. A fixed baseline-then-candidate pair is a scoped observation, potentially order-sensitive, not a distributional performance result. Repetition requires a separate predeclared experiment and admission.

The old coordinator put its eight serial jobs inside one outer 180-second command. Do not silently allocate 180 seconds anew to every internal step. If the historical policy is continued, the new admission must explicitly confirm 180 seconds per admitted outer command, 1,073,741,824 sampled group bytes, and the current remainder of the existing 2,400-second allowance. The historical 94.550533479-second balance is not a freshly verified current ledger. [R10, R11]

## 7. Proposed Sol work orders

These are specifications for subsequent assignments, not dispatched work and not execution permissions. A/S/B always mean the exact pins above. New drafts belong to separate owned directories. No worker may edit a frozen package, replace EXPECTED, delete historical failures, merge a PR, or change a frontier.

For source-only orders W1 through W4, proposed ceilings are 32 MiB of named text/source reads and 8 MiB of new draft outputs per order. The target execution, control, benchmark, compilation, and authentic transport decoding allowances are all zero. Passive parsing/hashing, where allowed by the parent's existing policy, is capped at 10 seconds per command, 60 seconds aggregate, and 256 MiB RSS per order. These are proposed ceilings, not an additional grant or a reset of any ledger. Stop at an input mismatch or a need to exceed scope.

### W1. Independent bounds, framing, and provider-workspace review

Exact inputs are A/consumer/{bounded_serialization.py,reference.py,CONTROL-SPEC.json}, A/loader/frozen_h25_inputs.py, S/component/docs/{API-v2.md,API-v3.md}, S/component/provenance/SOURCE-DESIGN.md, B/payload/baseline/engine/{compare_side_verifier.py,profile_side_verifier.py}, and the exact intended runtime source/build metadata supplied by the parent. The inspected upstream CPython comparison sources are linked in R15/R16; they are not a substitute for actual provider identity.

The narrow question is whether admitted records, framing, and scalar delegation establish byte equality and what provider assumptions are needed for the auxiliary-space model. Deliver `BOUND-FRAMING-REVIEW.md`, `ASSUMPTIONS.json`, and an ordered proposed boundary-control specification. Include integer/sign/zero bounds, Unicode and surrogates, float bound, dictionary punctuation/sorting, early cutoff, shared aliases/cycles, per-record depth, batch progress, and simultaneous buffers.

The independent oracle is the original B canonical/writer source plus a separately written inductive argument, not candidate hashes or a saved PASS. Do not run either encoder. Stop and retain any counterexample or unresolved provider assumption without weakening the domain silently.

### W2. Publication and primary-exception hardening

Exact inputs are A/consumer/{bounded_serialization.py,reference.py,serialization_controls.py,CONTROL-SPEC.json,full_consumer.py,validate_outputs.py}, S/component/docs/{API-v2.md,API-v3.md}, and the failure findings in this audit.

Deliver `FAILURE-STATE-TABLE.md`, a minimal proposed patch in a new source version, and `NEW-FAILURE-CONTROLS.json`. Preserve the encoding/batching algorithm and all original controls. Make secondary diagnostic mutations best effort without replacing the original exception. Map final-file visibility, residual stage bytes, manifest availability, and primary/secondary error precedence for staging, copy, cleanup, and late freshness failures.

The independent oracle is the admitted API and original writer's pre-acceptance/sequential-final semantics. Proposed deterministic cases must include primary plus close failure plus bookkeeping failure, primary plus failure-manifest failure plus diagnostic-record failure, successful copy followed by partial cleanup failure, and exit freshness after complete cleanup. Do not attempt real memory exhaustion. Stop if the patch requires changed publication semantics or changes the reference/EXPECTED.

### W3. Actual-runtime closure preparation

Exact inputs are A/validation/envelope-revision-v2/envelope/{bootstrap.py,effective.py,observer.py,worker.py,sequence_worker.py,custody.py,RUNTIME-PINS-v2.json,ELF-CLOSURE-v2.json,FIXED-SEQUENCE-v2.json,OPERATION-BILL-v2.json}, A/consumer/DEPENDENCIES-v1.json, and A/validation/execution-v1/complete-fixed-o03/observer-receipt.json.

Deliver `RUNTIME-CLOSURE-PLAN.md`, `DEPENDENCY-MATRIX.json`, and a concrete acquisition proposal for the intended host. Trace observer, controls, worker, loader, serializer, validator, failure, locale, JSON, hashing, gzip/zlib, and reachable integer-conversion dependencies. Prefer retaining the intended locale semantics and authenticating actual locale data. Any alternative locale policy must list changed startup behaviour and dependencies.

The independent check is consistency with the actual executable/providers, mapped-file identities, module origins, callables, and immutable source/input custody. Historical absolute paths and a new allow-list entry are not an oracle. Source work must not probe or launch the target. Actual host discovery requires separately specified tools, permissions, budget, and custody before it can produce a sealed runtime manifest. Stop if that information is unavailable; report it as an admission dependency rather than inventing pins.

### W4. Bounded timing parser and structured failure readback

Exact inputs are A/validation/envelope-revision-v2/envelope/{parent_readback.py,custody.py,observer.py}, A/validation/execution-v1/control/{outer-time.json,COMMAND-v1.json,READBACK-COMMAND-v1.json}, A/validation/source-reviews/FAILURE-REVIEW-v1.json, and the pinned timing utility/launcher contract selected by W3.

Deliver a new-version parser/readback source draft, `TIMING-GRAMMAR.md`, literal raw fixtures with independent expected outcomes, and an exact ordered control manifest. Move all fallible input reads, parsing, identity capture, and validation inside the structured failure boundary. Initialise a minimal report before reading external records. Report-writing failure must not replace the primary parsing or execution failure.

The selected design is a bounded, uniquely tagged timing record, for example `O03_TIME_V3 ` followed by one strict JSON object, within an immutable retained raw timing stream. Preserve diagnostics verbatim. Require exactly one record, an explicit admitted prefix grammar, and no undeclared suffix. Do not search for the last plausible JSON object. A separate explicitly declared legacy grammar may interpret the preserved historical two-line format into a new derived record, but must never rewrite it or promote the old failed operation to PASS.

Proposed limits are 65,536 raw timing bytes, 4,096 bytes for the tagged record, and 65,536 bytes for the derived report. Open/check regular descriptors and enforce the input cap before materialisation. Reject duplicate JSON keys, Boolean numeric fields, invalid/nonfinite/negative measurements, oversized numeric tokens, and schema drift. Keep execution success, measurement validity, and accounting completeness as separate fields. Require corroborated termination facts, or report termination/accounting as unknown. A valid timing record for a failed command remains a failed command.

Freeze the following 30 cases in this order. These are proposed literal fixtures, not executed tests.

| ID | Concrete fixture or condition | Required disposition |
|---|---|---|
| T01 | One valid tagged record, zero exit, matching observer/admission | Valid measurement; success only after all other checks |
| T02 | Declared nonzero diagnostic and matching exit-1 record | Valid measurement; workload STOP |
| T03 | Signal diagnostic plus independently supplied matching signal termination | Valid measurement where complete; workload STOP |
| T04 | Preserved historical two-line record under explicitly selected legacy grammar | Derived failed-startup accounting only |
| T05 | Missing raw timing file | Structured STOP; no zero substitutes |
| T06 | Empty raw timing file | Structured STOP |
| T07 | Diagnostic prefix without any timing record | Structured STOP |
| T08 | Truncated tagged JSON | Structured STOP |
| T09 | Malformed tagged JSON | Structured STOP |
| T10 | Two timing tags/records | Structured STOP |
| T11 | Undeclared trailing non-whitespace bytes | Structured STOP |
| T12 | Duplicate JSON key | Structured STOP |
| T13 | Missing required measurement key | Structured STOP |
| T14 | Extra undeclared measurement key | Structured STOP |
| T15 | String in a numeric measurement slot | Structured STOP |
| T16 | Boolean in a numeric measurement slot | Structured STOP |
| T17 | NaN constant | Structured STOP |
| T18 | Infinity or numeric floating overflow | Structured STOP |
| T19 | Negative elapsed time, CPU, or RSS | Structured STOP |
| T20 | Numeric token exceeding the declared lexical bound | Structured STOP before unbounded conversion |
| T21 | Raw file of cap plus one byte | Structured STOP without full materialisation |
| T22 | Tagged record of cap plus one byte | Structured STOP |
| T23 | Invalid text encoding in a required grammar field | Structured STOP; raw bytes retained |
| T24 | Symlink, nonregular descriptor, or disallowed alias | Structured STOP without blocking on a special file |
| T25 | Descriptor/path identity changes during bounded read | Structured STOP |
| T26 | Valid timing with observer STOP or wrong admission binding | No workload PASS |
| T27 | Termination status disagreement or missing corroboration | STOP/unknown accounting, never inferred success |
| T28 | Admission or observer read fails before timing parsing | Structured STOP |
| T29 | Primary failure followed by report-write/close failure | Primary preserved; reporting failure retained separately |
| T30 | Measurement passes but cap/ledger validation fails | Resource/accounting STOP |

Oracles must be literal expected fields and failure classes written independently of the parser. A proposed future finite execution must exercise normal and `-O` behaviour and real launcher zero/nonzero/signal cases under an actual admission. W4 itself has zero execution allowance.

### W5. Conditional integrated qualification operation

Inputs are the frozen A transports and original reference/EXPECTED, preserved old controls, reviewed W1/W2 results, independently sealed W3 runtime/source/input stages, reviewed W4 parser/controls, an actual current ledger, and a fresh one-use admission with concrete commands and paths. Every new source output needs its actual immutable hash before use; this document supplies no fictional future hash.

Deliver one retained P0-P5 evidence packet with all raw controls, first baseline, first candidate, complete independent validation, source/input/runtime custody, phase/inclusive measurements, cleanup records, resource accounting, outside-tail statement, and reviewed disposition. No benchmark distribution, caller saving, new construction, or frontier claim is authorised.

The independent oracle is the original five-field EXPECTED plus complete byte comparison to separately authenticated original logical inputs and an independently projected result. Each arm owns freshly restored values and separate output roots. Candidate PASS and instrumentation are necessary but not sufficient.

The actual tools required are a supervised host with the sealed CPython/runtime providers, immutable source/input staging, bounded regular-file I/O, process-tree observation and termination, and the reviewed timing/record tools. The existing historical caps may be reused only if explicitly reaffirmed. Under that policy the admitted outer command is capped at 180 seconds and 1,073,741,824 sampled group bytes, charged against the freshly established remainder of 2,400 guarded seconds. Freeze a numerical disk/log/receipt bill and its guard from the actual manifest before admission. No old consumed marker, permission, deadline, or host identity is portable.

Stop at the first unexpected control failure, source/runtime/custody drift, unsupported authentic record/fallback, output or receipt mismatch, cap breach, incomplete validation, or required-measurement failure. Retain the attempt. No automatic retry, smaller workload, adaptive splitting, EXPECTED change, or favourable-sample replacement is permitted. W5 remains blocked until its missing current-host, ledger, review, and admission inputs actually exist.

## 8. Evidence disposition and remaining obligations

The mathematical result supplied here is the conditional record-bound and framing argument. Source inspection supports the authentic schema, retained-value O03 interpretation, exact receipt structure, logical I/O bill, and the publication/readback distinctions. The provider-dependent auxiliary-space statement is explicitly conditional and is not a numerical RSS guarantee.

Historical S evidence records 70 normal and 70 optimised case executions and a small 9,417-byte comparison. Its baseline observations were 0.26 seconds wall, 0.24 CPU, and 20,168 KiB individual GNU peak RSS; its candidate observations were 0.27, 0.25, and 22,012 KiB. These are finite, rounded, single observations, not a complete H25 result or a stable regression estimate. [R13]

The authentic attempt records failed startup only. Its 0.33-second outer wall observation, 0.32-second CPU total, and 0.34-second policy debit do not establish workload fit. The historical scoped ledger is 94.550533479/2400. No new physical measurement or ledger debit is claimed by this analytical report. [R9, R11]

Complete authentic bounded-path execution, complete independent output validation, complete-artifact memory/cost evidence, actual provider closure, robust timing/failure readback, phase attribution, current custody, current ledger, fresh admission, and independent final adjudication remain open. The new primary-exception finding also needs a reviewed disposition. Prior I1/I2 source acceptance is historical evidence, not a substitute for reviewing changed dependent source. No O03, full-caller, six-area, or performance credit is awarded here.

Predecessor credit remains with PR6029, PR6326, PR6332, PR6328's separate inventory work, PR5864 and the retained Douglas R. Colkitt/CrocSwap circuit and verification lineage, and Chris / Clear1nsight. This audit is AI-assisted analytical work, not independent human review or proof-kernel certification.

## Source references

All repository links below are pinned unless explicitly described as a live PR. Grouped references identify exact source files rather than substitutes for an independently authenticated execution stage.

**R1** [A/provenance/original-goal/control/PLAN-before-granular-progress-v1.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/provenance/original-goal/control/PLAN-before-granular-progress-v1.md); [A/provenance/original-goal/control/hourly-progress/RUBRIC-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/provenance/original-goal/control/hourly-progress/RUBRIC-v1.json).

**R2** [A/provenance/feasibility/contract/DECISION-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/provenance/feasibility/contract/DECISION-v1.json); [A/provenance/feasibility/review/REVIEW-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/provenance/feasibility/review/REVIEW-v1.json); [A/provenance/feasibility/technical/PROBE-SPEC-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/provenance/feasibility/technical/PROBE-SPEC-v1.json).

**R3** [A/consumer/reference.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/consumer/reference.py); [B/payload/baseline/engine/compare_side_verifier.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/e05aad954689d0ee21baff19b4674f1fcb2e838f/research/h25-bookkeeping/payload/baseline/engine/compare_side_verifier.py); [B/payload/baseline/engine/profile_side_verifier.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/e05aad954689d0ee21baff19b4674f1fcb2e838f/research/h25-bookkeeping/payload/baseline/engine/profile_side_verifier.py); [A/provenance/original-serializer/REFERENCE-EXTRACTION.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/provenance/original-serializer/REFERENCE-EXTRACTION.json).

**R4** [A/loader/frozen_h25_inputs.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/loader/frozen_h25_inputs.py).

**R5** [A/consumer/bounded_serialization.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/consumer/bounded_serialization.py); [S/component/bounded_serialization.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/90df75ee32d0c51acbcc5b63ebbe6f26011ee92b/research/h25-bounded-serializer/component/bounded_serialization.py).

**R6** [A/consumer/full_consumer.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/consumer/full_consumer.py).

**R7** [A/consumer/validate_outputs.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/consumer/validate_outputs.py).

**R8** [S/component/docs/API-v2.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/90df75ee32d0c51acbcc5b63ebbe6f26011ee92b/research/h25-bounded-serializer/component/docs/API-v2.md); [S/component/docs/API-v3.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/90df75ee32d0c51acbcc5b63ebbe6f26011ee92b/research/h25-bounded-serializer/component/docs/API-v3.md).

**R9** [A/validation/execution-v1/complete-fixed-o03/observer-receipt.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/execution-v1/complete-fixed-o03/observer-receipt.json); [A/validation/execution-v1/control/outer-time.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/execution-v1/control/outer-time.json).

**R10** [A/validation/envelope-revision-v2/envelope/bootstrap.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/envelope-revision-v2/envelope/bootstrap.py); [A/validation/envelope-revision-v2/envelope/parent_readback.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/envelope-revision-v2/envelope/parent_readback.py); [A/validation/envelope-revision-v2/envelope/observer.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/envelope-revision-v2/envelope/observer.py); [A/validation/envelope-revision-v2/envelope/sequence_worker.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/envelope-revision-v2/envelope/sequence_worker.py); [A/validation/envelope-revision-v2/envelope/custody.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/envelope-revision-v2/envelope/custody.py); [A/validation/envelope-revision-v2/envelope/RUNTIME-PINS-v2.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/envelope-revision-v2/envelope/RUNTIME-PINS-v2.json).

**R11** [A/validation/source-reviews/FAILURE-REVIEW-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/validation/source-reviews/FAILURE-REVIEW-v1.json); [A/PUBLIC-OUTCOME-v2.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/PUBLIC-OUTCOME-v2.json); [A/EVIDENCE-README-v2.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/EVIDENCE-README-v2.md); [A/TAKEOVER-v2.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/TAKEOVER-v2.md).

**R12** [S/component/provenance/SOURCE-DESIGN.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/90df75ee32d0c51acbcc5b63ebbe6f26011ee92b/research/h25-bounded-serializer/component/provenance/SOURCE-DESIGN.md).

**R13** [S/validation/reviews/PUBLIC-OUTCOME-v2.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/90df75ee32d0c51acbcc5b63ebbe6f26011ee92b/research/h25-bounded-serializer/validation/reviews/PUBLIC-OUTCOME-v2.md); [A/consumer/CONTROL-SPEC.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/consumer/CONTROL-SPEC.json); [A/loader/CONTROL-SPEC-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/loader/CONTROL-SPEC-v1.json); [A/consumer/CONSUMER-CONTROL-SPEC-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/consumer/CONSUMER-CONTROL-SPEC-v1.json); [A/consumer/run_controls.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/consumer/run_controls.py); [A/reviews/I1-REVIEW-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/reviews/I1-REVIEW-v1.json); [A/reviews/I2-REVIEW-v1.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/85fa502d063c132a48eadeb4dc8a188e668a88e0/research/h25-authentic-serializer-20261031/reviews/I2-REVIEW-v1.json).

**R14** [PR6328 supporting inventory context](https://github.com/CrocSwap/integer-mult-bounds/pull/6328); [Pinned inventory package](https://github.com/Clear1nsight/integer-mult-bounds/tree/c95f76dfad324e6488a88dab9988ce534ee2a481/research/h25-inventory-digest-reuse-20261031).

**R15** [CPython v3.12.3 Lib/json/encoder.py](https://github.com/python/cpython/blob/v3.12.3/Lib/json/encoder.py); [CPython _json.c at f6650f9ad73359051f3e558c2431a109bc016664](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Modules/_json.c).

**R16** [CPython longobject.c at f6650f9ad73359051f3e558c2431a109bc016664](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Objects/longobject.c).
