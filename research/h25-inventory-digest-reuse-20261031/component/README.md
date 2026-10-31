# Inventory-local digest reuse: source-only component

This package extracts only `need`, `sha`, and `inventory` from the pinned v4
`integration/full_driver.py`. The independent reference is literal source.
The candidate assigns `raw_digest = sha(raw)` only after the original `expected`
pin expression, then uses it for the comparison and returned digest. It removes
one duplicate SHA pass per accepted file, with every original file read intact.
There is no helper module, digest table, cached PASS, or cross-call reuse.

`inventory_controls.py` is byte-identical to the original Area6 source. The
consumer retains its eleven ordered cases in each normal/-O process and runs
sixteen additional exact typed/error/count/freshness controls from
`digest_controls.py`. In production only trusted CPython3.12 stdlib
pathlib/stat/hashlib bindings and the fixed exact pin data are admitted.
Arbitrary concurrent mutation and mutable or callback-bearing monkeypatch
semantics are outside the production equivalence claim. The count controls
separately instrument the trusted fixed implementation and restore all bindings.

The concrete representative fixture is the exact32-file,453700-byte frozen v4
inventory pinned in `FIXTURE-v1.json`. No file content is executed. List pin
second entries retain historical0664 while actual frozen modes are0444;
inventory reports actual mode and the consumer independently checks it. Each
comparison process creates a fresh writable scratch directory, copies and
verifies all32 source byte payloads, runs exactly128 fresh inventory invocations
on that same fixed corpus, checks every typed result, writes/readbacks the exact
mapping, independently rereads/checks all fixture files, removes scratch, and
checks source custody. This128-call workload is declared for observation; it
is not a claim about full-driver inventory frequency.

The fixed prospective schedule in `BILL-v1.json` is controls-normal,
controls-optimized, baseline1,candidate1,candidate2,baseline2, all separate fresh
processes and serial parent guarded operations. There is no adaptive count,
reroll, excluded first observation, best-sample selection, or automatic retry.
Only the parent can admit/launch this source and freeze the actual runner/runtime
closure. The consumer itself has no process launch or native/scientific import.
`SOURCE-PINS.json` authenticates package/external bytes and exact modes; parent
staging must independently pin that manifest and this entire package before
execution. Authentication is fresh before module load and after cleanup.

All source-only status claims remain source-only. No target imports, tests,
compilation, measurements, native/scientific work, decoder, network or
publication were performed by this author. Metadata hashes and AST parsing
without target imports establish the source package, not executable correctness
or performance. An independent reviewer must accept actual sources, bill and
parent runtime before any execution. Full H25, publication digest snapshot and
ordered native/row observation reuse remain separate. This inventory component
cannot complete all digest/observation goals or support a whole-caller speedup.

Prospective timing begins in the parent outer guard before process bootstrap,
fixture creation/import/runtime checks, and ends after exit, output equivalence,
cleanup and guard/source/log validation and guard receipt. The final report's
own serialization and external preparation/review/publication are outside that
boundary, remain unknown until separately measured, and are never treated as
zero. Historical original timing and final metadata-publication gaps stay open.

Predecessor credit: original v4 integration inventory and Area6 inventory controls
are preserved and source-pinned. This package implements the narrow local reuse
identified by Area6 API and independent-components alternatives feasibility.

Failure handling: the consumer always attempts scratch cleanup but its post-work
authentication and receipt are success-path checks. The admitted outer guard must
retain exceptions/logs and perform source/runtime/log/guard and cleanup checks
after every failure as well; it must not count a failed process as a successful
comparison. Parent also validates each fresh output is disjoint from the source
closure before admission. Every failure remains charged and there is no retry.
