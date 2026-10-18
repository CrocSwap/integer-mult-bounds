# Reuse JSON parses in the complete T16 invoice boundary replay

This opt-in adapter runs Tairitsu-Aya's complete 54-case
[T16 invoice boundary audit](../t16-invoice-boundary-audit/README.md) while
reusing the loaded invoice's JSON parses. Every predicate in that boundary
audit still runs. The complete reconstructed receipt must equal the unchanged
`EXPECTED.json`. No selected source, frozen archive or kappa changes.

Kumagi's [PR3009](https://github.com/CrocSwap/integer-mult-bounds/pull/3009)
already reduced fixture compression costs. Its remaining handoff identified
repeated JSON parsing. Profiling the current predecessor on this Linux host
with CPython 3.14 found 1,968 `json.raw_decode` calls taking 28.846 seconds of
a 166.859-second instrumented run. These are profile costs, not speedup data.

## Measured result

Four fresh CPython 3.12.15 processes on one shared Linux host ran in
baseline/cached/cached/baseline order. Every complete emitted receipt was
byte-identical to the original. [RESULT.json](RESULT.json) records exact commands,
environment, verifier hash, timing method and all observations.

| Mode | Wall seconds, in execution order | Peak RSS (KiB) |
| --- | --- | --- |
| Baseline | 179.276, 197.756 | 939892, 939804 |
| Cached | 170.213, 179.694 | 970392, 970320 |

Mean wall time fell from 188.516 to 174.954 seconds (7.19%); mean peak RSS rose
by 30,508 KiB (about 29.8 MiB). Each cached replay reused 488 of 628 reads across
12 paths, retaining 30,013,304 bytes of raw and serialized data. Timing ranges
overlap and the host was shared: these are local observations, not a confidence
interval or portable speed guarantee. No process reused another process's cache.

## Equivalence and invalidation

Only the loaded `invoice_allcold.read` function is replaced. Its frozen source
bytes remain unchanged. The adapter keeps one `(raw bytes, marshaled JSON)`
entry for the first successfully parsed contents of each path:

1. Read the current file bytes on **every** call. Size, modification time,
   inode and a previously recorded digest are never freshness tests.
2. If the bytes differ, use the original `json.loads`/`gzip.decompress`
   semantics. One-shot mutations are not serialized or added to the cache.
3. If the bytes agree, deserialize the private in-memory representation.
   Every call returns a fresh mutable value, including nested lists/dictionaries.

A hit therefore returns the same JSON value as a fresh parse of the bytes just
read; a miss performs that parse. Mutating the return cannot change the cached
bytes. Malformed inputs and missing files still fail after a successful read.
Restoring a fixture is observed like any other change. `marshal` is used only
on this process's JSON values, never on input-controlled serialized bytes.
The predecessor already uses this representation for its mutation copies.
Keeping the first contents suits this audit's restored-fixture pattern. A file
that changes permanently will be reparsed on every subsequent read; this is
not intended as a general-purpose workload cache.

There is no persistent cache and no cached assertion or invoice result.
Each replay starts with an empty cache and
removes its extracted fixtures and private bytecode namespace on completion.

Source pins cover predecessor code, cases, expected receipt, manifests and all
nine transitive data/engine inputs. Archive-member checks, file hashes,
real-file mutations, the JSON assembly boundary, upstream controller checks,
the isolated driver predicate and final restored-fixture check remain active.
Predecessor harness sources are compiled directly; frozen imports use a fresh
bytecode namespace even for direct invocation. The replay refuses `-O`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/t16-invoice-read-cache/test_verify.py
python3.12 -B scripts/research_package.py --package research/t16-invoice-read-cache
```

Compare the same fixture with and without the adapter, using disposable paths:

```sh
python3.12 -B research/t16-invoice-read-cache/verify.py --baseline --receipt /tmp/t16-before.json
python3.12 -B research/t16-invoice-read-cache/verify.py --receipt /tmp/t16-after.json
cmp /tmp/t16-before.json /tmp/t16-after.json
cmp /tmp/t16-after.json research/t16-invoice-boundary-audit/EXPECTED.json
```

Both modes execute the same authenticated predecessor `run()` and compare its
complete result to the original receipt. Baseline mode leaves its reader
unchanged. Cases still give 28 invoice rejections and 26 acceptances; assembly
rejects 16 survivors and accepts ten, with the original further classifications.
The extra final cache-statistics line is not part of the receipt.

Ten focused controls cover plain/gzip types, byte changes with preserved timestamps,
repeated changed contents and restoration, cold/warm return mutation,
malformed/truncated data, missing paths, path/suffix separation, source tampering
and rejection of optimized replay. Local mutation experiments confirm that metadata-only
freshness and shared mutable returns fail these controls. The cache tests do
not replace any check of the predecessor's mathematical hypotheses.

## Scope and sources

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2051#discussioncomment-19001801)
continues the original audit's thread. `TASK.json` records scope and overlap.
This is verifier engineering. It neither runs the full selected cold chain nor
discharges any all-size supplier or multiplication theorem obligation.

## Open next questions

Does the improvement persist on another Python 3.12 host? Run the two modes in
alternating order, compare full receipts and report wall time and peak memory.
Interpreter and competing load affect timing; independent host measurements
remain outside this package's evidence.

## Credit

Credit Tairitsu-Aya for the audit, cases and expected receipt; Josie Elliston
for PR1959's handoff; Kumagi for PR3009 and the remaining parsing lead; and
jackmgaller for the predecessor's `marshal` copying technique. Original invoice,
controller, moment/outer and selected-construction contributors retain their
attribution in the predecessor. No predecessor package is copied or edited.

Prepared by thakrarsagar with substantial OpenAI Codex assistance, including
separate source inspection, regression-test implementation and code review.
Apache-2.0. No independent human or proof-assistant review is claimed.
