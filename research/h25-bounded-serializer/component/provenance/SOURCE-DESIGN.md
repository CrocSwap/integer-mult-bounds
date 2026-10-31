# Area 3: bounded exact witness serialization

Status: source proposal only; no implementation, scientific imports, compilation, decoding, timing or performance claim.

The immutable baseline is PR6029 `e05aad954689d0ee21baff19b4674f1fcb2e838f`, stage v4. `integration/full_driver.py:322-333` eagerly constructs the witness; `baseline/engine/compare_side_verifier.py:74-94` encodes result, witness and rank trace completely, hashes them, checks EXPECTED, then writes final files in that order. Historical C1 records 527 / 58,143,622 / 2,674,272 bytes and 1.204220868 seconds for serialization. These are historical observations, not candidate results.

## Source findings

Local `/usr/lib/python3.12/json/encoder.py` selects the C encoder only when `_one_shot` is true and indentation is absent. `encode` joins its result. Upstream CPython [commit f6650f9ad73359051f3e558c2431a109bc016664](https://github.com/python/cpython/commit/f6650f9ad73359051f3e558c2431a109bc016664), tagged 3.12.3, [Modules/_json.c](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Modules/_json.c) uses one Unicode writer and returns a one-element tuple after completion (1189-1215). Its integer branch uses Python integer representation (1309-1313); sorted dictionaries sort their items (1479-1494). Calling C `iterencode` on the whole witness therefore does not stream. Python `iterencode` does stream, but adds Python work per token; its time is unmeasured here.

## Proposed mechanism

Keep eager witness construction unchanged for the first candidate. Admit only the exact known witness schema, exact built-in containers/scalars, no cycles, bounded nesting and bounded per-record encoding. A callback-free preflight traverses exact containers using built-in operations. Subclasses, unfamiliar shapes, unsupported leaves, excessive depth or oversized records select the separately retained literal original `write_scientific` before any file action. Arbitrary-width integers have no machine-word restriction: use Python's original decimal conversion, including its configured digit-limit errors. The admitted streaming memory bound does not apply to literal fallback.

Visit top-level keys in canonical order: active, args, code, kind, labels, pieces, support; code keys: gates, outputs, roles, sources. Preserve every sequence item and every basis/source/output insertion order already captured as lists. Encode batches of at most 1,024 records and a conservative 1 MiB encoded upper bound with the unchanged `json.dumps(..., sort_keys=True, separators=(',', ':'), ensure_ascii=True)` expression. Remove only each batch's outer array brackets using a memoryview; insert precisely one comma between nonempty batches. Empty arrays remain `[]`. No JSON parsing, numeric recoding, new C extension or alternate serializer is required.

The estimator is callback-free: exact integer bound is `bit_length*30103//100000+2`; string bound is `12*len+2`; exact floats use a conservative 32-byte bound; containers add punctuation and child bounds. Cap depth at 32. Oversized single records use literal fallback. The result retains its original complete encoder; its frozen size is only 527 bytes. The rank lane confirmed that rank_calls remains an exact list of exact tuple rows/result events; existing length and distinct-matrix expressions remain unchanged.

## Files and failures

Encode result, witness and rank into a unique private stage, incrementally hashing every exact byte. Check the complete EXPECTED dictionary before exposing any ordinary final artifact. On a serialization, count or digest failure, leave ordinary final files untouched and retain staged prefixes plus a bounded failure manifest. Do not retry or convert exceptions into success.

After acceptance, copy staged files using bounded buffers into final `wb` sinks in the original result/witness/rank order. Preserve already completed finals and a failing final's prefix; never delete failure evidence. Success removes private stage files. Failure closes handles, retains its stage and records cleanup errors without masking the primary exception. Parent output-directory rejection remains unchanged. This preserves the semantic ordering and failure-prefix contract, but changes syscall grouping and adds stage IO failures; those differences require reviewer admission and explicit controls. Atomic rename is rejected because it removes the original partial-final-write behavior. An mmap plus original single write is a reserve only: it can count whole-file pages toward RSS.

## Further memory reduction and gate

Lazy labels/pieces projection could avoid their complete secondary lists. It also moves original eager property accesses and conversion failures into serialization order. Defer it until this candidate's measured memory and cost justify that extra source-bound contract; do not claim its savings. Generic Python streaming remains a reserve if batching regresses. A custom native encoder adds integer/escaping parity and cold-build obligations, so it is not the initial candidate.

Admission requires independent source review, all controls in COST-CONTROLS.json, exact old/new complete files and unchanged original encoder execution in a distinct process. Charge preflight, repeated bounds, all conversions, hashes, stage/final writes, reads, cleanup and source custody. Final full runs measure wall/CPU/peak RSS under the parent queue. No speed or memory factor is promised.
