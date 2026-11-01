# Proposed O03 Sol work orders

Prepared 1 November 2026. These orders are source preparation and a conditional execution specification, not dispatched work or a new execution grant. Read the companion analytical audit for the decisions and limitations.

## Exact package inputs

All packages are in Clear1nsight/integer-mult-bounds.

A is `research/h25-authentic-serializer-20261031` at `85fa502d063c132a48eadeb4dc8a188e668a88e0`.

S is `research/h25-bounded-serializer` at `90df75ee32d0c51acbcc5b63ebbe6f26011ee92b`.

B is `research/h25-bookkeeping` at `e05aad954689d0ee21baff19b4674f1fcb2e838f`.

Supporting inventory context is `research/h25-inventory-digest-reuse-20261031` at `c95f76dfad324e6488a88dab9988ce534ee2a481`.

## Decisions inherited from the analytical audit

Retain the C-backed bounded-batch algorithm. Repair and independently review the actual runtime closure and timing/failure-readback envelope. Harden secondary diagnostic recording so that it does not replace a primary exception. Preserve original reference, EXPECTED, old ordered controls, inputs, and failure history. Do not claim total-process savings from a batch cap or infer full-caller qualification from retained-value replay.

## Assignments


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


## Source references

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
