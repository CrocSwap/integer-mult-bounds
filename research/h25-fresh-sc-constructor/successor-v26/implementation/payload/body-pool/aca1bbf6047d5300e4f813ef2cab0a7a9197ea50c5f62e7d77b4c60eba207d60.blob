# P3: one-record native trace encoding

Source-only proposal; no implementation, scientific imports, compilation, corpus decoding, or numerical execution occurred. Ownership is exclusively this directory. Other agents and every frozen package remain untouched. Implementation awaits the parent gate.

## Frozen contract and evidence

Baseline: PR5995 `4f4159820c37f01d245784d1186bd51fcbc8ebb6`, native C arm. Current guidance: `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8. `PROPOSAL.json` records exact inspected file hashes. The pinned anchor records 238,685 ordered records, 55,839,507 canonical bytes, digest `7dec2bf33303c37e1c699609e83768d61df7e19104d34a26a148f66d5ccc4838`; these are existing observations, not new measurements.

`ComplementTrace.before` requires exact Label/dict/int objects, snapshots big values then small values into ordered tuples, validates integers, and returns `(us, vs)` before arithmetic. Preserve this method. `after` unpacks inputs, validates exact-list integer output or None, constructs two dictionaries, invokes JSON, ASCII-encodes and appends newline, updates the existing hash, then increments bytes and count. Exceptions before update leave the prefix unchanged; exceptions in later counter arithmetic can leave a changed hash. Preserve this order literally, including the current output validation and return-object identity.

The sorted encoding order is **call, result, us, vs**, with result keys **type, values** for lists. The schema description is not an instruction to use its displayed key order. Empty list and None differ. Intermediate `receipt()`, public counters and `hasher.copy()/hexdigest()` expose every completed record.

## Primary design and adapter

Supply `trace_encoder.c` and `trace_adapter.py` in this private directory after approval. Stateless native `encode_record(call, us, vs, output)` returns exact bytes including newline, or `NotImplemented`. Admit only exact integers in `[0, 2**64-1]`, exact tuple inputs, exact list/None output, and at most 64 entries in each vector. Out-of-domain values use the **literal original** JSON expression. This preserves negative signs, arbitrary-width values, nonstandard direct-after shapes, and decimal digit-limit errors through fallback.

Use a checked 8192-byte stack buffer, integer division/remainder for locale-independent decimal digits, and one final bytes allocation/copy. Every append checks capacity. Exact-type admission precedes integer conversion; inspect the error indicator and clear only expected overflow when choosing fallback. Hold the GIL; retain no Python references or caller buffers after return. No modular conversion, float conversion, custom callbacks or shared scratch state.

The parent injects the trace factory and encoder before binding; it finalizes closure identities before `RuntimeGuard` captures state. The parent must include the encoder owner/entry in the existing per-call freshness boundary before arithmetic/fallback. If compiled separately, that adds one native owner and callable check; if merged, extend the existing module's entry list. No post-capture replacement. Original `before`, `receipt`, input snapshots, hash update and counter code remain. A caller's output list is neither retained nor modified.

Supported environment remains the frozen ordinary CPython 3.12 JSON runtime and serial no-mutation-during-call policy. Local JSON files were inspected and pinned; no general JSON monkeypatch-equivalence or security claim is made. The fallback retains the ordinary original serializer.

## Alternatives and cost

Cross-call buffering is rejected: it delays observable hash prefixes and can shift update exceptions. Moving snapshots after arithmetic or storing mutable views is rejected. A cached JSONEncoder is a smaller alternative but retains both record dictionaries, result string, ASCII bytes and newline copy. Native hashing is not proposed: hashlib already uses native implementations. The candidate targets Python construction and dispatch overhead, not a speculative SHA gain.

Retained costs: every vector snapshot/type check, native kernel/guard, ordered record, 55,839,507 bytes, immediate SHA update, counters, receipts, full witnesses and all old controls. New costs: conversion/type admission, bounded stack work, one extra native crossing, callable freshness, source custody, cold compilation/link/load, new controls, failures and cleanup. Costs and complete gain are **unknown**, not zero; no per-lane 15% promise. Parent-only full pilots decide whether integration is useful.

## Controls and next gate

Retain all old finite controls, including seven trace pairs, four trace negatives, width fallback and independent dense checks. New controls compare literal reference bytes and every prefix/receipt/hash copy for empty/list/None, order permutations, decimal boundaries, uint64 maximum, negative/65-bit/100-bit/decimal-limit values, 64/65 entries, exact types versus subclasses/bool, snapshot mutation before after, output mutation after after, malformed unpacking/output, failing hash updates, and counter failure order. Verify callable replacement fails before arithmetic and restored bindings work. Encoder rejection must be side-effect-free and leave no stale error. Controls run normal and optimized modes; complete verification remains assertion-on.

First discriminating experiment: parent cold-builds once, runs exact byte/prefix/failure controls, then one complete frozen native-baseline/candidate pair including the entire new cost bill. Only correct complete results can justify combination.

Primary documentation: [JSON parameters](https://docs.python.org/3.12/library/json.html), [exact integers and checked conversion](https://docs.python.org/3.12/c-api/long.html), [bytes ownership](https://docs.python.org/3.12/c-api/bytes.html), [tuple references](https://docs.python.org/3.12/c-api/tuple.html), [list references](https://docs.python.org/3.12/c-api/list.html), [hash prefixes and native implementations](https://docs.python.org/3.12/library/hashlib.html). Local stdlib source confirms this keyword configuration constructs a new JSONEncoder per call and normally invokes its C encoder.
