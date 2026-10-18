# Two-tape finite control for nested parking frames

[PR2574](https://github.com/CrocSwap/integer-mult-bounds/pull/2574) proves a
nested invocation contract in a charged payload simulator, while leaving its
length/floor descriptors and fixed-tape controller open. This package closes
the **matched parking-record control subinterface**: ten finite states and a
complete 490-entry transition table implement BEGIN, PUSH, POP and END on two
tapes. The table reads only its state and two scanned symbols. Packet lengths
and nested frame boundaries are represented physically by head displacements
and delimiters; no width/depth counter or runtime descriptor stack selects an
action.

For every finite packet length and properly nested finite command sequence,
the [proof](PROOF.md) establishes exact packet order, consumed-record cleanup,
rewound packet heads, and bit-for-bit preservation of arbitrary opaque
ancestor data. Empty packets and unequal lengths are included. The domain is
the predecessor wrapper's reversed sequence of matching pushes and pops;
arbitrary partial-size `pop(size)` calls are not implemented. Caller commands
remain trusted: a callee may not close its caller's frame.

The exact parking-controller invoice is:

| Operation | Steps | Reads | Writes | Head moves |
|---|---:|---:|---:|---:|
| BEGIN | 1 | 2 | 1 | 1 |
| END | 2 | 4 | 1 | 1 |
| PUSH n | 2n+3 | 4n+6 | 2n+2 | 3n+3 |
| POP n | 3n+4 | 6n+8 | 2n+2 | 5n+5 |

Every step reads both cells; every issued write and unit move is counted.
For d balanced frame pairs, r matched packet pairs and total packet volume V,
the totals are `5V+7r+3d` steps, `10V+14r+6d` reads, `4V+4r+2d` writes and
`8V+8r+2d` moves. At a boundary the occupied parking suffix has one cell per
live payload bit, record and frame. These charges include the new physical
markers/control and do not replace the predecessor's different payload-only
meter by numerical comparison.

## Evidence and reproduction

Standard-library Python 3.12, from repository root:

```sh
python3.12 -I -O -B research/finite-parking-frames/verify.py
python3.12 -I -O -B research/finite-parking-frames/test_verify.py
python3.12 -B scripts/research_package.py --package research/finite-parking-frames
```

Expected status: `PASS_FINITE_PARKING_FRAMES`. The verifier regenerates every
entry of [TABLE.json](TABLE.json), validates the finite alphabet and unit head
moves, and compares every typed field of [RESULT.json](RESULT.json).
`--out NEW_PATH` writes an exclusive new receipt. Direct replay needs neither
Git nor a sibling package and is read-only; registered provenance checks need
the repository's Git history.

The sparse simulator and a separately written dense interpreter agree on:

- all 2,047 binary packets of lengths 0 through 10;
- 21 translated tests, including negative head coordinates and 16,384-bit packets;
- unequal and empty packets nested to depths 1, 2, 7, 32 and 129;
- exact endpoints, untouched caller cells, physical marker storage and all charges.

Nine control groups reject empty-frame POP, nonempty-frame END, five occupied
output positions before any write, changed payload, an unerased record, a
wrong output direction, missing head rewind, a lost empty record and an
incomplete transition table. Package checks exercise Git-free unchanged
exports, source-byte drift before any predecessor execution, missing table
evidence, incomplete source inventory, typed receipt drift and output
non-overwrite. The all-size theorem is the written induction, not an inference
from test widths.

The registered primary and both export/integrity test groups pass on CPython
3.12.7. A separate agent read the proof and both interpreters and independently
replayed the complete primary on optimized CPython 3.12.14 with no blocking
finding. This is agent review, not independent human review.

## Scope

This is an operational finite-table construction and conditional refinement,
not a whole-supplier allocator. Supplying/consuming the single packet port,
serializing distinct caller tapes, choosing well-bracketed commands, arithmetic,
and the rest of `frame.invoke` remain caller work. Fixtures supply and consume
ports outside the measured controller and do not treat those actions as free.
BEGIN/PUSH/POP/END have inverse complete endpoints on valid configurations;
the transition system is not claimed locally reversible or hostile-code-safe.
Malformed input need not roll back; only the stated valid boundary rejections
preserve both heads and cells exactly. No native supplier, changed recursive
profile, selected cold replay, new kappa or proof-assistant theorem is claimed.

## Open next questions

- **Fixed-tape invocation dispatch:** bind one actual caller's input/output
  serialization and granted storage to this packet port and charge those
  moves. The blocker is the predecessor's dynamic registry and multiple
  logical tape objects, which this parking primitive does not allocate.
- **Whole-call reserve:** combine peak live packet volume with the exact
  one-cell-per-record/frame overhead for a named sequential call tree. Its
  arithmetic widths, schedule and depth must be supplied by that caller;
  the finite controller alone does not bound them.

## Sources, selection and credit

Started from canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4. Picker seed `ec3ae3aa2e614be2c97851bf5f8ff527` selected
`supplier-boundary-audit`; the required historical owner-boundary first
command passed. `TASK.json` records the deliberate scope change to the
current physical parking handoff and the exact overlap coverage.

PR2574 at `07d75bfc2e13f0c17d84a3788885affc4d712dc1` supplies the nested
ownership contract and matching-record caller. Its PROOF, frame implementation,
retained pipeline/stream primitives and [notice](inputs/NOTICE.md) are preserved
unchanged and authenticated with SHA-256 and Git blobs before experiments.
They are reference text only; no predecessor executable is imported or run.
Credit ywz65/PR2574 and PR2534, the PR2483/2250/2287 physical primitive lineage,
and their retained native/selected-source contributors. These sources provide
the domain being refined, not evidence of a bug in their stated scope.

New work: ywz65 with substantial OpenAI Codex assistance in implementation,
proof, tests and separate agent review. No independent human review is claimed.
Apache-2.0; no broader priority claim for stack or tape-machine constructions.
